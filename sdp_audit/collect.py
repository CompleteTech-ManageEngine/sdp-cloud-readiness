"""Bounded, breadth-first collection from documented read-only endpoints.

Missing, forbidden, malformed and truncated results remain explicit coverage gaps.
No response bodies or source records are written to disk by this module.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

from .models import Dataset, ResourceSpec, Snapshot
from .transport import ApiError, BudgetExceeded, ReadOnlyClient
from .response_contract import shape_evidence


@dataclass
class CollectionOptions:
    page_size: int = 100
    max_records: int = 5000
    detail_limit: int = 20
    subresource_parents: int = 10
    max_child_records: int = 200
    inventory_budget_fraction: float = 0.65
    count_policy: str = "first"

    def __post_init__(self) -> None:
        if self.count_policy not in {"first", "always", "never"}:
            raise ValueError("count_policy must be first, always, or never.")


def _collect_id(record: dict[str, Any]) -> str | None:
    value = record.get("id")
    if value is None or isinstance(value, bool):
        return None
    text = str(value)
    return text if re.fullmatch(r"[0-9]+", text) else None


def _collect_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "false"):
        return value.lower() == "true"
    return None


def _collect_count(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        if isinstance(value, float) and not value.is_integer():
            return None
        result = int(value)
        return result if result >= 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def select_details(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Deterministic coverage sample, explicitly not a statistical estimate."""
    candidates = [r for r in records if _collect_id(r) is not None]
    if limit == 0 or len(candidates) <= limit:
        return candidates
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(row: dict[str, Any]) -> None:
        key = _collect_id(row)
        if key not in seen and len(chosen) < limit:
            seen.add(key)
            chosen.append(row)

    if not candidates:
        return chosen
    add(candidates[0])
    add(candidates[-1])
    signal_limit = max(2, limit // 2)
    for row in candidates:
        if len(chosen) >= signal_limit:
            break
        if any(row.get(k) is True for k in ("has_attachments", "has_notes", "has_fafr")):
            add(row)
    for index in range(limit):
        add(candidates[round(index * (len(candidates) - 1) / max(limit - 1, 1))])
    for row in candidates:
        add(row)
        if len(chosen) >= limit:
            break
    return chosen


class Collector:
    def __init__(self, client: ReadOnlyClient, resources: list[ResourceSpec],
                 options: CollectionOptions | None = None,
                 fallbacks: dict[str, list[ResourceSpec]] | None = None,
                 progress: Callable[[dict[str, Any]], None] | None = None):
        self.client = client
        self.resources = resources
        self.options = options or CollectionOptions()
        self.fallbacks = {key: list(value) for key, value in (fallbacks or {}).items()}
        self.progress = progress or (lambda event: None)
        self._specs = {r.key: r for r in resources}
        self._next: dict[str, int] = {}
        self._seen: dict[str, set[str]] = {}
        self._fingerprints: dict[str, set[str]] = {}
        self._minimal: set[str] = set()
        self._integrity_issues: set[str] = set()

    def _progress(self, **event: Any) -> None:
        stats = self.client.stats
        event.setdefault("requests", stats.get("requests", 0))
        event.setdefault("elapsed_seconds", stats.get("elapsed_seconds", 0))
        event.setdefault("portal_id", getattr(self.client, "portal_id", None))
        event.setdefault("portal_name", getattr(self.client, "portal_name", None))
        self.progress(event)

    def _set_error(self, dataset: Dataset, error: ApiError) -> None:
        dataset.status = "partial" if dataset.records else error.kind
        dataset.outcome = getattr(error, "classification", "UNKNOWN_API_ERROR")
        dataset.stop_reason = dataset.outcome
        if hasattr(error, "to_dict"):
            dataset.diagnostics.append(error.to_dict())
            dataset.last_response = error.to_dict()
        dataset.list_complete = False
        dataset.issues.append("Read failed: " + error.kind + ". No absence was inferred.")
        if error.kind == "authentication":
            raise error

    def _read_json(self, spec: ResourceSpec, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        scoped_read = getattr(self.client, "get_resource_json", None)
        if scoped_read is not None:
            return scoped_read(spec, path, params)
        return self.client.get_json(path, params)

    @staticmethod
    def _with_provenance(row: dict[str, Any], dataset: Dataset) -> dict[str, Any]:
        return {**row, "_portal_id": dataset.portal_id, "_portal_name": dataset.portal_name,
                "_module": dataset.module or dataset.key, "_scope": dataset.scope}

    @staticmethod
    def _wrong_portal(row: dict[str, Any], dataset: Dataset) -> bool:
        if dataset.scope != "portal" or dataset.portal_id is None:
            return False
        portal = row.get("portal")
        explicit = portal.get("id") if isinstance(portal, dict) else row.get("portal_id")
        return explicit is not None and str(explicit) != dataset.portal_id

    def _get_page(self, spec: ResourceSpec, start: int, count: int) -> dict[str, Any]:
        info: dict[str, Any] = {"row_count": count, "start_index": start}
        if spec.key not in self._minimal:
            info.update({"get_total_count": self.options.count_policy == "always"
                         or self.options.count_policy == "first" and start == 1,
                         "sort_field": "id", "sort_order": "asc"})
        if spec.search_fields:
            info["search_fields"] = spec.search_fields
        info.update(spec.list_info_extras)
        if "sort_fields" in info:
            info.pop("sort_field", None)
            info.pop("sort_order", None)
        params = {"input_data": json.dumps({"list_info": info}, separators=(",", ":"))}
        if not spec.paginated:
            params = ({"input_data": json.dumps({"list_info": spec.list_info_extras})}
                      if spec.list_info_extras else {})
        try:
            return self._read_json(spec, spec.path, params)
        except ApiError as error:
            # Some old builds reject sort/count flags. Required filters remain intact.
            codes = set(getattr(error, "api_codes", ()) or ())
            if (start == 1 and spec.paginated and spec.key not in self._minimal
                    and error.classification == "INVALID_QUERY"
                    and codes.intersection({4000, 4001, 4009, 4011, 4021})):
                self._minimal.add(spec.key)
                return self._get_page(spec, start, count)
            raise

    def _contract_diagnostic(self, dataset: Dataset, spec: ResourceSpec,
                             response: dict[str, Any], reason: str, *,
                             path: str | None = None, expected: str | None = None,
                             classification: str = "PARSE_ERROR") -> dict[str, Any]:
        path = path or spec.path
        last = getattr(self.client, "last_response", {})
        # Never reuse protocol evidence left over from another resource/page.
        protocol = last if isinstance(last, dict) and last.get("endpoint") == path else {}
        diagnostic = {key: protocol[key] for key in (
            "http_status", "api_codes", "content_type", "has_sdp_status", "credential_scope"
        ) if key in protocol}
        diagnostic.update({
            "classification": classification, "kind": "invalid_response",
            "http_status": protocol.get("http_status"), "api_codes": protocol.get("api_codes", []),
            "portal_id": dataset.portal_id, "endpoint": path, "endpoint_name": dataset.key,
            "module": dataset.module or dataset.key, "cause": "api_compatibility_or_scanner",
            "message": "The collector response contract did not match this operation.",
            "message_sanitized": True, "raw_message_omitted": True,
            "retryable": False, "response_format": "json_object", "parse_reason": reason,
            "response_shape": shape_evidence(response, expected or spec.plural),
        })
        dataset.diagnostics.append(diagnostic)
        dataset.last_response = diagnostic
        return diagnostic

    def _page(self, dataset: Dataset, spec: ResourceSpec, record_cap: int | None = None) -> bool:
        """Return True only when another page should be queued."""
        cap = self.options.max_records if record_cap is None else record_cap
        count = self.options.page_size
        if cap:
            count = min(count, max(0, cap - len(dataset.records)))
        if count <= 0:
            dataset.status = "partial"
            dataset.outcome = "RECORD_LIMIT_REACHED"
            dataset.stop_reason = dataset.outcome
            dataset.issues.append("Configured per-resource record limit reached.")
            return False
        start = self._next.setdefault(dataset.key, 1)
        attempts_before = int(self.client.stats.get("requests", 0))
        try:
            response = self._get_page(spec, start, count)
            dataset.read_attempted = True
        except ApiError as error:
            alternatives = self.fallbacks.get(spec.key, [])
            if error.kind == "unsupported" and not dataset.records and alternatives:
                fallback = alternatives.pop(0)
                dataset.diagnostics.append(error.to_dict())
                dataset.issues.append("Preferred documented endpoint unavailable; trying documented legacy endpoint.")
                self._specs[spec.key] = fallback
                dataset.endpoint = fallback.path
                dataset.doc_url = fallback.doc_url
                return self._page(dataset, fallback, record_cap)
            self._set_error(dataset, error)
            return False
        finally:
            dataset.read_attempted |= int(self.client.stats.get("requests", 0)) > attempts_before

        dataset.last_response = dict(getattr(self.client, "last_response", {}) or {})

        # The current /asset_modules contract uses asset_modules; retain the
        # earlier all_product_types wrapper only for this reviewed endpoint.
        wrapper = spec.plural
        if spec.key == "asset_modules" and spec.path == "/asset_modules" and "asset_modules" in response:
            wrapper = "asset_modules"
            if spec.plural in response and response[spec.plural] != response[wrapper]:
                self._contract_diagnostic(dataset, spec, response, "CONFLICTING_COLLECTION_WRAPPERS")
                dataset.status, dataset.outcome = "invalid_response", "PARSE_ERROR"
                dataset.stop_reason = dataset.outcome
                return False
        rows = response.get(wrapper)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            dataset.status = "partial" if dataset.records else "invalid_response"
            dataset.outcome = "PARSE_ERROR"
            dataset.stop_reason = dataset.outcome
            reason = ("MISSING_COLLECTION_WRAPPER" if wrapper not in response else
                      "INVALID_COLLECTION_TYPE" if not isinstance(rows, list) else "NON_OBJECT_COLLECTION_ITEM")
            self._contract_diagnostic(dataset, spec, response, reason)
            dataset.issues.append("Expected documented collection key was missing or malformed: " + spec.plural)
            return False
        if self._wrong_portal(response, dataset) or any(self._wrong_portal(row, dataset) for row in rows):
            dataset.status = "partial" if dataset.records else "invalid_response"
            dataset.outcome = "PORTAL_CONTEXT_REQUIRED"
            dataset.stop_reason = dataset.outcome
            self._contract_diagnostic(dataset, spec, response, "RESPONSE_PORTAL_MISMATCH",
                                      classification=dataset.outcome)
            dataset.issues.append("Explicit response portal did not match requested context; page excluded from inventory.")
            return False
        info = response.get("list_info")
        if info is not None and not isinstance(info, dict):
            dataset.status = "partial" if dataset.records else "invalid_response"
            dataset.outcome = dataset.stop_reason = "PARSE_ERROR"
            self._contract_diagnostic(dataset, spec, response, "INVALID_LIST_INFO")
            dataset.issues.append("The list_info response value was not a JSON object; page excluded.")
            return False
        info = info if isinstance(info, dict) else {}
        total = _collect_count(info.get("total_count"))
        if total is not None:
            if dataset.total_count is not None and dataset.total_count != total:
                self._integrity_issues.add(dataset.key)
                dataset.issues.append("API total changed during collection; source is not a frozen snapshot.")
            dataset.total_count = total
            dataset.total_count_page = dataset.pages + 1
        returned_start = _collect_count(info.get("start_index"))
        if returned_start is not None and returned_start != start:
            dataset.status = "partial"
            dataset.outcome = "INCOMPLETE"
            dataset.stop_reason = "PARSE_ERROR"
            self._contract_diagnostic(dataset, spec, response, "PAGINATION_INDEX_MISMATCH")
            dataset.issues.append("Server returned an unexpected pagination index; traversal stopped.")
            return False
        fingerprint = hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        fingerprints = self._fingerprints.setdefault(dataset.key, set())
        if rows and fingerprint in fingerprints:
            dataset.status = "partial"
            dataset.outcome = "INCOMPLETE"
            dataset.stop_reason = "PARSE_ERROR"
            self._contract_diagnostic(dataset, spec, response, "REPEATED_PAGE")
            dataset.issues.append("Repeated page detected; pagination may have been ignored.")
            return False
        fingerprints.add(fingerprint)
        dataset.pages += 1
        dataset.capability = "AVAILABLE"
        seen = self._seen.setdefault(dataset.key, set())
        duplicates = 0
        for row in rows:
            key = _collect_id(row)
            if key is None:
                self._integrity_issues.add(dataset.key)
                dataset.issues.append("A record had no documented numeric ID; its detail cannot be requested.")
                key = "anon:" + hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            if cap and len(dataset.records) >= cap:
                self._integrity_issues.add(dataset.key)
                continue
            dataset.records.append(self._with_provenance(row, dataset))
        if duplicates:
            self._integrity_issues.add(dataset.key)
            dataset.issues.append("Overlapping record IDs appeared across pages; coverage is not certified complete.")
        dataset.issues = list(dict.fromkeys(dataset.issues))
        more = _collect_bool(info.get("has_more_rows"))
        if not spec.paginated:
            more = False
        if more is None and total is not None:
            more = len(dataset.records) < total
        if more is False:
            # An earlier total is a source snapshot, not permission to skip a
            # page. Reconcile it conservatively only at an explicit terminator.
            terminal_total = total if total is not None else dataset.total_count
            dataset.list_complete = (dataset.key not in self._integrity_issues
                                     and (terminal_total is None or len(dataset.records) == terminal_total))
            dataset.status = "complete" if dataset.list_complete else "partial"
            dataset.outcome = ("EMPTY" if not dataset.records else "COMPLETE") if dataset.list_complete else "INCOMPLETE"
            if terminal_total is not None and len(dataset.records) != terminal_total:
                self._contract_diagnostic(dataset, spec, response, "TOTAL_COUNT_CONFLICT")
                dataset.issues.append("Enumerated unique records do not reconcile to the last API-reported total_count snapshot.")
            return False
        dataset.status = "partial"
        dataset.outcome = "INCOMPLETE"
        if more is None:
            self._contract_diagnostic(dataset, spec, response, "PAGINATION_TERMINATION_MISSING")
            dataset.issues.append("No reliable pagination termination metadata; complete coverage cannot be established.")
            return False
        if not rows:
            self._contract_diagnostic(dataset, spec, response, "EMPTY_PAGE_WITH_MORE_ROWS")
            dataset.issues.append("Server reported more rows but returned an empty page.")
            return False
        if cap and len(dataset.records) >= cap:
            dataset.outcome = "RECORD_LIMIT_REACHED"
            dataset.stop_reason = dataset.outcome
            dataset.issues.append("Configured per-resource record limit reached.")
            return False
        self._next[dataset.key] = start + len(rows)
        dataset.outcome = "COLLECTING"
        return True

    def detail_steps(self, snapshot: Snapshot):
        """Yield after each detail read so an environment scheduler can be fair."""
        pending: deque[tuple[ResourceSpec, Dataset, deque[dict[str, Any]]]] = deque()
        for key, dataset in list(snapshot.datasets.items()):
            spec = self._specs.get(key)
            if not spec or not spec.detail or not dataset.records:
                continue
            selected = select_details(dataset.records, self.options.detail_limit)
            if not selected:
                continue
            dataset.sampling = "ID-ordered list; deterministic risk-focused detail sample, not statistical"
            pending.append((spec, dataset, deque(selected)))
        while pending:
            spec, dataset, rows = pending.popleft()
            row = rows.popleft()
            record_id = _collect_id(row)
            attempts_before = int(self.client.stats.get("requests", 0))
            try:
                response = self._read_json(spec, spec.path + "/" + record_id)
                detail = response.get(spec.singular)
                if (not isinstance(detail, dict) or _collect_id(detail) != record_id
                        or self._wrong_portal(detail, dataset)):
                    dataset.issues.append("Detail response missing expected entity or matching ID.")
                    self._contract_diagnostic(dataset, spec, response, "DETAIL_ENTITY_OR_ID_MISMATCH",
                                              path=spec.path + "/" + record_id, expected=spec.singular)
                else:
                    dataset.details.append(self._with_provenance(detail, dataset))
                    dataset.detail_succeeded += 1
            except ApiError as error:
                dataset.issues.append("Detail coverage gap: " + error.kind + ".")
                if hasattr(error, "to_dict"):
                    dataset.diagnostics.append(error.to_dict())
                if error.kind == "authentication":
                    raise
                if error.kind in ("unsupported", "forbidden", "license", "throttled"):
                    rows.clear()
            finally:
                if int(self.client.stats.get("requests", 0)) > attempts_before:
                    dataset.detail_attempted += 1
            dataset.issues = list(dict.fromkeys(dataset.issues))
            self._progress(event="details", key=dataset.key, details=dataset.detail_succeeded,
                           attempted=dataset.detail_attempted)
            if rows:
                pending.append((spec, dataset, rows))
            dataset.detail_complete = (dataset.list_complete and dataset.detail_succeeded == len(dataset.records)
                                       and dataset.detail_attempted == dataset.detail_succeeded)
            yield None

    def _details(self, snapshot: Snapshot) -> None:
        for _ in self.detail_steps(snapshot):
            pass

    def child_steps(self, snapshot: Snapshot):
        """Yield after each child page; successful pages are committed immediately."""
        parents = snapshot.datasets.get("requests")
        if not parents or not parents.records or self.options.subresource_parents == 0:
            return
        chosen = select_details(parents.records, self.options.subresource_parents)
        for kind, singular, doc_slug in (("notes", "note", "request_note"), ("tasks", "task", "request_task")):
            key = "request_" + kind
            combined = Dataset(key, "/requests/{id}/" + kind,
                               doc_url="https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/" + doc_slug + ".html")
            combined.portal_id = parents.portal_id
            combined.portal_name = parents.portal_name
            combined.module = "requests"
            combined.sampling = "Subresources of up to " + str(self.options.subresource_parents) + " sampled requests"
            combined.status = "partial"
            combined.outcome = "COLLECTING"
            snapshot.datasets[key] = combined
            all_complete = parents.list_complete and len(chosen) == len(parents.records)
            sampled_complete = True
            visited = 0
            for parent_index, parent in enumerate(chosen):
                parent_id = _collect_id(parent)
                child_key = key + ":" + parent_id
                spec = ResourceSpec(child_key, "/requests/" + parent_id + "/" + kind,
                                    kind, singular, combined.doc_url, detail=False)
                child = Dataset(child_key, spec.path)
                child.portal_id, child.portal_name, child.module = parents.portal_id, parents.portal_name, "requests"
                copied_count = 0
                copied_pages = 0
                finalized = False

                def finish_parent() -> None:
                    nonlocal visited, all_complete, sampled_complete, copied_count, copied_pages, finalized
                    if finalized:
                        return
                    for row in child.records[copied_count:]:
                        combined.records.append({**row, "_parent_id": parent_id})
                    copied_count = len(child.records)
                    combined.pages += child.pages - copied_pages
                    copied_pages = child.pages
                    combined.read_attempted |= child.read_attempted
                    combined.last_response = dict(child.last_response)
                    if child.read_attempted:
                        visited += 1
                        combined.detail_attempted += 1
                    combined.issues.extend(child.issues)
                    combined.diagnostics.extend(child.diagnostics)
                    if child.list_complete:
                        combined.detail_succeeded += 1
                    else:
                        combined.issues.append("A sampled parent's child collection is incomplete.")
                    all_complete = all_complete and child.list_complete
                    sampled_complete = sampled_complete and child.list_complete
                    finalized = True

                def finish_collection() -> None:
                    combined.sample_complete = sampled_complete and visited == len(chosen)
                    combined.sampled_parents = len(chosen)
                    combined.list_complete = all_complete
                    combined.detail_complete = all_complete
                    combined.status = "complete" if all_complete else "partial"
                    combined.outcome = (("EMPTY" if not combined.records else "COMPLETE") if all_complete
                                        else "SAMPLE_COMPLETE" if combined.sample_complete else "INCOMPLETE")
                    if not combined.records and not combined.pages and child.outcome not in {None, "COLLECTING", "COMPLETE", "EMPTY"}:
                        combined.outcome = child.outcome
                        combined.status = child.status
                    combined.total_count = len(combined.records) if all_complete else None
                    combined.issues = list(dict.fromkeys(combined.issues))
                    if not all_complete:
                        note = "Only sampled parents/subresources were inspected; unknown is not zero."
                        if note not in combined.issues:
                            combined.issues.append(note)

                stop_kind = False
                try:
                    while True:
                        more = self._page(child, spec, self.options.max_child_records)
                        for row in child.records[copied_count:]:
                            combined.records.append({**row, "_parent_id": parent_id})
                        copied_count = len(child.records)
                        combined.pages += child.pages - copied_pages
                        copied_pages = child.pages
                        combined.read_attempted = child.read_attempted or combined.read_attempted
                        if not more:
                            finish_parent()
                            stop_kind = child.outcome in {"PERMISSION_DENIED", "PORTAL_NOT_ACCESSIBLE", "PORTAL_CONTEXT_REQUIRED",
                                                          "MODULE_NOT_ENABLED", "MODULE_NOT_AVAILABLE", "RATE_LIMITED", "ENDPOINT_UNSUPPORTED"}
                            if stop_kind:
                                all_complete = False
                            if parent_index == len(chosen) - 1 or stop_kind:
                                # Commit final coverage before yielding: another
                                # portal may exhaust the global budget next.
                                finish_collection()
                        self._progress(event="children", key=key, parents=visited if not more else visited + 1,
                                       records=len(combined.records))
                        yield None
                        if not more:
                            break
                finally:
                    # Preserve successfully read child pages even if the next
                    # request reaches a budget, fails auth, or is interrupted.
                    finish_parent()
                self._progress(event="children", key=key, parents=visited, records=len(combined.records))
                if stop_kind:
                    break
            if not chosen:
                combined.status, combined.outcome = "not_attempted", "NOT_STARTED"
                combined.issues.append("No sampled parent had a usable numeric identifier; child count unknown.")

    def _request_children(self, snapshot: Snapshot) -> None:
        for _ in self.child_steps(snapshot):
            pass

    def prepare(self, snapshot: Snapshot) -> None:
        for spec in self.resources:
            snapshot.datasets[spec.key] = Dataset(
                spec.key, spec.path, doc_url=spec.doc_url,
                portal_id=snapshot.source.get("portal_id"), portal_name=snapshot.source.get("portal_name"),
                module=spec.module or spec.key, scope=spec.scope,
                outcome="NOT_STARTED",
            )

    def read_page(self, snapshot: Snapshot, key: str) -> bool:
        dataset = snapshot.datasets[key]
        more = self._page(dataset, self._specs[key])
        self._progress(event="collection", key=key, records=len(dataset.records),
                       status=dataset.status, outcome=dataset.outcome, more_pages=more,
                       pages=dataset.pages, api_reported_total=dataset.total_count,
                       issues=list(dataset.issues), scope=dataset.scope,
                       portal_id=dataset.portal_id, portal_name=dataset.portal_name)
        return more

    def collect(self, snapshot: Snapshot) -> Snapshot:
        max_requests = int(snapshot.settings.get("max_requests", 500))
        inventory_budget = max(len(self.resources), math.floor(max_requests * self.options.inventory_budget_fraction))
        queue = deque()
        self.prepare(snapshot)
        for spec in self.resources:
            queue.append(spec.key)
        try:
            self._progress(event="phase", phase="inventory")
            while queue:
                used = int(self.client.stats.get("requests", 0))
                if used >= inventory_budget:
                    for key in queue:
                        ds = snapshot.datasets[key]
                        if ds.records:
                            ds.status = "partial"
                        ds.issues.append("Inventory budget reserved remaining requests for detail inspection.")
                    self._progress(event="budget_reservation", collections=len(queue),
                                   remaining_requests=max(0, max_requests - used))
                    break
                key = queue.popleft()
                more = self.read_page(snapshot, key)
                if more:
                    queue.append(key)
            # Inspect note/task metadata before the broader detail phase so these
            # migration exclusions receive some evidence even in large instances.
            self._progress(event="phase", phase="children")
            self._request_children(snapshot)
            self._progress(event="phase", phase="details")
            self._details(snapshot)
        except BudgetExceeded:
            snapshot.interrupted_reason = "Configured request/time budget reached; report is partial."
        except ApiError as error:
            snapshot.interrupted_reason = "Collection stopped: " + error.kind + ". Credentials and responses are not saved."
        except KeyboardInterrupt:
            snapshot.interrupted_reason = "Interrupted by user; collected evidence preserved in this partial report."
        finally:
            snapshot.stats = dict(self.client.stats)
            if snapshot.interrupted_reason:
                for ds in snapshot.datasets.values():
                    if not ds.list_complete:
                        if ds.records:
                            ds.status = "partial"
                        ds.issues.append(snapshot.interrupted_reason)
                        ds.issues = list(dict.fromkeys(ds.issues))
        return snapshot
