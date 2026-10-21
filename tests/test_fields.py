"""Synthetic, portal-scoped field strategy and privacy contract tests."""

from __future__ import annotations

import copy
import json
import unittest
from types import SimpleNamespace

from sdp_audit.fields import (
    FieldDefinition, FieldDiscovery, FieldInventory, MetadataParseError,
    normalize_ci_metadata, normalize_metainfo, normalize_udf_list,
)
from sdp_audit.transport import ApiError, BudgetExceeded


class FakeClient:
    """A shared deterministic transport; never opens a socket."""

    def __init__(self, responses=()):
        self.responses = list(responses)
        self.calls = []
        self.registrations = []
        self.stats = SimpleNamespace(requests=0)

    def allow_metadata_path(self, path, *, portal_id, provenance):
        self.registrations.append((path, portal_id, provenance))

    def get_json(self, path, params=None, **context):
        self.calls.append({"path": path, "params": params, **context})
        if not self.responses:
            raise AssertionError("Unexpected field metadata read")
        result = self.responses.pop(0)
        if not isinstance(result, BudgetExceeded):
            self.stats.requests += 1
        if isinstance(result, BaseException):
            raise result
        return copy.deepcopy(result)


def dataset(records=(), *, details=(), complete=True, outcome="COMPLETE", endpoint="/requests", diagnostics=()):
    return {"records": list(records), "details": list(details), "list_complete": complete,
            "outcome": outcome, "endpoint": endpoint, "diagnostics": list(diagnostics)}


def metadata(fields=None, *, builtin=False):
    definitions = {"udf_fields": {"type": "udf", "fields": fields or {}}}
    if builtin:
        definitions["id"] = {"type": "long", "read_only": True}
    return {"metainfo": {"fields": definitions}}


def field(name="udf_comment", **extra):
    return {name: {"id": "100", "display_name": "Additional comment", "type": "string",
                   "display_type": "single_line", "constraints": {"max_length": 250}, **extra}}


def templates(incident=("10",), service=()):
    return {"incident_templates": dataset([{"id": identifier} for identifier in incident]),
            "service_templates": dataset([{"id": identifier} for identifier in service])}


def input_data(call):
    return json.loads(call["params"]["input_data"]) if call["params"] else {}


def execute(engine):
    """Assert scheduler fairness at the field engine boundary."""
    events = []
    iterator = engine.iter_steps()
    while True:
        before = len(engine.client.calls)
        try:
            event = next(iterator)
        except StopIteration:
            if len(engine.client.calls) != before:
                raise AssertionError("Generator performed an unreported final read")
            return events
        if len(engine.client.calls) - before > 1:
            raise AssertionError("Field step exceeded one logical GET")
        events.append(event)


