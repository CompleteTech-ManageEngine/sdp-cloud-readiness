# ServiceDesk Plus Cloud Readiness Assessment

For a short introduction, see the [repository README](../../README.md). Run all commands below from the repository or extracted-release root. Examples using an adjacent `.pyz` apply to an extracted release; in a source checkout use `sdp_cloud_readiness.py`, or build first and use `dist/sdp_cloud_readiness.pyz`.

A local, **read-only assessment of standard ManageEngine ServiceDesk Plus on-premises before migration to Cloud**. Normally, provide only the source URL and integration API key. Version **2.2.0** attempts to discover the portal/ESM topology visible to that key, assesses discovered portals within one shared request budget, and produces a consolidated report with per-portal findings and explicit coverage gaps.

**Python 3.10 or newer. No third-party Python packages for the assessment** (`openpyxl` and `python-docx` are optional, for the branded workbook and Word Scope of Work). The source tree, portable `.pyz`, and Windows launcher run the same application. This is an independent assessment tool, not a ManageEngine product or a migration utility.

The main on-premises API catalog was reviewed on **7 October 2026**; directory discovery, pagination and error handling were rechecked on **14 October 2026**. Migration rules carry their own dated source references. API availability, effective permissions, and migration behavior still need validation against your installed build and proposed Cloud target.

## Branded deliverables and Scope of Work

Each run also writes client-ready copies to `<assessment>/branded/<Brand>/` with the CompleteTech LLC identity: the report and vendor questions as HTML and PDF, a findings and coverage workbook, and, when the folder holds an engagement `scope-of-work.md`, the Scope of Work as HTML, PDF and Word. Name the client with `--prepared-for "Client Name"`; choose another approved brand with `--brand`, or none with `--brand none`. `--brand-assessment <folder>` brands an existing assessment offline. The verified reports below are never modified. See [branded deliverables](branded-deliverables.md) and [Scope of Work](scope-of-work.md).

## Default local environment

Normal source and portable runs load `.env` beside the application, creating a blank 20-slot scaffold only when absent. Use `SDP_HOST` and explicit numbered key/portal-ID pairs for per-instance routing. Existing process variables take precedence; `--env-file <path>` selects another file and `--no-env` disables file loading/creation. See [local environment setup](local-env.md) for the complete syntax, scope, missing-key and conflict rules. Existing JSON settings and secure prompts remain supported.

## Per-instance credentials in 2.2.0

Use `--multi-key` for secure per-instance prompts or `--credential-file` for host-bound environment-reference assignments. Unassigned instances remain unassessed; keys are never silently shared. Global Orguser collection needs an explicitly assigned credential and request context. See [setup and examples](multiple-credentials.md). Existing single-key behavior remains available.

## Diagnostic credential recovery fixes in 2.1.2

**This fixes two scanner bugs, not a server-side directory permission denial.**
In 2.1.1, `--diagnose` returned from recovery before checking `--directory-key` or
`--directory-key-env`. A diagnostic invocation therefore tested only the initial
key even when a secondary directory key was explicitly requested. The ordinary
assessment path did perform the secondary attempt.

Version 2.1.2 honors the requested secondary credential in directory-only mode,
using only `GET /api/v3/portals` and the same global rate/time/attempt budgets.
No module inventory, scope-cache recovery, list import or profile save is performed
in this mode. A successful initial directory does not prompt for an unneeded key.

```powershell
python .\sdp_cloud_readiness.pyz --diagnose --directory-key --no-portal-cache --source-build 15240 --max-requests 10
```

This command is supported now; it was defective in 2.1.1. **Do not repeat an already
completed two-credential denial just to test the corrected prompt.** The full-run
log showing two denied directory calls already establishes that the entered
secondary credential did not resolve directory visibility. The log does not verify
its identity, OrgAdmin membership, or whether it differs from the initial key.

The recovery menu now removes `D` after the single secondary attempt has been used.
It offers `L/F/Enter`, explicitly explains attempts to reuse `D`, and warns that
Enter with no known IDs produces diagnostics only. A directory attempt is no
longer described as successful enumeration when it failed.

If both keys were denied, obtain the documented build-specific discovery contract
or a complete verified portal scope from the source administrator/ManageEngine.
Do not add speculative privileges, guess IDs, disable TLS, or retry every endpoint.
See [the precise patch boundaries](../releases/2.1.2.md).

## Diagnostic fixes in 2.1.1

The timeout, permission-denial and parser diagnostics now retain their portal/module context.
Successful authentication is not contradicted by generic failure advice. A Projects denial no
longer produces instructions for portal-directory access. Explicit selection is not presented
as automatic directory enumeration. Parser failures retain type-only response-shape evidence,
without exposing raw keys/values or guessing a response wrapper.

The new `--count-policy first|always|never` option requests totals on the first page only by
default. For slow inventory reads, `never` avoids requesting optional count calculations:

```powershell
.\Run-All-Portals.cmd --count-policy never --timeout 90 --max-requests 2000 --max-minutes 90
```

This retains a single shared 30/minute request limit and existing record/detail caps.
It is not a guaranteed timeout remedy or a permission bypass. The `/asset_modules` wrapper
mismatch in the supplied run cannot be reconstructed from the old diagnostic; this release
repairs the missing evidence, not an unobserved server response. See
[diagnostic context and count-policy details](../releases/2.1.1.md).

## Start with a URL and key

On Windows, extract the whole distribution and double-click **Run-Assessment.cmd**, or open PowerShell in the extracted folder:

```powershell
python .\sdp_cloud_readiness.py
```

If your installation uses the Windows Python launcher:

```powershell
py -3 .\sdp_cloud_readiness.py
```

Enter the final ServiceDesk Plus application URL, including a port or context path when needed. On Windows, automatic mode opens a **local masked API-key dialog**: paste only the key with Ctrl+V and select OK. On other platforms it uses the hidden console prompt. A supplied environment key still takes precedence in automatic mode. The scanner does not display the key text or save it. At completion, use the **Open verified HTML** path printed after the file is reopened and checked. Each run also creates a sibling report ZIP. If discovery cannot identify a portal, the output is a diagnostic report, not a completed source assessment.

The startup banner prints the running version before credential entry. The Windows launcher prefers the self-contained `.pyz` when both the portable runner and source entry point are present, so an older neighboring source tree cannot shadow a replaced portable file. To run source intentionally, use `python .\sdp_cloud_readiness.py`.

## All portals in ONE run (2.1.0)

On Windows, extract this release into a fresh folder and run:

```powershell
.\Run-All-Portals.cmd
```

The ordinary `Run-Assessment.cmd`, `python sdp_cloud_readiness.py`, and portable `.pyz` invocations also default to automatic discovery. The new launcher adds `--all-portals` to make environment-wide intent explicit. Do **not** restrict a normal whole-environment run with `--portal-id 1`.

Provide your host and the normal integration key once. When that key can enumerate the directory, all discovered portals are scheduled with explicit `PORTALID` headers. When the directory returns 403 or is unsupported, the scanner now offers recovery **before ending the current run**:

```text
Continue this SAME run:
D = a directory-authorized key
L = all verified portal IDs/links
F = a portal scope JSON file
Portal scope [D/L/F/Enter]:
```

After the secondary directory credential has already been attempted, `D` is removed and the prompt is `Portal scope [L/F/Enter]`. Blank input never means automatic discovery succeeded.

**D — authorized directory credential.** A second masked/hidden key is used exclusively for the existing `GET /api/v3/portals` operation. It must actually have permission for that operation. Collection credentials perform Requests, Projects, metadata and other module reads: the original key in single-key mode, or explicit instance assignments in multi-key mode. Both credentials share one HTTP client, rate limiter, attempt budget and time budget. No permission is changed and no key is saved. Successful directory-key authentication is not presented as proof that the original integration key can read every portal.

**L — enter the entire verified list once.** Provide the actual numeric IDs, separated by commas, or same-host instance links with a `PORTALID` query parameter. The links are parsed locally, never followed. There is no numeric-range expansion or guessing. All selected portals are assessed together; you do not switch the browser, replace an ID, restart the scanner or merge reports. The user-supplied list remains explicitly distinguished from a complete API-enumerated directory.

**F — reuse a verified scope file.** Copy `examples/config/portals.example.json`, replace its fictional host, IDs and labels with the administrator-verified values, and choose the file. Never put credentials, cookies, raw API responses or other fields in it. Unknown fields and a mismatched host/application context are rejected.

After interactive list/file entry, the scanner can remember the list **only after your consent**. It saves host, IDs, bounded names and a timestamp, never API keys. The default location is `%USERPROFILE%\.sdp-cloud-readiness\portal-scopes` on Windows (`~/.sdp-cloud-readiness/portal-scopes` elsewhere), with a host-derived filename. Subsequent runs refresh directory discovery first; if it is still unavailable, the saved list is reused and all module permissions are rechecked. New/removed portals require a refreshed verified list when directory enumeration remains denied. A saved list is **not** live automatic discovery.

For a pre-supplied list with no portal-recovery questions:

```powershell
.\Run-All-Portals.cmd --portal-file .\portals.json --non-interactive
```

To authorize saving that verified list for future runs:

```powershell
.\Run-All-Portals.cmd --portal-file .\portals.json --save-portals
```

Use `--no-portal-cache` to ignore previously saved scope and offer fresh recovery. `--directory-key` requests a separate directory credential on discovery failure; `--directory-key-env VARIABLE_NAME` uses a secret supplied through an existing secure environment mechanism. Never put a literal key on a command line. `--non-interactive` disables scope recovery prompts only; supply host and the original key through the supported mechanisms for fully unattended use.

