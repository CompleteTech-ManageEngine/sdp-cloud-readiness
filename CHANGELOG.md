# Changelog

## 2.2.0

- Add explicit per-instance collection credentials, secure prompts and host-bound environment-reference configuration.
- Isolate authentication failures by credential while retaining one transport and global budgets.
- Separate optional ESM global-resource credentials from directory and instance scopes.
- Report credential coverage without secrets; add multi-key synthetic and packaged demonstrations.
- Preserve unavailable discovery at recovery-input EOF instead of marking it interrupted.


## Unreleased

- Add Word (`.docx`) and Markdown copies of the branded report and vendor questions alongside HTML and PDF, and a Markdown copy of the Scope of Work; every branded document now comes in the same four formats from one shared Markdown reader. Large tables are written directly so a full assessment converts in seconds.
- Add `tools/build_docs.py` to render the repository documentation as branded HTML, PDF and Word, with a combined handbook and contents page.

- Document branded deliverables and the Scope of Work: new guides `docs/guides/branded-deliverables.md` and `docs/guides/scope-of-work.md`, validation record `docs/development/branding-validation.md`, and links from the usage, local-environment and troubleshooting guides and the documentation index.

- Render an engagement `scope-of-work.md` from the assessment folder as branded HTML, PDF and editable Word (optional `python-docx`), with `{{consultant}}`, `{{client}}`, inventory and confirmed-impact placeholders filled from the brand and `assessment.json`; incomplete evidence stops rendering, and the figures used are recorded in `branded-manifest.json`.

- Write branded copies to `branded/<Brand>/` so one assessment can be delivered under several brands without overwriting.

- Add CompleteTech-branded client deliverables (preset `completetech`, `assets/logo.png`) on every run of the entry points, with `--brand <file|preset|none>`, `--prepared-for`, `--brand-assessment <folder>`, `--no-pdf`, and `SDP_BRAND_FILE`/`SDP_PREPARED_FOR` in `.env`. Copies go to `<assessment>/branded/` (report and vendor questions as HTML and PDF, findings/coverage workbook, hash manifest); the verified unbranded reports are unchanged. PDF printing uses a local headless Edge/Chrome; the workbook uses optional `openpyxl`.
- Package the repository as a CompleteTech LLC agent skill (`SKILL.md`, `agents/openai.yaml`, `ONBOARDING.md`, `BRANDING.md`, `BRAND_ASSETS.md`).

- Accept the current asset-module wrapper alongside the earlier explicit contract and numeric Change role-slot metadata; add the documented modern workstation-list fallback and safe metadata contract diagnostics.
- Add explicit failed/selected-instance retries and full restart with changed collection limits, preserving prior committed evidence and pending retries.
- Distinguish completed child samples, row caps, transport/server failures and optional credential gaps in reports and console guidance; add coverage-recovery and source-review guides.

- Add opt-in `--checkpoint` and `--resume` at completed-instance boundaries, with sanitized report evidence, atomic integrity-checked files, concurrent-use locks, frozen host/scope/collection contracts, and fresh per-pass budgets. Interrupted instances restart; completed findings and coverage gaps persist without storing keys or source records. Normal collection scheduling is unchanged.

- Clarify ESM key creation, roles/session safety, optional credentials, excluded-instance coverage and diagnose limits. Align generated `.env` comments with the example and explain slot-only discovery skips without exposing credentials.

- Add default local `.env` loading and non-overwriting blank setup with 20 numbered instance key/portal-ID pairs, explicit host binding, additional slots, separate directory/global credentials, path override and opt-out.
- Preserve process environment precedence, reject conflicting assignments, and report ID-only slots as missing credentials. Bound literal parsing and exclude local environment files from release archives.
- Add source/portable/Windows-launcher, routing, redaction, parser and packaging regressions for issue #5.
- Replace the long root README with a quick start and move the full guide to `docs/guides/usage.md`.
- Group documentation into guides, reference, development evidence, and release notes; add a documentation index and contributor guide.
- Move non-secret configuration templates into `examples/config/`.
- Keep generated portable binaries and checksum manifests in ignored `dist/`; preserve the root source entry points and Windows launchers.
- Update the explicit release manifest and packaging checks for the new documentation and example paths.

## 2.1.2 — October 14, 2026