class FieldNormalizationTests(unittest.TestCase):
    def normalize(self, response, **extra):
        return normalize_metainfo(response, portal_id="7", portal_name="IT", module="requests",
                                  endpoint="/requests/metainfo", **extra)

    def test_normalizes_metadata_without_retaining_values_or_scripts(self):
        secret_text = "SENSITIVE_TICKET_BODY patient@example.invalid clinical.pdf"
        definition = field(
            default_value=secret_text, allowed_values=[secret_text, "#", "safe"],
            mandatory=True, read_only=False, description=secret_text,
            script="console.log('" + secret_text + "')", href="https://external.invalid/" + secret_text,
        )
        values = self.normalize(metadata(definition, builtin=True), context={"template_id": "10"})
        extra = next(value for value in values if value.is_additional)
        self.assertEqual(extra.maximum_length, 250)
        self.assertEqual(extra.allowed_value_count, 3)
        self.assertEqual(extra.maximum_option_character_count, len(secret_text))
        self.assertEqual(extra.default_character_count, len(secret_text))
        self.assertEqual(extra.options_with_unsupported_characters, 1)
        self.assertEqual(extra.options_with_only_unsupported_characters, 1)
        self.assertTrue(extra.mandatory)
        self.assertFalse(extra.read_only)
        self.assertIsNone(extra.custom)
        self.assertEqual(extra.field_path, "udf_fields.udf_comment")
        self.assertEqual(extra.contexts, [{"template_id": "10"}])
        serialized = json.dumps([value.to_dict() for value in values])
        for text in (secret_text, "patient@example.invalid", "clinical.pdf", "console.log", "external.invalid"):
            self.assertNotIn(text, serialized)

    def test_custom_origin_is_explicit_and_not_guessed_from_name(self):
        values = self.normalize({"metainfo": {"fields": {
            "udf_name_without_holder": {"type": "string"},
            "custom_flat": {"is_custom": True, "type": "string"},
            "converted_fields": {"type": "udf", "fields": {"property": {"type": "string", "is_custom": False}}},
        }}})
        by_name = {value.internal_name: value for value in values}
        self.assertIsNone(by_name["udf_name_without_holder"].custom)
        self.assertFalse(by_name["udf_name_without_holder"].is_additional)
        self.assertTrue(by_name["custom_flat"].is_additional)
        self.assertTrue(by_name["custom_flat"].custom)
        self.assertTrue(by_name["property"].is_additional)
        self.assertFalse(by_name["property"].custom)

    def test_legacy_udf_holders_keep_distinct_identical_numeric_ids(self):
        response = {"metainfo": {"fields": {
            "udf_fields": {"type": "udf", "fields": field("same")},
            "workstation_udf_fields": {"type": "udf", "fields": field("same")},
            "ci_server_fields": {"type": "udf", "fields": field("same")},
        }}}
        inventory = FieldInventory("computers", "7", "IT")
        for item in self.normalize(response):
            inventory.add(item)
        self.assertEqual(len(inventory.fields), 3)
        self.assertTrue(all(item.is_additional for item in inventory.fields))

    def test_nested_non_udf_fields_remain_builtin(self):
        values = self.normalize({"metainfo": {"fields": {
            "department": {"type": "object", "fields": {"id": {"type": "long"}}}
        }}})
        self.assertEqual(values[0].field_path, "department.id")
        self.assertFalse(values[0].is_additional)

    def test_missing_or_malformed_wrapper_is_never_empty_registry(self):
        for response in ({}, {"udf_fields": []}, {"metainfo": []}, {"metainfo": {"fields": []}},
                         {"metainfo": {"fields": {"udf_fields": {"type": "udf"}}}}):
            with self.subTest(response=response), self.assertRaises(MetadataParseError):
                self.normalize(response)

    def test_invalid_fields_or_excessive_nesting_fail_safely(self):
        malformed = [
            {"metainfo": {"fields": {"description body": {}}}},
            {"metainfo": {"fields": {"name": "SENSITIVE_TICKET_BODY"}}},
            {"metainfo": {"fields": {"name": {"fields": []}}}},
        ]
        deep = {"leaf": {"type": "string"}}
        for _ in range(18):
            deep = {"child": {"fields": deep}}
        malformed.append({"metainfo": {"fields": deep}})
        for response in malformed:
            with self.subTest(response=response), self.assertRaises(MetadataParseError) as caught:
                self.normalize(response)
            self.assertNotIn("SENSITIVE_TICKET_BODY", str(caught.exception))

    def test_missing_constraints_and_flags_stay_unknown(self):
        value = self.normalize(metadata({"field": {"type": "string"}}))[0]
        self.assertIsNone(value.maximum_length)
        self.assertIsNone(value.mandatory)
        self.assertIsNone(value.read_only)
        self.assertIsNone(value.custom)
        self.assertIsNone(value.allowed_value_count)

    def test_negative_unbounded_or_malformed_lengths_are_not_positive_limits(self):
        for length in (-1, "-1", True, "200 units", 1.5):
            with self.subTest(length=length):
                value = self.normalize(metadata(field(constraints={"max_length": length})))[0]
                self.assertIsNone(value.maximum_length)

    def test_numeric_default_is_measurement_only(self):
        value = self.normalize(metadata(field(default_value="-12345.67890")))[0]
        self.assertEqual(value.default_digit_count, 10)
        self.assertNotIn("-12345.67890", json.dumps(value.to_dict()))

    def test_labels_are_bounded_and_emails_removed(self):
        value = self.normalize(metadata(field(display_name="<b>Owner person@example.invalid</b> " + "x" * 300)))[0]
        self.assertLessEqual(len(value.display_label), 250)
        self.assertNotIn("person@example.invalid", value.display_label)
        self.assertNotIn("<b>", value.display_label)

    def test_context_union_deduplicates_and_retains_constraint_variants(self):
        inventory = FieldInventory("requests", "7", "IT")
        first = self.normalize(metadata(field()), context={"template_id": "10"})[0]
        second = self.normalize(metadata(field(constraints={"max_length": 500}, mandatory=True)),
                                context={"template_id": "12"})[0]
        inventory.add(first)
        inventory.add(second)
        self.assertEqual(len(inventory.fields), 1)
        merged = inventory.fields[0]
        self.assertEqual(merged.maximum_length, 500)
        self.assertIsNone(merged.mandatory)
        self.assertEqual(merged.completeness, "CONTEXT_DEPENDENT")
        self.assertEqual(len(merged.constraint_variants), 2)
        self.assertEqual(len(merged.contexts), 2)
        self.assertTrue(inventory.limitations)

    def test_confirmed_metadata_replaces_inferred_key_without_type_guess(self):
        inventory = FieldInventory("requests", "7", "IT")
        inventory.add(FieldDefinition("udf_comment", "udf_fields.udf_comment", "7", "IT", "requests",
                                      is_additional=True, evidence_basis="INFERRED_FROM_OBSERVED_UDF_KEY"))
        inventory.add(self.normalize(metadata(field()))[0])
        self.assertEqual(len(inventory.fields), 1)
        self.assertEqual(inventory.fields[0].evidence_basis, "API_METADATA")
        self.assertEqual(inventory.fields[0].data_type, "string")

    def test_udf_list_requires_correct_module_and_portal(self):
        common = dict(portal_id="7", portal_name="IT", module="space_room", endpoint="/udf_fields")
        for bad in (
            {"name": "udf_room", "portal": {"id": "9"}},
            {"name": "udf_room", "module": {"name": "requests"}},
            {"name": "not an API name"},
        ):
            with self.subTest(bad=bad), self.assertRaises(MetadataParseError):
                normalize_udf_list({"udf_fields": [bad]}, **common)
        result = normalize_udf_list({"udf_fields": [{"name": "udf_room", "portal": {"id": "7"},
                                                    "module": {"name": "space_room"}}]}, **common)
        self.assertEqual(result[0].module, "space_room")
        self.assertTrue(result[0].is_additional)

    def test_ci_metadata_uses_documented_nested_holder_and_discards_layout(self):
        response = {"metadata": {**metadata(field()), "layout": {"script": "SENSITIVE_SCRIPT"},
                                 "module_details": {"description": "SENSITIVE_DESCRIPTION"},
                                 "hierarchy": {"name": "PRIVATE_NAME"}}}
        values = normalize_ci_metadata(response, portal_id="7", portal_name="IT", module="cis",
                                       endpoint="/cmdb_server/_metadata", context={"api_plural_name": "cmdb_server"})
        self.assertEqual(values[0].maximum_length, 250)
        self.assertEqual(values[0].module, "cis")
        serialized = json.dumps([value.to_dict() for value in values])
        for canary in ("SENSITIVE_SCRIPT", "SENSITIVE_DESCRIPTION", "PRIVATE_NAME"):
            self.assertNotIn(canary, serialized)

    def test_ci_metadata_malformed_wrapper_or_wrong_type_never_becomes_empty(self):
        kwargs = dict(portal_id="7", portal_name="IT", module="cis", endpoint="/cmdb_server/_metadata",
                      context={"api_plural_name": "cmdb_server"})
        for response in ({"metainfo": {"fields": {}}}, {"metadata": []},
                         {"metadata": {"metainfo": {"plural_name": "cmdb_other", "fields": {}}}}):
            with self.subTest(response=response), self.assertRaises(MetadataParseError):
                normalize_ci_metadata(response, **kwargs)


