"""Small, secret-free diagnostics usable even when HTML publication fails.

Only fixed classifications, recognized SDP messages, validated identifiers and
numeric protocol evidence are emitted. Raw headers, URLs with parameters,
response bodies, exception strings and credential material are never emitted.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

from . import __version__
from .catalog import ALLOWED_PATTERNS, GLOBAL_RESOURCES, RESOURCES
from .models import EnvironmentSnapshot
from .transport import _status_message_evidence, _DYNAMIC_METADATA_PATH, _CI_METADATA_PATH
from .response_contract import PARSE_REASONS, safe_shape
from .topology import topology_scope_evidence

_MESSAGES = {
    "CREDENTIAL_MISSING": "No credential was assigned to this operation's scope; no read was sent.",
    "SUCCESS": "Read succeeded.", "EMPTY": "The API returned a successful empty list for this key.",
    "COMPLETE": "The API-visible directory traversal completed.", "COLLECTING": "Discovery is in progress.",
    "NOT_STARTED": "No read was started.", "INCOMPLETE": "Directory coverage could not be established completely.",
    "PERMISSION_DENIED": "This read operation was denied; the response does not identify a required role.",
    "AUTHENTICATION_FAILED": "Authentication was rejected; check the credential and account or upstream access control.",
    "PORTAL_CONTEXT_REQUIRED": "The API explicitly requires portal context for this operation.",
    "PORTAL_NOT_ACCESSIBLE": "The specified portal is inaccessible or unavailable to this operation.",
    "MODULE_NOT_ENABLED": "The API explicitly reports that the module is not enabled.",
    "MODULE_NOT_AVAILABLE": "The operation is unavailable under the current module or license configuration.",
    "ENDPOINT_UNSUPPORTED": "The requested API path was not found or is not supported; this is not proof of an empty environment.",
    "API_VERSION_INCOMPATIBLE": "The API reports an unsupported build or API version.",
    "INVALID_QUERY": "The API rejected the read query or its input.",
    "RATE_LIMITED": "The server's rate limit prevented completion; shared pacing and retry budgets apply.",
    "TIME_BUDGET_REACHED": "The global time budget was reached.",
    "REQUEST_BUDGET_REACHED": "The global HTTP attempt budget was reached.",
    "RECORD_LIMIT_REACHED": "The scanner's record limit was reached.",
    "NETWORK_ERROR": "The connection or HTTP exchange did not complete successfully.",
    "SERVER_ERROR": "The server could not complete this read.",
    "PARSE_ERROR": "The response did not satisfy the documented JSON or pagination contract.",
    "UNKNOWN_API_ERROR": "The unsuccessful API response could not be classified more precisely.",
    "INTERRUPTED": "The user interrupted discovery; partial evidence was retained.",
}
_FORMATS = {"not_received", "not_inspected", "json_object", "json_array", "json_scalar",
            "html", "xml", "empty", "non_json_or_malformed_json"}
_CONTENT_TYPES = {"not_supplied", "other", "application/json", "application/vnd.manageengine.sdp.v3+json",
                  "text/html", "text/plain", "application/xml", "text/xml", "application/octet-stream"}
_TRANSPORT = {"TLS_CERTIFICATE_VERIFICATION_FAILED", "TLS_NEGOTIATION_FAILED", "DNS_LOOKUP_FAILED",
              "CONNECTION_TIMED_OUT", "CONNECTION_REFUSED", "CONNECTION_RESET", "CONNECTION_FAILED",
              "REDIRECT_BLOCKED"}
_CAUSES = {"unknown", "authentication", "authorization", "configuration", "portal_access",
           "credential_configuration",
           "module_availability", "licensing_or_module_availability", "api_compatibility",
           "api_compatibility_or_resource_availability", "api_compatibility_or_scanner", "rate_limit",
           "network", "tls_configuration", "server", "scanner_budget", "scanner_limit",
           "pagination_integrity", "user_interruption"}
_KINDS = {"authentication", "forbidden", "portal_context", "portal_access", "module_disabled",
          "credential_missing",
          "license", "unsupported", "version", "throttled", "network", "tls", "server", "invalid_response"}
_LOGICAL = re.compile(r"[a-z][a-z0-9_.:-]{0,127}", re.ASCII)
_KNOWN_LOGICAL = frozenset({spec.key for spec in RESOURCES + GLOBAL_RESOURCES}
                         | {spec.module for spec in RESOURCES + GLOBAL_RESOURCES if spec.module}
                         | {"topology", "portals", "requests", "request_notes", "request_tasks", "request_subresources"})


def _known_logical(value: Any) -> bool:
    if not isinstance(value, str) or not _LOGICAL.fullmatch(value):
        return False
    if value in _KNOWN_LOGICAL or value.startswith("fields.") and value[7:] in _KNOWN_LOGICAL:
        return True
    return re.fullmatch(r"request_(?:notes|tasks):[0-9]+", value, re.ASCII) is not None


def safe_diagnostic(item: Mapping[str, Any]) -> dict[str, Any]:
    classification = item.get("classification")
    classification = classification if isinstance(classification, str) and classification in _MESSAGES else "UNKNOWN_API_ERROR"
    number = item.get("http_status")
    number = number if isinstance(number, int) and not isinstance(number, bool) and 100 <= number <= 599 else None
    values = item.get("api_codes", [])
    codes = [value for value in values if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < 10**12] if isinstance(values, (list, tuple)) else []
    path = item.get("endpoint")
    # Dynamic schema-only paths are already authorized by the transport from
    # authenticated metadata. This output validation does not widen GET access.
    path = path if isinstance(path, str) and (any(re.fullmatch(pattern, path, re.ASCII) for pattern in ALLOWED_PATTERNS)
                    or _DYNAMIC_METADATA_PATH.fullmatch(path) or _CI_METADATA_PATH.fullmatch(path)) else None
    portal = item.get("portal_id")
    portal = str(portal) if isinstance(portal, (int, str)) and not isinstance(portal, bool) else None
    portal = portal if portal and re.fullmatch(r"[0-9]{1,128}", portal, re.ASCII) else None
    cause = item.get("cause")
    cause = cause if isinstance(cause, str) and cause in _CAUSES else "unknown"
    kind = item.get("kind")
    kind = kind if isinstance(kind, str) and kind in _KINDS else None
    response_format = item.get("response_format")
    response_format = response_format if isinstance(response_format, str) and response_format in _FORMATS else None
    content_type = item.get("content_type")
    content_type = content_type if isinstance(content_type, str) and content_type in _CONTENT_TYPES else None
    detail = item.get("transport_detail")
    detail = detail if isinstance(detail, str) and detail in _TRANSPORT else None
    # The main transport has already recognized these phrases. Recognize again
    # at this output boundary instead of trusting a caller-supplied 'sanitized'
    # flag or arbitrary message text from a mocked/library invocation.
    api_message = item.get("api_message")
    recognized = []
    omitted = bool(item.get("raw_message_omitted"))
    if isinstance(api_message, str) and len(api_message) <= 2048:
        for part in api_message.split("; ")[:6]:
            message, raw_omitted, _ = _status_message_evidence({"response_status": {"message": part}})
            if message and message not in recognized:
                recognized.append(message)
            omitted = omitted or raw_omitted or message is None
    elif api_message:
        omitted = True
    message = _MESSAGES[classification]
    if kind == "tls" or cause == "tls_configuration":
        message = "TLS certificate verification or negotiation failed; no authenticated SDP response was established."
    if response_format == "html" and classification == "PARSE_ERROR":
        message = "Expected a JSON API object but received HTML; no response body was saved."
    result = {
        "credential_scope": (item["credential_scope"] if isinstance(item.get("credential_scope"), str) and item.get("credential_scope") in
                             {"directory_key", "portal_key", "global_key"} else "integration_key"),
        "classification": classification, "http_status": number, "api_codes": codes,
        "kind": kind, "cause": cause, "portal_id": portal, "endpoint": path,
        "message": message, "api_message": "; ".join(recognized) or None,
        "message_sanitized": True, "raw_message_omitted": omitted,
        "response_format": response_format, "content_type": content_type,
        "has_sdp_status": item.get("has_sdp_status") is True,
        "transport_detail": detail, "retryable": item.get("retryable") is True,
    }
    for name in ("endpoint_name", "module"):
        value = item.get(name)
        # Runtime logical names are fixed collector identifiers; do not retain
        # a value that was not sanitized by the client context boundary.
        result[name] = value if item.get("message_sanitized") is True and _known_logical(value) else None
    reason = item.get("parse_reason")
    if isinstance(reason, str) and reason in PARSE_REASONS:
        result["parse_reason"] = reason
    shape = safe_shape(item.get("response_shape"))
    if shape is not None:
        result["response_shape"] = shape
    if item.get("compatibility_retry") == "minimal_pagination_same_endpoint":
        result["compatibility_retry"] = "minimal_pagination_same_endpoint"
    return result


def guidance(item: Mapping[str, Any], *, authentication: str | None = None) -> str:
    data = safe_diagnostic(item)
    classification = data["classification"]
    directory = data["endpoint"] == "/portals" or data["module"] == "topology"
    established = authentication in {"VALID", "valid"} and data["credential_scope"] == "integration_key"
    auth_note = (" Other successful reads established integration-key authentication; this failure does not invalidate those reads."
                 if established else " This failed operation alone does not establish authentication.")
    if data["kind"] == "tls" or data["cause"] == "tls_configuration":
        return "Check certificate hostname, validity and trust chain. Supply the trusted PEM CA bundle using --ca-file; do not disable TLS verification as a default fix." + auth_note
    if data["transport_detail"] == "REDIRECT_BLOCKED":
        return "Check the final API base path for this operation. Redirects are deliberately not followed and the Location header is not printed." + auth_note
    if classification == "AUTHENTICATION_FAILED":
        credential = {"directory_key": "directory-only credential", "portal_key": "assigned instance credential",
                      "global_key": "assigned global credential"}.get(data["credential_scope"], "integration key/account")
        return "Verify the " + credential + " and whether an upstream gateway rejected this operation. HTTP 401 alone does not identify the rejecting component."
    if classification == "PERMISSION_DENIED":
        if directory:
            return "Confirm read visibility for the portal directory. A generic 403 does not identify a required role. Continue the same run with the full verified portal list/file or a directory-only credential. Neither method changes module permissions."
        return "Confirm read permission for this specific module operation in the stated portal using the original integration key. A generic 403 does not identify a required role; directory credentials and timeout changes do not grant module access."
    if classification == "PORTAL_CONTEXT_REQUIRED":
        return "Verify the explicit PORTALID for this operation and compare any returned portal context. Do not infer a missing role from a context error; do not guess additional IDs."
    if classification == "PORTAL_NOT_ACCESSIBLE":
        return "Confirm the selected portal ID and original integration key's access to that portal. Keep this portal as a coverage gap while other authorized portals are assessed."
    if classification in {"ENDPOINT_UNSUPPORTED", "API_VERSION_INCOMPATIBLE"}:
        if directory:
            return "Confirm the source build and supported directory API contract. Use only an administrator-verified full portal list when discovery is unavailable; no default ID is guessed."
        return "Check this module's documented endpoint and response contract for the installed build. Unsupported operations are coverage gaps, not zero records or proof of missing permissions."
    if classification in {"MODULE_NOT_ENABLED", "MODULE_NOT_AVAILABLE"}:
        return "Confirm this portal's module availability and entitlement. The response does not establish an empty collection or require broader administrator roles."
    if classification == "NETWORK_ERROR":
        if data["transport_detail"] == "CONNECTION_TIMED_OUT":
            return ("This operation timed out. Try --timeout 90 and a smaller --page-size; for slow list reads, --count-policy never avoids requesting total-count calculations. Retain successful pages and inspect source/proxy timing if it persists; none of these adjustments proves the underlying cause." + auth_note)
        return "Check the recorded transport detail and network/proxy reachability for this operation; retain previously successful collection evidence." + auth_note
    if classification == "PARSE_ERROR":
        if data["response_format"] in {"html", "xml"}:
            return "This operation returned a non-JSON document. Check API routing or a sign-in/proxy response for this endpoint; share only sanitized diagnostics, not the response body." + auth_note
        if data["response_format"] == "json_object" or data.get("response_shape", {}).get("root_type") == "object":
            return "A JSON object was received but the collector contract failed. Compare parse_reason, the expected wrapper and value-free response_shape with the installed-build API contract. This is not evidence of an invalid key or an empty module; do not replace the wrapper by guessing."
        return "Inspect the endpoint-specific response-format and contract evidence. A parse error alone does not prove an invalid key, wrong base URL or empty module. Share sanitized diagnostics, not raw responses."
    if classification == "INVALID_QUERY":
        return "The read query was rejected. Review its HTTP/SDP evidence and the installed-build contract; preserve filters and portal scope when using a documented compatibility query."
    if classification in {"REQUEST_BUDGET_REACHED", "TIME_BUDGET_REACHED", "RECORD_LIMIT_REACHED", "RATE_LIMITED"}:
        return "Review the global budgets and server rate-limit response; completed scope remains complete and unqueried scope remains unknown."
    return "Review the recorded classification and HTTP/SDP evidence with the source administrator; unknown scope is not zero data or proof of Cloud readiness."


def diagnostic_lines(item: Mapping[str, Any], *, authentication: str | None = None) -> list[str]:
    data = safe_diagnostic(item)
    endpoint = "/api/v3" + data["endpoint"] if data["endpoint"] else "not established"
    status = str(data["http_status"]) if data["http_status"] is not None else "not received/available"
    codes = ", ".join(str(code) for code in data["api_codes"]) or "not supplied"
    context = (("none (directory discovery)" if data["endpoint"] == "/portals" else "not supplied/established")
               if data["portal_id"] is None else data["portal_id"])
    lines = ["GET " + endpoint + " | PORTALID: " + context,
             "Result: " + data["classification"] + " | HTTP: " + status + " | SDP codes: " + codes,
             "Response: " + (data["response_format"] or "not established") + "; cause: " + data["cause"],
             "Message: " + (data["api_message"] or data["message"])]
    if data["transport_detail"]:
        lines.append("Transport detail: " + data["transport_detail"])
    if data.get("compatibility_retry"):
        lines.append("Compatibility action: one minimal-pagination retry on the same endpoint.")
    if data.get("credential_scope") == "directory_key":
        lines.append("Credential scope: separate directory-only key; not the module integration key.")
    if data.get("parse_reason"):
        lines.append("Contract issue: " + data["parse_reason"])
    if data.get("response_shape"):
        lines.append("Response shape (types only): " + json.dumps(data["response_shape"], sort_keys=True))
    lines.append("Next step: " + guidance(data, authentication=authentication))
    return lines


def print_topology_diagnostics(env: EnvironmentSnapshot) -> None:
    if not env.topology.diagnostics and env.topology.complete:
        return
    print("\nPortal-discovery diagnostics (sanitized):", flush=True)
    if env.topology.mode == "automatic" and env.topology.complete and env.topology.diagnostics:
        print("  Directory discovery completed; retained entries below describe earlier recoverable attempts.", flush=True)
    for item in env.topology.diagnostics:
        if isinstance(item, Mapping):
            for line in diagnostic_lines(item, authentication=env.authentication):
                print("  " + line, flush=True)
    if not env.topology.diagnostics:
        print("  No complete portal-directory response was established.", flush=True)
    if env.topology.mode == "assisted" and env.portals:
        print("  The in-run verified portal scope was used for module collection; this directory diagnostic does not mean those module reads were skipped.", flush=True)
    if env.topology.credential_scope == "directory_key":
        print("  A separate directory-only credential was attempted; its role assignments are not inferred. Module operations, when requested, retain the original integration key.", flush=True)
    if not env.portals:
        print("  No portal module inventories were collected. Migration readiness is UNKNOWN, not passed.", flush=True)
    if env.authentication not in {"VALID", "valid"}:
        print("  Integration-key authentication: " + ("FAILED" if env.authentication in {"FAILED", "failed"} else "NOT ESTABLISHED") + ".", flush=True)


def _diagnostic_records(env: EnvironmentSnapshot) -> list[dict[str, Any]]:
    records = [safe_diagnostic(item) for item in env.topology.diagnostics if isinstance(item, Mapping)]
    for entry in env.retained_portals.values():
        records.extend(safe_diagnostic(item) for item in entry.get("diagnostics", [])
                       if isinstance(item, Mapping))
    for row in env.retained_global_coverage:
        records.extend(safe_diagnostic(item) for item in row.get("diagnostics", [])
                       if isinstance(item, Mapping))
    snapshots = [item.snapshot for item in env.portals.values()]
    if env.global_snapshot is not None:
        snapshots.append(env.global_snapshot)
    for snapshot in snapshots:
        for dataset in snapshot.datasets.values():
            for diagnostic in dataset.diagnostics:
                if not isinstance(diagnostic, Mapping):
                    continue
                # Enrich older/library-created diagnostics from their owning
                # collector. Existing exact child/detail paths are not replaced.
                item = dict(diagnostic)
                for key, value in (("endpoint", dataset.endpoint), ("endpoint_name", dataset.key),
                                   ("module", dataset.module or dataset.key), ("portal_id", dataset.portal_id)):
                    if item.get(key) is None:
                        item[key] = value
                # This is a known collector context, but message text is still
                # separately revalidated against canonical phrases below.
                item["message_sanitized"] = True
                records.append(safe_diagnostic(item))
        for inventory in snapshot.fields.values():
            inventory = inventory.to_dict() if hasattr(inventory, "to_dict") else inventory
            if isinstance(inventory, Mapping):
                records.extend(safe_diagnostic(item) for item in inventory.get("diagnostics", [])
                               if isinstance(item, Mapping))
    unique = []
    seen = set()
    for item in records:
        identity = json.dumps(item, sort_keys=True)
        if identity not in seen:
            unique.append(item)
            seen.add(identity)
    return unique


def diagnostics_document(env: EnvironmentSnapshot) -> str:
    records = _diagnostic_records(env)
    topology_outcome = env.topology.outcome if env.topology.outcome in _MESSAGES else "UNKNOWN_API_ERROR"
    stop = env.stop_classification
    known_stops = set(_MESSAGES) | {"PORTAL_DISCOVERY_UNAVAILABLE", "NO_VISIBLE_PORTALS", "DIAGNOSTIC_ONLY"}
    stop = stop if isinstance(stop, str) and stop in known_stops else None
    authentication = env.authentication.upper() if isinstance(env.authentication, str) else "UNKNOWN"
    if authentication not in {"VALID", "FAILED", "UNVERIFIED", "UNKNOWN"}:
        authentication = "UNKNOWN"
    attempts = env.stats.get("requests", 0)
    attempts = attempts if isinstance(attempts, int) and not isinstance(attempts, bool) and attempts >= 0 else 0
    steps = []
    for record in records:
        location = "Portal " + record["portal_id"] if record["portal_id"] else "Environment"
        operation = record["endpoint_name"] or record["endpoint"] or "operation not established"
        record["next_step"] = guidance(record, authentication=authentication)
        step = location + " / " + operation + ": " + record["next_step"]
        if step not in steps:
            steps.append(step)
    scope = topology_scope_evidence(env.topology)
    document = {
        "schema_version": "1.1", "tool_version": __version__, "generated_at": env.generated_at,
        "purpose": "Sanitized topology and collection diagnostics; not migration-readiness approval.",
        "mode": "DISCOVERY_ONLY" if env.settings.get("diagnose_only") else "ASSESSMENT",
        "authentication": authentication,
        "topology": {"outcome": topology_outcome, "complete": bool(env.topology.complete),
                     "mode": env.topology.mode if env.topology.mode in {"automatic", "explicit", "assisted"} else "unknown",
                     "credential_scope": env.topology.credential_scope,
                     "selection_source": "explicit" if env.topology.mode == "explicit" else env.topology.selection_source,
                     "directory_outcome": scope["directory_outcome"],
                     "portals_observed": len(env.topology.portals), "portals_selected": len(env.portals), **scope},
        "scan_stop": stop, "http_attempts": attempts,
        "diagnostics": records, "next_steps": steps,
        "privacy": "No API keys, raw source responses, ticket content, Location headers or exception text are included. Response shapes contain only fixed schema names and JSON types; unknown keys are counted, not copied.",
        "safety": "GET only; no guessed portal IDs; one shared request limiter; no external AI service.",
    }
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"
