# ServiceDesk Plus Cloud migration readiness

Read-only environment assessment across the discovered and selected portal scope.

Generated: 2026-10-07T12:00:00+00:00 · Schema 2.0

## Executive summary

A dash means a count is unknown. Source reads cannot approve a future Cloud migration.

| Field | Value |
| --- | --- |
| portals\_discovered | 4 |
| portals\_selected | 4 |
| portals\_assessed | 4 |
| portals\_supplied\_explicitly | 0 |
| portals\_accessible | 3 |
| portals\_inaccessible | 1 |
| portals\_access\_unknown | 0 |
| collections\_complete | 58 |
| collections\_incomplete | 25 |
| permission\_related\_operations | 2 |
| unsupported\_unavailable\_operations | 4 |
| portal\_context\_operations | 0 |
| manual\_confirmation\_topics | 7 |
| findings\_by\_status | \{"CONFIRMED\_IMPACT": 81, "MANUAL\_CONFIRMATION": 27, "NO\_ISSUE\_OBSERVED": 2, "UNKNOWN": 115\} |
| acceptance\_items | 154 |

### Environment scan stop status

| Field | Value |
| --- | --- |
| classification | Not established |
| reason | Not established |
| requests | 137 |
| max\_requests | 500 |
| elapsed\_seconds | 272.0 |

## Environment topology

| Field | Value |
| --- | --- |
| outcome | COMPLETE |
| complete | true |
| complete\_scope | portal\_directory |
| directory\_complete | true |
| directory\_outcome | COMPLETE |
| portals\_discovered | 4 |
| portals\_supplied | 0 |
| coverage\_basis | discovery\_credential\_visible\_directory |
| mode | automatic |
| endpoint | /portals |
| source | https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator |
| credential\_scope | integration\_key |
| selection\_source | automatic |
| pages | 2 |
| limitations | \["The on-premises /portals contract is published in Netskope's primary integration documentation. A corresponding list operation was not located in the reviewed public ManageEngine V3 guide or official Postman collection; availability and a minimum supported source build are not guaranteed.", "Topology includes only portal identifiers returned to this integration key. Discovery visibility does not establish permission to read a portal's modules."\] |

### Source

| Field | Value |
| --- | --- |
| host | https://synthetic.example.invalid |
| product | ServiceDesk Plus On-Premises |
| demo | true |
| build\_origin | user\_supplied |
| orgusers\_collection | once\_for\_environment |

### Global budgets and usage

| Field | Value |
| --- | --- |
| demo | true |
| max\_requests | 500 |
| max\_child\_records | 2 |
| tls\_verification | true |
| max\_records | 5000 |
| max\_minutes | 20.0 |
| allow\_http | false |
| subresource\_parents | 1 |
| rpm | 30 |
| max\_runtime\_seconds | 1200 |
| credential\_visibility\_verified | false |
| attachment\_downloads | false |
| page\_size | 2 |
| detail\_limit | 2 |
| read\_only\_get\_only | true |
| timeout | 30 |
| collections\_selected | \["incident\_templates", "service\_templates", "sites", "support\_groups", "technicians", "users", "reports", "ci\_types", "asset\_modules", "requests", "changes", "problems", "projects", "releases", "assets", "computers", "cis", "contracts", "purchases"\] |
| max\_portals | 100 |
| metadata\_limit | 20 |

| Field | Value |
| --- | --- |
| requests | 137 |
| directory\_key\_authentication | unverified |
| successful\_requests | 130 |
| retries | 0 |
| failures\_by\_kind | \{"forbidden": 1, "license": 1, "portal\_access": 1, "unsupported": 4\} |
| failures\_by\_classification | \{"ENDPOINT\_UNSUPPORTED": 4, "MODULE\_NOT\_AVAILABLE": 1, "PERMISSION\_DENIED": 1, "PORTAL\_NOT\_ACCESSIBLE": 1\} |
| requests\_by\_scope | \{"global": 2, "portal:1": 49, "portal:2": 42, "portal:3": 43, "portal:4": 1\} |
| authentication | valid |
| elapsed\_seconds | 272.0 |
| wait\_seconds | 272.0 |
| requests\_per\_minute\_policy | 30.0 |
| max\_requests | 500 |
| max\_runtime\_seconds | 1200.0 |
| http\_allowed | false |
| tls\_verification | true |
| redirects\_followed | 0 |
| discovered\_metadata\_paths\_registered | 7 |
| portals\_discovered | 4 |
| portals\_selected | 4 |
| portals\_with\_successful\_scoped\_reads | 3 |
| portals\_with\_attempted\_assessment | 4 |
| global\_limiter\_instances | 1 |
| stop\_classification | Not established |
| network\_used | false |
| synthetic\_transport | true |
| findings\_by\_status | \{"CONFIRMED\_IMPACT": 81, "MANUAL\_CONFIRMATION": 27, "NO\_ISSUE\_OBSERVED": 2, "UNKNOWN": 115\} |
| portals\_assessed | 4 |
| global\_scheduler | true |

## Portals discovered

| Portal | ID | Instance type | State | Active | Source edition | Selected | Accessible | Scan status | Discovery endpoint |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IT Helpdesk | 1 | IT | Production | — | Enterprise | true | true | ASSESSED\_WITH\_COVERAGE\_GAPS | /portals |
| HR | 2 | HR | Production | — | Professional | true | true | ASSESSED\_WITH\_COVERAGE\_GAPS | /portals |
| Facilities | 3 | Facilities | Pre-Production | — | Standard | true | true | ASSESSED\_WITH\_COVERAGE\_GAPS | /portals |
| Security | 4 | Blank | Production | — | Enterprise | true | false | PORTAL\_NOT\_ACCESSIBLE | /portals |

## Portals assessed

| Portal | ID | Scan status | Complete lists | Lists with gaps | Finding statuses |
| --- | --- | --- | --- | --- | --- |
| IT Helpdesk | 1 | ASSESSED\_WITH\_COVERAGE\_GAPS | 19 | 2 | \{"CONFIRMED\_IMPACT": 28, "MANUAL\_CONFIRMATION": 7, "UNKNOWN": 30\} |
| HR | 2 | ASSESSED\_WITH\_COVERAGE\_GAPS | 18 | 3 | \{"CONFIRMED\_IMPACT": 26, "MANUAL\_CONFIRMATION": 6, "UNKNOWN": 30\} |
| Facilities | 3 | ASSESSED\_WITH\_COVERAGE\_GAPS | 20 | 1 | \{"CONFIRMED\_IMPACT": 23, "MANUAL\_CONFIRMATION": 4, "NO\_ISSUE\_OBSERVED": 1, "UNKNOWN": 30\} |
| Security | 4 | PORTAL\_NOT\_ACCESSIBLE | 0 | 19 | \{"CONFIRMED\_IMPACT": 1, "MANUAL\_CONFIRMATION": 3, "UNKNOWN": 25\} |

### Module availability and discovery evidence

Documented first-page reads establish operation availability. A denied or unsupported operation alone does not establish licensing or enablement.

| Portal | Module | Availability evidence | Collector | Endpoint | Operation result | Discovery method |
| --- | --- | --- | --- | --- | --- | --- |
| IT Helpdesk (ID 1) | requests | AVAILABLE | incident\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | requests | AVAILABLE | service\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | requests | AVAILABLE | requests | /requests | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | sites | AVAILABLE | sites | /sites | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | groups | AVAILABLE | support\_groups | /support\_groups | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | technicians | AVAILABLE | technicians | /technicians | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | users | AVAILABLE | users | /users | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | reports | AVAILABLE | reports | /reports | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | cmdb | AVAILABLE | ci\_types | /ci\_types | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | cmdb | AVAILABLE | cis | /cmdb | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | assets | AVAILABLE | asset\_modules | /asset\_modules | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | assets | AVAILABLE | assets | /asset\_assets | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | assets | AVAILABLE | computers | /asset\_computers | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | changes | AVAILABLE | changes | /changes | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | problems | AVAILABLE | problems | /problems | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | projects | AVAILABLE | projects | /projects | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | releases | AVAILABLE | releases | /releases | COMPLETE | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | contracts | AVAILABLE | contracts | /contracts | EMPTY | documented\_inventory\_first\_page\_reused |
| IT Helpdesk (ID 1) | purchases | AVAILABLE | purchases | /purchase\_orders | EMPTY | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | requests | AVAILABLE | incident\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | requests | AVAILABLE | service\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | requests | AVAILABLE | requests | /requests | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | sites | AVAILABLE | sites | /sites | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | groups | AVAILABLE | support\_groups | /support\_groups | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | technicians | AVAILABLE | technicians | /technicians | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | users | AVAILABLE | users | /users | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | reports | AVAILABLE | reports | /reports | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | cmdb | AVAILABLE | ci\_types | /ci\_types | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | cmdb | AVAILABLE | cis | /cmdb | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | assets | AVAILABLE | asset\_modules | /asset\_modules | EMPTY | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | assets | AVAILABLE | assets | /asset\_assets | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | assets | AVAILABLE | computers | /asset\_computers | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | changes | AVAILABLE | changes | /changes | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | problems | AVAILABLE | problems | /problems | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | projects | PERMISSION\_DENIED | projects | /projects | PERMISSION\_DENIED | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | releases | AVAILABLE | releases | /releases | COMPLETE | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | contracts | AVAILABLE | contracts | /contracts | EMPTY | documented\_inventory\_first\_page\_reused |
| HR (ID 2) | purchases | AVAILABLE | purchases | /purchase\_orders | EMPTY | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | requests | AVAILABLE | incident\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | requests | AVAILABLE | service\_templates | /request\_templates | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | requests | AVAILABLE | requests | /requests | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | sites | AVAILABLE | sites | /sites | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | groups | AVAILABLE | support\_groups | /support\_groups | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | technicians | AVAILABLE | technicians | /technicians | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | users | AVAILABLE | users | /users | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | reports | AVAILABLE | reports | /reports | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | cmdb | AVAILABLE | ci\_types | /ci\_types | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | cmdb | AVAILABLE | cis | /cmdb | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | assets | AVAILABLE | asset\_modules | /asset\_modules | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | assets | AVAILABLE | assets | /asset\_assets | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | assets | AVAILABLE | computers | /asset\_computers | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | changes | AVAILABLE | changes | /changes | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | problems | AVAILABLE | problems | /problems | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | projects | AVAILABLE | projects | /projects | COMPLETE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | releases | MODULE\_NOT\_AVAILABLE | releases | /releases | MODULE\_NOT\_AVAILABLE | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | contracts | AVAILABLE | contracts | /contracts | EMPTY | documented\_inventory\_first\_page\_reused |
| Facilities (ID 3) | purchases | AVAILABLE | purchases | /purchase\_orders | EMPTY | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | requests | UNKNOWN | incident\_templates | /request\_templates | PORTAL\_NOT\_ACCESSIBLE | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | requests | UNKNOWN | service\_templates | /request\_templates | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | requests | UNKNOWN | requests | /requests | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | sites | UNKNOWN | sites | /sites | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | groups | UNKNOWN | support\_groups | /support\_groups | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | technicians | UNKNOWN | technicians | /technicians | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | users | UNKNOWN | users | /users | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | reports | UNKNOWN | reports | /reports | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | cmdb | UNKNOWN | ci\_types | /ci\_types | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | cmdb | UNKNOWN | cis | /cmdb | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | assets | UNKNOWN | asset\_modules | /asset\_modules | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | assets | UNKNOWN | assets | /asset\_assets | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | assets | UNKNOWN | computers | /asset\_computers | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | changes | UNKNOWN | changes | /changes | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | problems | UNKNOWN | problems | /problems | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | projects | UNKNOWN | projects | /projects | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | releases | UNKNOWN | releases | /releases | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | contracts | UNKNOWN | contracts | /contracts | NOT\_STARTED | documented\_inventory\_first\_page\_reused |
| Security (ID 4) | purchases | UNKNOWN | purchases | /purchase\_orders | NOT\_STARTED | documented\_inventory\_first\_page\_reused |

## Portal access gaps and permissions diagnostics

A generic 403 does not establish a required role. Historical fallback failures remain available even when the final read succeeds.

| Field | Value |
| --- | --- |
| authentication | VALID |
| integration\_key\_expiration | NOT\_ASSESSED |
| key\_expiration\_note | No verified read-only expiration mechanism is implemented. Expiration is neither inferred nor required for the assessment. |
| orgusers\_collection | once\_for\_environment |
| portals\_accessible | 3 |
| portals\_access\_unknown | 0 |

| Portal / scope | Module | Operation | Classification | HTTP | SDP codes | Sanitized diagnostic | Likely category | Contract issue | Shape (types only) | Operation-specific next step | Raw text omitted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HR (ID 2) | projects | /projects | PERMISSION\_DENIED | 403 | \[4002\] | Forbidden | authorization | — | — | Confirm read permission for this specific module operation in the stated portal using the original integration key. A generic 403 does not identify a required role; directory credentials and timeout changes do not grant module access. | true |
| HR (ID 2) | assets | /asset\_assets/\_metainfo | ENDPOINT\_UNSUPPORTED | 404 | \[4007\] | Invalid URL | api\_compatibility\_or\_resource\_availability | — | — | Check this module's documented endpoint and response contract for the installed build. Unsupported operations are coverage gaps, not zero records or proof of missing permissions. | true |
| Facilities (ID 3) | releases | /releases | MODULE\_NOT\_AVAILABLE | 400 | \[7001\] | Not allowed as per current license | licensing\_or\_module\_availability | — | — | Confirm this portal's module availability and entitlement. The response does not establish an empty collection or require broader administrator roles. | true |
| Facilities (ID 3) | requests | /requests/metainfo | ENDPOINT\_UNSUPPORTED | 404 | \[4007\] | Invalid URL | api\_compatibility\_or\_resource\_availability | — | — | Check this module's documented endpoint and response contract for the installed build. Unsupported operations are coverage gaps, not zero records or proof of missing permissions. | true |
| Facilities (ID 3) | changes | /changes/metainfo | ENDPOINT\_UNSUPPORTED | 404 | \[4007\] | Invalid URL | api\_compatibility\_or\_resource\_availability | — | — | Check this module's documented endpoint and response contract for the installed build. Unsupported operations are coverage gaps, not zero records or proof of missing permissions. | true |
| Security (ID 4) | requests | /request\_templates | PORTAL\_NOT\_ACCESSIBLE | 403 | \[4002\] | Access to the specified portal is denied | portal\_access | — | — | Confirm the selected portal ID and original integration key's access to that portal. Keep this portal as a coverage gap while other authorized portals are assessed. | true |

## Per-portal migration risks

### IT Helpdesk (ID 1)

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| IT Helpdesk (ID 1) | multiple | Module records older than 1 year(s) | Confirmed impact | 5 | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| IT Helpdesk (ID 1) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| IT Helpdesk (ID 1) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| IT Helpdesk (ID 1) | requests | Additional-field value sizes | Confirmed impact | 1 | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| IT Helpdesk (ID 1) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | computers | Computer service-tag collisions | Confirmed impact | 2 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| IT Helpdesk (ID 1) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| IT Helpdesk (ID 1) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| IT Helpdesk (ID 1) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| IT Helpdesk (ID 1) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| IT Helpdesk (ID 1) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| IT Helpdesk (ID 1) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| IT Helpdesk (ID 1) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| IT Helpdesk (ID 1) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| IT Helpdesk (ID 1) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| IT Helpdesk (ID 1) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| IT Helpdesk (ID 1) | requests | requests: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | requests | requests: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | requests: additional-field name mapping | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | requests: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | requests: source field length declarations | Manual confirmation | 1 | Inspect measured value lengths where authorized and confirm target constraints; do not truncate data from metadata alone. |
| IT Helpdesk (ID 1) | requests | requests: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | requests: field constraints vary by form | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | problems | problems: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | problems | problems: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | problems | Problem additional fields require separate handling | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | changes: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | changes | changes: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | changes: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | changes: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | projects | projects: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | projects | projects: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | releases | releases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | releases | releases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | users | users: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | users | users: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | technicians | technicians: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | technicians | technicians: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | assets: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | assets | assets: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | assets: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | assets: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | computers: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | computers | computers: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | computers: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | computers: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | cis: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | cis | cis: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | cis: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | cis: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | contracts | contracts: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | contracts | contracts: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | purchases | purchases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| IT Helpdesk (ID 1) | purchases | purchases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | multiple | Portal operation coverage gaps | Unknown | — | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |

### HR (ID 2)

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| HR (ID 2) | multiple | Module records older than 1 year(s) | Confirmed impact | 4 | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| HR (ID 2) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| HR (ID 2) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| HR (ID 2) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| HR (ID 2) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| HR (ID 2) | requests | Additional-field value sizes | Confirmed impact | 1 | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| HR (ID 2) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | computers | Computer service-tag collisions | Confirmed impact | 2 | Review the identified records before migration. |
| HR (ID 2) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| HR (ID 2) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| HR (ID 2) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| HR (ID 2) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| HR (ID 2) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| HR (ID 2) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| HR (ID 2) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| HR (ID 2) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| HR (ID 2) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| HR (ID 2) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| HR (ID 2) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| HR (ID 2) | requests | requests: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | requests | requests: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | requests | requests: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | requests | requests: source field length declarations | Manual confirmation | 1 | Inspect measured value lengths where authorized and confirm target constraints; do not truncate data from metadata alone. |
| HR (ID 2) | requests | requests: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | requests | requests: field constraints vary by form | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | problems | problems: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | problems | problems: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | problems | Problem additional fields require separate handling | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | changes: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | changes | changes: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | changes: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | changes: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | projects | projects: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | projects | projects: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | releases | releases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | releases | releases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | users | users: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | users | users: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | technicians | technicians: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | technicians | technicians: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | assets: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | assets | assets: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | assets: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | assets: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | computers: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | computers | computers: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | computers: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | computers: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | cis | cis: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | cis | cis: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | contracts | contracts: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | contracts | contracts: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | purchases | purchases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| HR (ID 2) | purchases | purchases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | multiple | Portal operation coverage gaps | Unknown | — | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |

