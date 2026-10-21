# On-premises topology and API scope research

Reviewed **7 October 2026** for standard ServiceDesk Plus on-premises. Cloud
(`sdpod-v3-api`, OAuth, `/app/{portal}`) and MSP API contracts are not evidence
for an on-premises endpoint. Source build and credential visibility remain
runtime facts. The research establishes operation contracts; it does not test a
customer installation.

## Portal discovery: contract and sourcing qualification

The documented read-only discovery operation is **GET `/api/v3/portals`**.
The complete on-premises request and example response are published by
[Netskope, the maintainer of its ServiceDesk Plus integration](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator),
under **Fetch All Portals → For On-Premises**. This is primary integration
documentation, rather than a community example. A corresponding portal-list
operation was **not located in the reviewed public ManageEngine on-premises V3
guide or ServiceDeskPlus Postman collection**. Do not describe Netskope's
contract as a ManageEngine minimum-build or universal support guarantee.

The request uses `authtoken` and
`Accept: application/vnd.manageengine.sdp.v3+json`. The discovery example has no
`PORTALID`; its job is to obtain portal identifiers. Pagination is supplied as
JSON in `input_data.list_info`. The published example uses `row_count`,
`start_index` (1-based), `page`, `sort_field: created_time` and
`sort_order: desc`. A scanner may choose a smaller page size.

The on-premises response contains `portals` (array), `response_status` (array)
and `list_info` (`has_more_rows`, `start_index`, `row_count`). Portal metadata
includes:

| Retained source fields when supplied | Meaning or limitation |
|---|---|
| `id`, `name` | Portal identity and display context. IDs must come from this response or explicit user input. Aliases are not needed for scoping. |
| `type.internal_name`, falling back to `type.name` | Instance type. Examples include IT, Facilities and Blank. Do not invent a numeric ID-to-type mapping. |
| `status.internal_name`, falling back to `status.name` | Instance lifecycle state. Examples include Production, Pre-Production and New. Do not interpret a numeric value alone. |
| `license_details.edition` | Reported edition, if present; it is not a complete enabled-module or add-on inventory. |

The scanner leaves `active` unknown unless the source supplies an explicit
boolean flag. Its default 100-portal discovery cap is a configurable scanner
safety budget, not a vendor limit. Reaching the cap while more rows are available
retains the discovered portals and reports incomplete topology.

Do not retain `image_token`, logo URLs, owners or descriptive content merely to
report topology. An enumerated portal is **visible in topology**; successful
scoped module reads establish operational access. The example does not promise
that listing a portal authorizes every operation within it.

If discovery is denied, unsupported or malformed, preserve its structured
diagnostic and require explicit portal IDs for scoped collection. Do not guess
1, enumerate integer IDs, scrape session state or silently scan an implicit
portal. A partial discovery response can still identify portals safely; its
completeness must remain partial.

## Headers, identity and scope

ManageEngine's [V3 parameter deprecation notice](https://pitstop.manageengine.com/portal/en/community/topic/deprecating-few-params-of-v3-api-urls)
states that build **11204** introduced lowercase `input_data` and moved
`authtoken` and `portalid` to **headers only**. Do not copy Netskope's older
project query-parameter example: use the header required by ManageEngine and
shown in its current Postman examples. HTTP header names are case insensitive.

The [on-premises authentication guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/)
explains that the token identifies a user and operations depend on that user's
roles. Successful pagination proves completeness only within that user's
visible portal, sites and operation scope.

### Resource scope matrix

