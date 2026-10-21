# Validation record

## Version 2.1.2 — October 14, 2026

The 2.1.1 baseline ran 455 tests successfully (five optional GUI tests skipped).
The updated source and final extracted source ZIP each passed **479 tests**, with
all five GUI tests enabled on Python 3.13.5/Linux/Xvfb. Twenty-four regressions
cover the previously ignored diagnostic credential flag and stale recovery menu.

An isolated portable `.pyz` was also exercised against a real loopback-only HTTP
server through two actual hidden-console prompts in a POSIX terminal. Both-denied
and secondary-success/paginated-directory scenarios used the global 30/minute
limiter and made zero module reads. Single/multi/recovery demos, local output
self-test, help/version, archive integrity and checksums passed. See
[the current release verification](RELEASE-VERIFICATION.md).

No live customer system, real credential, native Windows desktop or separate
Python 3.10 runtime was used. This patch fixes client control-flow/menu defects;
it does not claim that the live build-15240 directory permission denial is fixed.

## Version 2.1.1 — October 14, 2026

Runtime: Python 3.13.5 on Linux; Tcl/Tk with Xvfb for graphical tests.
Baseline 2.1.0 ran 426 tests successfully (five GUI tests skipped on that baseline run).
The updated source suite passed 455 tests with all five GUI tests enabled, including 29 new
context/contract/count-policy regressions. See the shipped [release verification](RELEASE-VERIFICATION.md) for
final extracted-package and independent portable-runner results.

The new failure-pattern tests use synthetic objects and an injected transport/clock:
successful authentication, a Users timeout, an HTTP 200 unknown collection wrapper and a
Projects 403. The unknown wrapper is intentionally rejected. It is not asserted to be the
customer's actual response. Tests verify diagnostic context, fixed type-only JSON evidence,
no source-content/key leakage, correct advice, explicit-scope qualification, independent
per-portal pagination/count policies and a single shared limiter.

Native Windows and a separate Python 3.10 interpreter were unavailable. No customer server
or real API key was used. The previous diagnostic cannot reveal the missing response shape;
new evidence is necessary to establish an installed-build mismatch. Optional count suppression
is supported by official API documentation but is not proof that counts caused the timeout.

## Version 2.1.0 — October 14, 2026

Runtime: **Python 3.13.5 on Linux**, Tcl/Tk with Xvfb for the five opt-in graphical input tests. No customer instance, real key or native Windows desktop was used.

- The recovered 2.0.2 baseline passed 388 tests before changes.
- The updated suite passed **426 tests**, including the original tests and 38 new same-run recovery, scope-file/profile, credential-isolation, budget/privacy and portable-release regressions. Command: `SDP_TEST_GUI=1 xvfb-run -a python -m unittest discover -s tests -q`.
- The final extracted distribution is subjected to the same full suite, including real Linux/Xvfb graphical input tests and Python 3.10 syntax checks. Native Windows and a separate Python 3.10 interpreter were not available.
- Source and isolated portable single-, multi- and denied-directory recovery demonstrations produce consolidated reports. Multi and recovery select four portals, establish scoped read access for three, retain the inaccessible fourth, create 83 coverage rows and answer all seven migration questions. The recovery list is explicit fixture input, never guessed from a denial.
- Three independent real-loopback HTTP checks exercised the isolated `.pyz` without importing neighboring source: secondary directory-only credential, a host-bound full list, and a subsequent run reusing the consented saved profile. Every case assessed all three synthetic portals in one scanner process with the original integration key. Directory denial and a Projects denial remained distinct.
- The directory-key case made 11 GET attempts: one initial denial, one authorized directory read, then nine primary-key module/detail reads. File and saved-profile cases each made 10 GET attempts, one directory denial and nine primary-key reads. No directory-only credential was accepted on a module path or with PORTALID. Both credentials shared the same default 30/minute client scheduler; observed arrival spacing was approximately two seconds. Injected-clock tests also verify 429/Retry-After and global budgets across both credentials and all portals.
- The loopback runs generated eight verified local files plus a sibling report ZIP. ZIP entries matched their corresponding individual files; synthetic credential and private-content canaries were absent from output documents and console logs. This validates controlled scenarios, not customer permissions or all SDP builds.
- The source ZIP includes both Windows launchers, strict example scope/configuration, all source/tests, refreshed synthetic examples, research, changelog and SHA-256 manifests. No customer output, actual credentials, bytecode cache or environment file is included.

A denied directory still requires authorized enumeration or a verified complete list. A saved/supplied list is explicitly qualified as incomplete live-directory coverage. Selected portals that cannot be read, or are not reached before global budgets expire, are not reported as complete-zero inventories. The original integration key keeps its original permissions.


## Version 2.0.2 — October 14, 2026

