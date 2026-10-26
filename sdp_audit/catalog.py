"""Documented on-premises GET resources and a closed read-only path allowlist.

Reviewed 2026-10-07 against ManageEngine's on-premises V3 guide, verified
ServiceDesk Plus Postman workspace, and build 15100 asset/CMDB change guides.
Paths are relative to /api/v3. Nothing here authorizes an HTTP mutation or a
report-execution operation. Response wrappers are checked by the collector;
an absent expected wrapper is not evidence of an empty dataset.
"""

from __future__ import annotations

import re
from dataclasses import replace

from .models import ResourceSpec


REVIEWED_ON = "2026-10-07"
OP_DOCS = "https://www.manageengine.com/products/service-desk/sdpop-v3-api/"
POSTMAN = "https://www.postman.com/servicedeskplus/servicedesk-plus-api/request/"
ASSET_CHANGES = "https://help.servicedeskplus.com/asset-api-changes"
CMDB_CHANGES = "https://help.servicedeskplus.com/cmdb-api-v1-and-v3-comparison"


RESOURCES: list[ResourceSpec] = [
    ResourceSpec(
        "incident_templates", "/request_templates", "request_templates", "request_template",
        POSTMAN + "urfbpdc/get-incident-templates", kind="configuration",
        search_fields={"is_service_template": False},
        description="Incident-template inventory. Lists expose has_fafr and rule counts, but omit field properties and layout; details are separate.",
    ),
    ResourceSpec(
        "service_templates", "/request_templates", "request_templates", "request_template",
        POSTMAN + "vuub628/get-service-templates", kind="configuration",
        search_fields={"is_service_template": True},
        description="Service-template inventory. This is a template list, not a complete service-catalog/workflow export.",
    ),
    ResourceSpec(
        "sites", "/sites", "sites", "site",
        POSTMAN + "m7i4ubc/view-all-sites", kind="configuration",
        description="Sites visible to the API principal. Detail includes per-site settings and role associations when authorized.",
    ),
    ResourceSpec(
        "support_groups", "/support_groups", "support_groups", "support_group",
        POSTMAN + "qurnsjj/view-all-support-groups", kind="configuration",
        description="Support-group inventory; per-group detail can expose technician and organization-role associations.",
    ),
    ResourceSpec(
        "technicians", "/technicians", "technicians", "technician",
        POSTMAN + "e7t4k03/get-all-technicians", kind="configuration",
        description="Technicians visible in the selected portal. Identity and permission visibility depends on the API principal.",
    ),
    ResourceSpec(
        "users", "/users", "users", "user",
        OP_DOCS + "admin/user.html", kind="configuration",
        description="Portal users, including is_technician, email_id, login_name, associated_roles and user_udf_fields where returned. This is not the ESM-directory orgusers API.",
    ),
    ResourceSpec(
        "reports", "/reports", "reports", "report",
        POSTMAN + "lb43ei8/view-all-query-reports", kind="configuration", detail=False,
        list_info_extras={"filter_by": {"name": "Query_reports"}},
        description="Query-report names and folders only. Includes built-in reports; does not prove which are custom or used. Does not execute reports or SQL and does not retrieve external BI dependencies.",
    ),
    ResourceSpec(
        "ci_types", "/ci_types", "ci_types", "ci_type", CMDB_CHANGES,
        kind="configuration", detail=False,
        description="Build 15100+ CI-type inventory. Validated observed cmdb API plural names authorize exact per-portal /_metadata reads; arbitrary response URLs are never followed.",
    ),
    ResourceSpec(
        "asset_modules", "/asset_modules", "all_product_types", "product_type",
        "https://www.postman.com/servicedeskplus/servicedesk-plus-api/documentation/euwj7bl/servicedesk-plus-on-premise",
        kind="configuration", detail=False,
        description="Documented asset product-type/schema catalog. Observed API plural names can authorize exact per-type metadata GETs; this is not a universal ITSM module registry.",
    ),
    ResourceSpec(
        "requests", "/requests", "requests", "request",
        OP_DOCS + "requests/request.html",
        list_info_extras={"filter_by": {"name": "All_Requests"}},
        description="API-visible ordinary requests. The public on-prem guide does not establish that this includes archived or trashed requests. Detail provides dates, template/SLA references, UDF values, attachment metadata, and relationship-presence flags.",
    ),
    ResourceSpec(
        "changes", "/changes", "changes", "change",
        OP_DOCS + "changes/change.html",
        list_info_extras={"sort_fields": [{"field": "id", "order": "asc"}]},
        description="Change records; detail can expose workflow/template references, UDFs, stage/status, approval-related data and attachments. Workflow references do not constitute a complete workflow export.",
    ),
    ResourceSpec(
        "problems", "/problems", "problems", "problem",
        POSTMAN + "2qtgxu5/view-all-problem",
        description="Problem inventory and details using the verified on-premises Postman GET operations. Configuration, solutions and associations may require separate review.",
    ),
    ResourceSpec(
        "projects", "/projects", "projects", "project",
        OP_DOCS + "projects/project.html",
        description="Project records. Nested milestones, tasks and memberships are separate API resources and are not implied by a complete parent list.",
    ),
    ResourceSpec(
        "releases", "/releases", "releases", "release",
        OP_DOCS + "releases/release.html",
        list_info_extras={"filter_by": {"name": "all_releases"}, "sort_fields": [{"field": "id", "order": "asc"}]},
        description="Release records; support in the source API does not establish support in the Cloud migration utility.",
    ),
    ResourceSpec(
        "assets", "/asset_assets", "asset_assets", "asset_asset",
        POSTMAN + "4801ukn/get-all-assets", detail=False,
        description="Build 15100+ cross-type asset list. Generic rows omit product-type UDFs and subforms; computer detail is collected separately. Disposed/deleted items and a complete CMDB must be evaluated separately.",
    ),
    ResourceSpec(
        "computers", "/asset_computers", "asset_computers", "asset_computer",
        ASSET_CHANGES,
        description="Build 15100+ computer list/detail (replaces workstations). Details can expose service_tag, virtualization and date fields; field availability varies by build and discovery data.",
    ),
    ResourceSpec(
        "cis", "/cmdb", "cmdb", "cmdb", CMDB_CHANGES, detail=False,
        description="Build 15100+ all-CI basic inventory. Does not certify complete per-type attributes or relationship preservation; these require the documented per-type APIs and migration confirmation.",
    ),
    ResourceSpec(
        "contracts", "/contracts", "contracts", "contract",
        POSTMAN + "fieghu5/view-all-contracts", detail=False,
        description="Contract inventory. The list can include name, type, status, dates, vendor and custom contract ID; full terms, history and relationships are not certified by a parent list.",
    ),
    ResourceSpec(
        "purchases", "/purchase_orders", "purchase_orders", "purchase_order",
        POSTMAN + "pqnf1he/view-all-purchase-orders",
        description="Purchase-order inventory/detail. Invoices, payments and approval levels are separate resources; parent-row counts do not certify their preservation.",
    ),
]

