"""Portal-scoped field metadata with documented, bounded read strategies.

Only normalized schema attributes and measurements survive a response. Defaults,
option labels, scripts, descriptions and lookup URLs are deliberately discarded.
The supplied client owns the *environment-wide* scheduler and attempt budgets.
Every iteration performs at most one get_json call, allowing portal fairness.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterator, Mapping

from .transport import ApiError, BudgetExceeded
from .response_contract import shape_evidence


REQUEST_DOC = "https://www.manageengine.com/products/service-desk/on-premises/custom-help-desk-ticket-templates.html"
CHANGE_DOC = "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/j6u4ac3/meta-info-for-change-add"
ASSET_DOC = "https://help.servicedeskplus.com/asset-api-changes"
CMDB_DOC = "https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison"
LEGACY_ASSET_DOC = "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/hdso1p4/get-asset-metainfo"
LEGACY_COMPUTER_DOC = "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/13rvw6m/get-workstation-metainfo"
DEPARTMENT_DOC = "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/iq99xoi/metainfo-of-department-entity"
SPACE_DOCS = {
    "space_campus": "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/ixteupg/view-all-campus-additional-fields",
    "space_structure": "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/xm13aa9/view-all-structure-additional-fields",
    "space_floor": "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/7t73i18/view-all-floor-additional-fields",
    "space_room": "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/7x397b8/view-all-room-additional-fields",
}
_FIELD_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,127}")
_ASSET_API = re.compile(r"(?:asset_[a-z][a-z0-9_]{0,90}|custom_asset_[a-z0-9_]{1,90})")
_CMDB_API = re.compile(r"cmdb(?:_[a-z0-9_]{1,100})?")
_EMAIL = re.compile(r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_HTML = re.compile(r"<[^>]*>")
_UDF_CONTAINERS = {"udf_fields", "user_udf_fields", "workstation_udf_fields"}
_OPTION_SPECIAL = frozenset("`~#%^&*()=+?[]{}|;\"")
_COMPATIBILITY_FAILURES = {
    "ENDPOINT_UNSUPPORTED", "API_VERSION_INCOMPATIBLE", "PARSE_ERROR", "INVALID_QUERY",
}
_UNAVAILABLE = {"MODULE_NOT_ENABLED", "MODULE_NOT_AVAILABLE", "PORTAL_NOT_ACCESSIBLE"}
_CORE_MODULES = ("requests", "problems", "changes", "projects", "releases", "users",
                 "technicians", "assets", "computers", "cis", "contracts", "purchases")


def _text(value: Any, limit: int = 250) -> str | None:
    if not isinstance(value, str):
        return None
    value = _EMAIL.sub("[email omitted]", _HTML.sub("", value))
    value = " ".join(value.split())
    return value[:limit] or None


def _identifier(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    value = str(value) if isinstance(value, (int, str)) else ""
    return value if re.fullmatch(r"[0-9]{1,40}", value) else None


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if 0 <= value <= 10**18 else None
    if isinstance(value, str) and re.fullmatch(r"[0-9]{1,19}", value):
        number = int(value)
        return number if number <= 10**18 else None
    return None


def _boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


def _get(dataset: Any, key: str, default: Any = None) -> Any:
    if isinstance(dataset, Mapping):
        return dataset.get(key, default)
    return getattr(dataset, key, default)


def _rows(dataset: Any) -> Iterator[dict[str, Any]]:
    for source in ("records", "details"):
        rows = _get(dataset, source, ())
        if isinstance(rows, (list, tuple)):
            yield from (row for row in rows if isinstance(row, dict))


def _sample(items: list[Any], limit: int) -> list[Any]:
    if limit == 0 or len(items) <= limit:
        return items
    if limit == 1:
        return items[:1]
    return [items[round(i * (len(items) - 1) / (limit - 1))] for i in range(limit)]


@dataclass
class FieldDefinition:
    internal_name: str
    field_path: str
    portal_id: str
    portal_name: str
    module: str
    field_id: str | None = None
    display_label: str | None = None
    data_type: str | None = None
    display_type: str | None = None
    maximum_length: int | None = None
    allowed_value_count: int | None = None
    mandatory: bool | None = None
    read_only: bool | None = None
    custom: bool | None = None
    is_additional: bool = False
    is_encrypted: bool | None = None
    is_pii: bool | None = None
    metadata_source: str = ""
    sources: list[str] = field(default_factory=list)
    contexts: list[dict[str, str]] = field(default_factory=list)
    evidence_basis: str = "API_METADATA"
    completeness: str = "FORM_SCOPE"
    default_character_count: int | None = None
    default_digit_count: int | None = None
    maximum_option_character_count: int | None = None
    options_with_unsupported_characters: int | None = None
    options_with_only_unsupported_characters: int | None = None
    constraint_variants: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FieldInventory:
    module: str
    portal_id: str
    portal_name: str
    status: str = "NOT_SCANNED"
    fields: list[FieldDefinition] = field(default_factory=list)
    metadata_targets_total: int = 0
    metadata_targets_attempted: int = 0
    metadata_targets_successful: int = 0
    http_attempts: int = 0
    registry_complete: bool = False
    form_scope_complete: bool = False
    completeness: str = "UNKNOWN"
    evidence_basis: str = "UNKNOWN"
    sources: list[str] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        known_observations = bool(self.fields) or bool(self.metadata_targets_successful)
        result["fields_observed"] = len(self.fields) if known_observations else None
        result["additional_fields_observed"] = sum(item.is_additional for item in self.fields) if known_observations else None
        result["builtin_fields_observed"] = sum(not item.is_additional for item in self.fields) if known_observations else None
        result["unknown_origin_fields_observed"] = sum(item.custom is None for item in self.fields) if known_observations else None
        return result

    def add(self, new: FieldDefinition) -> None:
        # Definitions recur in multiple templates/product-type layouts. IDs are
        # scoped to a holder because legacy providers reuse numeric IDs.
        namespace = new.field_path.rpartition(".")[0]
        for index, old in enumerate(self.fields):
            same_id = (old.field_id is not None and old.field_id == new.field_id
                       and old.field_path.rpartition(".")[0] == namespace)
            if old.field_path != new.field_path and not same_id:
                continue
            original_contexts = list(old.contexts)
            contexts = old.contexts + [c for c in new.contexts if c not in old.contexts]
            sources = old.sources + [s for s in new.sources if s not in old.sources]
            if old.evidence_basis == "INFERRED_FROM_OBSERVED_UDF_KEY" and new.evidence_basis == "API_METADATA":
                new.contexts, new.sources = contexts, sources
                self.fields[index] = new
            else:
                old.contexts, old.sources = contexts, sources
                # Constraints can differ by layout; retain this as an explicit
                # conflict rather than silently selecting one as universal.
                if (old.evidence_basis == new.evidence_basis == "API_METADATA"
                        and any(getattr(old, key) != getattr(new, key)
                                for key in ("data_type", "display_type", "maximum_length", "mandatory", "read_only"))):
                    keys = ("data_type", "display_type", "maximum_length", "mandatory", "read_only")
                    if not old.constraint_variants:
                        old.constraint_variants.append({**{key: getattr(old, key) for key in keys},
                                                        "contexts": original_contexts})
                    variant = {**{key: getattr(new, key) for key in keys}, "contexts": new.contexts}
                    if variant not in old.constraint_variants:
                        old.constraint_variants.append(variant)
                    # Unknown flags/types remain unknown in the union. The
                    # maximum is an observed upper bound across inspected
                    # layouts, never a claim that every layout permits it.
                    for key in ("data_type", "display_type", "mandatory", "read_only"):
                        if getattr(old, key) != getattr(new, key):
                            setattr(old, key, None)
                    lengths = [item for item in (old.maximum_length, new.maximum_length) if item is not None]
                    old.maximum_length = max(lengths) if lengths else None
                    old.completeness = "CONTEXT_DEPENDENT"
                    note = "Field constraints differ between inspected forms; template/product-type mapping needs review."
                    if note not in self.limitations:
                        self.limitations.append(note)
                for key in ("allowed_value_count", "maximum_option_character_count", "default_character_count",
                            "default_digit_count", "options_with_unsupported_characters",
                            "options_with_only_unsupported_characters"):
                    values = [item for item in (getattr(old, key), getattr(new, key)) if item is not None]
                    setattr(old, key, max(values) if values else None)
            return
        self.fields.append(new)


class MetadataParseError(ValueError):
    """A safe fixed-message parse error; never carries a response payload."""

    def __init__(self, message):
        self.reason = {
            "Expected metainfo.fields mapping was missing or malformed.": "METADATA_FIELDS_MISSING",
            "A field definition had an invalid identifier or shape.": "METADATA_FIELD_INVALID",
            "Nested metadata fields were not a mapping.": "METADATA_NESTED_FIELDS_INVALID",
            "A UDF holder did not expose its field-definition mapping.": "METADATA_UDF_FIELDS_MISSING",
        }.get(message, "METADATA_CONTRACT_MISMATCH")
        super().__init__(message)


class MetadataContextError(MetadataParseError):
    """A metadata response explicitly identifies a different source portal."""


def _assert_portal_context(response: Mapping[str, Any], portal_id: str) -> None:
    portal = response.get("portal")
    returned = portal.get("id") if isinstance(portal, dict) else response.get("portal_id")
    if returned is not None and _identifier(returned) != portal_id:
        raise MetadataContextError("Metadata explicitly returned a different portal than the requested PORTALID.")


def _option_measurements(definition: Mapping[str, Any]) -> tuple[int | None, int | None, int | None, int | None]:
    options = next((definition[key] for key in ("allowed_values", "options", "values")
                    if isinstance(definition.get(key), list)), None)
    if options is None:
        return None, None, None, None
    bad, only, maximum_length = 0, 0, None
    for option in options:
        value = option if isinstance(option, str) else option.get("name", option.get("value")) if isinstance(option, dict) else None
        if not isinstance(value, str):
            continue
        maximum_length = max(maximum_length or 0, len(value))
        if any(char in _OPTION_SPECIAL for char in value):
            bad += 1
            if not "".join(char for char in value if char not in _OPTION_SPECIAL).strip():
                only += 1
    return len(options), bad, only, maximum_length


def _definition(name: str, path: str, data: Mapping[str, Any], *, portal_id: str,
                portal_name: str, module: str, endpoint: str, doc_url: str,
                context: dict[str, str], additional: bool) -> FieldDefinition:
    constraints = data.get("constraints")
    constraints = constraints if isinstance(constraints, dict) else {}
    maximum = _integer(constraints.get("max_length", data.get("max_length")))
    allowed, bad, only, option_length = _option_measurements(data)
    custom = _boolean(data.get("is_custom", data.get("custom")))
    # A UDF container establishes an additional field, not who created it.
    default = data.get("default_value")
    field_type = data.get("field_type")
    if isinstance(field_type, dict):
        field_type = field_type.get("name")
    primitive_type = data.get("type", data.get("data_type"))
    if isinstance(primitive_type, dict):
        primitive_type = primitive_type.get("name")
    numeric_default = None
    if isinstance(default, (str, int)) and not isinstance(default, bool):
        candidate = str(default)
        if re.fullmatch(r"[+-]?[0-9]+(?:\.[0-9]+)?", candidate):
            # A measurement only: the default itself never survives parsing.
            numeric_default = sum(char.isdigit() for char in candidate)
    return FieldDefinition(
        internal_name=name, field_path=path, portal_id=portal_id, portal_name=portal_name,
        module=module, field_id=_identifier(data.get("id")),
        display_label=_text(data.get("display_name", data.get("display_label", data.get("label")))),
        data_type=_text(primitive_type, 60),
        display_type=_text(data.get("display_type", field_type), 60),
        maximum_length=maximum, allowed_value_count=allowed,
        mandatory=_boolean(data.get("mandatory", data.get("is_mandatory"))),
        read_only=_boolean(data.get("read_only", data.get("readonly"))), custom=custom,
        is_additional=additional or custom is True or _boolean(data.get("is_udf")) is True,
        is_encrypted=_boolean(data.get("is_encrypted")),
        is_pii=_boolean(data.get("is_pii")), metadata_source=endpoint,
        sources=[doc_url] if doc_url else [], contexts=[context] if context else [],
        default_character_count=len(default) if isinstance(default, str) else None,
        default_digit_count=numeric_default,
        maximum_option_character_count=option_length,
        options_with_unsupported_characters=bad,
        options_with_only_unsupported_characters=only,
    )


def normalize_metainfo(response: Mapping[str, Any], *, portal_id: str, portal_name: str,
                       module: str, endpoint: str, doc_url: str = "",
                       context: dict[str, str] | None = None) -> list[FieldDefinition]:
    """Accept the documented metadata wrapper; copy only schema attributes."""
    _assert_portal_context(response, portal_id)
    meta = response.get("metainfo")
    if not isinstance(meta, dict) or not isinstance(meta.get("fields"), dict):
        raise MetadataParseError("Expected metainfo.fields mapping was missing or malformed.")
    _assert_portal_context(meta, portal_id)
    result: list[FieldDefinition] = []
    pending: list[tuple[dict[str, Any], str, bool, int]] = [(meta["fields"], "", False, 0)]
    while pending:
        definitions, prefix, inherited_additional, depth = pending.pop()
        if depth > 16:
            raise MetadataParseError("Metadata nesting exceeded the parser limit.")
        for name, data in definitions.items():
            # Change role slots are keyed by role ID, not an API field name.
            # Only accept the observed roles.fields lookup contract; never use
            # a free-text role name as an internal identifier or generalize
            # numeric keys to arbitrary metadata containers.
            role_slot = (module == "changes" and prefix == "roles." and isinstance(name, str)
                         and re.fullmatch(r"[0-9]{1,40}", name) and isinstance(data, dict)
                         and _identifier(data.get("id")) == name and data.get("type") == "lookup")
            if not isinstance(name, str) or (not _FIELD_NAME.fullmatch(name) and not role_slot) or not isinstance(data, dict):
                raise MetadataParseError("A field definition had an invalid identifier or shape.")
            path = prefix + name
            definition_name = "role_" + name if role_slot else name
            children = data.get("fields")
            container = data.get("type") == "udf" or name in _UDF_CONTAINERS
            additional = inherited_additional or container
            if children is not None:
                if not isinstance(children, dict):
                    raise MetadataParseError("Nested metadata fields were not a mapping.")
                pending.append((children, path + ".", additional, depth + 1))
                continue
            if container:
                raise MetadataParseError("A UDF holder did not expose its field-definition mapping.")
            result.append(_definition(definition_name, path, data, portal_id=portal_id,
                                      portal_name=portal_name, module=module,
                                      endpoint=endpoint, doc_url=doc_url,
                                      context=context or {}, additional=additional))
            if len(result) > 25000:
                raise MetadataParseError("Metadata field count exceeded the parser limit.")
    return result


def normalize_udf_list(response: Mapping[str, Any], *, portal_id: str, portal_name: str,
                       module: str, endpoint: str, doc_url: str = "") -> list[FieldDefinition]:
    rows = response.get("udf_fields")
    _assert_portal_context(response, portal_id)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise MetadataParseError("Expected module-specific udf_fields list was missing or malformed.")
    result: list[FieldDefinition] = []
    for row in rows:
        name = row.get("name", row.get("api_name"))
        if not isinstance(name, str) or not _FIELD_NAME.fullmatch(name):
            raise MetadataParseError("A UDF definition had an invalid API name.")
        _assert_portal_context(row, portal_id)
        returned_module = row.get("module")
        if isinstance(returned_module, dict) and returned_module.get("name") not in (None, module):
            raise MetadataParseError("UDF metadata returned a different module context.")
        result.append(_definition(name, "udf_fields." + name, row, portal_id=portal_id,
                                  portal_name=portal_name, module=module, endpoint=endpoint,
                                  doc_url=doc_url, context={"module": module}, additional=True))
    return result


def normalize_ci_metadata(response: Mapping[str, Any], *, portal_id: str, portal_name: str,
                          module: str, endpoint: str, doc_url: str = CMDB_DOC,
                          context: dict[str, str] | None = None) -> list[FieldDefinition]:
    """The CI-type API wraps metainfo inside metadata; other content is dropped."""
    _assert_portal_context(response, portal_id)
    metadata = response.get("metadata")
    if not isinstance(metadata, dict):
        raise MetadataParseError("Expected CI metadata mapping was missing or malformed.")
    metainfo = metadata.get("metainfo")
    expected_name = (context or {}).get("api_plural_name")
    if isinstance(metainfo, dict) and expected_name and metainfo.get("plural_name") not in (None, expected_name):
        raise MetadataParseError("CI metadata returned a different type than the requested API name.")
    return normalize_metainfo(metadata, portal_id=portal_id, portal_name=portal_name,
                              module=module, endpoint=endpoint, doc_url=doc_url, context=context)


@dataclass
class _Read:
    module: str
    path: str
    input_data: dict[str, Any]
    doc_url: str
    context: dict[str, str] = field(default_factory=dict)
    strategy: str = "METAINFO"
    alternatives: list["_Read"] = field(default_factory=list)
    dynamic: bool = False
    target_id: str = ""
    provenance: str = "asset_modules"


class FieldDiscovery:
    """One portal's field work, driven by the environment's fair scheduler."""

    def __init__(self, client: Any, portal_id: str, portal_name: str,
                 datasets: Mapping[str, Any], metadata_limit: int = 20,
                 source_build: int | str | None = None):
        checked_portal = _identifier(portal_id)
        if checked_portal is None or int(checked_portal) == 0:
            raise ValueError("Field discovery requires an explicit positive ASCII numeric portal ID.")
        if isinstance(metadata_limit, bool) or not isinstance(metadata_limit, int) or metadata_limit < 0:
            raise ValueError("metadata_limit must be a nonnegative integer.")
        self.client = client
        self.portal_id = str(int(checked_portal))
        self.portal_name = _text(portal_name) or "Portal " + checked_portal
        self.datasets = datasets
        self.metadata_limit = metadata_limit
        self.source_build = _integer(source_build)
        self.inventories: dict[str, FieldInventory] = {}
        self._jobs: list[_Read] = []
        self._finished_targets: dict[str, set[str]] = {}
        self._attempted_targets: dict[str, set[str]] = {}
        self._failed_targets: dict[str, set[str]] = {}
        self._scope_complete: dict[str, bool] = {}
        self._started = False
        self._space_seen: dict[str, set[str]] = {}
        self._plan()

    def _inventory(self, module: str) -> FieldInventory:
        if module not in self.inventories:
            self.inventories[module] = FieldInventory(module, self.portal_id, self.portal_name)
            self._finished_targets[module], self._failed_targets[module] = set(), set()
            self._attempted_targets[module] = set()
        return self.inventories[module]

    def _observe_keys(self, module: str) -> None:
        inventory = self._inventory(module)
        dataset = self.datasets.get(module)
        for row in _rows(dataset):
            for container in _UDF_CONTAINERS:
                values = row.get(container)
                if not isinstance(values, dict):
                    continue
                for name in values:
                    if not isinstance(name, str) or not _FIELD_NAME.fullmatch(name):
                        continue
                    inventory.add(FieldDefinition(
                        internal_name=name, field_path=container + "." + name,
                        portal_id=self.portal_id, portal_name=self.portal_name, module=module,
                        is_additional=True, metadata_source=str(_get(dataset, "endpoint", "")),
                        evidence_basis="INFERRED_FROM_OBSERVED_UDF_KEY", completeness="OBSERVED_KEYS_ONLY",
                    ))
        if inventory.fields:
            has_metadata = any(item.evidence_basis == "API_METADATA" for item in inventory.fields)
            has_keys = any(item.evidence_basis == "INFERRED_FROM_OBSERVED_UDF_KEY" for item in inventory.fields)
            inventory.evidence_basis = ("API_METADATA_AND_OBSERVED_KEYS" if has_metadata and has_keys else
                                        "API_METADATA" if has_metadata else "INFERRED_FROM_OBSERVED_UDF_KEY")
            if not has_metadata:
                inventory.completeness = "OBSERVED_KEYS_ONLY"

    def refresh_observed_keys(self) -> dict[str, FieldInventory]:
        """Add schema-key evidence from later samples without any HTTP request.

        Collection generators may add record details after metadata planning.
        This pass reads only direct documented UDF-container *keys*, and never
        persists the associated values or overwrites verified schema types.
        """
        for module in _CORE_MODULES:
            if module in self.datasets:
                self._observe_keys(module)
        return self.inventories

    def _inherit_unavailable(self, module: str) -> bool:
        inventory = self._inventory(module)
        dataset = self.datasets.get(module)
        source_outcome = _get(dataset, "outcome") or _get(dataset, "status")
        if source_outcome not in _UNAVAILABLE:
            return False
        inventory.status = source_outcome
        note = "Metadata was not probed because the source inventory explicitly reported " + source_outcome + "."
        if note not in inventory.limitations:
            inventory.limitations.append(note)
            for diagnostic in _get(dataset, "diagnostics", ()):
                if isinstance(diagnostic, dict):
                    inventory.diagnostics.append({**diagnostic, "inherited_from_inventory": True})
        return True

    def _queue(self, module: str, jobs: list[_Read], total: int, scope_complete: bool) -> None:
        inventory = self._inventory(module)
        if self._inherit_unavailable(module):
            return
        inventory.metadata_targets_total += total
        chosen = _sample(jobs, self.metadata_limit)
        if len(chosen) < len(jobs):
            inventory.limitations.append("Metadata inspection limit reached; some observed forms/types will not be inspected.")
        self._scope_complete[module] = scope_complete and len(chosen) == total
        for index, job in enumerate(chosen):
            job.target_id = job.target_id or f"{module}:{index}"
            self._jobs.append(job)

    def _legacy_ids(self, module: str) -> list[str]:
        # Legacy Workstation selectors must come from observed computer types;
        # a generic product-type list can also contain furniture or services.
        ids = ({_identifier(row.get("id")) for row in _rows(self.datasets.get("product_types"))}
               if module == "assets" else set())
        for row in _rows(self.datasets.get(module)):
            value = row.get("product_type")
            if isinstance(value, dict):
                ids.add(_identifier(value.get("id")))
        return sorted((item for item in ids if item is not None), key=int)

    def _legacy_reads(self, module: str) -> list[_Read]:
        path = "/workstations/metainfo" if module == "computers" else "/assets/metainfo"
        doc = LEGACY_COMPUTER_DOC if module == "computers" else LEGACY_ASSET_DOC
        return [_Read(module, path, {"template": {"id": pid}}, doc,
                      {"product_type_id": pid}, "LEGACY_PRODUCT_TYPE_METAINFO")
                for pid in self._legacy_ids(module)]

    def _plan(self) -> None:
        modules = [name for name in _CORE_MODULES if name in self.datasets]
        if "requests" not in modules and any(name in self.datasets for name in ("incident_templates", "service_templates")):
            modules.append("requests")
        if "cis" not in modules and "ci_types" in self.datasets:
            modules.append("cis")
        for name in modules:
            self._observe_keys(name)
            self._inherit_unavailable(name)
        if "requests" in modules:
            templates: dict[str, dict[str, str]] = {}
            template_sets_complete = True
            for key in ("incident_templates", "service_templates"):
                data = self.datasets.get(key)
                template_sets_complete &= bool(_get(data, "list_complete", False))
                for row in _rows(data):
                    ident = _identifier(row.get("id"))
                    if ident:
                        templates[ident] = {"template_id": ident, "template_kind": key}
            for row in _rows(self.datasets.get("requests")):
                template = row.get("template")
                ident = _identifier(template.get("id")) if isinstance(template, dict) else None
                if ident:
                    templates.setdefault(ident, {"template_id": ident})
            jobs = [_Read("requests", "/requests/metainfo", {"template": {"id": ident}},
                          REQUEST_DOC, context, "REQUEST_TEMPLATE_METAINFO")
                    for ident, context in sorted(templates.items(), key=lambda item: int(item[0]))]
            self._queue("requests", jobs, len(jobs), template_sets_complete)
            self.inventories["requests"].limitations.append("Request metadata is restricted to inspected templates; unattached administrator fields are not certified.")
            if not jobs:
                self.inventories["requests"].limitations.append("No template ID was observable; the documented Request metadata selector cannot be supplied.")
        if "changes" in modules:
            ids = sorted({_identifier(row.get("id")) for row in _rows(self.datasets.get("changes"))} - {None}, key=int)
            alternatives = [_Read("changes", f"/changes/{ids[0]}/metainfo", {}, CHANGE_DOC,
                                  {"record_id": ids[0]}, "CHANGE_RECORD_METAINFO")] if ids else []
            self._queue("changes", [_Read("changes", "/changes/metainfo", {}, CHANGE_DOC,
                                          strategy="CHANGE_FORM_METAINFO", alternatives=alternatives)], 1, True)
            self.inventories["changes"].limitations.append("Change form metadata does not certify all administrator fields or every template/stage configuration.")
        for module, base in (("assets", "asset_assets"), ("computers", "asset_computers")):
            if module == "computers" and _get(self.datasets.get(module), "endpoint") == "/asset_workstations":
                base = "asset_workstations"
            if module not in modules:
                continue
            legacy = self._legacy_reads(module)
            unresolved_types = 0
            if self.source_build is not None and self.source_build < 15100 and legacy:
                jobs = legacy
                scope = module == "assets" and bool(_get(self.datasets.get("product_types"), "list_complete", False))
            else:
                types: dict[str, dict[str, str]] = {}
                if module == "assets":
                    for row in _rows(self.datasets.get("asset_modules")):
                        api = row.get("api_plural_name")
                        if isinstance(api, str) and _ASSET_API.fullmatch(api):
                            context = {"api_plural_name": api}
                            ident = _identifier(row.get("id"))
                            if ident:
                                context["product_type_id"] = ident
                            types[api] = context
                        else:
                            unresolved_types += 1
                if types:
                    jobs = [_Read(module, f"/{api}/_metainfo", {}, ASSET_DOC, context,
                                  "ASSET_PRODUCT_TYPE_METAINFO", dynamic=True)
                            for api, context in sorted(types.items())]
                    scope = bool(_get(self.datasets.get("asset_modules"), "list_complete", False)) and not unresolved_types
                else:
                    jobs = [_Read(module, f"/{base}/_metainfo", {"for": "advanced_filter"}, ASSET_DOC,
                                  {"api_plural_name": base}, "ASSET_BASE_METAINFO", alternatives=legacy)]
                    scope = module == "computers"
                    if module == "assets":
                        self.inventories[module].limitations.append("A complete product-type catalog was not available; base Asset metadata omits type-specific fields.")
                if unresolved_types:
                    self.inventories[module].limitations.append("Some observed asset types lacked a safe documented API plural name; their field metadata could not be queried.")
            total = len(jobs) + unresolved_types
            self._queue(module, jobs, total, scope)
            self.inventories[module].limitations.append("Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.")
            if legacy:
                self.inventories[module].limitations.append("Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026.")
        if "cis" in modules:
            types: dict[str, dict[str, str]] = {}
            unresolved_types = 0
            for row in _rows(self.datasets.get("ci_types")):
                api = row.get("api_plural_name")
                if isinstance(api, str) and _CMDB_API.fullmatch(api):
                    context = {"api_plural_name": api}
                    ident = _identifier(row.get("id"))
                    if ident:
                        context["ci_type_id"] = ident
                    types[api] = context
                else:
                    unresolved_types += 1
            jobs = [_Read("cis", f"/{api}/_metadata", {}, CMDB_DOC, context,
                          "CMDB_TYPE_METADATA", dynamic=True, provenance="ci_types")
                    for api, context in sorted(types.items())]
            complete = bool(_get(self.datasets.get("ci_types"), "list_complete", False)) and not unresolved_types
            self._queue("cis", jobs, len(jobs) + unresolved_types, complete)
            inventory = self.inventories["cis"]
            inventory.limitations.append("CI metadata covers inspected CI-type layouts; unattached CMDB fields and uninspected types remain unknown.")
            if not types or unresolved_types:
                inventory.limitations.append("Some or all CI types lacked a validated observed API plural name; no CI metadata path was guessed.")
        if "departments" in self.datasets:
            self._queue("departments", [_Read("departments", "/departments/_metainfo", {}, DEPARTMENT_DOC)], 1, True)
        observed_space = {name for name in SPACE_DOCS if name in self.datasets}
        for key in ("modules", "capabilities", "space_modules"):
            for row in _rows(self.datasets.get(key)):
                name = row.get("name")
                if isinstance(name, str) and name in SPACE_DOCS:
                    observed_space.add(name)
        for module in sorted(observed_space):
            self._queue(module, [_Read(module, "/udf_fields", {"module": {"name": module},
                         "list_info": {"row_count": 100, "start_index": 1}}, SPACE_DOCS[module],
                         {"module": module}, "MODULE_UDF_LIST")], 1, True)
        planned = {job.module for job in self._jobs}
        for module, inventory in self.inventories.items():
            if module not in planned and inventory.status not in _UNAVAILABLE:
                inventory.status = "INCOMPLETE"
                inventory.limitations.append("No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only.")

    def _event(self, inventory: FieldInventory) -> dict[str, Any]:
        return {"event": "field_metadata", "phase": "fields", "portal_id": self.portal_id,
                "portal_name": self.portal_name, "module": inventory.module,
                "status": inventory.status,
                "fields_observed": len(inventory.fields) if inventory.fields or inventory.metadata_targets_successful else None,
                "registry_complete": inventory.registry_complete,
                "form_scope_complete": inventory.form_scope_complete,
                "evidence_basis": inventory.evidence_basis,
                "metadata_targets_attempted": inventory.metadata_targets_attempted,
                "metadata_targets_total": inventory.metadata_targets_total}

    def _record_target_attempt(self, job: _Read, before: int, *, fallback: bool = False) -> None:
        has_stats = hasattr(self.client, "stats")
        after = _get(self.client.stats, "requests", before) if has_stats else before
        if after > before or (not has_stats and fallback):
            self._attempted_targets[job.module].add(job.target_id)
            self.inventories[job.module].metadata_targets_attempted = len(self._attempted_targets[job.module])

    def _complete(self, module: str) -> None:
        inventory = self.inventories[module]
        finished = len(self._finished_targets[module])
        failed = self._failed_targets[module]
        inventory.metadata_targets_successful = finished
        inventory.form_scope_complete = (finished == inventory.metadata_targets_total
                                         and bool(self._scope_complete.get(module)) and not failed)
        inventory.completeness = "FORM_SCOPE_COMPLETE" if inventory.form_scope_complete else "PARTIAL" if finished else inventory.completeness
        if finished:
            inventory.evidence_basis = ("API_METADATA_AND_OBSERVED_KEYS" if any(f.evidence_basis != "API_METADATA" for f in inventory.fields)
                                        else "API_METADATA")
            inventory.status = ("COMPLETE" if inventory.fields else "EMPTY") if inventory.form_scope_complete else "INCOMPLETE"
        elif failed:
            inventory.status = inventory.diagnostics[-1]["classification"] if inventory.diagnostics else "INCOMPLETE"
        elif inventory.metadata_targets_total:
            inventory.status = "NOT_SCANNED"
        # Only a successful, exhausted documented module UDF definition list
        # can prove this module's additional-field registry was enumerated.
        # Form metadata never proves all administrator fields were returned.
        inventory.registry_complete = module in SPACE_DOCS and inventory.form_scope_complete

    def stop(self, reason: str) -> None:
        """Finalize work after a global stop without changing completed modules."""
        for module, inventory in self.inventories.items():
            if inventory.status in {"COMPLETE", "EMPTY"}:
                continue
            if any(job.module == module for job in self._jobs):
                inventory.status = "INCOMPLETE" if inventory.metadata_targets_attempted else "NOT_SCANNED"
                inventory.form_scope_complete = False
                note = "Metadata collection stopped: " + reason
                if note not in inventory.limitations:
                    inventory.limitations.append(note)

    def iter_steps(self) -> Iterator[dict[str, Any]]:
        if self._started:
            raise RuntimeError("Field discovery can only be iterated once.")
        self._started = True
        # Module round-robin within a portal as well as portal fairness outside.
        queue: list[_Read] = []
        groups: dict[str, list[_Read]] = {}
        for job in self._jobs:
            groups.setdefault(job.module, []).append(job)
        while any(groups.values()):
            for group in groups.values():
                if group:
                    queue.append(group.pop(0))
        self._jobs = queue
        while self._jobs:
            job = self._jobs.pop(0)
            inventory = self.inventories[job.module]
            inventory.status = "COLLECTING"
            encoded = json.dumps(job.input_data, sort_keys=True, separators=(",", ":"))
            before = _get(self.client.stats, "requests", 0) if hasattr(self.client, "stats") else 0
            requeued = False
            try:
                if job.dynamic:
                    self.client.allow_metadata_path(job.path, portal_id=self.portal_id, provenance=job.provenance)
                params = {"input_data": encoded} if job.input_data else None
                response = self.client.get_json(job.path, params, portal_id=self.portal_id,
                                                endpoint_name="fields." + job.module, module=job.module)
                self._record_target_attempt(job, before, fallback=True)
                kwargs = {"portal_id": self.portal_id, "portal_name": self.portal_name,
                          "module": job.module, "endpoint": job.path, "doc_url": job.doc_url}
                if job.strategy == "MODULE_UDF_LIST":
                    definitions = normalize_udf_list(response, **kwargs)
                    info = response.get("list_info")
                    info = info if isinstance(info, dict) else {}
                    start = job.input_data["list_info"]["start_index"]
                    reported_start = _integer(info.get("start_index"))
                    if reported_start is not None and reported_start != start:
                        raise MetadataParseError("Module UDF metadata returned an unexpected pagination index.")
                    seen = self._space_seen.setdefault(job.module, set())
                    names = {item.field_path for item in definitions}
                    if names & seen or len(names) != len(definitions):
                        raise MetadataParseError("Repeated module UDF metadata page or duplicate identity detected.")
                    seen.update(names)
                    more = _boolean(info.get("has_more_rows"))
                    if more is True and definitions:
                        # The field limit is independent of record inventory and
                        # prevents a malformed server from paging forever.
                        if self.metadata_limit and len(seen) >= self.metadata_limit * 100:
                            inventory.limitations.append("Module UDF page limit reached; additional definitions remain uninspected.")
                            self._scope_complete[job.module] = False
                        else:
                            job.input_data["list_info"]["start_index"] += len(definitions)
                            self._jobs.append(job)
                            requeued = True
                    elif more is True or more is None:
                        self._scope_complete[job.module] = False
                        inventory.limitations.append("Module UDF pagination did not establish an exhausted list.")
                elif job.strategy == "CMDB_TYPE_METADATA":
                    definitions = normalize_ci_metadata(response, context=job.context, **kwargs)
                else:
                    definitions = normalize_metainfo(response, context=job.context, **kwargs)
                for definition in definitions:
                    inventory.add(definition)
                if job.doc_url not in inventory.sources:
                    inventory.sources.append(job.doc_url)
                if not requeued:
                    self._finished_targets[job.module].add(job.target_id)
                    inventory.metadata_targets_successful = len(self._finished_targets[job.module])
            except MetadataParseError as error:
                last_response = getattr(self.client, "last_response", {})
                kind = "portal_context" if isinstance(error, MetadataContextError) else "invalid_response"
                failure = ApiError(kind, str(error), http_status=_get(last_response, "http_status"),
                                   api_codes=tuple(_get(last_response, "api_codes", ())), portal_id=self.portal_id,
                                   endpoint=job.path, endpoint_name="fields." + job.module, module=job.module)
                failure.response_format = "json_object"
                failure.parse_reason = error.reason
                failure.response_shape = shape_evidence(response, "metadata" if job.strategy == "CMDB_TYPE_METADATA" else "metainfo")
                requeued = self._failure(job, failure)
            except ApiError as error:
                self._record_target_attempt(job, before, fallback=True)
                if error.classification == "AUTHENTICATION_FAILED":
                    inventory.diagnostics.append(error.to_dict())
                    self._jobs.insert(0, job)
                    self.stop("AUTHENTICATION_FAILED")
                    raise
                requeued = self._failure(job, error)
            except BudgetExceeded as error:
                self._record_target_attempt(job, before)
                inventory.diagnostics.append({"classification": error.reason, "portal_id": self.portal_id,
                                              "module": job.module, "endpoint": job.path,
                                              "cause": "scanner_budget", "retryable": True,
                                              "message": "Global budget ended before field discovery completed."})
                self._jobs.insert(0, job)
                self.stop(error.reason)
                raise
            except KeyboardInterrupt:
                self._record_target_attempt(job, before)
                self._jobs.insert(0, job)
                self.stop("USER_INTERRUPTED")
                raise
            finally:
                after = _get(self.client.stats, "requests", before) if hasattr(self.client, "stats") else before
                inventory.http_attempts += max(0, after - before)
            if not any(item.module == job.module for item in self._jobs):
                self._complete(job.module)
            yield self._event(inventory)

    def _failure(self, job: _Read, error: ApiError) -> bool:
        inventory = self.inventories[job.module]
        diagnostic = error.to_dict()
        if hasattr(error, "parse_reason"):
            diagnostic.update(parse_reason=error.parse_reason, response_shape=error.response_shape)
        diagnostic.update({"portal_id": self.portal_id, "module": job.module,
                           "endpoint": job.path, "endpoint_name": "fields." + job.module,
                           "strategy": job.strategy})
        inventory.diagnostics.append(diagnostic)
        if error.classification in _COMPATIBILITY_FAILURES and job.alternatives:
            if job.strategy == "ASSET_BASE_METAINFO":
                # Each legacy product type is a distinct selector, not a
                # chain of interchangeable ways to read the same form.
                alternatives = _sample(job.alternatives, self.metadata_limit)
                inventory.metadata_targets_total += len(job.alternatives) - 1
                self._scope_complete[job.module] = False
                for index, alternative in enumerate(alternatives):
                    alternative.target_id = job.target_id if index == 0 else f"{job.target_id}:legacy:{index}"
                    self._jobs.append(alternative)
                inventory.limitations.append("Legacy fallback inspects observed product-type selectors only; complete type coverage is not established.")
                return True
            next_read = job.alternatives.pop(0)
            next_read.target_id = job.target_id
            next_read.alternatives.extend(job.alternatives)
            self._jobs.append(next_read)
            inventory.limitations.append("A documented metadata compatibility fallback was needed; the earlier diagnostic is retained.")
            return True
        self._failed_targets[job.module].add(job.target_id)
        return False
