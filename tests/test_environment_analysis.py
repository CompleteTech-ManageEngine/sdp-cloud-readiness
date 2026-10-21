"""Portal isolation, honest coverage and metadata impact regressions."""

from __future__ import annotations

import copy
import json
import unittest

from sdp_audit.analyze import analyze
from sdp_audit.demo import demo_snapshot
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.fields import FieldDefinition, FieldInventory
from sdp_audit.models import Dataset, EnvironmentSnapshot, PortalInfo, PortalSnapshot, Snapshot, Topology
from sdp_audit.transport import ApiError


PRIVATE = "SYNTHETIC PRIVATE PATIENT NOTE DO NOT REPORT"
WHEN = "2026-10-07T12:00:00Z"


def dataset(key, rows=(), *, portal_id="3", status="complete", outcome="COMPLETE",
            complete=True, attempted=True):
    return Dataset(key, "/" + key, records=list(rows), status=status, outcome=outcome,
                   pages=1 if complete or rows else 0, list_complete=complete,
                   portal_id=portal_id, module=key, read_attempted=attempted,
                   detail_complete=complete)


def multi_environment():
    environment = EnvironmentSnapshot(
        WHEN, {"host": "https://sdp.example.test", "product": "ServiceDesk Plus"},
        {"rpm": 30, "max_requests": 500},
        stats={"requests": 12, "max_requests": 500, "elapsed_seconds": 22},
        authentication="VALID",
    )
    for portal_id, name in (("3", "IT Helpdesk"), ("7", "HR")):
        portal = PortalInfo(portal_id, name, accessible=True, scan_status="ASSESSED_WITH_COVERAGE_GAPS",
                            discovery_endpoint="/portals")
        rows = [{"id": "1", "created_time": {"value": "1514764800000"}, "description": PRIVATE,
                 "udf_fields": {"udf_sline_1": PRIVATE * 10}, "linked_requests": [{"id": "2"}]}]
        snapshot = Snapshot(WHEN, {"portal_id": portal_id}, {}, datasets={
            "requests": dataset("requests", rows, portal_id=portal_id),
            "assets": dataset("assets", [{"id": "1"}], portal_id=portal_id),
            "computers": dataset("computers", [{"id": "1"}], portal_id=portal_id),
            "cis": dataset("cis", [{"id": "1"}], portal_id=portal_id),
            "users": dataset("users", [{"id": "1", "email_id": "private@example.test"}], portal_id=portal_id),
        })
        environment.portals[portal_id] = PortalSnapshot(portal, snapshot)
        environment.topology.portals.append(portal)
    error = ApiError("forbidden", "The scoped operation was denied.", http_status=403, api_codes=(4000, 4002),
                     portal_id="7", module="projects", endpoint="/projects", endpoint_name="projects")
    denied = dataset("projects", portal_id="7", status="forbidden", outcome="PERMISSION_DENIED", complete=False)
    denied.diagnostics = [error.to_dict()]
    environment.portals["7"].snapshot.datasets["projects"] = denied
    environment.portals["7"].portal.diagnostics = [error.to_dict()]
    environment.portals["3"].snapshot.datasets["projects"] = dataset("projects", [], portal_id="3", outcome="EMPTY")
    environment.topology.complete = True
    environment.topology.outcome = "COMPLETE"
    return environment


def field(number, *, module="requests", portal_id="3", typ="single_line", label=None, **extra):
    return FieldDefinition(
        f"udf_sline_{number}", f"udf_fields.udf_sline_{number}", portal_id, "IT Helpdesk", module,
        field_id=str(number), display_label=label or f"Additional field {number}", display_type=typ,
        data_type="string", is_additional=True, evidence_basis="API_METADATA",
        metadata_source="/requests/metainfo", **extra,
    )