Validation runtime: **Python 3.13.5 on Linux**, with **Xvfb/Tcl-Tk** for all five opt-in graphical credential tests. No customer ServiceDesk Plus instance or real credentials were used. Native Windows desktop execution and a separate Python 3.10 runtime were not available.

- The original 2.0.1 archive passed all **344 tests** before changes.
- The updated full suite passed **388 tests**, including the previous 344 and **44 new discovery/publication regressions**. The release gate repeats this suite against a fresh extraction of the final source ZIP, with graphical tests enabled.
- New tests exercise an initial invalid query followed by one minimal-pagination retry, no retry after successful first-page traversal, no fallback for denied/unsupported/authentication/TLS/media-type outcomes, global pacing and request-budget accounting, safe preservation of HTTP/SDP codes, and no guessed portal IDs.
- Transport diagnostics are tested with synthetic TLS/DNS failures, HTML/non-JSON responses, redirection, unrecognized content types and secret-bearing exception/header/message canaries. The main transport still permits only GET and header-only credentials. Arbitrary successful HTTP JSON no longer certifies SDP authentication.
- A **real localhost HTTP server** returns an SDP-shaped 404/4007 response. The CLI makes only a GET with the synthetic key in a header, reports the actual error, makes no module calls, writes usable diagnostic reports, and returns an incomplete-scan status. This is not a test against a customer server or certification of `/portals` on any SDP build.
- Filesystem tests simulate deleted and truncated files, blocked HTML writes, denied output directories, disk exhaustion, ZIP failure, symlinks and unrelated files placed in the output folder. The CLI does not print a nonexistent HTML path. The sibling ZIP is built from explicit sanitized report documents and retains HTML when only the individual HTML file is blocked. If all publication methods fail, the console diagnostic remains visible and the run fails.
- `--check-output` is tested to request no credentials, construct no API client, issue no HTTP requests, and produce the real report set with synthetic content. `--diagnose` is tested to stop after directory reads without module inventory. Output preflight failure uses zero HTTP attempts.
- End-to-end source single- and multi-portal demonstrations each generated the six existing reports plus diagnostics/manifest and a verified sibling ZIP. The multi-portal fixture still observes **4 portals / 3 readable / 137 simulated attempts / 83 coverage rows / 7 migration questions**. The single-portal fixture observes **1 portal / 47 simulated attempts / 21 coverage rows / 7 questions**. These remain synthetic, not customer assessments.
- The regenerated bundled example contains only synthetic data. Report checks compare byte lengths and SHA-256 against the manifest, validate every ZIP member and verify the eight individual documents match the archive.
- Release tests check deterministic packaging, explicit manifests, new runtime modules/docs/tests, exclusion of unrelated files, Python 3.10 syntax and standard-library imports, Windows launcher argument/exit forwarding, and the isolated portable version/help/demo paths. Final release verification also runs the portable local-output check and both portal demos from a source-free directory, and verifies inner/outer SHA-256 manifests.

To repeat the complete Linux suite:

```bash
SDP_TEST_GUI=1 xvfb-run -a python -m unittest discover -s tests -q
```

On a Windows desktop with Tcl/Tk, the corresponding suite can be run with the `SDP_TEST_GUI=1` environment variable. Without that opt-in, five graphical tests are skipped; the remaining tests still run.

The reported missing file and one-attempt discovery stop have **not** been reproduced on the user's machine. The old log omitted the underlying response and does not identify a filesystem cause. This release verifies improved diagnostics and publication behavior under controlled faults, not a guessed root cause. Read-back is a point-in-time test and cannot guarantee retention after another process acts. Source evidence does not establish future Cloud migration behavior.

## Version 2.0.1 — October 14, 2026

Validation runtime: **Python 3.13.5 on Linux**, Tcl/Tk 8.6 with **Xvfb** for real graphical input tests. No customer ServiceDesk Plus server or customer credentials were used.

