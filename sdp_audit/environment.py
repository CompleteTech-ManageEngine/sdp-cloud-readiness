"""Environment-wide portal orchestration using one read-only transport.

PortalClient is a context view, not an HTTP client: every operation goes through
the same ReadOnlyClient, lock, pacing clock, retry policy and attempt budget.
Records remain in their portal until the reporting layer computes rollups.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from .catalog import FALLBACKS, GLOBAL_RESOURCES, RESOURCES
from .collect import CollectionOptions, Collector
from .fields import FieldDiscovery
from .models import EnvironmentSnapshot, PortalInfo, PortalSnapshot, ResourceSpec, Snapshot, Topology
from .topology import discover_topology
from .transport import ApiError, BudgetExceeded


_TERMINAL_STOPS = {"REQUEST_BUDGET_REACHED", "TIME_BUDGET_REACHED",
                   "AUTHENTICATION_FAILED", "INTERRUPTED"}
_REASONS = {
    "REQUEST_BUDGET_REACHED": "Global HTTP attempt budget reached; collected evidence was preserved.",
    "TIME_BUDGET_REACHED": "Global time budget reached; collected evidence was preserved.",
    "AUTHENTICATION_FAILED": "Integration-key authentication failed; collected evidence was preserved.",
    "INTERRUPTED": "Interrupted by user; collected evidence was preserved.",
}


class PortalClient:
    """An explicit PORTALID view of the single environment scheduler."""

    def __init__(self, shared: Any, portal: PortalInfo, resources: list[ResourceSpec]):
        self.shared = shared
        self.portal_id = portal.id
        self.portal_name = portal.name
        self._resources = sorted(resources + [item for values in FALLBACKS.values() for item in values],
                                 key=lambda spec: len(spec.path), reverse=True)

    @property
    def stats(self) -> dict[str, Any]:
        return self.shared.stats

    @property
    def last_response(self) -> dict[str, Any]:
        return getattr(self.shared, "last_response", {})

    def get_json(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        spec = next((item for item in self._resources
                     if path == item.path or path.startswith(item.path + "/")), None)
        name = spec.key if spec else "request_subresources"
        module = (spec.module or spec.key) if spec else "requests"
        return self.shared.get_json(path, params, portal_id=self.portal_id,
                                    endpoint_name=name, module=module)

    def get_resource_json(self, spec: ResourceSpec, path: str,
                          params: dict[str, str] | None = None) -> dict[str, Any]:
        name = spec.key.split(":", 1)[0]
        module = spec.module or ("requests" if name.startswith("request_") else name)
        return self.shared.get_json(path, params, portal_id=self.portal_id,
                                    endpoint_name=name, module=module)


@dataclass
class EnvironmentOptions:
    max_portals: int = 100
    metadata_limit: int = 20
    discover_fields: bool = True
    collect_orgusers: bool = True
    diagnose_only: bool = False


class EnvironmentCollector:
    """Discover topology, probe capabilities, then fairly page and sample."""

    def __init__(self, client: Any, resources: list[ResourceSpec] | None = None,
                 collection_options: CollectionOptions | None = None,
                 environment_options: EnvironmentOptions | None = None,
                 progress: Callable[[dict[str, Any]], None] | None = None,
                 scope_resolver: Callable[..., Any] | None = None):
        self.scope_resolver = scope_resolver
        self.client = client
        self.resources = list(RESOURCES if resources is None else resources)
        self.options = collection_options or CollectionOptions()
        self.env_options = environment_options or EnvironmentOptions()
        self.progress = progress or (lambda event: None)
        self.collectors: dict[str, Collector] = {}
        self.field_discoveries: dict[str, FieldDiscovery] = {}
        self._generators: list[Iterator[Any]] = []

    def _event(self, **event: Any) -> None:
        event.setdefault("requests", self.client.stats.get("requests", 0))
        event.setdefault("elapsed_seconds", self.client.stats.get("elapsed_seconds", 0))
        self.progress(event)

    @staticmethod
    def _capabilities(item: PortalSnapshot) -> None:
        grouped: dict[str, list[Any]] = {}
        for dataset in item.snapshot.datasets.values():
            if dataset.key in {"request_notes", "request_tasks"}:
                continue
            grouped.setdefault(dataset.module or dataset.key, []).append(dataset)
            if dataset.pages or dataset.list_complete:
                dataset.capability = "AVAILABLE"
            elif dataset.outcome in {"MODULE_NOT_AVAILABLE", "MODULE_NOT_ENABLED", "ENDPOINT_UNSUPPORTED",
                                     "API_VERSION_INCOMPATIBLE", "PERMISSION_DENIED", "PORTAL_NOT_ACCESSIBLE",
                                     "PORTAL_CONTEXT_REQUIRED"}:
                dataset.capability = dataset.outcome
        for module, datasets in grouped.items():
            values = {dataset.capability for dataset in datasets}
            available = "AVAILABLE" if "AVAILABLE" in values else next(iter(values)) if len(values) == 1 else "UNKNOWN"
            item.snapshot.capabilities[module] = {
                "module": module, "portal_id": item.portal.id, "portal_name": item.portal.name,
                "availability": available,
                "discovery_method": "documented_inventory_first_page_reused",
                "operations": [{"resource": ds.key, "endpoint": ds.endpoint,
                                "status": ds.outcome or "NOT_STARTED", "capability": ds.capability}
                               for ds in datasets],
                "limitation": "No documented whole-portal module registry was verified. A denied or unsupported operation alone does not establish module licensing.",
            }

    @staticmethod
    def _access(item: PortalSnapshot) -> None:
        datasets = list(item.snapshot.datasets.values())
        explicit = [diag for ds in datasets for diag in ds.diagnostics
                    if diag.get("classification") == "PORTAL_NOT_ACCESSIBLE"]
        field_values = list(item.snapshot.fields.values())
        explicit += [diag for inventory in field_values for diag in inventory.diagnostics
                     if diag.get("classification") == "PORTAL_NOT_ACCESSIBLE"]
        success = (any(ds.pages or ds.list_complete for ds in datasets)
                   or any(inventory.metadata_targets_successful for inventory in field_values))
        if explicit:
            item.portal.accessible = False
            item.portal.access_status = "PORTAL_NOT_ACCESSIBLE"
            for diagnostic in explicit:
                if diagnostic not in item.portal.diagnostics:
                    item.portal.diagnostics.append(diagnostic)
        elif success:
            item.portal.accessible = True
            item.portal.access_status = "ACCESSIBLE_WITH_OPERATION_SPECIFIC_VISIBILITY"
        elif any(ds.read_attempted for ds in datasets):
            item.portal.access_status = "NO_SUCCESSFUL_SCOPED_READ"
        # Discovery-only visibility must never be promoted to operational access.

    def _read(self, env: EnvironmentSnapshot, portal_id: str, key: str) -> bool:
        item = env.portals[portal_id]
        if item.portal.accessible is False:
            return False
        item.portal.scan_status = "COLLECTING"
        try:
            more = self.collectors[portal_id].read_page(item.snapshot, key)
        except ApiError as error:
            if not getattr(self.client, "multi_key", False) or error.kind != "authentication":
                raise
            self._credential_gap(item, "AUTHENTICATION_FAILED")
            return False
        self._access(item)
        self._capabilities(item)
        return more

    @staticmethod
    def _credential_gap(item: PortalSnapshot, reason: str) -> None:
        item.portal.access_status = reason
        for dataset in item.snapshot.datasets.values():
            if not dataset.list_complete:
                # Preserve an earlier operation-specific failure and its history.
                if dataset.outcome in {None, "NOT_STARTED", "COLLECTING", "INCOMPLETE"}:
                    dataset.outcome = reason
                    dataset.status = "not_attempted" if not dataset.read_attempted else "partial"
                    dataset.stop_reason = reason
                note = "Credential coverage gap: " + reason + ". No absence was inferred."
                if note not in dataset.issues:
                    dataset.issues.append(note)

    def _credential_ready(self, item: PortalSnapshot) -> bool:
        if not getattr(self.client, "multi_key", False):
            return True
        status = self.client.credential_status(item.portal.id)
        if status in {"missing", "failed"}:
            self._credential_gap(item, "CREDENTIAL_MISSING" if status == "missing" else "AUTHENTICATION_FAILED")
            return False
        return True

    def _global_read(self, work: tuple[Collector, Snapshot]) -> bool:
        try:
            return work[0].read_page(work[1], "orgusers")
        except ApiError as error:
            if not getattr(self.client, "multi_key", False) or error.kind != "authentication":
                raise
            return False

    def _global_directory(self, env: EnvironmentSnapshot) -> tuple[Collector, Snapshot] | None:
        if not self.env_options.collect_orgusers:
            env.source["orgusers_collection"] = "not_selected"
            return None
        multi_key = getattr(self.client, "multi_key", False)
        if env.topology.mode == "explicit" and not multi_key:
            env.source["orgusers_collection"] = "not_collected_for_explicit_portal_targeting"
            return None
        if len(env.portals) <= 1:
            env.source["orgusers_collection"] = "multiple_instances_not_observed"
            return None
        if multi_key:
            context_id = self.client.global_portal_id
            if context_id is None:
                env.source["orgusers_collection"] = "credential_missing"
                snapshot = Snapshot(env.generated_at, {**env.source, "portal_id": None}, env.settings,
                                    schema_version="2.0")
                Collector(self.client, GLOBAL_RESOURCES, self.options).prepare(snapshot)
                for dataset in snapshot.datasets.values():
                    dataset.outcome = dataset.stop_reason = "CREDENTIAL_MISSING"
                    dataset.issues.append("No explicit global credential and request context were assigned.")
                env.global_snapshot = snapshot
                return None
            context = PortalInfo(id=context_id, name="Explicit global request context")
        else:
            context = next((item.portal for item in env.portals.values() if item.portal.accessible is True), None)
        if context is None and not self.resources:
            context = next((item.portal for item in env.portals.values() if item.portal.accessible is not False), None)
        if context is None:
            env.source["orgusers_collection"] = "no_accessible_portal_context_confirmed"
            return None
        # Scope is environment; PORTALID is only the request context required by
        # the documented example. It is not a new allowance or another copy.
        source = {**env.source, "portal_id": None, "portal_name": None,
                  "request_context_portal_id": context.id}
        snapshot = Snapshot(env.generated_at, source, env.settings, manual_answers=env.manual_answers,
                            schema_version="2.0")
        view = PortalClient(self.client, context, GLOBAL_RESOURCES)
        collector = Collector(view, GLOBAL_RESOURCES, self.options, progress=self.progress)
        collector.prepare(snapshot)
        env.global_snapshot = snapshot
        env.source["orgusers_collection"] = "once_for_environment"
        return collector, snapshot

    def _finalize(self, env: EnvironmentSnapshot) -> None:
        stop = env.stop_classification
        for iterator in self._generators:
            try:
                iterator.close()
            except (RuntimeError, ValueError):
                pass
        for portal_id, field_discovery in self.field_discoveries.items():
            if stop:
                field_discovery.stop(stop)
            elif (getattr(self.client, "multi_key", False)
                  and self.client.credential_status(portal_id) == "failed"):
                field_discovery.stop("AUTHENTICATION_FAILED")
            field_discovery.refresh_observed_keys()
        snapshots = [item.snapshot for item in env.portals.values()]
        if env.global_snapshot:
            snapshots.append(env.global_snapshot)
        for snapshot in snapshots:
            snapshot.interrupted_reason = env.interrupted_reason
            for dataset in snapshot.datasets.values():
                if dataset.list_complete:
                    # A global stop during details never undoes an exhausted list.
                    if dataset.detail_complete is None:
                        dataset.detail_complete = not dataset.records
                    continue
                if dataset.outcome in {None, "NOT_STARTED"}:
                    dataset.outcome = "NOT_STARTED"
                    dataset.status = "not_attempted"
                    dataset.stop_reason = stop or dataset.stop_reason
                elif dataset.outcome == "COLLECTING":
                    dataset.outcome = "INCOMPLETE"
                    dataset.status = "partial"
                    dataset.stop_reason = stop or dataset.stop_reason or "SAMPLING_RESERVATION"
                if stop and dataset.outcome in {"NOT_STARTED", "INCOMPLETE"}:
                    note = _REASONS.get(stop, "Collection stopped before all planned reads finished.")
                    if note not in dataset.issues:
                        dataset.issues.append(note)
                if dataset.detail_complete is None:
                    dataset.detail_complete = False
        for item in env.portals.values():
            self._access(item)
            credential_ready = self._credential_ready(item)
            self._capabilities(item)
            datasets = list(item.snapshot.datasets.values())
            if not credential_ready:
                item.portal.scan_status = item.portal.access_status
            elif item.portal.accessible is False:
                item.portal.scan_status = "PORTAL_NOT_ACCESSIBLE"
                for ds in datasets:
                    if ds.outcome == "NOT_STARTED":
                        ds.stop_reason = "PORTAL_NOT_ACCESSIBLE"
            elif not any(ds.read_attempted for ds in datasets) and not item.snapshot.fields:
                item.portal.scan_status = "NOT_STARTED"
            elif all(ds.list_complete for ds in datasets) and datasets:
                item.portal.scan_status = "LISTS_COMPLETE_DETAILS_BOUNDED"
            else:
                item.portal.scan_status = "ASSESSED_WITH_COVERAGE_GAPS"
            item.snapshot.stats = {"scope": "portal", "portal_id": item.portal.id,
                                   "global_budget_applies": True,
                                   "requests": self.client.stats.get("requests_by_scope", {}).get("portal:" + item.portal.id, 0)}
        env.stats = dict(self.client.stats)
        if getattr(self.client, "multi_key", False):
            env.stats["credential_coverage"]["portals"] = {
                pid: self.client.credential_status(pid) for pid in env.portals}
        env.authentication = str(env.stats.get("authentication", "unverified")).upper()
        env.stats["portals_discovered"] = sum(portal.discovered for portal in env.topology.portals)
        env.stats["portals_selected"] = len(env.portals)
        env.stats["portals_with_successful_scoped_reads"] = sum(item.portal.accessible is True for item in env.portals.values())
        env.stats["portals_with_attempted_assessment"] = sum(any(ds.read_attempted for ds in item.snapshot.datasets.values())
                                                            for item in env.portals.values())
        env.stats["global_limiter_instances"] = 1
        env.stats["stop_classification"] = stop

    def collect(self, env: EnvironmentSnapshot, portal_ids: list[str] | None = None, *,
                topology: Topology | None = None) -> EnvironmentSnapshot:
        queue: deque[tuple[str, str]] = deque()
        global_work: tuple[Collector, Snapshot] | None = None
        global_more = False
        try:
            if self.env_options.diagnose_only:
                # Establish the boundary before invoking an optional resolver,
                # including for library callers that do not use cli.main().
                env.settings["diagnose_only"] = True
                env.source["diagnostic_only"] = True
            self._event(event="phase", phase="topology")
            env.topology = topology if topology is not None else discover_topology(self.client, portal_ids=portal_ids,
                                             page_size=self.options.page_size,
                                             max_portals=self.env_options.max_portals,
                                             progress=self.progress)
            if (getattr(self.client, "multi_key", False)
                    and not self.env_options.diagnose_only
                    and env.topology.outcome == "AUTHENTICATION_FAILED"):
                env.topology.directory_outcome = env.topology.outcome
                env.topology.outcome = "INCOMPLETE"
            if topology is None and self.scope_resolver is not None and env.topology.outcome not in _TERMINAL_STOPS:
                env.topology = self.scope_resolver(env.topology, env)
            for portal in env.topology.portals:
                if not portal.selected:
                    continue
                source = {**env.source, "portal_id": portal.id, "portal_name": portal.name,
                          "portal_type": portal.instance_type, "edition": portal.edition}
                snapshot = Snapshot(env.generated_at, source, env.settings, manual_answers=env.manual_answers,
                                    schema_version="2.0")
                env.portals[portal.id] = PortalSnapshot(portal, snapshot)
                view = PortalClient(self.client, portal, self.resources)
                collector = Collector(view, self.resources, self.options, fallbacks=FALLBACKS,
                                      progress=self.progress)
                self.collectors[portal.id] = collector
                collector.prepare(snapshot)
            self._event(event="topology_complete", portals=len(env.portals), outcome=env.topology.outcome,
                        complete=env.topology.complete, mode=env.topology.mode, credential_scope=env.topology.credential_scope)
            if env.topology.outcome in _TERMINAL_STOPS:
                env.stop_classification = env.topology.outcome
                env.interrupted_reason = _REASONS[env.stop_classification]
                return env
            if not env.portals:
                env.stop_classification = "PORTAL_DISCOVERY_UNAVAILABLE" if not env.topology.complete else "NO_VISIBLE_PORTALS"
                env.interrupted_reason = ("No portal could be selected from discovery. Supply explicit --portal-id values obtained from your administrator; no default ID was assumed."
                                          if not env.topology.complete else "The directory returned no portals visible to this key; no portal inventory was queried.")
                return env

            if self.env_options.diagnose_only:
                env.settings["diagnose_only"] = True
                env.source["diagnostic_only"] = True
                # Discovery only: preserve selected IDs without querying a
                # single portal module or pretending that it is assessed.
                return env

            self._event(event="phase", phase="capabilities")
            for index, item in enumerate(env.portals.values(), 1):
                self._event(event="portal", portal_id=item.portal.id, portal_name=item.portal.name,
                            index=index, total=len(env.portals))
            # A documented first list page is the capability probe and is kept.
            # Resource-then-portal order prevents one large portal monopolising
            # all first-page attempts. Subsequent pages use their own cursors.
            for resource in self.resources:
                for portal_id in env.portals:
                    if not self._credential_ready(env.portals[portal_id]):
                        continue
                    if self._read(env, portal_id, resource.key):
                        queue.append((portal_id, resource.key))
            global_work = self._global_directory(env)
            if global_work:
                global_more = self._global_read(global_work)

            self._event(event="phase", phase="inventory")
            used = int(self.client.stats.get("requests", 0))
            maximum = int(env.settings.get("max_requests", self.client.stats.get("max_requests", 500)))
            inventory_budget = max(used, math.floor(maximum * self.options.inventory_budget_fraction))
            while queue or global_more:
                if int(self.client.stats.get("requests", 0)) >= maximum:
                    raise BudgetExceeded("Global HTTP attempt budget reached while list pages remain queued.",
                                         reason="REQUEST_BUDGET_REACHED")
                if int(self.client.stats.get("requests", 0)) >= inventory_budget:
                    for portal_id, key in queue:
                        ds = env.portals[portal_id].snapshot.datasets[key]
                        ds.stop_reason = "SAMPLING_RESERVATION"
                        ds.issues.append("Inventory budget reserved remaining requests for field and detail inspection.")
                    if global_more and global_work:
                        ds = global_work[1].datasets["orgusers"]
                        ds.stop_reason = "SAMPLING_RESERVATION"
                        ds.issues.append("Inventory budget reserved remaining requests for field and detail inspection.")
                    self._event(event="budget_reservation", collections=len(queue) + int(global_more),
                                remaining_requests=max(0, maximum - int(self.client.stats.get("requests", 0))))
                    break
                if queue:
                    portal_id, key = queue.popleft()
                    if self._credential_ready(env.portals[portal_id]) and self._read(env, portal_id, key):
                        queue.append((portal_id, key))
                if global_more and global_work:
                    global_more = self._global_read(global_work)

            self._event(event="phase", phase="sampling")
            pending: deque[tuple[str, Iterator[Any]]] = deque()
            for portal_id, item in env.portals.items():
                if item.portal.accessible is False or not self._credential_ready(item):
                    continue
                if self.env_options.discover_fields:
                    field_discovery = FieldDiscovery(self.client, portal_id, item.portal.name,
                                                     item.snapshot.datasets,
                                                     metadata_limit=self.env_options.metadata_limit,
                                                     source_build=env.manual_answers.get("source_build"))
                    self.field_discoveries[portal_id] = field_discovery
                    item.snapshot.fields = field_discovery.inventories
                    pending.append((portal_id, field_discovery.iter_steps()))
            # Interleave kinds as well as portals: metadata and notes cannot use
            # the whole remaining budget before another portal gets a sample.
            for kind in ("detail_steps", "child_steps"):
                for portal_id, item in env.portals.items():
                    if item.portal.accessible is not False and self._credential_ready(item):
                        pending.append((portal_id, getattr(self.collectors[portal_id], kind)(item.snapshot)))
            self._generators = [iterator for _, iterator in pending]
            while pending:
                portal_id, iterator = pending.popleft()
                item = env.portals[portal_id]
                if item.portal.accessible is False or not self._credential_ready(item):
                    iterator.close()
                    continue
                try:
                    event = next(iterator)
                    if isinstance(event, dict):
                        self._event(**event)
                    self._access(item)
                    pending.append((portal_id, iterator))
                except StopIteration:
                    self._access(item)
                except ApiError as error:
                    if not getattr(self.client, "multi_key", False) or error.kind != "authentication":
                        raise
                    self._credential_gap(item, "AUTHENTICATION_FAILED")
        except BudgetExceeded as error:
            env.stop_classification = error.reason
            env.interrupted_reason = _REASONS.get(error.reason, "Global collection budget reached.")
        except ApiError as error:
            env.stop_classification = error.classification
            env.interrupted_reason = _REASONS.get(error.classification, "A read prevented further collection; existing evidence was preserved.")
        except KeyboardInterrupt:
            env.stop_classification = "INTERRUPTED"
            env.interrupted_reason = _REASONS["INTERRUPTED"]
        finally:
            self._finalize(env)
            try:
                self._event(event="phase", phase="analysis")
            except KeyboardInterrupt:
                env.stop_classification = "INTERRUPTED"
                env.interrupted_reason = _REASONS["INTERRUPTED"]
                env.stats["stop_classification"] = "INTERRUPTED"
                for item in env.portals.values():
                    item.snapshot.interrupted_reason = env.interrupted_reason
        return env


def collect_environment(client: Any, env: EnvironmentSnapshot, *, portal_ids: list[str] | None = None,
                        resources: list[ResourceSpec] | None = None,
                        collection_options: CollectionOptions | None = None,
                        environment_options: EnvironmentOptions | None = None,
                        progress: Callable[[dict[str, Any]], None] | None = None) -> EnvironmentSnapshot:
    return EnvironmentCollector(client, resources, collection_options, environment_options,
                                progress).collect(env, portal_ids)
