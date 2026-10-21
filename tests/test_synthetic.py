"""End-to-end synthetic assessment checks through the real GET transport."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from sdp_audit.catalog import RESOURCES
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.fields import FieldDiscovery
from sdp_audit.models import Dataset
from sdp_audit.report import write_reports
from sdp_audit.synthetic import (
    SYNTHETIC_KEY, SYNTHETIC_SENSITIVE_MARKERS, SyntheticServer,
    create_synthetic_client, demo_environment, fixture_config, run_synthetic,
)


class SyntheticEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment, cls.server = run_synthetic("multi")
        cls.assessment = analyze_environment(cls.environment)

    def test_default_multi_has_every_portal_and_one_inaccessible_portal(self):
        env = self.environment
        # All portals are discovered; the denied portal retains its unknown
        # inventories rather than being silently removed or reported empty.
        self.assertEqual(list(env.portals), ["1", "2", "3", "4"])
        self.assertTrue(env.topology.complete)
        self.assertEqual([item.portal.name for item in env.portals.values()], ["IT Helpdesk", "HR", "Facilities", "Security"])
        self.assertEqual(sum(item.portal.accessible is True for item in env.portals.values()), 3)
        self.assertFalse(env.portals["4"].portal.accessible)
        self.assertEqual(env.portals["4"].portal.scan_status, "PORTAL_NOT_ACCESSIBLE")
        self.assertIsNone(env.stop_classification)
        self.assertEqual(sum(call["portal_id"] == "4" for call in self.server.calls), 1)

    def test_single_demonstration_has_no_network_or_directory_duplication(self):
        with mock.patch("socket.create_connection", side_effect=AssertionError("No sockets are permitted")) as connect:
            env, server = run_synthetic("single")
        connect.assert_not_called()
        self.assertEqual(list(env.portals), ["1"])
        self.assertFalse(env.stats["network_used"])
        self.assertTrue(env.stats["synthetic_transport"])
        self.assertFalse(any(call["path"] == "/orgusers" for call in server.calls))
        self.assertIsNone(env.global_snapshot)

    def test_calls_are_get_only_and_use_correct_explicit_scope(self):
        calls = self.server.calls
        self.assertTrue(calls)
        for call in calls:
            self.assertEqual(call["method"], "GET")
            self.assertFalse(call["has_body"])
            self.assertTrue(call["has_authtoken"])
            if call["path"] == "/portals":
                self.assertIsNone(call["portal_id"])
            else:
                self.assertIn(call["portal_id"], self.environment.portals)
        self.assertNotIn(SYNTHETIC_KEY, json.dumps(calls))
        self.assertEqual(self.environment.stats["requests"], len(calls))
        self.assertEqual(self.environment.stats["global_limiter_instances"], 1)
        self.assertTrue(all(b["time"] - a["time"] >= 2 for a, b in zip(calls, calls[1:])))

    def test_orgusers_collected_once_and_uses_one_request_context(self):
        calls = [call for call in self.server.calls if call["path"] == "/orgusers"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["portal_id"], "1")
        self.assertEqual(len(self.environment.global_snapshot.datasets["orgusers"].records), 2)
        rows = [row for row in self.assessment.coverage if row["key"] == "orgusers"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["scope"], "environment")
        self.assertIsNone(rows[0]["portal_id"])

    def test_mixed_module_errors_are_not_empty_collections(self):
        hr_projects = self.environment.portals["2"].snapshot.datasets["projects"]
        facilities_releases = self.environment.portals["3"].snapshot.datasets["releases"]
        self.assertEqual(hr_projects.outcome, "PERMISSION_DENIED")
        self.assertEqual(hr_projects.diagnostics[0]["http_status"], 403)
        self.assertEqual(hr_projects.diagnostics[0]["api_codes"], [4002])
        self.assertTrue(hr_projects.diagnostics[0]["raw_message_omitted"])
        self.assertEqual(facilities_releases.outcome, "MODULE_NOT_AVAILABLE")
        for dataset in (hr_projects, facilities_releases):
            self.assertIsNone(dataset.coverage()["records_observed"])
            self.assertFalse(dataset.list_complete)

    def test_module_and_portal_provenance_survives_metadata(self):
        for portal_id in ("1", "2"):
            fields = self.environment.portals[portal_id].snapshot.fields["requests"]
            self.assertTrue(fields.form_scope_complete)
            self.assertFalse(fields.registry_complete)
            self.assertEqual(fields.metadata_targets_successful, 2)
            for definition in fields.fields:
                self.assertEqual(definition.portal_id, portal_id)
                self.assertEqual(definition.module, "requests")
            reference = next(item for item in fields.fields if item.internal_name == "udf_char1")
            self.assertEqual(len(reference.contexts), 2)
            self.assertEqual(reference.completeness, "CONTEXT_DEPENDENT")
        self.assertNotEqual(
            next(item.display_label for item in self.environment.portals["1"].snapshot.fields["requests"].fields if item.internal_name == "udf_char1"),
            next(item.display_label for item in self.environment.portals["2"].snapshot.fields["requests"].fields if item.internal_name == "udf_char1"),
        )

    def test_asset_and_change_documented_fallbacks_are_real_gets(self):
        calls = self.server.calls
        hr_asset = [call for call in calls if call["portal_id"] == "2" and call["path"] == "/assets/metainfo"]
        self.assertEqual(len(hr_asset), 1)
        self.assertEqual(hr_asset[0]["input_data"]["template"]["id"], "88")
        self.assertEqual(self.environment.portals["2"].snapshot.fields["assets"].metadata_targets_successful, 1)
        self.assertTrue(any(call["portal_id"] == "3" and call["path"] == "/changes/401/metainfo" for call in calls))
        self.assertTrue(any(call["portal_id"] == "1" and call["path"] == "/custom_asset_demo/_metainfo" for call in calls))

    def test_ci_metadata_uses_only_observed_type_api_name(self):
        calls = [call for call in self.server.calls if call["path"].endswith("/_metadata")]
        self.assertEqual([(call["portal_id"], call["path"]) for call in calls], [("1", "/cmdb_demo/_metadata")])
        inventory = self.environment.portals["1"].snapshot.fields["cis"]
        self.assertGreater(inventory.metadata_targets_successful, 0)
        self.assertFalse(inventory.registry_complete)
        self.assertTrue(all(item.metadata_source == "/cmdb_demo/_metadata" or item.evidence_basis == "INFERRED_FROM_OBSERVED_UDF_KEY" for item in inventory.fields))

    def test_same_record_ids_across_portals_are_not_merged(self):
        requests = next(row for row in self.assessment.environment["volume_by_module"] if row["resource"] == "requests")
        self.assertEqual(requests["records_observed"], 6)
        self.assertEqual(requests["collections_unknown"], 1)
        self.assertEqual(requests["collections_complete"], 3)
        self.assertEqual([self.environment.portals[pid].snapshot.datasets["requests"].records[0]["id"] for pid in ("1", "2", "3")], ["101"] * 3)
        findings = [finding for finding in self.assessment.findings if finding.id.endswith("HISTORY_WINDOW_FIVE_YEARS")]
        self.assertTrue({finding.portal_id for finding in findings}.issuperset({"1", "2", "3"}))

    def test_all_six_reports_omit_every_sensitive_canary(self):
        serialized = json.dumps(self.assessment.to_dict()).casefold()
        for marker in SYNTHETIC_SENSITIVE_MARKERS:
            self.assertNotIn(marker.casefold(), serialized)
        with tempfile.TemporaryDirectory() as temporary:
            paths = write_reports(self.assessment, temporary)
            self.assertEqual(len(paths), 6)
            for filename, path in paths.items():
                content = Path(path).read_text(encoding="utf-8")
                self.assertTrue(content, filename)
                for marker in SYNTHETIC_SENSITIVE_MARKERS:
                    self.assertNotIn(marker.casefold(), content.casefold(), (filename, marker))
            payload = json.loads(Path(paths["assessment.json"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "2.0")
            self.assertEqual(len(payload["portals"]), 4)
            self.assertEqual(len(payload["questions"]), 7)
            self.assertEqual(payload["environment"]["summary"]["portals_inaccessible"], 1)

    def test_explicit_target_uses_no_discovery_or_other_portals(self):
        env, server = run_synthetic("multi", portal_ids=["2"])
        self.assertEqual(list(env.portals), ["2"])
        self.assertEqual(env.topology.mode, "explicit")
        self.assertFalse(any(call["path"] == "/portals" for call in server.calls))
        self.assertTrue(all(call["portal_id"] == "2" for call in server.calls))

    def test_successful_empty_projects_in_single_fixture(self):
        env, _ = run_synthetic("single")
        projects = env.portals["1"].snapshot.datasets["projects"]
        self.assertEqual(projects.outcome, "EMPTY")
        self.assertTrue(projects.list_complete)
        self.assertEqual(projects.coverage()["records_observed"], 0)


class SyntheticScenarioTests(unittest.TestCase):
    def test_fixture_files_match_reusable_scenarios(self):
        root = Path(__file__).parent / "fixtures"
        paths = sorted(root.glob("*.json"))
        self.assertGreaterEqual(len(paths), 11)
        for path in paths:
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(config, fixture_config(config["scenario"]))
            self.assertIsInstance(SyntheticServer(config), SyntheticServer)

    def test_budget_exhaustion_preserves_completed_and_never_started_collections(self):
        env, server = run_synthetic("budget_exhaustion")
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")
        self.assertEqual(env.stats["requests"], 8)
        self.assertEqual(len(server.calls), 8)
        self.assertTrue(env.portals["2"].snapshot.datasets["requests"].list_complete)
        self.assertFalse(env.portals["1"].snapshot.datasets["requests"].list_complete)
        never_started = env.portals["3"].snapshot.datasets["assets"]
        self.assertEqual(never_started.outcome, "NOT_STARTED")
        self.assertIsNone(never_started.coverage()["records_observed"])

    def test_time_budget_preserves_already_complete_list(self):
        env, server = run_synthetic("time_budget")
        self.assertEqual(env.stop_classification, "TIME_BUDGET_REACHED")
        self.assertEqual(len(server.calls), 3)
        self.assertTrue(env.portals["1"].snapshot.datasets["incident_templates"].list_complete)
        self.assertIsNone(env.portals["2"].snapshot.datasets["requests"].coverage()["records_observed"])

    def test_rate_limit_retry_after_is_observed_by_shared_clock(self):
        env, server = run_synthetic("rate_limiting")
        self.assertEqual(env.stats["retries"], 1)
        self.assertEqual(server.calls[0]["path"], "/portals")
        self.assertEqual(server.calls[1]["path"], "/portals")
        self.assertGreaterEqual(server.calls[1]["time"] - server.calls[0]["time"], 7)
        self.assertIsNone(env.stop_classification)

    def test_large_pagination_is_independent_per_portal(self):
        events = []
        env, server = run_synthetic("large_pagination", progress=events.append)
        first = env.portals["1"].snapshot.datasets["requests"]
        second = env.portals["2"].snapshot.datasets["requests"]
        self.assertEqual((len(first.records), len(second.records)), (1207, 613))
        self.assertTrue(first.list_complete and second.list_complete)
        self.assertEqual((first.pages, second.pages), (13, 7))
        pages = [event for event in events if event.get("event") == "collection" and event.get("key") == "requests" and event.get("more_pages")]
        self.assertTrue(pages)
        self.assertTrue(all(event.get("outcome") == "COLLECTING" for event in pages))
        starts = {pid: [call["input_data"]["list_info"]["start_index"] for call in server.calls
                        if call["path"] == "/requests" and call["portal_id"] == pid] for pid in ("1", "2")}
        self.assertEqual(starts["1"], list(range(1, 1300, 100)))
        self.assertEqual(starts["2"], list(range(1, 700, 100)))

    def test_unsupported_discovery_does_not_guess_ids(self):
        env, server = run_synthetic("portal_discovery_unavailable")
        self.assertEqual(env.topology.outcome, "ENDPOINT_UNSUPPORTED")
        self.assertEqual(env.portals, {})
        self.assertEqual(len(server.calls), 1)
        self.assertEqual(server.calls[0]["path"], "/portals")
        self.assertIsNone(server.calls[0]["portal_id"])
        assessment = analyze_environment(env)
        self.assertEqual(assessment.environment["summary"]["portals_discovered"], 0)
        self.assertTrue(assessment.environment["acceptance_blockers"])

    def test_interrupt_returns_a_reportable_partial_environment(self):
        env, _ = run_synthetic("interrupted")
        self.assertEqual(env.stop_classification, "INTERRUPTED")
        self.assertTrue(any(dataset.list_complete for item in env.portals.values() for dataset in item.snapshot.datasets.values()))
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(len(write_reports(analyze_environment(env), temporary)), 6)

    def test_disabled_module_is_distinct_from_denial(self):
        env, _ = run_synthetic("module_not_enabled")
        result = env.portals["1"].snapshot.datasets["problems"]
        self.assertEqual(result.outcome, "MODULE_NOT_ENABLED")
        self.assertIsNone(result.coverage()["records_observed"])

    def test_primary_and_fallback_field_fixtures(self):
        for scenario in ("udf_primary", "udf_fallback"):
            with self.subTest(scenario=scenario):
                env, server = run_synthetic(scenario)
                self.assertGreater(env.portals["1"].snapshot.fields["requests"].metadata_targets_successful, 0)
                self.assertGreater(env.portals["1"].snapshot.fields["assets"].metadata_targets_successful, 0)
                if scenario == "udf_fallback":
                    self.assertTrue(any(call["path"] == "/assets/metainfo" for call in server.calls))
                    self.assertTrue(any(call["path"] == "/changes/401/metainfo" for call in server.calls))

    def test_unsupported_definition_response_remains_a_field_coverage_gap(self):
        env, _ = run_synthetic("unsupported_metadata")
        inventory = env.portals["1"].snapshot.fields["requests"]
        self.assertEqual(inventory.status, "ENDPOINT_UNSUPPORTED")
        self.assertFalse(inventory.registry_complete)
        self.assertEqual(inventory.metadata_targets_successful, 0)
        self.assertTrue(inventory.fields)  # Already observed UDF names retained without invented definitions.
        self.assertTrue(all(item.evidence_basis == "INFERRED_FROM_OBSERVED_UDF_KEY" for item in inventory.fields))

    def test_module_selected_udf_primary_uses_real_allowlisted_transport(self):
        client, server, _ = create_synthetic_client("udf_primary")
        observed_scope = {"space_room": Dataset("space_room", "observed module context", list_complete=True)}
        discovery = FieldDiscovery(client, "1", "IT Helpdesk", observed_scope)
        list(discovery.iter_steps())
        call = next(call for call in server.calls if call["path"] == "/udf_fields")
        self.assertEqual(call["input_data"]["module"]["name"], "space_room")
        self.assertEqual(call["portal_id"], "1")
        inventory = discovery.inventories["space_room"]
        self.assertTrue(inventory.fields)
        self.assertTrue(all(field.module == "space_room" and field.portal_id == "1" for field in inventory.fields))

    def test_invalid_dynamic_type_name_is_not_followed_or_counted_complete(self):
        env, server = run_synthetic("asset_catalog_gap")
        inventory = env.portals["1"].snapshot.fields["assets"]
        self.assertFalse(inventory.form_scope_complete)
        self.assertEqual(inventory.status, "INCOMPLETE")
        self.assertFalse(any("must-not-follow" in call["path"] for call in server.calls))

    def test_demo_api_rejects_unknown_scenario(self):
        with self.assertRaises(ValueError):
            demo_environment("not-a-demo")


if __name__ == "__main__":
    unittest.main()