- Fix `--diagnose` silently ignoring `--directory-key` and `--directory-key-env`. Honor the explicitly requested secondary directory attempt while preserving directory-only GETs, one global scheduler, stop handling and no module/list/cache work.
- Establish the diagnostic-only boundary before invoking scope recovery for library callers as well as the CLI. Reject explicit ID/file/save options in diagnostic mode instead of reading unused files.
- Remove the D choice once the bounded secondary attempt has been consumed; explain repeated D input without making another request. Explicitly state that Enter with no IDs writes diagnostics only.
- Do not describe failed secondary attempts as successful directory enumeration, and do not infer credential identity or role membership.
- Add 24 regressions for exact CLI flag behavior, independent directory pagination, authentication separation, GET-only credential isolation, cancellation, shared pacing/Retry-After/budgets, no local-list recovery in diagnostic mode, and same-run multi-portal list recovery after both credentials are denied.
- Keep existing module collectors, field strategies, endpoints, transport, migration rules, report formats and release packaging. No new API or permission bypass was introduced; the live build-15240 portal-directory denial remains unresolved.

## 2.1.1 — October 14, 2026

- Correct module-vs-directory diagnostic advice and preserve previously established integration-key authentication when another read times out. Keep directory-only credential authentication separate.
- Preserve parser-failure endpoint, logical module, portal, actual HTTP/SDP evidence and fixed response-format evidence; add safe JSON shape/contract reasons without recording source values or arbitrary keys. Apply to list, detail and pagination-integrity failures.
- Include global-resource and metadata-discovery errors in the small diagnostic document. Add per-operation next steps to diagnostic JSON and HTML/Markdown reports.
- Add diagnostic schema 1.1 scope fields; preserve prior fields, clarify selection-complete versus directory-complete, and label explicit IDs as explicit rather than automatic.
- Add `--count-policy first|always|never`; default to first-page total requests to avoid repeating optional count work. Preserve filters, ordering, per-portal pagination, shared pacing and budgets. Store count-page provenance and never use stale totals to infer unverified termination.
- Add an explicit-scope warning before collection and preserve all-portal, same-run recovery, local scope caching, GET-only safety, report verification and credential privacy behavior.
- Add 29 regressions for the supplied diagnostic failure pattern, privacy, scoped advice, independent portal counts, protocol provenance and parser contracts. No live customer parser mismatch or timeout cure is claimed.

## 2.1.0 — October 14, 2026

- Add same-run portal-scope recovery after directory denial/unsupported discovery: hidden directory-only key, one full verified ID/link list, or a host-bound non-secret JSON file. Continue the existing collector instead of requiring portal-by-portal restarts.
- Add `Run-All-Portals.cmd`, `--all-portals`, `--portal-file`, `--directory-key`, `--directory-key-env`, `--save-portals`, `--no-portal-cache` and `--non-interactive`. Legacy explicit portal overrides remain restrictive unless `--all-portals` is supplied.
- Optional consented profiles remember IDs/names for one normalized host/application context, never credentials. Live directory discovery is retried first on later runs. Saved lists remain explicitly incomplete directory evidence and module access is rechecked.
- Restrict the optional second credential to `/portals` without a portal header using a view of the SAME client. No extra limiter, request budget, default PORTALID, guessed ID range, new endpoint or module privilege is introduced. Separate authentication diagnostics prevent a directory-key result from misrepresenting the scan key.
- Preserve directory errors alongside recovered portal provenance in JSON/HTML/Markdown/CSV and vendor questions. Contextualize retry messages with the portal and logical endpoint. Keep verified report-file/ZIP publication and masked Windows input fixes.
- Add a denied-directory, one-run multi-portal recovery demonstration and regression tests for recovery, saved scopes, credential isolation, global budgets, permissions, privacy and packaging.


## 2.0.2 — October 14, 2026

Address a run that stopped after one portal-discovery attempt and printed a report path the user could not find. The submitted log does not establish the HTTP/SDP response, certificate outcome, or reason the file was absent. This release fixes insufficient diagnostics and publication verification; it does not claim that the customer's exact live failure was reproduced.