The original `--portal-id` / `--portal-ids` behavior remains a **restrictive target set** unless `--all-portals` is also present. With `--all-portals`, provided IDs become verified seeds, combined with discovery/recovery rather than limiting it. An earlier single-portal flag cannot silently reduce a successful all-portal directory result to one portal.

**Authorization boundary:** an operation-level 403 cannot reveal the missing IDs. If neither a permitted directory credential nor a verified full list is available, the tool preserves the gap rather than manufacturing an "all portals" result. An inaccessible portal or denied module is recorded separately while permitted work continues. The existing global budgets still apply; all selected portals appear in coverage, including any work not reached before a global stop. More portals do not each get another 30 requests/minute or 500 attempts.

For a larger planned assessment, explicitly increase the global budgets while retaining conservative pacing:

```powershell
.\Run-All-Portals.cmd --max-requests 2000 --max-minutes 90
```

This increases total scan allowance, not privileges, concurrency or per-collection record/detail caps. See [the one-run portal guide](all-portals.md) for the precise recovery and reporting boundaries.

## Discovery stops or a report appears missing (2.0.2)

A run that stops after its first discovery attempt has not collected module data. **Zero impact findings are not a clean assessment.** Version 2.0.2 prints the underlying sanitized discovery diagnostic directly in the console, adds an explicit `UNKNOWN` topology-coverage finding, and does not depend on opening HTML to explain why collection stopped.

Separate local report publication from server/API troubleshooting. In PowerShell, run these commands from a **freshly extracted current-release folder**:

```powershell
python .\sdp_cloud_readiness.pyz --version

# Local-only test: no host, API key, or HTTP requests.
python .\sdp_cloud_readiness.pyz --check-output --output-dir "E:\sdp-reports"

# Directory discovery only: normal URL and masked-key prompts,
# but no Requests, Projects, Assets, or other module inventory.
python .\sdp_cloud_readiness.pyz --diagnose --output-dir "E:\sdp-reports"

# Normal read-only assessment after the diagnostic is resolved.
python .\sdp_cloud_readiness.pyz --output-dir "E:\sdp-reports"
```

Choose a writable directory that exists on your machine; the examples do not require drive E. `--output-dir` is the **parent** for a fresh timestamped run directory. The tool prints its resolved location. The default parent remains `sdp-assessments` under the current working directory.

Before an assessment consumes API requests, it creates the run directory and checks local write, flush, rename, and read-back. At publication it reopens each expected report, verifies its byte length and SHA-256, and repeats verification before printing paths. A missing or mismatched HTML file is **not** announced as successfully written. Known filesystem failures show a fixed classification plus `errno`/`winerror`, without exposing underlying exception text.

The sibling ZIP is created from the already-sanitized report documents in memory, not by scanning the output directory. It can preserve the HTML even when the individual HTML file could not be written or kept. Both formats can still be blocked by a local filesystem policy; this is not a way to bypass one. Verification establishes existence at that moment, **not permanent retention**. The tool does not infer antivirus, quarantine, permissions, or a particular Windows policy from a missing-file report.

On discovery failure the console distinguishes HTTP/SDP errors from TLS, DNS, refused connections, redirects, HTML responses and JSON schema problems wherever the evidence permits. Unrecognized response text is omitted. The same safe summary is saved as `diagnostics.json`, separately from the assessment. A generic HTTP 403 is not a recommendation to add a named role. A failed TLS exchange does not authenticate the key; arbitrary HTTP 200 JSON also is not treated as an SDP authentication receipt.

Automatic discovery remains `GET /api/v3/portals`. Only an initial `INVALID_QUERY` can trigger **one same-endpoint retry** with minimal documented pagination, inside the existing global limiter and attempt budget. There is no retry by guessing portal IDs or undocumented routes, no changed pagination strategy after the first successful page, and no such query rewrite for 403, 404, authentication, TLS, or content-negotiation failures. If the build genuinely does not expose a usable directory API, use the same-run full-list/file recovery above. A separately authorized directory key is useful only if the operation exists and permits it. The tool cannot manufacture a supported enumeration API.

See [Discovery and report-output troubleshooting](troubleshooting.md) for evidence interpretation and safe support material. The earlier Windows masked-key input fix remains included.

### Windows paste/input fix (2.0.1)

Some legacy Windows consoles pass Ctrl+V to Python `getpass()` as a control character instead of pasting the clipboard. The old generic “printable ASCII” error was a **local input-validation error**, not an API authentication or permissions result. A screenshot cannot establish which character was received.

Automatic Windows mode now avoids that path using a masked local dialog. Python's optional Tcl/Tk component and a graphical desktop are required for the dialog. If it cannot be opened, automatic mode falls back to a hidden console prompt with explicit paste guidance. The console path never falls back to echoing input. No clipboard data is read automatically: pasting into the dialog is an explicit user action.