### Facilities (ID 3)

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Facilities (ID 3) | multiple | Module records older than 1 year(s) | Confirmed impact | 4 | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Facilities (ID 3) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| Facilities (ID 3) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Facilities (ID 3) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| Facilities (ID 3) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Facilities (ID 3) | requests | Additional-field value sizes | Confirmed impact | 1 | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| Facilities (ID 3) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | computers | Computer service-tag collisions | No issue observed | 0 | Review the identified records before migration. |
| Facilities (ID 3) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| Facilities (ID 3) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Facilities (ID 3) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Facilities (ID 3) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Facilities (ID 3) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| Facilities (ID 3) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| Facilities (ID 3) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| Facilities (ID 3) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| Facilities (ID 3) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| Facilities (ID 3) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| Facilities (ID 3) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| Facilities (ID 3) | requests | requests: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | requests | requests: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | problems | problems: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | problems | problems: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | problems | Problem additional fields require separate handling | Manual confirmation | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | changes: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | changes | changes: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | changes: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | changes: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | projects | projects: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | projects | projects: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | releases | releases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | releases | releases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | users | users: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | users | users: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | technicians | technicians: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | technicians | technicians: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | assets: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | assets | assets: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | assets: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | assets: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | computers: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | computers | computers: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | computers: oversized field defaults or options | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | computers: additional-field option normalization | Confirmed impact | 1 | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | cis | cis: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | cis | cis: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | contracts | contracts: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | contracts | contracts: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | purchases | purchases: field-definition coverage | Unknown | — | Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility. |
| Facilities (ID 3) | purchases | purchases: additional-field capacity | Unknown | — | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | multiple | Portal operation coverage gaps | Unknown | — | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |

### Security (ID 4)

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Security (ID 4) | multiple | Module records older than 1 year(s) | Unknown | — | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | Module records older than 5 year(s) | Unknown | — | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Security (ID 4) | requests | Linked-request relationships | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Request dependencies | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Request and change associations | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | multiple | Attachment-size exposure | Unknown | — | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Security (ID 4) | requests | Attachments on request notes | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | technicians | Technician email readiness | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Security (ID 4) | requests | Request additional-field capacity | Unknown | — | Validate every field type and target entitlement; free-tier and other-module limits differ. |
| Security (ID 4) | requests | Case-insensitive field-name collisions | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Additional-field value sizes | Unknown | — | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| Security (ID 4) | requests | Request scheduled-date consistency | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | computers | Computer service-tag collisions | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| Security (ID 4) | assets | Asset date-order consistency | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | multiple | Workflow and SLA reconstruction | Unknown | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Security (ID 4) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Security (ID 4) | reports | Query-report inventory review | Unknown | — | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Security (ID 4) | templates | Template task and resource limits | Unknown | — | Review identified template structures and all uncollected task/resource/question details. |
| Security (ID 4) | requests | Request resolution length | Unknown | — | Preserve identified long resolutions and inspect uncollected historical text fields. |
| Security (ID 4) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| Security (ID 4) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| Security (ID 4) | problems | Problem ancillary-data preservation | Unknown | — | Record the migration disposition for problem ancillary content and configuration. |
| Security (ID 4) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| Security (ID 4) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| Security (ID 4) | multiple | Portal operation coverage gaps | Unknown | — | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |

## Environment-wide aggregated risks

Rule observations may overlap. Global objects are counted once; user memberships and asset resource types are separate populations.

| Rule | Portals with confirmed impact | Affected observations | Portals with unknown evidence | Portals needing confirmation |
| --- | --- | --- | --- | --- |
| Role and organization-membership mapping | 0 | — | 0 | 4 |
| Approver and CAB login access | 0 | — | 4 | 0 |
| Archived-request subentity exposure | 0 | — | 4 | 0 |
| Asset date-order consistency | 3 | 3 | 1 | 0 |
| Attachment-size exposure | 3 | 3 | 1 | 0 |
| Change identifier preservation | 0 | — | 0 | 4 |
| Computer service-tag collisions | 2 | 4 | 1 | 0 |
| assets: additional-field capacity | 0 | — | 3 | 0 |
| assets: field-definition coverage | 0 | — | 3 | 0 |
| assets: oversized field defaults or options | 3 | 3 | 0 | 0 |
| assets: additional-field option normalization | 3 | 3 | 0 | 0 |
| changes: additional-field capacity | 0 | — | 3 | 0 |
| changes: field-definition coverage | 0 | — | 3 | 0 |
| changes: oversized field defaults or options | 3 | 3 | 0 | 0 |
| changes: additional-field option normalization | 3 | 3 | 0 | 0 |
| cis: additional-field capacity | 0 | — | 3 | 0 |
| cis: field-definition coverage | 0 | — | 3 | 0 |
| cis: oversized field defaults or options | 1 | 1 | 0 | 0 |
| cis: additional-field option normalization | 1 | 1 | 0 | 0 |
| computers: additional-field capacity | 0 | — | 3 | 0 |
| computers: field-definition coverage | 0 | — | 3 | 0 |
| computers: oversized field defaults or options | 3 | 3 | 0 | 0 |
| computers: additional-field option normalization | 3 | 3 | 0 | 0 |
| contracts: additional-field capacity | 0 | — | 3 | 0 |
| contracts: field-definition coverage | 0 | — | 3 | 0 |
| Case-insensitive field-name collisions | 0 | — | 1 | 0 |
| problems: additional-field capacity | 0 | — | 3 | 0 |
| problems: field-definition coverage | 0 | — | 3 | 0 |
| Problem additional fields require separate handling | 0 | — | 0 | 3 |
| projects: additional-field capacity | 0 | — | 3 | 0 |
| projects: field-definition coverage | 0 | — | 3 | 0 |
| purchases: additional-field capacity | 0 | — | 3 | 0 |
| purchases: field-definition coverage | 0 | — | 3 | 0 |
| releases: additional-field capacity | 0 | — | 3 | 0 |
| releases: field-definition coverage | 0 | — | 3 | 0 |
| requests: additional-field capacity | 0 | — | 3 | 0 |
| requests: field constraints vary by form | 0 | — | 0 | 2 |
| requests: field-definition coverage | 0 | — | 3 | 0 |
| requests: source field length declarations | 0 | — | 0 | 2 |
| requests: oversized field defaults or options | 2 | 2 | 0 | 0 |
| requests: additional-field name mapping | 0 | — | 0 | 1 |
| requests: additional-field option normalization | 2 | 2 | 0 | 0 |
| technicians: additional-field capacity | 0 | — | 3 | 0 |
| technicians: field-definition coverage | 0 | — | 3 | 0 |
| users: additional-field capacity | 0 | — | 3 | 0 |
| users: field-definition coverage | 0 | — | 3 | 0 |
| Additional-field value sizes | 3 | 3 | 1 | 0 |
| Form-script action compatibility | 0 | — | 4 | 0 |
| Module records older than 5 year(s) | 3 | 3 | 1 | 0 |
| Module records older than 1 year(s) | 3 | 13 | 1 | 0 |
| Historical audit-detail preservation | 4 | — | 0 | 0 |
| Linked-request relationships | 3 | 3 | 1 | 0 |
| CMDB, Releases and custom-module migration scope | 0 | — | 0 | 4 |
| Attachments on request notes | 3 | 3 | 1 | 0 |
| Portal operation coverage gaps | 0 | — | 4 | 0 |
| Problem ancillary-data preservation | 3 | 3 | 1 | 0 |
| Query-report inventory review | 3 | 3 | 1 | 0 |
| Recurring maintenance schedules | 0 | — | 4 | 0 |
| Request and change associations | 3 | 3 | 1 | 0 |
| Request dependencies | 3 | 3 | 1 | 0 |
| Request additional-field capacity | 0 | — | 1 | 0 |
| Request scheduled-date consistency | 3 | 3 | 1 | 0 |
| Request resolution length | 3 | 3 | 1 | 0 |
| Technician email readiness | 3 | 9 | 1 | 0 |
| Template task and resource limits | 3 | 6 | 1 | 0 |
| Virtual-machine host references | 0 | — | 4 | 0 |
| Workflow and SLA reconstruction | 3 | — | 1 | 0 |

## Data-volume summary

| Scope | Resource | Records observed | Complete lists | Selected collections | Collections with unknown count | Population semantics |
| --- | --- | --- | --- | --- | --- | --- |
| environment | orgusers | 2 | 1 | 1 | 0 | Environment collection counted once. |
| portal | asset\_modules | 6 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | assets | 5 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | changes | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | ci\_types | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | cis | 6 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | computers | 5 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | contracts | 0 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | incident\_templates | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | problems | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | projects | 3 | 2 | 4 | 2 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | purchases | 0 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | releases | 2 | 2 | 4 | 2 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | reports | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | request\_notes | 3 | 1 | 3 | 0 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | request\_tasks | 3 | 1 | 3 | 0 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | requests | 6 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | service\_templates | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | sites | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | support\_groups | 3 | 3 | 4 | 1 | Observed records for this resource only; overlaps with other resource types are not added. |
| portal | technicians | 9 | 3 | 4 | 1 | Portal membership observations, not unique people across portals. |
| portal | users | 3 | 3 | 4 | 1 | Portal membership observations, not unique people across portals. |

## Configuration/customization impact

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| IT Helpdesk (ID 1) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| IT Helpdesk (ID 1) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| IT Helpdesk (ID 1) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| IT Helpdesk (ID 1) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| IT Helpdesk (ID 1) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| IT Helpdesk (ID 1) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| IT Helpdesk (ID 1) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| HR (ID 2) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| HR (ID 2) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| HR (ID 2) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| HR (ID 2) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| HR (ID 2) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| HR (ID 2) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| HR (ID 2) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| HR (ID 2) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| Facilities (ID 3) | requests | Linked-request relationships | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | requests | Request dependencies | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | requests | Request and change associations | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | technicians | Technician email readiness | Confirmed impact | 3 | Review the identified records before migration. |
| Facilities (ID 3) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Facilities (ID 3) | requests | Request scheduled-date consistency | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | multiple | Workflow and SLA reconstruction | Confirmed impact | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Facilities (ID 3) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Facilities (ID 3) | templates | Template task and resource limits | Confirmed impact | 2 | Review identified template structures and all uncollected task/resource/question details. |
| Facilities (ID 3) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| Facilities (ID 3) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| Facilities (ID 3) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |
| Security (ID 4) | requests | Linked-request relationships | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Request dependencies | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Request and change associations | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | technicians | Technician email readiness | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | users | Approver and CAB login access | Unknown | — | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Security (ID 4) | requests | Request scheduled-date consistency | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | multiple | Workflow and SLA reconstruction | Unknown | — | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Security (ID 4) | templates | Form-script action compatibility | Unknown | — | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Security (ID 4) | templates | Template task and resource limits | Unknown | — | Review identified template structures and all uncollected task/resource/question details. |
| Security (ID 4) | maintenances | Recurring maintenance schedules | Unknown | — | Inventory recurring maintenance and rebuild its schedule at the agreed migration stage. |
| Security (ID 4) | changes | Change identifier preservation | Manual confirmation | — | Confirm Change ID retention with support and require a cross-reference for any changed identifiers. |
| Security (ID 4) | identity | Role and organization-membership mapping | Manual confirmation | — | Test permitted and denied access for representative roles, sites, groups and sensitive queues. |

## Field/UDF impact

Field observations are scoped by portal and module. Form coverage is separate from complete registry coverage. Declared lengths and case-folded labels alone do not prove failed record migration.

| Portal | Module | Additional fields observed | Explicitly custom fields | Metadata targets successful / known | Result | Metadata coverage | Registry complete |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IT Helpdesk (ID 1) | requests | 3 | 3 | 2 / 2 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| IT Helpdesk (ID 1) | problems | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| IT Helpdesk (ID 1) | changes | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| IT Helpdesk (ID 1) | projects | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| IT Helpdesk (ID 1) | releases | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| IT Helpdesk (ID 1) | users | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| IT Helpdesk (ID 1) | technicians | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| IT Helpdesk (ID 1) | assets | 2 | 2 | 3 / 3 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| IT Helpdesk (ID 1) | computers | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| IT Helpdesk (ID 1) | cis | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| IT Helpdesk (ID 1) | contracts | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| IT Helpdesk (ID 1) | purchases | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| HR (ID 2) | requests | 3 | 3 | 2 / 2 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| HR (ID 2) | problems | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| HR (ID 2) | changes | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| HR (ID 2) | projects | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| HR (ID 2) | releases | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| HR (ID 2) | users | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| HR (ID 2) | technicians | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| HR (ID 2) | assets | 2 | 2 | 1 / 1 | INCOMPLETE | PARTIAL | false |
| HR (ID 2) | computers | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| HR (ID 2) | cis | 1 | 0 | 0 / 1 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| HR (ID 2) | contracts | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| HR (ID 2) | purchases | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| Facilities (ID 3) | requests | 1 | 0 | 0 / 2 | ENDPOINT\_UNSUPPORTED | OBSERVED\_KEYS\_ONLY | false |
| Facilities (ID 3) | problems | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| Facilities (ID 3) | changes | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| Facilities (ID 3) | projects | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| Facilities (ID 3) | releases | — | — | 0 / 0 | MODULE\_NOT\_AVAILABLE | UNKNOWN | false |
| Facilities (ID 3) | users | 1 | 0 | 0 / 0 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| Facilities (ID 3) | technicians | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| Facilities (ID 3) | assets | 2 | 2 | 3 / 3 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| Facilities (ID 3) | computers | 2 | 2 | 1 / 1 | COMPLETE | FORM\_SCOPE\_COMPLETE | false |
| Facilities (ID 3) | cis | 1 | 0 | 0 / 1 | INCOMPLETE | OBSERVED\_KEYS\_ONLY | false |
| Facilities (ID 3) | contracts | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |
| Facilities (ID 3) | purchases | — | — | 0 / 0 | INCOMPLETE | UNKNOWN | false |

