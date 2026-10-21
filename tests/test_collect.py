import unittest

from sdp_audit.collect import CollectionOptions, Collector, select_details
from sdp_audit.models import Dataset, ResourceSpec, Snapshot
from sdp_audit.transport import ApiError, BudgetExceeded


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.stats = {"requests": 0}
        self.calls = []

    def get_json(self, path, params=None):
        self.stats["requests"] += 1
        self.calls.append((path, params))
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


SPEC = ResourceSpec("requests", "/requests", "requests", "request", "https://example.invalid/docs", detail=False)


def page(ids, more, total=None):
    info = {"has_more_rows": more}
    if total is not None:
        info["total_count"] = total
    return {"requests": [{"id": str(i)} for i in ids], "list_info": info}


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = Snapshot("2026-10-05T17:00:00+00:00", {}, {"max_requests": 50})

    def collect(self, responses, cap=0):
        client = FakeClient(responses)
        collector = Collector(client, [SPEC], CollectionOptions(page_size=2, max_records=cap, subresource_parents=0))
        return collector.collect(self.snapshot), client

    def test_one_based_complete_pagination(self):
        import json
        result, client = self.collect([page([1, 2], True, 3), page([3], False, 3)])
        ds = result.datasets["requests"]
        self.assertTrue(ds.list_complete)
        self.assertEqual(len(ds.records), 3)
        self.assertEqual(json.loads(client.calls[1][1]["input_data"])["list_info"]["start_index"], 3)

    def test_limit_is_partial_not_empty_success(self):
        result, _ = self.collect([page([1, 2], True, 200)], cap=2)
        ds = result.datasets["requests"]
        self.assertFalse(ds.list_complete)
        self.assertEqual(ds.status, "partial")
        self.assertEqual(ds.total_count, 200)

    def test_missing_wrapper_is_unknown_not_zero(self):
        result, _ = self.collect([{"other": [], "list_info": {"has_more_rows": False}}])
        self.assertEqual(result.datasets["requests"].status, "invalid_response")
        self.assertFalse(result.datasets["requests"].list_complete)

    def test_repeated_page_stops(self):
        result, client = self.collect([page([1, 2], True), page([1, 2], True)])
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(len(result.datasets["requests"].records), 2)
        self.assertFalse(result.datasets["requests"].list_complete)

    def test_overlap_not_certified_complete(self):
        result, _ = self.collect([page([1, 2], True), page([2, 3], False)])
        self.assertFalse(result.datasets["requests"].list_complete)
        self.assertEqual(len(result.datasets["requests"].records), 3)

    def test_total_mismatch_stays_partial(self):
        result, _ = self.collect([page([1], False, 5)])
        self.assertFalse(result.datasets["requests"].list_complete)

    def test_missing_pagination_does_not_claim_complete(self):
        result, _ = self.collect([{"requests": [{"id": "1"}]}])
        self.assertFalse(result.datasets["requests"].list_complete)

    def test_auth_error_stops_other_reads(self):
        client = FakeClient([ApiError("authentication", "Invalid credential")])
        second = ResourceSpec("users", "/users", "users", "user", "https://example.invalid/docs", detail=False)
        collector = Collector(client, [SPEC, second], CollectionOptions(subresource_parents=0))
        collector.collect(self.snapshot)
        self.assertEqual(client.stats["requests"], 1)
        self.assertIsNotNone(self.snapshot.interrupted_reason)
        self.assertEqual(self.snapshot.datasets["users"].status, "not_attempted")

    def test_budget_writes_partial_snapshot(self):
        result, _ = self.collect([page([1, 2], True), BudgetExceeded("done")])
        self.assertIsNotNone(result.interrupted_reason)
        self.assertEqual(len(result.datasets["requests"].records), 2)

    def test_safe_detail_selection_no_duplicates(self):
        rows = [{"id": str(i)} for i in range(100)]
        selected = select_details(rows, 20)
        self.assertEqual(len(selected), 20)
        self.assertEqual(len({r["id"] for r in selected}), 20)
        self.assertIn(rows[0], selected)
        self.assertIn(rows[-1], selected)


if __name__ == "__main__":
    unittest.main()