```powershell
# Check the file you are actually executing.
python .\sdp_cloud_readiness.pyz --version

# Local input-only test: no host, network requests, or reports.
python .\sdp_cloud_readiness.pyz --check-key-input

# Explicitly choose a masked dialog, bypassing an environment key.
python .\sdp_cloud_readiness.pyz --key-input dialog

# Headless/console preference: use the window menu Edit > Paste,
# not Ctrl+V in a legacy console.
python .\sdp_cloud_readiness.pyz --key-input console
```

The local check validates formatting only; it does **not** authenticate the key or test portal access. Explicit `console` or `dialog` selection always prompts rather than silently using a possibly stale environment key. In default `auto` mode, the existing `SDP_API_KEY` / `--api-key-env` behavior is retained.

Interactive malformed input is retried locally up to three times without issuing an HTTP request. Empty input, a Ctrl+V control character, other controls, interior whitespace, and non-ASCII content have distinct safe messages. Ordinary surrounding whitespace and edge-only BOM/zero-width-space markers are removed with a notice. Interior characters are never deleted or rejoined, quoted text is not unquoted, and invalid input is not transmitted. Do not put the key in a command line, a JSON file, a ticket, or a screenshot. See [Windows key input and troubleshooting](windows-key-input.md).


The portable application needs only Python and its `.pyz` file:

```powershell
py -3 .\sdp_cloud_readiness.pyz
```

On Linux or macOS:

```bash
python3 sdp_cloud_readiness.py
```

The normal flow is topology discovery, module/capability assessment, portal inventory, bounded detail and field inspection, then migration-impact analysis. A denied operation in one portal does not prevent work in other portals. A global authentication failure, interruption, or exhausted global budget stops further collection and preserves evidence already obtained.

## Portals, ESM instances, and automatic discovery

