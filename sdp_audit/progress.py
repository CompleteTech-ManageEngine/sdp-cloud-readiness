"""Console progress without changing the assessment's coverage semantics.

An unfinished page traversal is normal while a collection remains queued. Its
stored status stays ``partial`` until enumeration completes; the console calls
that live state ``collecting`` and reserves ``incomplete`` for a stopped list.
Only fixed diagnostic text and numeric measurements are printed. Source bodies,
credentials, exception messages and arbitrary event values are never echoed.
"""

from __future__ import annotations

import math
import re
from typing import Any

from .models import Dataset, EnvironmentSnapshot, Snapshot


_KEYS = {
    "incident_templates", "service_templates", "field_definitions", "sites",
    "support_groups", "technicians", "users", "reports", "ci_types", "requests",
    "changes", "problems", "projects", "releases", "assets", "computers", "cis",
    "contracts", "purchases", "request_notes", "request_tasks",
    "asset_modules", "orgusers", "departments", "space_structure", "space_floor", "space_room", "space_campus",
}
_PHASES = {
    "topology": "Phase 1/5: Discovering ServiceDesk Plus topology",
    "capabilities": "Phase 2/5: Enumerating portal modules",
    "inventory": "Phase 3/5: Collecting inventories",
    "sampling": "Phase 4/5: Sampling record details, subresources and field metadata",
    "analysis": "Phase 5/5: Evaluating migration impact",
    "children": "Inspecting notes and tasks of selected requests",
    "details": "Inspecting selected record details",
}
_OUTCOME_TEXT = {
    "PERMISSION_DENIED": "access denied; count unknown",
    "AUTHENTICATION_FAILED": "authentication failed; count unknown",
    "PORTAL_CONTEXT_REQUIRED": "portal context rejected or required; count unknown",
    "PORTAL_NOT_ACCESSIBLE": "portal not accessible; count unknown",
    "MODULE_NOT_ENABLED": "module not enabled; count unknown",
    "MODULE_NOT_AVAILABLE": "module unavailable/not exposed; count unknown",
    "ENDPOINT_UNSUPPORTED": "endpoint unsupported; count unknown",
    "API_VERSION_INCOMPATIBLE": "API/build incompatible; count unknown",
    "INVALID_QUERY": "API query rejected; count unknown",
    "NETWORK_ERROR": "connection failed; count unknown",
    "SERVER_ERROR": "server error; count unknown",
    "PARSE_ERROR": "unexpected API response; count unknown",
    "RATE_LIMITED": "rate limit stopped this read; count unknown",
    "UNKNOWN_API_ERROR": "unclassified API error; count unknown",
    "NOT_STARTED": "never scanned; count unknown",
}
_STATUS_TEXT = {
    "forbidden": "access denied; count unknown",
    "authentication": "authentication failed; count unknown",
    "unsupported": "endpoint unavailable; count unknown",
    "license": "unavailable under source license; count unknown",
    "throttled": "rate limit stopped this read; count unknown",
    "network": "connection failed; count unknown",
    "tls": "certificate validation failed; count unknown",
    "invalid_response": "unexpected API response; count unknown",
    "not_attempted": "not attempted; count unknown",
}
_ISSUE_REASONS = (
    ("Read failed: forbidden", "access denied after earlier reads"),
    ("Read failed: unsupported", "endpoint unavailable after earlier reads"),
    ("Read failed: license", "source license prevented a read"),
    ("Read failed: throttled", "rate limit stopped a read"),
    ("Read failed: network", "connection failed during a read"),
    ("Read failed: tls", "certificate validation failed"),
    ("Read failed: invalid_response", "unexpected API response"),
    ("Configured per-resource record limit", "configured record limit reached"),
    ("Inventory budget reserved", "request budget reserved for detail inspection"),
    ("Expected documented collection key", "unexpected API response structure"),
    ("No reliable pagination termination", "pagination completion unverified"),
    ("Repeated page detected", "repeated page detected"),
    ("Overlapping record IDs", "overlapping page data"),
    ("API total changed", "source changed during collection"),
    ("Server returned an unexpected pagination index", "unexpected page index"),
    ("Server reported more rows", "pagination inconsistency"),
    ("Enumerated unique records do not reconcile", "count mismatch"),
    ("A record had no documented numeric ID", "record identifiers could not be validated"),
)


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        result = float(value)
    except (ValueError, OverflowError):
        return None
    return result if math.isfinite(result) and result >= 0 else None


