# Diagnostics, permissions, and coverage

This guide explains the v2.0 environment/portal reports. It distinguishes **source evidence**, **collection completeness**, and **migration readiness**. A successful source read is useful evidence; it cannot prove how a future Cloud migration will behave.

## Read coverage before interpreting counts

Every collection has its own portal or environment scope, endpoint/module, list pagination state, detail inspection counts, diagnostics, and stop reason. These fields must be read together.

| Example result | Records meaning | List meaning | Detail meaning |
| --- | --- | --- | --- |
| IT / Requests: 2,347; `COMPLETE` | 2,347 distinct observed list rows in this API-visible scope | The list finished under the account/portal/filter used | A 20-record sample does not make every request's details complete |
| HR / Projects: `PERMISSION_DENIED` | Unknown, shown as blank/null or an em dash | Access was denied; absence was not established | Not assessed unless separate successful evidence exists |
| Facilities / Releases: `MODULE_NOT_AVAILABLE` | Unknown | Explicit source evidence indicates unavailability | Unknown |
| IT / Assets: 5,000; `RECORD_LIMIT_REACHED` | At least 5,000 observed, with more pages possible/available | Incomplete because a scanner cap was reached | Reported independently |
| HR / Changes: 0; `EMPTY` | Zero rows returned in a successful complete scoped response | Complete for that visible list | No parent records to sample |
| Security / Requests: `NOT_SCANNED` | Unknown; never convert to zero | No successful list read established coverage | Not assessed |

The numbers above are illustrative, not measurements from any customer installation.

During pagination, `COLLECTING` means another page is queued. It is not a final incomplete result. If an attempt/time/record limit, error, or pagination inconsistency stops work, the final state explains that reason. Completed collections retain their completion when some later collection consumes the remaining global budget.

The default inventory and metadata limits may be reached before a large environment is fully assessed. Increasing depth can improve coverage, but cannot resolve authentication, permission, module or build limitations.

## Topology and access are separate

The portal directory establishes which IDs the key can enumerate. It does not establish permission to read all data in those portals, nor does it guarantee visibility of every portal in the installation.

Each portal retains discovery source, name/ID/type/state/edition when exposed, selection, access evidence, scan status, diagnostics and limitations. A successful operation establishes access to that operation. A denial of HR / Projects does not invalidate a successful HR / Requests list or prove that every operation in HR is denied.

With explicit `--portal-id` targeting, IDs are user supplied and discovery is bypassed. `complete` on that explicit target set means the specified set was retained; it does not claim a complete environment directory. The report records `mode: explicit` and the discovery gap.

When automatic discovery cannot obtain an ID, the scanner issues no portal-scoped reads until known IDs are supplied. It never tries 1, 2, 3… or the integration key's implicit portal. Unsupported discovery therefore produces useful diagnostic reports without a fabricated zero-record environment.

## Structured result classifications

| Classification | Evidence needed / interpretation | Usual next step |
| --- | --- | --- |
| `SUCCESS` | A specific read succeeded | Continue remaining pagination/detail work |
| `EMPTY` | Successful complete collection with zero rows | Confirm the account/filter scope if data was expected |
| `COLLECTING` | A successful page left additional work | Let the scan continue |
| `COMPLETE` | Pagination finished without unresolved list integrity issues | Review separate detail and metadata coverage |
| `INCOMPLETE` | Some known scope remains unresolved | Read its stop reason, sample limits or pagination diagnostic |
| `AUTHENTICATION_FAILED` | HTTP/API evidence indicates invalid or failed authentication | Verify the integration key/account; all further reads stop |
| `PERMISSION_DENIED` | The specific operation was denied, e.g. generic 403/SDP 4002 | Review effective permissions for that portal/module with the administrator |
| `PORTAL_CONTEXT_REQUIRED` | Recognized API evidence identifies missing mandatory portal context | Check explicit `PORTALID`, selected IDs and installed API documentation |
| `PORTAL_NOT_ACCESSIBLE` | Recognized evidence identifies an inaccessible/unavailable/invalid portal | Verify that known portal ID and the key's association/visibility |
| `MODULE_NOT_ENABLED` | The API explicitly reports a disabled module | Confirm whether it is intentionally disabled and relevant to migration |
| `MODULE_NOT_AVAILABLE` | Explicit license/module availability evidence, including SDP 7001 | Confirm source availability and desired target entitlement |
| `ENDPOINT_UNSUPPORTED` | Endpoint or object was not found/unsupported | Review build contract and available documented fallback; do not infer absence |
| `INVALID_QUERY` | The API rejected selector/input/type/query data | Review recorded codes and query/build compatibility; do not assume a role fix |
| `API_VERSION_INCOMPATIBLE` | Explicit evidence states build/API-version incompatibility | Confirm the documented strategy applicable to the installed build |
| `RATE_LIMITED` | Throttling remains after bounded retries | Respect `Retry-After`; lower rate or schedule a later scan |
| `REQUEST_BUDGET_REACHED` | Shared HTTP attempt budget exhausted | Increase the global budget if more coverage is needed |
| `TIME_BUDGET_REACHED` | Shared runtime budget exhausted | Extend the duration if more coverage is needed |
| `RECORD_LIMIT_REACHED` | A scanner list/portal cap was reached | Increase that cap as appropriate, keeping global budgets explicit |
| `NETWORK_ERROR` | DNS/connection/TLS/redirect or other network issue | Resolve the recorded network/configuration condition |
| `SERVER_ERROR` | The server could not complete the read | Review service health and retry guidance |
| `PARSE_ERROR` | JSON/wrapper/metadata shape is invalid or incompatible | Compare against the installed build's documentation; preserve the gap |
| `UNKNOWN_API_ERROR` | Unsuccessful response could not be safely classified | Use sanitized codes and operation context in a vendor investigation |
| `NOT_STARTED`, `NOT_SCANNED` | No sufficient read evidence exists | Check selection, dependencies and global stop reasons |
| `INTERRUPTED` | User stopped collection | Use the partial report or rerun for remaining coverage |

