"""Conservative, side-effect-free migration impact assessment.

Missing fields, denied endpoints and partial samples are never converted to a
clean bill of health. Findings retain identifiers and measurements, not source
ticket text, user names, email addresses, file names, or script bodies.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .models import Assessment, Dataset, Finding, Snapshot
from .sources import SOURCES

CONFIRMED = "CONFIRMED_IMPACT"
CLEAN = "NO_ISSUE_OBSERVED"
UNKNOWN = "UNKNOWN"
MANUAL = "MANUAL_CONFIRMATION"
MAX_EXAMPLES = 20
_MISSING = object()
_OK = {"ok", "success", "complete", "collected"}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


def _identifier(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("id")
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and _ID.fullmatch(value):
        return value
    return None


def _pick(record: dict[str, Any], *paths: str) -> Any:
    for path in paths:
        value: Any = record
        for part in path.split("."):
            if not isinstance(value, dict) or part not in value:
                value = _MISSING
                break
            value = value[part]
        if value is not _MISSING:
            return value
    return _MISSING


def _integer(value: Any) -> int | None:
    if isinstance(value, dict):
        value = value.get("value", _MISSING)
    if isinstance(value, bool) or value is None or value is _MISSING:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None or value is _MISSING:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _time(value: Any) -> datetime | None:
    """Recognize epoch milliseconds or ISO dates, never localized display text."""
    if isinstance(value, dict):
        value = value.get("value", _MISSING)
    numeric = _integer(value)
    if numeric is not None:
        if numeric < 0:
            return None
        try:
            return datetime.fromtimestamp(numeric / 1000, timezone.utc)
        except (OverflowError, ValueError, OSError):
            return None
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            # Date-only fields have a calendar-day interpretation. A naive
            # time-of-day would require an unprovided server timezone.
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                parsed = parsed.replace(tzinfo=timezone.utc)
            else:
                return None
        return parsed.astimezone(timezone.utc)
    return None


def _years_before(reference: datetime, years: int) -> datetime:
    try:
        return reference.replace(year=reference.year - years)
    except ValueError:
        return reference.replace(year=reference.year - years, day=28)


def _evidence(row: dict[str, Any], **measurements: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    entity_id = _identifier(row.get("id"))
    if entity_id is not None:
        result["entity_id"] = entity_id
    parent = _identifier(_pick(row, "_parent_id", "request_id", "request.id"))
    if parent is not None:
        result["parent_id"] = parent
    # All names in this map are internal constants, never record property names.
    for key, value in measurements.items():
        if isinstance(value, (int, float, bool)) and not isinstance(value, complex):
            if not isinstance(value, float) or math.isfinite(value):
                result[key] = value
        elif key.endswith("_id") and _identifier(value) is not None:
            result[key] = _identifier(value)
    return result


def _safe_source(source: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("host", "base_url", "url"):
        value = source.get(key)
        if isinstance(value, str):
            try:
                parts = urlsplit(value if "://" in value else "https://" + value)
                if parts.hostname:
                    netloc = "[" + parts.hostname + "]" if ":" in parts.hostname else parts.hostname
                    if parts.port:
                        netloc += ":" + str(parts.port)
                    result[key] = urlunsplit((parts.scheme, netloc, parts.path, "", ""))
            except ValueError:
                pass
    for key in ("build", "build_number", "source_build"):
        value = _integer(source.get(key))
        if value is not None:
            result[key] = value
    # Preserve only fixed recognizable labels; arbitrary version banners may
    # contain credentials echoed by a broken endpoint.
    for key in ("product", "deployment"):
        if isinstance(source.get(key), str) and source[key] in {"ServiceDesk Plus", "ServiceDesk Plus On-Premises", "on-premises", "onprem", "standard"}:
            result[key] = source[key]
    if isinstance(source.get("demo"), bool):
        result["demo"] = source["demo"]
    if isinstance(source.get("build_origin"), str) and source["build_origin"] in {"user_supplied", "not_exposed", "api_verified"}:
        result["build_origin"] = source["build_origin"]
    portal = _identifier(source.get("portal_id"))
    if portal is not None:
        result["portal_id"] = portal
    return result


def _safe_settings(settings: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "rpm", "requests_per_minute", "max_requests", "max_records", "page_size",
        "max_pages", "detail_limit", "max_details", "timeout", "timeout_seconds",
        "max_retries", "verify_tls", "allow_http", "mode", "sample_size",
        "deep", "budget", "request_budget", "max_runtime_seconds",
        "max_minutes", "subresource_parents", "max_child_records", "read_only_get_only",
        "attachment_downloads", "tls_verification", "credential_visibility_verified", "demo",
    }
    result = {}
    for key in allowed:
        value = settings.get(key, _MISSING)
        if isinstance(value, (bool, int, float)):
            result[key] = value
        elif key == "mode" and isinstance(value, str) and value in {"quick", "standard", "deep", "full", "bounded"}:
            result[key] = value
    if isinstance(settings.get("count_policy"), str) and settings["count_policy"] in {"first", "always", "never"}:
        result["count_policy"] = settings["count_policy"]
    selected = settings.get("collections_selected")
    if isinstance(selected, list):
        known = {"requests", "archived_requests", "request_notes", "request_tasks", "changes", "problems", "projects",
                 "releases", "users", "technicians", "incident_templates", "service_templates", "assets", "computers",
                 "ci_types", "cis", "roles", "sites", "support_groups", "slas", "request_lifecycles", "change_workflows",
                 "custom_triggers", "request_fields", "field_definitions", "reports", "contracts", "purchases"}
        result["collections_selected"] = [key for key in selected if isinstance(key, str) and key in known]
    return result


class _Analyzer:
    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot
        self.answers = snapshot.manual_answers
        self.findings: list[Finding] = []
        self.reference = _time(snapshot.generated_at)
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def dataset(self, key: str) -> Dataset | None:
        return self.snapshot.datasets.get(key)

    def rows(self, key: str) -> list[dict[str, Any]]:
        if key not in self._cache:
            ds = self.dataset(key)
            merged: dict[str, dict[str, Any]] = {}
            anonymous = []
            if ds:
                for row in [*ds.records, *ds.details]:
                    if not isinstance(row, dict):
                        continue
                    identity = _identifier(row.get("id"))
                    parent = _identifier(_pick(row, "_parent_id", "request_id", "request.id"))
                    if identity is None:
                        anonymous.append(row)
                    else:
                        identity = (parent + "/" if parent else "") + identity
                        merged[identity] = {**merged.get(identity, {}), **row}
            self._cache[key] = [*merged.values(), *anonymous]
        return self._cache[key]

    def complete(self, keys: list[str]) -> bool:
        for key in keys:
            ds = self.dataset(key)
            if not ds or not ds.list_complete or ds.status not in _OK:
                return False
            if ds.total_count is not None and ds.total_count > len(self.rows(key)):
                return False
        return True

    def add(self, ident: str, title: str, category: str, severity: str,
            status: str, summary: str, *, affected: int | None = None,
            examined: int = 0, evidence: list[dict[str, Any]] | None = None,
            action: str = "Review the identified scope with the migration owner.",
            sources: tuple[str, ...] = ("limitations",), complete: bool = False) -> None:
        coverage = (
            "All required observed fields checked in the enumerated API-visible scope. "
            if complete else "Counts describe observed evidence and may be lower bounds. "
        ) + "API permissions and omitted subresources can hide additional data."
        self.findings.append(Finding(
            id=ident, title=title, category=category, severity=severity,
            status=status, summary=summary, affected_count=affected,
            examined_count=examined, evidence=(evidence or [])[:MAX_EXAMPLES],
            action=action, sources=list(sources), coverage=coverage,
        ))

    def checked(self, ident: str, title: str, category: str, severity: str,
                keys: list[str], examined: int, positives: list[dict[str, Any]],
                expected: int, message: str, *, sources=("limitations",),
                action="Review the identified records before migration.",
                all_fields: bool = True) -> None:
        complete = self.complete(keys) and examined == expected and all_fields
        if positives:
            status = CONFIRMED
            summary = f"{len(positives)} affected records observed. {message}"
        elif complete:
            status = CLEAN
            summary = f"No matching issue among {examined} API-visible records checked."
        else:
            status = UNKNOWN
            summary = (f"No matching issue established from {examined} checked records; "
                       "collection or required-field coverage is incomplete.")
        self.add(ident, title, category, severity, status, summary,
                 affected=len(positives) if positives or complete else None,
                 examined=examined, evidence=positives, action=action,
                 sources=tuple(sources), complete=complete)

    def run(self) -> Assessment:
        self._baseline()
        self._historical()
        self._relationships()
        self._attachments()
        self._identities()
        self._fields()
        self._dates_assets()
        self._configuration()
        self._manual_context()
        counts = Counter(item.status for item in self.findings)
        stats = {
            "findings_by_status": {status: counts[status] for status in (CONFIRMED, CLEAN, UNKNOWN, MANUAL)},
            "datasets_observed": len(self.snapshot.datasets),
            "api_scope_confirmed_by_user": self.answers.get("api_scope_confirmed") is True,
        }
        for key, value in self.snapshot.stats.items():
            if isinstance(key, str) and re.fullmatch(r"[a-z_]{1,60}", key):
                if isinstance(value, (int, float, bool)):
                    stats[key] = value
        return Assessment(
            generated_at=self.snapshot.generated_at,
            source=_safe_source(self.snapshot.source),
            settings=_safe_settings(self.snapshot.settings),
            findings=self.findings, questions=self._questions(),
            coverage=[ds.coverage() for ds in self.snapshot.datasets.values()],
            stats=stats, sources={key: dict(value) for key, value in SOURCES.items()},
            notes=[
                "Source-only assessment; no migration, configuration changes, attachment downloads, or arbitrary query execution are performed.",
                "Unknown and manual-confirmation findings are unresolved, not passed checks.",
                "Manual answers describe user-supplied requirements and have not been verified against the API or target tenant.",
                "An API credential can see only its authorized scope; completed pagination does not certify organization-wide visibility.",
                "Rule documentation was reviewed on 2026-10-05. Confirm target-tenant and migration-build behavior with ManageEngine.",
                "Positive counts can be lower bounds; findings may concern overlapping records and must not be summed as unique impacted records.",
            ] + (["Collection ended early; unresolved coverage remains."] if self.snapshot.interrupted_reason else []),
        )

    def _baseline(self) -> None:
        confirmed = self.answers.get("api_scope_confirmed") is True
        self.add("API_VISIBILITY", "Credential visibility", "coverage", "high", MANUAL,
                 "The user reports the credential has the required scope; this is not API-verified."
                 if confirmed else "The API cannot establish that this credential can see every instance, site, module, and record.",
                 sources=("migration",), action="Confirm the assessed instance and read visibility with its administrator.")
        api_build = _integer(_pick(self.snapshot.source, "build", "build_number", "source_build"))
        supplied = _integer(self.answers.get("source_build"))
        build = api_build if api_build is not None else supplied
        if build is None:
            status, summary = MANUAL, "The source build was not available from verified metadata or a supplied answer."
        else:
            status = CONFIRMED if build < 14810 else CLEAN
            origin = "API metadata" if api_build is not None else "User-supplied answer (not API-verified)"
            summary = f"{origin} identifies build {build}; the documented migration baseline is 14810."
        self.add("SOURCE_BUILD", "Source build prerequisite", "platform", "high", status,
                 summary, evidence=[{"build": build, "minimum_build": 14810}] if build is not None else [],
                 action="Confirm the supported migration build and any required upgrade with ManageEngine.", sources=("migration",))

    def _historical(self) -> None:
        keys = ["requests", "archived_requests", "changes", "problems", "projects"]
        for years, ident in ((1, "HISTORY_WINDOW_ONE_YEAR"), (5, "HISTORY_WINDOW_FIVE_YEARS")):
            checked = 0
            hits = []
            expected = sum(len(self.rows(key)) for key in keys)
            cutoff = _years_before(self.reference, years) if self.reference else None
            for key in keys:
                for row in self.rows(key):
                    created = _time(_pick(row, "created_time", "created_date"))
                    if created is None or cutoff is None:
                        continue
                    checked += 1
                    if created < cutoff:
                        hits.append(_evidence(row, age_years_threshold=years,
                                              created_epoch_ms=int(created.timestamp() * 1000)))
            self.checked(ident, f"Module records older than {years} year(s)", "historical data", "high",
                         keys, checked, hits, expected,
                         "An agreed historical-data disposition is required.", sources=("migration",),
                         action="Confirm the required history window and vendor-supported handling for these age groups.")
        history = []
        checked = 0
        for key in keys:
            for row in self.rows(key):
                value = _pick(row, "history", "history_entries", "history_count")
                count = len(value) if isinstance(value, list) else _integer(value)
                if count is not None and count >= 0:
                    checked += 1
                    if count:
                        history.append(_evidence(row, history_entries=count))
        requirement = self.answers.get("requires_legacy_history") is True
        self.add("LEGACY_HISTORY", "Historical audit-detail preservation", "historical data", "high",
                 CONFIRMED if history or requirement else MANUAL,
                 (f"History entries were observed on {len(history)} records. " if history else "History subresources have not been exhaustively inspected. ") +
                 ("Preserving legacy history is a user-supplied requirement. " if requirement else "") +
                 "The built-in migration excludes History-tab data.",
                 affected=len(history) if history else None, examined=checked, evidence=history,
                 action="Agree how legacy history will be preserved and validated; ticket counts cannot verify it.")

    def _relationships(self) -> None:
        keys = ["requests", "archived_requests"]
        rules = [
            ("LINKED_REQUESTS", "Linked-request relationships", ("linked_requests", "linked_request_ids", "has_linked_requests")),
            ("REQUEST_DEPENDENCIES", "Request dependencies", ("dependent_requests", "dependencies", "request_dependencies")),
            ("REQUEST_CHANGE_LINKS", "Request and change associations", ("changes", "associated_changes", "associated_change", "change")),
        ]
        for ident, title, paths in rules:
            checked, hits = 0, []
            for key in keys:
                for row in self.rows(key):
                    value = _pick(row, *paths)
                    if value is _MISSING:
                        continue
                    if isinstance(value, bool):
                        checked += 1
                        if value:
                            hits.append(_evidence(row, relationship_present=True))
                    elif value is None or value == []:
                        checked += 1
                    elif isinstance(value, list):
                        checked += 1
                        hits.append(_evidence(row, relationship_count=len(value)))
                    elif isinstance(value, dict) and _identifier(value):
                        checked += 1
                        hits.append(_evidence(row, relationship_count=1, related_id=value.get("id")))
            self.checked(ident, title, "relationships", "high", keys, checked, hits,
                         sum(len(self.rows(key)) for key in keys),
                         "The identified relationship requires a migration disposition.")
        archived = self.rows("archived_requests")
        checked, hits = 0, []
        for row in archived:
            values = [_pick(row, key) for key in ("approvals", "dependencies", "resources")]
            known = all(value is None or isinstance(value, list) for value in values)
            if known:
                checked += 1
            count = sum(len(value) for value in values if isinstance(value, list))
            if count:
                hits.append(_evidence(row, affected_subentities=count))
        self.checked("ARCHIVED_SUBENTITIES", "Archived-request subentity exposure", "historical data", "high",
                     ["archived_requests"], checked, hits, len(archived),
                     "These archived subentities need separate preservation.", sources=("limitations", "migration_scope"))

    def _attachments(self) -> None:
        keys = ["requests", "archived_requests", "changes", "problems", "projects", "assets", "computers"]
        checked, hits, uncertain_units = 0, [], []
        expected = sum(len(self.rows(key)) for key in keys)
        for key in keys:
            for row in self.rows(key):
                attachments = _pick(row, "attachments")
                if not isinstance(attachments, list):
                    continue
                seen, known_bytes, missing = set(), 0, 0
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        missing += 1
                        continue
                    aid = _identifier(attachment.get("id"))
                    if aid is not None and aid in seen:
                        continue
                    if aid is not None:
                        seen.add(aid)
                    size = _integer(_pick(attachment, "size", "size_in_bytes", "file_size", "filesize"))
                    if size is None or size < 0:
                        missing += 1
                    else:
                        known_bytes += size
                if not missing:
                    checked += 1
                measurement = _evidence(row, known_attachment_bytes=known_bytes,
                                        missing_sizes=missing, decimal_limit=48_000_000,
                                        binary_limit=50_331_648)
                if known_bytes > 50_331_648:
                    hits.append(measurement)
                elif known_bytes > 48_000_000:
                    uncertain_units.append(measurement)
        # Never claim complete attachment inspection: immediate-owner fields
        # do not establish the coverage of every conversation/task/resolution.
        if hits:
            status = CONFIRMED
            summary = f"{len(hits)} observed owner totals exceed both interpretations of 48 MB."
        elif uncertain_units:
            status = MANUAL
            summary = "Observed totals fall between decimal and binary interpretations of 48 MB; confirm the vendor's byte threshold."
        else:
            status = UNKNOWN
            summary = "No oversized owner was established; unseen attachment subresources and missing sizes remain unverified."
        self.add("ATTACHMENT_SIZE", "Attachment-size exposure", "attachments", "high", status,
                 summary, affected=len(hits) if hits else None, examined=checked,
                 evidence=hits or uncertain_units,
                 action="Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity.")
        notes, checked, hits = self.rows("request_notes"), 0, []
        for row in notes:
            value = _pick(row, "attachments")
            if isinstance(value, list):
                checked += 1
                if value:
                    hits.append(_evidence(row, attachment_count=len(value)))
        self.checked("NOTE_ATTACHMENTS", "Attachments on request notes", "attachments", "high",
                     ["request_notes"], checked, hits, len(notes),
                     "Identified note attachments require separate preservation.")

    def _identities(self) -> None:
        techs = self.rows("technicians")
        checked, hits, addresses = 0, [], defaultdict(list)
        for row in techs:
            value = _pick(row, "email_id", "email", "user.email_id")
            if value is _MISSING:
                continue
            if value is None or isinstance(value, str):
                checked += 1
                if value is None or not value.strip():
                    hits.append(_evidence(row, missing_email=True))
                else:
                    addresses[value.strip().casefold()].append(row)
        for rows in addresses.values():
            if len(rows) > 1:
                hits.extend(_evidence(row, duplicate_email_group_size=len(rows)) for row in rows)
        self.checked("TECHNICIAN_EMAILS", "Technician email readiness", "identity", "high",
                     ["technicians"], checked, hits, len(techs),
                     "Resolve missing or shared technician email identities.", sources=("migration",))
        users = {_identifier(row.get("id")): row for key in ("users", "technicians") for row in self.rows(key)
                 if _identifier(row.get("id")) is not None}
        checked, hits, references = 0, [], 0
        template_keys = ["incident_templates", "service_templates"]
        for key in template_keys:
            for row in self.rows(key):
                stages = _pick(row, "approval_levels", "approval_stages")
                if not isinstance(stages, list):
                    continue
                for stage in stages:
                    if not isinstance(stage, dict) or not isinstance(stage.get("approvers"), list):
                        continue
                    for person in stage["approvers"]:
                        references += 1
                        uid = _identifier(person)
                        resolved = users.get(uid, person if isinstance(person, dict) else {})
                        login = _pick(resolved, "is_login_enabled", "login_enabled", "has_login")
                        if isinstance(login, bool):
                            checked += 1
                            if not login:
                                hits.append(_evidence(row, approver_id=uid, login_enabled=False))
        self.add("APPROVER_LOGIN", "Approver and CAB login access", "identity", "high",
                 CONFIRMED if hits else UNKNOWN,
                 f"{len(hits)} explicit non-login approver references found; CAB and unresolved memberships still need validation.",
                 affected=len(hits) if hits else None, examined=checked, evidence=hits,
                 action="Validate login access for every service approver and CAB member; missing user fields are inconclusive.")

    def _fields(self) -> None:
        fields = self.rows("request_fields")
        field_keys = ["request_fields"]
        # The documented global UDF collection is not Request-only. Use an
        # explicit module tag; unidentified global definitions remain unknown.
        global_rows = self.rows("field_definitions")
        ambiguous_global = False
        if global_rows and not fields:
            field_keys = ["field_definitions"]
            for row in global_rows:
                module = _pick(row, "module", "module_name", "entity", "entity_type")
                if isinstance(module, dict):
                    module = module.get("name", module.get("value"))
                if isinstance(module, str):
                    normalized_module = module.casefold().replace(" ", "_")
                    if normalized_module in {"request", "requests", "incident", "incidents", "service_request", "service_requests"}:
                        fields.append(row)
                else:
                    ambiguous_global = True
        # Only recognized types participate in type-specific caps.
        type_aliases = {
            "single_line": "string", "singleline": "string", "multi_line": "string", "multiline": "string",
            "pick_list": "string", "picklist": "string", "multi_select": "string", "multiselect": "string",
            "radio": "string", "radio_button": "string", "checkbox": "string", "email": "string",
            "phone": "string", "url": "string", "web_url": "string", "string": "string",
            "numeric": "long", "number": "long", "long": "long", "auto_number": "long",
            "date_time": "datetime", "datetime": "datetime", "date": "date",
            "boolean": "boolean", "decision_box": "boolean", "decimal": "double", "double": "double",
            "percent": "double", "currency": "double", "lookup": "lookup", "multi_lookup": "multilookup",
        }
        counts = Counter()
        known = 0
        names = defaultdict(list)
        definitions = {}
        for row in fields:
            raw_type = _pick(row, "field_type", "type", "data_type")
            if isinstance(raw_type, dict):
                raw_type = raw_type.get("name", raw_type.get("value"))
            normalized = raw_type.lower().replace("-", "_").replace(" ", "_") if isinstance(raw_type, str) else ""
            if normalized in type_aliases:
                counts[type_aliases[normalized]] += 1
                known += 1
            name = _pick(row, "display_name", "name", "label")
            if isinstance(name, str) and name.strip():
                names[name.strip().casefold()].append(row)
            internal = _pick(row, "column_name", "field_name", "api_name", "name")
            if isinstance(internal, str) and internal.startswith("udf_"):
                definitions[internal] = (row, normalized)
        # Template detail can expose typed field references even when the
        # global definition endpoint is unavailable. These support value checks
        # but do not establish a complete field-definition inventory.
        for template_key in ("incident_templates", "service_templates"):
            for template in self.rows(template_key):
                template_fields = template.get("fields")
                if not isinstance(template_fields, list):
                    continue
                for row in template_fields:
                    if not isinstance(row, dict):
                        continue
                    internal = _pick(row, "column_name", "field_name", "api_name")
                    typ = _pick(row, "field_type", "type", "data_type")
                    if isinstance(typ, dict):
                        typ = typ.get("name", typ.get("value"))
                    if isinstance(internal, str) and internal.startswith("udf_") and isinstance(typ, str):
                        normalized = typ.lower().replace("-", "_").replace(" ", "_")
                        definitions.setdefault(internal, (row, normalized))
        limits = {"string": 250, "long": 75, "datetime": 75, "boolean": 25,
                  "double": 50, "lookup": 10, "multilookup": 10, "date": 10}
        excess = [{"observed_fields": len(fields), "limit": 250}] if len(fields) > 250 else []
        excess.extend({"observed_fields": counts[k], "limit": limit} for k, limit in limits.items() if counts[k] > limit)
        complete = (field_keys == ["request_fields"] and self.complete(field_keys)
                    and known == len(fields) and not ambiguous_global)
        self.add("REQUEST_FIELD_CAPACITY", "Request additional-field capacity", "fields", "high",
                 CONFIRMED if excess else CLEAN if complete else UNKNOWN,
                 f"{len(fields)} distinct request-field definitions observed; {known} have recognized types. The combined paid-tier limit is 250.",
                 affected=len(excess) if excess else 0 if complete else None,
                 examined=len(fields), evidence=excess, sources=("field_limits",), complete=complete,
                 action="Validate every field type and target entitlement; free-tier and other-module limits differ.")
        duplicates = [row for group in names.values() if len(group) > 1 for row in group]
        self.checked("FIELD_NAME_COLLISIONS", "Case-insensitive field-name collisions", "fields", "high",
                     field_keys, sum(len(group) for group in names.values()),
                     [_evidence(row) for row in duplicates], len(fields),
                     "Review definition identity and naming before target mapping.",
                     all_fields=not ambiguous_global and field_keys == ["request_fields"])
        # Definitions establish meaning; field-key prefixes are not sufficient
        # to invent a type or a limit for an unknown build.
        checked, hits = 0, []
        request_rows = [row for key in ("requests", "archived_requests") for row in self.rows(key)]
        for row in request_rows:
            values = _pick(row, "udf_fields", "additional_fields")
            if not isinstance(values, dict):
                continue
            for key, value in values.items():
                definition = definitions.get(key)
                if not definition or value is None:
                    continue
                field, typ = definition
                limit = {"single_line": 250, "singleline": 250, "multi_line": 5000, "multiline": 5000,
                         "email": 50, "phone": 30, "url": 250, "web_url": 250}.get(typ)
                if limit is not None and isinstance(value, str):
                    checked += 1
                    if len(value) > limit:
                        hits.append(_evidence(row, field_id=field.get("id"), character_count=len(value), limit=limit))
                elif typ in {"numeric", "number", "decimal", "double", "long"} and not isinstance(value, bool):
                    try:
                        decimal = Decimal(str(value))
                        if decimal.is_finite():
                            parts = decimal.as_tuple()
                            # Count without expanding exponent notation: a
                            # tiny value such as 1e999999 must not allocate an
                            # enormous intermediate string.
                            digits = (len(parts.digits) + parts.exponent if parts.exponent >= 0
                                      else max(len(parts.digits), -parts.exponent + 1))
                            checked += 1
                            if digits > 15:
                                hits.append(_evidence(row, field_id=field.get("id"), digit_count=digits, limit=15))
                    except (ValueError, InvalidOperation):
                        pass
        self.add("FIELD_VALUE_LENGTHS", "Additional-field value sizes", "fields", "high",
                 CONFIRMED if hits else UNKNOWN,
                 f"{checked} typed values checked; definitions, defaults, options, and uninspected record values may add exposure.",
                 affected=len(hits) if hits else None, examined=checked, evidence=hits,
                 sources=("field_limits",), action="Review identified values and obtain complete definitions/defaults/options before accepting field compatibility.")

    def _dates_assets(self) -> None:
        request_keys = ["requests", "archived_requests"]
        checked, hits = 0, []
        for key in request_keys:
            for row in self.rows(key):
                created = _time(_pick(row, "created_time", "created_date"))
                start = _pick(row, "scheduled_start_time", "scheduled_start_date")
                end = _pick(row, "scheduled_end_time", "scheduled_end_date")
                if created:
                    dates = [_time(start), _time(end)]
                    if all(value is not _MISSING and (value is None or parsed is not None)
                           for value, parsed in zip([start, end], dates)):
                        checked += 1
                    if any(date is not None and date < created for date in dates):
                        hits.append(_evidence(row, schedule_precedes_creation=True))
        self.checked("REQUEST_SCHEDULE_DATES", "Request scheduled-date consistency", "data quality", "high",
                     request_keys, checked, hits, sum(len(self.rows(key)) for key in request_keys),
                     "The observed date ordering needs remediation.")
        # Computers are the relevant workstation/VM/host population. Avoid
        # asserting that arbitrary asset classes share service-tag semantics.
        computers = self.rows("computers")
        tags, checked, hits = defaultdict(list), 0, []
        for row in computers:
            tag = _pick(row, "service_tag", "servicetag", "computer_system.service_tag")
            if tag is None or isinstance(tag, str):
                checked += 1
                if isinstance(tag, str) and tag.strip():
                    tags[tag.strip()].append(row)
        for group in tags.values():
            if len(group) > 1:
                hits.extend(_evidence(row, duplicate_tag_group_size=len(group)) for row in group)
        self.checked("DUPLICATE_SERVICE_TAGS", "Computer service-tag collisions", "assets", "high",
                     ["computers"], checked, hits, len(computers), "Duplicate tags require a supported migration treatment.")
        checked, hits, vms = 0, [], 0
        for row in computers:
            is_vm = _pick(row, "is_virtual_machine", "computer_system.is_virtual_machine")
            typ = _pick(row, "type.name", "product_type.name", "computer_type")
            if is_vm is not True and not (isinstance(typ, str) and typ.casefold() in {"virtual machine", "virtual_machine"}):
                continue
            vms += 1
            host = _pick(row, "virtual_host", "virtual_host_id", "host", "computer_system.virtual_host")
            if host is _MISSING:
                continue
            checked += 1
            if host is None or host == "":
                hits.append(_evidence(row, missing_virtual_host=True))
        self.add("VM_HOST_LINKS", "Virtual-machine host references", "assets", "high",
                 CONFIRMED if hits else UNKNOWN,
                 f"{vms} explicitly classified VMs observed; {checked} host references checked. Unknown VM classifications remain outside this check.",
                 affected=len(hits) if hits else None, examined=checked, evidence=hits,
                 action="Validate VM classification and host relationships across the complete computer inventory.")
        keys = ["assets", "computers"]
        checked, hits = 0, []
        for key in keys:
            for row in self.rows(key):
                values = [_pick(row, *paths) for paths in (
                    ("acquisition_date", "acquired_date"),
                    ("warranty_expiry_date", "warranty_expiry"), ("expiry_date", "expiration_date"))]
                parsed = [_time(value) for value in values]
                if all(value is not _MISSING and (value is None or date is not None) for value, date in zip(values, parsed)):
                    checked += 1
                acquisition, warranty, expiry = parsed
                bad = ((acquisition and expiry and expiry <= acquisition) or
                       (acquisition and warranty and warranty <= acquisition) or
                       (warranty and expiry and warranty >= expiry))
                if bad:
                    hits.append(_evidence(row, invalid_date_order=True))
        self.checked("ASSET_DATE_ORDER", "Asset date-order consistency", "assets", "medium", keys,
                     checked, hits, sum(len(self.rows(key)) for key in keys),
                     "Observed date ordering can change migrated values.")

    def _configuration(self) -> None:
        workflow_keys = ["slas", "request_lifecycles", "request_workflows", "change_workflows"]
        observed = sum(len(self.rows(key)) for key in workflow_keys)
        evidence = [_evidence(row) for key in workflow_keys for row in self.rows(key)]
        # Request references are useful lower-bound evidence even if the
        # admin endpoint is not exposed.
        references = []
        for key in ("requests", "changes"):
            for row in self.rows(key):
                for path in ("sla", "request_lifecycle", "request_life_cycle", "request_workflow", "workflow", "change_workflow"):
                    value = _pick(row, path)
                    if isinstance(value, dict) and _identifier(value):
                        references.append(_evidence(row, configuration_id=value.get("id")))
        self.add("WORKFLOW_REBUILD", "Workflow and SLA reconstruction", "configuration", "high",
                 CONFIRMED if observed or references else UNKNOWN,
                 f"{observed} configuration objects and {len(references)} record references observed. Source inventory does not verify target reconstruction.",
                 affected=observed if observed else None, examined=observed,
                 evidence=evidence + references, sources=("migration",),
                 action="Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent.")
        hits, checked = [], 0
        for key in ("incident_templates", "service_templates"):
            for row in self.rows(key):
                rules = _pick(row, "field_and_form_rules", "field_form_rules", "form_rules")
                if not isinstance(rules, list):
                    continue
                checked += 1
                count = 0
                for rule in rules:
                    if not isinstance(rule, dict):
                        continue
                    actions = rule.get("actions", [])
                    if not isinstance(actions, list):
                        continue
                    for action in actions:
                        if not isinstance(action, dict):
                            continue
                        action_type = _pick(action, "type", "action_type")
                        if isinstance(action_type, str) and action_type.casefold().replace(" ", "_") in {"custom_script", "execute_script"}:
                            count += 1
                if count:
                    hits.append(_evidence(row, custom_script_actions=count))
        self.add("FORM_SCRIPT_ACTIONS", "Form-script action compatibility", "configuration", "high",
                 CONFIRMED if hits else UNKNOWN,
                 f"{checked} template rule collections inspected; {len(hits)} templates contain explicit script actions.",
                 affected=len(hits) if hits else None, examined=checked, evidence=hits,
                 action="Review script actions and unexposed Change form rules; test supported target scripting behavior.")
        checked, hits = 0, []
        report_ds = self.dataset("reports")
        documented_query_filter = bool(report_ds and "view-all-query-reports" in report_ds.doc_url)
        for row in self.rows("reports"):
            typ = _pick(row, "type", "report_type")
            if isinstance(typ, dict):
                typ = typ.get("name")
            query = _pick(row, "query", "sql_query")
            if isinstance(typ, str):
                checked += 1
                if typ.strip().casefold() in {"query", "query report", "query_report", "sql"}:
                    hits.append(_evidence(row, query_report=True))
            elif isinstance(query, str) and query.strip():
                checked += 1
                hits.append(_evidence(row, query_report=True))
            elif documented_query_filter:
                checked += 1
                hits.append(_evidence(row, query_report=True))
        self.checked("QUERY_REPORTS", "Query-report inventory review", "reporting", "high", ["reports"],
                     checked, hits, len(self.rows("reports")),
                     "This query-report inventory may include built-ins; custom status and actual usage are not established.",
                     sources=("limitations", "reporting"),
                     action="Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment.")
        complexity, inspected = [], 0
        for key in ("incident_templates", "service_templates"):
            for row in self.rows(key):
                tasks, resources = row.get("tasks"), row.get("resources")
                if isinstance(tasks, list) or isinstance(resources, list):
                    inspected += 1
                violations = {}
                if isinstance(tasks, list) and len(tasks) > 200:
                    violations["associated_tasks"] = len(tasks)
                    violations["task_limit"] = 200
                if isinstance(resources, list):
                    if len(resources) > 20:
                        violations["resource_count"] = len(resources)
                        violations["resource_limit"] = 20
                    for resource in resources:
                        questions = resource.get("questions") if isinstance(resource, dict) else None
                        if isinstance(questions, list):
                            if len(questions) > 20:
                                violations["largest_question_count"] = max(violations.get("largest_question_count", 0), len(questions))
                                violations["question_limit"] = 20
                            for question in questions:
                                options = question.get("options") if isinstance(question, dict) else None
                                if isinstance(options, list) and len(options) > 300:
                                    violations["largest_option_count"] = max(violations.get("largest_option_count", 0), len(options))
                                    violations["option_limit"] = 300
                if violations:
                    complexity.append(_evidence(row, **violations))
        self.add("TEMPLATE_COMPLEXITY", "Template task and resource limits", "configuration", "high",
                 CONFIRMED if complexity else UNKNOWN,
                 f"{inspected} templates exposed relevant nested metadata; {len(complexity)} exceed a documented count limit.",
                 affected=len(complexity) if complexity else None, examined=inspected, evidence=complexity,
                 action="Review identified template structures and all uncollected task/resource/question details.")
        resolutions, inspected = [], 0
        for key in ("requests", "archived_requests"):
            for row in self.rows(key):
                content = _pick(row, "resolution.content", "resolution.description")
                if isinstance(content, str):
                    inspected += 1
                    if len(content) > 65536:
                        resolutions.append(_evidence(row, character_count=len(content), limit=65536))
        self.add("RESOLUTION_LENGTH", "Request resolution length", "historical data", "medium",
                 CONFIRMED if resolutions else UNKNOWN,
                 f"{inspected} resolution values measured; {len(resolutions)} exceed the documented limit.",
                 affected=len(resolutions) if resolutions else None, examined=inspected, evidence=resolutions,
                 action="Preserve identified long resolutions and inspect uncollected historical text fields.")
        schedules = self.rows("maintenances")
        hits = [_evidence(row) for row in schedules if isinstance(_pick(row, "schedule", "recurrence"), dict)]
        self.add("RECURRING_MAINTENANCE", "Recurring maintenance schedules", "configuration", "medium",
                 CONFIRMED if hits else UNKNOWN,
                 f"{len(hits)} explicit schedules observed; unexposed recurrence settings require a manual inventory.",
                 affected=len(hits) if hits else None, examined=len(schedules), evidence=hits,
                 action="Inventory recurring maintenance and rebuild its schedule at the agreed migration stage.")
        scope_keys = ["cis", "ci_types", "releases", "custom_modules"]
        scope = sum(len(self.rows(key)) for key in scope_keys)
        self.add("MODULE_MIGRATION_SCOPE", "CMDB, Releases and custom-module migration scope", "scope", "high", MANUAL,
                 f"{scope} records or type definitions observed in these inventories. An absent or denied endpoint does not prove a module is unused.",
                 examined=scope, evidence=[_evidence(row) for key in scope_keys for row in self.rows(key)],
                 sources=("migration_scope",),
                 action="Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible.")
        checked, hits = 0, []
        for row in self.rows("problems"):
            values = [_pick(row, path) for path in ("workaround", "solution", "associated_requests", "notifications")]
            if any(value is not _MISSING for value in values):
                checked += 1
            count = sum(1 for value in values if value is not _MISSING and value is not None and value != [] and value != "")
            if count:
                hits.append(_evidence(row, ancillary_categories_present=count))
        self.add("PROBLEM_ANCILLARY_DATA", "Problem ancillary-data preservation", "historical data", "high",
                 CONFIRMED if hits else UNKNOWN,
                 f"{len(hits)} problems have observed ancillary content; unexposed problem configuration remains unassessed.",
                 affected=len(hits) if hits else None, examined=checked, evidence=hits,
                 action="Record the migration disposition for problem ancillary content and configuration.")
        changes = self.rows("changes")
        self.add("CHANGE_IDENTIFIERS", "Change identifier preservation", "relationships", "medium", MANUAL,
                 f"{len(changes)} Change IDs observed. Source inspection cannot establish target ID preservation.",
                 examined=len(changes), evidence=[_evidence(row) for row in changes], sources=("migration",),
                 action="Confirm Change ID retention with support and require a cross-reference for any changed identifiers.")
        roles = self.rows("roles")
        self.add("ACCESS_MAPPING", "Role and organization-membership mapping", "identity", "high", MANUAL,
                 f"{len(roles)} role definitions observed; equivalent target permissions and membership have not been validated.",
                 examined=len(roles), evidence=[_evidence(row) for row in roles],
                 action="Test permitted and denied access for representative roles, sites, groups and sensitive queues.")

    def _manual_context(self) -> None:
        needs_bi = self.answers.get("needs_power_bi")
        lag = _number(self.answers.get("max_dashboard_lag_minutes"))
        years = _number(self.answers.get("required_history_years"))
        descriptions = self.answers.get("needs_full_descriptions")
        bi_impact = needs_bi is True and ((lag is not None and lag < 120) or (years is not None and years > 1))
        self.add("POWER_BI_REQUIREMENTS", "Native Power BI reporting requirements", "reporting", "high",
                 CONFIRMED if bi_impact else MANUAL,
                 "User-supplied reporting requirements exceed at least one documented native-integration behavior."
                 if bi_impact else "Native Power BI suitability requires confirmed history, refresh and field-detail requirements.",
                 evidence=[{key: value for key, value in {
                     "required_history_years": years, "max_dashboard_lag_minutes": lag,
                     "needs_power_bi": needs_bi,
                     "native_refresh_minutes": 120, "native_request_history_years": 1,
                 }.items() if isinstance(value, (int, float, bool))}], sources=("reporting",),
                 action="Validate the native connector against reporting requirements or design a separate historical extraction path.")
        self.add("REPORT_DESCRIPTION_REQUIREMENTS", "Full descriptions in reporting", "reporting", "medium", MANUAL,
                 "The user requires full descriptions; the actual report/extraction path needs validation. "
                 if descriptions is True else "Full-description requirements and the chosen report/extraction path are not established. ",
                 evidence=[{"needs_full_descriptions_user_supplied": descriptions}] if isinstance(descriptions, bool) else [],
                 sources=("reporting",),
                 action="Test required full descriptions in the selected reporting path. The generic Cloud report FAQ describes a 250-character display limit; this does not prove a native Power BI limit.")
        audit_years = _number(self.answers.get("required_audit_years"))
        self.add("ADMIN_AUDIT_RETENTION", "Cloud administrative audit retention", "retention", "medium",
                 CONFIRMED if audit_years is not None and audit_years > 3 else MANUAL,
                 "The user-supplied administrative audit requirement exceeds three years."
                 if audit_years is not None and audit_years > 3 else "The required administrative audit retention has not been validated against target behavior.",
                 evidence=[{"required_years": audit_years, "native_years": 3}] if audit_years is not None else [],
                 sources=("audit",), action="Plan complete periodic exports when needed; administrative logs are distinct from ticket-history retention.")
        scripts = self.answers.get("uses_local_scripts") is True
        self.add("AUTOMATION_RUNTIME", "Automation runtimes and execution budgets", "automation", "high",
                 CONFIRMED if scripts else MANUAL,
                 "The user reports local scripts in use; runtime and integration review is required."
                 if scripts else "External scripts, function execution volumes and target language/region support cannot be established from this inventory.",
                 evidence=[{"uses_local_scripts_user_supplied": True}] if scripts else [],
                 sources=("functions", "java_functions", "node_functions"),
                 action="Inventory script dependencies and actual execution rates; verify target datacenter support and quotas. Definition counts are not execution counts.")
        edition = self.answers.get("target_edition")
        supplied_target = ""
        if isinstance(edition, str) and edition.casefold() in {"standard", "professional", "enterprise", "free"}:
            supplied_target = "User-supplied target edition: " + edition.capitalize() + ". "
        if self.answers.get("target_region"):
            supplied_target += "A target region was supplied but is not API-verified. "
        self.add("TARGET_LICENSE", "Target edition and licensed capacity", "licensing", "high", MANUAL,
                 supplied_target + "Target entitlement, technician seats, asset capacity and add-ons require written confirmation.",
                 evidence=[{"observed_technicians": len(self.rows("technicians")), "observed_computers": len(self.rows("computers")),
                            "observed_assets": len(self.rows("assets"))}], sources=("editions", "migration"),
                 action="Match the source feature inventory and visible capacities to the target order and tenant limits.")
        self.add("DISCOVERY_NETWORK", "Asset discovery and network continuity", "operations", "medium", MANUAL,
                 "Source asset records cannot establish working Cloud discovery, probe coverage or network access.",
                 evidence=[{"observed_computers": len(self.rows("computers")), "observed_sites": len(self.rows("sites"))}],
                 sources=("editions",), action="Confirm discovery architecture and test repeated scans from every required network segment.")
        self.add("DELTA_CUTOVER", "Final delta and cutover behavior", "cutover", "high", MANUAL,
                 "A source-only read cannot validate delta semantics, target freshness, write-freeze duration or rollback.",
                 sources=("migration",),
                 action="Obtain vendor answers on changed/deleted records and subentities; rehearse final delta, mail transition, reconciliation and rollback.")
        self.add("BACKUP_RECOVERY", "Target export and recovery commitments", "recovery", "high", MANUAL,
                 "Customer export and recovery capabilities require tenant-specific confirmation. Public export and backup guidance is not fully aligned.",
                 sources=("exports", "admin_faq"),
                 action="Agree export completeness, frequency, restore granularity, RPO/RTO, support involvement and exit arrangements; demonstrate them before retiring the source.")
        self.add("EXTERNAL_INTEGRATIONS", "External integrations and email behavior", "integrations", "high", MANUAL,
                 "ServiceDesk Plus API inventory cannot enumerate all external flows, database consumers, jobs or old-email reply paths.",
                 sources=("email_behavior", "reporting", "functions"),
                 action="Inventory external automation/report consumers, replace authentication and endpoints, and test old-email threading and failure recovery.")

    def _questions(self) -> list[dict[str, Any]]:
        lookup = {finding.id: finding for finding in self.findings}
        specifications = [
            ("Q1", "Which limitations apply to our exact source build and target?",
             ["SOURCE_BUILD", "TARGET_LICENSE", "API_VISIBILITY"],
             "Source build evidence and triggered rules are listed above; complete target behavior is not observable from source credentials.",
             "Confirm source build, target edition/datacenter, migration support and credential coverage with the relevant administrator and ManageEngine."),
            ("Q2", "How will older records, CMDB, Releases and custom modules be handled?",
             ["HISTORY_WINDOW_ONE_YEAR", "HISTORY_WINDOW_FIVE_YEARS", "MODULE_MIGRATION_SCOPE", "LEGACY_HISTORY"],
             "Age findings give observed counts; module inventories and collection gaps identify remaining scope.",
             "Agree preservation requirements and a supported migration or retention method for each module, relationship and historical period."),
            ("Q3", "What will the final delta include?",
             ["DELTA_CUTOVER"],
             "The source inventory cannot establish final-delta behavior.",
             "Ask ManageEngine how edits, deletions, new conversations, attachments, approvals and tasks on previously migrated records are reconciled."),
            ("Q4", "Which identifiers will be retained?",
             ["CHANGE_IDENTIFIERS", "LINKED_REQUESTS", "REQUEST_CHANGE_LINKS"],
             "The assessment records source identifiers and observed relationship exposure.",
             "Confirm retained identifiers, changed-ID cross-references, legacy links and email-threading behavior; source IDs alone cannot prove preservation."),
            ("Q5", "What requires rebuilding, reconfiguration or additional licensing?",
             ["WORKFLOW_REBUILD", "FORM_SCRIPT_ACTIONS", "QUERY_REPORTS", "REPORT_DESCRIPTION_REQUIREMENTS", "RECURRING_MAINTENANCE", "AUTOMATION_RUNTIME", "TARGET_LICENSE", "DISCOVERY_NETWORK", "EXTERNAL_INTEGRATIONS"],
             "Observed configuration references and report/script findings identify work; unexposed settings remain unresolved.",
             "Validate SLA/lifecycle/Change workflow equivalents, external scripts and reports, discovery probes, identity permissions, license capacity and datacenter support."),
            ("Q6", "What export and recovery capabilities will be available after go-live?",
             ["BACKUP_RECOVERY", "ADMIN_AUDIT_RETENTION"],
             "Retention requirements are assessed only when supplied by the user; no target recovery claim is verified.",
             "Obtain written export/restore coverage, frequency, RPO/RTO, support and cost commitments and demonstrate an agreed recovery scenario."),
            ("Q7", "Which failures or unresolved differences prevent acceptance?",
             ["API_VISIBILITY", "DELTA_CUTOVER", "LEGACY_HISTORY", "ACCESS_MAPPING", "ATTACHMENT_SIZE"],
             "Confirmed findings, partial evidence and unresolved checks form an exception register; no overall migration-ready certificate is issued.",
             "Agree go/no-go thresholds, historical preservation, workflow/report reconciliation, permitted/denied access tests, cutover duration and ownership of every exception."),
        ]
        result = []
        for ident, title, ids, observed, confirmation in specifications:
            count = sum(lookup[key].status == CONFIRMED for key in ids)
            detail = " ".join(lookup[key].title + ": " + lookup[key].summary for key in ids)
            result.append({"id": ident, "title": title, "status": MANUAL,
                           "observed": observed + " " + detail + f" Related confirmed findings: {count}.",
                           "requires_confirmation": confirmation, "finding_ids": ids})
        return result


def analyze(snapshot: Snapshot) -> Assessment:
    """Analyze an in-memory snapshot without additional reads or writes."""
    return _Analyzer(snapshot).run()
