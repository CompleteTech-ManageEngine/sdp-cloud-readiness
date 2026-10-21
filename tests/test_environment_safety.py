"""Independent environment integration regressions using real GET transport."""

from __future__ import annotations

import contextlib
import email.message
import io
import json
from pathlib import Path
import tempfile
import unittest

from sdp_audit.catalog import ALLOWED_PATTERNS
from sdp_audit.collect import CollectionOptions, Collector
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions, PortalClient
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.models import Dataset, EnvironmentSnapshot, PortalInfo, ResourceSpec, Snapshot
from sdp_audit.progress import ProgressPrinter, print_environment_coverage
from sdp_audit.report import write_reports
from sdp_audit.transport import ApiError, BudgetExceeded, ReadOnlyClient


SECRET = "safety-regression-api-key-4cd187"
PRIVATE = "PRIVATE_TICKET_CONTENT_65db27"
PRIVATE_EMAIL = "private.person@example.invalid"
PRIVATE_FILENAME = "private-medical-document.pdf"


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, duration):
        self.now += duration


class Response(io.BytesIO):
    def __init__(self, payload, status=200):
        super().__init__(json.dumps(payload).encode("utf-8"))
        self.status = status
        self.headers = email.message.Message()
        self.headers["Content-Type"] = "application/json"

    def getcode(self):
        return self.status


class Opener:
    def __init__(self, responses, clock):
        self.responses = list(responses)
        self.clock = clock
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((self.clock(), request, timeout))
        if not self.responses:
            raise AssertionError("Unexpected network attempt in synthetic safety fixture")
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


def response_page(key, rows, *, more=False, start=1):
    return Response({"response_status": {"status_code": 2000, "status": "success"}, key: rows,
                     "list_info": {"has_more_rows": more, "start_index": start, "row_count": len(rows)}})


def portals(ids=("7",), *, names=None):
    return response_page("portals", [{"id": ident, "name": (names or {}).get(ident, "Portal " + ident)} for ident in ids])


def failure(message, status=403, code=4000):
    return Response({"response_status": {"status": "failed", "status_code": code,
                                         "messages": [{"status_code": code, "message": message}]}}, status)


def spec(key="requests", *, detail=False):
    return ResourceSpec(key, "/" + key, key, key[:-1], "https://www.manageengine.com/",
                        detail=detail, module=key)


