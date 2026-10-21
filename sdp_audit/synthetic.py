"""Deterministic synthetic on-premises API for offline demonstration and tests.

The real ReadOnlyClient, global scheduler, topology discovery and environment
collector run against an injected in-memory opener. No socket is opened. The
example token is a public synthetic marker, never a working integration key.
The original demo.py snapshot stays unchanged as the v1 regression baseline.
"""

from __future__ import annotations

import copy
from dataclasses import asdict
import email.message
import io
import json
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, urlsplit

from .catalog import ALLOWED_PATTERNS, GLOBAL_RESOURCES, RESOURCES
from .collect import CollectionOptions
from .demo import demo_snapshot
from .environment import EnvironmentCollector, EnvironmentOptions
from .models import EnvironmentSnapshot, ResourceSpec
from .transport import ReadOnlyClient


SYNTHETIC_KEY = "synthetic-only-not-a-real-integration-key-82c641"
SYNTHETIC_HOST = "https://synthetic.example.invalid"
PRIVATE_SUBJECT = "CANARY_PRIVATE_TICKET_SUBJECT_828138"
PRIVATE_DESCRIPTION = "CANARY_PRIVATE_TICKET_DESCRIPTION_828138"
PRIVATE_NOTE = "CANARY_PRIVATE_NOTE_BODY_828138"
PRIVATE_EMAIL = "canary-private-email-828138@example.invalid"
PRIVATE_FILENAME = "CANARY_PRIVATE_ATTACHMENT_828138.txt"
PRIVATE_QUERY = "CANARY_PRIVATE_QUERY_SQL_828138"
PRIVATE_SCRIPT = "CANARY_PRIVATE_SCRIPT_BODY_828138"
PRIVATE_DEFAULT = "CANARY_PRIVATE_FIELD_DEFAULT_828138"
PRIVATE_OPTION = "CANARY_PRIVATE_FIELD_OPTION_828138"
PRIVATE_ERROR = "CANARY_PRIVATE_ERROR_DETAIL_828138"
SYNTHETIC_SENSITIVE_MARKERS = (
    SYNTHETIC_KEY, PRIVATE_SUBJECT, PRIVATE_DESCRIPTION, PRIVATE_NOTE,
    PRIVATE_EMAIL, PRIVATE_FILENAME, PRIVATE_QUERY, PRIVATE_SCRIPT,
    PRIVATE_DEFAULT, PRIVATE_OPTION, PRIVATE_ERROR,
)


_SCENARIOS: dict[str, dict[str, Any]] = {
    "multi_key": {"topology": "multi", "multi_key": True,
        "portal_credentials": {str(i): "synthetic-portal-key-" + str(i) for i in range(1, 5)},
        "global_credential": "synthetic-org-key", "global_context": "1",
        "description": "Explicit per-instance keys and a separately assigned global key; one shared transport."},
    "single": {"topology": "single", "description": "One visible portal with real GET collection and field metadata."},
    "multi": {"topology": "multi", "description": "IT, HR, Facilities and inaccessible Security; mixed permissions, module limits and metadata strategies."},
    "recovery": {"topology": "multi", "errors": {"global:/portals": {
        "http_status": 403, "api_code": 4002, "message": "User does not have this permission"}},
        "verified_portal_ids": ["1", "2", "3", "4"],
        "description": "Denied directory recovered by an explicitly supplied synthetic full list in the same collector; never a guessed list."},
    "mixed_permissions": {"topology": "multi", "description": "HR Projects denied; Security portal inaccessible; other portal reads continue."},
    "module_unavailable": {"topology": "single", "errors": {
        "1:/releases": {"http_status": 400, "api_code": 7001, "message": "Not allowed as per current license"},
    }},
    "module_not_enabled": {"topology": "single", "errors": {
        "1:/problems": {"http_status": 403, "api_code": 4002, "message": "The Problems module is not enabled"},
    }},
    "unsupported_metadata": {"topology": "single", "asset_catalog": "empty", "errors": {
        "1:/requests/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
        "1:/changes/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
        "1:/changes/401/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
        "1:/asset_assets/_metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
        "1:/assets/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
    }},
    "udf_primary": {"topology": "single", "description": "Observed Request-template and current Asset type metadata; module-selected Space UDF reads supported by the fixture."},
    "udf_fallback": {"topology": "single", "asset_catalog": "empty", "errors": {
        "1:/asset_assets/_metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
        "1:/changes/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
    }},
    "budget_exhaustion": {"topology": "multi", "modules": ["requests", "projects", "assets"],
                          "settings": {"max_requests": 8, "page_size": 2}},
    "time_budget": {"topology": "multi", "settings": {"max_runtime_seconds": 6, "page_size": 2}},
    "rate_limiting": {"topology": "single", "scripted": {"global:/portals": [
        {"http_status": 429, "api_code": 4015, "message": "API Rate Limit reached", "headers": {"Retry-After": "7"}},
    ]}},
    "large_pagination": {"topology": "multi", "record_counts": {
        "1": {"requests": 1207}, "2": {"requests": 613},
    }, "settings": {"page_size": 100, "max_records": 0, "detail_limit": 2}},
    "portal_discovery_unavailable": {"topology": "multi", "errors": {
        "global:/portals": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
    }},
    "portal_context_required": {"topology": "single", "errors": {
        "1:/projects": {"http_status": 400, "api_code": 4012, "message": "Portal ID is required", "field": "PORTALID"},
    }},
    "asset_catalog_gap": {"topology": "single", "asset_catalog": "gap"},
    "empty_directory": {"topology": "empty"},
    "interrupted": {"topology": "multi", "interrupt_at_attempt": 8},
}


