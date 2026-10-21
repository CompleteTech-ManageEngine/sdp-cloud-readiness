# Discovery and report-output troubleshooting — 2.0.2

The two issues have separate evidence paths. A failed portal-directory request
explains why no modules were assessed. A missing local report needs filesystem
verification. The earlier console text did not establish the underlying server
error or why a file could not be found. Do not infer either cause from that text.

## 1. Verify which program is running

Extract 2.0.2 to a fresh folder rather than mixing source files from several
versions. From the folder containing the portable application:

```powershell
python .\sdp_cloud_readiness.pyz --version
```

Expected: `2.0.2`. The Windows launcher prefers the self-contained portable
application. Replacing source alone does not replace an older neighboring
`.pyz`; use `python .\sdp_cloud_readiness.py` to intentionally run source.

## 2. Test local output without a host or key

```powershell
python .\sdp_cloud_readiness.pyz --check-output --output-dir "E:\sdp-reports"
```

The directory is an example; choose a short, writable path on your own machine.
The application creates a fresh `output-check-...` directory beneath that parent.
It requests no credentials, constructs no API client, and issues no HTTP calls.
It renders clearly labeled synthetic documents using the actual report writers.

A successful run prints **Open verified HTML** and **Verified report ZIP**.
The directory contains the original six reports plus `diagnostics.json` and
`report-manifest.json`. Its sibling ZIP contains these same eight documents.
Copy only the **actual path printed by your run** when checking a file:

```powershell
# Substitute the exact path printed by your run, not this illustrative value.
$report = 'E:\sdp-reports\output-check-YYYYMMDD-HHMMSS-xxxxxx\report.html'
Test-Path -LiteralPath $report
Get-Item -LiteralPath $report | Select-Object FullName, Length, LastWriteTime
```

The publication path checks are:

1. Create the fresh run directory and verify a temporary write/flush/rename/read.
2. Render only approved, sanitized report documents in memory.
3. Write each file atomically, reopen it, and compare byte length and SHA-256.
4. Verify the set after all individual writes. Write a manifest with per-file
   verification and safe numeric filesystem errors.
5. Build the sibling ZIP from explicit rendered documents, not a directory sweep.
   Check its structure and content; write and reopen the ZIP.
6. Recheck file paths before the console announces verified locations.

If an individual HTML write fails, other formats and the ZIP are still attempted.
The ZIP can contain HTML even when the individual HTML file could not be written.
This is a recovery copy, not a bypass of security policy. The same filesystem or
policy can deny both forms. The tool never claims that a later deletion cannot
occur after successful read-back.

Filesystem diagnostics use fixed classifications such as `ACCESS_DENIED`,
`FILE_NOT_FOUND`, `DISK_FULL`, `PATH_TOO_LONG` or `OUTPUT_CONTENT_MISMATCH`, with
numeric `errno`/`winerror` when available. Unknown conditions stay
`FILESYSTEM_ERROR`. Underlying exception strings and arbitrary filenames are not
printed. A failed publication returns exit 1 and does not manufacture a success
path. Fix the local failure before collecting a large inventory.

## 3. Diagnose the actual portal-directory response

```powershell
python .\sdp_cloud_readiness.pyz --diagnose --output-dir "E:\sdp-reports"
```

This uses the ordinary source URL and hidden/masked key prompts. It reads only
the portal directory, following its pages if available. It does not request
Requests, Projects, Assets, users, metadata, or other module inventories. The
usual global attempt/time limits and 30/minute pacing apply to every attempt,
including retry/backoff. It writes diagnostic reports with a discovery-only note.

On failure, a **Portal-discovery diagnostics (sanitized)** block appears in the
console before report rendering, even with `--quiet`. It identifies the allowlisted
GET path, absent or explicit portal context, HTTP status, SDP codes, recognized
safe response phrases, response format, and supported transport-failure evidence.
It never prints raw responses, key values, redirect destinations, or tracebacks.
Unrecognized server message text is omitted while numeric codes are retained.

The following is a **synthetic illustration**, not an observation from your server:

```text
Portal-discovery diagnostics (sanitized):
  GET /api/v3/portals | PORTALID: none (directory discovery)
  Result: ENDPOINT_UNSUPPORTED | HTTP: 404 | SDP codes: 4007
  Response: json_object; cause: api_compatibility
  ...
  No portal module inventories were collected. Migration readiness is UNKNOWN, not passed.
```

The classification depends on the response actually received. The same generic
`PORTAL_DISCOVERY_UNAVAILABLE` stop in an older version could have resulted from
several different conditions:

