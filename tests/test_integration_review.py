"""Independent regression checks at collection/analysis boundaries."""

import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from sdp_audit.analyze import analyze
from sdp_audit.catalog import ALLOWED_PATTERNS, RESOURCES
from sdp_audit.collect import CollectionOptions, Collector
from sdp_audit.models import ResourceSpec, Snapshot
from sdp_audit.report import write_reports
from sdp_audit.transport import ApiError, BudgetExceeded, ReadOnlyClient


class _SequencedClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.stats = {"requests": 0}

    def get_json(self, path, params=None):
        self.stats["requests"] += 1
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class _FastClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class _LocalServer:
    """Exercise urllib against loopback; never contact any ServiceDesk instance."""

    def __init__(self, dispatch):
        calls = self.calls = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                calls.append({"method": self.command, "path": self.path,
                              "auth": self.headers.get("authtoken"),
                              "portal": self.headers.get("portalid")})
                status, headers, payload = dispatch(self.path)
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                for key, value in headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.01}, daemon=True)
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def _local_client(base, secret):
    clock = _FastClock()
    # Isolate synthetic loopback traffic from any workstation proxy settings.
    with mock.patch.dict(os.environ, {"http_proxy": "", "HTTP_PROXY": "",
                                      "https_proxy": "", "HTTPS_PROXY": "",
                                      "all_proxy": "", "ALL_PROXY": "",
                                      "no_proxy": "*", "NO_PROXY": "*"}):
        return ReadOnlyClient(base, secret, ALLOWED_PATTERNS, allow_http=True,
                              portal_id="1", rpm=30, max_requests=50,
                              max_runtime=200, clock=clock, sleep=clock.sleep)


