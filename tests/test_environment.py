"""Environment orchestration invariants independent of API response fixtures."""

import contextlib
import io
import json
import unittest
from dataclasses import replace

from sdp_audit.catalog import RESOURCES
from sdp_audit.collect import CollectionOptions
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.models import EnvironmentSnapshot
from sdp_audit.progress import ProgressPrinter
from sdp_audit.transport import ApiError, BudgetExceeded


class Client:
    def __init__(self, portals=("7", "42"), rows=None, errors=None, maximum=1000,
                 runtime=2000, interrupt_at=None):
        self.portals = list(portals)
        self.rows = rows or {}
        self.errors = errors or {}
        self.maximum, self.runtime = maximum, runtime
        self.interrupt_at = interrupt_at
        self.calls = []
        self.last_response = {}
        self.base_url = "https://synthetic.example.invalid"
        self._successes = 0

    @property
    def stats(self):
        counts = {}
        for call in self.calls:
            scope = "portal:" + call["portal_id"] if call["portal_id"] is not None else "global"
            counts[scope] = counts.get(scope, 0) + 1
        return {"requests": len(self.calls), "max_requests": self.maximum,
                "elapsed_seconds": len(self.calls) * 2, "requests_by_scope": counts,
                "authentication": "valid" if self._successes else "unverified"}

    def get_json(self, path, params=None, *, portal_id, endpoint_name=None, module=None):
        if len(self.calls) >= self.maximum:
            raise BudgetExceeded("Synthetic request budget reached", "REQUEST_BUDGET_REACHED")
        if len(self.calls) * 2 >= self.runtime:
            raise BudgetExceeded("Synthetic time budget reached", "TIME_BUDGET_REACHED")
        data = json.loads((params or {}).get("input_data", "{}"))
        info = data.get("list_info", {})
        start, count = int(info.get("start_index", 1)), int(info.get("row_count", 100))
        self.calls.append({"path": path, "portal_id": portal_id, "endpoint_name": endpoint_name,
                           "module": module, "start": start, "count": count, "input_data": data})
        if len(self.calls) == self.interrupt_at:
            raise KeyboardInterrupt
        error = self.errors.get((portal_id, path, start), self.errors.get((portal_id, path)))
        if error:
            error.portal_id, error.endpoint, error.endpoint_name, error.module = portal_id, path, endpoint_name, module
            self.last_response = error.to_dict()
            raise error
        if path == "/portals":
            rows = [{"id": value, "name": "Portal " + value, "type": {"name": "IT"},
                     "status": {"name": "Production"}} for value in self.portals]
            wrapper = "portals"
        elif path == "/orgusers":
            rows = self.rows.get((None, "orgusers"), [{"id": "800"}, {"id": "801"}])
            wrapper = "orgusers"
        else:
            spec = next((item for item in RESOURCES if path == item.path), None)
            if spec is None:
                parts = path.split("/")
                spec = next((item for item in RESOURCES if len(parts) == 3 and "/" + parts[1] == item.path), None)
                if spec and parts[-1].isdigit():
                    rows = self.rows.get((portal_id, spec.key), [])
                    row = next((row for row in rows if row.get("id") == parts[-1]), {"id": parts[-1]})
                    self._successes += 1
                    self.last_response = {"http_status": 200, "api_codes": [2000], "classification": "SUCCESS"}
                    return {spec.singular: dict(row)}
                raise ApiError("unsupported", "Synthetic endpoint unsupported", 404, (4007,),
                               portal_id=portal_id, endpoint=path, endpoint_name=endpoint_name, module=module)
            rows = self.rows.get((portal_id, spec.key), [])
            wrapper = spec.plural
        selected = [dict(row) for row in rows[start - 1:start - 1 + count]]
        self._successes += 1
        self.last_response = {"http_status": 200, "api_codes": [2000], "classification": "SUCCESS"}
        return {wrapper: selected, "list_info": {"start_index": start, "row_count": len(selected),
                                                 "total_count": len(rows), "has_more_rows": start - 1 + len(selected) < len(rows)}}