class FieldDiscoveryTests(unittest.TestCase):
    def test_each_portal_uses_only_its_observed_template_selector(self):
        client = FakeClient([metadata(field()), metadata(field())])
        engines = [FieldDiscovery(client, "7", "IT", templates(("10",))),
                   FieldDiscovery(client, "9", "HR", templates(("90",)))]
        for engine in engines:
            execute(engine)
        self.assertEqual([call["portal_id"] for call in client.calls], ["7", "9"])
        self.assertEqual([input_data(call)["template"]["id"] for call in client.calls], ["10", "90"])
        self.assertTrue(all(call["path"] == "/requests/metainfo" for call in client.calls))
        for engine in engines:
            item = engine.inventories["requests"].fields[0]
            self.assertEqual(item.portal_id, engine.portal_id)
            self.assertEqual(item.portal_name, engine.portal_name)

    def test_all_observed_request_template_types_are_merged(self):
        client = FakeClient([metadata(field()), metadata(field())])
        engine = FieldDiscovery(client, "7", "IT", templates(("10",), ("12",)))
        events = execute(engine)
        inventory = engine.inventories["requests"]
        self.assertEqual(events[0]["status"], "COLLECTING")
        self.assertEqual(events[1]["status"], "COMPLETE")
        self.assertEqual(len(inventory.fields), 1)
        self.assertEqual({context["template_kind"] for context in inventory.fields[0].contexts},
                         {"incident_templates", "service_templates"})
        self.assertTrue(inventory.form_scope_complete)
        self.assertFalse(inventory.registry_complete)

    def test_request_without_observed_template_never_guesses_an_id(self):
        client = FakeClient()
        engine = FieldDiscovery(client, "7", "IT", {"requests": dataset()})
        self.assertEqual(execute(engine), [])
        inventory = engine.inventories["requests"]
        self.assertEqual(inventory.status, "INCOMPLETE")
        self.assertIsNone(inventory.to_dict()["fields_observed"])
        self.assertEqual(client.calls, [])

    def test_partial_template_catalog_cannot_be_complete(self):
        data = templates(("10",))
        data["incident_templates"]["list_complete"] = False
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", data)
        execute(engine)
        self.assertEqual(engine.inventories["requests"].status, "INCOMPLETE")
        self.assertFalse(engine.inventories["requests"].form_scope_complete)

    def test_metadata_limit_samples_targets_and_records_total(self):
        engine = FieldDiscovery(FakeClient([metadata(field()), metadata(field())]), "7", "IT",
                                templates(tuple(str(i) for i in range(10, 20))), metadata_limit=2)
        execute(engine)
        inventory = engine.inventories["requests"]
        self.assertEqual(inventory.metadata_targets_total, 10)
        self.assertEqual(inventory.metadata_targets_attempted, 2)
        self.assertEqual(inventory.metadata_targets_successful, 2)
        self.assertEqual(inventory.status, "INCOMPLETE")
        self.assertEqual([input_data(call)["template"]["id"] for call in engine.client.calls], ["10", "19"])

    def test_zero_metadata_limit_is_unlimited_subject_to_shared_client(self):
        engine = FieldDiscovery(FakeClient([metadata(), metadata(), metadata()]), "7", "IT",
                                templates(("10", "11", "12")), metadata_limit=0)
        execute(engine)
        self.assertEqual(engine.inventories["requests"].metadata_targets_successful, 3)

    def test_change_uses_documented_form_metadata_then_observed_record_fallback(self):
        client = FakeClient([ApiError("unsupported", "Endpoint not supported.", 404), metadata(field())])
        engine = FieldDiscovery(client, "7", "IT", {"changes": dataset([{"id": "44"}])})
        events = execute(engine)
        self.assertEqual([call["path"] for call in client.calls], ["/changes/metainfo", "/changes/44/metainfo"])
        self.assertTrue(all(call["portal_id"] == "7" for call in client.calls))
        inventory = engine.inventories["changes"]
        self.assertEqual(inventory.metadata_targets_attempted, 1)
        self.assertEqual(inventory.http_attempts, 2)
        self.assertEqual(inventory.diagnostics[0]["classification"], "ENDPOINT_UNSUPPORTED")
        self.assertEqual(events[0]["status"], "COLLECTING")
        self.assertEqual(inventory.fields[0].contexts, [{"record_id": "44"}])

    def test_metadata_permission_denial_is_specific_and_does_not_try_compatibility(self):
        denied = ApiError("forbidden", "The operation was denied.", 403, (4002,), api_message="Insufficient permissions.")
        client = FakeClient([denied])
        engine = FieldDiscovery(client, "7", "IT", {"changes": dataset([{"id": "44"}])})
        execute(engine)
        inventory = engine.inventories["changes"]
        self.assertEqual(inventory.status, "PERMISSION_DENIED")
        self.assertIsNone(inventory.to_dict()["additional_fields_observed"])
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(inventory.diagnostics[0]["http_status"], 403)
        self.assertEqual(inventory.diagnostics[0]["api_codes"], [4002])
        self.assertEqual(inventory.diagnostics[0]["portal_id"], "7")
        self.assertEqual(inventory.diagnostics[0]["endpoint"], "/changes/metainfo")
        self.assertNotIn("Admin", json.dumps(inventory.to_dict()))

    def test_denied_record_inventory_does_not_imply_metadata_permission_denial(self):
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT",
                                {"changes": dataset(outcome="PERMISSION_DENIED", complete=False)})
        execute(engine)
        self.assertEqual(engine.inventories["changes"].status, "COMPLETE")

    def test_explicit_unavailability_skips_module_metadata_and_keeps_counts_unknown(self):
        for status in ("MODULE_NOT_ENABLED", "MODULE_NOT_AVAILABLE", "PORTAL_NOT_ACCESSIBLE"):
            with self.subTest(status=status):
                diagnostics = [{"classification": status, "http_status": 403, "api_codes": [4000]}]
                data = {module: dataset(outcome=status, complete=False, diagnostics=diagnostics)
                        for module in ("requests", "changes", "assets", "computers", "problems")}
                data.update(templates())
                engine = FieldDiscovery(FakeClient(), "7", "IT", data)
                execute(engine)
                self.assertEqual(engine.client.calls, [])
                for module in ("requests", "changes", "assets", "computers", "problems"):
                    inventory = engine.inventories[module]
                    self.assertEqual(inventory.status, status)
                    self.assertIsNone(inventory.to_dict()["fields_observed"])
                    self.assertTrue(inventory.diagnostics[0]["inherited_from_inventory"])

    def test_successful_empty_metadata_has_zero_observations_but_no_admin_registry_claim(self):
        engine = FieldDiscovery(FakeClient([metadata()]), "7", "IT", {"changes": dataset()})
        execute(engine)
        inventory = engine.inventories["changes"]
        self.assertEqual(inventory.status, "EMPTY")
        self.assertEqual(inventory.to_dict()["fields_observed"], 0)
        self.assertEqual(inventory.to_dict()["additional_fields_observed"], 0)
        self.assertTrue(inventory.form_scope_complete)
        self.assertFalse(inventory.registry_complete)

    def test_invalid_metadata_response_is_parse_error_and_not_empty(self):
        engine = FieldDiscovery(FakeClient([{"unexpected": []}]), "7", "IT", {"changes": dataset()})
        execute(engine)
        self.assertEqual(engine.inventories["changes"].status, "PARSE_ERROR")
        self.assertIsNone(engine.inventories["changes"].to_dict()["fields_observed"])

    def test_explicit_wrong_metadata_portal_is_context_error_without_fallback(self):
        response = {**metadata(field()), "portal": {"id": "9"}}
        engine = FieldDiscovery(FakeClient([response]), "7", "IT", {"changes": dataset([{"id": "44"}])})
        execute(engine)
        self.assertEqual(engine.inventories["changes"].status, "PORTAL_CONTEXT_REQUIRED")
        self.assertEqual(engine.inventories["changes"].fields, [])
        self.assertEqual(len(engine.client.calls), 1)

    def test_failed_metadata_progress_has_unknown_count(self):
        engine = FieldDiscovery(FakeClient([ApiError("forbidden", "Access denied.", 403)]), "7", "IT", {"changes": dataset()})
        event = execute(engine)[0]
        self.assertIsNone(event["fields_observed"])
        self.assertEqual(event["status"], "PERMISSION_DENIED")

    def test_no_invented_routes_for_core_modules_without_verified_schema(self):
        keys = ("problems", "projects", "releases", "users", "technicians", "cis", "contracts", "purchases")
        data = {key: dataset([{"id": "100", "udf_fields": {"udf_char_1": "SENSITIVE_TICKET_BODY"}}], endpoint="/" + key)
                for key in keys}
        engine = FieldDiscovery(FakeClient(), "7", "IT", data)
        execute(engine)
        self.assertEqual(engine.client.calls, [])
        for key in keys:
            inventory = engine.inventories[key]
            self.assertEqual(inventory.status, "INCOMPLETE")
            self.assertFalse(inventory.registry_complete)
            self.assertEqual(inventory.fields[0].evidence_basis, "INFERRED_FROM_OBSERVED_UDF_KEY")
            self.assertIsNone(inventory.fields[0].data_type)
            self.assertEqual(inventory.fields[0].module, key)
            self.assertNotIn("SENSITIVE_TICKET_BODY", json.dumps(inventory.to_dict()))

    def test_refresh_after_detail_sampling_retains_only_keys_and_existing_metadata(self):
        data = {"changes": dataset()}
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", data)
        execute(engine)
        data["changes"]["details"].append({"udf_fields": {"udf_comment": "SENSITIVE_TICKET_BODY", "another": "private.pdf"}})
        before = len(engine.client.calls)
        engine.refresh_observed_keys()
        self.assertEqual(len(engine.client.calls), before)
        inventory = engine.inventories["changes"]
        self.assertEqual(inventory.evidence_basis, "API_METADATA_AND_OBSERVED_KEYS")
        self.assertEqual(len(inventory.fields), 2)
        self.assertEqual(inventory.fields[0].data_type, "string")
        self.assertNotIn("SENSITIVE_TICKET_BODY", json.dumps(inventory.to_dict()))
        self.assertNotIn("private.pdf", json.dumps(inventory.to_dict()))

    def test_dynamic_asset_types_are_registered_only_from_safe_observed_names(self):
        modules = [{"id": "1", "api_plural_name": "asset_servers"},
                   {"id": "2", "api_plural_name": "custom_asset_facilities"},
                   {"id": "3", "api_plural_name": "../requests"},
                   {"id": "4", "api_plural_name": "asset_servers/../scan"},
                   {"id": "5", "href": "https://external.invalid/asset_secret/_metainfo"}]
        client = FakeClient([metadata(field()), metadata(field())])
        engine = FieldDiscovery(client, "7", "IT", {"assets": dataset(), "asset_modules": dataset(modules)})
        execute(engine)
        self.assertEqual([call["path"] for call in client.calls],
                         ["/asset_servers/_metainfo", "/custom_asset_facilities/_metainfo"])
        self.assertEqual(client.registrations, [(path, "7", "asset_modules") for path in
                         ("/asset_servers/_metainfo", "/custom_asset_facilities/_metainfo")])
        self.assertEqual(engine.inventories["assets"].metadata_targets_total, 5)
        self.assertEqual(engine.inventories["assets"].status, "INCOMPLETE")

    def test_new_asset_base_is_not_all_type_coverage_when_catalog_unknown(self):
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", {"assets": dataset()})
        execute(engine)
        self.assertEqual(engine.client.calls[0]["path"], "/asset_assets/_metainfo")
        self.assertEqual(input_data(engine.client.calls[0]), {"for": "advanced_filter"})
        self.assertEqual(engine.inventories["assets"].status, "INCOMPLETE")

    def test_legacy_asset_selectors_use_observed_product_types_and_scan_each(self):
        rows = [{"id": "11", "product_type": {"id": "2"}}, {"id": "12", "product_type": {"id": "8"}}]
        client = FakeClient([ApiError("unsupported", "Endpoint unavailable.", 404), metadata(field()), metadata(field())])
        engine = FieldDiscovery(client, "7", "IT", {"assets": dataset(rows)})
        execute(engine)
        self.assertEqual([call["path"] for call in client.calls],
                         ["/asset_assets/_metainfo", "/assets/metainfo", "/assets/metainfo"])
        self.assertEqual([input_data(call)["template"]["id"] for call in client.calls[1:]], ["2", "8"])
        inventory = engine.inventories["assets"]
        self.assertEqual(inventory.metadata_targets_total, 2)
        self.assertEqual(inventory.metadata_targets_successful, 2)
        self.assertEqual(inventory.status, "INCOMPLETE")
        self.assertFalse(inventory.registry_complete)

    def test_source_build_selects_documented_legacy_asset_metadata(self):
        data = {"assets": dataset([{"product_type": {"id": "4"}}])}
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", data, source_build="14900")
        execute(engine)
        self.assertEqual(engine.client.calls[0]["path"], "/assets/metainfo")
        self.assertEqual(input_data(engine.client.calls[0]), {"template": {"id": "4"}})
        self.assertEqual(engine.inventories["assets"].status, "INCOMPLETE")

    def test_legacy_computers_do_not_treat_every_product_type_as_workstation(self):
        data = {"computers": dataset([{"product_type": {"id": "4"}}]),
                "product_types": dataset([{"id": "1"}, {"id": "4"}, {"id": "8"}])}
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", data, source_build=14900)
        execute(engine)
        self.assertEqual(len(engine.client.calls), 1)
        self.assertEqual(engine.client.calls[0]["path"], "/workstations/metainfo")
        self.assertEqual(input_data(engine.client.calls[0])["template"]["id"], "4")

    def test_departments_are_separate_from_user_fields(self):
        engine = FieldDiscovery(FakeClient([metadata(field())]), "7", "IT", {"departments": dataset(), "users": dataset()})
        execute(engine)
        self.assertEqual(engine.client.calls[0]["path"], "/departments/_metainfo")
        self.assertEqual(engine.inventories["departments"].fields[0].module, "departments")
        self.assertEqual(engine.inventories["users"].status, "INCOMPLETE")

    def test_ci_types_drive_exact_portal_scoped_metadata_registration(self):
        response = {"metadata": metadata(field())}
        data = {"cis": dataset(), "ci_types": dataset([
            {"id": "11", "api_plural_name": "cmdb"}, {"id": "12", "api_plural_name": "cmdb_server"}])}
        engine = FieldDiscovery(FakeClient([response, response]), "7", "IT", data)
        execute(engine)
        self.assertEqual(engine.client.registrations,
                         [("/cmdb/_metadata", "7", "ci_types"), ("/cmdb_server/_metadata", "7", "ci_types")])
        self.assertEqual([call["path"] for call in engine.client.calls], ["/cmdb/_metadata", "/cmdb_server/_metadata"])
        inventory = engine.inventories["cis"]
        self.assertTrue(inventory.form_scope_complete)
        self.assertFalse(inventory.registry_complete)
        self.assertEqual(inventory.fields[0].contexts,
                         [{"api_plural_name": "cmdb", "ci_type_id": "11"}, {"api_plural_name": "cmdb_server", "ci_type_id": "12"}])

    def test_ci_type_catalog_alone_can_drive_metadata(self):
        engine = FieldDiscovery(FakeClient([{"metadata": metadata(field())}]), "7", "IT",
                                {"ci_types": dataset([{"api_plural_name": "cmdb_server", "id": "12"}])})
        execute(engine)
        self.assertEqual(engine.inventories["cis"].metadata_targets_successful, 1)

    def test_ci_metadata_does_not_guess_from_type_display_name_href_or_record_module(self):
        data = {"ci_types": dataset([{"id": "10", "name": "cmdb_server", "href": "/cmdb_server/_metadata"},
                                     {"id": "11", "api_plural_name": "cmdb_server/../requests"}]),
                "cis": dataset([{"module": {"api_plural_name": "cmdb_workstation"}}])}
        engine = FieldDiscovery(FakeClient(), "7", "IT", data)
        execute(engine)
        self.assertEqual(engine.client.calls, [])
        self.assertEqual(engine.client.registrations, [])
        self.assertEqual(engine.inventories["cis"].status, "INCOMPLETE")
        self.assertEqual(engine.inventories["cis"].metadata_targets_total, 2)
        self.assertIsNone(engine.inventories["cis"].to_dict()["fields_observed"])

    def test_ci_metadata_catalog_cap_or_unknown_types_keep_coverage_incomplete(self):
        data = {"ci_types": dataset([{"id": "10", "api_plural_name": "cmdb_server"}, {"id": "11", "name": "Legacy"}])}
        engine = FieldDiscovery(FakeClient([{"metadata": metadata(field())}]), "7", "IT", data)
        execute(engine)
        self.assertEqual(engine.inventories["cis"].status, "INCOMPLETE")
        self.assertEqual(engine.inventories["cis"].metadata_targets_total, 2)
        self.assertEqual(engine.inventories["cis"].metadata_targets_successful, 1)

    def test_space_udf_discovery_requires_observed_module_and_uses_exact_selector(self):
        response = {"udf_fields": [{"id": "1", "name": "udf_room", "display_name": "Room field"}],
                    "list_info": {"has_more_rows": False, "start_index": 1}}
        client = FakeClient([response])
        engine = FieldDiscovery(client, "7", "IT", {"modules": dataset([{"name": "space_room"}, {"name": "invented_space"}])})
        execute(engine)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["path"], "/udf_fields")
        self.assertEqual(client.calls[0]["portal_id"], "7")
        self.assertEqual(input_data(client.calls[0])["module"], {"name": "space_room"})
        self.assertTrue(engine.inventories["space_room"].registry_complete)
        self.assertEqual(set(engine.inventories), {"space_room"})

    def test_unobserved_space_module_never_probes_udf_registry(self):
        engine = FieldDiscovery(FakeClient(), "7", "IT", {"modules": dataset([{"name": "spaces"}])})
        execute(engine)
        self.assertEqual(engine.client.calls, [])

    def test_space_udf_pagination_is_paced_and_reports_collecting_until_exhausted(self):
        responses = [{"udf_fields": [{"id": str(i), "name": "udf_" + str(i)}],
                      "list_info": {"has_more_rows": i < 3, "start_index": i}} for i in (1, 2, 3)]
        engine = FieldDiscovery(FakeClient(responses), "7", "IT", {"space_room": dataset()})
        events = execute(engine)
        self.assertEqual([event["status"] for event in events], ["COLLECTING", "COLLECTING", "COMPLETE"])
        self.assertEqual([input_data(call)["list_info"]["start_index"] for call in engine.client.calls], [1, 2, 3])
        inventory = engine.inventories["space_room"]
        self.assertEqual(inventory.metadata_targets_attempted, 1)
        self.assertEqual(inventory.http_attempts, 3)
        self.assertEqual(len(inventory.fields), 3)
        self.assertTrue(inventory.registry_complete)

    def test_space_udf_unknown_pagination_is_incomplete(self):
        engine = FieldDiscovery(FakeClient([{"udf_fields": []}]), "7", "IT", {"space_room": dataset()})
        execute(engine)
        self.assertEqual(engine.inventories["space_room"].status, "INCOMPLETE")
        self.assertFalse(engine.inventories["space_room"].registry_complete)

    def test_repeated_space_page_is_parse_error_and_preserves_first_page(self):
        response = {"udf_fields": [{"name": "udf_repeat"}], "list_info": {"has_more_rows": True}}
        engine = FieldDiscovery(FakeClient([response, response]), "7", "IT", {"space_room": dataset()})
        execute(engine)
        inventory = engine.inventories["space_room"]
        self.assertEqual(len(inventory.fields), 1)
        self.assertEqual(inventory.status, "PARSE_ERROR")
        self.assertFalse(inventory.registry_complete)

    def test_same_page_duplicate_udf_identity_is_parse_error(self):
        response = {"udf_fields": [{"name": "udf_repeat"}, {"name": "udf_repeat"}], "list_info": {"has_more_rows": False}}
        engine = FieldDiscovery(FakeClient([response]), "7", "IT", {"space_room": dataset()})
        execute(engine)
        self.assertEqual(engine.inventories["space_room"].status, "PARSE_ERROR")

    def test_shared_client_can_interleave_portals_and_modules(self):
        client = FakeClient([metadata(field())] * 6)
        data = templates(("10", "12"))
        data["changes"] = dataset()
        a, b = FieldDiscovery(client, "7", "IT", data), FieldDiscovery(client, "9", "HR", data)
        iterators = [a.iter_steps(), b.iter_steps()]
        for _ in range(3):
            for iterator in iterators:
                before = len(client.calls)
                next(iterator)
                self.assertEqual(len(client.calls) - before, 1)
        self.assertEqual([call["portal_id"] for call in client.calls], ["7", "9"] * 3)
        self.assertEqual([call["module"] for call in client.calls], ["requests", "requests", "changes", "changes", "requests", "requests"])
        self.assertEqual(client.stats.requests, 6)

    def test_global_budget_preserves_completed_module_and_partial_fields(self):
        for reason in ("REQUEST_BUDGET_REACHED", "TIME_BUDGET_REACHED"):
            with self.subTest(reason=reason):
                client = FakeClient([metadata(field()), metadata(field()), BudgetExceeded("Global budget ended.", reason)])
                data = templates(("10", "12"))
                data["changes"] = dataset()
                engine = FieldDiscovery(client, "7", "IT", data)
                iterator = engine.iter_steps()
                next(iterator)
                next(iterator)
                with self.assertRaises(BudgetExceeded):
                    next(iterator)
                self.assertEqual(engine.inventories["changes"].status, "COMPLETE")
                requests = engine.inventories["requests"]
                self.assertEqual(requests.status, "INCOMPLETE")
                self.assertEqual(len(requests.fields), 1)
                self.assertEqual(requests.metadata_targets_successful, 1)
                self.assertFalse(requests.form_scope_complete)
                self.assertEqual(requests.diagnostics[-1]["classification"], reason)
                self.assertIn(reason, " ".join(requests.limitations))

    def test_budget_before_first_read_is_not_started_and_has_unknown_count(self):
        engine = FieldDiscovery(FakeClient([BudgetExceeded("Budget ended.")]), "7", "IT", {"changes": dataset()})
        with self.assertRaises(BudgetExceeded):
            next(engine.iter_steps())
        inventory = engine.inventories["changes"]
        self.assertEqual(inventory.metadata_targets_attempted, 0)
        self.assertEqual(inventory.http_attempts, 0)
        self.assertEqual(inventory.status, "NOT_SCANNED")
        self.assertIsNone(inventory.to_dict()["fields_observed"])

    def test_interrupt_preserves_successful_metadata_and_propagates(self):
        client = FakeClient([metadata(field()), KeyboardInterrupt()])
        engine = FieldDiscovery(client, "7", "IT", templates(("10", "12")))
        iterator = engine.iter_steps()
        next(iterator)
        with self.assertRaises(KeyboardInterrupt):
            next(iterator)
        self.assertEqual(len(engine.inventories["requests"].fields), 1)
        self.assertEqual(engine.inventories["requests"].status, "INCOMPLETE")
        json.dumps(engine.inventories["requests"].to_dict())

    def test_authentication_failure_propagates_without_losing_prior_fields(self):
        client = FakeClient([metadata(field()), ApiError("authentication", "Authentication failed.", 401)])
        engine = FieldDiscovery(client, "7", "IT", templates(("10", "12")))
        iterator = engine.iter_steps()
        next(iterator)
        with self.assertRaises(ApiError):
            next(iterator)
        inventory = engine.inventories["requests"]
        self.assertEqual(len(inventory.fields), 1)
        self.assertEqual(inventory.diagnostics[-1]["classification"], "AUTHENTICATION_FAILED")

    def test_stop_before_start_keeps_unknown_counts_and_does_not_change_completed_modules(self):
        engine = FieldDiscovery(FakeClient([metadata()]), "7", "IT", {"changes": dataset()})
        engine.stop("TIME_BUDGET_REACHED")
        self.assertEqual(engine.inventories["changes"].status, "NOT_SCANNED")
        self.assertIsNone(engine.inventories["changes"].to_dict()["fields_observed"])
        execute(engine)
        engine.stop("TIME_BUDGET_REACHED")
        self.assertEqual(engine.inventories["changes"].status, "EMPTY")

    def test_invalid_portal_and_metadata_limits_fail_without_echoing_input(self):
        for portal in ("0", "１", "-1", "1\n", "SECRET_INVALID_PORTAL", True):
            with self.subTest(portal=portal), self.assertRaises(ValueError) as error:
                FieldDiscovery(FakeClient(), portal, "IT", {})
            self.assertNotIn("SECRET_INVALID_PORTAL", str(error.exception))
        for limit in (-1, True, "10", 1.5):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                FieldDiscovery(FakeClient(), "7", "IT", {}, metadata_limit=limit)

    def test_no_repeat_iteration_accidentally_replays_reads(self):
        engine = FieldDiscovery(FakeClient([metadata()]), "7", "IT", {"changes": dataset()})
        execute(engine)
        with self.assertRaises(RuntimeError):
            list(engine.iter_steps())
        self.assertEqual(len(engine.client.calls), 1)


if __name__ == "__main__":
    unittest.main()
