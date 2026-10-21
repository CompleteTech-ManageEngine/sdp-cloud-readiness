"""Read-only discovery of API-visible ServiceDesk Plus on-premises portals.

The /portals on-premises contract is documented by the maintainer of Netskope's
SDP integration. It was not found in the reviewed native ManageEngine guide or
Postman collection; this is not a promise of availability on every SDP build.
See docs/research-topology.md. No identifiers or alternative paths are guessed.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Callable

from .models import PortalInfo, Topology
from .transport import ApiError, BudgetExceeded, ReadOnlyClient


PORTAL_DISCOVERY_ENDPOINT = "/portals"
PORTAL_DISCOVERY_SOURCE = (
    "https://docs.netskope.com/en/"
    "manage-engine-service-desk-plus-plugin-for-ticket-orchestrator"
)
_SOURCE_QUALIFICATION = (
    "The on-premises /portals contract is published in Netskope's primary "
    "integration documentation. A corresponding list operation was not located "
    "in the reviewed public ManageEngine V3 guide or official Postman collection; "
    "availability and a minimum supported source build are not guaranteed."
)
_VISIBILITY_LIMITATION = (
    "Topology includes only portal identifiers returned to this integration key. "
    "Discovery visibility does not establish permission to read a portal's modules."
)
_EXPLICIT_IDS_FALLBACK = (
    "No portal identifiers were obtained; no implicit/default portal will be scanned. "
    "Obtain known portal IDs from your ServiceDesk Plus administrator and supply "
    "--portal-id ID (repeat for multiple portals) to assess explicit targets."
)
_ID = re.compile(r"[0-9]{1,128}", flags=re.ASCII)
_EMAIL = re.compile(r"[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+")
_URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
_CREDENTIAL = re.compile(
    r"(?i)\b(?:authtoken|api[_ -]?key|access[_ -]?token|authorization|password)"
    r"\s*[:=]\s*\S+"
)


def portal_identifier(value: Any) -> str:
    """Validate a supplied/discovered positive ASCII ID without echoing input."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError("Portal IDs must be positive ASCII decimal identifiers.")
    text = str(value)
    if not _ID.fullmatch(text) or int(text) <= 0:
        raise ValueError("Portal IDs must be positive ASCII decimal identifiers.")
    # Canonicalization prevents duplicate requests for e.g. 3 and 003.
    return str(int(text))


def _label(value: Any, maximum: int = 160) -> str | None:
    """Retain bounded configuration labels, never arbitrary record structures.

    The transport already redacts all spellings of the active integration key.
    This second boundary removes control characters and common PII/credential
    patterns from the few portal display labels that reporting needs.
    """
    if not isinstance(value, str):
        return None
    text = "".join(" " if unicodedata.category(ch).startswith("C") else ch for ch in value)
    text = _CREDENTIAL.sub("[credential omitted]", text)
    text = _EMAIL.sub("[email omitted]", text)
    text = _URL.sub("[URL omitted]", text)
    text = " ".join(text.split())
    return text[:maximum] or None


def _nested_label(value: Any) -> str | None:
    if isinstance(value, dict):
        return _label(value.get("internal_name")) or _label(value.get("name"))
    return _label(value)


def _boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    return None


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    text = str(value)
    if not _ID.fullmatch(text):
        return None
    return int(text)


def _portal(record: dict[str, Any]) -> PortalInfo:
    identifier = portal_identifier(record.get("id"))
    license_details = record.get("license_details")
    license_details = license_details if isinstance(license_details, dict) else {}
    # Status numbers vary by build/installation. They are never interpreted as
    # active/inactive or accessible/inaccessible without an explicit flag.
    active = _boolean(record.get("is_active"))
    if active is None:
        active = _boolean(record.get("active"))
    return PortalInfo(
        id=identifier,
        name=_label(record.get("name")) or f"Portal {identifier}",
        instance_type=_nested_label(record.get("type")),
        state=_nested_label(record.get("status")),
        active=active,
        edition=_label(license_details.get("edition")),
        discovery_endpoint=PORTAL_DISCOVERY_ENDPOINT,
        discovery_source=PORTAL_DISCOVERY_SOURCE,
    )