| Resource | Data scope | Relevant official contract |
|---|---|---|
| Portal directory | Environment topology | Netskope discovery contract above; no portal header in its discovery example. |
| Organization users (`/orgusers`) | Global ESM directory | [Orguser folder](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser) explicitly says all users in the organization, ESM-directory only, Org admin privilege and more than one instance. [GET list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/7qfshjw/get-all-orgusers) returns `orgusers` and paginated `list_info`. |
| Portal users and technicians | Portal memberships and effective roles | [User](https://www.manageengine.com/products/service-desk/sdpop-v3-api/admin/user.html), [technician list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/e7t4k03/get-all-technicians). The [ESM V3 transition notice](https://pitstop.manageengine.com/portal/en/community/topic/user-technician-api-v3-changes-over-the-esm-release) distinguishes directory users from users/technicians in an instance. |
| Requests | Portal | [Official Postman request documentation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/documentation/euwj7bl/servicedesk-plus-on-premise?entity=request-43683186-dc422394-4e1f-4d42-8e14-0308c4ad9a96), [V3 request guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/requests/request.html). |
| Problems | Portal | [Problem list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/2qtgxu5/view-all-problem). |
| Changes | Portal | [V3 change guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/changes/change.html). |
| Projects | Portal | [Project list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/dul66jw/view-all-projects) explicitly includes `PORTALID`; wrapper `projects`; `list_info` pagination. [V3 project guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/projects/project.html). |
| Releases | Portal | [V3 release guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/releases/release.html). |
| Incident/service templates | Portal | [Incident template list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/urfbpdc/get-incident-templates), [service template list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/vuub628/get-service-templates). Both use `/request_templates` with the corresponding `is_service_template` filter and explicit portal header. |
| Sites, groups, reports, contracts and purchases | Portal | Existing source-linked entries in [api-catalog.md](api-catalog.md) use scoped Postman GET contracts. They are not directory-wide inventories. |
| Assets/computers | Portal; product-type hierarchy overlaps | [Asset list](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/4801ukn/get-all-assets) includes `PORTALID`; [build 15100 API changes](https://help.servicedeskplus.com/asset-api-changes) describe generic and type-specific scope. |
| CI types/CMDB | Portal; generic and per-type results overlap | [V1/V3 CMDB comparison](https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison). Keep separate logical coverage for basic inventory, per-type fields and relationships. |
| UDF/schema metadata | Portal plus module/type; some identity definitions can be directory-wide | See [field research](fields.md) when present and the source-linked schema strategies in the executable field catalog. A generic UDF operation must not become an organization-wide Request-field inventory. |

The generated Postman **orgusers** example includes a `PORTALID` placeholder
despite the folder's explicit global data scope. Data scope and request context
are separate concepts: fetch a global collection once in an explicit discovered
context where necessary, record that request context, and classify/report its
data as environment-wide. Do not retry the same global inventory for every
portal merely to obtain duplicates. Do not sum orgusers with per-portal user
memberships or describe the sum of memberships as unique people.

## Module discovery and permissions

No public, supported on-premises **whole-portal enabled-module catalog GET** was
located in the reviewed native V3 guide and ServiceDeskPlus Postman material.
The safe approach is to make the first page of each documented collection serve
as that operation's capability probe, reusing the successful page for inventory.
`asset_modules` describes asset product types; it is not an all-ITSM-module
license catalog.

[ESM licensing documentation](https://www.manageengine.com/products/service-desk/on-premises/faq/esm-license-management.html)
states that individual instances have their own license components and editions
can vary. An edition string alone does not prove whether an add-on or particular
operation is enabled. A retired or license-expired portal can also have special
access restrictions; retain the state and actual access evidence.

A Projects denial after a request carrying the correct portal header establishes
that this operation was denied in this context. It **does not establish that
Project Admin is the required remedy**. A portal-specific failure must not end
the assessment of other portals. A generic authorization failure must not be
relabelled as a missing module without module/licensing evidence.

### Documented error codes

The [on-premises status-code guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html)
provides the following useful distinctions:

| SDP code | Published HTTP status | Meaning for a read-only assessment |
|---|---:|---|
| `4001` | 400 | Input ID/name is missing, unavailable or unusable by the user; retain ambiguity and input context. |
| `4002` | 403 | Operation forbidden; do not infer a specific missing role. |
| `4004` | 500 | Internal server error. |
| `4007` | 404 | Invalid URL or missing resource; endpoint compatibility is a candidate for collection reads. |
| `4012` | 400 | Required field missing. A portal-context interpretation needs actual message/field evidence. |
| `4015` | 429 | API rate limit reached. |
| `4021` | 400 | Data type mismatch; query/schema compatibility must be inspected. |
| `4022` | 401 | Invalid API key. |
| `7001` | 400 | Operation not allowed by the current license. |

No universal numeric portal-context or portal-inaccessible code was located.
Use actual response text/field evidence for those classifications, while storing
HTTP status and SDP codes. Do not fabricate a code mapping. Response status can
be an object or array; nested messages can carry the informative code beneath
an outer generic failure. Preserve only sanitized diagnostics, never arbitrary
response bodies. A generic HTML 403 from a proxy does not establish SDP-level
authentication success.

No universal contractual rate quota was established. The scanner's **30/minute
combined across portals** remains a conservative client policy. All attempts,
including discovery, metadata and retries, share one budget and scheduler.

## Build compatibility and key expiry

- ESM and the user/technician V3 change arrived in build **11000**. Old
  requester/technician V1/V2 calls are not a suitable GET-only fallback; the
  [legacy user guide](https://help.servicedeskplus.com/user-operations) describes
  a POST-attribute operation for older versions.
- Build **11204** changed authentication and portal parameters to headers.
- Build **15100** introduced the current asset/CMDB APIs. The
  [asset change guide](https://help.servicedeskplus.com/asset-api-changes) says
  old `/assets` and `/workstations` API support ended in April 2026. Legacy reads
  may still work on older installations but cannot prove newer field coverage.
- The same guide says generic `/asset_assets` returns basic Asset fields,
  including custom types/components, but excludes product-type UDFs/subforms.
  Type-specific lists include child types, so parent and child rows must not be
  blindly added together. Metadata is type-specific and additional fields must
  be associated with a layout to appear there.
- ManageEngine's public mobile guide labels
  `/api/v3/app_resources/post_login_props` **internal only**. Release notes
  mention `/api/v3/app_resources/build_info`, but the reviewed sources did not
  establish a supported integration GET request/response contract. The scanner
  should not infer its own schema or masquerade as the mobile application;
  retain `--source-build` as explicitly user-supplied context.
- No documented read-only **integration-key expiry metadata** contract that
  avoids exposing key material was located. Do not request token-generation or
  key-management endpoints, infer expiry from an opaque key, or make expiry
  metadata a prerequisite for collection.

## Research limits

Native V3 pages, the official ServiceDeskPlus Postman collection's available
folders/requests and indexed documentation, official change notices and ESM
guides were reviewed. The public Postman document renderer exposed selected
sections and intermittently returned a shell/timeout; an exhaustive offline
export of every collection operation was not available. Unlocated capability,
build and expiry contracts are reported as research gaps, not proof that no
installed SDP build can expose them. The installed build's API documentation or
ManageEngine support can settle those specific contracts without guessing API
paths or changing the read-only model.


## October 14, 2026 follow-up: startup diagnostics and bounded compatibility

The directory contract and on-premises headers in Netskope's integration documentation were rechecked. The existing qualification remains: this is the integration maintainer's primary documentation; no universally supported minimum SDP build or equivalent native public portal-list contract has been established by this review.

- [Netskope: Fetch All Portals, on-premises headers and response](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator) documents GET `/api/v3/portals`, V3 Accept, `authtoken`, and form-urlencoded Content-Type. The scanner now sends the Content-Type header as well, still with no request body.
- [Official on-premises pagination guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/pagination.html) documents minimal `list_info` containing only `row_count` and `start_index`. If an initial sorted directory read returns `INVALID_QUERY`, the scanner permits one minimal-pagination attempt on the same path. This is a bounded compatibility strategy, not proof that the endpoint exists or that a particular source build accepts it. It is not used after a successful page or on 403/404/TLS/authentication/media-type failures.
- [Official on-premises status-code table](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html) distinguishes operation denial (4002), missing URL/resource (4007), throttling (4015), invalid key (4022), and license restrictions (7001). The actual HTTP/SDP evidence must be retained; `PORTAL_DISCOVERY_UNAVAILABLE` alone does not identify which happened.
- The official pagination response includes SDP success code 2000. The transport records authentication confirmed only after an SDP success envelope; an arbitrary HTTP 200 JSON object is insufficient. A missing SDP envelope does not prove the key invalid, and a permission response alone does not prove which upstream component denied it.

The user's log contains no actual HTTP/SDP or TLS diagnostic. Its first-attempt stop therefore cannot justify asserting a bad key, an unsupported server build, a missing role, or an untrusted certificate. Similarly, printing a filesystem path is not proof that the file can be reopened. The new output verification and console diagnostics address these separate evidence gaps without contacting the customer server.


## 2.1.0 review — October 14, 2026

Official sources rechecked for the same-run recovery design:

- ManageEngine [ESM general FAQs](https://help.servicedeskplus.com/esm-general-faqs) distinguish organization-directory administration from instance administration and describe instance URLs containing `PORTALID`. They do not establish the exact minimum role for the `/api/v3/portals` integration-key operation.
- ManageEngine [V3 common error codes](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html) distinguish 4002/403 operation denial from 4022/401 invalid key and 4015/429 throttling.
- The [official Postman Get User operation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/5uwqk3x/get-an-user) supplies the portal and authentication headers. This is scoped user access, not an alternate directory enumeration operation.
- The [Netskope on-premises connector documentation](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator) remains the source for the existing `/portals` response contract. It is primary documentation for that integration, not a universal ManageEngine build/role guarantee.

No supported alternative enumeration route available to the currently denied key was verified. This release therefore does not silently introduce `/my_portals`, current-user membership guesses, HTML scraping, a default portal or numerical probing. A separate user-authorized credential is limited to the same `/portals` GET and all module operations keep the original key. Alternatively, the user supplies a complete verified list once. These are scanner recovery mechanisms, not claims that the original credential acquired additional permissions. See [one-run portal assessment](../guides/all-portals.md).