- Recovered and inspected the version 2.0.0 source archive. Its existing **289 tests passed before changes**.
- The updated full suite passed **344 tests** with graphical tests enabled. This includes all 289 existing tests plus 55 credential-input, GUI, CLI and release regressions.
- Five tests exercised actual Tk dialog creation, masked input, user-initiated paste of a synthetic credential, cancellation, widget clearing and secret-safe callback failure. These are real graphical tests on Linux/Xvfb, **not native Windows desktop tests**.
- Verified the default Windows selection through injected platform/UI boundaries: it chooses a masked dialog, preserves environment-key precedence in auto mode, falls back to hidden console only when the GUI is unavailable, and never falls back after cancel or callback failure.
- Input tests cover Ctrl+V/SYN detection, control characters, empty input, interior whitespace, Unicode formatting, allowed boundary cleanup, length bounds, local retries, noninteractive behavior, explicit input mode overrides, hidden-input failure and suppression of secret-bearing exception messages.
- CLI tests establish that rejected/cancelled input constructs no API client, creates no report folder, and that `--check-key-input` needs no host, issues no HTTP requests and writes no reports. The success message explicitly disclaims authentication testing.
- Both source end-to-end synthetic assessments generated all six reports: multi-portal **4 discovered / 3 readable / 137 simulated attempts / 83 coverage rows**; single-portal **1 discovered / 47 simulated attempts / 21 coverage rows**. Both answered seven migration questions.
- Byte comparison with 2.0.0 established that **transport, catalog, collectors, topology, field discovery, migration analysis, progress, reports, sources and synthetic fixtures are unchanged**. Runtime code changes are confined to `cli.py`, the version file, and the new `credentials.py`.
- Packaging tests verify the self-contained portable runner, version/help flags, local-only key check, embedded runner, deterministic archives, exclusion of customer files/secrets/caches, launcher preference and inner/outer checksum manifests.
- Python 3.10 syntax compatibility passes. Native Windows execution and a separate Python 3.10 interpreter were not available; the host/key failure mode on the user's machine is not claimed reproduced from the screenshot alone.

To run the ordinary suite:

```powershell
python -m unittest discover -s tests -v
```

Five graphical tests are opt-in. On a Windows desktop with Tcl/Tk installed:

```powershell
$env:SDP_TEST_GUI = '1'
python -m unittest discover -s tests -v
Remove-Item Env:\SDP_TEST_GUI
```

Linux/Xvfb command used for the complete suite:

```bash
SDP_TEST_GUI=1 xvfb-run -a python -m unittest discover -s tests -q
```

Only synthetic values are used by the graphical tests. A source-only live scan still cannot prove Cloud behavior or migration acceptance. Credential-input improvements do not bypass transport validation or grant API permissions.

## Version 2.0.0 — verification method

The release uses synthetic source fixtures, an injected clock and transport, and local report generation. It does not query the user's ServiceDesk Plus installation or use customer credentials. API research and implementation validation are separate: a documented operation is not assumed to work on every build merely because a fixture passes.

### Completed release results — October 7, 2026

Validation runtime: **Python 3.12.14 on Linux**.

- **289 automated tests passed** using `python3 -m unittest discover -s tests -q`.
- The ordinary two-prompt CLI path was exercised with an injected synthetic transport: it requested the host and hidden key, automatically discovered four portals, and attempted the selected scope without requiring portal IDs.
- The end-to-end multi-portal assessment made **137 simulated HTTP attempts through the shared client**, discovered four portals, established read access to three, and retained the fourth as explicitly inaccessible. The HR Projects authorization failure and Facilities Releases licensing failure remained distinct from each other and from empty results.
- That assessment produced **all six report files**, **83 collection coverage rows**, and **seven migration-question answers**. It retained 58 complete lists and 25 non-complete/unavailable/unread scopes without treating the latter as zero-record successes. The environment-wide Orguser collection appeared once.
- The actual built portable `.pyz` ran `--version`, `--help`, `--list-endpoints`, and both single- and multi-portal demonstrations from an isolated directory under Python's isolated mode, with source-path and SDP environment configuration removed. It reported version **2.0.0** and generated all six files for each scenario.
- Release tests checked deterministic packaging, the explicit source manifest, exclusion of customer reports/secrets/caches, the embedded `.pyz`, and inner/outer SHA-256 manifests. The generated distribution's ZIP integrity and both checksum manifests were also verified directly.
- Python 3.10 syntax compatibility was checked for the shipped Python source. Windows launcher structure and argument/exit-code forwarding were checked; neither a separate Python 3.10 interpreter nor a Windows desktop was available for native runtime validation.
- Report verification covered all requested sections, structured topology and diagnostics, unknown-versus-zero counts, escaping, CSV formula neutralization, and sensitive-data canaries across HTML, Markdown, JSON and CSV. Browser pixel rendering was not part of this validation.

These results validate scanner behavior against the included controlled scenarios. They do not certify the API contract of every installed SDP build or any future Cloud migration outcome.

Run the complete automated suite from the extracted source tree:

```powershell
python -m unittest discover -s tests -v
```

Run end-to-end report generation for both demonstration topologies:

```powershell
python .\sdp_cloud_readiness.py --demo --demo-scenario multi --output-dir .\validation-multi
python .\sdp_cloud_readiness.py --demo --demo-scenario single --output-dir .\validation-single
```

The default `--demo` scenario is multi-portal. All demonstration outputs must be marked synthetic. They exercise report composition and migration analysis without credentials or customer-source requests.

### Required verification coverage