| Evidence | Interpretation and next step |
| --- | --- |
| TLS certificate verification failure, no HTTP response | Check hostname, dates and trusted certificate chain. Obtain a trusted PEM CA bundle from the administrator; use `--ca-file`. Do not default to disabling TLS verification. |
| DNS, refused connection, timeout, or reset | Check source host/port, DNS, routing and relevant network/proxy access. No SDP authentication receipt is established by that failed connection. |
| Blocked redirect | Supply the final on-premises API base URL. Redirects are intentionally not followed and `Location` is not printed. |
| HTML/non-JSON instead of a JSON object | A gateway, sign-in page, wrong path, or different response format must be investigated. Response shape alone does not prove which component returned it. |
| HTTP 401 / SDP 4022 | Verify integration-key validity and the account. HTTP 401 without SDP evidence can be generated upstream; it does not identify the rejecting component. |
| HTTP 403 / SDP 4002 | Directory read was denied. Do not infer a named role requirement from generic 403. Verify actual read scope; module access and directory access are separate. |
| HTTP 404 / SDP 4007 | Endpoint/path/resource is not exposed by this response. Confirm the source base path and installed API contract; do not assume zero portals. |
| `INVALID_QUERY` | The initial query can receive one same-endpoint minimal-pagination retry. Persistent failure remains a compatibility/query diagnostic, not an authorization finding. |
| SDP 7001 or explicit module/license message | Record the license/module limitation supported by the actual response, separately from permissions. |
| HTTP 200 with unexpected JSON schema | The endpoint did not return a usable portal list. Success-looking JSON alone is not proof of authentication or complete discovery. |
| Successful complete empty directory | No portals were returned in this key's visible scope. No module data was collected; it does not establish that the organization has no portals. |

Official status-code meanings are in the [ManageEngine on-premises V3 guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/common-error-code.html).
The success envelope and minimal pagination are illustrated in its
[pagination guide](https://www.manageengine.com/products/service-desk/sdpop-v3-api/getting-started/pagination.html).

## 4. Directory compatibility, without guessing portal IDs

The implemented GET `/api/v3/portals` on-premises contract is published by
[Netskope, the maintainer of its ServiceDesk Plus integration](https://docs.netskope.com/en/manage-engine-service-desk-plus-plugin-for-ticket-orchestrator).
A native public ManageEngine/Postman equivalent and a universal minimum build
were not established in this review. This does not prove that the route is absent
on your build; the diagnostic run provides the actual evidence.

For initial `INVALID_QUERY` only, the scanner can drop optional sort parameters
and retry the same read with `row_count`/`start_index`, as documented by the native
pagination guide. This happens once at the beginning, uses the same limiter and
attempt budget, and preserves the first diagnostic. It is not used for denial,
authentication, unavailable paths, TLS, HTTP 406/415, or after a successful page.
An earlier recovered error remains visible but is labeled as a recoverable attempt.

When discovery is genuinely unsupported or denied, use portal IDs verified by
your administrator or supported in-product API documentation. `--portal-id`
bypasses enumeration; it does not bypass module permissions. Do not guess an ID
or test a numeric range. Explicit targeting cannot certify all-portal coverage.
Use the ordinary scan command with the verified override, not `--diagnose`.

## 5. Resume the normal assessment

```powershell
python .\sdp_cloud_readiness.pyz --output-dir "E:\sdp-reports"
```

No-portal runs say **ASSESSMENT NOT PERFORMED** and include the high-severity
`UNKNOWN` topology finding in the acceptance register. Directory-only runs also
state that no module inventory was requested. Existing partial evidence is
retained when discovery, collection, budgets, or interruption leave gaps.

Useful support material is the console's sanitized diagnostic block and the
small `diagnostics.json` file. The verification manifest can help diagnose a
local publication failure. Do not send the API key, raw response bodies, arbitrary
headers, full ticket exports, or the clipboard. This patch was tested with
synthetic data and localhost only; it did not contact the customer's server and
was not executed on a native Windows desktop.


## Diagnostic comparison correction in 2.1.2

The combination `--diagnose --directory-key` now honors the requested second
credential while querying only the directory. Version 2.1.1 incorrectly skipped
that option. The ordinary assessment path already performed it. After the one
secondary attempt, D is removed from the recovery menu. See
[detailed boundaries](../releases/2.1.2.md). A completed two-denial
ordinary run does not need to be repeated to establish the same result.

## Different keys for different instances

An instance SDAdmin key cannot gain access to other instances through a `PORTALID` header. Use [per-instance credential setup](multiple-credentials.md). `CREDENTIAL_MISSING` means no key was assigned, not an empty instance. `AUTHENTICATION_FAILED` in multi-key mode stops the failed key's assignments while other keys continue. Inspect each module's coverage even when authentication succeeds.

Missing or denied Orguser access is separate from portal discovery and instance access. Assign an explicitly authorized global key and verified request context, or retain that global coverage gap. A directory-only key cannot be used for Orguser collection.
