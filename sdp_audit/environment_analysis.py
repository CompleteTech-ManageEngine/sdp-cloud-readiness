"""Portal-aware assessment with no network or filesystem side effects.

Raw records remain in their portal snapshots. Only schema metadata, identifiers,
measurements and sanitized diagnostics reach the report contract.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, replace
import re
from typing import Any, Mapping

from .analyze import CLEAN, CONFIRMED, MANUAL, UNKNOWN, _safe_settings, _safe_source, analyze
from .catalog import GLOBAL_RESOURCES, RESOURCES
from .diagnostics import guidance
from .models import Assessment, Dataset, EnvironmentSnapshot, Finding, PortalInfo, Snapshot
from .sources import SOURCES
from .response_contract import PARSE_REASONS, safe_shape
from .topology import topology_scope_evidence

_ENVIRONMENT_RULES = {
    "API_VISIBILITY", "SOURCE_BUILD", "POWER_BI_REQUIREMENTS",
    "REPORT_DESCRIPTION_REQUIREMENTS", "ADMIN_AUDIT_RETENTION",
    "AUTOMATION_RUNTIME", "TARGET_LICENSE", "DISCOVERY_NETWORK",
    "DELTA_CUTOVER", "BACKUP_RECOVERY", "EXTERNAL_INTEGRATIONS",
}
_FIELD_RULES = {"REQUEST_FIELD_CAPACITY", "FIELD_NAME_COLLISIONS"}
_RULE_MODULES = {
    "API_VISIBILITY": "topology", "SOURCE_BUILD": "platform",
    "LINKED_REQUESTS": "requests", "REQUEST_DEPENDENCIES": "requests",
    "REQUEST_CHANGE_LINKS": "requests", "ARCHIVED_SUBENTITIES": "archived_requests",
    "ATTACHMENT_SIZE": "multiple", "NOTE_ATTACHMENTS": "requests",
    "TECHNICIAN_EMAILS": "technicians", "APPROVER_LOGIN": "users",
    "REQUEST_FIELD_CAPACITY": "requests", "FIELD_NAME_COLLISIONS": "requests",
    "FIELD_VALUE_LENGTHS": "requests", "REQUEST_SCHEDULE_DATES": "requests",
    "DUPLICATE_SERVICE_TAGS": "computers", "VM_HOST_LINKS": "computers",
    "ASSET_DATE_ORDER": "assets", "WORKFLOW_REBUILD": "multiple",
    "FORM_SCRIPT_ACTIONS": "templates", "QUERY_REPORTS": "reports",
    "TEMPLATE_COMPLEXITY": "templates", "RESOLUTION_LENGTH": "requests",
    "RECURRING_MAINTENANCE": "maintenances", "MODULE_MIGRATION_SCOPE": "multiple",
    "PROBLEM_ANCILLARY_DATA": "problems", "CHANGE_IDENTIFIERS": "changes",
    "ACCESS_MAPPING": "identity", "HISTORY_WINDOW_ONE_YEAR": "multiple",
    "HISTORY_WINDOW_FIVE_YEARS": "multiple", "LEGACY_HISTORY": "multiple",
    "POWER_BI_REQUIREMENTS": "reports", "REPORT_DESCRIPTION_REQUIREMENTS": "reports",
    "ADMIN_AUDIT_RETENTION": "audit", "AUTOMATION_RUNTIME": "automation",
    "TARGET_LICENSE": "licensing", "DISCOVERY_NETWORK": "assets",
    "DELTA_CUTOVER": "cutover", "BACKUP_RECOVERY": "recovery",
    "EXTERNAL_INTEGRATIONS": "integrations",
}
_DENIED = {"PERMISSION_DENIED", "PORTAL_NOT_ACCESSIBLE"}
_UNAVAILABLE = {"ENDPOINT_UNSUPPORTED", "API_VERSION_INCOMPATIBLE",
                "MODULE_NOT_AVAILABLE", "MODULE_NOT_ENABLED"}
_FIELD_ATTRIBUTES = {
    "internal_name", "field_path", "field_id", "display_label", "data_type",
    "display_type", "maximum_length", "allowed_value_count", "mandatory",
    "read_only", "custom", "is_additional", "is_encrypted", "is_pii",
    "metadata_source", "sources", "contexts", "evidence_basis", "completeness",
    "default_character_count", "default_digit_count", "maximum_option_character_count",
    "options_with_unsupported_characters", "options_with_only_unsupported_characters",
    "constraint_variants",
}
_FIELD_CONTEXT_ATTRIBUTES = {"template_id", "template_kind", "record_id",
                             "product_type_id", "api_plural_name", "ci_type_id", "module"}
_FIELD_CONSTRAINT_ATTRIBUTES = {
    "data_type", "display_type", "maximum_length", "mandatory", "read_only", "contexts",
}
_INVENTORY_ATTRIBUTES = {
    "status", "metadata_targets_total", "metadata_targets_attempted",
    "metadata_targets_successful", "http_attempts", "registry_complete",
    "form_scope_complete", "completeness", "evidence_basis", "sources", "limitations",
}
_CAPACITY = {
    "requests": (250, {"string": 250, "long": 75, "datetime": 75, "boolean": 25,
                       "double": 50, "lookup": 10, "multilookup": 10, "date": 10}),
    "users": (50, {"string": 30, "long": 10, "datetime": 10}),
    "technicians": (50, {"string": 30, "long": 10, "datetime": 10}),
    "problems": (160, {"string": 100, "long": 17, "datetime": 17, "boolean": 6,
                       "double": 10, "lookup": 10}),
    "changes": (160, {"string": 150, "long": 35, "datetime": 35, "boolean": 10,
                      "double": 10, "lookup": 10}),
    "projects": (110, {"string": 50, "long": 15, "datetime": 15, "boolean": 10,
                       "double": 15, "lookup": 5}),
    "releases": (160, {"string": 100, "long": 17, "datetime": 17, "boolean": 6,
                       "double": 10, "lookup": 10}),
    "assets": (100, {"string": 55, "long": 10, "datetime": 15, "boolean": 5,
                     "double": 10, "lookup": 5}),
    "computers": (52, {"string": 32, "long": 4, "datetime": 4, "boolean": 4, "double": 8}),
    "cis": (1560, {"string": 840, "long": 240, "datetime": 120, "boolean": 60,
                   "double": 180, "lookup": 60, "multilookup": 60}),
    "contracts": (160, {"string": 100, "long": 17, "datetime": 17, "boolean": 6,
                        "double": 10, "lookup": 10}),
    "purchases": (164, {"string": 100, "long": 17, "datetime": 17, "boolean": 6,
                        "double": 10, "lookup": 10, "cost": 4}),
}
_GROUP_TYPES = {
    "single_line": "string", "singleline": "string", "sline": "string",
    "multi_line": "string", "multiline": "string", "mline": "string",
    "pick_list": "string", "picklist": "string", "multi_select": "string",
    "multiselect": "string", "radio_button": "string", "radio": "string",
    "checkbox": "string", "check_box": "string", "email": "string",
    "phone": "string", "web_url": "string", "url": "string", "string": "string",
    "numeric": "long", "number": "long", "long": "long", "auto_number": "long",
    "datetime": "datetime", "date_time": "datetime", "date": "date",
    "boolean": "boolean", "decision_box": "boolean", "decimal": "double",
    "double": "double", "currency": "double", "percent": "double", "percentage": "double",
    "lookup": "lookup", "multi_lookup": "multilookup", "multilookup": "multilookup",
    "cost": "cost",
}
_VALUE_LIMITS = {"single_line": 250, "singleline": 250, "sline": 250,
                 "multi_line": 5000, "multiline": 5000, "mline": 5000,
                 "email": 50, "phone": 30, "web_url": 250, "url": 250}
_OPTION_TYPES = {"pick_list", "picklist", "multi_select", "multiselect",
                  "radio_button", "radio", "checkbox", "check_box"}


def _map(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return dict(value) if isinstance(value, Mapping) else {}


def _count(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _label(value: Any, fallback: str = "") -> str:
    if not isinstance(value, str):
        return fallback
    value = re.sub(r"\b[\w.!#$%&'*+/=?^{|}~-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[email omitted]", value)
    return " ".join(value.split())[:250] or fallback


def _portal_identifier(value: Any) -> str | None:
    if isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    if isinstance(value, str) and re.fullmatch(r"[0-9]{1,128}", value) and int(value) > 0:
        return str(int(value))
    return None


def _credential_scopes(environment: EnvironmentSnapshot) -> list[dict[str, str]]:
    coverage = environment.stats.get("credential_coverage", {})
    if coverage.get("mode") != "per_instance":
        return []
    def status(value: Any) -> str:
        return value if isinstance(value, str) and value in {"missing", "unverified", "valid", "failed"} else "unverified"
    rows = [{"scope": "directory", "status": status(coverage.get("directory"))},
            {"scope": "global", "status": status(coverage.get("global"))}]
    if "directory_recovery" in coverage:
        rows.insert(1, {"scope": "directory_recovery", "status": status(coverage["directory_recovery"])})
    for pid in environment.portals:
        identifier = _portal_identifier(pid)
        if identifier is not None:
            rows.append({"scope": "portal:" + identifier,
                         "status": status(coverage.get("portals", {}).get(pid))})
    return rows


def _environment_source(source: Mapping[str, Any]) -> dict[str, Any]:
    result = _safe_source(dict(source))
    if source.get("key_expiration") == "not_exposed_by_verified_read_only_api":
        result["key_expiration"] = "not_exposed_by_verified_read_only_api"
    orgusers_states = {
        "not_selected", "not_collected_for_explicit_portal_targeting",
        "multiple_instances_not_observed", "no_accessible_portal_context_confirmed",
        "once_for_environment", "credential_missing",
    }
    if isinstance(source.get("orgusers_collection"), str) and source["orgusers_collection"] in orgusers_states:
        result["orgusers_collection"] = source["orgusers_collection"]
    context_id = _portal_identifier(source.get("request_context_portal_id"))
    if context_id is not None:
        result["request_context_portal_id"] = context_id
    return result


def _environment_settings(settings: Mapping[str, Any]) -> dict[str, Any]:
    result = _safe_settings(dict(settings))
    if isinstance(settings.get("diagnose_only"), bool):
        result["diagnose_only"] = settings["diagnose_only"]
    for key in ("max_portals", "metadata_limit"):
        value = _count(settings.get(key))
        if value is not None:
            result[key] = value
    if isinstance(settings.get("portal_discovery_mode"), str) and settings["portal_discovery_mode"] in {"automatic", "explicit", "assisted"}:
        result["portal_discovery_mode"] = settings["portal_discovery_mode"]
    if isinstance(settings.get("portal_ids"), list):
        result["portal_ids"] = list(dict.fromkeys(
            portal_id for item in settings["portal_ids"]
            if (portal_id := _portal_identifier(item)) is not None))
    if isinstance(settings.get("collections_selected"), list):
        known = {spec.key for spec in RESOURCES + GLOBAL_RESOURCES} | set(result.get("collections_selected", []))
        result["collections_selected"] = [
            item for item in settings["collections_selected"] if isinstance(item, str) and item in known]
    return result


def _capability(value: Any, module: str, portal: PortalInfo) -> dict[str, Any]:
    raw = _map(value)
    allowed = {"status", "classification", "source", "endpoint", "reason", "available", "enabled",
               "availability", "discovery_method", "limitation"}
    result = {key: raw[key] for key in allowed if key in raw}
    result["operations"] = [
        {key: operation[key] for key in ("resource", "endpoint", "status", "capability") if key in operation}
        for operation in raw.get("operations", []) if isinstance(operation, Mapping)
    ]
    result.update(module=module, portal_id=portal.id, portal_name=_label(portal.name))
    return result


def _diagnostics(items: Any, portal: PortalInfo | None = None) -> list[dict[str, Any]]:
    result = []
    allowed = {"classification", "kind", "http_status", "api_codes", "api_message", "message",
               "message_sanitized", "raw_message_omitted", "endpoint", "endpoint_name",
               "module", "retryable", "cause", "portal_id", "portal_name",
               "response_format", "content_type", "has_sdp_status", "transport_detail", "compatibility_retry", "credential_scope"}
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, Mapping):
            continue
        safe = {key: item[key] for key in allowed if key in item}
        if item.get("message_sanitized") is not True:
            safe["message"] = "Unverified diagnostic text omitted; review classification and HTTP/API codes."
            safe["api_message"] = None
            safe["raw_message_omitted"] = True
        safe["message_sanitized"] = True
        if isinstance(item.get("parse_reason"), str) and item["parse_reason"] in PARSE_REASONS:
            safe["parse_reason"] = item["parse_reason"]
        shape = safe_shape(item.get("response_shape"))
        if shape is not None:
            safe["response_shape"] = shape
        if "credential_scope" in safe:
            value = safe["credential_scope"]
            safe["credential_scope"] = (value if isinstance(value, str) and value in
                                        {"directory_key", "portal_key", "global_key"} else "integration_key")
        if portal:
            safe["portal_id"], safe["portal_name"] = portal.id, _label(portal.name, "Portal " + portal.id)
        result.append(safe)
    return result


def _unique_diagnostics(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        identity = tuple(str(item.get(key)) for key in (
            "portal_id", "module", "endpoint", "endpoint_name", "classification", "http_status", "api_codes"))
        if identity not in seen:
            result.append(item)
            seen.add(identity)
    return result


def _portal_metadata(portal: PortalInfo) -> dict[str, Any]:
    result = asdict(portal)
    result["name"] = _label(portal.name, "Portal " + portal.id)
    result["diagnostics"] = _diagnostics(portal.diagnostics, portal)
    return result


def _coverage(dataset: Dataset, portal: PortalInfo | None) -> dict[str, Any]:
    result = dataset.coverage()
    outcome = dataset.outcome
    if not outcome:
        outcome = ("EMPTY" if not dataset.records else "COMPLETE") if dataset.list_complete else {
            "forbidden": "PERMISSION_DENIED", "unsupported": "ENDPOINT_UNSUPPORTED",
            "license": "MODULE_NOT_AVAILABLE", "not_attempted": "NOT_SCANNED",
        }.get(dataset.status, "INCOMPLETE")
    observed = len(dataset.records) if dataset.records or dataset.pages or dataset.list_complete else None
    result.update({
        "portal_id": portal.id if portal else None,
        "portal_name": _label(portal.name) if portal else "Environment",
        "scope": "portal" if portal else "environment",
        "module": dataset.module or dataset.key, "resource": dataset.key,
        "outcome": outcome, "records_observed": observed,
        "pages_observed": dataset.pages, "list_complete": dataset.list_complete,
        "detail_records_attempted": dataset.detail_attempted,
        "detail_records_successful": dataset.detail_succeeded,
        "detail_complete": dataset.detail_complete,
        "diagnostics": _diagnostics(dataset.diagnostics, portal),
        "reason": dataset.stop_reason or "; ".join(dataset.issues) or None,
        "confidence": "API_VISIBLE_LIST" if dataset.list_complete else
                      "PARTIAL_EVIDENCE" if observed is not None else "UNRESOLVED",
    })
    last = dict(dataset.last_response) if dataset.last_response else result["diagnostics"][-1] if result["diagnostics"] else {}
    result["http_status"] = last.get("http_status", result.get("http_status"))
    result["api_codes"] = last.get("api_codes", result.get("api_codes", []))
    result["error_class"] = None if last.get("classification") == "SUCCESS" else last.get("classification")
    if not dataset.list_complete:
        if dataset.sample_complete:
            result["next_step"] = "The configured parent sample completed; other parents remain uninspected. Increase --subresource-parents for a new assessment, or explicitly --restart-all when changing limits on resume."
        else:
            result["next_step"] = guidance({**last, "classification": outcome, "endpoint": dataset.endpoint,
                "endpoint_name": dataset.key, "module": dataset.module or dataset.key})
    return result


def _field_inventory(value: Any, module: str, portal: PortalInfo) -> dict[str, Any]:
    original = _map(value)
    result = {key: original[key] for key in _INVENTORY_ATTRIBUTES if key in original}
    fields = []
    for entry in original.get("fields", []):
        entry = _map(entry)
        safe = {key: entry[key] for key in _FIELD_ATTRIBUTES if key in entry}
        safe["contexts"] = [
            {key: context[key] for key in _FIELD_CONTEXT_ATTRIBUTES if key in context}
            for context in safe.get("contexts", []) if isinstance(context, Mapping)
        ]
        safe["constraint_variants"] = [
            {key: ([{context_key: context[context_key] for context_key in _FIELD_CONTEXT_ATTRIBUTES
                     if context_key in context} for context in variant[key] if isinstance(context, Mapping)]
                   if key == "contexts" and isinstance(variant[key], list) else variant[key])
             for key in _FIELD_CONSTRAINT_ATTRIBUTES if key in variant}
            for variant in safe.get("constraint_variants", []) if isinstance(variant, Mapping)
        ]
        if isinstance(safe.get("display_label"), str):
            safe["display_label"] = _label(safe["display_label"])
        safe.update({"portal_id": portal.id, "portal_name": _label(portal.name), "module": module})
        fields.append(safe)
    observable = bool(fields) or original.get("metadata_targets_successful", 0) > 0 or original.get("registry_complete") is True
    result.update({
        "portal_id": portal.id, "portal_name": _label(portal.name), "module": module,
        "fields": fields, "diagnostics": _diagnostics(original.get("diagnostics", []), portal),
        "fields_observed": len(fields) if observable else None,
        "additional_fields_observed": sum(item.get("is_additional") is True for item in fields) if observable else None,
        "custom_fields_confirmed": sum(item.get("custom") is True for item in fields) if observable else None,
        "builtin_fields_observed": sum(item.get("is_additional") is not True for item in fields) if observable else None,
        "unknown_origin_fields_observed": sum(item.get("custom") is None for item in fields) if observable else None,
    })
    return result


def _type(field: Mapping[str, Any]) -> str:
    value = field.get("display_type") or field.get("data_type")
    return re.sub(r"[\s-]+", "_", value.strip().casefold()) if isinstance(value, str) else ""


def _analysis_snapshot(snapshot: Snapshot, inventories: list[dict[str, Any]]) -> Snapshot:
    """Adapt module metadata to the existing measured-value rule, without reads."""
    request_fields = next((item for item in inventories if item["module"] == "requests"), None)
    if request_fields is None:
        return snapshot
    rows = []
    for field in request_fields["fields"]:
        if field.get("is_additional") is not True or field.get("evidence_basis") != "API_METADATA":
            continue
        rows.append({
            "id": field.get("field_id"),
            "api_name": field.get("internal_name"),
            "column_name": field.get("internal_name"),
            "display_name": field.get("display_label"),
            "field_type": field.get("display_type") or field.get("data_type"),
        })
    definitions = Dataset("request_fields", "metadata-derived", records=rows,
                          status="complete" if request_fields.get("registry_complete") else "partial",
                          list_complete=request_fields.get("registry_complete") is True)
    return replace(snapshot, datasets={**snapshot.datasets, "request_fields": definitions})


def _field_evidence(field: Mapping[str, Any], **measurements: Any) -> dict[str, Any]:
    result = {key: field.get(key) for key in ("field_id", "internal_name", "field_path")}
    result.update(measurements)
    return result


def _metadata_findings(inventory: dict[str, Any], answers: Mapping[str, Any]) -> list[Finding]:
    module = inventory["module"]
    fields = [field for field in inventory["fields"] if field.get("is_additional") is True]
    unique = {}
    for field in fields:
        holder = str(field.get("field_path", "")).rpartition(".")[0]
        identity = (holder, str(field.get("field_id") or field.get("field_path") or field.get("internal_name")))
        unique.setdefault(identity, field)
    fields = list(unique.values())
    direct = [field for field in fields if field.get("evidence_basis") == "API_METADATA"]
    complete = inventory.get("registry_complete") is True
    count_known = inventory.get("additional_fields_observed") is not None
    observed_text = f"{len(fields)} distinct additional fields observed" if count_known else "Additional-field count is unknown"
    findings = []

    def add(suffix: str, title: str, status: str, summary: str, *,
            evidence: list[dict[str, Any]] | None = None, affected: int | None = None,
            basis: str = "API_METADATA", action: str = "", severity: str = "high",
            sources: list[str] | None = None) -> None:
        findings.append(Finding(
            id=f"FIELD_{module.upper()}_{suffix}", title=title, category="fields",
            severity=severity, status=status, summary=summary,
            affected_count=affected, examined_count=len(fields), evidence=(evidence or [])[:20],
            module=module, evidence_basis=basis, sources=sources or ["field_limits", "limitations"],
            action=action or "Confirm source definitions, target mapping and field behavior in the trial migration.",
            coverage=("Complete API-visible definition registry." if complete else
                      "Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing."),
        ))

    add("COVERAGE", f"{module}: field-definition coverage", CLEAN if complete else UNKNOWN,
        observed_text + (f"; {len(direct)} have explicit API metadata. " if count_known else "; no field metadata or UDF keys were available. ") +
        f"Definition coverage: {inventory.get('completeness', 'UNKNOWN')}. "
        "A completed form inspection does not certify the administrator field registry.",
        basis="API_COVERAGE_LIMITATION" if not complete else "API_METADATA", severity="medium",
        action="Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.",
        evidence=[{"additional_fields_observed": inventory.get("additional_fields_observed"),
                   "custom_fields_confirmed": inventory.get("custom_fields_confirmed"),
                   "metadata_targets_successful": inventory.get("metadata_targets_successful"),
                   "metadata_targets_total": inventory.get("metadata_targets_total"),
                   "registry_complete": complete}])
    if module in _CAPACITY:
        total_limit, type_limits = _CAPACITY[module]
        if module == "requests" and str(answers.get("target_edition", "")).casefold() == "free":
            total_limit = 50
            type_limits = {**type_limits, "string": 50, "long": 50, "datetime": 50}
        counts = Counter(_GROUP_TYPES.get(_type(field)) for field in fields)
        direct_counts = Counter(_GROUP_TYPES.get(_type(field)) for field in direct)
        excess = [{"field_group": "all", "observed": len(fields), "documented_limit": total_limit}] if len(fields) > total_limit else []
        excess.extend({"field_group": group, "observed": counts[group], "documented_limit": limit}
                      for group, limit in type_limits.items() if counts[group] > limit)
        direct_excess = len(direct) > total_limit or any(direct_counts[group] > limit for group, limit in type_limits.items())
        needs_mapping = module in {"assets", "computers", "cis"}
        status = (CONFIRMED if direct_excess and not needs_mapping else MANUAL if excess else
                  CLEAN if complete and None not in counts else UNKNOWN)
        add("CAPACITY", f"{module}: additional-field capacity", status,
            observed_text + f"; the documented total limit is {total_limit}. " +
            "Target edition and per-type mapping still require confirmation."
            + (" Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable." if needs_mapping else ""),
            evidence=excess or [{"additional_fields_observed": len(fields) if count_known else None, "documented_limit": total_limit,
                                "field_types_unknown": counts.get(None, 0)}],
            affected=len(excess) if excess else 0 if status == CLEAN else None,
            basis="INFERRED_FROM_METADATA" if excess and status == MANUAL else "API_METADATA")
    names: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for field in fields:
        label = field.get("display_label")
        if isinstance(label, str) and label.strip():
            names[label.strip().casefold()].append(field)
    collisions = [group for group in names.values() if len(group) > 1]
    confirmed_duplicates = []
    for group in collisions:
        incident = [field for field in group if any(context.get("template_kind") == "incident_templates" for context in field.get("contexts", []))]
        service = [field for field in group if any(context.get("template_kind") == "service_templates" for context in field.get("contexts", []))]
        for left in incident:
            for right in service:
                if (left is not right and left.get("display_label") == right.get("display_label")
                        and left.get("evidence_basis") == right.get("evidence_basis") == "API_METADATA"):
                    confirmed_duplicates.append(_field_evidence(right, incident_field_id=left.get("field_id")))
    if collisions:
        add("NAME_MAPPING", f"{module}: additional-field name mapping",
            CONFIRMED if module == "requests" and confirmed_duplicates else MANUAL,
            f"{len(collisions)} groups of field labels match after case folding. "
            + ("Distinct Incident and Service definitions with exactly matching labels were observed; the documented consolidation rule applies."
               if module == "requests" and confirmed_duplicates else
               "These are mapping candidates. The documented case-insensitive rule-name restriction does not establish a universal UDF-name failure."),
            affected=len(confirmed_duplicates) if confirmed_duplicates else len(collisions),
            evidence=confirmed_duplicates or [_field_evidence(field) for group in collisions for field in group],
            basis="API_METADATA" if confirmed_duplicates else "INFERRED_FROM_METADATA")
    defaults, options, declared, special, only_special, variants = [], [], [], [], [], []
    for field in direct:
        typ = _type(field)
        limit = _VALUE_LIMITS.get(typ)
        default = _count(field.get("default_character_count"))
        maximum = _count(field.get("maximum_length"))
        if limit is not None:
            if default is not None and default > limit:
                defaults.append(_field_evidence(field, default_character_count=default, documented_limit=limit))
            if maximum is not None and maximum > limit:
                declared.append(_field_evidence(field, source_maximum_length=maximum, documented_limit=limit))
        if typ in {"numeric", "decimal"} and (_count(field.get("default_digit_count")) or 0) > 15:
            defaults.append(_field_evidence(field, default_digit_count=field["default_digit_count"], documented_limit=15))
        if typ in _OPTION_TYPES:
            option_maximum = _count(field.get("maximum_option_character_count"))
            if option_maximum is not None and option_maximum > 200:
                options.append(_field_evidence(field, maximum_option_character_count=option_maximum, documented_limit=200))
            count = _count(field.get("options_with_unsupported_characters"))
            if count:
                special.append(_field_evidence(field, affected_options=count))
            count = _count(field.get("options_with_only_unsupported_characters"))
            if count:
                only_special.append(_field_evidence(field, affected_options=count))
        if field.get("completeness") == "CONTEXT_DEPENDENT":
            variants.append(_field_evidence(field, context_count=len(field.get("contexts", []))))
    if defaults or options:
        add("DEFAULT_OPTION_SIZE", f"{module}: oversized field defaults or options", CONFIRMED,
            f"{len(defaults)} field defaults and {len(options)} option sets exceed documented value constraints. "
            "Only measurements are retained; defaults and option text are excluded.",
            affected=len(defaults) + len(options), evidence=defaults + options)
    if declared:
        add("DECLARED_LENGTH", f"{module}: source field length declarations", MANUAL,
            f"{len(declared)} source definitions permit longer text than the published Cloud value limits. "
            "A larger declared maximum does not prove any stored value is oversized.",
            affected=len(declared), evidence=declared, basis="INFERRED_FROM_METADATA",
            action="Inspect measured value lengths where authorized and confirm target constraints; do not truncate data from metadata alone.")
    if special:
        add("OPTION_NORMALIZATION", f"{module}: additional-field option normalization", CONFIRMED,
            f"{len(special)} fields contain options with characters the migration guide removes; "
            f"{len(only_special)} fields include an option consisting only of those characters.",
            affected=len(special), evidence=special + only_special)
    if variants:
        add("CONSTRAINT_VARIANTS", f"{module}: field constraints vary by form", MANUAL,
            f"{len(variants)} field definitions have differing observed form constraints. "
            "A single source maximum cannot represent every template or product type.",
            affected=len(variants), evidence=variants, basis="INFERRED_FROM_METADATA")
    conversions = [field for field in direct if _type(field) in {"radio", "radio_button", "checkbox", "check_box", "decimal"}
                   and module not in {"requests", "assets", "computers"}]
    if conversions:
        add("TYPE_CONVERSION", f"{module}: additional-field type conversions", CONFIRMED,
            f"{len(conversions)} fields use types the migration guide converts for entities outside Incident, Service, Assets and Workstations. "
            "Validate the mapped controls, stored values and automation references.",
            affected=len(conversions), evidence=[_field_evidence(field, source_field_type=_type(field)) for field in conversions])
    if module == "problems" and fields:
        add("MIGRATION_OMISSION", "Problem additional fields require separate handling",
            CONFIRMED if direct else MANUAL,
            f"{len(fields)} Problem additional fields observed. The published migration guide excludes Problem additional-field configuration.",
            affected=len(fields), evidence=[_field_evidence(field) for field in fields],
            basis="API_METADATA" if direct else "INFERRED_FROM_METADATA")
    radios = [field for field in direct if _type(field) in {"radio", "radio_button"} and
              (module in {"assets", "computers"} or (module == "requests" and field.get("is_encrypted") is True))]
    if radios:
        add("RADIO_BEHAVIOR", f"{module}: radio-field compatibility", CONFIRMED,
            f"{len(radios)} radio fields need explicit target handling. "
            + ("Asset radio additional fields are documented as unsupported." if module in {"assets", "computers"}
               else "Encrypted Request radio fields are documented to lose encryption in Cloud."),
            affected=len(radios), evidence=[_field_evidence(field) for field in radios])
    return findings


def _attach(finding: Finding, portal: PortalInfo | None) -> Finding:
    scope = "portal" if portal else "environment"
    portal_id = portal.id if portal else None
    portal_name = _label(portal.name) if portal else None
    evidence = [{**entry, "scope": scope, "portal_id": portal_id, "portal_name": portal_name}
                for entry in finding.evidence if isinstance(entry, dict)]
    basis = finding.evidence_basis
    if finding.id in {"POWER_BI_REQUIREMENTS", "ADMIN_AUDIT_RETENTION", "AUTOMATION_RUNTIME"}:
        basis = "USER_SUPPLIED_REQUIREMENT" if finding.status == CONFIRMED else "TARGET_CLOUD_CONFIRMATION"
    elif finding.status == MANUAL and not evidence:
        basis = "TARGET_CLOUD_CONFIRMATION"
    elif finding.id == "LEGACY_HISTORY" and not finding.affected_count and finding.status == CONFIRMED:
        basis = "USER_SUPPLIED_REQUIREMENT"
    return replace(finding, id=f"portal:{portal_id}:{finding.id}" if portal else finding.id,
                   scope=scope, portal_id=portal_id, portal_name=portal_name,
                   module=finding.module or _RULE_MODULES.get(finding.id, "multiple"),
                   evidence=evidence, evidence_basis=basis)


def _volume_rows(coverage: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in coverage:
        groups[(row["scope"], row["key"])].append(row)
    result = []
    for (scope, resource), rows in sorted(groups.items()):
        observed = [row["records_observed"] for row in rows if row["records_observed"] is not None]
        result.append({
            "scope": scope, "resource": resource, "records_observed": sum(observed) if observed else None,
            "collections": len(rows), "collections_with_observations": len(observed),
            "collections_complete": sum(row["list_complete"] for row in rows),
            "collections_unknown": sum(row["records_observed"] is None for row in rows),
            "all_selected_lists_complete": all(row["list_complete"] for row in rows),
            "count_semantics": ("Environment collection counted once." if scope == "environment" else
                                "Portal membership observations, not unique people across portals." if resource in {"users", "technicians"} else
                                "Observed records for this resource only; overlaps with other resource types are not added."),
        })
    return result


def _risk_rollup(findings: list[Finding]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        if finding.scope == "portal":
            grouped[finding.id.split(":", 2)[-1]].append(finding)
    result = []
    for rule_id, items in sorted(grouped.items()):
        counts = Counter(item.status for item in items)
        affected = [item.affected_count for item in items if item.status == CONFIRMED and item.affected_count is not None]
        result.append({
            "rule_id": rule_id, "title": items[0].title, "category": items[0].category,
            "portals_with_confirmed_impact": counts[CONFIRMED],
            "portals_with_unknown_evidence": counts[UNKNOWN],
            "portals_requiring_confirmation": counts[MANUAL],
            "affected_observations": sum(affected) if affected else None,
            "finding_ids": [item.id for item in items],
            "interpretation": "Counts are rule observations; overlapping findings are not unique affected records.",
        })
    return result


_QUESTION_SPECS = (
    ("Q1", "Which documented limitations apply to our source environment and proposed target?",
     set(),
     "Target build support, edition, datacenter and effective tenant limits have not been read.",
     "Confirm supported source builds and the mapping of every selected source portal to a target service desk.",
     "Confirm the intended target topology, required modules and acceptance criteria."),
    ("Q2", "How should old records, CMDB, Releases, Projects and custom modules be handled?",
     {"historical data", "scope", "assets"},
     "The scan cannot verify target import coverage, historical-window exceptions or custom-module equivalence.",
     "Confirm supported migration or retention routes for each portal/module, age group, CMDB relationship and Release/Project subresource.",
     "Choose required history retention, source archive access and ownership of data that needs a separate route."),
    ("Q3", "What needs confirmation regarding final-delta migration?",
     {"cutover"},
     "Source reads cannot establish the future delta's handling of edits, deletes or newly added subentities.",
     "Confirm reconciliation of changed/deleted records, notes, attachments, approvals and tasks, plus target freshness and rollback behavior.",
     "Approve the freeze window, mail transition, delta rehearsal and rollback decision owner."),
    ("Q4", "Which identifiers and relationships require preservation or cross-reference?",
     {"relationships"},
     "Retained IDs, target URLs and email-threading behavior cannot be proven with source credentials.",
     "Confirm Change ID retention, per-portal ID cross-references, linked/dependent requests, request-change mappings and legacy links.",
     "Choose the cross-reference format and tests for each required relationship and historical link."),
    ("Q5", "Which settings, fields, workflows, scripts, reports or modules require reconstruction or licensing?",
     {"configuration", "fields", "reporting", "automation", "integrations", "licensing", "identity", "operations"},
     "Target entitlements, runtime support, quotas and functional equivalents remain unverified.",
     "Confirm field/type mapping, SLA and lifecycle/workflow matching, unsupported form actions, reporting paths, module licenses and discovery architecture.",
     "Assign owners to reconstruction and external integrations; agree which behaviors must be equivalent at go-live."),
    ("Q6", "What export and recovery capabilities require confirmation?",
     {"recovery", "retention"},
     "The scan does not inspect Cloud backup/export configuration or prove restore and exit capabilities.",
     "Obtain tenant-specific export completeness/frequency, recovery granularity, RPO/RTO, support involvement and exit commitments.",
     "Define retention, recovery objectives, periodic export ownership and when source retirement is permitted."),
    ("Q7", "Which failures or unresolved differences should block migration acceptance?",
     set(),
     "Target reconciliation, permissions, workflow execution, recovery and migration success are not validated by this scan.",
     "Agree evidence requirements and exception handling for every unresolved migration difference.",
     "Approve go/no-go thresholds and accountable owners; resolve or explicitly accept each blocker before cutover."),
)


def _questions(findings: list[Finding], coverage: list[dict[str, Any]], topology_complete: bool) -> list[dict[str, Any]]:
    result = []
    for ident, title, categories, target, vendor, business in _QUESTION_SPECS:
        related = [item for item in findings if not categories or item.category in categories]
        direct = [item for item in related if item.status == CONFIRMED and item.evidence_basis not in
                  {"USER_SUPPLIED_REQUIREMENT", "TARGET_CLOUD_CONFIRMATION", "INFERRED_FROM_METADATA"}]
        evidence = [{
            "finding_id": item.id, "portal_id": item.portal_id, "portal_name": item.portal_name,
            "module": item.module, "summary": item.summary,
            "affected_observations": item.affected_count, "examined": item.examined_count,
            "evidence_basis": item.evidence_basis,
        } for item in direct]
        gaps = [{
            "portal_id": row.get("portal_id"), "portal_name": row.get("portal_name"),
            "module": row.get("module"), "resource": row.get("key"),
            "outcome": row.get("outcome"), "records_observed": row.get("records_observed"),
            "list_complete": row.get("list_complete"), "detail_complete": row.get("detail_complete"),
            "reason": row.get("reason"),
        } for row in coverage if not row.get("list_complete") or row.get("detail_complete") is False]
        if not topology_complete:
            gaps.insert(0, {"module": "topology", "outcome": "INCOMPLETE",
                            "reason": "Portal discovery did not certify all API-visible topology."})
        gaps.extend({"finding_id": item.id, "portal_id": item.portal_id, "portal_name": item.portal_name,
                     "module": item.module, "reason": item.summary}
                    for item in related if item.status == UNKNOWN and item.category == "fields")
        result.append({
            "id": ident, "title": title, "status": MANUAL,
            "confirmed_source_evidence": evidence, "api_coverage_limitations": gaps,
            "target_cloud_unknowns": [target], "vendor_confirmation_required": [vendor],
            "project_decisions_required": [business],
            "observed": f"{len(evidence)} confirmed source-evidence findings across the assessed environment. "
                        "Counts apply to the observed scope and may be lower bounds.",
            "requires_confirmation": vendor + " " + business,
            "finding_ids": [item.id for item in related],
        })
    return result


def analyze_environment(environment: EnvironmentSnapshot) -> Assessment:
    """Assess each portal independently, then aggregate only summary evidence."""
    sources = {key: dict(value) for key, value in SOURCES.items()}
    for key in ("field_limits", "limitations"):
        sources[key]["reviewed_on"] = "2026-10-07"
    context_source = dict(environment.source)
    answers = dict(environment.manual_answers)
    if context_source.get("build_origin") == "user_supplied":
        for key in ("build", "build_number", "source_build"):
            value = context_source.pop(key, None)
            if value is not None:
                answers.setdefault("source_build", value)
    context = Snapshot(environment.generated_at, context_source, environment.settings,
                       manual_answers=answers, interrupted_reason=environment.interrupted_reason)
    shared = analyze(context)
    findings = [_attach(finding, None) for finding in shared.findings if finding.id in _ENVIRONMENT_RULES]
    for finding in findings:
        if finding.id == "SOURCE_BUILD" and environment.source.get("build_origin") == "user_supplied":
            finding.evidence_basis = "USER_SUPPLIED_REQUIREMENT"
    portal_entries, field_inventories, coverage = [], [], []
    diagnostics = _diagnostics(environment.topology.diagnostics)
    global_coverage = list(environment.retained_global_coverage)
    global_seen = {row["key"] for row in global_coverage}
    if environment.global_snapshot:
        for dataset in environment.global_snapshot.datasets.values():
            global_seen.add(dataset.key)
            global_coverage.append(_coverage(dataset, None))
    for portal_id, portal_snapshot in environment.portals.items():
        portal = portal_snapshot.portal
        if portal_id in environment.retained_portals:
            entry = environment.retained_portals[portal_id]
            portal_entries.append(entry)
            coverage.extend(entry["coverage"])
            field_inventories.extend(entry["fields"])
            diagnostics.extend(entry["diagnostics"])
            findings.extend(Finding(**item) for item in entry["findings"])
            continue
        snapshot = replace(portal_snapshot.snapshot, manual_answers={**answers, **portal_snapshot.snapshot.manual_answers})
        fields = [_field_inventory(value, module, portal) for module, value in snapshot.fields.items()]
        portal_assessment = analyze(_analysis_snapshot(snapshot, fields))
        field_inventories.extend(fields)
        portal_findings = []
        for finding in portal_assessment.findings:
            if finding.id in _ENVIRONMENT_RULES or (fields and finding.id in _FIELD_RULES):
                continue
            if finding.id == "FIELD_NAME_COLLISIONS" and finding.status == CONFIRMED:
                finding = replace(finding, status=MANUAL, evidence_basis="INFERRED_FROM_METADATA",
                                  summary=finding.summary + " Case-folded UDF labels require target mapping confirmation; the form-rule naming restriction cannot be generalized.")
            portal_findings.append(_attach(finding, portal))
        for inventory in fields:
            portal_findings.extend(_attach(finding, portal) for finding in _metadata_findings(inventory, answers))
        portal_coverage = []
        for dataset in snapshot.datasets.values():
            if dataset.scope == "environment":
                if dataset.key not in global_seen:
                    global_seen.add(dataset.key)
                    global_coverage.append(_coverage(dataset, None))
                continue
            row = _coverage(dataset, portal)
            credentials = environment.stats.get("credential_coverage", {})
            if credentials.get("mode") == "per_instance":
                status = credentials.get("portals", {}).get(portal_id, "missing")
                row["credential_status"] = status if status in {"missing", "failed", "valid", "unverified"} else "unverified"
            portal_coverage.append(row)
        portal_diagnostics = _diagnostics(portal.diagnostics, portal)
        portal_diagnostics.extend(item for row in portal_coverage for item in row["diagnostics"])
        portal_diagnostics.extend(item for inventory in fields for item in inventory["diagnostics"])
        portal_diagnostics = _unique_diagnostics(portal_diagnostics)
        gaps = [row for row in portal_coverage if not row["list_complete"]]
        if gaps:
            portal_findings.append(_attach(Finding(
                id="OPERATION_COVERAGE", title="Portal operation coverage gaps", category="coverage",
                severity="high", status=UNKNOWN,
                summary=f"{len(gaps)} selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories.",
                examined_count=sum(row["records_observed"] or 0 for row in portal_coverage),
                evidence=[{"resource": row["key"], "outcome": row["outcome"], "records_observed": row["records_observed"]}
                          for row in gaps[:20]],
                module="multiple", evidence_basis="API_COVERAGE_LIMITATION",
                action="Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403.",
                sources=["api"],
            ), portal))
        capabilities = [_capability(value, module, portal) for module, value in snapshot.capabilities.items()]
        findings.extend(portal_findings)
        coverage.extend(portal_coverage)
        diagnostics.extend(portal_diagnostics)
        portal_entries.append({
            "portal_id": portal_id, "portal_name": _label(portal.name), "metadata": _portal_metadata(portal),
            "summary": {"findings_by_status": dict(Counter(item.status for item in portal_findings)),
                        "collections_complete": sum(row["list_complete"] for row in portal_coverage),
                        "collections_with_gaps": len(gaps)},
            "coverage": portal_coverage, "findings": [asdict(item) for item in portal_findings],
            "capabilities": capabilities, "fields": fields, "diagnostics": portal_diagnostics,
        })
    coverage.extend(global_coverage)
    diagnostics.extend(item for row in global_coverage for item in row["diagnostics"])
    diagnostics = _unique_diagnostics(diagnostics)
    volumes = _volume_rows(coverage)
    for finding in findings:
        if finding.id in {"TARGET_LICENSE", "DISCOVERY_NETWORK"}:
            wanted = {"technicians", "computers", "assets"} if finding.id == "TARGET_LICENSE" else {"computers", "assets", "sites"}
            finding.evidence = [{"scope": row["scope"], "resource": row["resource"],
                                 "records_observed": row["records_observed"], "collections_unknown": row["collections_unknown"]}
                                for row in volumes if row["resource"] in wanted]
    topology = environment.topology
    selected = [portal for portal in topology.portals if portal.selected]
    discovered = [portal for portal in topology.portals if portal.discovered]
    assessed = sum(any(row.get("read_attempted") or row.get("pages_observed", 0) or row.get("list_complete")
                       for row in entry["coverage"]) or any(inventory.get("http_attempts", 0) for inventory in entry["fields"])
                   for entry in portal_entries)
    for finding in findings:
        if finding.id == "API_VISIBILITY":
            finding.summary = (f"{len(discovered)} portals discovered; {len(selected)} selected; {assessed} had collection attempts. "
                               "Directory metadata may use a separate authorized credential or a verified local list. Module reads use the integration key; hidden or unauthorized portals and records cannot be certified.")
            finding.evidence = [{"discovered": len(discovered), "selected": len(selected), "assessed": assessed,
                                 "discovery_complete": topology.complete}]
    if topology.mode in {"automatic", "assisted"} and (not topology.complete or not selected):
        findings.append(_attach(Finding(
            id="TOPOLOGY_COVERAGE", title="Portal discovery did not establish assessable environment coverage",
            category="coverage", severity="high", status=UNKNOWN,
            summary=("No portal inventory was established." if not selected else "The selected portal list does not certify a complete live directory.")
                    + " Discovery outcome: " + topology.outcome + ". Unknown scope is not an empty source or a passed migration check.",
            examined_count=0, affected_count=None, module="topology", evidence_basis="API_COVERAGE_LIMITATION",
            evidence=[{"discovery_outcome": topology.outcome, "selected_portals": len(selected),
                       "discovery_complete": topology.complete}],
            action="Review the sanitized discovery diagnostic. Resolve connection, authentication, query or endpoint compatibility as evidenced. "
                   "When discovery is unavailable, use only administrator-verified explicit portal IDs; do not guess an ID or a required role.",
            sources=["api"],
        ), None))
    questions = _questions(findings, coverage, topology.complete and topology.mode == "automatic")
    blockers = [{
        "finding_id": item.id, "portal_id": item.portal_id, "portal_name": item.portal_name,
        "module": item.module, "status": item.status, "reason": item.summary,
        "required_resolution": item.action, "blocker_type": "SOURCE_EXCEPTION" if item.status == CONFIRMED else "EVIDENCE_GAP",
    } for item in findings if item.severity.casefold() == "high" and item.status in {CONFIRMED, UNKNOWN}]
    blockers.extend({"finding_id": question["id"], "portal_id": None, "module": "migration_acceptance",
                     "status": MANUAL, "reason": question["title"],
                     "required_resolution": question["requires_confirmation"], "blocker_type": "AGREEMENT_REQUIRED"}
                    for question in questions)
    summary = {
        "portals_discovered": len(discovered), "portals_selected": len(selected), "portals_assessed": assessed,
        "portals_supplied_explicitly": sum(not portal.discovered for portal in selected),
        "portals_accessible": sum(portal.accessible is True for portal in selected),
        "portals_inaccessible": sum(portal.accessible is False for portal in selected),
        "portals_access_unknown": sum(portal.accessible is None for portal in selected),
        "collections_complete": sum(row["list_complete"] for row in coverage),
        "collections_incomplete": sum(not row["list_complete"] for row in coverage),
        "permission_related_operations": sum(item.get("classification") in _DENIED for item in diagnostics),
        "unsupported_unavailable_operations": sum(item.get("classification") in _UNAVAILABLE for item in diagnostics),
        "portal_context_operations": sum(item.get("classification") == "PORTAL_CONTEXT_REQUIRED" for item in diagnostics),
        "manual_confirmation_topics": len(questions),
        "findings_by_status": dict(Counter(item.status for item in findings)), "acceptance_items": len(blockers),
    }
    stats = {**environment.stats, "findings_by_status": summary["findings_by_status"],
             "portals_assessed": assessed, "global_scheduler": True}
    return Assessment(
        generated_at=environment.generated_at, source=_environment_source(environment.source),
        settings=_environment_settings(environment.settings), findings=findings, questions=questions,
        coverage=coverage, stats=stats, sources=sources, schema_version="2.0",
        notes=shared.notes + ([
            "Resumable assessment: completed instance evidence is retained from earlier passes; it is not reauthenticated or refreshed. Interrupted instances restart from their first read. Each pass has fresh request/time budgets.",
            "Completed with coverage gaps is not complete visibility. Counts combine observations made at different times; this is not a transactional snapshot.",
        ] if environment.resume_history else []) + [
            "Portal-specific findings retain portal IDs; matching numeric record IDs in different portals are not merged.",
            "Global resources are counted once. Portal users/technicians are membership observations; Assets, Computers and CIs overlap and are not summed into a unique asset population.",
            "Environment-wide confirmation topics are counted once; source impact and coverage remain portal-specific.",
            "Field definitions, option/default measurements and allowed schema labels are retained; raw field values, options, defaults and script bodies are excluded.",
            "Acceptance items are an evidence and decision register. The source scan cannot approve future Cloud migration behavior.",
            "Integration-key expiration was not queried. No verified read-only expiration API is implemented; key metadata is not required for this assessment.",
        ],
        environment={
            "summary": summary,
            **({"resume_history": environment.resume_history} if environment.resume_history else {}),
            "topology": {"outcome": topology.outcome, "complete": topology.complete,
                         **topology_scope_evidence(topology),
                         "mode": topology.mode, "endpoint": topology.endpoint, "source": topology.source,
                         "credential_scope": topology.credential_scope,
                         "selection_source": topology.selection_source,
                         "directory_outcome": topology_scope_evidence(topology)["directory_outcome"],
                         "pages": topology.pages, "limitations": topology.limitations,
                         "portals": [_portal_metadata(portal) for portal in topology.portals],
                         "diagnostics": _diagnostics(topology.diagnostics)},
            "volume_by_module": volumes, "risk_rollup": _risk_rollup(findings),
            "permissions": {"authentication": environment.authentication,
                            "credential_scopes": _credential_scopes(environment),
                            "integration_key_expiration": "NOT_ASSESSED",
                            "key_expiration_note": "No verified read-only expiration mechanism is implemented. Expiration is neither inferred nor required for the assessment.",
                            "orgusers_collection": _environment_source(environment.source).get("orgusers_collection", "not_established"),
                            "portals_accessible": summary["portals_accessible"],
                            "portals_access_unknown": summary["portals_access_unknown"],
                            "denied_operations": [item for item in diagnostics if item.get("classification") in _DENIED],
                            "unsupported_operations": [item for item in diagnostics if item.get("classification") in _UNAVAILABLE]},
            "stop": {"classification": environment.stop_classification, "reason": environment.interrupted_reason,
                     "requests": environment.stats.get("requests"), "max_requests": environment.stats.get("max_requests"),
                     "elapsed_seconds": environment.stats.get("elapsed_seconds")},
            "acceptance_blockers": blockers,
        },
        portals=portal_entries, global_resources={"coverage": global_coverage, "resource_count": len(global_coverage)},
        field_inventory=field_inventories, diagnostics=diagnostics,
    )