def _count(value: Any) -> int | None:
    result = _number(value)
    return int(result) if result is not None and result.is_integer() else None


def _key(value: Any) -> str:
    return value if isinstance(value, str) and value in _KEYS else "collection"


def _scope(event: dict[str, Any]) -> str:
    if event.get("scope") == "environment":
        return "Environment / "
    portal_id = event.get("portal_id")
    if not isinstance(portal_id, str) or not re.fullmatch(r"[0-9]{1,40}", portal_id):
        return ""
    name = event.get("portal_name")
    if not isinstance(name, str):
        name = "Portal " + portal_id
    name = re.sub(r"<[^>]*>", "", name)
    name = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[email omitted]", name)
    name = " ".join("".join(c for c in name if c.isprintable()).split())[:100]
    return 'Portal "' + (name or portal_id) + '" [' + portal_id + "] / "


def _duration(value: float) -> str:
    seconds = int(value)
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes:02d}:{seconds:02d}"
    hours, minutes = divmod(minutes, 60)
    return f"{hours:d}:{minutes:02d}:{seconds:02d}"


def _issue_reason(issues: Any) -> str:
    if isinstance(issues, (list, tuple)):
        for prefix, reason in _ISSUE_REASONS:
            if any(isinstance(item, str) and item.startswith(prefix) for item in issues):
                return reason
    return "list completion was not established"


def _interruption_reason(value: Any) -> str:
    if isinstance(value, str):
        if value.startswith("Configured request/time budget reached"):
            return "configured request/time budget reached"
        if value.startswith("Interrupted by user"):
            return "interrupted by user"
        if value.startswith("Collection stopped: authentication"):
            return "authentication failed"
        if value.startswith("Collection stopped:"):
            return "an API read prevented further collection"
    return "collection ended before all planned reads finished"


