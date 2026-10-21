"""Small synthetic fixture for an offline, explicitly labeled demonstration."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import Dataset, Snapshot


def _demo_time(value: str) -> dict[str, str]:
    parsed = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    return {"value": str(int(parsed.timestamp() * 1000))}


def demo_snapshot() -> Snapshot:
    snapshot = Snapshot(
        generated_at="2026-10-05T17:00:00+00:00",
        source={"host": "https://synthetic.example.invalid", "product": "ServiceDesk Plus On-Premises", "demo": True, "build_origin": "user_supplied"},
        settings={"demo": True, "rpm": 30, "page_size": 100, "max_requests": 500,
                  "max_runtime_seconds": 1200, "detail_limit": 20, "read_only_get_only": True,
                  "attachment_downloads": False, "tls_verification": True,
                  "credential_visibility_verified": False},
        manual_answers={"source_build": 14700, "target_edition": "Enterprise", "target_region": "EU",
                        "required_history_years": 7, "required_audit_years": 7, "needs_power_bi": True,
                        "max_dashboard_lag_minutes": 15, "uses_local_scripts": True,
                        "needs_full_descriptions": True, "requires_legacy_history": True},
        stats={"requests": 0, "successes": 0, "retries": 0, "throttles": 0, "elapsed_seconds": 0,
               "network_used": False},
    )

    def add(key: str, records: list[dict], *, details: bool = True, complete: bool = True, total: int | None = None) -> Dataset:
        dataset = Dataset(key, "/" + key, records=records,
                          details=[dict(row) for row in records] if details else [],
                          total_count=len(records) if total is None else total,
                          status="complete" if complete else "partial", pages=1,
                          list_complete=complete,
                          detail_attempted=len(records) if details else 0,
                          detail_succeeded=len(records) if details else 0,
                          sampling="Synthetic demonstration records; not a live instance")
        snapshot.datasets[key] = dataset
        return dataset

    add("requests", [
        {"id": "101", "subject": "SYNTHETIC PRIVATE SUBJECT SHOULD NOT APPEAR IN REPORT",
         "created_time": _demo_time("2018-04-01"), "last_updated_time": _demo_time("2026-09-30"),
         "scheduled_start_time": _demo_time("2018-03-01"), "scheduled_end_time": _demo_time("2018-05-01"),
         "template": {"id": "11"}, "sla": {"id": "51"}, "request_life_cycle": {"id": "61"},
         "has_notes": True, "has_attachments": True, "has_linked_requests": True,
         "linked_requests": [{"id": "102"}], "dependent_requests": [{"id": "103"}],
         "changes": [{"id": "401"}],
         "attachments": [{"id": "1001", "size": 55000000, "name": "SYNTHETIC_PRIVATE_ATTACHMENT.txt"}],
         "resolution": {"content": "R" * 66000}, "udf_fields": {"udf_char1": "x" * 300}},
        {"id": "102", "created_time": _demo_time("2024-01-10"), "last_updated_time": _demo_time("2026-09-29"),
         "template": {"id": "12"}, "sla": {"id": "51"}, "has_notes": False,
         "attachments": [], "udf_fields": {"udf_char1": "short"}},
        {"id": "103", "created_time": _demo_time("2026-10-01"), "template": {"id": "11"},
         "attachments": [], "has_notes": False, "udf_fields": {}},
    ])
    add("technicians", [
        {"id": "201", "email_id": "same@example.invalid", "is_login_enabled": True},
        {"id": "202", "email_id": "SAME@example.invalid", "is_login_enabled": True},
        {"id": "203", "email_id": "", "is_login_enabled": False},
    ])
    add("users", [{"id": "301", "email_id": "person@example.invalid", "is_technician": False, "is_login_enabled": False}], details=False)
    add("incident_templates", [{"id": "11", "name": "SYNTHETIC INC TEMPLATE", "has_fafr": True,
                                "is_service_template": False, "tasks": [{"id": str(5000 + i)} for i in range(201)],
                                "fields": [{"id": "71", "name": "Example", "type": "single_line", "api_name": "udf_char1"}]}])
    add("service_templates", [{"id": "12", "name": "SYNTHETIC SERVICE TEMPLATE", "is_service_template": True,
                               "has_fafr": True, "resources": [{"id": str(7000 + i), "questions": []} for i in range(21)]}])
    add("request_notes", [{"id": "801", "_parent_id": "101", "description": "SYNTHETIC NOTE BODY NEVER WRITTEN",
                           "attachments": [{"id": "802", "size": 1000}]}], complete=False, total=10)
    add("request_tasks", [{"id": "901", "_parent_id": "101", "dependencies": [{"id": "902"}]}], complete=False, total=4)
    add("changes", [{"id": "401", "created_time": _demo_time("2024-02-10"), "workflow": {"id": "41"},
                     "template": {"id": "42"}, "attachments": []}])
    add("problems", [{"id": "501", "created_time": _demo_time("2025-01-01"), "solution": {"content": "Synthetic solution"},
                      "workaround": {"content": "Synthetic workaround"}, "attachments": []}])
    add("projects", [], details=False)
    add("releases", [{"id": "601", "created_time": _demo_time("2026-08-01"), "attachments": []}])
    add("assets", [{"id": "10001"}, {"id": "10002"}], details=False)
    add("computers", [
        {"id": "10001", "service_tag": "SYNTHETIC-TAG", "acquisition_date": _demo_time("2026-02-01"),
         "warranty_expiry": _demo_time("2025-01-01"), "expiry_date": _demo_time("2027-01-01")},
        {"id": "10002", "service_tag": "SYNTHETIC-TAG", "is_virtual": True, "virtual_host": None,
         "product_type": {"name": "Virtual Machine"}},
    ])
    add("ci_types", [{"id": "11001", "name": "Application"}], details=False)
    add("cis", [{"id": "12001"}, {"id": "12002"}], details=False)
    add("reports", [{"id": "13001", "report_name": "Synthetic query report"}], details=False)
    add("purchases", [], details=False)
    add("contracts", [], details=False)
    add("sites", [{"id": "14001"}], details=False)
    add("support_groups", [{"id": "15001"}], details=False)
    snapshot.datasets["field_definitions"] = Dataset("field_definitions", "/udf_fields", status="forbidden", issues=["Synthetic permission denial to demonstrate unknown coverage."])
    return snapshot