def fixture_config(scenario: str) -> dict[str, Any]:
    """Return a JSON-serializable fixture specification without private rows."""
    if scenario not in _SCENARIOS:
        raise ValueError("Unknown synthetic scenario.")
    return {"scenario": scenario, **copy.deepcopy(_SCENARIOS[scenario])}


def _configuration(scenario: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(scenario, str):
        return fixture_config(scenario)
    if not isinstance(scenario, Mapping):
        raise ValueError("A synthetic scenario must be a known name or fixture mapping.")
    name = scenario.get("scenario", "multi")
    result = fixture_config(name)
    for key, value in scenario.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), dict):
            result[key].update(copy.deepcopy(value))
        else:
            result[key] = copy.deepcopy(value)
    return result


class SyntheticClock:
    """A virtual monotonic clock: pacing occurs without real waiting."""

    def __init__(self, start: float = 0.0):
        self.now = float(start)
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("Synthetic time cannot move backwards.")
        self.sleeps.append(float(seconds))
        self.now += float(seconds)


class SyntheticResponse(io.BytesIO):
    def __init__(self, payload: Any, http_status: int = 200, headers: Mapping[str, str] | None = None):
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        super().__init__(body)
        self.status = http_status
        self.headers = email.message.Message()
        self.headers["Content-Type"] = "application/json"
        self.headers["Content-Length"] = str(len(body))
        for key, value in (headers or {}).items():
            self.headers[key] = str(value)

    def getcode(self) -> int:
        return self.status


def _success(**payload: Any) -> dict[str, Any]:
    return {"response_status": [{"status_code": 2000, "status": "success"}], **payload}


def _error(spec: Mapping[str, Any]) -> SyntheticResponse:
    code = int(spec.get("api_code", 4007))
    message = str(spec.get("message", "Invalid URL"))
    detail = {"status_code": code, "message": message}
    if spec.get("field"):
        detail["field"] = spec["field"]
    # A second unrecognized message verifies that only sanitized status
    # evidence is retained, without losing the real HTTP/SDP classification.
    payload = {"response_status": [{"status": "failed", "status_code": code,
               "messages": [detail, {"status_code": code, "message": PRIVATE_ERROR}]}]}
    return SyntheticResponse(payload, int(spec.get("http_status", 404)), spec.get("headers"))


def _metadata(name: str, label: str, *, portal: str, maximum: int = 250,
              container: str = "udf_fields", mandatory: bool | None = None) -> dict[str, Any]:
    definition: dict[str, Any] = {
        "id": "71", "display_name": label, "type": "string", "display_type": "single_line",
        "constraints": {"max_length": maximum}, "read_only": False, "is_custom": True,
        "default_value": PRIVATE_DEFAULT + "x" * 280, "description": PRIVATE_DESCRIPTION,
        "script": PRIVATE_SCRIPT, "href": "https://must-not-follow.invalid/" + PRIVATE_FILENAME,
    }
    if mandatory is not None:
        definition["mandatory"] = mandatory
    fields = {name: definition,
              "udf_choice": {"id": "72", "display_name": "Fulfillment class", "type": "string",
                             "display_type": "pick_list", "is_custom": True,
                             "allowed_values": ["Standard", "#", PRIVATE_OPTION]}}
    return _success(metainfo={"fields": {
        "id": {"type": "long", "read_only": True, "is_custom": False},
        container: {"type": "udf", "fields": fields},
    }})


