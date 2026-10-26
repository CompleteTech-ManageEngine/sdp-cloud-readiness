"""Shared plain-data contracts. No network or filesystem side effects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ResourceSpec:
    key: str
    path: str
    plural: str
    singular: str
    doc_url: str
    kind: str = "records"
    detail: bool = True
    paginated: bool = True
    search_fields: dict[str, Any] = field(default_factory=dict)
    list_info_extras: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    scope: str = "portal"
    module: str = ""


@dataclass
class Dataset:
    key: str
    endpoint: str
    records: list[dict[str, Any]] = field(default_factory=list)
    details: list[dict[str, Any]] = field(default_factory=list)
    total_count: int | None = None
    status: str = "not_attempted"
    pages: int = 0
    list_complete: bool = False
    detail_attempted: int = 0
    detail_succeeded: int = 0
    issues: list[str] = field(default_factory=list)
    doc_url: str = ""
    sampling: str = "bounded list; details selected across observed records"
    portal_id: str | None = None
    portal_name: str | None = None
    module: str | None = None
    scope: str = "portal"
    outcome: str | None = None
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    stop_reason: str | None = None
    detail_complete: bool | None = None
    capability: str = "UNKNOWN"
    read_attempted: bool = False
    last_response: dict[str, Any] = field(default_factory=dict)
    total_count_page: int | None = None

    def coverage(self) -> dict[str, Any]:
        observed = len(self.records) if self.records or self.pages or self.list_complete else None
        result = {
            "key": self.key,
            "endpoint": self.endpoint,
            "status": self.status,
            "records_examined": len(self.records),
            "api_reported_total": self.total_count,
            "api_reported_total_page": self.total_count_page,
            "pages": self.pages,
            "list_complete_for_api_scope": self.list_complete,
            "details_attempted": self.detail_attempted,
            "details_examined": self.detail_succeeded,
            "issues": list(self.issues),
            "sampling": self.sampling,
            "source": self.doc_url,
        }
        if self.portal_id is not None or self.scope == "environment" or self.outcome is not None:
            result.update({
                "portal_id": self.portal_id, "portal_name": self.portal_name,
                "module": self.module or self.key, "scope": self.scope,
                "outcome": self.outcome or self.status.upper(),
                "records_observed": observed, "pages_observed": self.pages,
                "list_complete": self.list_complete, "detail_complete": self.detail_complete,
                "detail_records_attempted": self.detail_attempted,
                "detail_records_successful": self.detail_succeeded,
                "diagnostics": list(self.diagnostics), "stop_reason": self.stop_reason,
                "http_status": self.last_response.get("http_status"),
                "api_codes": self.last_response.get("api_codes", []),
                "last_response": dict(self.last_response),
                "capability": self.capability, "read_attempted": self.read_attempted,
                "confidence": "API_VISIBLE_LIST" if self.list_complete else "PARTIAL_EVIDENCE" if observed else "UNRESOLVED",
            })
        return result


@dataclass
class Snapshot:
    generated_at: str
    source: dict[str, Any]
    settings: dict[str, Any]
    datasets: dict[str, Dataset] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    manual_answers: dict[str, Any] = field(default_factory=dict)
    interrupted_reason: str | None = None
    schema_version: str = "1.0"
    fields: dict[str, Any] = field(default_factory=dict)
    capabilities: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class Finding:
    id: str
    title: str
    category: str
    severity: str
    status: str
    summary: str
    affected_count: int | None = None
    examined_count: int = 0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    action: str = ""
    sources: list[str] = field(default_factory=list)
    coverage: str = "API-visible observations only; not an organization-wide certification"
    scope: str = "portal"
    portal_id: str | None = None
    portal_name: str | None = None
    module: str | None = None
    evidence_basis: str = "SOURCE_OBSERVATION"


@dataclass
class Assessment:
    generated_at: str
    source: dict[str, Any]
    settings: dict[str, Any]
    findings: list[Finding]
    questions: list[dict[str, Any]]
    coverage: list[dict[str, Any]]
    stats: dict[str, Any]
    sources: dict[str, dict[str, str]]
    notes: list[str] = field(default_factory=list)
    schema_version: str = "1.0"
    environment: dict[str, Any] = field(default_factory=dict)
    portals: list[dict[str, Any]] = field(default_factory=list)
    global_resources: dict[str, Any] = field(default_factory=dict)
    field_inventory: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PortalInfo:
    id: str
    name: str
    instance_type: str | None = None
    state: str | None = None
    active: bool | None = None
    edition: str | None = None
    discovery_endpoint: str | None = None
    discovery_source: str | None = None
    discovered: bool = True
    selected: bool = True
    accessible: bool | None = None
    access_status: str = "UNKNOWN"
    scan_status: str = "NOT_STARTED"
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class Topology:
    portals: list[PortalInfo] = field(default_factory=list)
    outcome: str = "NOT_STARTED"
    complete: bool = False
    mode: str = "automatic"
    endpoint: str = "/portals"
    source: str = ""
    pages: int = 0
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    credential_scope: str = "integration_key"
    selection_source: str = "automatic"
    directory_outcome: str | None = None


@dataclass
class PortalSnapshot:
    portal: PortalInfo
    snapshot: Snapshot


@dataclass
class EnvironmentSnapshot:
    generated_at: str
    source: dict[str, Any]
    settings: dict[str, Any]
    topology: Topology = field(default_factory=Topology)
    portals: dict[str, PortalSnapshot] = field(default_factory=dict)
    global_snapshot: Snapshot | None = None
    manual_answers: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)
    interrupted_reason: str | None = None
    stop_classification: str | None = None
    authentication: str = "UNKNOWN"
    schema_version: str = "2.0"
    retained_portals: dict[str, dict[str, Any]] = field(default_factory=dict)
    retained_global_coverage: list[dict[str, Any]] = field(default_factory=list)
    resume_history: list[dict[str, Any]] = field(default_factory=list)