def inventory(fields, *, module="requests", complete=False, **extra):
    return FieldInventory(
        module, "3", "IT Helpdesk", status="COMPLETE", fields=fields,
        metadata_targets_total=1, metadata_targets_attempted=1, metadata_targets_successful=1,
        registry_complete=complete, form_scope_complete=True, completeness="FORM_SCOPE_COMPLETE",
        evidence_basis="API_METADATA", **extra,
    )


class EnvironmentAnalysisTests(unittest.TestCase):
    def test_safe_environment_context_and_capability_contract_are_retained(self):
        env = multi_environment()
        env.settings.update(max_portals=100, metadata_limit=20, portal_ids=["03", "7", "7", "../9", PRIVATE],
                            portal_discovery_mode="explicit", api_key=PRIVATE,
                            collections_selected=["requests", "request_lifecycles", "asset_modules", "orgusers", PRIVATE])
        env.source.update(key_expiration="not_exposed_by_verified_read_only_api",
                          orgusers_collection="once_for_environment", request_context_portal_id="3", api_key=PRIVATE)
        env.portals["3"].snapshot.capabilities["requests"] = {
            "availability": "AVAILABLE", "discovery_method": "documented_inventory_first_page_reused",
            "operations": [{"resource": "requests", "endpoint": "/requests", "status": "COMPLETE",
                            "capability": "AVAILABLE", "description": PRIVATE}],
            "limitation": "No documented whole-portal module registry was verified.",
            "raw_response": {"subject": PRIVATE},
        }
        result = analyze_environment(env)
        self.assertEqual(result.settings["max_portals"], 100)
        self.assertEqual(result.settings["metadata_limit"], 20)
        self.assertEqual(result.settings["portal_ids"], ["3", "7"])
        self.assertEqual(result.settings["portal_discovery_mode"], "explicit")
        self.assertEqual(result.settings["collections_selected"], ["requests", "request_lifecycles", "asset_modules", "orgusers"])
        self.assertEqual(result.source["orgusers_collection"], "once_for_environment")
        self.assertEqual(result.source["request_context_portal_id"], "3")
        self.assertEqual(result.environment["permissions"]["integration_key_expiration"], "NOT_ASSESSED")
        capability = result.portals[0]["capabilities"][0]
        self.assertEqual(capability["availability"], "AVAILABLE")
        self.assertEqual(capability["portal_name"], "IT Helpdesk")
        self.assertEqual(capability["operations"][0]["status"], "COMPLETE")
        self.assertIn("limitation", capability)
        self.assertNotIn(PRIVATE, json.dumps(result.to_dict()))

    def test_ci_metadata_context_and_constraint_variants_remain_safe(self):
        env = multi_environment()
        definition = field(1, module="cis", contexts=[{"ci_type_id": "34", "api_plural_name": "servers"}],
                           constraint_variants=[{"maximum_length": 600, "default_value": PRIVATE,
                                                 "contexts": [{"ci_type_id": "34", "description": PRIVATE}]}])
        env.portals["3"].snapshot.fields["cis"] = inventory([definition], module="cis")
        result = analyze_environment(env)
        item = result.field_inventory[0]["fields"][0]
        self.assertEqual(item["contexts"][0]["ci_type_id"], "34")
        self.assertEqual(item["constraint_variants"][0]["contexts"], [{"ci_type_id": "34"}])
        self.assertEqual(item["constraint_variants"][0]["maximum_length"], 600)
        self.assertEqual(result.field_inventory[0]["fields_observed"], 1)
        self.assertNotIn(PRIVATE, json.dumps(result.to_dict()))

    def test_same_record_id_in_two_portals_stays_separate(self):
        result = analyze_environment(multi_environment())
        rows = [item for item in result.findings if item.id.endswith(":HISTORY_WINDOW_FIVE_YEARS")]
        self.assertEqual(len(rows), 2)
        self.assertEqual({item.portal_id for item in rows}, {"3", "7"})
        for item in rows:
            self.assertEqual(item.affected_count, 1)
            self.assertEqual(item.evidence[0]["entity_id"], "1")
            self.assertEqual(item.evidence[0]["portal_id"], item.portal_id)
        request_volume = next(row for row in result.environment["volume_by_module"] if row["resource"] == "requests")
        self.assertEqual(request_volume["records_observed"], 2)
        self.assertEqual(result.schema_version, "2.0")
        self.assertEqual(len(result.portals), 2)

    def test_global_objects_are_counted_once_and_resource_types_are_separate(self):
        env = multi_environment()
        global_dataset = dataset("orgusers", [{"id": "1"}, {"id": "2"}], portal_id=None)
        global_dataset.scope = "environment"
        env.global_snapshot = Snapshot(WHEN, {}, {}, datasets={"orgusers": global_dataset})
        for portal in env.portals.values():
            portal.snapshot.datasets["orgusers"] = copy.deepcopy(global_dataset)
        result = analyze_environment(env)
        volumes = {row["resource"]: row for row in result.environment["volume_by_module"]}
        self.assertEqual(volumes["orgusers"]["records_observed"], 2)
        self.assertEqual(volumes["orgusers"]["collections"], 1)
        self.assertEqual(len([row for row in result.coverage if row["key"] == "orgusers"]), 1)
        for key in ("assets", "computers", "cis"):
            self.assertEqual(volumes[key]["records_observed"], 2)
        self.assertIn("membership", volumes["users"]["count_semantics"])
        self.assertNotIn("total_unique_assets", result.environment["summary"])

    def test_denied_empty_and_never_started_are_distinct(self):
        env = multi_environment()
        env.portals["7"].snapshot.datasets["releases"] = dataset(
            "releases", portal_id="7", status="not_attempted", outcome="NOT_SCANNED", complete=False, attempted=False)
        result = analyze_environment(env)
        lookup = {(row["portal_id"], row["key"]): row for row in result.coverage}
        self.assertEqual(lookup["3", "projects"]["records_observed"], 0)
        self.assertTrue(lookup["3", "projects"]["list_complete"])
        self.assertEqual(lookup["3", "projects"]["outcome"], "EMPTY")
        self.assertIsNone(lookup["7", "projects"]["records_observed"])
        self.assertIsNone(lookup["7", "releases"]["records_observed"])
        self.assertFalse(lookup["7", "projects"]["list_complete"])
        self.assertEqual(result.environment["summary"]["permission_related_operations"], 1)

    def test_budget_stop_preserves_already_completed_collections(self):
        env = multi_environment()
        env.stop_classification = "REQUEST_BUDGET_REACHED"
        env.interrupted_reason = "Global HTTP attempt budget reached."
        env.stats.update(requests=500, max_requests=500)
        result = analyze_environment(env)
        self.assertTrue(next(row for row in result.coverage if row["portal_id"] == "3" and row["key"] == "requests")["list_complete"])
        self.assertEqual(result.environment["stop"]["requests"], 500)
        self.assertEqual(result.environment["stop"]["classification"], "REQUEST_BUDGET_REACHED")

    def test_successful_fallback_keeps_error_history_but_reports_final_success(self):
        env = multi_environment()
        ds = env.portals["3"].snapshot.datasets["assets"]
        ds.diagnostics.append(ApiError("unsupported", "Unsupported endpoint", http_status=404, api_codes=(4007,)).to_dict())
        ds.last_response = {"classification": "SUCCESS", "http_status": 200, "api_codes": [2000]}
        result = analyze_environment(env)
        row = next(item for item in result.coverage if item["portal_id"] == "3" and item["key"] == "assets")
        self.assertEqual(row["http_status"], 200)
        self.assertIsNone(row["error_class"])
        self.assertEqual(row["diagnostics"][0]["http_status"], 404)

    def test_environment_only_topics_are_not_multiplied_by_portal_count(self):
        result = analyze_environment(multi_environment())
        for ident in ("SOURCE_BUILD", "TARGET_LICENSE", "API_VISIBILITY", "DELTA_CUTOVER", "BACKUP_RECOVERY"):
            self.assertEqual(len([item for item in result.findings if item.id == ident]), 1)
        self.assertEqual(len(result.questions), 7)
        self.assertEqual(result.environment["summary"]["manual_confirmation_topics"], 7)
        for question in result.questions:
            for key in ("confirmed_source_evidence", "api_coverage_limitations", "target_cloud_unknowns",
                        "vendor_confirmation_required", "project_decisions_required"):
                self.assertIn(key, question)
        history_question = next(item for item in result.questions if item["id"] == "Q2")
        self.assertEqual({item["portal_id"] for item in history_question["confirmed_source_evidence"]}, {"3", "7"})

    def test_no_discovery_means_no_invented_portal_or_inventory(self):
        env = EnvironmentSnapshot(WHEN, {}, {}, topology=Topology(outcome="ENDPOINT_UNSUPPORTED"))
        result = analyze_environment(env)
        self.assertEqual(result.portals, [])
        self.assertEqual(result.coverage, [])
        self.assertEqual(result.environment["volume_by_module"], [])
        self.assertTrue(result.questions[0]["api_coverage_limitations"])
        self.assertFalse(any(item.portal_id == "1" for item in result.findings))

    def test_single_portal_legacy_rules_remain_equivalent(self):
        source = demo_snapshot()
        portal = PortalInfo("3", "IT Helpdesk", accessible=True)
        env = EnvironmentSnapshot(source.generated_at, source.source, source.settings,
                                  topology=Topology([portal], outcome="COMPLETE", complete=True),
                                  portals={"3": PortalSnapshot(portal, source)}, manual_answers=source.manual_answers)
        old = analyze(source)
        new = analyze_environment(env)
        lookup = {item.id.split(":", 2)[-1]: item for item in new.findings}
        for previous in old.findings:
            if previous.id == "FIELD_NAME_COLLISIONS":
                continue
            item = lookup[previous.id]
            self.assertEqual(item.status, previous.status, previous.id)
            self.assertEqual(item.affected_count, previous.affected_count, previous.id)
            self.assertEqual(item.examined_count, previous.examined_count, previous.id)

    def test_module_metadata_capacity_and_form_coverage_are_separate(self):
        env = multi_environment()
        extra = [field(number) for number in range(1, 252)]
        extra.append(FieldDefinition("id", "id", "3", "IT Helpdesk", "requests", custom=False))
        env.portals["3"].snapshot.fields["requests"] = inventory(extra)
        result = analyze_environment(env)
        capacity = next(item for item in result.findings if item.id == "portal:3:FIELD_REQUESTS_CAPACITY")
        coverage = next(item for item in result.findings if item.id == "portal:3:FIELD_REQUESTS_COVERAGE")
        self.assertEqual(capacity.status, "CONFIRMED_IMPACT")
        self.assertEqual(capacity.examined_count, 251)
        self.assertEqual(coverage.status, "UNKNOWN")
        self.assertFalse(any(item.id == "portal:3:REQUEST_FIELD_CAPACITY" for item in result.findings))
        self.assertEqual(result.field_inventory[0]["additional_fields_observed"], 251)

    def test_unavailable_metadata_does_not_report_zero_fields(self):
        env = multi_environment()
        env.portals["3"].snapshot.fields["projects"] = FieldInventory(
            "projects", "3", "IT Helpdesk", status="ENDPOINT_UNSUPPORTED")
        result = analyze_environment(env)
        self.assertIsNone(result.field_inventory[0]["additional_fields_observed"])
        relevant = [item for item in result.findings if item.id.startswith("portal:3:FIELD_PROJECTS")]
        self.assertTrue(all("count is unknown" in item.summary for item in relevant))
        self.assertTrue(all(item.status == "UNKNOWN" for item in relevant))

    def test_declared_lengths_are_inferred_defaults_and_options_are_measured(self):
        env = multi_environment()
        fields = [field(1, maximum_length=1000, default_character_count=300),
                  field(2, typ="pick_list", maximum_option_character_count=250,
                        options_with_unsupported_characters=2, options_with_only_unsupported_characters=1)]
        env.portals["3"].snapshot.fields["requests"] = inventory(fields)
        result = analyze_environment(env)
        lookup = {item.id.split(":")[-1]: item for item in result.findings if item.portal_id == "3"}
        self.assertEqual(lookup["FIELD_REQUESTS_DECLARED_LENGTH"].status, "MANUAL_CONFIRMATION")
        self.assertEqual(lookup["FIELD_REQUESTS_DECLARED_LENGTH"].evidence_basis, "INFERRED_FROM_METADATA")
        self.assertEqual(lookup["FIELD_REQUESTS_DEFAULT_OPTION_SIZE"].status, "CONFIRMED_IMPACT")
        self.assertEqual(lookup["FIELD_REQUESTS_OPTION_NORMALIZATION"].status, "CONFIRMED_IMPACT")
        # Existing typed-value rule receives the module-aware metadata.
        self.assertEqual(lookup["FIELD_VALUE_LENGTHS"].status, "CONFIRMED_IMPACT")

    def test_case_only_udf_names_are_mapping_candidates(self):
        env = multi_environment()
        fields = [field(1, label="Account", contexts=[{"template_kind": "incident_templates"}]),
                  field(2, label="account", contexts=[{"template_kind": "service_templates"}])]
        env.portals["3"].snapshot.fields["requests"] = inventory(fields)
        result = analyze_environment(env)
        finding = next(item for item in result.findings if item.id.endswith("FIELD_REQUESTS_NAME_MAPPING"))
        self.assertEqual(finding.status, "MANUAL_CONFIRMATION")
        fields[1].display_label = "Account"
        finding = next(item for item in analyze_environment(env).findings if item.id.endswith("FIELD_REQUESTS_NAME_MAPPING"))
        self.assertEqual(finding.status, "CONFIRMED_IMPACT")

    def test_problem_udf_omission_and_asset_mapping_have_distinct_basis(self):
        env = multi_environment()
        env.portals["3"].snapshot.fields["problems"] = inventory([field(1, module="problems", typ="decimal")], module="problems")
        env.portals["3"].snapshot.fields["assets"] = inventory([field(i, module="assets") for i in range(101)], module="assets")
        lookup = {item.id.split(":")[-1]: item for item in analyze_environment(env).findings}
        self.assertEqual(lookup["FIELD_PROBLEMS_MIGRATION_OMISSION"].status, "CONFIRMED_IMPACT")
        self.assertEqual(lookup["FIELD_PROBLEMS_TYPE_CONVERSION"].status, "CONFIRMED_IMPACT")
        self.assertEqual(lookup["FIELD_ASSETS_CAPACITY"].status, "MANUAL_CONFIRMATION")

    def test_workflow_aliases_are_recognized_and_source_content_not_retained(self):
        env = multi_environment()
        env.portals["3"].snapshot.datasets["requests"].records[0]["request_workflow"] = {"id": "42", "description": PRIVATE}
        env.portals["3"].snapshot.fields["requests"] = inventory([field(1)])
        result = analyze_environment(env)
        finding = next(item for item in result.findings if item.id == "portal:3:WORKFLOW_REBUILD")
        self.assertEqual(finding.status, "CONFIRMED_IMPACT")
        self.assertIn("lifecycle/workflow", finding.action)
        serialized = json.dumps(result.to_dict())
        self.assertNotIn(PRIVATE, serialized)
        self.assertNotIn("private@example.test", serialized)
        self.assertNotIn('"records":', serialized)


if __name__ == "__main__":
    unittest.main()