class SyntheticServer:
    """In-memory urllib opener with portal isolation and scripted outcomes.

    ``calls`` deliberately excludes all header values except PORTALID. Raw
    request/response objects and API keys are never retained in this audit log.
    Tests can edit ``datasets[portal_id][collection]`` or use queue_response.
    """

    def __init__(self, scenario: str | Mapping[str, Any] = "multi", *, clock: SyntheticClock | None = None):
        self.config = _configuration(scenario)
        self.scenario = self.config["scenario"]
        self.clock = clock or SyntheticClock()
        self.calls: list[dict[str, Any]] = []
        self.scripted = copy.deepcopy(self.config.get("scripted", {}))
        multi = self.config.get("topology", "multi") == "multi"
        self.portals = [
            {"id": "1", "name": "IT Helpdesk", "type": {"internal_name": "IT"},
             "status": {"internal_name": "Production"}, "license_details": {"edition": "Enterprise"}},
        ]
        if multi:
            self.portals.extend([
                {"id": "2", "name": "HR", "type": {"internal_name": "HR"},
                 "status": {"internal_name": "Production"}, "license_details": {"edition": "Professional"}},
                {"id": "3", "name": "Facilities", "type": {"internal_name": "Facilities"},
                 "status": {"internal_name": "Pre-Production"}, "license_details": {"edition": "Standard"}},
                {"id": "4", "name": "Security", "type": {"internal_name": "Blank"},
                 "status": {"internal_name": "Production"}, "license_details": {"edition": "Enterprise"}},
            ])
        if self.config.get("topology") == "empty":
            self.portals = []
        if "portals" in self.config:
            self.portals = copy.deepcopy(self.config["portals"])
        for portal in self.portals:
            portal.update(description=PRIVATE_DESCRIPTION, owners=[{"name": PRIVATE_EMAIL}], image_token=SYNTHETIC_KEY)
        self.inaccessible_portals = set(self.config.get("inaccessible_portals", ["4"] if multi else []))
        self.errors: dict[str, Any] = {}
        if multi:
            self.errors.update({
                "2:/projects": {"http_status": 403, "api_code": 4002, "message": "Forbidden"},
                "3:/releases": {"http_status": 400, "api_code": 7001, "message": "Not allowed as per current license"},
                "2:/asset_assets/_metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
                "3:/requests/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
                "3:/changes/metainfo": {"http_status": 404, "api_code": 4007, "message": "Invalid URL"},
            })
        self.errors.update(copy.deepcopy(self.config.get("errors", {})))
        baseline = demo_snapshot()
        self.datasets: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for portal in self.portals:
            pid = str(portal["id"])
            records = {key: copy.deepcopy(dataset.records) for key, dataset in baseline.datasets.items()
                       if key != "field_definitions"}
            # Portal-local IDs intentionally repeat between portals.
            records["requests"] = records["requests"][:3 if pid == "1" else 2 if pid == "2" else 1]
            for row in records["requests"]:
                row.update(subject=PRIVATE_SUBJECT, description=PRIVATE_DESCRIPTION + SYNTHETIC_KEY,
                           requester={"id": "301", "email_id": PRIVATE_EMAIL})
                for attachment in row.get("attachments", []):
                    attachment["name"] = PRIVATE_FILENAME
            records["technicians"][0]["email_id"] = PRIVATE_EMAIL
            records["technicians"][1]["email_id"] = PRIVATE_EMAIL.upper()
            records["users"][0]["email_id"] = PRIVATE_EMAIL
            records["users"][0]["user_udf_fields"] = {"udf_identity_note": PRIVATE_DEFAULT}
            for row in records["request_notes"]:
                row["description"] = PRIVATE_NOTE
                for attachment in row.get("attachments", []):
                    attachment["name"] = PRIVATE_FILENAME
            records["reports"][0].update(report_name=PRIVATE_QUERY, query="SELECT " + PRIVATE_QUERY,
                                         script=PRIVATE_SCRIPT)
            for row in records["incident_templates"] + records["service_templates"]:
                row["script"] = PRIVATE_SCRIPT
                row["description"] = PRIVATE_DESCRIPTION
            records["projects"] = [] if not multi else [
                {"id": "701", "created_time": {"value": "1704844800000"}, "description": PRIVATE_DESCRIPTION,
                 "udf_fields": {"udf_project_code": PRIVATE_DEFAULT}},
            ]
            if pid == "1" and multi:
                records["projects"].append({"id": "702", "description": PRIVATE_DESCRIPTION})
            for row in records["problems"]:
                row["udf_fields"] = {"udf_problem_ref": PRIVATE_DEFAULT}
            for row in records["releases"]:
                row["udf_fields"] = {"udf_release_ref": PRIVATE_DEFAULT}
            for key in ("assets", "computers"):
                if pid == "3":
                    records[key] = records[key][:1]
                for row in records[key]:
                    row["product_type"] = {"id": "88", "name": "Workstation"}
                    row["udf_fields"] = {"udf_asset_ref": PRIVATE_DEFAULT}
            for row in records["cis"]:
                row["udf_fields"] = {"udf_ci_owner": PRIVATE_DEFAULT}
            if pid == "1":
                records["ci_types"][0]["api_plural_name"] = "cmdb_demo"
            records["asset_modules"] = [
                {"id": "88", "name": "Assets", "api_plural_name": "asset_assets"},
                {"id": "89", "name": "Servers", "api_plural_name": "asset_servers"},
                {"id": "90", "name": "Custom asset type", "api_plural_name": "custom_asset_demo"},
            ]
            if pid == "2" or self.config.get("asset_catalog") == "empty":
                records["asset_modules"] = []
            elif self.config.get("asset_catalog") == "gap":
                records["asset_modules"].append({"id": "91", "name": "Unresolved type", "api_plural_name": "https://must-not-follow.invalid"})
            for key, count in self.config.get("record_counts", {}).get(pid, {}).items():
                source_rows = records.get(key, [])
                if not isinstance(count, int) or count < 0:
                    raise ValueError("Synthetic record counts must be nonnegative integers.")
                seed = source_rows[-1] if source_rows else {"id": "1"}
                records[key] = source_rows[:count]
                initial = max((int(row["id"]) for row in source_rows), default=0)
                while len(records[key]) < count:
                    row = copy.deepcopy(seed)
                    row["id"] = str(initial + len(records[key]) - len(source_rows) + 1)
                    records[key].append(row)
            self.datasets[pid] = records
        self.orgusers = [
            {"id": "301", "email_id": PRIVATE_EMAIL, "name": PRIVATE_DESCRIPTION},
            {"id": "302", "email_id": PRIVATE_EMAIL.upper(), "name": PRIVATE_DESCRIPTION},
        ]
        self._routes = {spec.path: spec for spec in RESOURCES + GLOBAL_RESOURCES}

    def queue_response(self, portal_id: str | None, path: str, payload: Any = None, *,
                       http_status: int = 200, headers: Mapping[str, str] | None = None,
                       api_code: int | None = None, message: str | None = None) -> None:
        key = (portal_id if portal_id is not None else "global") + ":" + path
        item: dict[str, Any] = {"http_status": http_status, "headers": dict(headers or {})}
        if api_code is not None:
            item.update(api_code=api_code, message=message or "Invalid URL")
        else:
            item["payload"] = copy.deepcopy(payload)
        self.scripted.setdefault(key, []).append(item)

    @staticmethod
    def _page(wrapper: str, rows: list[dict[str, Any]], data: Mapping[str, Any]) -> SyntheticResponse:
        info = data.get("list_info", {})
        if not isinstance(info, Mapping):
            return _error({"http_status": 400, "api_code": 4021, "message": "Data type mismatch"})
        try:
            start = int(info.get("start_index", 1))
            count = int(info.get("row_count", 100))
        except (TypeError, ValueError):
            return _error({"http_status": 400, "api_code": 4021, "message": "Data type mismatch"})
        if start < 1 or count < 1:
            return _error({"http_status": 400, "api_code": 4021, "message": "Data type mismatch"})
        selected = copy.deepcopy(rows[start - 1:start - 1 + count])
        return SyntheticResponse(_success(**{wrapper: selected}, list_info={
            "start_index": start, "row_count": len(selected), "total_count": len(rows),
            "has_more_rows": start - 1 + len(selected) < len(rows),
        }))

    def _definition_response(self, portal: str, path: str, data: Mapping[str, Any]) -> SyntheticResponse | None:
        if path == "/requests/metainfo":
            selector = data.get("template", {})
            tid = str(selector.get("id", "")) if isinstance(selector, Mapping) else ""
            observed = {row["id"] for key in ("incident_templates", "service_templates")
                        for row in self.datasets[portal][key]}
            if tid not in observed:
                return _error({"http_status": 400, "api_code": 4012, "message": "Invalid input"})
            response = _metadata("udf_char1", "Business reference" if portal == "1" else "Personnel reference",
                                 portal=portal, maximum=400 if tid == "11" else 250, mandatory=tid == "11")
            response["metainfo"]["fields"]["udf_fields"]["fields"]["udf_case"] = {
                "id": "73", "display_name": "business reference" if portal == "1" else "Additional reference",
                "type": "string", "display_type": "single_line", "is_custom": True,
                "constraints": {"max_length": 250},
            }
            return SyntheticResponse(response)
        if path == "/changes/metainfo" or (path.startswith("/changes/") and path.endswith("/metainfo")):
            if path != "/changes/metainfo":
                identifier = path.split("/")[2]
                if not any(row["id"] == identifier for row in self.datasets[portal]["changes"]):
                    return _error({"http_status": 404, "api_code": 4007, "message": "Resource not found"})
            return SyntheticResponse(_metadata("udf_change_ref", "Change reference", portal=portal))
        if path in {"/assets/metainfo", "/workstations/metainfo"}:
            selector = data.get("template", {})
            tid = str(selector.get("id", "")) if isinstance(selector, Mapping) else ""
            if tid != "88":
                return _error({"http_status": 400, "api_code": 4012, "message": "Invalid input"})
            holder = "workstation_udf_fields" if path.startswith("/workstations") else "udf_fields"
            return SyntheticResponse(_metadata("udf_asset_ref", "Legacy asset reference", portal=portal, container=holder))
        if path.endswith("/_metainfo"):
            api = path.split("/")[1]
            known = {"asset_assets", "asset_computers", "asset_servers", "asset_printers", "departments"}
            known.update(row.get("api_plural_name") for row in self.datasets[portal]["asset_modules"])
            if api not in known:
                return None
            return SyntheticResponse(_metadata("udf_asset_ref", "Asset reference", portal=portal))
        if path.endswith("/_metadata"):
            api = path.split("/")[1]
            known = {row.get("api_plural_name") for row in self.datasets[portal]["ci_types"]}
            if api not in known:
                return None
            meta = _metadata("udf_ci_owner", "Application owner", portal=portal)["metainfo"]
            meta["plural_name"] = api
            return SyntheticResponse(_success(metadata={
                "metainfo": meta,
                "layout": {"description": PRIVATE_DESCRIPTION, "script": PRIVATE_SCRIPT},
            }))
        if path == "/udf_fields":
            module = data.get("module", {})
            name = module.get("name") if isinstance(module, Mapping) else None
            if name not in {"space_campus", "space_structure", "space_floor", "space_room"}:
                return _error({"http_status": 400, "api_code": 4012, "message": "Invalid input"})
            rows = [{"id": "81", "name": "udf_space_ref", "display_name": "Space reference",
                     "type": "string", "display_type": "single_line", "is_custom": True,
                     "constraints": {"max_length": 250}, "module": {"name": name},
                     "portal": {"id": portal}, "default_value": PRIVATE_DEFAULT, "script": PRIVATE_SCRIPT}]
            return self._page("udf_fields", rows, data)
        return None

    def open(self, request: Any, timeout: float) -> SyntheticResponse:
        parsed = urlsplit(request.full_url)
        if parsed.scheme != "https" or parsed.netloc != "synthetic.example.invalid" or not parsed.path.startswith("/api/v3/"):
            raise AssertionError("Synthetic opener received an unexpected origin or API prefix.")
        path = parsed.path[len("/api/v3"):]
        portal = request.get_header("Portalid")
        parameters = parse_qs(parsed.query)
        try:
            data = json.loads(parameters.get("input_data", ["{}"])[0])
        except (ValueError, TypeError):
            data = None
        method = request.get_method()
        self.calls.append({"method": method, "path": path, "portal_id": portal,
                           "input_data": copy.deepcopy(data), "time": self.clock(),
                           "has_authtoken": bool(request.get_header("Authtoken")),
                           "has_body": request.data is not None})
        if self.config.get("interrupt_at_attempt") == len(self.calls):
            raise KeyboardInterrupt()
        if method != "GET" or request.data is not None:
            raise AssertionError("Synthetic assessment attempted a non-GET or a request body.")
        if self.config.get("multi_key"):
            expected = (SYNTHETIC_KEY if path == "/portals" else
                        self.config.get("global_credential") if path == "/orgusers" else
                        self.config.get("portal_credentials", {}).get(portal))
            if not expected or request.get_header("Authtoken") != expected:
                return _error({"http_status": 401, "api_code": 4001, "message": "Invalid API key"})
        if not isinstance(data, Mapping):
            return _error({"http_status": 400, "api_code": 4021, "message": "Data type mismatch"})
        key = (portal if portal is not None else "global") + ":" + path
        scripted = self.scripted.get(key, [])
        if scripted:
            outcome = scripted.pop(0)
            if "payload" in outcome:
                return SyntheticResponse(outcome["payload"], outcome.get("http_status", 200), outcome.get("headers"))
            return _error(outcome)
        if key in self.errors:
            return _error(self.errors[key])
        if path == "/portals":
            if portal is not None:
                raise AssertionError("Portal discovery inherited a default portal context.")
            return self._page("portals", self.portals, data)
        if portal is None:
            return _error({"http_status": 400, "api_code": 4012, "message": "Portal ID is required", "field": "PORTALID"})
        if portal not in self.datasets or portal in self.inaccessible_portals:
            return _error({"http_status": 403, "api_code": 4002, "message": "Access to the specified portal is denied"})
        if path == "/orgusers":
            return self._page("orgusers", self.orgusers, data)
        metadata = self._definition_response(portal, path, data)
        if metadata is not None:
            return metadata
        records = self.datasets[portal]
        if path == "/request_templates":
            info = data.get("list_info", {})
            search = info.get("search_fields", {}) if isinstance(info, Mapping) else {}
            service = search.get("is_service_template")
            rows = records["service_templates"] if service is True or service == "true" else records["incident_templates"]
            return self._page("request_templates", rows, data)
        spec = self._routes.get(path)
        if spec:
            return self._page(spec.plural, records.get(spec.key, []), data)
        if path in {"/assets", "/workstations"}:
            wrapper, name = ("assets", "assets") if path == "/assets" else ("workstations", "computers")
            return self._page(wrapper, records[name], data)
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[0] in {"requests", "changes", "projects", "releases", "asset_assets"}:
            parent_id, child = parts[1], parts[2]
            rows = []
            if parts[0] == "requests" and child in {"notes", "tasks"}:
                rows = [row for row in records["request_" + child] if row.get("_parent_id") == parent_id]
            if child in {"notes", "tasks", "worklogs", "attachments"}:
                if len(parts) == 3:
                    return self._page(child, rows, data)
                row = next((row for row in rows if row.get("id") == parts[3]), None)
                if row is not None:
                    return SyntheticResponse(_success(**{child.rstrip("s"): copy.deepcopy(row)}))
        if len(parts) == 2:
            base, identifier = "/" + parts[0], parts[1]
            if base == "/request_templates":
                rows = records["incident_templates"] + records["service_templates"]
                singular = "request_template"
            elif base in self._routes:
                spec = self._routes[base]
                rows, singular = records.get(spec.key, []), spec.singular
            else:
                rows, singular = [], "record"
            row = next((row for row in rows if str(row.get("id")) == identifier), None)
            if row is not None:
                return SyntheticResponse(_success(**{singular: copy.deepcopy(row)}))
        return _error({"http_status": 404, "api_code": 4007, "message": "Invalid URL"})


