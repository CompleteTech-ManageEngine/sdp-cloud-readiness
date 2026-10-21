# Contributing

Use Python 3.10 or newer. The runtime and tests use the standard library; no package installation is required. Run commands from the repository root.

## Local checks

```powershell
python -X utf8 -m unittest discover -s tests -v
python .\sdp_cloud_readiness.py --version
python .\sdp_cloud_readiness.py --demo --output-dir .\sdp-assessments
```

UTF-8 mode avoids platform-default text decoding differences on Windows. Five graphical credential tests require a desktop and explicit `SDP_TEST_GUI=1`; platform-dependent skips are reported by unittest.

The initial Windows import check ran 479 tests in UTF-8 mode: 472 passed, six skipped, and `test_unavailable_discovery_cli_writes_unknown_topology_without_default` failed because it received `INTERRUPTED` instead of `PORTAL_DISCOVERY_UNAVAILABLE`. This is a recorded baseline limitation, not a passing test result. Historical Linux evidence is in [validation](docs/development/validation.md).

Version 2.2.0 resolves that recovery-input EOF failure. The expanded suite and its exact local results are recorded in [multi-key validation](docs/development/multi-key-validation.md).

## Release build

```powershell
python .\tools\build_release.py --output-dir .\dist
python .\dist\sdp_cloud_readiness.pyz --version
```

The builder uses an explicit source/documentation/example manifest. It produces reproducible ZIPs and SHA-256 manifests, and includes the portable app at the extracted release root. Build output belongs in ignored `dist/`; do not commit generated binaries or checksums. Release tests verify self-contained execution, archive contents, checksums, reproducibility, and exclusion of private files.

## Project conventions

- Keep runtime code under `sdp_audit/` and synthetic tests under `tests/`.
- Put user instructions in `docs/guides/`, API contracts and research in `docs/reference/`, verification evidence in `docs/development/`, and detailed version notes in `docs/releases/`.
- Keep root launchers and Python entry points compatible with both source checkouts and extracted releases.
- Never commit real API keys, local configuration, customer reports, or saved portal profiles. Configuration templates and committed report examples must remain synthetic.
- Preserve the read-only endpoint allowlist, shared request budgets, credential redaction, and explicit incomplete-coverage reporting.
- Distinguish local synthetic validation from live installation behavior. Record the exact checks run and any failures or skips.