| Area | Verification evidence |
| --- | --- |
| Topology | Single/multiple portals; independent directory pages; safe metadata; explicit targeting; unavailable/denied/malformed discovery; no guessed IDs; partial discovery after interruption/budget |
| Portal context and isolation | Explicit `PORTALID` on scoped reads; no default header on directory discovery; separate portal pagination; a denied operation/portal does not erase other successful scope |
| Global resources and totals | One Orguser collection; no per-portal duplication of global data; portal memberships and overlapping Asset/Computer/CI inventories remain distinct |
| Transport safety | GET only; exact allowlists; no API key in URLs or diagnostics; no followed redirects/response links; validated metadata-only dynamic paths |
| Shared scheduler | Discovery, different portals, retries and metadata share one request clock and attempt/runtime budgets; HTTP 429/SDP 4015 and `Retry-After` remain effective |
| Outcome classification | Successful empty versus denied/unsupported/unavailable/unread; HTTP/SDP codes retained safely; generic 403 does not invent a required role or module state |
| Collection integrity | Large/independent pagination; duplicate/overlap/contradictory page detection; completed lists preserved at later budget exhaustion; interrupted reports remain usable |
| Fields | Module-specific primary/fallback mechanisms, observed template/type selectors, provenance, safe constraints, deduplication, unknown registry completeness and unsupported definition scope |
| Migration analysis | Existing single-portal rule evidence remains equivalent; per-portal findings do not lose scope; field exposure separates observed values from inferred definition risks |
| Reports | Six formats render for synthetic multi-portal evidence; null/blank unknown counts are distinct from zero; gaps and vendor questions retain portal/module context; no raw sensitive source content |
| Compatibility and release | Python 3.10+ syntax/runtime target; ordinary invocation/help/selection; Windows launcher retained; isolated portable `.pyz` run; example configuration accepted; ZIP and checksum verification |

The implementation-focused tests include `test_topology.py`, `test_transport.py`, `test_collect.py`, `test_environment.py`, `test_fields.py`, `test_analyze.py`, `test_report.py`, `test_progress.py`, `test_cli.py`, `test_synthetic.py`, and integration coverage. Reusable scenario configurations and their purpose are documented in [the fixture guide](../tests/fixtures/README.md). Final suite totals and packaging validation are recorded only from the completed release run, not estimated from this matrix.

### Portable artifact check

Copy the built `.pyz` into an otherwise empty temporary directory and run its `--version`, `--help`, `--list-endpoints`, and synthetic multi-portal assessment there. This verifies that it imports its packaged application rather than a neighboring source tree. Compare its generated schema/version and report structure with the source entry point. Verify ZIP integrity and the shipped `SHA256SUMS` after final packaging.

The Windows `.cmd` launcher is portable glue around an installed Python interpreter; a successful Linux/Python run alone is not a Windows desktop execution test. Likewise, a Python 3.12 run does not by itself prove execution on a separate Python 3.10 installation. Record the actual validation runtime and any unavailable platforms in the final release results.

## Version 1.0.1 — October 7, 2026

Validated using Python 3.12.14 on Linux.

- All **90 automated tests passed** using `python3 -m unittest discover -s tests -q`.
- Eight added progress regressions distinguish queued pages from stopped/capped or denied reads, preserve the API-visible qualification on empty and completed lists, separate detail failures and sampled child coverage, and check safe heartbeat/retry output.
- The CLI synthetic demonstration produced all six reports and the new final coverage summary.
- The portable `.pyz` ran `--version`, `--list-endpoints` and `--demo --quiet` from an isolated directory without importing the source tree.
- The portable version reported `1.0.1`, and its synthetic assessment JSON was identical to the version 1.0.0 example: 39 checks and seven question answers.
- The transport, endpoint allowlist, analyzer and rule-source files matched the released version 1.0.0 bytes. The collector changes supply progress events only; existing pagination, budget, authentication, read-only and interruption tests still pass.
- Package ZIP integrity was checked.

The user's supplied live console log established that several inventory endpoints returned records and advanced through pages, while two collections were denied. It did not establish completed scanning, detail coverage or migration outcomes. No connection to that user's server or use of customer credentials was performed during this patch.

## Original version 1.0.0 — October 5, 2026

The initial release passed 82 tests, including real loopback HTTP transport, header-only authentication, redirect rejection, GET-only allowlists, pacing/backoff, budgets, pagination, preserved partial evidence and report privacy. Its single-portal synthetic assessment was the baseline for later regression checks; the current release includes the updated multi-portal example.

## Verification limits

Automated tests use mocks and a local synthetic HTTP server. Pacing tests use a controlled clock; live pacing remains enabled. Runtime validation here used the Python version above; Python 3.10 or newer is required. A Windows desktop was not available to execute the supplied `.cmd` launcher during packaging.

Actual endpoint availability, response shapes, source-build compatibility, permissions and migration outcomes require acceptance against the installed product. The example describes fictional data and is not an assessment of the user's environment.