- Print sanitized portal-discovery diagnostics in the console, including under `--quiet`, before analysis or file publication. Preserve HTTP status, SDP codes, recognized safe response phrases, response format and fixed transport-failure categories. Never print bodies, arbitrary server text, redirect Location values, or underlying exception text.
- Distinguish certificate verification, TLS negotiation, DNS, timeout, refused/reset connection and blocked redirect evidence where the exception/response supports it. Keep TLS verification enabled. Do not mark arbitrary HTTP 200 JSON as proven SDP authentication.
- Match the published on-premises GET content-type header. For initial `INVALID_QUERY` only, permit one bounded retry of the same directory endpoint with `row_count` and `start_index`. Preserve the first error and share the existing scheduler/budgets. No endpoint guessing, portal-ID guessing or strategy switch mid-pagination.
- Add `--diagnose` for directory-only reads with normal host/hidden-key entry; it does not query module inventories. Add `--check-output` for actual local report and ZIP publication without a host, credentials, or HTTP requests.
- Add a pre-scan filesystem write/read/rename probe. Publish individual reports atomically; reopen and check lengths and SHA-256 after writing and before printing paths. Remove the constructed fallback HTML path from the CLI.
- Add sanitized `diagnostics.json` and a publication `report-manifest.json`. Write a sibling ZIP from explicit in-memory sanitized report documents, so a failed individual HTML write does not exclude HTML from the ZIP. Other files already in the folder are never archived.
- Continue trying the other formats and ZIP after an individual file failure. Expose fixed filesystem classification and numeric errno/winerror. Return an error for incomplete publication instead of an unverified success. Verification is point-in-time, not a retention guarantee.
- A no-portal run now says **ASSESSMENT NOT PERFORMED**, adds an environment-wide high-severity `UNKNOWN` topology-coverage finding, and includes it in acceptance questions/blockers. No source records are interpreted as zero impact.
- Retain all six report formats, JSON assessment schema 2.0, masked-key fix, single global limiter, portal/UDF collection, explicit overrides, source impact rules and read-only/privacy protections.
- Add 44 regressions for discovery compatibility, safe transport evidence, local publication faults, diagnostic-only/output-only modes, and a real localhost HTTP failure. Expand CLI/release/privacy expectations for the additional outputs. Update the launcher exit summary and troubleshooting documentation.

## 2.0.1 — October 14, 2026

Fix local API-key entry after repeated Windows console “printable ASCII characters without whitespace” failures. The screenshot establishes local rejection, not a server-side key, role or portal failure; the documented Ctrl+V control-character behavior is a matching cause, not a proven reconstruction of the user's keystrokes.

- Add a credential-input layer; Windows auto mode uses a local masked dialog to bypass the legacy `getpass()` paste path. Console entry remains explicit and is the fallback when the optional Tcl/Tk GUI is unavailable.
- Add `--key-input auto|console|dialog`. Explicit interactive modes bypass environment credentials; auto retains the prior environment interface. No automatic clipboard reads, plaintext input fallback, key files or command-line key option.
- Add `--check-key-input`: local format/input preflight, no host, HTTP calls, or report files, and no claim of authenticated access.
- Retry malformed interactive input up to three times with category-only diagnostics. Detect Ctrl+V separately; reject interior whitespace, controls and non-ASCII data without exposing input. Normalize only surrounding whitespace and edge BOM/zero-width-space markers, with a notice; do not repair interior key content.
- Guard Tk callback failures and getpass exceptions against tracebacks or credential disclosure. Cancel stops without switching input methods or connecting.
- Show the running version before prompting. The Windows launcher now prefers the portable runner over potentially stale source, disables delayed expansion, and still forwards arguments and exit status.
- Avoid creating empty assessment directories when key entry or local validation fails.
- Add input/CLI regressions, real masked-dialog tests with synthetic data, updated troubleshooting, and deterministic packaging verification.

Unchanged from 2.0.0: transport and GET allowlists, portal discovery and scoping, global pacing/budgets, UDF/module collection, impact analysis and six report formats. Transport still independently rejects unsafe header values. Native Windows desktop execution was not available during release testing; the real dialog tests ran under Linux/Xvfb.

## 2.0.0 — October 7, 2026

The original architecture treated the source as one implicit portal and attempted a single generic UDF inventory. That could omit other ESM instances and conflate a wrong portal, a denied operation, a disabled module, and an unsupported field-definition API. Version 2.0 makes the environment, portal context and evidence coverage explicit.