class ProgressPrinter:
    """Format safe event dictionaries; at most one generic heartbeat per 15 s."""

    def __init__(self, max_requests: int, quiet: bool = False):
        self.max_requests = _count(max_requests) or 0
        self.quiet = quiet
        self._last_output_at: float | None = None
        self._elapsed = 0.0
        self._requests = 0
        self._phase: str | None = None
        self._last_measurement_at: dict[str, float] = {}

    def _prefix(self) -> str:
        return (f"  [{_duration(self._elapsed)} elapsed | "
                f"{self._requests}/{self.max_requests} HTTP attempts] ")

    def _write(self, message: str) -> None:
        print(self._prefix() + message, flush=True)
        self._last_output_at = self._elapsed

    def __call__(self, event: dict[str, Any]) -> None:
        if self.quiet:
            return
        elapsed = _number(event.get("elapsed_seconds"))
        if elapsed is not None:
            self._elapsed = max(self._elapsed, elapsed)
        requests = _count(event.get("requests"))
        if requests is not None:
            self._requests = max(self._requests, requests)
        kind = event.get("event")
        if kind == "phase":
            phase = event.get("phase")
            if isinstance(phase, str) and phase in _PHASES and phase != self._phase:
                self._phase = phase
                self._write(_PHASES[phase] + ".")
            return
        if kind == "portal":
            index, total = _count(event.get("index")), _count(event.get("total"))
            if index is not None and total is not None:
                self._write(f"Assessing portal {index}/{total}: " + _scope(event).removesuffix(" / "))
            return
        if kind == "topology_complete":
            count = _count(event.get("portals")) or 0
            if event.get("mode") == "explicit":
                suffix = "explicit targets; environment directory was not enumerated"
            elif event.get("complete"):
                suffix = ("directory list complete for the separate directory key; module permissions use assigned collection credentials"
                          if event.get("credential_scope") == "directory_key" else "directory list complete for this key")
            elif event.get("mode") == "assisted":
                suffix = "verified multi-portal list selected within this run; directory coverage unverified"
            else:
                suffix = "directory coverage incomplete"
            outcome = event.get("outcome")
            if outcome not in {"COMPLETE", "EMPTY", "COLLECTING", "INCOMPLETE", "INTERRUPTED", *_OUTCOME_TEXT.keys(),
                               "RECORD_LIMIT_REACHED", "TIME_BUDGET_REACHED", "REQUEST_BUDGET_REACHED"}:
                outcome = "UNKNOWN"
            self._write(f"{count} portals selected; {suffix}; result: {outcome}.")
            if count == 0:
                self._write("No portal module inventory will be queried; source coverage is unknown.")
            return
        if kind == "collection":
            count = _count(event.get("records")) or 0
            total = _count(event.get("api_reported_total"))
            measured = f"{count} records observed"
            if total is not None:
                measured += f" / {total} API-reported total"
            status = event.get("status")
            if event.get("more_pages") is True:
                state = "collecting; more pages queued"
                if isinstance(event.get("issues"), list) and event["issues"]:
                    state += "; coverage note: " + _issue_reason(event["issues"])
            elif status == "complete":
                state = "list complete for API-visible scope"
                if count == 0:
                    state += "; no visible rows returned"
            elif event.get("outcome") in _OUTCOME_TEXT or isinstance(status, str) and status in _STATUS_TEXT:
                state = _OUTCOME_TEXT.get(event.get("outcome"), _STATUS_TEXT.get(status, "count unknown"))
                if count == 0:
                    measured = "no records read"
                else:
                    state = "incomplete; " + state.replace("; count unknown", "; total count unknown")
            else:
                state = "incomplete; " + _issue_reason(event.get("issues"))
            pages = _count(event.get("pages"))
            page_text = f" Pages read: {pages}." if pages else ""
            self._write(_scope(event) + f"{_key(event.get('key'))}: {measured}; {state}." + page_text)
            return
        if kind == "budget_reservation":
            remaining = _count(event.get("remaining_requests"))
            pending = _count(event.get("collections"))
            remainder = (f"at most {remaining} HTTP attempts remaining" if remaining is not None
                         else "the remaining request budget")
            pending_text = (f" {pending} list collections remain incomplete." if pending is not None else "")
            self._write("Continuing to sampled reads with " + remainder + "." + pending_text)
            return
        if kind == "retry":
            label = {"throttled": "Server rate limit", "network": "Connection read failure"}.get(
                event.get("kind") if isinstance(event.get("kind"), str) else None,
                "Read retry",
            )
            delay = _number(event.get("delay_seconds"))
            delay_text = f"at least {delay:g} seconds" if delay is not None else "the permitted retry time"
            logical = event.get("endpoint_name")
            context = _scope(event)
            if isinstance(logical, str) and logical in _KEYS:
                context += logical + ": "
            self._write(context + label + "; waiting " + delay_text + " before retrying.")
            return
        heartbeat_due = self._last_output_at is None or self._elapsed - self._last_output_at >= 15
        if kind in ("details", "children", "field_metadata"):
            last_measurement = self._last_measurement_at.get(kind)
            if last_measurement is not None and self._elapsed - last_measurement < 15:
                return
            self._last_measurement_at[kind] = self._elapsed
        elif not heartbeat_due:
            return
        if kind == "details":
            examined = _count(event.get("details")) or 0
            attempted = _count(event.get("attempted"))
            detail_text = f"{examined} successful detail reads"
            if attempted is not None:
                detail_text += f" / {attempted} attempted"
            self._write(_scope(event) + f"{_key(event.get('key'))}: {detail_text}; selected records only.")
        elif kind == "children":
            parents = _count(event.get("parents")) or 0
            records = _count(event.get("records")) or 0
            self._write(_scope(event) + f"{_key(event.get('key'))}: {parents} selected requests visited; {records} child records observed.")
        elif kind == "field_metadata":
            fields = _count(event.get("fields_observed"))
            attempted = _count(event.get("metadata_targets_attempted")) or 0
            amount = f"{fields} field definitions observed" if fields is not None else "field count unknown"
            self._write(_scope(event) + _key(event.get("module")) + f": {amount}; {attempted} metadata targets attempted; registry completeness unverified.")
        elif kind in ("request", "success", "wait", "error"):
            activity = {
                "topology": "portal discovery in progress",
                "capabilities": "portal capability reads in progress",
                "inventory": "list inventory in progress",
                "sampling": "field metadata and selected details in progress",
                "children": "selected request notes/tasks in progress",
                "details": "selected record details in progress",
            }.get(self._phase, "assessment in progress")
            if kind == "wait":
                remaining = _number(event.get("remaining_seconds"))
                wait_text = f" ({remaining:g}s remaining)" if remaining is not None else ""
                self._write("Paced wait before the next GET" + wait_text + "; " + activity + ".")
            else:
                self._write("Paced GET requests; " + activity + ".")