# Data scope and request context are separate: Orgusers is an organisation-wide
# ESM directory, although the official example includes an explicit PORTALID.
# The environment scheduler reads it once, never once per portal. It is not
# combined with portal user/technician membership counts.
GLOBAL_RESOURCES: list[ResourceSpec] = [
    ResourceSpec(
        "orgusers", "/orgusers", "orgusers", "orguser",
        POSTMAN + "7qfshjw/get-all-orgusers", kind="configuration", detail=False,
        scope="environment", module="orgusers",
        description="Organisation-wide ESM users. Documented for installations with multiple instances; Orgadmin visibility may be required. Collected once with one explicit discovered portal context.",
    ),
]

_MODULES = {
    "incident_templates": "requests", "service_templates": "requests",
    "support_groups": "groups", "ci_types": "cmdb", "cis": "cmdb",
    "assets": "assets", "computers": "assets", "asset_modules": "assets",
    "purchases": "purchases",
}
RESOURCES = [replace(spec, module=_MODULES.get(spec.key, spec.key)) for spec in RESOURCES]


# Only attempted after an unsupported primary/fallback list response. These
# are explicitly documented compatibility reads, not a route around an
# authorization failure. The vendor documents retirement of these APIs.
FALLBACKS: dict[str, list[ResourceSpec]] = {
    "assets": [
        ResourceSpec(
            "assets", "/assets", "assets", "asset",
            POSTMAN + "kueinrc/get-all-assets", detail=False,
            description="Legacy asset list; deprecated after build 15100, with documented support ending April 2026. A fallback result is limited to fields supported by the legacy API.",
        ),
    ],
    "computers": [
        ResourceSpec(
            "computers", "/asset_workstations", "asset_workstations", "asset_workstation",
            ASSET_CHANGES, detail=False,
            description="Documented build 15100+ workstation list. Separate from all-computer inventory; detail coverage is not implied.",
        ),
        ResourceSpec(
            "computers", "/workstations", "workstations", "workstation",
            ASSET_CHANGES,
            description="Legacy workstation API for older source builds only. New custom product-type fields may not appear; migrated-source compatibility requires review.",
        ),
    ],
}
FALLBACKS = {key: [replace(spec, module=_MODULES.get(key, key)) for spec in choices]
             for key, choices in FALLBACKS.items()}