class IntegrationReviewTests(unittest.TestCase):
    def test_budget_interrupt_retains_prior_child_page_and_impact(self):
        """A late note-page stop must not discard an earlier proven exclusion."""
        client = _SequencedClient([
            {"requests": [{"id": "1"}], "list_info": {"has_more_rows": False}},
            {"notes": [{"id": "10", "attachments": [{"id": "501", "size": 42}]}],
             "list_info": {"has_more_rows": True}},
            BudgetExceeded("Synthetic next-page budget exhaustion"),
        ])
        snapshot = Snapshot("2026-10-05T17:00:00+00:00", {}, {"max_requests": 10})
        spec = ResourceSpec("requests", "/requests", "requests", "request", "", detail=False)
        Collector(client, [spec], CollectionOptions(page_size=1, subresource_parents=1)).collect(snapshot)
        self.assertIsNotNone(snapshot.interrupted_reason)
        notes = snapshot.datasets["request_notes"]
        self.assertEqual([row["id"] for row in notes.records], ["10"])
        self.assertEqual(notes.records[0]["_parent_id"], "1")
        self.assertFalse(notes.list_complete)
        self.assertEqual(notes.status, "partial")
        self.assertEqual(notes.pages, 1)
        findings = {finding.id: finding for finding in analyze(snapshot).findings}
        self.assertEqual(findings["NOTE_ATTACHMENTS"].status, "CONFIRMED_IMPACT")

    def test_missing_denied_and_partial_collections_are_not_clean(self):
        """Unobserved data never becomes a zero-count compatibility finding."""
        client = _SequencedClient([{"unexpected_wrapper": [], "list_info": {"has_more_rows": False}}])
        snapshot = Snapshot("2026-10-05T17:00:00+00:00", {}, {"max_requests": 10})
        spec = ResourceSpec("technicians", "/technicians", "technicians", "technician", "", detail=False)
        Collector(client, [spec], CollectionOptions(subresource_parents=0)).collect(snapshot)
        self.assertEqual(snapshot.datasets["technicians"].status, "invalid_response")
        assessment = analyze(snapshot)
        self.assertFalse([finding.id for finding in assessment.findings if finding.status == "NO_ISSUE_OBSERVED"])
        finding = next(item for item in assessment.findings if item.id == "TECHNICIAN_EMAILS")
        self.assertIsNone(finding.affected_count)

    def test_loopback_transport_collector_analyzer_and_private_reports(self):
        secret = "synthetic-test-key-828138"
        private = "SYNTHETIC_PRIVATE_TICKET_TEXT"
        datasets = {
            "/requests": ("requests", [
                {"id": "1", "created_time": {"value": "1514764800000"},
                 "has_attachments": True, "has_notes": True, "subject": private,
                 "description": private + secret, "href": "https://must-not-follow.invalid"},
                {"id": "2", "created_time": {"value": "1790812800000"}, "subject": private},
            ]),
            "/technicians": ("technicians", [
                {"id": "10", "email_id": "synthetic-private-email@example.invalid"},
                {"id": "11", "email_id": "synthetic-private-email@example.invalid"},
            ]),
            "/reports": ("reports", [{"id": "20", "report_name": private,
                                       "type": "query", "query": private}]),
            "/requests/1/notes": ("notes", [{"id": "30", "description": private,
                                              "attachments": [{"id": "40", "size": 10}]}]),
            "/requests/2/notes": ("notes", []),
            "/requests/1/tasks": ("tasks", []),
            "/requests/2/tasks": ("tasks", []),
        }
        details = {
            "/requests/1": {"request": {**datasets["/requests"][1][0],
                                          "attachments": [{"id": "50", "size": 55000000,
                                                            "name": private}]}},
            "/requests/2": {"request": {**datasets["/requests"][1][1], "attachments": []}},
            "/technicians/10": {"technician": datasets["/technicians"][1][0]},
            "/technicians/11": {"technician": datasets["/technicians"][1][1]},
        }

        def dispatch(target):
            parsed = urlsplit(target)
            path = parsed.path.removeprefix("/api/v3")
            if path in details:
                return 200, {}, details[path]
            self.assertIn(path, datasets, "Collector requested an unexpected route")
            plural, records = datasets[path]
            query = parse_qs(parsed.query)
            info = json.loads(query["input_data"][0])["list_info"]
            start, count = info["start_index"], info["row_count"]
            selected = records[start - 1:start - 1 + count]
            return 200, {}, {plural: selected, "list_info": {
                "start_index": start, "total_count": len(records),
                "has_more_rows": start - 1 + len(selected) < len(records),
            }, "response_status": [{"status_code": 2000, "status": "success"}]}

        with _LocalServer(dispatch) as server:
            client = _local_client(server.base, secret)
            specs = [resource for resource in RESOURCES
                     if resource.key in {"requests", "technicians", "reports"}]
            snapshot = Snapshot("2026-10-05T17:00:00+00:00", {"host": client.base_url},
                                {"max_requests": 50})
            Collector(client, specs, CollectionOptions(page_size=1, detail_limit=0,
                                                       subresource_parents=2)).collect(snapshot)
            self.assertIsNone(snapshot.interrupted_reason)
            self.assertGreater(len(server.calls), 5)
            self.assertTrue(all(call["method"] == "GET" for call in server.calls))
            self.assertTrue(all(call["auth"] == secret for call in server.calls))
            self.assertTrue(all(call["portal"] == "1" for call in server.calls))
            self.assertTrue(all(secret not in call["path"] for call in server.calls))
            self.assertEqual(client.stats["requests"], len(server.calls))
            self.assertGreaterEqual(client.stats["elapsed_seconds"], 2 * (len(server.calls) - 1))
        assessment = analyze(snapshot)
        findings = {finding.id: finding for finding in assessment.findings}
        for key in ("HISTORY_WINDOW_FIVE_YEARS", "TECHNICIAN_EMAILS", "ATTACHMENT_SIZE", "NOTE_ATTACHMENTS"):
            self.assertEqual(findings[key].status, "CONFIRMED_IMPACT", key)
        self.assertEqual(findings["TECHNICIAN_EMAILS"].affected_count, 2)
        with tempfile.TemporaryDirectory() as temporary:
            paths = write_reports(assessment, temporary)
            self.assertEqual(len(paths), 6)
            for path in paths.values():
                contents = Path(path).read_text(encoding="utf-8")
                for sensitive in (secret, private, "synthetic-private-email@example.invalid"):
                    self.assertNotIn(sensitive, contents)

    def test_real_urllib_redirect_does_not_forward_auth_or_follow(self):
        # The disallowed destination is on the same local server so a mistaken
        # follow is observed immediately without any external network contact.
        def dispatch(target):
            if urlsplit(target).path == "/api/v3/requests":
                return 302, {"Location": "/credential-collector"}, {}
            return 200, {}, {"requests": []}

        with _LocalServer(dispatch) as server:
            client = _local_client(server.base, "synthetic-redirect-key")
            with self.assertRaises(ApiError) as failure:
                client.get_json("/requests")
            self.assertEqual(failure.exception.kind, "network")
            self.assertEqual(len(server.calls), 1)
            self.assertEqual(server.calls[0]["path"], "/api/v3/requests")


if __name__ == "__main__":
    unittest.main()
