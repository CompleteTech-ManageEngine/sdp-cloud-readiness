"""Synthetic topology/GET contract tests; no customer system is contacted."""

from __future__ import annotations

from dataclasses import asdict
import email.message
import io
import json
import unittest

from sdp_audit.topology import PORTAL_DISCOVERY_SOURCE, discover_topology, portal_identifier
from sdp_audit.transport import ApiError, BudgetExceeded, ReadOnlyClient


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get_json(self, path, params=None, **context):
        self.calls.append({"path": path, "params": params, **context})
        if not self.responses:
            raise AssertionError("Unexpected topology request")
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


def page(ids, more=False, start=None, **extra_info):
    info = {"has_more_rows": more, "row_count": len(ids), **extra_info}
    if start is not None:
        info["start_index"] = start
    return {
        "response_status": [{"status_code": 2000, "status": "success"}],
        "portals": [{"id": str(identifier), "name": f"Portal {identifier}"} for identifier in ids],
        "list_info": info,
    }


class TopologyTests(unittest.TestCase):
    def test_multiple_portals_have_provenance_and_unknown_access(self):
        client = FakeClient([page([1, 3, 18])])
        result = discover_topology(client)
        self.assertEqual(result.outcome, "COMPLETE")
        self.assertTrue(result.complete)
        self.assertEqual([p.id for p in result.portals], ["1", "3", "18"])
        for portal in result.portals:
            self.assertEqual(portal.discovery_endpoint, "/portals")
            self.assertEqual(portal.discovery_source, PORTAL_DISCOVERY_SOURCE)
            self.assertIsNone(portal.accessible)
            self.assertEqual(portal.access_status, "UNKNOWN")
            self.assertEqual(portal.scan_status, "NOT_STARTED")
        self.assertEqual(client.calls[0]["portal_id"], None)
        self.assertEqual(client.calls[0]["endpoint_name"], "portals")

    def test_discovery_uses_only_global_portals_and_one_based_pages(self):
        client = FakeClient([page([7, 14], True, 1), page([31], False, 3)])
        result = discover_topology(client, page_size=2)
        self.assertTrue(result.complete)
        self.assertEqual(result.pages, 2)
        self.assertEqual([p.id for p in result.portals], ["7", "14", "31"])
        self.assertEqual([c["path"] for c in client.calls], ["/portals", "/portals"])
        self.assertEqual([c["portal_id"] for c in client.calls], [None, None])
        first, second = [json.loads(c["params"]["input_data"])["list_info"] for c in client.calls]
        self.assertEqual((first["start_index"], second["start_index"]), (1, 3))
        self.assertEqual((first["page"], second["page"]), (1, 2))
        self.assertEqual(first["sort_field"], "created_time")

    def test_single_portal_fixture(self):
        result = discover_topology(FakeClient([page([9])]))
        self.assertTrue(result.complete)
        self.assertEqual(result.portals[0].id, "9")

    def test_explicit_override_bypasses_discovery_and_deduplicates(self):
        client = FakeClient([])
        result = discover_topology(client, portal_ids=["3", "09", "3", "9"])
        self.assertEqual(client.calls, [])
        self.assertEqual(result.mode, "explicit")
        self.assertEqual([p.id for p in result.portals], ["3", "9"])
        self.assertTrue(result.complete)
        self.assertTrue(all(not p.discovered and p.accessible is None for p in result.portals))
        self.assertTrue(all(p.discovery_endpoint is None for p in result.portals))

    def test_invalid_override_never_issues_a_request_or_echoes_value(self):
        values = ["0", "-1", "１", "1\n", "1,3", "secret.invalid-id", "1/requests", True, None, 1.0, "1" * 129]
        for value in values:
            with self.subTest(value=value):
                client = FakeClient([])
                with self.assertRaisesRegex(ValueError, "positive ASCII decimal") as raised:
                    discover_topology(client, portal_ids=["3", value])
                self.assertEqual(client.calls, [])
                self.assertNotIn("secret.invalid-id", str(raised.exception))

    def test_empty_override_is_not_an_implicit_default(self):
        client = FakeClient([])
        with self.assertRaises(ValueError):
            discover_topology(client, portal_ids=[])
        self.assertEqual(client.calls, [])

    def test_identifier_normalization(self):
        self.assertEqual(portal_identifier(341), "341")
        self.assertEqual(portal_identifier("003"), "3")

    def test_explicit_portal_limit_is_an_incomplete_target_set(self):
        client = FakeClient([])
        result = discover_topology(client, portal_ids=["3", "8", "12"], max_portals=2)
        self.assertEqual(result.outcome, "RECORD_LIMIT_REACHED")
        self.assertFalse(result.complete)
        self.assertEqual([p.id for p in result.portals], ["3", "8"])
        self.assertEqual(client.calls, [])

    def test_successful_empty_directory_is_empty_complete(self):
        result = discover_topology(FakeClient([page([])]))
        self.assertEqual(result.outcome, "EMPTY")
        self.assertTrue(result.complete)
        self.assertEqual(result.portals, [])
        self.assertEqual(result.pages, 1)

    def test_unsupported_discovery_never_guesses_or_bruteforces(self):
        client = FakeClient([ApiError("unsupported", "API endpoint was not found.", 404, (4007,))])
        result = discover_topology(client)
        self.assertEqual(result.outcome, "ENDPOINT_UNSUPPORTED")
        self.assertFalse(result.complete)
        self.assertEqual(result.portals, [])
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["path"], "/portals")
        self.assertIsNone(client.calls[0]["portal_id"])
        self.assertTrue(any("--portal-id" in note for note in result.limitations))

    def test_permission_denial_retains_exact_safe_diagnostic(self):
        error = ApiError("forbidden", "The requested operation was denied.", 403, (4002,),
                         api_message="Insufficient permissions.", cause="authorization")
        result = discover_topology(FakeClient([error]))
        self.assertEqual(result.outcome, "PERMISSION_DENIED")
        self.assertEqual(result.diagnostics[0]["http_status"], 403)
        self.assertEqual(result.diagnostics[0]["api_codes"], [4002])
        self.assertEqual(result.diagnostics[0]["api_message"], "Insufficient permissions.")
        self.assertIsNone(result.diagnostics[0]["portal_id"])
        self.assertEqual(result.portals, [])

    def test_authentication_failure_preserves_prior_portals(self):
        client = FakeClient([page([18], True), ApiError("authentication", "Invalid API key.", 401, (4022,))])
        result = discover_topology(client, page_size=1)
        self.assertEqual(result.outcome, "AUTHENTICATION_FAILED")
        self.assertFalse(result.complete)
        self.assertEqual([p.id for p in result.portals], ["18"])
        self.assertEqual(len(client.calls), 2)

    def test_request_budget_retains_exact_budget_and_partial_topology(self):
        budget = BudgetExceeded("HTTP attempt budget reached.", requests=1, max_requests=1,
                                elapsed_seconds=2.0, max_runtime_seconds=1200.0)
        result = discover_topology(FakeClient([page([1, 5], True), budget]), page_size=2)
        self.assertEqual(result.outcome, "REQUEST_BUDGET_REACHED")
        self.assertFalse(result.complete)
        self.assertEqual([p.id for p in result.portals], ["1", "5"])
        self.assertEqual(result.diagnostics[0]["requests"], 1)
        self.assertEqual(result.diagnostics[0]["max_requests"], 1)
        self.assertEqual(result.diagnostics[0]["elapsed_seconds"], 2.0)

    def test_time_budget_is_distinct(self):
        budget = BudgetExceeded("Runtime budget reached.", "TIME_BUDGET_REACHED",
                                requests=7, max_requests=500, elapsed_seconds=1200, max_runtime_seconds=1200)
        result = discover_topology(FakeClient([budget]))
        self.assertEqual(result.outcome, "TIME_BUDGET_REACHED")
        self.assertEqual(result.diagnostics[0]["max_runtime_seconds"], 1200)
        self.assertEqual(result.portals, [])

    def test_interrupt_preserves_topology_and_marks_global_stop(self):
        client = FakeClient([page([5, 6], True), KeyboardInterrupt()])
        result = discover_topology(client, page_size=2)
        self.assertEqual(result.outcome, "INTERRUPTED")
        self.assertFalse(result.complete)
        self.assertEqual([p.id for p in result.portals], ["5", "6"])
        self.assertEqual(result.diagnostics[-1]["cause"], "user_interruption")

    def test_progress_interrupt_still_returns_partial_result(self):
        events = []
        def progress(event):
            events.append(event)
            if event["portals_observed"]:
                raise KeyboardInterrupt()
        result = discover_topology(FakeClient([page([5, 6], True)]), page_size=2, progress=progress)
        self.assertEqual(result.outcome, "INTERRUPTED")
        self.assertEqual(len(result.portals), 2)

    def test_repeat_page_stops_without_repeating_identifiers(self):
        client = FakeClient([page([1, 2], True), page([1, 2], True)])
        result = discover_topology(client, page_size=2)
        self.assertEqual(result.outcome, "INCOMPLETE")
        self.assertEqual(len(result.portals), 2)
        self.assertEqual(len(client.calls), 2)

    def test_overlap_page_retains_new_identifiers_but_cannot_complete(self):
        result = discover_topology(FakeClient([page([1, 2], True), page([2, 3])]), page_size=2)
        self.assertFalse(result.complete)
        self.assertEqual(result.outcome, "INCOMPLETE")
        self.assertEqual([p.id for p in result.portals], ["1", "2", "3"])

    def test_duplicate_inside_page_is_incomplete(self):
        result = discover_topology(FakeClient([page([1, 1])]))
        self.assertEqual(result.outcome, "INCOMPLETE")
        self.assertEqual(len(result.portals), 1)

    def test_missing_portals_wrapper_does_not_mean_zero_complete(self):
        result = discover_topology(FakeClient([{"list_info": {"has_more_rows": False}}]))
        self.assertEqual(result.outcome, "PARSE_ERROR")
        self.assertFalse(result.complete)
        self.assertEqual(result.pages, 0)

    def test_invalid_rows_retain_valid_ids_without_raw_records(self):
        response = page([7])
        response["portals"].extend([{"id": "unsafe-id", "description": "Private content"}, None])
        result = discover_topology(FakeClient([response]))
        self.assertEqual(result.outcome, "PARSE_ERROR")
        self.assertEqual([p.id for p in result.portals], ["7"])
        self.assertNotIn("unsafe-id", json.dumps(asdict(result)))
        self.assertNotIn("Private content", json.dumps(asdict(result)))

    def test_missing_pagination_retains_portals_without_completeness_claim(self):
        result = discover_topology(FakeClient([{"portals": [{"id": "1", "name": "IT"}]}]))
        self.assertFalse(result.complete)
        self.assertEqual(result.outcome, "PARSE_ERROR")
        self.assertEqual(len(result.portals), 1)

    def test_string_booleans_and_counts_from_older_envelopes(self):
        response = page([7], "false", "1", row_count="1", total_count="1")
        result = discover_topology(FakeClient([response]))
        self.assertTrue(result.complete)

    def test_contradictory_pagination_stays_incomplete(self):
        responses = [
            page([1], False, 2), page([1], False, row_count=2),
            page([1], False, total_count=8), page([], True), page([1], True, total_count=1),
        ]
        for response in responses:
            with self.subTest(response=response):
                result = discover_topology(FakeClient([response]))
                self.assertFalse(result.complete)
                self.assertEqual(result.outcome, "INCOMPLETE")

    def test_total_change_cannot_certify_complete(self):
        result = discover_topology(FakeClient([
            page([1], True, total_count=2), page([2], False, total_count=3),
        ]), page_size=1)
        self.assertFalse(result.complete)
        self.assertEqual(result.outcome, "INCOMPLETE")

    def test_scanner_portal_limit_stops_without_an_extra_request(self):
        client = FakeClient([page([2, 9], True)])
        result = discover_topology(client, max_portals=2)
        self.assertEqual(result.outcome, "RECORD_LIMIT_REACHED")
        self.assertEqual(len(result.portals), 2)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(json.loads(client.calls[0]["params"]["input_data"])["list_info"]["row_count"], 2)

    def test_limit_exactly_equal_to_complete_directory_is_complete(self):
        result = discover_topology(FakeClient([page([2, 9])]), max_portals=2)
        self.assertTrue(result.complete)
        self.assertEqual(result.outcome, "COMPLETE")

    def test_oversized_response_does_not_exceed_limit(self):
        result = discover_topology(FakeClient([page([1, 2, 3])]), max_portals=2)
        self.assertEqual(result.outcome, "RECORD_LIMIT_REACHED")
        self.assertEqual(len(result.portals), 2)

    def test_safe_metadata_omits_owners_tokens_urls_and_descriptions(self):
        response = page([8])
        response["portals"][0].update({
            "name": "HR\x1b\n portal", "type": {"internal_name": "Facilities", "id": "3"},
            "status": {"internal_name": "Pre-Production", "id": "2"},
            "license_details": {"edition": "Enterprise", "private-license-key": "license-secret"},
            "owners": [{"name": "A Person", "email": "private@example.test"}],
            "description": "Private ticket content", "image_token": "private-image-token",
            "logo_url": {"content-url": "https://example.test/private-file.png"},
        })
        result = discover_topology(FakeClient([response]))
        portal = result.portals[0]
        self.assertEqual(portal.name, "HR portal")
        self.assertEqual(portal.instance_type, "Facilities")
        self.assertEqual(portal.state, "Pre-Production")
        self.assertEqual(portal.edition, "Enterprise")
        self.assertIsNone(portal.active)
        serialized = json.dumps(asdict(result))
        for private in ["A Person", "private@example.test", "Private ticket content", "private-image-token", "private-file.png", "license-secret"]:
            self.assertNotIn(private, serialized)

    def test_explicit_active_flag_only(self):
        response = page([8, 9])
        response["portals"][0].update(status={"id": "1"}, is_active=False)
        response["portals"][1].update(status={"id": "2"}, active="true")
        result = discover_topology(FakeClient([response]))
        self.assertFalse(result.portals[0].active)
        self.assertTrue(result.portals[1].active)
        self.assertIsNone(result.portals[0].state)

    def test_progress_marks_collecting_and_topology_phase(self):
        events = []
        discover_topology(FakeClient([page([1], True), page([3])]), page_size=1, progress=events.append)
        paging = next(event for event in events if event["event"] == "discovery_page")
        self.assertEqual(paging["outcome"], "COLLECTING")
        self.assertFalse(paging["complete"])
        self.assertEqual(events[-1]["outcome"], "COMPLETE")
        self.assertTrue(all(event["phase"] == "topology" for event in events))
        self.assertFalse(any("records" in event or "response" in event for event in events))

    def test_documentation_qualification_is_retained(self):
        result = discover_topology(FakeClient([page([1])]))
        self.assertTrue(any("not located" in note and "ManageEngine" in note for note in result.limitations))

    def test_invalid_limits_fail_before_network(self):
        for kwargs in [{"page_size": 0}, {"page_size": 1001}, {"page_size": True}, {"max_portals": -1}]:
            with self.subTest(kwargs=kwargs):
                client = FakeClient([])
                with self.assertRaises(ValueError):
                    discover_topology(client, **kwargs)
                self.assertEqual(client.calls, [])


