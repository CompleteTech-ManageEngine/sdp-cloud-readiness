"""Value-free JSON contract evidence for read-only collector diagnostics.

Only names from the scanner's fixed catalog are retained. Unknown JSON keys
are counted, not copied; values, record labels and content never leave here.
This module describes a response shape. It does NOT authorize new endpoints,
accept guessed collection wrappers, or infer successful collection coverage.
"""
from __future__ import annotations

from typing import Any, Mapping

from .catalog import GLOBAL_RESOURCES, RESOURCES

KNOWN_KEYS = frozenset({
    'response_status', 'list_info', 'asset_modules', 'all_product_types',
    'module', 'modules', 'data', 'result', 'results', 'entities', 'metadata',
    'metainfo', 'fields', 'field_definitions', 'udf_fields', 'portals',
    'notes', 'note', 'tasks', 'task',
} | {r.plural for r in RESOURCES + GLOBAL_RESOURCES}
  | {r.singular for r in RESOURCES + GLOBAL_RESOURCES})
KNOWN_LIST_KEYS = frozenset({'start_index', 'row_count', 'has_more_rows', 'total_count',
                           'get_total_count', 'sort_field', 'sort_fields', 'sort_order', 'page'})
JSON_TYPES = frozenset({'missing', 'null', 'object', 'array', 'boolean', 'number', 'string', 'other'})
PARSE_REASONS = frozenset({
    'MISSING_COLLECTION_WRAPPER', 'INVALID_COLLECTION_TYPE', 'NON_OBJECT_COLLECTION_ITEM',
    'INVALID_LIST_INFO', 'PAGINATION_INDEX_MISMATCH', 'REPEATED_PAGE',
    'PAGINATION_TERMINATION_MISSING', 'EMPTY_PAGE_WITH_MORE_ROWS', 'TOTAL_COUNT_CONFLICT',
    'DETAIL_ENTITY_OR_ID_MISMATCH', 'RESPONSE_PORTAL_MISMATCH',
    'CONFLICTING_COLLECTION_WRAPPERS', 'METADATA_CONTRACT_MISMATCH',
    'METADATA_FIELDS_MISSING', 'METADATA_FIELD_INVALID',
    'METADATA_NESTED_FIELDS_INVALID', 'METADATA_UDF_FIELDS_MISSING',
})


def json_type(value: Any) -> str:
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, Mapping):
        return 'object'
    if isinstance(value, list):
        return 'array'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, (int, float)):
        return 'number'
    return 'other'


def shape_evidence(response: Any, expected: str) -> dict[str, Any]:
    """No scalar values or arbitrary source keys are included in the result."""
    root = response if isinstance(response, Mapping) else {}
    info = root.get('list_info')
    return {
        'root_type': json_type(response),
        'expected_wrapper': expected if expected in KNOWN_KEYS else None,
        'expected_wrapper_type': json_type(root[expected]) if expected in root else 'missing',
        'recognized_root_types': {key: json_type(root[key]) for key in sorted(KNOWN_KEYS) if key in root},
        'other_root_key_count': min(sum(key not in KNOWN_KEYS for key in root), 2**31 - 1),
        'list_info_types': {key: json_type(info[key]) for key in sorted(KNOWN_LIST_KEYS)
                            if isinstance(info, Mapping) and key in info},
        'values_omitted': True,
    }


def safe_shape(value: Any) -> dict[str, Any] | None:
    """Revalidate shape-only evidence at each report boundary."""
    if not isinstance(value, Mapping):
        return None
    def types(source: Any, allowed: frozenset[str]) -> dict[str, str]:
        return {key: source[key] for key in sorted(allowed) if isinstance(source, Mapping)
                and isinstance(source.get(key), str) and source[key] in JSON_TYPES}
    expected = value.get('expected_wrapper')
    count = value.get('other_root_key_count')
    return {
        'root_type': value.get('root_type') if isinstance(value.get('root_type'), str) and value['root_type'] in JSON_TYPES else 'other',
        'expected_wrapper': expected if isinstance(expected, str) and expected in KNOWN_KEYS else None,
        'expected_wrapper_type': value.get('expected_wrapper_type') if isinstance(value.get('expected_wrapper_type'), str) and value['expected_wrapper_type'] in JSON_TYPES else 'other',
        'recognized_root_types': types(value.get('recognized_root_types'), KNOWN_KEYS),
        'other_root_key_count': count if isinstance(count, int) and not isinstance(count, bool) and 0 <= count < 2**31 else None,
        'list_info_types': types(value.get('list_info_types'), KNOWN_LIST_KEYS),
        'values_omitted': True,
    }