def _diagnostic(classification: str, message: str, *, cause: str = "api_compatibility_or_scanner",
                retryable: bool = False, **extra: Any) -> dict[str, Any]:
    return {
        "classification": classification,
        "message": message,
        "message_sanitized": True,
        "http_status": None,
        "api_codes": [],
        "portal_id": None,
        "endpoint": PORTAL_DISCOVERY_ENDPOINT,
        "endpoint_name": "portals",
        "module": "topology",
        "cause": cause,
        "retryable": retryable,
        **extra,
    }


def discover_topology(
    client: ReadOnlyClient,
    portal_ids: list[str] | None = None,
    page_size: int = 100,
    max_portals: int = 100,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> Topology:
    """Return discovered/explicit portal contexts and honest coverage metadata.

    The supplied client owns the only scheduler and all HTTP/runtime budgets.
    This function creates no clients, performs no portal-specific probes, and
    never retries an unsupported discovery path using guessed identifiers.
    A returned INTERRUPTED topology must make the caller stop further work and
    write the partial report. Other global stop outcomes are similarly explicit.
    """
    for name, value in (("page_size", page_size), ("max_portals", max_portals)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")
    if page_size > 1000:
        raise ValueError("Portal discovery page_size must not exceed the scanner limit of 1000.")

    topology = Topology(source=PORTAL_DISCOVERY_SOURCE)

    def emit(event: str) -> None:
        if progress is not None:
            progress({
                "phase": "topology", "event": event,
                "portal_id": None, "endpoint_name": "portals", "module": "topology",
                "portals_observed": len(topology.portals), "pages_observed": topology.pages,
                "outcome": topology.outcome, "complete": topology.complete,
            })

    def stop(classification: str, diagnostic: dict[str, Any]) -> Topology:
        topology.outcome = classification
        topology.complete = False
        last = getattr(client, "last_response", {})
        if isinstance(last, dict) and last.get("endpoint") == PORTAL_DISCOVERY_ENDPOINT:
            for field in ("http_status", "api_codes", "response_format", "content_type", "has_sdp_status"):
                if diagnostic.get(field) is None or field == "api_codes" and not diagnostic.get(field):
                    if field in last:
                        diagnostic[field] = last[field]
        topology.diagnostics.append(diagnostic)
        if topology.mode == "automatic" and not topology.portals:
            topology.limitations.append(_EXPLICIT_IDS_FALLBACK)
        elif topology.mode == "automatic":
            topology.limitations.append(
                "Portal discovery is incomplete. Safely discovered IDs are retained; "
                "additional visible portals may remain undiscovered."
            )
        # Never let a second Ctrl+C in a progress callback prevent returning the
        # partial topology. The interrupt remains explicit in the outcome.
        if classification != "INTERRUPTED":
            try:
                emit("discovery_stopped")
            except KeyboardInterrupt:
                topology.outcome = "INTERRUPTED"
                topology.diagnostics.append(_diagnostic(
                    "INTERRUPTED", "Portal discovery was interrupted by the user.",
                    cause="user_interruption", retryable=True,
                ))
        return topology

    if portal_ids is not None:
        if not isinstance(portal_ids, (list, tuple)) or not portal_ids:
            raise ValueError("Provide one or more explicit portal IDs, or omit the override for automatic discovery.")
        identifiers = list(dict.fromkeys(portal_identifier(item) for item in portal_ids))
        topology.mode = "explicit"
        topology.selection_source = "explicit"
        topology.directory_outcome = "NOT_ATTEMPTED"
        topology.endpoint = ""
        topology.source = "user-supplied portal IDs"
        topology.limitations.append(
            "Explicit targeting bypassed topology enumeration. These IDs are user supplied; "
            "other portals and target accessibility are not established by discovery."
        )
        topology.portals = [
            PortalInfo(
                id=identifier, name=f"Portal {identifier}", discovered=False,
                discovery_source="user-supplied --portal-id override",
            )
            for identifier in identifiers[:max_portals]
        ]
        if len(identifiers) > max_portals:
            return stop("RECORD_LIMIT_REACHED", _diagnostic(
                "RECORD_LIMIT_REACHED", "The scanner's portal limit restricted the explicit target list.",
                cause="scanner_limit", max_portals=max_portals, explicit_targets=len(identifiers),
            ))
        topology.outcome = "COMPLETE"
        topology.complete = True  # Complete explicit target set, not complete environment discovery.
        try:
            emit("explicit_targets")
        except KeyboardInterrupt:
            return stop("INTERRUPTED", _diagnostic(
                "INTERRUPTED", "Portal discovery was interrupted by the user.",
                cause="user_interruption", retryable=True,
            ))
        return topology

    topology.limitations.extend([_SOURCE_QUALIFICATION, _VISIBILITY_LIMITATION])
    topology.outcome = "COLLECTING"
    seen: set[str] = set()
    start_index = 1
    known_total: int | None = None
    minimal_query = False

    try:
        emit("discovery_started")
        while True:
            requested = min(page_size, max_portals - len(topology.portals))
            if requested <= 0:
                return stop("RECORD_LIMIT_REACHED", _diagnostic(
                    "RECORD_LIMIT_REACHED", "The scanner's portal limit was reached while more portals were available.",
                    cause="scanner_limit", max_portals=max_portals,
                ))
            list_info = {"row_count": requested, "start_index": start_index}
            if not minimal_query:
                list_info.update(page=topology.pages + 1, sort_field="created_time", sort_order="desc")
            params = {"input_data": json.dumps({"list_info": list_info}, separators=(",", ":"))}
            # None is deliberate even when the client's legacy default portal
            # is configured: the directory is the global discovery operation.
            try:
                response = client.get_json(
                    PORTAL_DISCOVERY_ENDPOINT, params,
                    portal_id=None, endpoint_name="portals", module="topology",
                )
            except ApiError as error:
                # One narrowly bounded compatibility retry of the SAME GET.
                # Never retry authorization/TLS/404 as if it were a query issue,
                # and never change ordering after a page has been accepted.
                if (error.classification == "INVALID_QUERY" and not minimal_query
                        and topology.pages == 0
                        and error.http_status not in {406, 415}):
                    diagnostic = error.to_dict()
                    diagnostic.update(endpoint=PORTAL_DISCOVERY_ENDPOINT, endpoint_name="portals",
                                      portal_id=None, module="topology",
                                      compatibility_retry="minimal_pagination_same_endpoint")
                    topology.diagnostics.append(diagnostic)
                    topology.limitations.append(
                        "The first portal query was rejected. One read-only retry omits optional page/sort fields; "
                        "it uses the same endpoint, credentials, global rate limiter and budgets."
                    )
                    minimal_query = True
                    emit("discovery_query_fallback")
                    continue
                raise
            if not isinstance(response, dict) or not isinstance(response.get("portals"), list):
                return stop("PARSE_ERROR", _diagnostic(
                    "PARSE_ERROR", "The documented portals array was missing or malformed; no absence was inferred.",
                ))
            rows = response["portals"]
            topology.pages += 1
            invalid_records = False
            overlap = False
            truncated = False
            for row in rows:
                if not isinstance(row, dict):
                    invalid_records = True
                    continue
                try:
                    portal = _portal(row)
                except ValueError:
                    invalid_records = True
                    continue
                if portal.id in seen:
                    overlap = True
                    continue
                if len(topology.portals) >= max_portals:
                    truncated = True
                    continue
                seen.add(portal.id)
                topology.portals.append(portal)

            if invalid_records:
                return stop("PARSE_ERROR", _diagnostic(
                    "PARSE_ERROR", "A portal record lacked a valid positive ASCII identifier or was malformed; valid IDs were retained.",
                ))
            if overlap:
                return stop("INCOMPLETE", _diagnostic(
                    "INCOMPLETE", "Portal pagination repeated or overlapped identifiers; distinct IDs were retained without claiming completeness.",
                    cause="pagination_integrity", retryable=True,
                ))
            if truncated:
                return stop("RECORD_LIMIT_REACHED", _diagnostic(
                    "RECORD_LIMIT_REACHED", "The response exceeded the scanner's portal limit; only the allowed number of IDs was retained.",
                    cause="scanner_limit", max_portals=max_portals,
                ))

            info = response.get("list_info")
            if not isinstance(info, dict) or _boolean(info.get("has_more_rows")) is None:
                return stop("PARSE_ERROR", _diagnostic(
                    "PARSE_ERROR", "Portal pagination metadata was missing or malformed; completeness is unknown.",
                ))
            more = _boolean(info["has_more_rows"])
            if "start_index" in info and _count(info["start_index"]) != start_index:
                return stop("INCOMPLETE", _diagnostic(
                    "INCOMPLETE", "The portal response start_index did not match the requested page.",
                    cause="pagination_integrity", retryable=True,
                ))
            if "row_count" in info and _count(info["row_count"]) != len(rows):
                return stop("INCOMPLETE", _diagnostic(
                    "INCOMPLETE", "The portal response row_count did not match the returned array.",
                    cause="pagination_integrity", retryable=True,
                ))
            if "total_count" in info:
                total = _count(info["total_count"])
                if total is None:
                    return stop("PARSE_ERROR", _diagnostic(
                        "PARSE_ERROR", "The portal response contained an invalid total_count.",
                    ))
                if known_total is not None and total != known_total:
                    return stop("INCOMPLETE", _diagnostic(
                        "INCOMPLETE", "The API-reported portal total changed between pages.",
                        cause="pagination_integrity", retryable=True,
                    ))
                known_total = total
            if not more:
                if known_total is not None and known_total != len(topology.portals):
                    return stop("INCOMPLETE", _diagnostic(
                        "INCOMPLETE", "The API-reported portal total did not match the distinct identifiers discovered.",
                        cause="pagination_integrity", retryable=True,
                    ))
                topology.complete = True
                topology.outcome = "COMPLETE" if topology.portals else "EMPTY"
                if not topology.portals:
                    topology.limitations.append(_EXPLICIT_IDS_FALLBACK)
                emit("discovery_complete")
                return topology
            if not rows:
                return stop("INCOMPLETE", _diagnostic(
                    "INCOMPLETE", "The portal API returned an empty page while claiming more rows; pagination could not advance safely.",
                    cause="pagination_integrity", retryable=True,
                ))
            if known_total is not None and len(topology.portals) >= known_total:
                return stop("INCOMPLETE", _diagnostic(
                    "INCOMPLETE", "The portal API claimed more rows after reaching its reported total.",
                    cause="pagination_integrity", retryable=True,
                ))
            if len(topology.portals) >= max_portals:
                return stop("RECORD_LIMIT_REACHED", _diagnostic(
                    "RECORD_LIMIT_REACHED", "The scanner's portal limit was reached while more portals were available.",
                    cause="scanner_limit", max_portals=max_portals,
                ))
            start_index += len(rows)
            emit("discovery_page")
    except ApiError as error:
        diagnostic = error.to_dict()
        diagnostic.update(portal_id=None, endpoint=PORTAL_DISCOVERY_ENDPOINT,
                          endpoint_name="portals", module="topology")
        return stop(error.classification, diagnostic)
    except BudgetExceeded as error:
        budget = error.to_dict()
        message = budget.pop("message")
        return stop(error.classification, _diagnostic(
            error.classification, message, cause="scanner_budget", **budget,
        ))
    except KeyboardInterrupt:
        return stop("INTERRUPTED", _diagnostic(
            "INTERRUPTED", "Portal discovery was interrupted by the user; partial identifiers were retained.",
            cause="user_interruption", retryable=True,
        ))


def topology_scope_evidence(topology: Topology) -> dict[str, Any]:
    """Separate successful target selection from a complete portal directory.

    The historical 'complete' flag is kept for library/JSON compatibility.
    Its meaning is made explicit instead of relabelling a supplied ID as a
    discovered portal or certifying environment-wide access.
    """
    directory_complete = topology.mode == "automatic" and topology.complete
    outcome = ("NOT_ATTEMPTED" if topology.mode == "explicit" else
               topology.directory_outcome or topology.outcome)
    return {
        "complete_scope": "explicit_selection" if topology.mode == "explicit" else "portal_directory",
        "directory_complete": directory_complete,
        "directory_outcome": outcome,
        "portals_discovered": sum(portal.discovered for portal in topology.portals),
        "portals_supplied": sum(not portal.discovered for portal in topology.portals),
        "coverage_basis": ("explicit_targets_only" if topology.mode == "explicit" else
                           "discovery_credential_visible_directory" if directory_complete else
                           "incomplete_directory_or_supplied_scope"),
    }