- Discover API-visible portals with GET `/portals`, retain safe topology metadata/provenance, and schedule discovered portals through one shared client. The discovery contract is transparently attributed to Netskope's primary on-premises integration documentation; a corresponding native ManageEngine/Postman list contract or minimum supported SDP build was not established.
- Preserve explicit targeting through repeatable `--portal-id`, comma-separated `--portal-ids`, and non-secret configuration. No portal IDs are guessed or enumerated by integer probing when discovery is unavailable. `--max-portals` bounds topology work.
- Send explicit `PORTALID` for portal-scoped operations, including Projects, and retain the response's originating scope. Collect the global ESM Orguser directory once rather than once per portal.
- Use documented first-page reads as capability evidence where a universal enabled-module API is unavailable. Reuse successful pages for inventory and keep operation availability separate from licensing assumptions.
- Add structured HTTP/SDP diagnostics for authentication, authorization, portal context/access, module availability, query/build compatibility, throttling, network/server/parse failures and scanner limits. Generic 403 no longer implies a specific required role, and failed/unread collections no longer appear as zero-record successes.
- Replace the bare `/udf_fields` inventory with portal/module field strategies, observed-template selectors, documented `metainfo`/`_metainfo`, CI-type `_metadata`, exact validated Asset/CI-type paths and documented compatibility fallbacks. The old `field_definitions` CLI name is a selection alias only.
- Retain field provenance and exposed constraints, deduplicate repeated layout appearances, and distinguish complete inspected form scope from an unproven administrator field registry. Observed UDF names remain inferred evidence when no verified definition endpoint is available. `--metadata-limit` controls observed form/type inspection.
- Preserve migration rules with portal-aware findings and module-specific field qualifications. Seven migration answers separate source evidence, API gaps, target unknowns, vendor commitments and business decisions.
- Add consolidated topology/access summaries, per-portal migration impacts, separate global resources, field coverage and acceptance questions to the existing HTML, Markdown, JSON and CSV report formats. JSON schema 2.0 introduces first-class portals while retaining flat findings and coverage for integration compatibility.
- Report `collecting` during paging, successful empty/complete lists distinctly, and exact incomplete or never-started scope after budgets/interruption. Completed collections remain complete when later work hits a global limit.
- Keep the conservative default of 30 requests/minute, one in-flight request, 500 global HTTP attempts and 20 minutes. All portals, metadata, fallback operations and retries share the same scheduler and budgets.
- Expand synthetic topology, permission, metadata, pagination, budget, interruption, aggregation and privacy tests. `--demo` now defaults to a multi-portal scenario; `--demo-scenario single` retains a single-portal demonstration.
- Update API research, troubleshooting, coverage interpretation, example configuration and release documentation. Source build remains optional user-supplied context; key expiration is not inferred or required.

Preserved: GET-only allowlists, header-only credentials, hidden key entry, redirect rejection, bounded retry/backoff with `Retry-After`, partial reports, local analysis, no raw sensitive ticket dumps, no attachment-body downloads, no external AI upload, Python 3.10+, the Windows launcher and portable `.pyz` distribution. Source-only evidence still cannot prove future Cloud migration behavior or approve acceptance.

## 1.0.1 — October 7, 2026

The first reported live scan showed increasing page counts marked `partial`, making normal collection progress look like an error. This release improves the console's explanation of that state.

- Display `collecting` while additional collection pages are queued.
- Distinguish a completed API-visible list from stopped/incomplete and denied/unavailable reads.
- Show page count, API-reported totals when supplied, request attempts and elapsed time.
- Announce inventory, sampled child-record inspection and detail phases, including inventory-budget reservation.
- Print a final coverage summary that separates complete, incomplete and unavailable lists from detail coverage.
- Explain why a completed empty list is limited to the credential, portal and filter, and why access restrictions remain unknown.

The GET allowlist, rate limiting, authentication, scan budgets, sampling defaults, report statuses and migration rules are unchanged. The source-only scan still cannot establish target commitments or confirm a migration outcome.

## 1.0.0 — October 5, 2026

Initial release: bounded read-only inventory, 39 impact checks, seven migration question answers, six offline report outputs, Windows launcher and portable Python application.