class Response(io.BytesIO):
    def __init__(self, payload):
        super().__init__(json.dumps(payload).encode("utf-8"))
        self.headers = email.message.Message()

    def getcode(self):
        return 200


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, duration):
        self.now += duration


class TopologyTransportIntegrationTests(unittest.TestCase):
    def test_global_discovery_shares_scheduler_omits_default_portal_and_redacts_key(self):
        secret = "topology-private-key-4db1a9"
        first = page([1], True)
        first["portals"][0]["name"] = f"IT {secret}"
        pending = [Response(first), Response(page([3])), Response({"requests": []}), Response({"requests": []})]
        clock = Clock()
        calls = []
        class Opener:
            def open(self, request, timeout):
                calls.append((clock(), request))
                return pending.pop(0)
        client = ReadOnlyClient("https://sdp.example.test", secret, [r"/portals", r"/requests"],
                                portal_id="999", clock=clock, sleep=clock.sleep)
        client._opener = Opener()
        result = discover_topology(client, page_size=1)
        for portal in result.portals:
            client.get_json("/requests", portal_id=portal.id, endpoint_name="requests", module="requests")
        self.assertEqual([time for time, _ in calls], [0.0, 2.0, 4.0, 6.0])
        self.assertEqual([request.get_header("Portalid") for _, request in calls], [None, None, "1", "3"])
        self.assertTrue(all(request.get_method() == "GET" and request.data is None for _, request in calls))
        self.assertTrue(all(secret not in request.full_url for _, request in calls))
        self.assertNotIn(secret, json.dumps(asdict(result)))
        self.assertEqual(client.stats["requests"], 4)


if __name__ == "__main__":
    unittest.main()