def print_coverage_summary(snapshot: Snapshot, resource_keys: set[str]) -> None:
    """Keep parent list, detail, and sampled child coverage separate on exit."""
    complete: list[tuple[str, Dataset]] = []
    incomplete: list[tuple[str, Dataset]] = []
    unavailable: list[tuple[str, Dataset | None]] = []
    for key in sorted(resource_keys):
        dataset = snapshot.datasets.get(key)
        if dataset is not None and dataset.list_complete:
            complete.append((key, dataset))
        elif dataset is not None and (dataset.records or dataset.status == "partial"):
            incomplete.append((key, dataset))
        else:
            unavailable.append((key, dataset))

    print("\nCollection coverage (API-visible scope):")
    print(f"  Parent lists complete: {len(complete)}/{len(resource_keys)}")
    print(f"  Parent lists incomplete: {len(incomplete)}/{len(resource_keys)}")
    print(f"  Parent lists unavailable or not attempted: {len(unavailable)}/{len(resource_keys)}")
    for key, dataset in incomplete:
        print(f"    {_key(key)}: incomplete; {_issue_reason(dataset.issues)}.")
    for key, dataset in unavailable:
        status = dataset.status if dataset is not None else "not_attempted"
        print(f"    {_key(key)}: {_STATUS_TEXT.get(status, 'unavailable; count unknown')}.")

    parent_datasets = [snapshot.datasets[key] for key in resource_keys if key in snapshot.datasets]
    succeeded = sum(_count(item.detail_succeeded) or 0 for item in parent_datasets)
    attempted = sum(_count(item.detail_attempted) or 0 for item in parent_datasets)
    print(f"  Parent record details: {succeeded} successful / {attempted} attempted.")
    print("  Detail reads cover selected observed records; a complete list does not certify full detail coverage.")
    for key in ("request_notes", "request_tasks"):
        dataset = snapshot.datasets.get(key)
        if dataset is None:
            continue
        success = _count(dataset.detail_succeeded) or 0
        attempts = _count(dataset.detail_attempted) or 0
        scope = "complete for API-visible parents" if dataset.list_complete else "selected-parent scope; other coverage unknown"
        print(f"  {key}: {success}/{attempts} selected parent lists read completely; {scope}.")
    print("  Empty lists establish only that no rows were visible to this API key in the selected scope.")
    if snapshot.interrupted_reason:
        print("  Run ended early: " + _interruption_reason(snapshot.interrupted_reason) + ". Collected evidence was preserved.")


def print_environment_coverage(env: EnvironmentSnapshot) -> None:
    """Consolidated exit summary, with unknown counts preserved."""
    print("\nEnvironment coverage (API-visible scope):")
    print(f"  Portals discovered: {sum(p.discovered for p in env.topology.portals)}; selected: {len(env.portals)}; with successful scoped reads: {sum(p.portal.accessible is True for p in env.portals.values())}.")
    if env.topology.mode == "explicit":
        print("  Explicit portal targeting was used; other environment portals were not discovered or assessed.")
    elif env.topology.mode == "assisted":
        print("  A verified list/profile supplemented discovery within this run; all selected portals share one assessment. Directory completeness remains unverified.")
    elif not env.topology.complete:
        print("  Portal directory coverage is incomplete; additional accessible portals may exist.")
    for item in env.portals.values():
        header = _scope({"portal_id": item.portal.id, "portal_name": item.portal.name}).removesuffix(" / ")
        datasets = list(item.snapshot.datasets.values())
        complete = sum(ds.list_complete for ds in datasets)
        print(f"  {header}: {complete}/{len(datasets)} lists complete; {item.portal.scan_status}.")
        for ds in datasets:
            if ds.list_complete:
                continue
            observed = ds.coverage().get("records_observed")
            amount = f"{observed} records observed" if observed is not None else "count unknown"
            state = ds.outcome or "NOT_STARTED"
            reason = ds.stop_reason if ds.stop_reason else state
            print(f"    {_key(ds.key)}: {amount}; {state}; reason: {reason}.")
    if env.global_snapshot:
        ds = env.global_snapshot.datasets.get("orgusers")
        if ds:
            amount = ds.coverage().get("records_observed")
            print(f"  Organisation directory (collected once): {amount if amount is not None else 'unknown'} users observed; {ds.outcome}.")
    if env.stop_classification:
        print("  Environment scan stopped: " + env.stop_classification + ".")
    print(f"  Global HTTP attempts: {env.stats.get('requests', 0)}/{env.settings.get('max_requests', 500)}; one shared rate limiter.")
    print("  Complete lists describe assigned credentials' visibility; sampled details and field registries have separate coverage.")