### IT Helpdesk (ID 1) / requests

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://www.manageengine.com/products/service-desk/on-premises/custom-help-desk-ticket-templates.html"\] |
| limitations | \["Request metadata is restricted to inspected templates; unattached administrator fields are not certified.", "Field constraints differ between inspected forms; template/product-type mapping needs review."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_char1 | 71 | Business reference | single\_line | 400 | — | — | false | /requests/metainfo |
| id | — | — | long | — | — | — | true | /requests/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /requests/metainfo |
| udf\_fields.udf\_case | 73 | business reference | single\_line | 250 | — | — | — | /requests/metainfo |

### IT Helpdesk (ID 1) / problems

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_problem\_ref | — | — | — | — | — | — | — | /problems |

### IT Helpdesk (ID 1) / changes

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/j6u4ac3/meta-info-for-change-add"\] |
| limitations | \["Change form metadata does not certify all administrator fields or every template/stage configuration."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | — | — | long | — | — | — | true | /changes/metainfo |
| udf\_fields.udf\_change\_ref | 71 | Change reference | single\_line | 250 | — | — | false | /changes/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /changes/metainfo |

### IT Helpdesk (ID 1) / projects

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_project\_code | — | — | — | — | — | — | — | /projects |

### IT Helpdesk (ID 1) / releases

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_release\_ref | — | — | — | — | — | — | — | /releases |

### IT Helpdesk (ID 1) / users

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user\_udf\_fields.udf\_identity\_note | — | — | — | — | — | — | — | /users |

### IT Helpdesk (ID 1) / technicians

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### IT Helpdesk (ID 1) / assets

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/asset-api-changes"\] |
| limitations | \["Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Asset reference | single\_line | 250 | — | — | false | /asset\_assets/\_metainfo |
| id | — | — | long | — | — | — | true | /asset\_assets/\_metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /asset\_assets/\_metainfo |

### IT Helpdesk (ID 1) / computers

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/asset-api-changes"\] |
| limitations | \["Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Asset reference | single\_line | 250 | — | — | false | /asset\_computers/\_metainfo |
| id | — | — | long | — | — | — | true | /asset\_computers/\_metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /asset\_computers/\_metainfo |

### IT Helpdesk (ID 1) / cis

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison"\] |
| limitations | \["CI metadata covers inspected CI-type layouts; unattached CMDB fields and uninspected types remain unknown."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_ci\_owner | 71 | Application owner | single\_line | 250 | — | — | false | /cmdb\_demo/\_metadata |
| id | — | — | long | — | — | — | true | /cmdb\_demo/\_metadata |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /cmdb\_demo/\_metadata |

### IT Helpdesk (ID 1) / contracts

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### IT Helpdesk (ID 1) / purchases

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### HR (ID 2) / requests

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://www.manageengine.com/products/service-desk/on-premises/custom-help-desk-ticket-templates.html"\] |
| limitations | \["Request metadata is restricted to inspected templates; unattached administrator fields are not certified.", "Field constraints differ between inspected forms; template/product-type mapping needs review."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_char1 | 71 | Personnel reference | single\_line | 400 | — | — | false | /requests/metainfo |
| id | — | — | long | — | — | — | true | /requests/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /requests/metainfo |
| udf\_fields.udf\_case | 73 | Additional reference | single\_line | 250 | — | — | — | /requests/metainfo |

### HR (ID 2) / problems

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_problem\_ref | — | — | — | — | — | — | — | /problems |

### HR (ID 2) / changes

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/j6u4ac3/meta-info-for-change-add"\] |
| limitations | \["Change form metadata does not certify all administrator fields or every template/stage configuration."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | — | — | long | — | — | — | true | /changes/metainfo |
| udf\_fields.udf\_change\_ref | 71 | Change reference | single\_line | 250 | — | — | false | /changes/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /changes/metainfo |

### HR (ID 2) / projects

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### HR (ID 2) / releases

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_release\_ref | — | — | — | — | — | — | — | /releases |

### HR (ID 2) / users

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user\_udf\_fields.udf\_identity\_note | — | — | — | — | — | — | — | /users |

### HR (ID 2) / technicians

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### HR (ID 2) / assets

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | PARTIAL |
| sources | \["https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/hdso1p4/get-asset-metainfo"\] |
| limitations | \["A complete product-type catalog was not available; base Asset metadata omits type-specific fields.", "Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026.", "Legacy fallback inspects observed product-type selectors only; complete type coverage is not established."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Legacy asset reference | single\_line | 250 | — | — | false | /assets/metainfo |
| id | — | — | long | — | — | — | true | /assets/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /assets/metainfo |

### HR (ID 2) / computers

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/asset-api-changes"\] |
| limitations | \["Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Asset reference | single\_line | 250 | — | — | false | /asset\_computers/\_metainfo |
| id | — | — | long | — | — | — | true | /asset\_computers/\_metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /asset\_computers/\_metainfo |

### HR (ID 2) / cis

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["CI metadata covers inspected CI-type layouts; unattached CMDB fields and uninspected types remain unknown.", "Some or all CI types lacked a validated observed API plural name; no CI metadata path was guessed.", "No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_ci\_owner | — | — | — | — | — | — | — | /cmdb |

### HR (ID 2) / contracts

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### HR (ID 2) / purchases

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### Facilities (ID 3) / requests

| Field | Value |
| --- | --- |
| status | ENDPOINT\_UNSUPPORTED |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["Request metadata is restricted to inspected templates; unattached administrator fields are not certified."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_char1 | — | — | — | — | — | — | — | /requests |

### Facilities (ID 3) / problems

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_problem\_ref | — | — | — | — | — | — | — | /problems |

### Facilities (ID 3) / changes

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/j6u4ac3/meta-info-for-change-add"\] |
| limitations | \["Change form metadata does not certify all administrator fields or every template/stage configuration.", "A documented metadata compatibility fallback was needed; the earlier diagnostic is retained."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | — | — | long | — | — | — | true | /changes/401/metainfo |
| udf\_fields.udf\_change\_ref | 71 | Change reference | single\_line | 250 | — | — | false | /changes/401/metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /changes/401/metainfo |

### Facilities (ID 3) / projects

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_project\_code | — | — | — | — | — | — | — | /projects |

### Facilities (ID 3) / releases

| Field | Value |
| --- | --- |
| status | MODULE\_NOT\_AVAILABLE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["Metadata was not probed because the source inventory explicitly reported MODULE\_NOT\_AVAILABLE."\] |

No observations supplied; absence is not established.

### Facilities (ID 3) / users

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user\_udf\_fields.udf\_identity\_note | — | — | — | — | — | — | — | /users |

### Facilities (ID 3) / technicians

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### Facilities (ID 3) / assets

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/asset-api-changes"\] |
| limitations | \["Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Asset reference | single\_line | 250 | — | — | false | /asset\_assets/\_metainfo |
| id | — | — | long | — | — | — | true | /asset\_assets/\_metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /asset\_assets/\_metainfo |

### Facilities (ID 3) / computers

| Field | Value |
| --- | --- |
| status | COMPLETE |
| completeness | FORM\_SCOPE\_COMPLETE |
| sources | \["https://help.servicedeskplus.com/asset-api-changes"\] |
| limitations | \["Asset metadata includes fields attached to inspected product-type layouts; unattached fields and uninspected child types remain unknown.", "Legacy metadata exposes older field layouts only; vendor support for the legacy Asset API was stated to end in April 2026."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_asset\_ref | 71 | Asset reference | single\_line | 250 | — | — | false | /asset\_computers/\_metainfo |
| id | — | — | long | — | — | — | true | /asset\_computers/\_metainfo |
| udf\_fields.udf\_choice | 72 | Fulfillment class | pick\_list | — | 3 | — | — | /asset\_computers/\_metainfo |

### Facilities (ID 3) / cis

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | OBSERVED\_KEYS\_ONLY |
| sources | \[\] |
| limitations | \["CI metadata covers inspected CI-type layouts; unattached CMDB fields and uninspected types remain unknown.", "Some or all CI types lacked a validated observed API plural name; no CI metadata path was guessed.", "No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

| Internal path | Field ID | Label | Type | Maximum length | Options | Mandatory | Read-only | Metadata source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| udf\_fields.udf\_ci\_owner | — | — | — | — | — | — | — | /cmdb |

### Facilities (ID 3) / contracts

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

### Facilities (ID 3) / purchases

| Field | Value |
| --- | --- |
| status | INCOMPLETE |
| completeness | UNKNOWN |
| sources | \[\] |
| limitations | \["No complete field registry was established by a documented read in this scan; observed UDF keys are lower-bound evidence only."\] |

No observations supplied; absence is not established.

## Reporting impact

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Environment | reports | Native Power BI reporting requirements | Confirmed impact | — | Validate the native connector against reporting requirements or design a separate historical extraction path. |
| Environment | reports | Full descriptions in reporting | Manual confirmation | — | Test required full descriptions in the selected reporting path. The generic Cloud report FAQ describes a 250-character display limit; this does not prove a native Power BI limit. |
| IT Helpdesk (ID 1) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| HR (ID 2) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Facilities (ID 3) | reports | Query-report inventory review | Confirmed impact | 1 | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Security (ID 4) | reports | Query-report inventory review | Unknown | — | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |

## Automation/integration impact

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Environment | automation | Automation runtimes and execution budgets | Confirmed impact | — | Inventory script dependencies and actual execution rates; verify target datacenter support and quotas. Definition counts are not execution counts. |
| Environment | integrations | External integrations and email behavior | Manual confirmation | — | Inventory external automation/report consumers, replace authentication and endpoints, and test old-email threading and failure recovery. |

## Historical-data exposure

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Environment | audit | Cloud administrative audit retention | Confirmed impact | — | Plan complete periodic exports when needed; administrative logs are distinct from ticket-history retention. |
| IT Helpdesk (ID 1) | multiple | Module records older than 1 year(s) | Confirmed impact | 5 | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| IT Helpdesk (ID 1) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| IT Helpdesk (ID 1) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| IT Helpdesk (ID 1) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| HR (ID 2) | multiple | Module records older than 1 year(s) | Confirmed impact | 4 | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| HR (ID 2) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| HR (ID 2) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| HR (ID 2) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| HR (ID 2) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| Facilities (ID 3) | multiple | Module records older than 1 year(s) | Confirmed impact | 4 | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | Module records older than 5 year(s) | Confirmed impact | 1 | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Facilities (ID 3) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| Facilities (ID 3) | multiple | Attachment-size exposure | Confirmed impact | 1 | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Facilities (ID 3) | requests | Attachments on request notes | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | requests | Request resolution length | Confirmed impact | 1 | Preserve identified long resolutions and inspect uncollected historical text fields. |
| Facilities (ID 3) | problems | Problem ancillary-data preservation | Confirmed impact | 1 | Record the migration disposition for problem ancillary content and configuration. |
| Security (ID 4) | multiple | Module records older than 1 year(s) | Unknown | — | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | Module records older than 5 year(s) | Unknown | — | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | Historical audit-detail preservation | Confirmed impact | — | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Security (ID 4) | archived\_requests | Archived-request subentity exposure | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | multiple | Attachment-size exposure | Unknown | — | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Security (ID 4) | requests | Attachments on request notes | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | requests | Request resolution length | Unknown | — | Preserve identified long resolutions and inspect uncollected historical text fields. |
| Security (ID 4) | problems | Problem ancillary-data preservation | Unknown | — | Record the migration disposition for problem ancillary content and configuration. |

## Assets/CMDB exposure

| Portal / scope | Module | Finding | Status | Affected observations | Required action |
| --- | --- | --- | --- | --- | --- |
| Environment | assets | Asset discovery and network continuity | Manual confirmation | — | Confirm discovery architecture and test repeated scans from every required network segment. |
| IT Helpdesk (ID 1) | computers | Computer service-tag collisions | Confirmed impact | 2 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| IT Helpdesk (ID 1) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| HR (ID 2) | computers | Computer service-tag collisions | Confirmed impact | 2 | Review the identified records before migration. |
| HR (ID 2) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| HR (ID 2) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| HR (ID 2) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| Facilities (ID 3) | computers | Computer service-tag collisions | No issue observed | 0 | Review the identified records before migration. |
| Facilities (ID 3) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| Facilities (ID 3) | assets | Asset date-order consistency | Confirmed impact | 1 | Review the identified records before migration. |
| Facilities (ID 3) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |
| Security (ID 4) | computers | Computer service-tag collisions | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | computers | Virtual-machine host references | Unknown | — | Validate VM classification and host relationships across the complete computer inventory. |
| Security (ID 4) | assets | Asset date-order consistency | Unknown | — | Review the identified records before migration. |
| Security (ID 4) | multiple | CMDB, Releases and custom-module migration scope | Manual confirmation | — | Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible. |

## Coverage and confidence

List completion survives later global budget exhaustion. Detail/subresource coverage remains separate. Failed or unstarted reads do not establish zero records.

| Portal / scope | Resource | Records observed | List coverage | Detail coverage | Result | HTTP | SDP codes | Reason | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IT Helpdesk (ID 1) | incident\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | service\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | sites | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | support\_groups | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | technicians | 3 | Complete | 2 successful / 2 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | users | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | reports | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | ci\_types | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | asset\_modules | 3 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | requests | 3 | Complete | 2 successful / 2 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | changes | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | problems | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | projects | 2 | Complete | 2 successful / 2 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | releases | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | assets | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | computers | 2 | Complete | 2 successful / 2 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | cis | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | contracts | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | purchases | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| IT Helpdesk (ID 1) | request\_notes | 1 | Incomplete / not established | 1 successful / 1 attempted; incomplete or sampled | INCOMPLETE | 200 | \[2000\] | Only sampled parents/subresources were inspected; unknown is not zero. | PARTIAL\_EVIDENCE |
| IT Helpdesk (ID 1) | request\_tasks | 1 | Incomplete / not established | 1 successful / 1 attempted; incomplete or sampled | INCOMPLETE | 200 | \[2000\] | Only sampled parents/subresources were inspected; unknown is not zero. | PARTIAL\_EVIDENCE |
| HR (ID 2) | incident\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | service\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | sites | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | support\_groups | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | technicians | 3 | Complete | 2 successful / 2 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | users | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | reports | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | ci\_types | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | asset\_modules | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | requests | 2 | Complete | 2 successful / 2 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | changes | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | problems | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | projects | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | PERMISSION\_DENIED | 403 | \[4002\] | PERMISSION\_DENIED | UNRESOLVED |
| HR (ID 2) | releases | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | assets | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | computers | 2 | Complete | 2 successful / 2 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | cis | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | contracts | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | purchases | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| HR (ID 2) | request\_notes | 1 | Incomplete / not established | 1 successful / 1 attempted; incomplete or sampled | INCOMPLETE | 200 | \[2000\] | Only sampled parents/subresources were inspected; unknown is not zero. | PARTIAL\_EVIDENCE |
| HR (ID 2) | request\_tasks | 1 | Incomplete / not established | 1 successful / 1 attempted; incomplete or sampled | INCOMPLETE | 200 | \[2000\] | Only sampled parents/subresources were inspected; unknown is not zero. | PARTIAL\_EVIDENCE |
| Facilities (ID 3) | incident\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | service\_templates | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | sites | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | support\_groups | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | technicians | 3 | Complete | 2 successful / 2 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | users | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | reports | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | ci\_types | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | asset\_modules | 3 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | requests | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | changes | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | problems | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | projects | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | releases | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | MODULE\_NOT\_AVAILABLE | 400 | \[7001\] | MODULE\_NOT\_AVAILABLE | UNRESOLVED |
| Facilities (ID 3) | assets | 1 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | computers | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | cis | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | contracts | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | purchases | 0 | Complete | 0 successful / 0 attempted; complete for listed scope | EMPTY | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | request\_notes | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Facilities (ID 3) | request\_tasks | 1 | Complete | 1 successful / 1 attempted; complete for listed scope | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |
| Security (ID 4) | incident\_templates | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | PORTAL\_NOT\_ACCESSIBLE | 403 | \[4002\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | service\_templates | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | sites | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | support\_groups | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | technicians | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | users | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | reports | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | ci\_types | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | asset\_modules | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | requests | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | changes | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | problems | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | projects | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | releases | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | assets | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | computers | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | cis | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | contracts | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Security (ID 4) | purchases | — | Incomplete / not established | 0 successful / 0 attempted; incomplete or sampled | NOT\_STARTED | — | \[\] | PORTAL\_NOT\_ACCESSIBLE | UNRESOLVED |
| Environment | orgusers | 2 | Complete | 0 successful / 0 attempted; incomplete or sampled | COMPLETE | 200 | \[2000\] | — | API\_VISIBLE\_LIST |

- A completed list traversal covers only records visible to this API key. It does not establish organization-wide completeness or access to every module.
- The scan is not a transactional snapshot. Source records may be added, changed, or removed while pagination and detail reads are in progress.
- List and detail coverage are separate. Counts and examples apply to the examined evidence; sampled observations must not be extrapolated into exact totals.
- Unknown and manual-confirmation items remain unresolved. This report does not assign an overall readiness score or approve a production migration.
- These artifacts contain assessment metadata, record identifiers, counts, and documented rules. Raw API records, credentials, ticket subjects, attachment filenames, and request bodies are excluded by the assessment contract.
- SYNTHETIC DEMONSTRATION ONLY. No actual ServiceDesk Plus instance was contacted.
- Source-only assessment; no migration, configuration changes, attachment downloads, or arbitrary query execution are performed.
- Unknown and manual-confirmation findings are unresolved, not passed checks.
- Manual answers describe user-supplied requirements and have not been verified against the API or target tenant.
- An API credential can see only its authorized scope; completed pagination does not certify organization-wide visibility.
- Rule documentation was reviewed on 2026-10-05. Confirm target-tenant and migration-build behavior with ManageEngine.
- Positive counts can be lower bounds; findings may concern overlapping records and must not be summed as unique impacted records.
- Portal-specific findings retain portal IDs; matching numeric record IDs in different portals are not merged.
- Global resources are counted once. Portal users/technicians are membership observations; Assets, Computers and CIs overlap and are not summed into a unique asset population.
- Environment-wide confirmation topics are counted once; source impact and coverage remain portal-specific.
- Field definitions, option/default measurements and allowed schema labels are retained; raw field values, options, defaults and script bodies are excluded.
- Acceptance items are an evidence and decision register. The source scan cannot approve future Cloud migration behavior.
- Integration-key expiration was not queried. No verified read-only expiration API is implemented; key metadata is not required for this assessment.

## Vendor/project questions

### Q1 · Which documented limitations apply to our source environment and proposed target?

#### Confirmed source evidence

- IT Helpdesk (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- IT Helpdesk (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- IT Helpdesk (ID 1) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:1:ATTACHMENT\_SIZE\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:1:NOTE\_ATTACHMENTS\]
- IT Helpdesk (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- IT Helpdesk (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:1:REQUEST\_SCHEDULE\_DATES\]
- IT Helpdesk (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- IT Helpdesk (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- IT Helpdesk (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- IT Helpdesk (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- IT Helpdesk (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- IT Helpdesk (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- IT Helpdesk (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- IT Helpdesk (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- HR (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- HR (ID 2) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:2:ATTACHMENT\_SIZE\]
- HR (ID 2) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:2:NOTE\_ATTACHMENTS\]
- HR (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- HR (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- HR (ID 2) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:2:REQUEST\_SCHEDULE\_DATES\]
- HR (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- HR (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- HR (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- HR (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- HR (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- HR (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- HR (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- HR (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- HR (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Facilities (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]
- Facilities (ID 3) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:3:ATTACHMENT\_SIZE\]
- Facilities (ID 3) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:3:NOTE\_ATTACHMENTS\]
- Facilities (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Facilities (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Facilities (ID 3) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:3:REQUEST\_SCHEDULE\_DATES\]
- Facilities (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Facilities (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Facilities (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Facilities (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Facilities (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Facilities (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]
- Facilities (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- HR (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- HR (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- HR (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- HR (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- HR (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- HR (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- HR (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- HR (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- HR (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- HR (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- HR (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- HR (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- HR (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- HR (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- HR (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- HR (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- HR (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- HR (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- HR (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- HR (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- HR (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- HR (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- HR (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- HR (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Facilities (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Facilities (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Security (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Security (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Security (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target build support, edition, datacenter and effective tenant limits have not been read.

#### Vendor confirmation required

- Confirm supported source builds and the mapping of every selected source portal to a target service desk.

#### Project/business decision required

- Confirm the intended target topology, required modules and acceptance criteria.

### Q2 · How should old records, CMDB, Releases, Projects and custom modules be handled?

#### Confirmed source evidence

- IT Helpdesk (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- IT Helpdesk (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- IT Helpdesk (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- IT Helpdesk (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- IT Helpdesk (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- IT Helpdesk (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- HR (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- HR (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- HR (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- HR (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- HR (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- HR (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- Facilities (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Facilities (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Facilities (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Facilities (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Facilities (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- The scan cannot verify target import coverage, historical-window exceptions or custom-module equivalence.

#### Vendor confirmation required

- Confirm supported migration or retention routes for each portal/module, age group, CMDB relationship and Release/Project subresource.

#### Project/business decision required

- Choose required history retention, source archive access and ownership of data that needs a separate route.

### Q3 · What needs confirmation regarding final-delta migration?

#### Confirmed source evidence

No applicable evidence established; absence or target compatibility is not certified.

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- Source reads cannot establish the future delta's handling of edits, deletes or newly added subentities.

#### Vendor confirmation required

- Confirm reconciliation of changed/deleted records, notes, attachments, approvals and tasks, plus target freshness and rollback behavior.

#### Project/business decision required

- Approve the freeze window, mail transition, delta rehearsal and rollback decision owner.

### Q4 · Which identifiers and relationships require preservation or cross-reference?

#### Confirmed source evidence

- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- Retained IDs, target URLs and email-threading behavior cannot be proven with source credentials.

#### Vendor confirmation required

- Confirm Change ID retention, per-portal ID cross-references, linked/dependent requests, request-change mappings and legacy links.

#### Project/business decision required

- Choose the cross-reference format and tests for each required relationship and historical link.

### Q5 · Which settings, fields, workflows, scripts, reports or modules require reconstruction or licensing?

#### Confirmed source evidence

- IT Helpdesk (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- IT Helpdesk (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- IT Helpdesk (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- IT Helpdesk (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- IT Helpdesk (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- IT Helpdesk (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- HR (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- HR (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- HR (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- HR (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- HR (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- HR (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Facilities (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Facilities (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Facilities (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Facilities (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Facilities (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- HR (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- HR (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- HR (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- HR (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- HR (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- HR (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- HR (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- HR (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- HR (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- HR (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- HR (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- HR (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- HR (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- HR (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- HR (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- HR (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- HR (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- HR (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- HR (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- HR (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- HR (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- HR (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- HR (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- HR (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Facilities (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Facilities (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Security (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Security (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Security (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target entitlements, runtime support, quotas and functional equivalents remain unverified.

#### Vendor confirmation required

- Confirm field/type mapping, SLA and lifecycle/workflow matching, unsupported form actions, reporting paths, module licenses and discovery architecture.

#### Project/business decision required

- Assign owners to reconstruction and external integrations; agree which behaviors must be equivalent at go-live.

### Q6 · What export and recovery capabilities require confirmation?

#### Confirmed source evidence

No applicable evidence established; absence or target compatibility is not certified.

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.

#### Target-cloud unknowns

- The scan does not inspect Cloud backup/export configuration or prove restore and exit capabilities.

#### Vendor confirmation required

- Obtain tenant-specific export completeness/frequency, recovery granularity, RPO/RTO, support involvement and exit commitments.

#### Project/business decision required

- Define retention, recovery objectives, periodic export ownership and when source retirement is permitted.

### Q7 · Which failures or unresolved differences should block migration acceptance?

#### Confirmed source evidence

- IT Helpdesk (ID 1) / multiple: 5 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_ONE\_YEAR\]
- IT Helpdesk (ID 1) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:1:HISTORY\_WINDOW\_FIVE\_YEARS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:LINKED\_REQUESTS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_DEPENDENCIES\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:1:REQUEST\_CHANGE\_LINKS\]
- IT Helpdesk (ID 1) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:1:ATTACHMENT\_SIZE\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:1:NOTE\_ATTACHMENTS\]
- IT Helpdesk (ID 1) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:1:TECHNICIAN\_EMAILS\]
- IT Helpdesk (ID 1) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:1:FIELD\_VALUE\_LENGTHS\]
- IT Helpdesk (ID 1) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:1:REQUEST\_SCHEDULE\_DATES\]
- IT Helpdesk (ID 1) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:1:DUPLICATE\_SERVICE\_TAGS\]
- IT Helpdesk (ID 1) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:1:ASSET\_DATE\_ORDER\]
- IT Helpdesk (ID 1) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:1:WORKFLOW\_REBUILD\]
- IT Helpdesk (ID 1) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:1:QUERY\_REPORTS\]
- IT Helpdesk (ID 1) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:1:TEMPLATE\_COMPLEXITY\]
- IT Helpdesk (ID 1) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:1:RESOLUTION\_LENGTH\]
- IT Helpdesk (ID 1) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:1:PROBLEM\_ANCILLARY\_DATA\]
- IT Helpdesk (ID 1) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- IT Helpdesk (ID 1) / cis: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE\]
- IT Helpdesk (ID 1) / cis: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_ONE\_YEAR\]
- HR (ID 2) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:2:HISTORY\_WINDOW\_FIVE\_YEARS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:LINKED\_REQUESTS\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_DEPENDENCIES\]
- HR (ID 2) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:2:REQUEST\_CHANGE\_LINKS\]
- HR (ID 2) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:2:ATTACHMENT\_SIZE\]
- HR (ID 2) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:2:NOTE\_ATTACHMENTS\]
- HR (ID 2) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:2:TECHNICIAN\_EMAILS\]
- HR (ID 2) / requests: 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:2:FIELD\_VALUE\_LENGTHS\]
- HR (ID 2) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:2:REQUEST\_SCHEDULE\_DATES\]
- HR (ID 2) / computers: 2 affected records observed. Duplicate tags require a supported migration treatment. \[portal:2:DUPLICATE\_SERVICE\_TAGS\]
- HR (ID 2) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:2:ASSET\_DATE\_ORDER\]
- HR (ID 2) / multiple: 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. \[portal:2:WORKFLOW\_REBUILD\]
- HR (ID 2) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:2:QUERY\_REPORTS\]
- HR (ID 2) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:2:TEMPLATE\_COMPLEXITY\]
- HR (ID 2) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:2:RESOLUTION\_LENGTH\]
- HR (ID 2) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:2:PROBLEM\_ANCILLARY\_DATA\]
- HR (ID 2) / requests: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / requests: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- HR (ID 2) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- HR (ID 2) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- HR (ID 2) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / multiple: 4 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_ONE\_YEAR\]
- Facilities (ID 3) / multiple: 1 affected records observed. An agreed historical-data disposition is required. \[portal:3:HISTORY\_WINDOW\_FIVE\_YEARS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:LINKED\_REQUESTS\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_DEPENDENCIES\]
- Facilities (ID 3) / requests: 1 affected records observed. The identified relationship requires a migration disposition. \[portal:3:REQUEST\_CHANGE\_LINKS\]
- Facilities (ID 3) / multiple: 1 observed owner totals exceed both interpretations of 48 MB. \[portal:3:ATTACHMENT\_SIZE\]
- Facilities (ID 3) / requests: 1 affected records observed. Identified note attachments require separate preservation. \[portal:3:NOTE\_ATTACHMENTS\]
- Facilities (ID 3) / technicians: 3 affected records observed. Resolve missing or shared technician email identities. \[portal:3:TECHNICIAN\_EMAILS\]
- Facilities (ID 3) / requests: 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:3:FIELD\_VALUE\_LENGTHS\]
- Facilities (ID 3) / requests: 1 affected records observed. The observed date ordering needs remediation. \[portal:3:REQUEST\_SCHEDULE\_DATES\]
- Facilities (ID 3) / assets: 1 affected records observed. Observed date ordering can change migrated values. \[portal:3:ASSET\_DATE\_ORDER\]
- Facilities (ID 3) / multiple: 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. \[portal:3:WORKFLOW\_REBUILD\]
- Facilities (ID 3) / reports: 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. \[portal:3:QUERY\_REPORTS\]
- Facilities (ID 3) / templates: 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. \[portal:3:TEMPLATE\_COMPLEXITY\]
- Facilities (ID 3) / requests: 1 resolution values measured; 1 exceed the documented limit. \[portal:3:RESOLUTION\_LENGTH\]
- Facilities (ID 3) / problems: 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. \[portal:3:PROBLEM\_ANCILLARY\_DATA\]
- Facilities (ID 3) / changes: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / changes: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / assets: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / assets: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION\]
- Facilities (ID 3) / computers: 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. \[portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE\]
- Facilities (ID 3) / computers: 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. \[portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION\]

#### API coverage limitations

- IT Helpdesk (ID 1) / technicians: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / reports: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 1. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / requests: COMPLETE Records observed: 3. List complete: true.
- IT Helpdesk (ID 1) / assets: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / cmdb: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- IT Helpdesk (ID 1) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / technicians: COMPLETE Records observed: 3. List complete: true.
- HR (ID 2) / reports: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 1. List complete: true.
- HR (ID 2) / projects: PERMISSION\_DENIED Records observed: —. List complete: false.
- HR (ID 2) / assets: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / cmdb: COMPLETE Records observed: 2. List complete: true.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- HR (ID 2) / requests: Only sampled parents/subresources were inspected; unknown is not zero. Records observed: 1. List complete: false.
- Facilities (ID 3) / technicians: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / reports: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / assets: COMPLETE Records observed: 3. List complete: true.
- Facilities (ID 3) / releases: MODULE\_NOT\_AVAILABLE Records observed: —. List complete: false.
- Facilities (ID 3) / assets: COMPLETE Records observed: 1. List complete: true.
- Facilities (ID 3) / cmdb: COMPLETE Records observed: 2. List complete: true.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / sites: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / groups: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / technicians: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / users: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / reports: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / requests: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / changes: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / problems: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / projects: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / releases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / assets: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / cmdb: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / contracts: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Security (ID 4) / purchases: PORTAL\_NOT\_ACCESSIBLE Records observed: —. List complete: false.
- Environment / orgusers: COMPLETE Records observed: 2. List complete: true.
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_REQUESTS\_COVERAGE\]
- IT Helpdesk (ID 1) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_REQUESTS\_CAPACITY\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROBLEMS\_COVERAGE\]
- IT Helpdesk (ID 1) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROBLEMS\_CAPACITY\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CHANGES\_COVERAGE\]
- IT Helpdesk (ID 1) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CHANGES\_CAPACITY\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PROJECTS\_COVERAGE\]
- IT Helpdesk (ID 1) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PROJECTS\_CAPACITY\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_RELEASES\_COVERAGE\]
- IT Helpdesk (ID 1) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_RELEASES\_CAPACITY\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_USERS\_COVERAGE\]
- IT Helpdesk (ID 1) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_USERS\_CAPACITY\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_TECHNICIANS\_COVERAGE\]
- IT Helpdesk (ID 1) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_TECHNICIANS\_CAPACITY\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_ASSETS\_COVERAGE\]
- IT Helpdesk (ID 1) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_ASSETS\_CAPACITY\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_COMPUTERS\_COVERAGE\]
- IT Helpdesk (ID 1) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_COMPUTERS\_CAPACITY\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CIS\_COVERAGE\]
- IT Helpdesk (ID 1) / cis: 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:1:FIELD\_CIS\_CAPACITY\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_CONTRACTS\_COVERAGE\]
- IT Helpdesk (ID 1) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_CONTRACTS\_CAPACITY\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:1:FIELD\_PURCHASES\_COVERAGE\]
- IT Helpdesk (ID 1) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:1:FIELD\_PURCHASES\_CAPACITY\]
- HR (ID 2) / requests: 3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_REQUESTS\_COVERAGE\]
- HR (ID 2) / requests: 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_REQUESTS\_CAPACITY\]
- HR (ID 2) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROBLEMS\_COVERAGE\]
- HR (ID 2) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROBLEMS\_CAPACITY\]
- HR (ID 2) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CHANGES\_COVERAGE\]
- HR (ID 2) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CHANGES\_CAPACITY\]
- HR (ID 2) / projects: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PROJECTS\_COVERAGE\]
- HR (ID 2) / projects: Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PROJECTS\_CAPACITY\]
- HR (ID 2) / releases: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_RELEASES\_COVERAGE\]
- HR (ID 2) / releases: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_RELEASES\_CAPACITY\]
- HR (ID 2) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_USERS\_COVERAGE\]
- HR (ID 2) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_USERS\_CAPACITY\]
- HR (ID 2) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_TECHNICIANS\_COVERAGE\]
- HR (ID 2) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_TECHNICIANS\_CAPACITY\]
- HR (ID 2) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_ASSETS\_COVERAGE\]
- HR (ID 2) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_ASSETS\_CAPACITY\]
- HR (ID 2) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_COMPUTERS\_COVERAGE\]
- HR (ID 2) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_COMPUTERS\_CAPACITY\]
- HR (ID 2) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CIS\_COVERAGE\]
- HR (ID 2) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:2:FIELD\_CIS\_CAPACITY\]
- HR (ID 2) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_CONTRACTS\_COVERAGE\]
- HR (ID 2) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_CONTRACTS\_CAPACITY\]
- HR (ID 2) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:2:FIELD\_PURCHASES\_COVERAGE\]
- HR (ID 2) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:2:FIELD\_PURCHASES\_CAPACITY\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_REQUESTS\_COVERAGE\]
- Facilities (ID 3) / requests: 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_REQUESTS\_CAPACITY\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROBLEMS\_COVERAGE\]
- Facilities (ID 3) / problems: 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROBLEMS\_CAPACITY\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CHANGES\_COVERAGE\]
- Facilities (ID 3) / changes: 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CHANGES\_CAPACITY\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PROJECTS\_COVERAGE\]
- Facilities (ID 3) / projects: 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PROJECTS\_CAPACITY\]
- Facilities (ID 3) / releases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_RELEASES\_COVERAGE\]
- Facilities (ID 3) / releases: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_RELEASES\_CAPACITY\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_USERS\_COVERAGE\]
- Facilities (ID 3) / users: 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_USERS\_CAPACITY\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_TECHNICIANS\_COVERAGE\]
- Facilities (ID 3) / technicians: Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_TECHNICIANS\_CAPACITY\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_ASSETS\_COVERAGE\]
- Facilities (ID 3) / assets: 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_ASSETS\_CAPACITY\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_COMPUTERS\_COVERAGE\]
- Facilities (ID 3) / computers: 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_COMPUTERS\_CAPACITY\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CIS\_COVERAGE\]
- Facilities (ID 3) / cis: 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. \[portal:3:FIELD\_CIS\_CAPACITY\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_CONTRACTS\_COVERAGE\]
- Facilities (ID 3) / contracts: Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_CONTRACTS\_CAPACITY\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry. \[portal:3:FIELD\_PURCHASES\_COVERAGE\]
- Facilities (ID 3) / purchases: Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. \[portal:3:FIELD\_PURCHASES\_CAPACITY\]
- Security (ID 4) / requests: 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. \[portal:4:REQUEST\_FIELD\_CAPACITY\]
- Security (ID 4) / requests: No matching issue established from 0 checked records; collection or required-field coverage is incomplete. \[portal:4:FIELD\_NAME\_COLLISIONS\]
- Security (ID 4) / requests: 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. \[portal:4:FIELD\_VALUE\_LENGTHS\]

#### Target-cloud unknowns

- Target reconciliation, permissions, workflow execution, recovery and migration success are not validated by this scan.

#### Vendor confirmation required

- Agree evidence requirements and exception handling for every unresolved migration difference.

#### Project/business decision required

- Approve go/no-go thresholds and accountable owners; resolve or explicitly accept each blocker before cutover.


## Acceptance blockers

Resolve or explicitly accept applicable source exceptions and evidence gaps, then validate the target. This is not a go-live approval.

| Portal / scope | Module | Reference | Acceptance item | Reason | Required resolution |
| --- | --- | --- | --- | --- | --- |
| Environment | reports | POWER\_BI\_REQUIREMENTS | SOURCE\_EXCEPTION | User-supplied reporting requirements exceed at least one documented native-integration behavior. | Validate the native connector against reporting requirements or design a separate historical extraction path. |
| Environment | automation | AUTOMATION\_RUNTIME | SOURCE\_EXCEPTION | The user reports local scripts in use; runtime and integration review is required. | Inventory script dependencies and actual execution rates; verify target datacenter support and quotas. Definition counts are not execution counts. |
| IT Helpdesk (ID 1) | multiple | portal:1:HISTORY\_WINDOW\_ONE\_YEAR | SOURCE\_EXCEPTION | 5 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | portal:1:HISTORY\_WINDOW\_FIVE\_YEARS | SOURCE\_EXCEPTION | 1 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| IT Helpdesk (ID 1) | multiple | portal:1:LEGACY\_HISTORY | SOURCE\_EXCEPTION | History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data. | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| IT Helpdesk (ID 1) | requests | portal:1:LINKED\_REQUESTS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | portal:1:REQUEST\_DEPENDENCIES | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | requests | portal:1:REQUEST\_CHANGE\_LINKS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | archived\_requests | portal:1:ARCHIVED\_SUBENTITIES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | multiple | portal:1:ATTACHMENT\_SIZE | SOURCE\_EXCEPTION | 1 observed owner totals exceed both interpretations of 48 MB. | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| IT Helpdesk (ID 1) | requests | portal:1:NOTE\_ATTACHMENTS | SOURCE\_EXCEPTION | 1 affected records observed. Identified note attachments require separate preservation. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | technicians | portal:1:TECHNICIAN\_EMAILS | SOURCE\_EXCEPTION | 3 affected records observed. Resolve missing or shared technician email identities. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | users | portal:1:APPROVER\_LOGIN | EVIDENCE\_GAP | 0 explicit non-login approver references found; CAB and unresolved memberships still need validation. | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| IT Helpdesk (ID 1) | requests | portal:1:FIELD\_VALUE\_LENGTHS | SOURCE\_EXCEPTION | 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| IT Helpdesk (ID 1) | requests | portal:1:REQUEST\_SCHEDULE\_DATES | SOURCE\_EXCEPTION | 1 affected records observed. The observed date ordering needs remediation. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | computers | portal:1:DUPLICATE\_SERVICE\_TAGS | SOURCE\_EXCEPTION | 2 affected records observed. Duplicate tags require a supported migration treatment. | Review the identified records before migration. |
| IT Helpdesk (ID 1) | computers | portal:1:VM\_HOST\_LINKS | EVIDENCE\_GAP | 0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check. | Validate VM classification and host relationships across the complete computer inventory. |
| IT Helpdesk (ID 1) | multiple | portal:1:WORKFLOW\_REBUILD | SOURCE\_EXCEPTION | 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| IT Helpdesk (ID 1) | templates | portal:1:FORM\_SCRIPT\_ACTIONS | EVIDENCE\_GAP | 0 template rule collections inspected; 0 templates contain explicit script actions. | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| IT Helpdesk (ID 1) | reports | portal:1:QUERY\_REPORTS | SOURCE\_EXCEPTION | 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| IT Helpdesk (ID 1) | templates | portal:1:TEMPLATE\_COMPLEXITY | SOURCE\_EXCEPTION | 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. | Review identified template structures and all uncollected task/resource/question details. |
| IT Helpdesk (ID 1) | problems | portal:1:PROBLEM\_ANCILLARY\_DATA | SOURCE\_EXCEPTION | 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. | Record the migration disposition for problem ancillary content and configuration. |
| IT Helpdesk (ID 1) | requests | portal:1:FIELD\_REQUESTS\_CAPACITY | EVIDENCE\_GAP | 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | requests | portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | problems | portal:1:FIELD\_PROBLEMS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | portal:1:FIELD\_CHANGES\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | changes | portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | projects | portal:1:FIELD\_PROJECTS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | releases | portal:1:FIELD\_RELEASES\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | users | portal:1:FIELD\_USERS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | technicians | portal:1:FIELD\_TECHNICIANS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | portal:1:FIELD\_ASSETS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | assets | portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | portal:1:FIELD\_COMPUTERS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | computers | portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | portal:1:FIELD\_CIS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | cis | portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | contracts | portal:1:FIELD\_CONTRACTS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | purchases | portal:1:FIELD\_PURCHASES\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| IT Helpdesk (ID 1) | multiple | portal:1:OPERATION\_COVERAGE | EVIDENCE\_GAP | 2 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories. | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |
| HR (ID 2) | multiple | portal:2:HISTORY\_WINDOW\_ONE\_YEAR | SOURCE\_EXCEPTION | 4 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | portal:2:HISTORY\_WINDOW\_FIVE\_YEARS | SOURCE\_EXCEPTION | 1 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| HR (ID 2) | multiple | portal:2:LEGACY\_HISTORY | SOURCE\_EXCEPTION | History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data. | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| HR (ID 2) | requests | portal:2:LINKED\_REQUESTS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| HR (ID 2) | requests | portal:2:REQUEST\_DEPENDENCIES | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| HR (ID 2) | requests | portal:2:REQUEST\_CHANGE\_LINKS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| HR (ID 2) | archived\_requests | portal:2:ARCHIVED\_SUBENTITIES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| HR (ID 2) | multiple | portal:2:ATTACHMENT\_SIZE | SOURCE\_EXCEPTION | 1 observed owner totals exceed both interpretations of 48 MB. | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| HR (ID 2) | requests | portal:2:NOTE\_ATTACHMENTS | SOURCE\_EXCEPTION | 1 affected records observed. Identified note attachments require separate preservation. | Review the identified records before migration. |
| HR (ID 2) | technicians | portal:2:TECHNICIAN\_EMAILS | SOURCE\_EXCEPTION | 3 affected records observed. Resolve missing or shared technician email identities. | Review the identified records before migration. |
| HR (ID 2) | users | portal:2:APPROVER\_LOGIN | EVIDENCE\_GAP | 0 explicit non-login approver references found; CAB and unresolved memberships still need validation. | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| HR (ID 2) | requests | portal:2:FIELD\_VALUE\_LENGTHS | SOURCE\_EXCEPTION | 2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| HR (ID 2) | requests | portal:2:REQUEST\_SCHEDULE\_DATES | SOURCE\_EXCEPTION | 1 affected records observed. The observed date ordering needs remediation. | Review the identified records before migration. |
| HR (ID 2) | computers | portal:2:DUPLICATE\_SERVICE\_TAGS | SOURCE\_EXCEPTION | 2 affected records observed. Duplicate tags require a supported migration treatment. | Review the identified records before migration. |
| HR (ID 2) | computers | portal:2:VM\_HOST\_LINKS | EVIDENCE\_GAP | 0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check. | Validate VM classification and host relationships across the complete computer inventory. |
| HR (ID 2) | multiple | portal:2:WORKFLOW\_REBUILD | SOURCE\_EXCEPTION | 0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction. | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| HR (ID 2) | templates | portal:2:FORM\_SCRIPT\_ACTIONS | EVIDENCE\_GAP | 0 template rule collections inspected; 0 templates contain explicit script actions. | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| HR (ID 2) | reports | portal:2:QUERY\_REPORTS | SOURCE\_EXCEPTION | 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| HR (ID 2) | templates | portal:2:TEMPLATE\_COMPLEXITY | SOURCE\_EXCEPTION | 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. | Review identified template structures and all uncollected task/resource/question details. |
| HR (ID 2) | problems | portal:2:PROBLEM\_ANCILLARY\_DATA | SOURCE\_EXCEPTION | 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. | Record the migration disposition for problem ancillary content and configuration. |
| HR (ID 2) | requests | portal:2:FIELD\_REQUESTS\_CAPACITY | EVIDENCE\_GAP | 3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | requests | portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | requests | portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | problems | portal:2:FIELD\_PROBLEMS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | portal:2:FIELD\_CHANGES\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | changes | portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | projects | portal:2:FIELD\_PROJECTS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | releases | portal:2:FIELD\_RELEASES\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | users | portal:2:FIELD\_USERS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | technicians | portal:2:FIELD\_TECHNICIANS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | portal:2:FIELD\_ASSETS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | assets | portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | portal:2:FIELD\_COMPUTERS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | computers | portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | cis | portal:2:FIELD\_CIS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | contracts | portal:2:FIELD\_CONTRACTS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | purchases | portal:2:FIELD\_PURCHASES\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| HR (ID 2) | multiple | portal:2:OPERATION\_COVERAGE | EVIDENCE\_GAP | 3 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories. | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |
| Facilities (ID 3) | multiple | portal:3:HISTORY\_WINDOW\_ONE\_YEAR | SOURCE\_EXCEPTION | 4 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | portal:3:HISTORY\_WINDOW\_FIVE\_YEARS | SOURCE\_EXCEPTION | 1 affected records observed. An agreed historical-data disposition is required. | Confirm the required history window and vendor-supported handling for these age groups. |
| Facilities (ID 3) | multiple | portal:3:LEGACY\_HISTORY | SOURCE\_EXCEPTION | History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data. | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Facilities (ID 3) | requests | portal:3:LINKED\_REQUESTS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| Facilities (ID 3) | requests | portal:3:REQUEST\_DEPENDENCIES | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| Facilities (ID 3) | requests | portal:3:REQUEST\_CHANGE\_LINKS | SOURCE\_EXCEPTION | 1 affected records observed. The identified relationship requires a migration disposition. | Review the identified records before migration. |
| Facilities (ID 3) | archived\_requests | portal:3:ARCHIVED\_SUBENTITIES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Facilities (ID 3) | multiple | portal:3:ATTACHMENT\_SIZE | SOURCE\_EXCEPTION | 1 observed owner totals exceed both interpretations of 48 MB. | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Facilities (ID 3) | requests | portal:3:NOTE\_ATTACHMENTS | SOURCE\_EXCEPTION | 1 affected records observed. Identified note attachments require separate preservation. | Review the identified records before migration. |
| Facilities (ID 3) | technicians | portal:3:TECHNICIAN\_EMAILS | SOURCE\_EXCEPTION | 3 affected records observed. Resolve missing or shared technician email identities. | Review the identified records before migration. |
| Facilities (ID 3) | users | portal:3:APPROVER\_LOGIN | EVIDENCE\_GAP | 0 explicit non-login approver references found; CAB and unresolved memberships still need validation. | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Facilities (ID 3) | requests | portal:3:FIELD\_VALUE\_LENGTHS | SOURCE\_EXCEPTION | 1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| Facilities (ID 3) | requests | portal:3:REQUEST\_SCHEDULE\_DATES | SOURCE\_EXCEPTION | 1 affected records observed. The observed date ordering needs remediation. | Review the identified records before migration. |
| Facilities (ID 3) | computers | portal:3:VM\_HOST\_LINKS | EVIDENCE\_GAP | 0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check. | Validate VM classification and host relationships across the complete computer inventory. |
| Facilities (ID 3) | multiple | portal:3:WORKFLOW\_REBUILD | SOURCE\_EXCEPTION | 0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction. | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Facilities (ID 3) | templates | portal:3:FORM\_SCRIPT\_ACTIONS | EVIDENCE\_GAP | 0 template rule collections inspected; 0 templates contain explicit script actions. | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Facilities (ID 3) | reports | portal:3:QUERY\_REPORTS | SOURCE\_EXCEPTION | 1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established. | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Facilities (ID 3) | templates | portal:3:TEMPLATE\_COMPLEXITY | SOURCE\_EXCEPTION | 2 templates exposed relevant nested metadata; 2 exceed a documented count limit. | Review identified template structures and all uncollected task/resource/question details. |
| Facilities (ID 3) | problems | portal:3:PROBLEM\_ANCILLARY\_DATA | SOURCE\_EXCEPTION | 1 problems have observed ancillary content; unexposed problem configuration remains unassessed. | Record the migration disposition for problem ancillary content and configuration. |
| Facilities (ID 3) | requests | portal:3:FIELD\_REQUESTS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | problems | portal:3:FIELD\_PROBLEMS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | portal:3:FIELD\_CHANGES\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | changes | portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | projects | portal:3:FIELD\_PROJECTS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | releases | portal:3:FIELD\_RELEASES\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | users | portal:3:FIELD\_USERS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | technicians | portal:3:FIELD\_TECHNICIANS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | portal:3:FIELD\_ASSETS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | assets | portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | portal:3:FIELD\_COMPUTERS\_CAPACITY | EVIDENCE\_GAP | 2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE | SOURCE\_EXCEPTION | 1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | computers | portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION | SOURCE\_EXCEPTION | 1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | cis | portal:3:FIELD\_CIS\_CAPACITY | EVIDENCE\_GAP | 1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | contracts | portal:3:FIELD\_CONTRACTS\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | purchases | portal:3:FIELD\_PURCHASES\_CAPACITY | EVIDENCE\_GAP | Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation. | Confirm source definitions, target mapping and field behavior in the trial migration. |
| Facilities (ID 3) | multiple | portal:3:OPERATION\_COVERAGE | EVIDENCE\_GAP | 1 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories. | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |
| Security (ID 4) | multiple | portal:4:HISTORY\_WINDOW\_ONE\_YEAR | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | portal:4:HISTORY\_WINDOW\_FIVE\_YEARS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Confirm the required history window and vendor-supported handling for these age groups. |
| Security (ID 4) | multiple | portal:4:LEGACY\_HISTORY | SOURCE\_EXCEPTION | History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data. | Agree how legacy history will be preserved and validated; ticket counts cannot verify it. |
| Security (ID 4) | requests | portal:4:LINKED\_REQUESTS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | requests | portal:4:REQUEST\_DEPENDENCIES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | requests | portal:4:REQUEST\_CHANGE\_LINKS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | archived\_requests | portal:4:ARCHIVED\_SUBENTITIES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | multiple | portal:4:ATTACHMENT\_SIZE | EVIDENCE\_GAP | No oversized owner was established; unseen attachment subresources and missing sizes remain unverified. | Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity. |
| Security (ID 4) | requests | portal:4:NOTE\_ATTACHMENTS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | technicians | portal:4:TECHNICIAN\_EMAILS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | users | portal:4:APPROVER\_LOGIN | EVIDENCE\_GAP | 0 explicit non-login approver references found; CAB and unresolved memberships still need validation. | Validate login access for every service approver and CAB member; missing user fields are inconclusive. |
| Security (ID 4) | requests | portal:4:REQUEST\_FIELD\_CAPACITY | EVIDENCE\_GAP | 0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250. | Validate every field type and target entitlement; free-tier and other-module limits differ. |
| Security (ID 4) | requests | portal:4:FIELD\_NAME\_COLLISIONS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | requests | portal:4:FIELD\_VALUE\_LENGTHS | EVIDENCE\_GAP | 0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure. | Review identified values and obtain complete definitions/defaults/options before accepting field compatibility. |
| Security (ID 4) | requests | portal:4:REQUEST\_SCHEDULE\_DATES | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | computers | portal:4:DUPLICATE\_SERVICE\_TAGS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Review the identified records before migration. |
| Security (ID 4) | computers | portal:4:VM\_HOST\_LINKS | EVIDENCE\_GAP | 0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check. | Validate VM classification and host relationships across the complete computer inventory. |
| Security (ID 4) | multiple | portal:4:WORKFLOW\_REBUILD | EVIDENCE\_GAP | 0 configuration objects and 0 record references observed. Source inventory does not verify target reconstruction. | Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent. |
| Security (ID 4) | templates | portal:4:FORM\_SCRIPT\_ACTIONS | EVIDENCE\_GAP | 0 template rule collections inspected; 0 templates contain explicit script actions. | Review script actions and unexposed Change form rules; test supported target scripting behavior. |
| Security (ID 4) | reports | portal:4:QUERY\_REPORTS | EVIDENCE\_GAP | No matching issue established from 0 checked records; collection or required-field coverage is incomplete. | Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment. |
| Security (ID 4) | templates | portal:4:TEMPLATE\_COMPLEXITY | EVIDENCE\_GAP | 0 templates exposed relevant nested metadata; 0 exceed a documented count limit. | Review identified template structures and all uncollected task/resource/question details. |
| Security (ID 4) | problems | portal:4:PROBLEM\_ANCILLARY\_DATA | EVIDENCE\_GAP | 0 problems have observed ancillary content; unexposed problem configuration remains unassessed. | Record the migration disposition for problem ancillary content and configuration. |
| Security (ID 4) | multiple | portal:4:OPERATION\_COVERAGE | EVIDENCE\_GAP | 19 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories. | Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403. |
| Environment | migration\_acceptance | Q1 | AGREEMENT\_REQUIRED | Which documented limitations apply to our source environment and proposed target? | Confirm supported source builds and the mapping of every selected source portal to a target service desk. Confirm the intended target topology, required modules and acceptance criteria. |
| Environment | migration\_acceptance | Q2 | AGREEMENT\_REQUIRED | How should old records, CMDB, Releases, Projects and custom modules be handled? | Confirm supported migration or retention routes for each portal/module, age group, CMDB relationship and Release/Project subresource. Choose required history retention, source archive access and ownership of data that needs a separate route. |
| Environment | migration\_acceptance | Q3 | AGREEMENT\_REQUIRED | What needs confirmation regarding final-delta migration? | Confirm reconciliation of changed/deleted records, notes, attachments, approvals and tasks, plus target freshness and rollback behavior. Approve the freeze window, mail transition, delta rehearsal and rollback decision owner. |
| Environment | migration\_acceptance | Q4 | AGREEMENT\_REQUIRED | Which identifiers and relationships require preservation or cross-reference? | Confirm Change ID retention, per-portal ID cross-references, linked/dependent requests, request-change mappings and legacy links. Choose the cross-reference format and tests for each required relationship and historical link. |
| Environment | migration\_acceptance | Q5 | AGREEMENT\_REQUIRED | Which settings, fields, workflows, scripts, reports or modules require reconstruction or licensing? | Confirm field/type mapping, SLA and lifecycle/workflow matching, unsupported form actions, reporting paths, module licenses and discovery architecture. Assign owners to reconstruction and external integrations; agree which behaviors must be equivalent at go-live. |
| Environment | migration\_acceptance | Q6 | AGREEMENT\_REQUIRED | What export and recovery capabilities require confirmation? | Obtain tenant-specific export completeness/frequency, recovery granularity, RPO/RTO, support involvement and exit commitments. Define retention, recovery objectives, periodic export ownership and when source retirement is permitted. |
| Environment | migration\_acceptance | Q7 | AGREEMENT\_REQUIRED | Which failures or unresolved differences should block migration acceptance? | Agree evidence requirements and exception handling for every unresolved migration difference. Approve go/no-go thresholds and accountable owners; resolve or explicitly accept each blocker before cutover. |

## Detailed findings and measured evidence

### API\_VISIBILITY · Credential visibility

**Scope:** Environment / topology  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

4 portals discovered; 4 selected; 4 had collection attempts. Directory metadata may use a separate authorized credential or a verified local list. Module reads use the integration key; hidden or unauthorized portals and records cannot be certified.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| discovered | 4 |
| selected | 4 |
| assessed | 4 |
| discovery\_complete | true |

**Action:** Confirm the assessed instance and read visibility with its administrator.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### SOURCE\_BUILD · Source build prerequisite

**Scope:** Environment / platform  
**Status:** NO\_ISSUE\_OBSERVED  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

User-supplied answer (not API-verified) identifies build 15100; the documented migration baseline is 14810.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| build | 15100 |
| minimum\_build | 14810 |
| scope | environment |
| portal\_id | Not established |
| portal\_name | Not established |

**Action:** Confirm the supported migration build and any required upgrade with ManageEngine.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### POWER\_BI\_REQUIREMENTS · Native Power BI reporting requirements

**Scope:** Environment / reports  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

User-supplied reporting requirements exceed at least one documented native-integration behavior.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| required\_history\_years | 7.0 |
| max\_dashboard\_lag\_minutes | 15.0 |
| needs\_power\_bi | true |
| native\_refresh\_minutes | 120 |
| native\_request\_history\_years | 1 |
| scope | environment |
| portal\_id | Not established |
| portal\_name | Not established |

**Action:** Validate the native connector against reporting requirements or design a separate historical extraction path.

**Sources:** [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### REPORT\_DESCRIPTION\_REQUIREMENTS · Full descriptions in reporting

**Scope:** Environment / reports  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

The user requires full descriptions; the actual report/extraction path needs validation. 

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| needs\_full\_descriptions\_user\_supplied | true |
| scope | environment |
| portal\_id | Not established |
| portal\_name | Not established |

**Action:** Test required full descriptions in the selected reporting path. The generic Cloud report FAQ describes a 250-character display limit; this does not prove a native Power BI limit.

**Sources:** [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### ADMIN\_AUDIT\_RETENTION · Cloud administrative audit retention

**Scope:** Environment / audit  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

The user-supplied administrative audit requirement exceeds three years.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| required\_years | 7.0 |
| native\_years | 3 |
| scope | environment |
| portal\_id | Not established |
| portal\_name | Not established |

**Action:** Plan complete periodic exports when needed; administrative logs are distinct from ticket-history retention.

**Sources:** [audit](<https://help.sdpondemand.com/audit-log>)

### AUTOMATION\_RUNTIME · Automation runtimes and execution budgets

**Scope:** Environment / automation  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

The user reports local scripts in use; runtime and integration review is required.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| uses\_local\_scripts\_user\_supplied | true |
| scope | environment |
| portal\_id | Not established |
| portal\_name | Not established |

**Action:** Inventory script dependencies and actual execution rates; verify target datacenter support and quotas. Definition counts are not execution counts.

**Sources:** [functions](<https://help.sdpondemand.com/custom-functions>), [java\_functions](<https://help.sdpondemand.com/java-in-custom-function>), [node\_functions](<https://help.sdpondemand.com/nodejs-in-custom-function>)

### TARGET\_LICENSE · Target edition and licensed capacity

**Scope:** Environment / licensing  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

User-supplied target edition: Enterprise. A target region was supplied but is not API-verified. Target entitlement, technician seats, asset capacity and add-ons require written confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| scope | portal |
| resource | assets |
| records\_observed | 5 |
| collections\_unknown | 1 |

| Field | Value |
| --- | --- |
| scope | portal |
| resource | computers |
| records\_observed | 5 |
| collections\_unknown | 1 |

| Field | Value |
| --- | --- |
| scope | portal |
| resource | technicians |
| records\_observed | 9 |
| collections\_unknown | 1 |

**Action:** Match the source feature inventory and visible capacities to the target order and tenant limits.

**Sources:** [editions](<https://www.manageengine.com/products/service-desk/cloud/online-helpdesk-comparison.html>), [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### DISCOVERY\_NETWORK · Asset discovery and network continuity

**Scope:** Environment / assets  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

Source asset records cannot establish working Cloud discovery, probe coverage or network access.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| scope | portal |
| resource | assets |
| records\_observed | 5 |
| collections\_unknown | 1 |

| Field | Value |
| --- | --- |
| scope | portal |
| resource | computers |
| records\_observed | 5 |
| collections\_unknown | 1 |

| Field | Value |
| --- | --- |
| scope | portal |
| resource | sites |
| records\_observed | 3 |
| collections\_unknown | 1 |

**Action:** Confirm discovery architecture and test repeated scans from every required network segment.

**Sources:** [editions](<https://www.manageengine.com/products/service-desk/cloud/online-helpdesk-comparison.html>)

### DELTA\_CUTOVER · Final delta and cutover behavior

**Scope:** Environment / cutover  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

A source-only read cannot validate delta semantics, target freshness, write-freeze duration or rollback.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Obtain vendor answers on changed/deleted records and subentities; rehearse final delta, mail transition, reconciliation and rollback.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### BACKUP\_RECOVERY · Target export and recovery commitments

**Scope:** Environment / recovery  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

Customer export and recovery capabilities require tenant-specific confirmation. Public export and backup guidance is not fully aligned.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Agree export completeness, frequency, restore granularity, RPO/RTO, support involvement and exit arrangements; demonstrate them before retiring the source.

**Sources:** [exports](<https://help.sdpondemand.com/export-data>), [admin\_faq](<https://pitstop.manageengine.com/portal/en/kb/articles/admin>)

### EXTERNAL\_INTEGRATIONS · External integrations and email behavior

**Scope:** Environment / integrations  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

ServiceDesk Plus API inventory cannot enumerate all external flows, database consumers, jobs or old-email reply paths.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Inventory external automation/report consumers, replace authentication and endpoints, and test old-email threading and failure recovery.

**Sources:** [email\_behavior](<https://pitstop.manageengine.com/portal/en/kb/articles/general-faq>), [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>), [functions](<https://help.sdpondemand.com/custom-functions>)

### portal:1:HISTORY\_WINDOW\_ONE\_YEAR · Module records older than 1 year(s)

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

5 affected records observed. An agreed historical-data disposition is required.

Affected: 5 \| Examined: 6

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 102 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1704844800000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1707523200000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1735689600000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 701 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1704844800000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:1:HISTORY\_WINDOW\_FIVE\_YEARS · Module records older than 5 year(s)

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. An agreed historical-data disposition is required.

Affected: 1 \| Examined: 6

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 5 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:1:LEGACY\_HISTORY · Historical audit-detail preservation

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Agree how legacy history will be preserved and validated; ticket counts cannot verify it.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:LINKED\_REQUESTS · Linked-request relationships

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:REQUEST\_DEPENDENCIES · Request dependencies

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:REQUEST\_CHANGE\_LINKS · Request and change associations

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:ARCHIVED\_SUBENTITIES · Archived-request subentity exposure

**Scope:** IT Helpdesk (ID 1) / archived\_requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:1:ATTACHMENT\_SIZE · Attachment-size exposure

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 observed owner totals exceed both interpretations of 48 MB.

Affected: 1 \| Examined: 5

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| known\_attachment\_bytes | 55000000 |
| missing\_sizes | 0 |
| decimal\_limit | 48000000 |
| binary\_limit | 50331648 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:NOTE\_ATTACHMENTS · Attachments on request notes

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Identified note attachments require separate preservation.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 801 |
| parent\_id | 101 |
| attachment\_count | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:TECHNICIAN\_EMAILS · Technician email readiness

**Scope:** IT Helpdesk (ID 1) / technicians  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

3 affected records observed. Resolve missing or shared technician email identities.

Affected: 3 \| Examined: 3

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 203 |
| missing\_email | true |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 201 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 202 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:1:APPROVER\_LOGIN · Approver and CAB login access

**Scope:** IT Helpdesk (ID 1) / users  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit non-login approver references found; CAB and unresolved memberships still need validation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate login access for every service approver and CAB member; missing user fields are inconclusive.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_VALUE\_LENGTHS · Additional-field value sizes

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure.

Affected: 1 \| Examined: 2

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| field\_id | 71 |
| character\_count | 300 |
| limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review identified values and obtain complete definitions/defaults/options before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>)

### portal:1:REQUEST\_SCHEDULE\_DATES · Request scheduled-date consistency

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The observed date ordering needs remediation.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| schedule\_precedes\_creation | true |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:DUPLICATE\_SERVICE\_TAGS · Computer service-tag collisions

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 affected records observed. Duplicate tags require a supported migration treatment.

Affected: 2 \| Examined: 2

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 10001 |
| duplicate\_tag\_group\_size | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 10002 |
| duplicate\_tag\_group\_size | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:VM\_HOST\_LINKS · Virtual-machine host references

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate VM classification and host relationships across the complete computer inventory.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:ASSET\_DATE\_ORDER · Asset date-order consistency

**Scope:** IT Helpdesk (ID 1) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Observed date ordering can change migrated values.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 10001 |
| invalid\_date\_order | true |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:WORKFLOW\_REBUILD · Workflow and SLA reconstruction

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 51 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 61 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 102 |
| configuration\_id | 51 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| configuration\_id | 41 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:1:FORM\_SCRIPT\_ACTIONS · Form-script action compatibility

**Scope:** IT Helpdesk (ID 1) / templates  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 template rule collections inspected; 0 templates contain explicit script actions.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review script actions and unexposed Change form rules; test supported target scripting behavior.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:QUERY\_REPORTS · Query-report inventory review

**Scope:** IT Helpdesk (ID 1) / reports  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established.

Affected: 1 \| Examined: 1

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 13001 |
| query\_report | true |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### portal:1:TEMPLATE\_COMPLEXITY · Template task and resource limits

**Scope:** IT Helpdesk (ID 1) / templates  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 templates exposed relevant nested metadata; 2 exceed a documented count limit.

Affected: 2 \| Examined: 2

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 11 |
| associated\_tasks | 201 |
| task\_limit | 200 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 12 |
| resource\_count | 21 |
| resource\_limit | 20 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Review identified template structures and all uncollected task/resource/question details.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:RESOLUTION\_LENGTH · Request resolution length

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 resolution values measured; 1 exceed the documented limit.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| character\_count | 66000 |
| limit | 65536 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Preserve identified long resolutions and inspect uncollected historical text fields.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:RECURRING\_MAINTENANCE · Recurring maintenance schedules

**Scope:** IT Helpdesk (ID 1) / maintenances  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit schedules observed; unexposed recurrence settings require a manual inventory.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Inventory recurring maintenance and rebuild its schedule at the agreed migration stage.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:MODULE\_MIGRATION\_SCOPE · CMDB, Releases and custom-module migration scope

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

4 records or type definitions observed in these inventories. An absent or denied endpoint does not prove a module is unused.

Affected: Not established \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 12001 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 12002 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 11001 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| entity\_id | 601 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible.

**Sources:** [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:1:PROBLEM\_ANCILLARY\_DATA · Problem ancillary-data preservation

**Scope:** IT Helpdesk (ID 1) / problems  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 problems have observed ancillary content; unexposed problem configuration remains unassessed.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| ancillary\_categories\_present | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Record the migration disposition for problem ancillary content and configuration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:CHANGE\_IDENTIFIERS · Change identifier preservation

**Scope:** IT Helpdesk (ID 1) / changes  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

1 Change IDs observed. Source inspection cannot establish target ID preservation.

Affected: Not established \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm Change ID retention with support and require a cross-reference for any changed identifiers.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:1:ACCESS\_MAPPING · Role and organization-membership mapping

**Scope:** IT Helpdesk (ID 1) / identity  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 role definitions observed; equivalent target permissions and membership have not been validated.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Test permitted and denied access for representative roles, sites, groups and sensitive queues.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_COVERAGE · requests: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 3 |
| custom\_fields\_confirmed | 3 |
| metadata\_targets\_successful | 2 |
| metadata\_targets\_total | 2 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_CAPACITY · requests: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 3 |
| documented\_limit | 250 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_NAME\_MAPPING · requests: additional-field name mapping

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 groups of field labels match after case folding. These are mapping candidates. The documented case-insensitive rule-name restriction does not establish a universal UDF-name failure.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 73 |
| internal\_name | udf\_case |
| field\_path | udf\_fields.udf\_case |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE · requests: oversized field defaults or options

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_DECLARED\_LENGTH · requests: source field length declarations

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 source definitions permit longer text than the published Cloud value limits. A larger declared maximum does not prove any stored value is oversized.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| source\_maximum\_length | 400 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Inspect measured value lengths where authorized and confirm target constraints; do not truncate data from metadata alone.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_OPTION\_NORMALIZATION · requests: additional-field option normalization

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_REQUESTS\_CONSTRAINT\_VARIANTS · requests: field constraints vary by form

**Scope:** IT Helpdesk (ID 1) / requests  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 field definitions have differing observed form constraints. A single source maximum cannot represent every template or product type.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| context\_count | 2 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PROBLEMS\_COVERAGE · problems: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PROBLEMS\_CAPACITY · problems: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 160 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PROBLEMS\_MIGRATION\_OMISSION · Problem additional fields require separate handling

**Scope:** IT Helpdesk (ID 1) / problems  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 Problem additional fields observed. The published migration guide excludes Problem additional-field configuration.

Affected: 1 \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | Not established |
| internal\_name | udf\_problem\_ref |
| field\_path | udf\_fields.udf\_problem\_ref |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CHANGES\_COVERAGE · changes: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CHANGES\_CAPACITY · changes: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE · changes: oversized field defaults or options

**Scope:** IT Helpdesk (ID 1) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_change\_ref |
| field\_path | udf\_fields.udf\_change\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CHANGES\_OPTION\_NORMALIZATION · changes: additional-field option normalization

**Scope:** IT Helpdesk (ID 1) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PROJECTS\_COVERAGE · projects: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PROJECTS\_CAPACITY · projects: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 110 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_RELEASES\_COVERAGE · releases: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_RELEASES\_CAPACITY · releases: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 160 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_USERS\_COVERAGE · users: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_USERS\_CAPACITY · users: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 50 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_TECHNICIANS\_COVERAGE · technicians: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_TECHNICIANS\_CAPACITY · technicians: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 50 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_ASSETS\_COVERAGE · assets: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 3 |
| metadata\_targets\_total | 3 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_ASSETS\_CAPACITY · assets: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 100 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE · assets: oversized field defaults or options

**Scope:** IT Helpdesk (ID 1) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_ASSETS\_OPTION\_NORMALIZATION · assets: additional-field option normalization

**Scope:** IT Helpdesk (ID 1) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_COMPUTERS\_COVERAGE · computers: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_COMPUTERS\_CAPACITY · computers: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 52 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE · computers: oversized field defaults or options

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION · computers: additional-field option normalization

**Scope:** IT Helpdesk (ID 1) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CIS\_COVERAGE · cis: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CIS\_CAPACITY · cis: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 1560 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CIS\_DEFAULT\_OPTION\_SIZE · cis: oversized field defaults or options

**Scope:** IT Helpdesk (ID 1) / cis  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_ci\_owner |
| field\_path | udf\_fields.udf\_ci\_owner |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CIS\_OPTION\_NORMALIZATION · cis: additional-field option normalization

**Scope:** IT Helpdesk (ID 1) / cis  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CONTRACTS\_COVERAGE · contracts: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_CONTRACTS\_CAPACITY · contracts: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PURCHASES\_COVERAGE · purchases: field-definition coverage

**Scope:** IT Helpdesk (ID 1) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:FIELD\_PURCHASES\_CAPACITY · purchases: additional-field capacity

**Scope:** IT Helpdesk (ID 1) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 164 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:1:OPERATION\_COVERAGE · Portal operation coverage gaps

**Scope:** IT Helpdesk (ID 1) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories.

Affected: Not established \| Examined: 29

**Coverage:** API-visible observations only; not an organization-wide certification

| Field | Value |
| --- | --- |
| resource | request\_notes |
| outcome | INCOMPLETE |
| records\_observed | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

| Field | Value |
| --- | --- |
| resource | request\_tasks |
| outcome | INCOMPLETE |
| records\_observed | 1 |
| scope | portal |
| portal\_id | 1 |
| portal\_name | IT Helpdesk |

**Action:** Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403.

**Sources:** [api](<https://www.manageengine.com/products/service-desk/sdpop-v3-api/>)

### portal:2:HISTORY\_WINDOW\_ONE\_YEAR · Module records older than 1 year(s)

**Scope:** HR (ID 2) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

4 affected records observed. An agreed historical-data disposition is required.

Affected: 4 \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 102 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1704844800000 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1707523200000 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1735689600000 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:2:HISTORY\_WINDOW\_FIVE\_YEARS · Module records older than 5 year(s)

**Scope:** HR (ID 2) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. An agreed historical-data disposition is required.

Affected: 1 \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 5 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:2:LEGACY\_HISTORY · Historical audit-detail preservation

**Scope:** HR (ID 2) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Agree how legacy history will be preserved and validated; ticket counts cannot verify it.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:LINKED\_REQUESTS · Linked-request relationships

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:REQUEST\_DEPENDENCIES · Request dependencies

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:REQUEST\_CHANGE\_LINKS · Request and change associations

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:ARCHIVED\_SUBENTITIES · Archived-request subentity exposure

**Scope:** HR (ID 2) / archived\_requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:2:ATTACHMENT\_SIZE · Attachment-size exposure

**Scope:** HR (ID 2) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 observed owner totals exceed both interpretations of 48 MB.

Affected: 1 \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| known\_attachment\_bytes | 55000000 |
| missing\_sizes | 0 |
| decimal\_limit | 48000000 |
| binary\_limit | 50331648 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:NOTE\_ATTACHMENTS · Attachments on request notes

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Identified note attachments require separate preservation.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 801 |
| parent\_id | 101 |
| attachment\_count | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:TECHNICIAN\_EMAILS · Technician email readiness

**Scope:** HR (ID 2) / technicians  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

3 affected records observed. Resolve missing or shared technician email identities.

Affected: 3 \| Examined: 3

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 203 |
| missing\_email | true |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 201 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 202 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:2:APPROVER\_LOGIN · Approver and CAB login access

**Scope:** HR (ID 2) / users  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit non-login approver references found; CAB and unresolved memberships still need validation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate login access for every service approver and CAB member; missing user fields are inconclusive.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_VALUE\_LENGTHS · Additional-field value sizes

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 typed values checked; definitions, defaults, options, and uninspected record values may add exposure.

Affected: 1 \| Examined: 2

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| field\_id | 71 |
| character\_count | 300 |
| limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review identified values and obtain complete definitions/defaults/options before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>)

### portal:2:REQUEST\_SCHEDULE\_DATES · Request scheduled-date consistency

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The observed date ordering needs remediation.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| schedule\_precedes\_creation | true |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:DUPLICATE\_SERVICE\_TAGS · Computer service-tag collisions

**Scope:** HR (ID 2) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 affected records observed. Duplicate tags require a supported migration treatment.

Affected: 2 \| Examined: 2

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 10001 |
| duplicate\_tag\_group\_size | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 10002 |
| duplicate\_tag\_group\_size | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:VM\_HOST\_LINKS · Virtual-machine host references

**Scope:** HR (ID 2) / computers  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate VM classification and host relationships across the complete computer inventory.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:ASSET\_DATE\_ORDER · Asset date-order consistency

**Scope:** HR (ID 2) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Observed date ordering can change migrated values.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 10001 |
| invalid\_date\_order | true |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:WORKFLOW\_REBUILD · Workflow and SLA reconstruction

**Scope:** HR (ID 2) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

0 configuration objects and 4 record references observed. Source inventory does not verify target reconstruction.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 51 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 61 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 102 |
| configuration\_id | 51 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| configuration\_id | 41 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:2:FORM\_SCRIPT\_ACTIONS · Form-script action compatibility

**Scope:** HR (ID 2) / templates  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 template rule collections inspected; 0 templates contain explicit script actions.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review script actions and unexposed Change form rules; test supported target scripting behavior.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:QUERY\_REPORTS · Query-report inventory review

**Scope:** HR (ID 2) / reports  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established.

Affected: 1 \| Examined: 1

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 13001 |
| query\_report | true |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### portal:2:TEMPLATE\_COMPLEXITY · Template task and resource limits

**Scope:** HR (ID 2) / templates  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 templates exposed relevant nested metadata; 2 exceed a documented count limit.

Affected: 2 \| Examined: 2

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 11 |
| associated\_tasks | 201 |
| task\_limit | 200 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 12 |
| resource\_count | 21 |
| resource\_limit | 20 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Review identified template structures and all uncollected task/resource/question details.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:RESOLUTION\_LENGTH · Request resolution length

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 resolution values measured; 1 exceed the documented limit.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| character\_count | 66000 |
| limit | 65536 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Preserve identified long resolutions and inspect uncollected historical text fields.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:RECURRING\_MAINTENANCE · Recurring maintenance schedules

**Scope:** HR (ID 2) / maintenances  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit schedules observed; unexposed recurrence settings require a manual inventory.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Inventory recurring maintenance and rebuild its schedule at the agreed migration stage.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:MODULE\_MIGRATION\_SCOPE · CMDB, Releases and custom-module migration scope

**Scope:** HR (ID 2) / multiple  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

4 records or type definitions observed in these inventories. An absent or denied endpoint does not prove a module is unused.

Affected: Not established \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 12001 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 12002 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 11001 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| entity\_id | 601 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible.

**Sources:** [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:2:PROBLEM\_ANCILLARY\_DATA · Problem ancillary-data preservation

**Scope:** HR (ID 2) / problems  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 problems have observed ancillary content; unexposed problem configuration remains unassessed.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| ancillary\_categories\_present | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Record the migration disposition for problem ancillary content and configuration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:CHANGE\_IDENTIFIERS · Change identifier preservation

**Scope:** HR (ID 2) / changes  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

1 Change IDs observed. Source inspection cannot establish target ID preservation.

Affected: Not established \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm Change ID retention with support and require a cross-reference for any changed identifiers.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:2:ACCESS\_MAPPING · Role and organization-membership mapping

**Scope:** HR (ID 2) / identity  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 role definitions observed; equivalent target permissions and membership have not been validated.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Test permitted and denied access for representative roles, sites, groups and sensitive queues.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_COVERAGE · requests: field-definition coverage

**Scope:** HR (ID 2) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

3 distinct additional fields observed; 3 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 3 |
| custom\_fields\_confirmed | 3 |
| metadata\_targets\_successful | 2 |
| metadata\_targets\_total | 2 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_CAPACITY · requests: additional-field capacity

**Scope:** HR (ID 2) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

3 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 3 |
| documented\_limit | 250 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_DEFAULT\_OPTION\_SIZE · requests: oversized field defaults or options

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_DECLARED\_LENGTH · requests: source field length declarations

**Scope:** HR (ID 2) / requests  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 source definitions permit longer text than the published Cloud value limits. A larger declared maximum does not prove any stored value is oversized.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| source\_maximum\_length | 400 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Inspect measured value lengths where authorized and confirm target constraints; do not truncate data from metadata alone.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_OPTION\_NORMALIZATION · requests: additional-field option normalization

**Scope:** HR (ID 2) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_REQUESTS\_CONSTRAINT\_VARIANTS · requests: field constraints vary by form

**Scope:** HR (ID 2) / requests  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 field definitions have differing observed form constraints. A single source maximum cannot represent every template or product type.

Affected: 1 \| Examined: 3

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_char1 |
| field\_path | udf\_fields.udf\_char1 |
| context\_count | 2 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PROBLEMS\_COVERAGE · problems: field-definition coverage

**Scope:** HR (ID 2) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PROBLEMS\_CAPACITY · problems: additional-field capacity

**Scope:** HR (ID 2) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 160 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PROBLEMS\_MIGRATION\_OMISSION · Problem additional fields require separate handling

**Scope:** HR (ID 2) / problems  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 Problem additional fields observed. The published migration guide excludes Problem additional-field configuration.

Affected: 1 \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | Not established |
| internal\_name | udf\_problem\_ref |
| field\_path | udf\_fields.udf\_problem\_ref |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CHANGES\_COVERAGE · changes: field-definition coverage

**Scope:** HR (ID 2) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CHANGES\_CAPACITY · changes: additional-field capacity

**Scope:** HR (ID 2) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE · changes: oversized field defaults or options

**Scope:** HR (ID 2) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_change\_ref |
| field\_path | udf\_fields.udf\_change\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CHANGES\_OPTION\_NORMALIZATION · changes: additional-field option normalization

**Scope:** HR (ID 2) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PROJECTS\_COVERAGE · projects: field-definition coverage

**Scope:** HR (ID 2) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PROJECTS\_CAPACITY · projects: additional-field capacity

**Scope:** HR (ID 2) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 110. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 110 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_RELEASES\_COVERAGE · releases: field-definition coverage

**Scope:** HR (ID 2) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_RELEASES\_CAPACITY · releases: additional-field capacity

**Scope:** HR (ID 2) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 160 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_USERS\_COVERAGE · users: field-definition coverage

**Scope:** HR (ID 2) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_USERS\_CAPACITY · users: additional-field capacity

**Scope:** HR (ID 2) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 50 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_TECHNICIANS\_COVERAGE · technicians: field-definition coverage

**Scope:** HR (ID 2) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_TECHNICIANS\_CAPACITY · technicians: additional-field capacity

**Scope:** HR (ID 2) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 50 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_ASSETS\_COVERAGE · assets: field-definition coverage

**Scope:** HR (ID 2) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: PARTIAL. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_ASSETS\_CAPACITY · assets: additional-field capacity

**Scope:** HR (ID 2) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 100 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE · assets: oversized field defaults or options

**Scope:** HR (ID 2) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_ASSETS\_OPTION\_NORMALIZATION · assets: additional-field option normalization

**Scope:** HR (ID 2) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_COMPUTERS\_COVERAGE · computers: field-definition coverage

**Scope:** HR (ID 2) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_COMPUTERS\_CAPACITY · computers: additional-field capacity

**Scope:** HR (ID 2) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 52 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE · computers: oversized field defaults or options

**Scope:** HR (ID 2) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION · computers: additional-field option normalization

**Scope:** HR (ID 2) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CIS\_COVERAGE · cis: field-definition coverage

**Scope:** HR (ID 2) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CIS\_CAPACITY · cis: additional-field capacity

**Scope:** HR (ID 2) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 1560 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CONTRACTS\_COVERAGE · contracts: field-definition coverage

**Scope:** HR (ID 2) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_CONTRACTS\_CAPACITY · contracts: additional-field capacity

**Scope:** HR (ID 2) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PURCHASES\_COVERAGE · purchases: field-definition coverage

**Scope:** HR (ID 2) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:FIELD\_PURCHASES\_CAPACITY · purchases: additional-field capacity

**Scope:** HR (ID 2) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 164 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:2:OPERATION\_COVERAGE · Portal operation coverage gaps

**Scope:** HR (ID 2) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

3 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories.

Affected: Not established \| Examined: 23

**Coverage:** API-visible observations only; not an organization-wide certification

| Field | Value |
| --- | --- |
| resource | projects |
| outcome | PERMISSION\_DENIED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| resource | request\_notes |
| outcome | INCOMPLETE |
| records\_observed | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

| Field | Value |
| --- | --- |
| resource | request\_tasks |
| outcome | INCOMPLETE |
| records\_observed | 1 |
| scope | portal |
| portal\_id | 2 |
| portal\_name | HR |

**Action:** Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403.

**Sources:** [api](<https://www.manageengine.com/products/service-desk/sdpop-v3-api/>)

### portal:3:HISTORY\_WINDOW\_ONE\_YEAR · Module records older than 1 year(s)

**Scope:** Facilities (ID 3) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

4 affected records observed. An agreed historical-data disposition is required.

Affected: 4 \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1707523200000 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1735689600000 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 701 |
| age\_years\_threshold | 1 |
| created\_epoch\_ms | 1704844800000 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:3:HISTORY\_WINDOW\_FIVE\_YEARS · Module records older than 5 year(s)

**Scope:** Facilities (ID 3) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. An agreed historical-data disposition is required.

Affected: 1 \| Examined: 4

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| age\_years\_threshold | 5 |
| created\_epoch\_ms | 1522540800000 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:3:LEGACY\_HISTORY · Historical audit-detail preservation

**Scope:** Facilities (ID 3) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Agree how legacy history will be preserved and validated; ticket counts cannot verify it.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:LINKED\_REQUESTS · Linked-request relationships

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:REQUEST\_DEPENDENCIES · Request dependencies

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:REQUEST\_CHANGE\_LINKS · Request and change associations

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The identified relationship requires a migration disposition.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| relationship\_count | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:ARCHIVED\_SUBENTITIES · Archived-request subentity exposure

**Scope:** Facilities (ID 3) / archived\_requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:3:ATTACHMENT\_SIZE · Attachment-size exposure

**Scope:** Facilities (ID 3) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 observed owner totals exceed both interpretations of 48 MB.

Affected: 1 \| Examined: 3

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| known\_attachment\_bytes | 55000000 |
| missing\_sizes | 0 |
| decimal\_limit | 48000000 |
| binary\_limit | 50331648 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:NOTE\_ATTACHMENTS · Attachments on request notes

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Identified note attachments require separate preservation.

Affected: 1 \| Examined: 1

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 801 |
| parent\_id | 101 |
| attachment\_count | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:TECHNICIAN\_EMAILS · Technician email readiness

**Scope:** Facilities (ID 3) / technicians  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

3 affected records observed. Resolve missing or shared technician email identities.

Affected: 3 \| Examined: 3

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 203 |
| missing\_email | true |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 201 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 202 |
| duplicate\_email\_group\_size | 2 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:3:APPROVER\_LOGIN · Approver and CAB login access

**Scope:** Facilities (ID 3) / users  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit non-login approver references found; CAB and unresolved memberships still need validation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate login access for every service approver and CAB member; missing user fields are inconclusive.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_VALUE\_LENGTHS · Additional-field value sizes

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 typed values checked; definitions, defaults, options, and uninspected record values may add exposure.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| field\_id | 71 |
| character\_count | 300 |
| limit | 250 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review identified values and obtain complete definitions/defaults/options before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>)

### portal:3:REQUEST\_SCHEDULE\_DATES · Request scheduled-date consistency

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. The observed date ordering needs remediation.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| schedule\_precedes\_creation | true |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:DUPLICATE\_SERVICE\_TAGS · Computer service-tag collisions

**Scope:** Facilities (ID 3) / computers  
**Status:** NO\_ISSUE\_OBSERVED  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue among 1 API-visible records checked.

Affected: 0 \| Examined: 1

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:VM\_HOST\_LINKS · Virtual-machine host references

**Scope:** Facilities (ID 3) / computers  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate VM classification and host relationships across the complete computer inventory.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:ASSET\_DATE\_ORDER · Asset date-order consistency

**Scope:** Facilities (ID 3) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. Observed date ordering can change migrated values.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 10001 |
| invalid\_date\_order | true |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:WORKFLOW\_REBUILD · Workflow and SLA reconstruction

**Scope:** Facilities (ID 3) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

0 configuration objects and 3 record references observed. Source inventory does not verify target reconstruction.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 51 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| configuration\_id | 61 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| configuration\_id | 41 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:3:FORM\_SCRIPT\_ACTIONS · Form-script action compatibility

**Scope:** Facilities (ID 3) / templates  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 template rule collections inspected; 0 templates contain explicit script actions.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review script actions and unexposed Change form rules; test supported target scripting behavior.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:QUERY\_REPORTS · Query-report inventory review

**Scope:** Facilities (ID 3) / reports  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 affected records observed. This query-report inventory may include built-ins; custom status and actual usage are not established.

Affected: 1 \| Examined: 1

**Coverage:** All required observed fields checked in the enumerated API-visible scope. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 13001 |
| query\_report | true |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### portal:3:TEMPLATE\_COMPLEXITY · Template task and resource limits

**Scope:** Facilities (ID 3) / templates  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

2 templates exposed relevant nested metadata; 2 exceed a documented count limit.

Affected: 2 \| Examined: 2

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 11 |
| associated\_tasks | 201 |
| task\_limit | 200 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 12 |
| resource\_count | 21 |
| resource\_limit | 20 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Review identified template structures and all uncollected task/resource/question details.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:RESOLUTION\_LENGTH · Request resolution length

**Scope:** Facilities (ID 3) / requests  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 resolution values measured; 1 exceed the documented limit.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 101 |
| character\_count | 66000 |
| limit | 65536 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Preserve identified long resolutions and inspect uncollected historical text fields.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:RECURRING\_MAINTENANCE · Recurring maintenance schedules

**Scope:** Facilities (ID 3) / maintenances  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit schedules observed; unexposed recurrence settings require a manual inventory.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Inventory recurring maintenance and rebuild its schedule at the agreed migration stage.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:MODULE\_MIGRATION\_SCOPE · CMDB, Releases and custom-module migration scope

**Scope:** Facilities (ID 3) / multiple  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

3 records or type definitions observed in these inventories. An absent or denied endpoint does not prove a module is unused.

Affected: Not established \| Examined: 3

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 12001 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 12002 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| entity\_id | 11001 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible.

**Sources:** [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:3:PROBLEM\_ANCILLARY\_DATA · Problem ancillary-data preservation

**Scope:** Facilities (ID 3) / problems  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** SOURCE\_OBSERVATION

1 problems have observed ancillary content; unexposed problem configuration remains unassessed.

Affected: 1 \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 501 |
| ancillary\_categories\_present | 2 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Record the migration disposition for problem ancillary content and configuration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:CHANGE\_IDENTIFIERS · Change identifier preservation

**Scope:** Facilities (ID 3) / changes  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** SOURCE\_OBSERVATION

1 Change IDs observed. Source inspection cannot establish target ID preservation.

Affected: Not established \| Examined: 1

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

| Field | Value |
| --- | --- |
| entity\_id | 401 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm Change ID retention with support and require a cross-reference for any changed identifiers.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:3:ACCESS\_MAPPING · Role and organization-membership mapping

**Scope:** Facilities (ID 3) / identity  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 role definitions observed; equivalent target permissions and membership have not been validated.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Test permitted and denied access for representative roles, sites, groups and sensitive queues.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_REQUESTS\_COVERAGE · requests: field-definition coverage

**Scope:** Facilities (ID 3) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 2 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_REQUESTS\_CAPACITY · requests: additional-field capacity

**Scope:** Facilities (ID 3) / requests  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 250. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 250 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PROBLEMS\_COVERAGE · problems: field-definition coverage

**Scope:** Facilities (ID 3) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PROBLEMS\_CAPACITY · problems: additional-field capacity

**Scope:** Facilities (ID 3) / problems  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 160 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PROBLEMS\_MIGRATION\_OMISSION · Problem additional fields require separate handling

**Scope:** Facilities (ID 3) / problems  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** INFERRED\_FROM\_METADATA

1 Problem additional fields observed. The published migration guide excludes Problem additional-field configuration.

Affected: 1 \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | Not established |
| internal\_name | udf\_problem\_ref |
| field\_path | udf\_fields.udf\_problem\_ref |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CHANGES\_COVERAGE · changes: field-definition coverage

**Scope:** Facilities (ID 3) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CHANGES\_CAPACITY · changes: additional-field capacity

**Scope:** Facilities (ID 3) / changes  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CHANGES\_DEFAULT\_OPTION\_SIZE · changes: oversized field defaults or options

**Scope:** Facilities (ID 3) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_change\_ref |
| field\_path | udf\_fields.udf\_change\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CHANGES\_OPTION\_NORMALIZATION · changes: additional-field option normalization

**Scope:** Facilities (ID 3) / changes  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PROJECTS\_COVERAGE · projects: field-definition coverage

**Scope:** Facilities (ID 3) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PROJECTS\_CAPACITY · projects: additional-field capacity

**Scope:** Facilities (ID 3) / projects  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 110. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 110 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_RELEASES\_COVERAGE · releases: field-definition coverage

**Scope:** Facilities (ID 3) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_RELEASES\_CAPACITY · releases: additional-field capacity

**Scope:** Facilities (ID 3) / releases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_USERS\_COVERAGE · users: field-definition coverage

**Scope:** Facilities (ID 3) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_USERS\_CAPACITY · users: additional-field capacity

**Scope:** Facilities (ID 3) / users  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 50 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_TECHNICIANS\_COVERAGE · technicians: field-definition coverage

**Scope:** Facilities (ID 3) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_TECHNICIANS\_CAPACITY · technicians: additional-field capacity

**Scope:** Facilities (ID 3) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 50. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 50 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_ASSETS\_COVERAGE · assets: field-definition coverage

**Scope:** Facilities (ID 3) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 3 |
| metadata\_targets\_total | 3 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_ASSETS\_CAPACITY · assets: additional-field capacity

**Scope:** Facilities (ID 3) / assets  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 100. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 100 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_ASSETS\_DEFAULT\_OPTION\_SIZE · assets: oversized field defaults or options

**Scope:** Facilities (ID 3) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_ASSETS\_OPTION\_NORMALIZATION · assets: additional-field option normalization

**Scope:** Facilities (ID 3) / assets  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_COMPUTERS\_COVERAGE · computers: field-definition coverage

**Scope:** Facilities (ID 3) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

2 distinct additional fields observed; 2 have explicit API metadata. Definition coverage: FORM\_SCOPE\_COMPLETE. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| custom\_fields\_confirmed | 2 |
| metadata\_targets\_successful | 1 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_COMPUTERS\_CAPACITY · computers: additional-field capacity

**Scope:** Facilities (ID 3) / computers  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

2 distinct additional fields observed; the documented total limit is 52. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 2 |
| documented\_limit | 52 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_COMPUTERS\_DEFAULT\_OPTION\_SIZE · computers: oversized field defaults or options

**Scope:** Facilities (ID 3) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 field defaults and 0 option sets exceed documented value constraints. Only measurements are retained; defaults and option text are excluded.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 71 |
| internal\_name | udf\_asset\_ref |
| field\_path | udf\_fields.udf\_asset\_ref |
| default\_character\_count | 315 |
| documented\_limit | 250 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_COMPUTERS\_OPTION\_NORMALIZATION · computers: additional-field option normalization

**Scope:** Facilities (ID 3) / computers  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** API\_METADATA

1 fields contain options with characters the migration guide removes; 1 fields include an option consisting only of those characters.

Affected: 1 \| Examined: 2

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

| Field | Value |
| --- | --- |
| field\_id | 72 |
| internal\_name | udf\_choice |
| field\_path | udf\_fields.udf\_choice |
| affected\_options | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CIS\_COVERAGE · cis: field-definition coverage

**Scope:** Facilities (ID 3) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 distinct additional fields observed; 0 have explicit API metadata. Definition coverage: OBSERVED\_KEYS\_ONLY. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| custom\_fields\_confirmed | 0 |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 1 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CIS\_CAPACITY · cis: additional-field capacity

**Scope:** Facilities (ID 3) / cis  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

1 distinct additional fields observed; the documented total limit is 1560. Target edition and per-type mapping still require confirmation. Asset/CI layouts may map to different target field populations; their counts are not automatically interchangeable.

Affected: Not established \| Examined: 1

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | 1 |
| documented\_limit | 1560 |
| field\_types\_unknown | 1 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CONTRACTS\_COVERAGE · contracts: field-definition coverage

**Scope:** Facilities (ID 3) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_CONTRACTS\_CAPACITY · contracts: additional-field capacity

**Scope:** Facilities (ID 3) / contracts  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 160. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 160 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PURCHASES\_COVERAGE · purchases: field-definition coverage

**Scope:** Facilities (ID 3) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

Additional-field count is unknown; no field metadata or UDF keys were available. Definition coverage: UNKNOWN. A completed form inspection does not certify the administrator field registry.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| custom\_fields\_confirmed | Not established |
| metadata\_targets\_successful | 0 |
| metadata\_targets\_total | 0 |
| registry\_complete | false |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve uninspected forms, missing metadata strategies and field-registry gaps before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:FIELD\_PURCHASES\_CAPACITY · purchases: additional-field capacity

**Scope:** Facilities (ID 3) / purchases  
**Status:** UNKNOWN  
**Evidence basis:** API\_METADATA

Additional-field count is unknown; the documented total limit is 164. Target edition and per-type mapping still require confirmation.

Affected: Not established \| Examined: 0

**Coverage:** Observed definitions/form metadata are a lower bound; unattached or uninspected fields may be missing.

| Field | Value |
| --- | --- |
| additional\_fields\_observed | Not established |
| documented\_limit | 164 |
| field\_types\_unknown | 0 |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Confirm source definitions, target mapping and field behavior in the trial migration.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>), [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:3:OPERATION\_COVERAGE · Portal operation coverage gaps

**Scope:** Facilities (ID 3) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

1 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories.

Affected: Not established \| Examined: 23

**Coverage:** API-visible observations only; not an organization-wide certification

| Field | Value |
| --- | --- |
| resource | releases |
| outcome | MODULE\_NOT\_AVAILABLE |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 3 |
| portal\_name | Facilities |

**Action:** Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403.

**Sources:** [api](<https://www.manageengine.com/products/service-desk/sdpop-v3-api/>)

### portal:4:HISTORY\_WINDOW\_ONE\_YEAR · Module records older than 1 year(s)

**Scope:** Security (ID 4) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:4:HISTORY\_WINDOW\_FIVE\_YEARS · Module records older than 5 year(s)

**Scope:** Security (ID 4) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Confirm the required history window and vendor-supported handling for these age groups.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:4:LEGACY\_HISTORY · Historical audit-detail preservation

**Scope:** Security (ID 4) / multiple  
**Status:** CONFIRMED\_IMPACT  
**Evidence basis:** USER\_SUPPLIED\_REQUIREMENT

History subresources have not been exhaustively inspected. Preserving legacy history is a user-supplied requirement. The built-in migration excludes History-tab data.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Agree how legacy history will be preserved and validated; ticket counts cannot verify it.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:LINKED\_REQUESTS · Linked-request relationships

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:REQUEST\_DEPENDENCIES · Request dependencies

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:REQUEST\_CHANGE\_LINKS · Request and change associations

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:ARCHIVED\_SUBENTITIES · Archived-request subentity exposure

**Scope:** Security (ID 4) / archived\_requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:4:ATTACHMENT\_SIZE · Attachment-size exposure

**Scope:** Security (ID 4) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No oversized owner was established; unseen attachment subresources and missing sizes remain unverified.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Confirm per-owner aggregation and byte units; inspect uncollected attachment metadata and server-path integrity.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:NOTE\_ATTACHMENTS · Attachments on request notes

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:TECHNICIAN\_EMAILS · Technician email readiness

**Scope:** Security (ID 4) / technicians  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:4:APPROVER\_LOGIN · Approver and CAB login access

**Scope:** Security (ID 4) / users  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit non-login approver references found; CAB and unresolved memberships still need validation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate login access for every service approver and CAB member; missing user fields are inconclusive.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:REQUEST\_FIELD\_CAPACITY · Request additional-field capacity

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 distinct request-field definitions observed; 0 have recognized types. The combined paid-tier limit is 250.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate every field type and target entitlement; free-tier and other-module limits differ.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>)

### portal:4:FIELD\_NAME\_COLLISIONS · Case-insensitive field-name collisions

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:FIELD\_VALUE\_LENGTHS · Additional-field value sizes

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 typed values checked; definitions, defaults, options, and uninspected record values may add exposure.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review identified values and obtain complete definitions/defaults/options before accepting field compatibility.

**Sources:** [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>)

### portal:4:REQUEST\_SCHEDULE\_DATES · Request scheduled-date consistency

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:DUPLICATE\_SERVICE\_TAGS · Computer service-tag collisions

**Scope:** Security (ID 4) / computers  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:VM\_HOST\_LINKS · Virtual-machine host references

**Scope:** Security (ID 4) / computers  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicitly classified VMs observed; 0 host references checked. Unknown VM classifications remain outside this check.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Validate VM classification and host relationships across the complete computer inventory.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:ASSET\_DATE\_ORDER · Asset date-order consistency

**Scope:** Security (ID 4) / assets  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review the identified records before migration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:WORKFLOW\_REBUILD · Workflow and SLA reconstruction

**Scope:** Security (ID 4) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 configuration objects and 0 record references observed. Source inventory does not verify target reconstruction.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Map each SLA, Request lifecycle/workflow (terminology varies by source build) and Change workflow to a configured and tested target equivalent.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:4:FORM\_SCRIPT\_ACTIONS · Form-script action compatibility

**Scope:** Security (ID 4) / templates  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 template rule collections inspected; 0 templates contain explicit script actions.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review script actions and unexposed Change form rules; test supported target scripting behavior.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:QUERY\_REPORTS · Query-report inventory review

**Scope:** Security (ID 4) / reports  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

No matching issue established from 0 checked records; collection or required-field coverage is incomplete.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Map observed query reports to target equivalents; verify which are custom or used before estimating redevelopment.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>), [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>)

### portal:4:TEMPLATE\_COMPLEXITY · Template task and resource limits

**Scope:** Security (ID 4) / templates  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 templates exposed relevant nested metadata; 0 exceed a documented count limit.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Review identified template structures and all uncollected task/resource/question details.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:RESOLUTION\_LENGTH · Request resolution length

**Scope:** Security (ID 4) / requests  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 resolution values measured; 0 exceed the documented limit.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Preserve identified long resolutions and inspect uncollected historical text fields.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:RECURRING\_MAINTENANCE · Recurring maintenance schedules

**Scope:** Security (ID 4) / maintenances  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 explicit schedules observed; unexposed recurrence settings require a manual inventory.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Inventory recurring maintenance and rebuild its schedule at the agreed migration stage.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:MODULE\_MIGRATION\_SCOPE · CMDB, Releases and custom-module migration scope

**Scope:** Security (ID 4) / multiple  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 records or type definitions observed in these inventories. An absent or denied endpoint does not prove a module is unused.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Obtain explicit migration handling for these modules and their relationships; publication omissions are not proof that migration is impossible.

**Sources:** [migration\_scope](<https://help.servicedeskplus.com/data-migrated>)

### portal:4:PROBLEM\_ANCILLARY\_DATA · Problem ancillary-data preservation

**Scope:** Security (ID 4) / problems  
**Status:** UNKNOWN  
**Evidence basis:** SOURCE\_OBSERVATION

0 problems have observed ancillary content; unexposed problem configuration remains unassessed.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Record the migration disposition for problem ancillary content and configuration.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:CHANGE\_IDENTIFIERS · Change identifier preservation

**Scope:** Security (ID 4) / changes  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 Change IDs observed. Source inspection cannot establish target ID preservation.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Confirm Change ID retention with support and require a cross-reference for any changed identifiers.

**Sources:** [migration](<https://help.servicedeskplus.com/op-to-od-migration>)

### portal:4:ACCESS\_MAPPING · Role and organization-membership mapping

**Scope:** Security (ID 4) / identity  
**Status:** MANUAL\_CONFIRMATION  
**Evidence basis:** TARGET\_CLOUD\_CONFIRMATION

0 role definitions observed; equivalent target permissions and membership have not been validated.

Affected: Not established \| Examined: 0

**Coverage:** Counts describe observed evidence and may be lower bounds. API permissions and omitted subresources can hide additional data.

**Action:** Test permitted and denied access for representative roles, sites, groups and sensitive queues.

**Sources:** [limitations](<https://help.servicedeskplus.com/migration-limitations>)

### portal:4:OPERATION\_COVERAGE · Portal operation coverage gaps

**Scope:** Security (ID 4) / multiple  
**Status:** UNKNOWN  
**Evidence basis:** API\_COVERAGE\_LIMITATION

19 selected collections lack complete API-visible lists. Denied, unsupported and unstarted collections are not zero-record inventories.

Affected: Not established \| Examined: 0

**Coverage:** API-visible observations only; not an organization-wide certification

| Field | Value |
| --- | --- |
| resource | incident\_templates |
| outcome | PORTAL\_NOT\_ACCESSIBLE |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | service\_templates |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | sites |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | support\_groups |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | technicians |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | users |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | reports |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | ci\_types |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | asset\_modules |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | requests |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | changes |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | problems |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | projects |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | releases |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | assets |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | computers |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | cis |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | contracts |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

| Field | Value |
| --- | --- |
| resource | purchases |
| outcome | NOT\_STARTED |
| records\_observed | Not established |
| scope | portal |
| portal\_id | 4 |
| portal\_name | Security |

**Action:** Resolve each specific diagnostic or document required alternative evidence; do not infer a role requirement from generic HTTP 403.

**Sources:** [api](<https://www.manageengine.com/products/service-desk/sdpop-v3-api/>)

## Documentation sources

- [migration](<https://help.servicedeskplus.com/op-to-od-migration>) · ServiceDesk Plus migration prerequisites and process · Reviewed 2026-10-05
- [limitations](<https://help.servicedeskplus.com/migration-limitations>) · ServiceDesk Plus migration limitations · Reviewed 2026-10-07
- [migration\_scope](<https://help.servicedeskplus.com/data-migrated>) · Data included in the published migration matrix · Reviewed 2026-10-05
- [field\_limits](<https://help.sdpondemand.com/field-count/character-limit>) · Cloud additional-field count and value limits · Reviewed 2026-10-07
- [reporting](<https://pitstop.manageengine.com/portal/en/kb/articles/sdpc-reporting-faq-s>) · ServiceDesk Plus Cloud reporting FAQ · Reviewed 2026-10-05
- [functions](<https://help.sdpondemand.com/custom-functions>) · Cloud custom functions · Reviewed 2026-10-05
- [java\_functions](<https://help.sdpondemand.com/java-in-custom-function>) · Java custom functions · Reviewed 2026-10-05
- [node\_functions](<https://help.sdpondemand.com/nodejs-in-custom-function>) · Node.js custom functions · Reviewed 2026-10-05
- [audit](<https://help.sdpondemand.com/audit-log>) · Cloud administrative audit logs · Reviewed 2026-10-05
- [exports](<https://help.sdpondemand.com/export-data>) · Cloud data export · Reviewed 2026-10-05
- [admin\_faq](<https://pitstop.manageengine.com/portal/en/kb/articles/admin>) · Cloud administration FAQ · Reviewed 2026-10-05
- [archive](<https://help.sdpondemand.com/data-archiving>) · Cloud data archiving · Reviewed 2026-10-05
- [editions](<https://www.manageengine.com/products/service-desk/cloud/online-helpdesk-comparison.html>) · ServiceDesk Plus Cloud edition comparison · Reviewed 2026-10-05
- [email\_behavior](<https://pitstop.manageengine.com/portal/en/kb/articles/general-faq>) · Cloud request and notification FAQ · Reviewed 2026-10-05
- [api](<https://www.manageengine.com/products/service-desk/sdpop-v3-api/>) · ServiceDesk Plus on-premises API documentation · Reviewed 2026-10-05
