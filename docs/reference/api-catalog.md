# On-premises API catalog and scope

Reviewed **7 October 2026** for standard ManageEngine ServiceDesk Plus **on-premises V3**, including the build-15100 Asset/CMDB changes. Cloud OAuth and `/app/{portal}` contracts, MSP APIs, and undocumented application routes are not substitutes for these source APIs.

The executable inventory/allowlist is in `sdp_audit/catalog.py`; module-aware schema strategies are in `sdp_audit/fields.py`; topology is in `sdp_audit/topology.py`. Their presence in the catalog authorizes only the specific GET read. An allowed route does not mean a scan traverses every subresource: inspect actual coverage and detail counts.

## Authentication, portal context, and discovery

Requests use `authtoken` and `Accept: application/vnd.manageengine.sdp.v3+json` headers. Portal-scoped reads explicitly include `PORTALID`; the key and portal ID are never query parameters. The integration key inherits account visibility, so complete pagination remains limited to that account's portal/site/operation scope. See [on-premises authentication](https://www.manageengine.com/products/service-desk/sdpop-v3-api/) and [the build-11204 header change notice](https://pitstop.manageengine.com/portal/en/community/topic/deprecating-few-params-of-v3-api-urls).

| Operation | Data scope | Request context | Contract and limits |
| --- | --- | --- | --- |
| `/portals` | Environment topology | Explicitly no `PORTALID` | `portals` array plus `list_info`; on-prem request/response published by [Netskope's integration maintainer](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator) |
| `/orgusers` | Organization-wide ESM directory | Published example contains an explicit portal header; retain that context separately from data scope | [Official Orguser scope](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser), [GET list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/7qfshjw/get-all-orgusers); `orgusers` array, collected once |
| `/users`, `/technicians` | Portal memberships/effective identity roles | Explicit originating `PORTALID` | [ESM identity API transition](https://pitstop.manageengine.com/portal/en/community/topic/user-technician-api-v3-changes-over-the-esm-release); do not sum memberships as unique people |
| Remaining inventory/form operations below | Portal, plus module/template/type where required | Explicit originating `PORTALID` | Record and field IDs remain namespaced to their portal/module |

**Discovery sourcing qualification:** a corresponding portal-list operation was not located in the reviewed public ManageEngine on-premises guide or official ServiceDeskPlus Postman collection. Netskope provides a primary integration contract, not a ManageEngine minimum-build guarantee. The scanner records this qualification and runtime endpoint outcome. If the installed build cannot expose discovery, only explicitly supplied known IDs can establish targets. No default ID, integer sweep, browser session, or undocumented topology fallback is used. Details are in [research-topology.md](topology.md).

A discovered portal's metadata may include name, type, lifecycle state, and edition. It does not prove access to all modules. `accessible` stays unknown until scoped response evidence establishes access or denial. State IDs are not interpreted using an invented numeric mapping, and edition labels do not serve as an enabled-module catalog.

No supported universal all-module capability GET was verified. The first documented page for a collection serves as that operation's capability probe and is reused as inventory. `/asset_modules` is an asset product-type catalog, not a catalog of every ITSM module or entitlement.

## Pagination and global request policy

List calls encode JSON in `input_data`; general pagination uses one-based `list_info.start_index`, `row_count`, and returned `has_more_rows`. Some published examples encode numbers/booleans as strings. The scanner validates the wrapper, independent page state, repeated/overlapping IDs, forward progress, and available totals instead of treating a malformed response as empty. See [official pagination](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/pagination.html).

The portal discovery contract additionally demonstrates `page`, `sort_field: created_time`, and `sort_order: desc`. Inventory collectors use only fixed documented query selectors; older-build compatibility does not remove required portal or module selectors.

All attempts share the same client and scheduler, normally one GET every two seconds. The default 30/minute, 500-attempt, and 20-minute settings are scanner policies. Retries and metadata reads use these same budgets. Server HTTP 429, SDP code 4015, and `Retry-After` are respected. No universal numerical vendor allowance is asserted.

## Portal inventory

Paths are relative to `/api/v3`. Each row uses explicit `PORTALID`.

| Logical collection | GET path / response wrapper | Detail read | Evidence and coverage boundary |
| --- | --- | --- | --- |
| Incident templates | [`/request_templates`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/urfbpdc/get-incident-templates) / `request_templates`, `is_service_template=false` | `/request_templates/{id}` | Template inventory and exposed form-rule signals; list scope excludes complete field/layout configuration |
| Service templates | [Same route](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/vuub628/get-service-templates), `is_service_template=true` | Same | Separate service-template scope, with independent pagination |
| Sites | [`/sites`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/m7i4ubc/view-all-sites) / `sites` | `/sites/{id}` | Visible sites; exposed settings are not a complete role/SLA export |
| Support groups | [`/support_groups`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/qurnsjj/view-all-support-groups) / `support_groups` | `/support_groups/{id}` | Group inventory and visible associations |
| Technicians | [`/technicians`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/e7t4k03/get-all-technicians) / `technicians` | `/technicians/{id}` | Portal technicians; email completeness/duplicates can be analyzed without reporting addresses |
| Users | [`/users`](https://www.manageengine.com/products/service-desk/sdpop-v3-api/admin/user.html) / `users` | `/users/{id}` | Portal memberships, visible roles and UDF values; separate from global Orgusers |
| Query reports | [`/reports`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/lb43ei8/view-all-query-reports) / `reports`, `filter_by.name=Query_reports` | None | Report metadata; no execution, SQL, usage telemetry or external BI discovery |
| CI types | [`/ci_types`](https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison) / `ci_types` | None | New API CI-type inventory; not a complete CI-attribute/relationship schema |
| Asset modules | [`/asset_modules`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/documentation/euwj7bl/servicedesk-plus-on-premise) / `all_product_types` | None | Product-type/API names for validated exact metadata paths; not an all-module license catalog |
| Requests | [`/requests`](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/request.html) / `requests`, `All_Requests` filter | `/requests/{id}` | Visible ordinary requests, exposed dates/template/SLA references/relationships and attachment metadata; archived completeness is not established |
| Changes | [`/changes`](https://www.manageengine.com/products/service-desk/sdpop-v3-api/changes/change.html) / `changes` | `/changes/{id}` | Records and visible workflow/template/stage references; references do not export workflow behavior |
| Problems | [`/problems`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/2qtgxu5/view-all-problem) / `problems` | `/problems/{id}` | Visible records; related solutions, associations and administration remain separate scope |
| Projects | [`/projects`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/dul66jw/view-all-projects) / `projects` | `/projects/{id}` | Explicit portal context shown in official example; milestones/tasks/memberships are separate reads |
| Releases | [`/releases`](https://www.manageengine.com/products/service-desk/sdpop-v3-api/releases/release.html) / `releases`, `all_releases` filter | `/releases/{id}` | Source Release records; availability does not prove migration-utility or target entitlement |
| Assets | [`/asset_assets`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/4801ukn/get-all-assets) / `asset_assets` | No generic detail | New API cross-type basic rows, including components; product-type UDFs and subforms are excluded |
| Computers | [`/asset_computers`](https://help.servicedeskplus.com/asset-api-changes) / `asset_computers` | [`/asset_computers/{id}`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/zc2vkas/get-a-computer) | Exposed service tags, VM/date properties and type-specific detail; may overlap generic Assets/CMDB |
| CIs | [`/cmdb`](https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison) / `cmdb` | No generic detail | Basic CI inventory; per-type attributes and relationship preservation remain separate |
| Contracts | [`/contracts`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/fieghu5/view-all-contracts) / `contracts` | None | Parent inventory, not full terms/history/associations |
| Purchases | [`/purchase_orders`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/pqnf1he/view-all-purchase-orders) / `purchase_orders` | [`/purchase_orders/{id}`](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/ujtp3lz/view-a-purchase-order) | Parent inventory/detail; invoices, payments and approval levels require separate validation |

A global Orguser success does not substitute for a failed portal User read. A successful generic Asset/CMDB list does not imply complete type-specific fields. Per-portal records are combined only for reporting and analysis, with scope retained.

## Module-aware metadata

The old unfiltered `/udf_fields` inventory has been removed. `field_definitions` survives only as a CLI selection alias for module-aware field discovery.

| Module/context | Verified GET mechanism | Required selector or boundary |
| --- | --- | --- |
| Requests | `/requests/metainfo` | `input_data.template.id` from an observed template in the same portal |
| Changes | `/changes/metainfo`; documented `/changes/{observed_id}/metainfo` fallback | Form/stage scope; no fabricated record ID |
| Assets/Computers | `/asset_assets/_metainfo`, `/asset_computers/_metainfo`, documented product-type `/_metainfo` | Base metadata may use `input_data.for=advanced_filter`; product-type API plural names must come from the type catalog and pass validation |
| CMDB / CI types | `/{observed CI-type API plural name}/_metadata` | API plural name must come from `ci_types`; exact per-portal path validation; response `metadata.metainfo.fields`, as documented under [Get CI Type Details](https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison) |
| Legacy Assets/Workstations | `/assets/metainfo`, `/workstations/metainfo` | Observed product-type ID as `input_data.template.id`; limited legacy evidence |
| Departments | `/departments/_metainfo` | Department schema only, when that scope is available to field discovery |
| Documented Space modules | `/udf_fields` with the exact `space_campus`, `space_structure`, `space_floor` or `space_room` module selector | Only for that observed/applicable module; never generalized to unrelated modules |
| Modules without a verified definition read | No invented metadata endpoint | Observe UDF API names in already-collected rows without storing their values as metadata; report inferred, incomplete schema evidence |

The verified links, response structures, fallbacks and normalization rules are documented in [research-fields.md](fields.md). No official current generic definition endpoint was verified for Problems, Projects, Releases, Users, Technicians, Contracts or Purchases. CMDB uses observed CI-type metadata; it is not replaced by an invented universal `/cmdb/_metainfo` call. A missing strategy or type identifier does not imply zero fields.

A successful definition read retains field/module/portal provenance, constraints and counts. `form_scope_complete` and `registry_complete` are distinct. Completing inspected forms/types cannot certify fields not attached to those layouts. The field limit/default count is a bounded inspection policy; zero selects all observed metadata targets, still within global budgets.

The static allowlist also contains a few explicitly documented metadata variants, such as Printer/Server metadata. Dynamic registration admits exact validated Asset/CI-type metadata paths only, with the corresponding type-catalog provenance; it cannot authorize mutations, attachments, arbitrary links or another portal's reads.

## Detail/subresource allowlist

The allowlist permits bounded [Request Note](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/request_note.html) list/detail reads, [Request Worklog](https://www.manageengine.jp/support/kb/ServiceDesk_Plus/?p=7166) list/detail reads, and task list/detail reads under [Requests](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/request_task.html), [Changes](https://www.manageengine.com/products/service-desk/sdpop-v3-api/changes/change_task.html), [Projects](https://www.manageengine.com/products/service-desk/sdpop-v3-api/projects/project_task.html) and [Releases](https://www.manageengine.com/products/service-desk/sdpop-v3-api/releases/release_task.html). An explicit [Asset attachment metadata list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/pv19zxk/get-attachments-list) is allowlisted; attachment bodies remain prohibited.

Actual inspected parent/child counts and failures appear in coverage. A complete parent list does not make its nested records complete. No stored report, SQL, discovery, migration, export, or mutating endpoint is authorized.

## Compatibility and diagnostics

Current and legacy endpoint strategies are explicit; they are not a way around authorization. The vendor documents new Asset APIs at build **15100**, with legacy support stated to end in **April 2026**. A documented legacy read can supply limited older-build evidence when appropriate, but cannot be called comprehensive current coverage. See [Asset API changes](https://help.servicedeskplus.com/asset-api-changes).

The [official error-code guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html) documents these relevant codes:

| SDP code | Published HTTP status | Meaning and scanner interpretation |
| --- | ---: | --- |
| `4001` | 400 | Invalid/unavailable input or a value that the user cannot set; ambiguous, not proof of one required role |
| `4002` | 403 | Forbidden; retain operation/portal evidence without naming an unproven role |
| `4004` | 500 | Internal server error |
| `4007` | 404 | Invalid URL/resource; endpoint/object compatibility gap, not proven module absence |
| `4012` | 400 | Mandatory input missing; specifically recognized `PORTALID` evidence can establish required portal context |
| `4015` | 429 | API rate limit; bounded backoff and `Retry-After` handling |
| `4021` | 400 | Type mismatch; query/build compatibility investigation |
| `4022` | 401 | Invalid integration key; stop further reads |
| `7001` | 400 | Operation not allowed under the current license; distinguish from ordinary forbidden |

Recognized response-message evidence can further identify missing portal context, inaccessible portal, disabled module, or an incompatible API version. Generic HTTP 403 alone cannot establish any of those specific causes. Arbitrary response text is omitted to preserve privacy. See [diagnostics-and-coverage.md](diagnostics-and-coverage.md).

The scanner does not call undocumented internal `post_login_props`, guess build/version routes, or require key-expiration metadata. `--source-build` supplies optional user context. A safe, documented integration-key-expiration read was not verified, so expiration remains unassessed.

## Questions the source API cannot settle

- A complete archive inventory: the reviewed [on-premises archive guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/archive_request.html) documents a DELETE operation, from which the scanner does not invent a GET.
- Complete histories, hidden records, attachment bodies, every approval/relationship graph, and every administrator field registry.
- Full SLA/workflow/lifecycle behavior, custom scripts, triggers, recurring maintenance and external integration workloads.
- Target edition, effective tenant limits, licensing, exports, recovery, retention and vendor-approved exceptions.
- Final-delta/update/deletion semantics, identifier mapping, actual migration outcomes and functional acceptance.

Use the installed product's API documentation to resolve build differences. Cloud commitments require target/vendor evidence; unavailable source reads remain explicit coverage gaps.

## 2.1.1 query and diagnostic update

`get_total_count` is now controlled by `--count-policy first|always|never`.
The default is first-page only; every-page mode preserves earlier behavior. No endpoint
or response-wrapper allowlist is expanded by this patch. See
[the current source/contract review](../releases/2.1.1.md).