# re.fullmatch is required by the client. IDs use ASCII digits, not arbitrary
# strings, and there are no broad /api/v3/.* or dynamic href allowances.
ALLOWED_PATTERNS: list[str] = [
    re.escape(spec.path)
    for spec in RESOURCES + GLOBAL_RESOURCES
] + [
    re.escape(spec.path) + r"/[0-9]+"
    for spec in RESOURCES
    if spec.detail
] + [
    re.escape(spec.path)
    for fallbacks in FALLBACKS.values()
    for spec in fallbacks
] + [
    re.escape(spec.path) + r"/[0-9]+"
    for fallbacks in FALLBACKS.values()
    for spec in fallbacks
    if spec.detail
] + [
    # Explicitly documented Request Note GET list/detail operations.
    r"/requests/[0-9]+/notes(?:/[0-9]+)?",
    # Formal task GET list/detail operations in the four public on-prem guides.
    r"/(?:requests|changes|projects|releases)/[0-9]+/tasks(?:/[0-9]+)?",
    # GET worklog list/detail: vendor Request Admin V1 -> V3 migration notice.
    r"/requests/[0-9]+/worklogs(?:/[0-9]+)?",
    # Asset attachment metadata list, excluding downloads and attachment data.
    r"/asset_assets/[0-9]+/attachments",
    # Documented metainfo reads; the collector must not follow embedded hrefs.
    r"/portals",
    r"/requests/metainfo",
    r"/asset_assets/_metainfo",
    r"/asset_computers/_metainfo",
    r"/asset_workstations",
    r"/asset_workstations/_metainfo",
    r"/asset_printers/_metainfo",
    r"/asset_servers/_metainfo",
    r"/assets/metainfo",
    r"/workstations/metainfo",
    r"/changes/metainfo",
    r"/changes/[0-9]+/metainfo",
    r"/departments/_metainfo",
    # Only fields.py's documented module-selector strategies issue this GET.
    # It is deliberately absent from the ordinary resource inventory above.
    r"/udf_fields",
]


UNEXPOSED_FEATURES: list[str] = [
    "Archived request list/detail: the public on-prem archive guide documents DELETE, not a supported complete GET inventory; archive coverage remains unknown.",
    "Complete field registries: template/layout metadata and observed UDF keys are lower bounds. No bare /udf_fields registry is assumed. Undocumented module metadata is not probed.",
    "Complete role definitions and permission mappings; associated user/group/site roles can be observed but do not prove Cloud equivalence.",
    "Full SLA rules, Request Life Cycles, Change workflows, form-rule action scripts, custom triggers and recurring maintenance configuration.",
    "External scripts, scheduled jobs, SQL/SSRS/Power BI/Excel consumers, integrations and their actual execution/API-call volumes.",
    "Source product/build/license properties: /app_resources/post_login_props is described as internal-only in vendor mobile documentation and is not called.",
    "Full history-tab contents, all relationship graphs, all notification/approval data and all module-specific nested records.",
    "Every product-type UDF/subform, CMDB per-type attribute and CI relationship: generic asset/CMDB inventory is not a complete export.",
    "Cloud target edition, data center, effective tenant limits, license entitlements, retention, backups, recovery and vendor migration exceptions.",
    "Vendor migration outcomes, delta-update/deletion behavior, cutover outage, historical-data window exceptions and end-to-end functional equivalence.",
    "Portal discovery build support: the /portals on-prem request/response contract is documented by the official Netskope integration maintainer; a minimum supported SDP build was not established in reviewed ManageEngine references. Explicit portal IDs are required when discovery is unavailable.",
    "Integration-key expiration: no documented safe read-only expiration API was verified; expiration is neither inferred nor required.",
]


SUPPLEMENTAL_SOURCES = {
    "authentication": OP_DOCS,
    "pagination": OP_DOCS + "getting-started/pagination.html",
    "status_codes": OP_DOCS + "getting-started/common-error-code.html",
    "header_changes": "https://pitstop.manageengine.com/portal/en/community/topic/deprecating-few-params-of-v3-api-urls",
    "request_notes": OP_DOCS + "requests/request_note.html",
    "request_tasks": OP_DOCS + "requests/request_task.html",
    "change_tasks": OP_DOCS + "changes/change_task.html",
    "project_tasks": OP_DOCS + "projects/project_task.html",
    "release_tasks": OP_DOCS + "releases/release_task.html",
    "request_admin_api": "https://www.manageengine.jp/support/kb/ServiceDesk_Plus/?p=7166",
    "template_detail": POSTMAN + "f9xljpc/get-template-details",
    "technician_detail": POSTMAN + "ixevz4h/get-a-technician",
    "problem_detail": POSTMAN + "1bhzpjb/view-problem",
    "computer_detail": POSTMAN + "zc2vkas/get-a-computer",
    "purchase_detail": POSTMAN + "ujtp3lz/view-a-purchase-order",
    "asset_metainfo": POSTMAN + "wyufbep/get-asset-metainfo",
    "asset_attachments": POSTMAN + "pv19zxk/get-attachments-list",
    "asset_build_changes": ASSET_CHANGES,
    "cmdb_build_changes": CMDB_CHANGES,
}