A classification is as specific as the evidence allows. A generic 403 stays a permission denial unless additional recognized response evidence supports a more precise context/module explanation. A 404 can mean an endpoint or object is unavailable; it does not independently prove that a licensed module is disabled. API code 4001 is ambiguous input/availability/permission-related evidence; it cannot identify a particular required role.

The source for the documented numeric mappings is [ManageEngine's on-premises common error-code guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html). The scanner's more descriptive outcome names are its reporting vocabulary, not invented ManageEngine numeric codes.

## A Projects denial, interpreted correctly

Projects GETs use the originating portal's `PORTALID`, as shown in the [official Postman example](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/dul66jw/view-all-projects).

An illustrative denied operation is retained like this:

```json
{
  "portal_id": "3",
  "endpoint": "/projects",
  "endpoint_name": "projects",
  "module": "projects",
  "classification": "PERMISSION_DENIED",
  "http_status": 403,
  "api_codes": [4002],
  "api_message": "Forbidden",
  "message_sanitized": true,
  "cause": "authorization",
  "retryable": false
}
```

This establishes that the operation was denied in the selected portal. It does **not** establish a requirement for Project Admin, prove that Projects is unlicensed, or prove that the key cannot read any other module. Confirm the effective operation permissions using the installed product's documentation or vendor support.

For missing `PORTALID`, the scanner reports the actual recognized context evidence. It does not deliberately omit the header to experiment, change roles, or try a sequence of alternative portal IDs.

## Sanitized messages and secrets

Diagnostics retain HTTP status, SDP codes, endpoint logical name, module, portal ID, classification, probable cause, and retry appropriateness. Known safe message forms are retained or normalized. Unknown free text, raw response bodies, embedded records, URLs, and arbitrary names from error messages are omitted. `raw_message_omitted` records this limitation where applicable.

A missing verbatim message is intentional privacy protection, not proof that the API returned no message. Use the safe status/code/context for vendor investigation. Do not paste integration keys, full ticket responses, or attachment content into bug reports. The application provides no option to dump raw sensitive responses.

No documented safe integration-key-expiration read was established for this version. Expiration is not inferred from runtime, token shape, response headers, or success/failure. Authentication and expiration remain different questions.

## Fields: forms, registries, and observed keys

Field discovery has its own coverage. Important fields include:

| Field metadata item | Meaning |
| --- | --- |
| `portal_id`, `module`, `field_path` | Provenance/namespace; identical IDs in different portals/modules are not automatically the same field |
| `metadata_targets_total` | Observed metadata targets, including type entries that could not be queried safely; not necessarily every configured administrator field |
| `metadata_targets_attempted`, `metadata_targets_successful` | Actual inspection coverage; an allowed fallback can require additional HTTP attempts |
| `form_scope_complete` | Successful coverage of the observed, in-scope form/type targets |
| `registry_complete` | Whether all configured field definitions have been established; form success does not set this to true |
| `evidence_basis` | API metadata versus inferred observed UDF names |
| `completeness`, `limitations` | Unattached fields, uninspected templates/types, unsupported module metadata and other gaps |

`fields_observed: null` means no sufficient field evidence was available. It is not a zero-field registry. An empty successful form definition can establish zero fields in that form response while the administrator registry remains unknown.

Configured types/lengths are taken from definitions when exposed. Values observed in a record are not used to invent the field's type, label, mandatory/read-only setting or maximum length. Additional/custom origin can remain unknown, especially for migrated or vendor-provided fields.

A repeated field across templates is deduplicated within its portal/module namespace; its contexts are retained. Conflicting exposed constraints remain explicit variants. An observed definition allowing 1,000 characters against a relevant target limit of 250 indicates possible truncation exposure. It does not establish that any current value is over 250. This is an illustrative comparison; use the specific documented limit and module in the finding.

See [field research](fields.md) for verified selectors and module-specific limits. A failed bare universal UDF call is no longer part of the architecture.

## Aggregation and confidence

The environment view sums portal-scoped observations only within the relevant logical resource. It keeps global objects separate and counts the global Orguser directory once. User memberships are not unique people; Computers may be included in Assets; assets and CIs may represent related/overlapping objects. There is no meaningful grand total obtained by adding every module count.

Confidence qualifies evidence, not future migration probability:

- **API-visible list coverage:** pagination completed for the selected portal/account/filter.
- **Partial evidence:** some rows/definitions/details were observed, but remaining scope is unknown.
- **Unresolved:** no sufficient successful read established the count or conclusion.

Field/form coverage and deterministic detail sampling remain separate qualifications even when a list has complete API-visible coverage. A clean sample does not establish the absence of issues in unsampled details.

Every migration question separates source evidence, API limitations, target unknowns, vendor confirmation and business decisions. Acceptance blockers should be resolved through project decisions and migration/reconciliation evidence; they are not cleared merely by increasing an API scan's request budget.

## Using the structured reports

Version 2.0 JSON introduces an environment and first-class portals alongside flat findings/coverage. CSV outputs add portal, module, status, count, completeness and diagnostic information. Preserve `schema_version` when importing results and use at least `(scope, portal_id, resource/module)` for collection identity.

Legacy fields may remain for compatibility; use the structured `outcome`, completeness flags, nullable observed counts and diagnostic details for new integrations. A legacy `status` string or a single numeric counter is insufficient to interpret coverage. Environment-wide findings must retain environment scope; portal-specific findings must retain their portal ID even if a rule is repeated in several portals.
