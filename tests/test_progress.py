"""Prevent active pagination, denied reads and detail sampling being called complete."""

import contextlib
import copy
import io
import unittest

from sdp_audit.collect import CollectionOptions, Collector
from sdp_audit.models import Dataset, ResourceSpec, Snapshot
from sdp_audit.progress import ProgressPrinter, print_coverage_summary
from sdp_audit.transport import ApiError


class _Client:
    def __init__(self, responses):
        self.responses = list(responses)
        self.stats = {"requests": 0, "elapsed_seconds": 0.0}

    def get_json(self, path, params=None):
        self.stats["requests"] += 1
        self.stats["elapsed_seconds"] += 2
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


def _page(ids, more, total):
    return {"requests": [{"id": str(item)} for item in ids],
            "list_info": {"has_more_rows": more, "total_count": total}}


class ProgressTests(unittest.TestCase):
    def _collect(self, responses, *, cap=0, details=False):
        output = io.StringIO()
        snapshot = Snapshot("2026-10-07T15:00:00+00:00", {}, {"max_requests": 100})
        spec = ResourceSpec("requests", "/requests", "requests", "request", "", detail=details)
        client = _Client(responses)
        events = []
        printer = ProgressPrinter(100)

        def progress(event):
            events.append(copy.deepcopy(event))
            printer(event)

        with contextlib.redirect_stdout(output):
            Collector(client, [spec], CollectionOptions(page_size=2, max_records=cap,
                                                        subresource_parents=0),
                      progress=progress).collect(snapshot)
        return snapshot, output.getvalue(), events

    def test_active_pages_are_collecting_without_changing_stored_partial(self):
        snapshot, output, events = self._collect([_page([1, 2], True, 3), _page([3], False, 3)])
        list_events = [event for event in events if event["event"] == "collection"]
        self.assertEqual([event["status"] for event in list_events], ["partial", "complete"])
        self.assertEqual([event["more_pages"] for event in list_events], [True, False])
        self.assertTrue(snapshot.datasets["requests"].list_complete)
        self.assertIn("2 records observed / 3 API-reported total; collecting; more pages queued", output)
        self.assertIn("3 records observed / 3 API-reported total; list complete for API-visible scope", output)
        self.assertNotIn("incomplete", output)
        self.assertIn("2/100 HTTP attempts", output)

    def test_record_cap_is_final_incomplete_despite_server_having_more(self):
        snapshot, output, events = self._collect([_page([1, 2], True, 50)], cap=2)
        dataset = snapshot.datasets["requests"]
        self.assertFalse(dataset.list_complete)
        self.assertEqual(dataset.status, "partial")
        event = next(event for event in events if event["event"] == "collection")
        self.assertFalse(event["more_pages"])
        self.assertIn("incomplete; configured record limit reached", output)
        self.assertNotIn("collecting; more pages queued", output)

    def test_denied_read_does_not_turn_zero_observations_into_empty_inventory(self):
        snapshot, output, _ = self._collect([ApiError("forbidden", "PRIVATE RESPONSE MUST NOT PRINT")])
        self.assertEqual(snapshot.datasets["requests"].status, "forbidden")
        self.assertIn("no records read; access denied; count unknown", output)
        self.assertNotIn("0 records observed", output)
        self.assertNotIn("PRIVATE RESPONSE", output)
        summary = io.StringIO()
        with contextlib.redirect_stdout(summary):
            print_coverage_summary(snapshot, {"requests"})
        self.assertIn("Parent lists unavailable or not attempted: 1/1", summary.getvalue())
        self.assertIn("requests: access denied; count unknown", summary.getvalue())

    def test_empty_complete_list_is_always_qualified_by_api_scope(self):
        snapshot, output, _ = self._collect([_page([], False, 0)])
        self.assertTrue(snapshot.datasets["requests"].list_complete)
        self.assertIn("list complete for API-visible scope; no visible rows returned", output)
        self.assertNotIn("module unused", output)

    def test_list_complete_survives_detail_failure_but_summary_exposes_detail_gap(self):
        snapshot, _, _ = self._collect([
            _page([1], False, 1), ApiError("forbidden", "PRIVATE DETAIL RESPONSE"),
        ], details=True)
        dataset = snapshot.datasets["requests"]
        self.assertTrue(dataset.list_complete)
        self.assertEqual(dataset.detail_attempted, 1)
        self.assertEqual(dataset.detail_succeeded, 0)
        snapshot.interrupted_reason = "Configured request/time budget reached; report is partial."
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_coverage_summary(snapshot, {"requests"})
        text = output.getvalue()
        self.assertIn("Parent lists complete: 1/1", text)
        self.assertIn("Parent record details: 0 successful / 1 attempted", text)
        self.assertIn("a complete list does not certify full detail coverage", text)
        self.assertIn("Run ended early: configured request/time budget reached", text)
        self.assertNotIn("PRIVATE DETAIL", text)

    def test_child_parent_visits_are_not_counted_as_parent_record_detail_reads(self):
        snapshot = Snapshot("2026-10-07T15:00:00+00:00", {}, {})
        snapshot.datasets["requests"] = Dataset("requests", "/requests", status="complete",
                                                 list_complete=True, detail_attempted=4, detail_succeeded=3)
        snapshot.datasets["request_notes"] = Dataset("request_notes", "/requests/{id}/notes",
                                                      status="partial", detail_attempted=10, detail_succeeded=8)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_coverage_summary(snapshot, {"requests"})
        self.assertIn("Parent record details: 3 successful / 4 attempted", output.getvalue())
        self.assertIn("request_notes: 8/10 selected parent lists read completely", output.getvalue())
        self.assertIn("other coverage unknown", output.getvalue())

    def test_quiet_hides_live_output_but_not_final_coverage(self):
        printer = ProgressPrinter(100, quiet=True)
        snapshot = Snapshot("2026-10-07T15:00:00+00:00", {}, {})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            printer({"event": "phase", "phase": "inventory"})
            printer({"event": "retry", "kind": "throttled", "delay_seconds": 30})
            print_coverage_summary(snapshot, {"projects"})
        self.assertNotIn("Listing API-visible", output.getvalue())
        self.assertNotIn("Server rate limit", output.getvalue())
        self.assertIn("projects: not attempted; count unknown", output.getvalue())

    def test_retry_heartbeat_and_measurements_are_safe_and_rate_limited(self):
        printer = ProgressPrinter(100)
        output = io.StringIO()
        private = "PRIVATE_SERVER_STRING"
        with contextlib.redirect_stdout(output):
            printer({"event": "phase", "phase": "details", "elapsed_seconds": 0})
            for second in range(31):
                printer({"event": "wait", "elapsed_seconds": second, "remaining_seconds": 30 - second,
                         "requests": 10, "url": private, "message": private})
            printer({"event": "details", "elapsed_seconds": 30, "key": "requests", "details": 7})
            printer({"event": "retry", "kind": "throttled", "elapsed_seconds": 31, "delay_seconds": 25,
                     "api_key": private, "message": private})
            printer({"event": "collection", "key": private, "status": "partial", "records": 2,
                     "more_pages": False, "issues": [private], "elapsed_seconds": float("nan")})
        text = output.getvalue()
        self.assertEqual(text.count("Paced wait before the next GET"), 2)
        self.assertIn("7 successful detail reads", text)
        self.assertIn("Server rate limit; waiting at least 25 seconds before retrying", text)
        self.assertNotIn(private, text)
        self.assertNotIn("nan", text)


if __name__ == "__main__":
    unittest.main()
