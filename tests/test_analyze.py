"""Behavioral tests for migration conclusions, missing evidence and redaction."""

import json
import unittest

from sdp_audit.analyze import analyze
from sdp_audit.models import Dataset, Snapshot


def dataset(key, records=None, *, complete=True, status="complete", details=None, total=None, doc_url=""):
    records = records or []
    return Dataset(key=key, endpoint="/" + key, records=records, details=details or [],
                   list_complete=complete, status=status, total_count=total,
                   detail_succeeded=len(details or []), doc_url=doc_url)


def assessment(*datasets, answers=None, source=None):
    return analyze(Snapshot(
        generated_at="2026-10-05T17:00:00Z", source=source or {}, settings={},
        datasets={ds.key: ds for ds in datasets}, manual_answers=answers or {},
    ))


def finding(report, ident):
    return next(item for item in report.findings if item.id == ident)


class AssessmentTests(unittest.TestCase):
    def test_empty_snapshot_is_not_ready_or_clean(self):
        report = assessment()
        self.assertGreaterEqual(len(report.findings), 30)
        self.assertEqual(len(report.questions), 7)
        self.assertFalse(any(item.status == "NO_ISSUE_OBSERVED" for item in report.findings))

    def test_permission_failure_is_unknown_not_empty(self):
        report = assessment(dataset("technicians", complete=False, status="forbidden"))
        result = finding(report, "TECHNICIAN_EMAILS")
        self.assertEqual(result.status, "UNKNOWN")
        self.assertIsNone(result.affected_count)

    def test_clean_identity_requires_email_field_and_complete_list(self):
        self.assertEqual(finding(assessment(dataset("technicians", [{"id": "1"}])), "TECHNICIAN_EMAILS").status, "UNKNOWN")
        records = [{"id": "1", "email_id": "one@example.invalid"}]
        report = assessment(dataset("technicians", records, complete=False))
        self.assertEqual(finding(report, "TECHNICIAN_EMAILS").status, "UNKNOWN")
        report = assessment(dataset("technicians", records))
        self.assertEqual(finding(report, "TECHNICIAN_EMAILS").status, "NO_ISSUE_OBSERVED")

    def test_reported_total_prevents_false_complete_result(self):
        report = assessment(dataset("technicians", [{"id": "1", "email_id": "one@example.invalid"}], total=2))
        self.assertEqual(finding(report, "TECHNICIAN_EMAILS").status, "UNKNOWN")

    def test_partial_positive_identity_finding_and_no_pii(self):
        records = [{"id": "1", "email_id": "DuplicatePerson@example.invalid", "name": "Private Name"},
                   {"id": "2", "email_id": "duplicateperson@EXAMPLE.INVALID", "name": "Other Name"},
                   {"id": "3", "email_id": None}, {"id": "4"}]
        report = assessment(dataset("technicians", records, complete=False))
        result = finding(report, "TECHNICIAN_EMAILS")
        self.assertEqual(result.status, "CONFIRMED_IMPACT")
        self.assertEqual(result.affected_count, 3)
        serialized = json.dumps(report.to_dict())
        self.assertNotIn("DuplicatePerson", serialized)
        self.assertNotIn("Private Name", serialized)

    def test_detail_merges_by_identity_without_double_counting(self):
        rows = [{"id": "1", "email_id": "same@example.invalid"}]
        report = assessment(dataset("technicians", rows, details=rows))
        result = finding(report, "TECHNICIAN_EMAILS")
        self.assertEqual(result.affected_count, 0)
        self.assertEqual(result.examined_count, 1)

    def test_age_observation_is_lower_bound_with_missing_archives(self):
        report = assessment(dataset("requests", [{"id": "1", "created_time": {"value": "1577836800000"}}]))
        self.assertEqual(finding(report, "HISTORY_WINDOW_FIVE_YEARS").status, "CONFIRMED_IMPACT")
        self.assertEqual(finding(report, "HISTORY_WINDOW_FIVE_YEARS").affected_count, 1)
        self.assertIn("lower bounds", finding(report, "HISTORY_WINDOW_FIVE_YEARS").coverage)

    def test_list_request_does_not_imply_audit_history_or_attachments(self):
        report = assessment(dataset("requests", [{"id": "1", "created_time": {"value": "1700000000000"}, "has_attachments": True}]))
        self.assertEqual(finding(report, "ATTACHMENT_SIZE").status, "UNKNOWN")
        self.assertEqual(finding(report, "LEGACY_HISTORY").status, "MANUAL_CONFIRMATION")

    def test_attachment_aggregate_deduplication_and_unknown_sizes(self):
        records = [{"id": "1", "attachments": [{"id": "51", "size": 30_000_000}, {"id": "52", "size": 30_000_000},
                                                     {"id": "51", "size": 30_000_000}, {"id": "53", "size": None}]}]
        result = finding(assessment(dataset("requests", records)), "ATTACHMENT_SIZE")
        self.assertEqual(result.status, "CONFIRMED_IMPACT")
        self.assertEqual(result.evidence[0]["known_attachment_bytes"], 60_000_000)
        self.assertEqual(result.evidence[0]["missing_sizes"], 1)

    def test_attachment_decimal_binary_boundary_remains_manual(self):
        records = [{"id": "1", "attachments": [{"id": "51", "size": 49_000_000}]}]
        self.assertEqual(finding(assessment(dataset("requests", records)), "ATTACHMENT_SIZE").status, "MANUAL_CONFIRMATION")

    def test_task_dependencies_do_not_trigger_request_dependency_loss(self):
        report = assessment(dataset("requests", [{"id": "1", "tasks": [{"id": "2", "dependencies": [{"id": "3"}]}]}]),
                            dataset("request_tasks", [{"id": "2", "dependencies": [{"id": "3"}]}]))
        self.assertEqual(finding(report, "REQUEST_DEPENDENCIES").status, "UNKNOWN")

    def test_positive_schedule_date_detected_with_other_date_missing(self):
        row = {"id": "1", "created_time": "2026-01-02T00:00:00Z", "scheduled_start_time": "2026-01-01T00:00:00Z"}
        result = finding(assessment(dataset("requests", [row])), "REQUEST_SCHEDULE_DATES")
        self.assertEqual(result.status, "CONFIRMED_IMPACT")

    def test_missing_asset_dates_are_not_fabricated_zero_dates(self):
        rows = [{"id": "1", "acquisition_date": None, "expiry_date": None}, {"id": "2"}]
        result = finding(assessment(dataset("assets", rows)), "ASSET_DATE_ORDER")
        self.assertEqual(result.status, "UNKNOWN")
        self.assertIsNone(result.affected_count)

    def test_vm_host_not_in_sample_is_not_missing_host(self):
        rows = [{"id": "1", "is_virtual_machine": True, "virtual_host": {"id": "999"}},
                {"id": "2", "is_virtual_machine": True}]
        result = finding(assessment(dataset("computers", rows)), "VM_HOST_LINKS")
        self.assertEqual(result.status, "UNKNOWN")
        self.assertIsNone(result.affected_count)

    def test_global_fields_require_explicit_request_module(self):
        rows = [{"id": str(index), "field_type": "single_line", "module": "Asset", "name": "sensitive" + str(index)}
                for index in range(300)]
        result = finding(assessment(dataset("field_definitions", rows)), "REQUEST_FIELD_CAPACITY")
        self.assertNotEqual(result.status, "CONFIRMED_IMPACT")
        rows[0].pop("module")
        result = finding(assessment(dataset("field_definitions", rows)), "REQUEST_FIELD_CAPACITY")
        self.assertEqual(result.status, "UNKNOWN")

    def test_capacity_limits_are_total_not_sum_of_type_caps(self):
        rows = [{"id": str(index), "type": "single_line", "name": "field" + str(index)} for index in range(251)]
        result = finding(assessment(dataset("request_fields", rows)), "REQUEST_FIELD_CAPACITY")
        self.assertEqual(result.status, "CONFIRMED_IMPACT")
        self.assertEqual(result.evidence[0]["limit"], 250)

    def test_typed_field_value_is_measured_without_recording_value(self):
        field = {"id": "91", "name": "udf_sline_1", "type": "single_line"}
        row = {"id": "7", "subject": "PRIVATE", "udf_fields": {"udf_sline_1": "x" * 251}}
        report = assessment(dataset("request_fields", [field]), dataset("requests", [row]))
        result = finding(report, "FIELD_VALUE_LENGTHS")
        self.assertEqual(result.status, "CONFIRMED_IMPACT")
        self.assertEqual(result.evidence[0]["character_count"], 251)
        self.assertNotIn("x" * 251, json.dumps(report.to_dict()))
        self.assertNotIn("PRIVATE", json.dumps(report.to_dict()))

    def test_source_secrets_are_not_propagated(self):
        report = assessment(source={"api_key": "PRIVATEKEY", "url": "https://login:PRIVATEKEY@example.invalid/api?api_key=PRIVATEKEY", "name": "Private Name"})
        serialized = json.dumps(report.to_dict())
        self.assertNotIn("PRIVATEKEY", serialized)
        self.assertNotIn("Private Name", serialized)
        self.assertNotIn("login:", serialized)

    def test_manual_requirements_are_not_mislabeled_api_evidence(self):
        report = assessment(answers={"source_build": 14000, "required_audit_years": 7,
                                     "needs_power_bi": True, "max_dashboard_lag_minutes": 15})
        self.assertIn("User-supplied", finding(report, "SOURCE_BUILD").summary)
        self.assertEqual(finding(report, "ADMIN_AUDIT_RETENTION").status, "CONFIRMED_IMPACT")
        self.assertEqual(finding(report, "POWER_BI_REQUIREMENTS").status, "CONFIRMED_IMPACT")

    def test_all_evidence_examples_are_bounded(self):
        rows = [{"id": str(index), "email_id": None} for index in range(40)]
        result = finding(assessment(dataset("technicians", rows)), "TECHNICIAN_EMAILS")
        self.assertEqual(result.affected_count, 40)
        self.assertEqual(len(result.evidence), 20)

    def test_query_filter_inventory_without_report_type(self):
        ds = dataset("reports", [{"id": "1", "name": "Private report title"}],
                     doc_url="https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/lb43ei8/view-all-query-reports")
        report = assessment(ds)
        self.assertEqual(finding(report, "QUERY_REPORTS").status, "CONFIRMED_IMPACT")
        self.assertNotIn("Private report title", json.dumps(report.to_dict()))

    def test_documented_relationship_flags_and_aliases_are_observed(self):
        row = {"id": "1", "has_linked_requests": True, "dependent_requests": [{"id": "2"}],
               "changes": [{"id": "3"}], "request_life_cycle": {"id": "4"}}
        report = assessment(dataset("requests", [row]))
        for ident in ("LINKED_REQUESTS", "REQUEST_DEPENDENCIES", "REQUEST_CHANGE_LINKS", "WORKFLOW_REBUILD"):
            self.assertEqual(finding(report, ident).status, "CONFIRMED_IMPACT")

    def test_template_fields_support_value_check_without_complete_registry(self):
        template = {"id": "1", "fields": [{"id": "11", "api_name": "udf_char1", "type": "single_line"}]}
        row = {"id": "2", "udf_fields": {"udf_char1": "z" * 300}}
        report = assessment(dataset("incident_templates", [template]), dataset("requests", [row]))
        self.assertEqual(finding(report, "FIELD_VALUE_LENGTHS").status, "CONFIRMED_IMPACT")
        self.assertEqual(finding(report, "REQUEST_FIELD_CAPACITY").status, "UNKNOWN")

    def test_large_numeric_exponent_does_not_need_expansion(self):
        field = {"id": "91", "name": "udf_numeric1", "type": "numeric"}
        row = {"id": "7", "udf_fields": {"udf_numeric1": "1e999999999"}}
        report = assessment(dataset("request_fields", [field]), dataset("requests", [row]))
        self.assertEqual(finding(report, "FIELD_VALUE_LENGTHS").status, "CONFIRMED_IMPACT")

    def test_settings_keep_exact_safe_budgets_and_ipv6_origin(self):
        snapshot = Snapshot("2026-10-05T17:00:00Z", {"host": "https://[::1]:8443", "demo": True},
                            {"max_minutes": 20, "subresource_parents": 10, "tls_verification": True,
                             "collections_selected": ["requests", "technicians", "private-unrecognized"], "api_key": "SECRET"})
        report = analyze(snapshot)
        self.assertEqual(report.source["host"], "https://[::1]:8443")
        self.assertEqual(report.settings["subresource_parents"], 10)
        self.assertEqual(report.settings["collections_selected"], ["requests", "technicians"])
        self.assertNotIn("SECRET", json.dumps(report.to_dict()))

    def test_generic_description_limit_is_not_a_power_bi_claim(self):
        report = assessment(answers={"needs_power_bi": True, "needs_full_descriptions": True})
        self.assertEqual(finding(report, "POWER_BI_REQUIREMENTS").status, "MANUAL_CONFIRMATION")
        self.assertEqual(finding(report, "REPORT_DESCRIPTION_REQUIREMENTS").status, "MANUAL_CONFIRMATION")
        self.assertIn("does not prove a native Power BI limit", finding(report, "REPORT_DESCRIPTION_REQUIREMENTS").action)

    def test_question_answers_include_actual_build_and_history_evidence(self):
        report = assessment(dataset("requests", [{"id": "1", "created_time": "2019-01-01T00:00:00Z"}]),
                            answers={"source_build": 14700, "target_edition": "Enterprise"})
        questions = {question["id"]: question for question in report.questions}
        self.assertIn("14700", questions["Q1"]["observed"])
        self.assertIn("Enterprise", questions["Q1"]["observed"])
        self.assertIn("1 affected records observed", questions["Q2"]["observed"])


if __name__ == "__main__":
    unittest.main()
