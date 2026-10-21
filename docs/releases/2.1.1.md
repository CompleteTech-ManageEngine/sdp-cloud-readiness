# Contextual diagnostics and optional count queries — 2.1.1

## What the supplied evidence established

The incident pattern comprised successful scoped reads and `authentication: VALID`, a Users
`CONNECTION_TIMED_OUT`, an HTTP 200 collector `PARSE_ERROR`, and a Projects HTTP 403 with
SDP codes 4000/4002. Those are distinct outcomes. A Users timeout does not invalidate
successful authentication. A Projects denial is not a portal-directory denial. No particular
administrator role is established by that generic permission response.

The old parse diagnostic omitted endpoint/module identifiers and response format, so its
actual wrapper mismatch cannot be reconstructed. This release does not pretend that a
synthetic response is the customer's actual response or claim that the live schema mismatch
has been solved.

## Corrections

- Diagnostic JSON schema 1.1 keeps previous keys and adds scope qualifications and
  per-operation next steps. The assessment JSON remains schema 2.0.
- Explicit IDs are labelled `selection_source: explicit`. `complete: true` is retained as
  the historical selection-resolution field, qualified by `complete_scope: explicit_selection`,
  `directory_complete: false`, `directory_outcome: NOT_ATTEMPTED`, and a separate count of
  discovered versus supplied portals. Resolving a target ID does not enumerate the environment.
- Collector contract errors retain the exact operation path, logical collector/module,
  portal, response format, available HTTP status and SDP codes. Protocol metadata is used
  only when it belongs to that actual request, not a previous endpoint.
- `parse_reason` explains which condition failed. `response_shape` stores only known,
  fixed schema names and JSON types; unrecognized root keys are counted, never copied.
  String/numeric field values, row contents, arbitrary key names, bodies and exception text
  are not included. It does not authorize additional endpoints or expand response acceptance.
- List and detail contract failures, malformed pagination, repeated-page errors and count
  reconciliation failures use the same contextual diagnostic path.
- `diagnostics.json` includes global-resource and field-discovery failures as well as portal
  collection failures. Duplicate diagnostic objects are collapsed without merging portals.
- HTML/Markdown diagnostic tables display contract evidence and operation-specific advice.
- Network guidance acknowledges prior successful authentication where established for the
  same integration credential. The directory-only key remains a distinct credential scope.
- An explicit-portal startup notice warns that other portals will not be assessed. Existing
  targeting semantics are unchanged; `--all-portals` is not silently inferred from one ID.

## Avoiding repeated count requests

`--count-policy` accepts:

| Policy | Request behavior |
| --- | --- |
| `first` (new default) | Request `total_count` on the first page of each collection, not every subsequent page. |
| `always` | Preserve the earlier every-page count-request behavior. |
| `never` | Set `get_total_count` false on normal paginated reads. Use `has_more_rows` and independent pagination evidence. |

Each portal/collection tracks its first page independently. Required filters, explicit portal
headers and ordering remain unchanged. The existing first-page invalid-query compatibility
fallback can omit optional count/sort flags on older APIs.

A returned count is a point-in-time source value, not a frozen inventory. Coverage records
include `api_reported_total_page`. An old count is never used as permission to skip a page
or declare termination without reliable metadata. An unresolved count mismatch remains
incomplete. A successfully empty API-visible collection is still EMPTY/complete.

This is a workload-control option, not a proven diagnosis of a timeout. The server may ignore
the option, and query/record generation, database work, proxy timeouts or other factors can
still delay a read. Raising a timeout or reducing a page does not repair permission errors.
All reads and retries retain the same global scheduler, 30/minute default and budgets.

## Running one consolidated scan

```powershell
.\Run-All-Portals.cmd --count-policy never --timeout 90 --max-requests 2000 --max-minutes 90
```

Do not append an explicit single-portal restriction. On directory denial, use the existing
same-run D/L/F choices: a separately authorized directory-only key, a complete verified
ID/link list, or a saved host-bound scope file. Neither the new count policy nor improved
diagnostics bypasses directory or module permissions. No IDs are guessed. Saved lists are
not automatic evidence of newly added portals. Row/detail limits still apply.

## Official sources rechecked on 2026-10-14

- [ManageEngine on-premises Input Data](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/input-data.html)
  documents `get_total_count` as an optional boolean, false by default, plus `has_more_rows`.
- [ManageEngine on-premises Pagination](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/pagination.html)
  documents row-count/start-index traversal without a required total count.
- [ManageEngine on-premises Status Codes](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html)
  distinguishes 4002 permission denial, 4022 invalid key, 4015 rate limiting and 7001 licensing.
- [Official ServiceDesk Plus Postman product-type operation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/u4eoaf0/get-all-product-types)
  documents GET `/api/v3/asset_modules`.
- [Official Postman product-type examples](https://www.postman.com/servicedeskplus/servicedesk-plus-api/documentation/euwj7bl/servicedesk-plus-on-premise?entity=request-43683186-03d7c71a-c64a-483a-a834-8692b4405fd8)
  show `all_product_types` as the list wrapper. The collector retains this documented wrapper;
  arbitrary aliases or similarly named arrays are not silently accepted.

No minimum-build contract or new ManageEngine-native all-portal enumeration method was
established in this patch. See the existing topology research for the `/portals` source
qualification. No customer credentials, source bodies or system-specific portal list are
included in this distribution.