class EnvironmentSafetyTests(unittest.TestCase):
    def client(self, responses, *, max_requests=100, max_runtime=1200, progress=None):
        clock = Clock()
        client = ReadOnlyClient("https://sdp.example.invalid", SECRET, ALLOWED_PATTERNS,
                                max_requests=max_requests, max_runtime=max_runtime,
                                rpm=30, clock=clock, sleep=clock.sleep, progress=progress)
        opener = Opener(responses, clock)
        client._opener = opener
        return client, opener

    def environment(self, client, *, resources=None, progress=None, fields=False, children=0):
        env = EnvironmentSnapshot("2026-10-07T00:00:00+00:00", {"host": client.base_url},
                                  {"max_requests": client.max_requests, "max_runtime_seconds": client.max_runtime})
        collector = EnvironmentCollector(
            client, resources if resources is not None else [spec()],
            CollectionOptions(page_size=2, subresource_parents=children, inventory_budget_fraction=1.0),
            EnvironmentOptions(discover_fields=fields, collect_orgusers=False), progress,
        )
        return collector.collect(env)

    def snapshot(self):
        snapshot = Snapshot("2026-10-07T00:00:00+00:00", {"portal_id": "7", "portal_name": "IT"}, {})
        snapshot.datasets["requests"] = Dataset(
            "requests", "/requests", records=[{"id": "10", "_portal_id": "7"}],
            pages=1, list_complete=True, status="complete", outcome="COMPLETE",
            read_attempted=True, portal_id="7", portal_name="IT", module="requests",
        )
        return snapshot

    def test_request_budget_before_first_scoped_attempt_does_not_assess_portal(self):
        client, opener = self.client([portals()], max_requests=1)
        env = self.environment(client)
        collection = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")
        self.assertEqual(len(opener.calls), 1)
        self.assertFalse(collection.read_attempted)
        self.assertEqual(collection.outcome, "NOT_STARTED")
        self.assertIsNone(collection.coverage()["records_observed"])
        self.assertEqual(env.portals["7"].portal.scan_status, "NOT_STARTED")
        self.assertEqual(env.stats["portals_with_attempted_assessment"], 0)

    def test_time_budget_before_first_scoped_attempt_does_not_assess_portal(self):
        client, opener = self.client([portals()], max_runtime=1)
        env = self.environment(client)
        collection = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(env.stop_classification, "TIME_BUDGET_REACHED")
        self.assertEqual(len(opener.calls), 1)
        self.assertFalse(collection.read_attempted)
        self.assertIsNone(collection.coverage()["records_observed"])
        self.assertEqual(env.stats["portals_with_attempted_assessment"], 0)

    def test_explicit_module_and_portal_errors_do_not_retry_with_a_different_query(self):
        for message, classification in (("Module is disabled", "MODULE_NOT_ENABLED"),
                                        ("PORTALID is required", "PORTAL_CONTEXT_REQUIRED"),
                                        ("Portal is not accessible", "PORTAL_NOT_ACCESSIBLE")):
            with self.subTest(classification=classification):
                client, opener = self.client([portals(), failure(message), failure(message)])
                env = self.environment(client, resources=[spec("projects")])
                collection = env.portals["7"].snapshot.datasets["projects"]
                self.assertEqual(collection.outcome, classification)
                self.assertEqual(len(opener.calls), 2)
                self.assertEqual(collection.diagnostics[-1]["http_status"], 403)
                self.assertEqual(collection.diagnostics[-1]["api_codes"], [4000])
                self.assertIsNone(collection.coverage()["records_observed"])

    def test_auth_failure_on_detail_retains_actual_diagnostic_and_complete_list(self):
        client, _ = self.client([failure("Invalid API Key", status=401, code=4022)])
        view = PortalClient(client, PortalInfo("7", "IT"), [spec(detail=True)])
        collector = Collector(view, [spec(detail=True)], CollectionOptions(subresource_parents=0))
        snapshot = self.snapshot()
        with self.assertRaises(ApiError):
            next(collector.detail_steps(snapshot))
        collection = snapshot.datasets["requests"]
        self.assertTrue(collection.list_complete)
        self.assertEqual(collection.outcome, "COMPLETE")
        self.assertEqual(collection.diagnostics[-1]["classification"], "AUTHENTICATION_FAILED")
        self.assertEqual(collection.diagnostics[-1]["http_status"], 401)
        self.assertEqual(collection.diagnostics[-1]["api_codes"], [4022])
        self.assertEqual(collection.diagnostics[-1]["portal_id"], "7")

    def test_no_detail_attempt_is_reported_when_budget_blocks_http_admission(self):
        client, _ = self.client([response_page("requests", [])], max_requests=1)
        client.get_json("/requests", portal_id="7", endpoint_name="requests", module="requests")
        collector = Collector(PortalClient(client, PortalInfo("7", "IT"), [spec(detail=True)]),
                              [spec(detail=True)], CollectionOptions(subresource_parents=0))
        snapshot = self.snapshot()
        with self.assertRaises(BudgetExceeded):
            next(collector.detail_steps(snapshot))
        self.assertEqual(snapshot.datasets["requests"].detail_attempted, 0)
        self.assertTrue(snapshot.datasets["requests"].list_complete)

    def test_final_successful_child_page_is_committed_before_generator_is_closed(self):
        client, _ = self.client([response_page("notes", [])])
        collector = Collector(PortalClient(client, PortalInfo("7", "IT"), [spec()]),
                              [spec()], CollectionOptions(subresource_parents=1))
        snapshot = self.snapshot()
        iterator = collector.child_steps(snapshot)
        next(iterator)
        iterator.close()  # Another portal can reach its budget before this resumes.
        children = snapshot.datasets["request_notes"]
        self.assertEqual(children.pages, 1)
        self.assertTrue(children.list_complete)
        self.assertEqual(children.outcome, "EMPTY")
        self.assertEqual(children.detail_succeeded, 1)
        self.assertEqual(children.coverage()["records_observed"], 0)

    def test_actual_exhausted_http_budget_is_not_reported_as_sampling_reservation(self):
        client, opener = self.client([portals(), response_page("requests", [{"id": "10"}], more=True)],
                                     max_requests=2)
        env = self.environment(client)
        collection = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")
        self.assertEqual(collection.outcome, "INCOMPLETE")
        self.assertEqual(collection.stop_reason, "REQUEST_BUDGET_REACHED")
        self.assertEqual(collection.coverage()["records_observed"], 1)

    def test_one_inaccessible_portal_does_not_abort_an_accessible_portal(self):
        client, opener = self.client([portals(("7", "9")), failure("Portal is not accessible"),
                                     response_page("requests", [])])
        env = self.environment(client)
        self.assertFalse(env.portals["7"].portal.accessible)
        self.assertTrue(env.portals["9"].portal.accessible)
        self.assertEqual(env.portals["7"].snapshot.datasets["requests"].outcome, "PORTAL_NOT_ACCESSIBLE")
        self.assertEqual(env.portals["9"].snapshot.datasets["requests"].outcome, "EMPTY")
        self.assertEqual([request.get_header("Portalid") for _, request, _ in opener.calls], [None, "7", "9"])

    def test_get_header_scope_privacy_and_reporting_use_same_actual_transport(self):
        console = io.StringIO()
        progress = ProgressPrinter(max_requests=100)
        names = {"7": "IT " + SECRET, "9": "HR"}
        rows = [{"id": "10", "subject": PRIVATE, "description": PRIVATE,
                 "requester": {"email_id": PRIVATE_EMAIL, "name": PRIVATE},
                 "attachments": [{"id": "20", "name": PRIVATE_FILENAME, "size": 12}],
                 "udf_fields": {"udf_private": PRIVATE + SECRET}}]
        client, opener = self.client([portals(("7", "9"), names=names),
                                     response_page("requests", rows), response_page("requests", [])], progress=progress)
        with contextlib.redirect_stdout(console):
            env = self.environment(client, progress=progress)
            print_environment_coverage(env)
        self.assertEqual(client.stats["requests"], 3)
        self.assertEqual([time for time, _, _ in opener.calls], [0.0, 2.0, 4.0])
        self.assertTrue(all(request.get_method() == "GET" and request.data is None for _, request, _ in opener.calls))
        self.assertEqual([request.get_header("Portalid") for _, request, _ in opener.calls], [None, "7", "9"])
        self.assertTrue(all(SECRET not in request.full_url for _, request, _ in opener.calls))
        assessment = analyze_environment(env)
        with tempfile.TemporaryDirectory() as directory:
            write_reports(assessment, Path(directory))
            reports = [path.read_text(encoding="utf-8") for path in Path(directory).iterdir() if path.is_file()]
        for text in reports + [console.getvalue(), json.dumps(assessment.to_dict())]:
            for canary in (SECRET, PRIVATE, PRIVATE_EMAIL, PRIVATE_FILENAME):
                self.assertNotIn(canary, text)

    def test_list_completed_before_other_portal_auth_failure_stays_complete(self):
        client, _ = self.client([portals(("7", "9")), response_page("requests", []),
                                failure("Invalid API Key", status=401, code=4022)])
        env = self.environment(client)
        self.assertEqual(env.stop_classification, "AUTHENTICATION_FAILED")
        finished = env.portals["7"].snapshot.datasets["requests"]
        self.assertTrue(finished.list_complete)
        self.assertEqual(finished.outcome, "EMPTY")
        self.assertEqual(finished.coverage()["records_observed"], 0)
        denied = env.portals["9"].snapshot.datasets["requests"]
        self.assertEqual(denied.outcome, "AUTHENTICATION_FAILED")
        self.assertIsNone(denied.coverage()["records_observed"])

    def test_interrupt_at_final_phase_notification_keeps_collected_report_input(self):
        def progress(event):
            if event.get("event") == "phase" and event.get("phase") == "analysis":
                raise KeyboardInterrupt()

        client, _ = self.client([portals(), response_page("requests", [])])
        env = self.environment(client, progress=progress)
        self.assertEqual(env.stop_classification, "INTERRUPTED")
        collection = env.portals["7"].snapshot.datasets["requests"]
        self.assertTrue(collection.list_complete)
        self.assertEqual(collection.outcome, "EMPTY")
        self.assertEqual(collection.coverage()["records_observed"], 0)


if __name__ == "__main__":
    unittest.main()