An ESM installation can contain separate ServiceDesk Plus service-desk instances, also called **portals**, such as IT, HR, or Facilities. A portal can have its own records, templates, roles, configuration, and licensed capabilities. The same integration key can have different effective visibility in different portals. ManageEngine describes the per-instance licensing model in its [ESM licensing documentation](https://www.manageengine.com/products/service-desk/on-premises/faq/esm-license-management.html).

On-premises V3 operations use the integration key in the `authtoken` header. Portal-scoped operations also receive an explicit **`PORTALID` header**. A key that can list Requests in one portal does not thereby prove access to Projects in another. The scanner records portal provenance on inventories, field definitions, diagnostics, and findings. See the [official V3 header change notice](https://pitstop.manageengine.com/portal/en/community/topic/deprecating-few-params-of-v3-api-urls).

Automatic discovery uses **GET `/api/v3/portals` without a portal header**, and follows its documented `portals` and `list_info` response structure. The on-premises request/response contract is published in [Netskope's primary ServiceDesk Plus integration documentation, “Fetch All Portals → For On-Premises”](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator). A corresponding list operation was not located in the reviewed public ManageEngine on-premises V3 guide or official ServiceDeskPlus Postman collection. Consequently, the scanner does **not** assert a universally supported minimum build for this route. This sourcing qualification is included in topology coverage.

When discovery works, every discovered portal is scheduled for assessment, subject to the shared scan budgets and any explicit module selection. Listing a portal establishes topology visibility; scoped operation results establish whether the key can actually assess it. The report retains the portal ID, safe display name, reported type/state/edition when exposed, discovery source, access evidence, and scan status.

When discovery is denied, unsupported, malformed, or unavailable on the installed build, the report preserves that diagnostic. **No portal ID is guessed, no integer range is probed, and no implicit/default portal is scanned.** Use same-run directory-key/list/file recovery or a previously consented host-bound profile. Partial discovery retains its safely discovered IDs and clearly states that additional portals may remain unknown.

### Target known portals explicitly

```powershell
python .\sdp_cloud_readiness.py --portal-id 3
python .\sdp_cloud_readiness.py --portal-id 1 --portal-id 3
python .\sdp_cloud_readiness.py --portal-ids 1,3
```

Without `--all-portals`, an explicit override bypasses enumeration and assesses only those targets. It does not establish whether the installation contains other portals. IDs must be positive ASCII decimal identifiers; the scanner never uses the override as a starting point for further enumeration.

`--max-portals 100` is the default discovery/target cap. It is a scanner safety limit, not a ManageEngine product limit. Increase it when needed; reaching it while more portals exist produces incomplete topology, not a claim that all portals were assessed.

### Environment-wide resources

The ESM organization-user directory, `/orgusers`, is a global data resource and is collected **once**, with the request context retained where the published example requires one. It is not duplicated for every portal. Its availability and permission requirements are documented separately from portal `/users` and `/technicians`; see the [official Orguser documentation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser).

Portal user/technician counts represent visible memberships. Their sum is not a count of unique people across the organization. Assets, Computers, and CIs can also overlap; their inventories are shown separately rather than added into one unique-object total.

## Read-only and privacy boundaries

All source requests use **HTTP GET** against an explicit allowlist. Dynamic Asset/CI-type metadata paths can be admitted only from the corresponding documented type catalogs, after validation, as exact metadata-only GET paths for the originating portal. Response links and redirects are never followed.

The scanner cannot POST, PUT, PATCH, DELETE, execute SQL or stored reports, start migration/discovery/export jobs, modify configuration, send messages, or download attachment bodies. A GET that triggers an action is not authorized merely because it uses GET; only the reviewed inventory/detail/metadata routes are callable.

The API key is accepted through a local masked dialog, a hidden console prompt, or an environment variable. It is never put in a URL or saved in configuration, reports, logs, exceptions, or debug output. Server responses are redacted before analysis. API diagnostics retain bounded, recognized response evidence; arbitrary error bodies are omitted when they cannot be safely retained.

Source rows are analyzed in memory. Outputs retain necessary identifiers, portal/module context, field labels and constraints, counts, and migration findings. They avoid raw descriptions, notes, email addresses, attachment filenames, scripts, SQL text, option labels, and unnecessary field values. Attachment checks use exposed metadata such as size and presence; no attachment content is fetched.

No collected data is sent to an AI service or another assessment endpoint. Runtime network activity is limited to the configured source, using the operating system's applicable proxy settings. Documentation links are references; the scanner does not fetch them during a live assessment. Reports can still describe internal structure and should be handled as internal information.

Review the callable inventory without credentials:

```powershell
python .\sdp_cloud_readiness.py --list-endpoints
```

## Checkpoint and resume

Add `--checkpoint` to opt into instance-by-instance collection with durable, sanitized checkpoints. Resume with `--resume <checkpoint.json>` and fresh `--max-requests` / `--max-minutes` budgets. Completed instances are reused; interrupted instances restart. The default scheduler is unchanged. See [resume commands, binding and limitations](resume.md). Existing runs without checkpoints cannot be resumed retroactively.

## Global pacing, budgets, and fair coverage

| Setting | Default | Scope |
| --- | ---: | --- |
| Request rate | 30/minute | One scheduler shared by all portals and phases |
| Concurrent requests | 1 | Entire scanner |
| HTTP attempt budget | 500 | Includes topology, metadata, details, and retries |
| Network assessment time budget | 20 minutes | Entire scanner |
| Per-request timeout | 30 seconds | Each attempt, bounded by remaining runtime |
| Portal cap | 100 | Topology/explicit target set |
| Requested page size | 100 | Each paginated collection |
| List record cap | 5,000 | Each portal/collection |
| Record details | 20 | Each portal/collection |
| Metadata targets | 20 | Each portal/module's observed forms or types |
| Requests inspected for notes/tasks | 10 | Each applicable portal collection |
| Child records per sampled parent | 200 | Each inspected child collection |

**30 requests/minute is the scanner's conservative policy, not a claim about a ManageEngine contractual or universal API limit.** Other integrations can use the same server capacity. Honor stricter limits specified by your administrator or vendor. The official [on-premises error-code guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html) documents rate-limit code `4015`; the scanner also handles HTTP 429 and `Retry-After` with bounded backoff.

Portal A does not receive a fresh 30/minute allowance when Portal B starts. Every attempt, including discovery, fallback reads, and retries, consumes the same scheduler and budgets. Collection work is interleaved across portals and modules to improve breadth before large lists or detail sampling consume the remaining budget.

A completed list remains complete if a later operation exhausts a global budget. Incomplete lists retain the observed count and stop reason. An operation that never started has **unknown records**, not zero. Detailed inspection is reported separately from list pagination.

API traversal is not a transactional snapshot. Changing records, repeated/overlapping pages, missing wrappers, and inconsistent pagination are explicit confidence limitations. Sampling is deterministic and bounded; it is not a statistically representative estimate. Counts and age findings from incomplete lists are lower bounds within the visible scope.

### Follow the progress

The five progress phases are:

1. Discovering ServiceDesk Plus topology.
2. Enumerating portal modules using documented read operations.
3. Collecting inventories across portals.
4. Sampling record details/subresources and module-aware field metadata.
5. Evaluating migration impact and writing reports.

A capability probe is the first page of the corresponding documented collection, reused as inventory evidence. There is no invented universal “enabled modules” API. A successful page establishes that the operation is exposed to the key. An unavailable endpoint does not establish that the business module is unused.

Progress uses the portal name and collection. `800 records observed; collecting; more pages queued` means pagination is continuing. `List complete for API-visible scope` means that list finished for the portal/account/filter; details may still be sampled. Denied or unsupported operations display **count unknown**. `0` is valid only after a successful empty response.

Press **Ctrl+C once** to stop collection and write a partial report. Request/time limits also preserve partial results. A blocking operating-system DNS/connect/read operation can exceed the intended wall-time limit until the operating system returns; this is not a hard real-time cancellation facility.

### Adjust depth or rate

```powershell
python .\sdp_cloud_readiness.py --rpm 15 --max-minutes 40
python .\sdp_cloud_readiness.py --full-inventory --max-requests 3000 --max-minutes 120 --detail-limit 100 --metadata-limit 50
```

`--full-inventory` removes the per-collection record cap; global budgets and separate detail/metadata limits still apply. `--detail-limit 0` selects all observed record details. `--metadata-limit 0` selects all observed metadata targets. Neither option discovers hidden objects or certifies a complete administrator field registry. `--subresource-parents 0` skips child-resource inspection.

## Field/UDF discovery and its limits

Field collection is **portal- and module-aware**. It no longer treats a bare `/udf_fields` response as a universal field registry or a failure there as a universal permission problem. The strategies and verified source links are in [field discovery reference](../reference/fields.md).

| Scope | Strategy | Meaning of successful coverage |
| --- | --- | --- |
| Requests | `/requests/metainfo`, selecting template IDs observed in that portal | Fields exposed by inspected incident/service templates; repeated appearances are deduplicated |
| Changes | Documented form metadata, with an observed record-specific metadata fallback where applicable | Inspected form scope; not every administrative field/template/stage |
| Assets and Computers | Documented `_metainfo` routes and exact per-product-type metadata paths discovered from `asset_modules` | Fields attached to inspected product-type layouts |
| CMDB / CI types | `/{observed CI-type API plural name}/_metadata` from `ci_types` | Exposed definitions for inspected CI types; unavailable API names and uninspected types remain gaps |
| Older Asset/Workstation APIs | Documented legacy `metainfo`, using observed product-type selectors | Legacy schema evidence only, with compatibility limitations |
| Other modules | A verified module-specific definition strategy where available; otherwise observed UDF names from already collected rows | Observed-key evidence remains inferred and incomplete |

The code also supports documented Department metadata and module-selected Space UDF lists when the corresponding scope is available to field discovery. A Space example is not generalized into Request, Problem, Project, or Release APIs. Arbitrary `/<module>/_metainfo` routes are not constructed by analogy.

Metadata retains internal IDs/API names, safe display labels, exposed type/length/mandatory/read-only constraints, allowed-value counts where available, portal/module provenance, and template/product-type context. Defaults and allowed values are measured when relevant but their raw text is not included in reports. A missing flag remains unknown. An observed UDF key alone does not prove its configured data type, maximum length, display label, or custom-versus-built-in origin.

**Complete form metadata is not the same as a complete administrator UDF registry.** Unattached fields, uninspected templates/types, permissions, build changes, and modules without a verified public definition endpoint remain explicit gaps. Counts from observed fields are lower bounds. A definition that permits a value longer than a documented Cloud limit indicates potential exposure; it does not prove that a source value actually exceeds that limit.

Field impact applies documented limits only to the relevant module/type and retains target-edition/tenant qualifications. Review [ManageEngine's migration limitations](https://help.servicedeskplus.com/migration-limitations) and [Cloud field limits](https://help.sdpondemand.com/field-count/character-limit) alongside the report. Scripts, form rules, dependent fields, workflow behavior, and licensing may still require reconstruction or target validation.

## Connection settings and selection

Copy `examples/config/connection.example.json` and change its non-secret settings:

```powershell
python .\sdp_cloud_readiness.py --config .\connection.json
```

Leave `portal_id` as `null` and `portal_ids` as `[]` for automatic discovery. To use explicit targets in JSON, populate only the desired override field, for example `"portal_ids": ["1", "3"]`. An optional `"portal_file": "portals.json"` supplies a host-bound verified list while automatic discovery is still attempted. Keep API keys out of JSON files.

For unattended use, inject `SDP_API_KEY` through your existing secret mechanism. `SDP_HOST` can supply the host; `--api-key-env VARIABLE_NAME` selects a different key variable. Avoid literal keys in shell history or scheduler command lines.

`--modules` narrows assessment to selected logical collection keys shown by `--list-endpoints`:

```powershell
python .\sdp_cloud_readiness.py --modules requests,projects,releases
python .\sdp_cloud_readiness.py --modules field_definitions
```

The legacy `field_definitions` name remains a **field-discovery selection alias**. It uses the module-aware metadata architecture and supporting inventory context; it does not restore a bare global `/udf_fields` probe. A selected-module scan reports its selection and cannot certify omitted modules.

### Certificates and build context

TLS verification is enabled. Supply an internal CA bundle when needed:

```powershell
python .\sdp_cloud_readiness.py --host https://helpdesk.example.org:8443 --ca-file C:\Certificates\company-ca.pem
```

Use the final application URL because redirects are disabled. `--allow-http` and `--insecure-tls` are explicit diagnostic/legacy exceptions and are recorded in the report. Prefer trusted HTTPS because plain HTTP exposes credentials in transit.

The scanner does not invent a source-build or key-expiration endpoint. Supply a known build when available:

```powershell
python .\sdp_cloud_readiness.py --source-build 15100 --target-edition Enterprise --target-region US
```

Build and target values are labeled **user supplied**, not API verified. No documented safe integration-key-expiration read was verified for this release; the scanner does not infer expiration, expose key metadata, or require it to proceed.

## Read diagnostics correctly

Collection status, capability evidence, and migration finding status are separate. The complete diagnostic reference is [diagnostics and coverage reference](../reference/diagnostics-and-coverage.md).

| Outcome | Interpretation |
| --- | --- |
| `SUCCESS`, `COLLECTING` | A read succeeded or additional pages remain queued |
| `EMPTY`, `COMPLETE` | Successful complete list within API-visible scope; EMPTY specifically confirms zero returned rows |
| `INCOMPLETE` | Some scope remains unresolved; use the specific stop reason and detail coverage |
| `AUTHENTICATION_FAILED` | The API reports an invalid/failed credential; further API reads stop |
| `PERMISSION_DENIED` | This operation was denied; a particular role requirement is not inferred |
| `PORTAL_CONTEXT_REQUIRED` | Recognized response evidence indicates required portal context |
| `PORTAL_NOT_ACCESSIBLE` | Recognized evidence identifies portal access denial |
| `MODULE_NOT_ENABLED`, `MODULE_NOT_AVAILABLE` | Explicit evidence indicates disabled module or module/license unavailability |
| `ENDPOINT_UNSUPPORTED`, `API_VERSION_INCOMPATIBLE` | Endpoint/build compatibility is unresolved or explicitly incompatible |
| `INVALID_QUERY` | The API rejected request parameters; examine the recorded evidence and compatibility context |
| `RATE_LIMITED` | Throttling/backoff remains unresolved after bounded retries |
| `REQUEST_BUDGET_REACHED`, `TIME_BUDGET_REACHED`, `RECORD_LIMIT_REACHED` | A scanner limit stopped further work; previously completed scope stays complete |
| `NETWORK_ERROR`, `SERVER_ERROR`, `PARSE_ERROR`, `UNKNOWN_API_ERROR` | The read failed for the recorded reason; no zero-record inference is made |
| `NOT_SCANNED`, `NOT_STARTED`, `INTERRUPTED` | Scope was not read or work was interrupted; retained evidence and reasons remain visible |

A generic HTTP 403 is not evidence that Projects requires Project Admin, that a module is disabled, or that the key itself is invalid. Projects are queried with the explicit originating portal. If denied, the report retains HTTP status, SDP codes, sanitized message evidence, portal, logical endpoint/module, probable cause, and retry guidance.

For a permission gap, verify the key's effective operation/site/portal visibility with your administrator. For a context gap, verify the selected portal ID and installed API contract. For unsupported metadata, check the source build and documented fallback coverage. Increasing scan budgets does not fix denied operations. No permissions are changed by this tool.

## What the assessment answers

The analyzer preserves established migration checks and applies them per portal: record-age exposure (including observed records older than one/five years), history and archived-record gaps, relationships and Request↔Change associations, attachment metadata and note-attachment exposure, typed text/field constraints, templates/form rules, SLA and workflow references, approval/recurring-maintenance gaps, Problem omissions, Assets/CMDB relationships and service tags, query-report exposure, technician identities, Projects, Releases, and external automation/integration unknowns.

The report answers seven migration questions across the discovered environment. Each answer separates **confirmed source evidence**, **API coverage limitations**, **target-Cloud unknowns**, **vendor confirmation**, and **project/business decisions**.

| Migration question | Contribution from the scan | What still needs agreement or validation |
| --- | --- | --- |
| Which documented limitations apply? | Source volumes, dates, field constraints, templates and observed relationships | Exact target edition/region/limits, migration scope, approved exceptions |
| How should old records, CMDB, Releases, Projects and custom modules be handled? | Per-portal evidence and module/metadata coverage | Archive, migrate, reconstruct or retire decisions; complete relationship/history preservation |
| What needs confirmation about the final delta? | Records and dependencies that will need reconciliation | Cutoff, changed/deleted records, attachments, repeatability, final freeze and outage process |
| Which identifiers and relationships must survive? | Visible IDs, associations and dependency signals | ID preservation versus cross-reference mapping, URL changes, integration rewrite and reconciliation |
| What needs reconstruction or additional licensing? | Visible templates, field definitions, reports, workflow references and source edition metadata | Complete workflow/script behavior, target features/add-ons, ownership and test criteria |
| What export and recovery capabilities are required? | Stated retention/reporting needs and source evidence gaps | Export completeness, audit/history scope, retention, restore method, recovery objectives and commercial terms |
| What should block migration acceptance? | Confirmed source risks and unresolved critical coverage gaps | Business-approved acceptance criteria and evidence from rehearsal/final reconciliation |

These are evidence-backed answers with remaining actions. A source-only scan cannot prove future Cloud behavior, complete a migration rehearsal, establish contractual recovery guarantees, or approve acceptance. See [the migration process](https://help.servicedeskplus.com/op-to-od-migration), [published data scope](https://help.servicedeskplus.com/data-migrated), and [migration limitations](https://help.servicedeskplus.com/migration-limitations).

Optional business context is accepted through `examples/config/answers.example.json`:

```powershell
python .\sdp_cloud_readiness.py --answers .\answers.json
```

Replace known values and leave unknown answers as `null`. Retention years, Power BI needs, dashboard delay, external scripts, and recovery requirements make questions more specific; they remain user-supplied context.

## Reports and compatibility

| File | Purpose |
| --- | --- |
| `report.html` | Offline executive/environment summary, topology, per-portal risks, impact sections, coverage, questions and acceptance blockers |
| `report.md` | Markdown version of the assessment |
| `assessment.json` | Structured environment and first-class portals, global resources, findings, field inventory, diagnostics and sources |
| `findings.csv` | Remediation register including portal/environment scope and evidence basis |
| `coverage.csv` | Portal/module/endpoint results, nullable observed counts, pages, list/detail completeness, diagnostic reasons and confidence |
| `vendor-questions.md` | Remaining vendor and project questions with the relevant portal/module context |
| `diagnostics.json` | Small sanitized discovery/connection summary, useful without opening HTML |
| `report-manifest.json` | Expected report filenames, byte lengths, SHA-256 values, and point-in-time publication status |
| Sibling `<run-directory>.zip` | Verified ZIP containing the six reports, diagnostics, and manifest; created only from explicit sanitized documents |
| `branded/<Brand>/` | Presentation copies for the client (HTML, PDF, workbook, optional Scope of Work) and `branded-manifest.json`; not part of the verified set or ZIP. See [branded deliverables](branded-deliverables.md) |

Existing report formats remain available. JSON schema **2.0** adds first-class environment/portal structures; flat findings and coverage retain portal identifiers so existing integrations can adapt without losing provenance. Consumers should read `schema_version`, use scope and portal ID with resource keys, and treat a blank/null unknown count differently from zero. Do not key findings only by their old single-portal rule ID or add the same global inventory once for each portal.

Finding states retain their meanings: `CONFIRMED_IMPACT` is supported by observed source evidence; `NO_ISSUE_OBSERVED` applies only to the explicitly covered scope; `UNKNOWN` reflects insufficient evidence; and `MANUAL_CONFIRMATION` requires vendor, target, business, or external-system input. There is no overall green readiness score. Finding counts are not unique affected-record totals.

## Try the synthetic scenarios

```powershell
python .\sdp_cloud_readiness.py --demo
python .\sdp_cloud_readiness.py --demo --demo-scenario multi
python .\sdp_cloud_readiness.py --demo --demo-scenario single
```

`--demo` defaults to a clearly labeled multi-portal example. It uses no credentials and makes no source-system network requests. The packaged example under `examples/synthetic-assessment` demonstrates the consolidated reports. Synthetic evidence is never presented as an assessment of your installation.

## Help, exit codes, and validation

```powershell
python .\sdp_cloud_readiness.py --help
python .\sdp_cloud_readiness.py --version
python -m unittest discover -s tests -v
```

Exit `0` means the selected mode completed with verified output, not that migration is approved. A successful `--diagnose` run establishes only directory coverage, and `--check-output` establishes only local output behavior. Exit `1` indicates a startup/settings/local-file error or incomplete report publication. Exit `2` means diagnostic/partial reporting completed with a global interruption, authentication failure, or stop condition, including unavailable portal discovery. Exit `130` means cancellation before collection or a second interruption while recovering reports. Individual denied/unsupported operations can still produce reports with exit `0`; automation must inspect topology, coverage, finding statuses and acceptance blockers.

[Changelog](../../CHANGELOG.md) records release changes. [Validation record](../development/validation.md) describes the synthetic verification and its limits. The suite covers multi-portal discovery, scoped GET headers, a single global scheduler, permissions and module diagnostics, independent pagination, budgets/interruption, metadata strategies, source-rule compatibility, aggregation, and report privacy. It does not use customer credentials or certify behavior on every SDP build.

Use the installed build's in-product API documentation and a controlled live run to resolve discrepancies in public examples. Source-build compatibility, complete account visibility, and migration outcomes remain acceptance work for the source/target owners and ManageEngine.

## Build the portable distribution

From the extracted source directory:

```powershell
python .\tools\build_release.py --output-dir .\dist
```

The standard-library build creates the portable `.pyz`, the complete source ZIP, the Windows launcher, the synthetic HTML example and `SHA256SUMS.txt`. An explicit file manifest includes source, documentation, tests and synthetic fixtures; customer assessment directories and local caches are excluded. The source ZIP also contains an internal checksum manifest for its files. Given identical input files, the archive bytes are reproducible.
