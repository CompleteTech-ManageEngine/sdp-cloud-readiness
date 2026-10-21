# Release verification — ServiceDesk Plus Cloud Readiness 2.1.2

Date: October 14, 2026.
Runtime: Python 3.13.5 on Linux; Xvfb/Tcl-Tk for the opt-in graphical tests.

## Baseline and full suite

- Recovered and tested the supplied 2.1.1 source ZIP: 455 tests ran successfully; five opt-in graphical tests were skipped in the baseline invocation.
- Updated working source: 479 tests passed with all five graphical tests enabled.
- Final extracted distribution: 479 tests passed with all five graphical tests enabled.
- Command: `SDP_TEST_GUI=1 xvfb-run -a python -m unittest discover -s tests -q`.
- The 24 new regressions cover the precise diagnostic-key flag failure, library diagnostic boundary, no list/cache/save recovery in diagnostic mode, paginated directory success, separate auth outcomes, input cancellation/rejection, shared rate/Retry-After/time/attempt budgets, stale-D menu correction, blank-input behavior and one-run verified-list recovery after both directory credentials are denied.

## Independent portable tests

The built `.pyz` was copied into an isolated temporary directory without the source tree and invoked with Python `-I`.

Two real HTTP scenarios used only a local test server bound to `127.0.0.1`. The application ran in a POSIX pseudo-terminal so both real hidden-console input prompts could be driven with synthetic credentials. No mock was substituted for the credential acquisition, HTTP client, diagnostic mode, report writer or portable imports in these checks.

1. **Both credentials denied:** the exact diagnostic-key flag path requested two hidden inputs, made two GETs with no PORTALID header, retained both 403/4002 diagnostics, performed zero module reads and exited 2. Authentication of the initial key remained unverified, not falsely validated by a denial.
2. **Secondary directory succeeds:** the initial read was denied; the second key retrieved a three-portal list over two directory pages. Total: three GETs, two hidden inputs, zero module reads, exit 0. Directory visibility did not certify module access.

Both runs used the unchanged shared default 30/minute limiter; observed request-start spacing was at least 2.000 seconds. Each published verified individual reports and a sibling ZIP. ZIP integrity and equality of its documents with the individual report files passed. Neither synthetic credential appeared in console output, reports or the report ZIP.

Portable `--version`, `--help`, `--list-endpoints` and local `--check-output` passed. All three synthetic assessment demonstrations passed: single (one portal, 21 coverage rows), multi (four portals, 83 rows) and denied-directory/list recovery (four portals, 83 rows). Each answered all seven migration questions. These demonstrations use fixtures and a virtual scheduler, not a customer system.

The source ZIP has an inner SHA-256 manifest. The embedded portable runner equals the standalone `.pyz`. Outer release hashes and ZIP integrity were checked. Python 3.10 syntax compatibility is part of the suite.

## Scope and limits

- No customer ServiceDesk Plus server, real key, cookie, account or connected service was accessed.
- Native Windows execution and a separate Python 3.10 runtime were unavailable. The real two-prompt tests used Linux/POSIX; the five graphical tests used Linux/Xvfb, not a Windows desktop.
- No API endpoint, transport authentication rule, module collector, field-metadata strategy, migration rule or rate allowance was broadened by this patch.
- The build-15240 directory denial is not repaired or fully explained. The user's ordinary assessment already attempted both entered credentials; its two-denial result remains valid evidence. The diagnostic-mode bug explains only the earlier one-attempt command.
- The supplied second credential's identity, equality to the initial key and OrgAdmin membership are not known from the logs. No specific new role or source upgrade is prescribed.
- A complete verified portal list still permits one consolidated assessment of the supplied scope. It does not establish discovery of every current portal. No IDs are guessed and no permissions bypassed.
- Tests validate controlled scenarios, not universal live API support or future Cloud migration acceptance. Report-file verification is point-in-time.