def scan(client, keys=("requests", "projects"), *, ids=None, page_size=100, cap=0,
         fraction=1.0, details=False, fields=False, progress=None):
    resources = [replace(item, detail=details) for item in RESOURCES if item.key in keys]
    env = EnvironmentSnapshot("2026-10-07T12:00:00+00:00", {"host": client.base_url, "demo": True},
                              {"max_requests": client.maximum, "rpm": 30})
    collector = EnvironmentCollector(client, resources,
        CollectionOptions(page_size=page_size, max_records=cap, detail_limit=20,
                          subresource_parents=0, inventory_budget_fraction=fraction),
        EnvironmentOptions(discover_fields=fields, collect_orgusers=True), progress=progress)
    return collector.collect(env, ids)


class EnvironmentTests(unittest.TestCase):
    def test_auto_discovery_scans_every_observed_id_without_guessing(self):
        client = Client()
        env = scan(client)
        self.assertEqual(set(env.portals), {"7", "42"})
        self.assertEqual({call["portal_id"] for call in client.calls if call["path"] != "/portals"}, {"7", "42"})
        self.assertTrue(all(item.portal.accessible for item in env.portals.values()))
        self.assertEqual(env.stats["global_limiter_instances"], 1)

    def test_first_capability_page_is_reused_without_duplicate_list_reads(self):
        client = Client()
        env = scan(client)
        for portal in ("7", "42"):
            for path in ("/requests", "/projects"):
                self.assertEqual(sum(call["path"] == path and call["portal_id"] == portal for call in client.calls), 1)
        self.assertEqual(env.portals["7"].snapshot.capabilities["projects"]["availability"], "AVAILABLE")

    def test_global_directory_is_once_and_separate_from_portal_memberships(self):
        client = Client(rows={("7", "users"): [{"id": "800"}], ("42", "users"): [{"id": "800"}]})
        env = scan(client, ("users",))
        calls = [call for call in client.calls if call["path"] == "/orgusers"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["portal_id"], "7")
        self.assertEqual(env.global_snapshot.datasets["orgusers"].scope, "environment")
        self.assertIsNone(env.global_snapshot.datasets["orgusers"].portal_id)
        self.assertTrue(all("orgusers" not in item.snapshot.datasets for item in env.portals.values()))
        assessment = analyze_environment(env)
        global_rows = [row for row in assessment.coverage if row.get("resource") == "orgusers"]
        self.assertEqual(len(global_rows), 1)
        self.assertEqual(global_rows[0]["records_observed"], 2)

    def test_single_portal_does_not_query_multi_instance_orguser_operation(self):
        client = Client(portals=("42",))
        env = scan(client)
        self.assertIsNone(env.global_snapshot)
        self.assertFalse(any(call["path"] == "/orgusers" for call in client.calls))

    def test_explicit_override_skips_discovery_and_environment_directory(self):
        client = Client()
        env = scan(client, ids=["42"])
        self.assertEqual(list(env.portals), ["42"])
        self.assertTrue(all(call["portal_id"] == "42" for call in client.calls))
        self.assertFalse(any(call["path"] in {"/portals", "/orgusers"} for call in client.calls))

    def test_repeated_explicit_ids_are_deduplicated(self):
        client = Client()
        env = scan(client, ids=["7", "042", "42", "7"])
        self.assertEqual(list(env.portals), ["7", "42"])
        self.assertEqual(len(client.calls), 4)

    def test_discovery_unavailable_does_not_assume_default(self):
        client = Client(errors={(None, "/portals"): ApiError("unsupported", "Unsupported", 404, (4007,))})
        env = scan(client)
        self.assertEqual(env.portals, {})
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(env.stop_classification, "PORTAL_DISCOVERY_UNAVAILABLE")
        self.assertIn("--portal-id", env.interrupted_reason)

    def test_explicit_portal_inaccessible_does_not_abort_other_portals(self):
        client = Client(errors={("7", "/requests"): ApiError("portal_access", "Portal is not accessible", 403, (4002,))})
        env = scan(client)
        self.assertFalse(env.portals["7"].portal.accessible)
        self.assertTrue(env.portals["42"].portal.accessible)
        self.assertFalse(any(call["portal_id"] == "7" and call["path"] == "/projects" for call in client.calls))
        ds = env.portals["7"].snapshot.datasets["projects"]
        self.assertEqual(ds.outcome, "NOT_STARTED")
        self.assertIsNone(ds.coverage()["records_observed"])

    def test_generic_project_403_is_operation_specific_and_retains_codes(self):
        client = Client(errors={("42", "/projects"): ApiError("forbidden", "Operation denied", 403, (4002,))})
        env = scan(client)
        portal = env.portals["42"]
        self.assertTrue(portal.portal.accessible)
        ds = portal.snapshot.datasets["projects"]
        self.assertEqual(ds.outcome, "PERMISSION_DENIED")
        self.assertEqual(ds.diagnostics[0]["http_status"], 403)
        self.assertEqual(ds.diagnostics[0]["api_codes"], [4002])
        self.assertEqual(ds.diagnostics[0]["portal_id"], "42")
        self.assertEqual(ds.diagnostics[0]["module"], "projects")
        self.assertIsNone(ds.coverage()["records_observed"])
        self.assertNotIn("Project Admin", json.dumps(analyze_environment(env).to_dict()))

    def test_module_license_denial_is_unknown_count_not_empty(self):
        client = Client(errors={("42", "/projects"): ApiError("license", "Not allowed by license", 400, (7001,))})
        env = scan(client)
        ds = env.portals["42"].snapshot.datasets["projects"]
        self.assertEqual(ds.outcome, "MODULE_NOT_AVAILABLE")
        self.assertEqual(ds.capability, "MODULE_NOT_AVAILABLE")
        self.assertFalse(ds.list_complete)
        self.assertIsNone(ds.coverage()["records_observed"])

    def test_empty_success_is_complete_only_for_visible_scope(self):
        env = scan(Client())
        ds = env.portals["7"].snapshot.datasets["projects"]
        self.assertEqual(ds.outcome, "EMPTY")
        self.assertTrue(ds.list_complete)
        self.assertEqual(ds.coverage()["records_observed"], 0)

    def test_pagination_is_independent_and_fair_across_portals(self):
        rows = {(pid, "requests"): [{"id": str(i)} for i in range(1, total + 1)]
                for pid, total in (("7", 5), ("42", 3))}
        client = Client(rows=rows)
        env = scan(client, ("requests",), page_size=2)
        calls = [(call["portal_id"], call["start"]) for call in client.calls if call["path"] == "/requests"]
        self.assertEqual(calls, [("7", 1), ("42", 1), ("7", 3), ("42", 3), ("7", 5)])
        for pid, count in (("7", 5), ("42", 3)):
            ds = env.portals[pid].snapshot.datasets["requests"]
            self.assertTrue(ds.list_complete)
            self.assertEqual(len(ds.records), count)
            self.assertTrue(all(row["_portal_id"] == pid for row in ds.records))

    def test_progress_collecting_and_portal_names_during_paging(self):
        client = Client(rows={("7", "requests"): [{"id": str(i)} for i in range(3)]})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            scan(client, ("requests",), page_size=2, progress=ProgressPrinter(1000))
        value = output.getvalue()
        self.assertIn('Portal "Portal 7" [7] / requests', value)
        self.assertIn("collecting; more pages queued", value)
        self.assertNotIn("; partial", value)
        for phase in range(1, 6):
            self.assertIn(f"Phase {phase}/5", value)

    def test_record_cap_preserves_observations_without_false_completion(self):
        client = Client(rows={("7", "requests"): [{"id": str(i)} for i in range(8)]})
        env = scan(client, ("requests",), cap=3, page_size=2)
        ds = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(ds.outcome, "RECORD_LIMIT_REACHED")
        self.assertEqual(len(ds.records), 3)
        self.assertFalse(ds.list_complete)
        self.assertTrue(env.portals["42"].snapshot.datasets["requests"].list_complete)

    def test_request_budget_keeps_completed_collections_and_unknown_unstarted(self):
        client = Client(maximum=3)
        env = scan(client)
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")
        for item in env.portals.values():
            self.assertTrue(item.snapshot.datasets["requests"].list_complete)
            ds = item.snapshot.datasets["projects"]
            self.assertEqual(ds.outcome, "NOT_STARTED")
            self.assertFalse(ds.read_attempted)
            self.assertIsNone(ds.coverage()["records_observed"])

    def test_time_budget_keeps_completed_collections(self):
        client = Client(runtime=6)
        env = scan(client)
        self.assertEqual(env.stop_classification, "TIME_BUDGET_REACHED")
        self.assertTrue(env.portals["7"].snapshot.datasets["requests"].list_complete)
        self.assertTrue(env.portals["42"].snapshot.datasets["requests"].list_complete)
        self.assertIsNone(env.portals["7"].snapshot.datasets["projects"].coverage()["records_observed"])

    def test_ctrl_c_returns_a_usable_portal_snapshot_and_assessment(self):
        client = Client(interrupt_at=4, rows={("7", "requests"): [{"id": "90"}]})
        env = scan(client)
        self.assertEqual(env.stop_classification, "INTERRUPTED")
        self.assertEqual(len(env.portals["7"].snapshot.datasets["requests"].records), 1)
        result = analyze_environment(env)
        self.assertEqual(len(result.questions), 7)
        self.assertEqual(result.schema_version, "2.0")
        self.assertEqual(len(result.portals), 2)

    def test_record_provenance_includes_details_and_scoped_module(self):
        client = Client(portals=("7",), rows={("7", "requests"): [{"id": "1"}]})
        env = scan(client, ("requests",), details=True)
        ds = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(ds.details[0]["_portal_id"], "7")
        self.assertEqual(ds.details[0]["_module"], "requests")
        self.assertTrue(ds.detail_complete)

    def test_final_budget_with_pending_pages_is_exhaustion_not_reservation(self):
        client = Client(portals=("7",), maximum=2,
                        rows={("7", "requests"): [{"id": str(i)} for i in range(4)]})
        env = scan(client, ("requests",), page_size=2)
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")
        ds = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(ds.stop_reason, "REQUEST_BUDGET_REACHED")
        self.assertEqual(ds.outcome, "INCOMPLETE")
        self.assertEqual(len(ds.records), 2)

    def test_sampling_reservation_is_distinct_from_global_exhaustion(self):
        client = Client(portals=("7",), maximum=10,
                        rows={("7", "requests"): [{"id": str(i)} for i in range(50)]})
        env = scan(client, ("requests",), page_size=2, fraction=.5)
        self.assertIsNone(env.stop_classification)
        ds = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(ds.stop_reason, "SAMPLING_RESERVATION")
        self.assertEqual(len(ds.records), 8)
        self.assertLess(env.stats["requests"], 10)

    def test_wrong_explicit_portal_in_response_is_not_merged(self):
        client = Client(portals=("7",), rows={("7", "requests"): [{"id": "1", "portal": {"id": "42"}}]})
        env = scan(client, ("requests",))
        ds = env.portals["7"].snapshot.datasets["requests"]
        self.assertEqual(ds.outcome, "PORTAL_CONTEXT_REQUIRED")
        self.assertEqual(ds.records, [])
        self.assertIsNone(ds.coverage()["records_observed"])

    def test_findings_same_numeric_record_id_keep_distinct_portal_identity(self):
        timestamp = {"value": "1514764800000"}
        client = Client(rows={(pid, "requests"): [{"id": "1", "created_time": timestamp}] for pid in ("7", "42")})
        result = analyze_environment(scan(client))
        findings = [f for f in result.findings if f.id.endswith("HISTORY_WINDOW_FIVE_YEARS")]
        self.assertEqual({f.portal_id for f in findings}, {"7", "42"})
        self.assertEqual(sum(f.affected_count or 0 for f in findings), 2)
        self.assertTrue(all(all(e["portal_id"] == f.portal_id for e in f.evidence) for f in findings))


if __name__ == "__main__":
    unittest.main()
