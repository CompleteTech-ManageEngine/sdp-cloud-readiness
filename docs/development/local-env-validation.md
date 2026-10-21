# Issue #5: local environment validation

Validation platform: Windows, Python standard-library runtime, 2026-10-21.

## Commands

```powershell
python -X utf8 -m unittest discover -s tests -q
python -X utf8 tools/build_release.py --output-dir dist/issue-5
python dist/issue-5/sdp_cloud_readiness.pyz --version
git diff --check
```

The suite ran 529 tests successfully, with six skips (five opt-in graphical credential tests and one unavailable-symlink test). All 23 local-environment tests and all 14 release tests passed. Both Windows command launchers were executed. The built portable application returned version `2.2.0`. Generated binaries and local environment files remain ignored.

## Synthetic routing evidence

`tests/test_local_env.py::LocalEnvTests.test_two_slots_route_correctly_and_publish_without_secrets` runs the normal CLI with a temporary `.env`, a synthetic HTTP transport, and real report publication. It supplies these explicit assignments:

| Slot | Portal ID | Result |
| --- | --- | --- |
| 03 | 1 | Inventory requests use the first synthetic key |
| 19 | 2 | Inventory requests use the second synthetic key |
| 20 | 3 | Empty key remains `CREDENTIAL_MISSING`; no request is sent for this portal |
| 02 | Blank | Ignored |

The test asserts the actual request headers, the three selected portal IDs in one consolidated assessment, and absence of both keys from console output, report files and every member of the report ZIP. Slot numbers do not select portal IDs. The separately scoped directory/global test asserts that the directory key accesses only `/portals` without a portal header, the global key accesses `/orgusers` with its explicit context, and the instance key accesses its own portal inventory. The diagnostic-mode test confirms that populated slots do not cause module reads during `--diagnose`.

Other checks cover exact default source/portable lookup from another working directory, first-run blank creation, preserving existing files, explicit path and opt-out, process precedence including empty values, all 20 default slots plus slot 21, ID-only gaps, malformed input and byte/line/value bounds, literal shell expressions, host/context mismatch, duplicate and conflicting assignments, and redacted representations.

Release tests create private `.env`, `.env.customer` and `credentials.env` canaries, including under example directories, then assert their exclusion from the source distribution and portable application. A filled `.env.example` fails packaging. Existing reproducibility and checksum checks also pass.

All HTTP evidence is synthetic. No customer installation, real credentials, vendor rate allowance, or Cloud migration behavior was tested. Concurrency and request-rate policies are unchanged.