def create_synthetic_client(
    scenario: str | Mapping[str, Any] = "multi", *, max_requests: int = 500,
    max_runtime: float = 1200, rpm: float = 30, api_key: str = SYNTHETIC_KEY,
    progress: Callable[[dict[str, Any]], None] | None = None,
    multi_key: bool = False,
) -> tuple[ReadOnlyClient, SyntheticServer, SyntheticClock]:
    clock = SyntheticClock()
    server = SyntheticServer(scenario, clock=clock)
    client = ReadOnlyClient(SYNTHETIC_HOST, api_key, ALLOWED_PATTERNS,
                            rpm=rpm, max_requests=max_requests, max_runtime=max_runtime,
                            progress=progress, clock=clock, sleep=clock.sleep, multi_key=multi_key)
    client._opener = server
    return client, server, clock


def run_synthetic(
    scenario: str | Mapping[str, Any] = "multi", *, resources: list[ResourceSpec] | None = None,
    collection_options: CollectionOptions | None = None,
    environment_options: EnvironmentOptions | None = None,
    max_requests: int | None = None, max_runtime: float | None = None,
    portal_ids: list[str] | None = None,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[EnvironmentSnapshot, SyntheticServer]:
    config = _configuration(scenario)
    settings: dict[str, Any] = {
        "demo": True, "rpm": 30, "page_size": 2, "max_records": 5000,
        "detail_limit": 2, "metadata_limit": 20, "max_portals": 100,
        "max_requests": 500, "max_runtime_seconds": 1200, "timeout": 30,
        "subresource_parents": 1, "max_child_records": 2,
        "read_only_get_only": True, "attachment_downloads": False,
        "tls_verification": True, "allow_http": False, "credential_visibility_verified": False,
    }
    settings.update(config.get("settings", {}))
    if max_requests is not None:
        settings["max_requests"] = max_requests
    if max_runtime is not None:
        settings["max_runtime_seconds"] = max_runtime
    if collection_options is None:
        collection_options = CollectionOptions(**{key: settings[key] for key in (
            "page_size", "max_records", "detail_limit", "subresource_parents", "max_child_records",
        )})
    else:
        settings.update(asdict(collection_options))
    if environment_options is None:
        environment_options = EnvironmentOptions(max_portals=settings["max_portals"],
                                                 metadata_limit=settings["metadata_limit"])
    else:
        settings.update(asdict(environment_options))
    if resources is None and "modules" in config:
        requested = set(config["modules"])
        resources = [spec for spec in RESOURCES if spec.key in requested]
        if {spec.key for spec in resources} != requested:
            raise ValueError("Synthetic fixture selected an unknown resource.")
    selected = list(RESOURCES if resources is None else resources)
    settings["collections_selected"] = [spec.key for spec in selected]
    settings["max_minutes"] = settings["max_runtime_seconds"] / 60
    client, server, _ = create_synthetic_client(
        config, max_requests=settings["max_requests"], max_runtime=settings["max_runtime_seconds"],
        rpm=settings["rpm"], progress=progress, multi_key=bool(config.get("multi_key")),
    )
    if config.get("multi_key"):
        for pid, key in config.get("portal_credentials", {}).items():
            client.bind_portal_credential(SYNTHETIC_HOST, pid, key)
        if config.get("global_credential"):
            client.bind_global_credential(SYNTHETIC_HOST, config["global_context"], config["global_credential"])
    answers = copy.deepcopy(demo_snapshot().manual_answers)
    answers.update(source_build=15100)
    answers.update(config.get("manual_answers", {}))
    env = EnvironmentSnapshot(
        generated_at="2026-10-07T12:00:00+00:00",
        source={"host": SYNTHETIC_HOST, "product": "ServiceDesk Plus On-Premises", "demo": True,
                "build_origin": "user_supplied", "synthetic_scenario": config["scenario"]},
        settings=settings, manual_answers=answers,
    )
    resolver = None
    if config.get("verified_portal_ids"):
        from .portal_scope import PortalScopeResolver, ScopeOptions
        resolver = PortalScopeResolver(client, ScopeOptions(seed_ids=config["verified_portal_ids"],
                                       non_interactive=True, no_portal_cache=True),
                                       page_size=settings["page_size"], progress=progress)
    EnvironmentCollector(client, selected, collection_options, environment_options, progress,
                         scope_resolver=resolver).collect(env, portal_ids)
    env.stats.update(network_used=False, synthetic_transport=True)
    return env, server


def demo_environment(scenario: str = "multi") -> EnvironmentSnapshot:
    """Build a fresh single/multi demonstration through actual collection code."""
    if scenario not in {"single", "multi"}:
        raise ValueError("Demonstration scenario must be single or multi.")
    return run_synthetic(scenario)[0]
