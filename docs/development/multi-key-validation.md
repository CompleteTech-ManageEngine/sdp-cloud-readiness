# Version 2.2.0 validation

Validation date: 2026-10-21. Platform: Windows, Python 3.14. All API responses were synthetic; no customer credentials or live customer endpoints were used.

## Checks

- `python -X utf8 -m unittest discover -s tests -v`: 505 tests run; 499 passed, six skipped; no failures (16.578 seconds).
- Focused credential suite: 25 tests passed. Covers explicit sharing, distinct keys, missing assignments, malformed configuration, canonical IDs, wrong-host rejection, shared budgets, redaction, global context, isolated failures during list/detail/metadata reads, preservation of earlier permission failures, and unattended CLI reports.
- Source and portable version commands report 2.2.0.
- The source `Run-Assessment.cmd --version` launcher reports 2.2.0.
- The standard source `--demo` and packaged `Run-All-Portals.cmd --demo --demo-scenario multi_key` both completed, publishing reports with file/ZIP readback verification. The packaged launcher exercised the adjacent portable app.
- Source `--demo --demo-scenario multi_key` completed: four selected synthetic portals, three with successful scoped reads, one inaccessible portal, and explicit module gaps. Global Orguser collection completed once. This is deliberately partial source visibility, not an all-clear report.
- Release suite verifies deterministic archives, inner/outer SHA-256 manifests, exclusion of customer reports/secrets/caches, packaged configuration/docs, standalone execution, and the multi-key portable demonstration.

## Boundaries

Five graphical credential-input tests are opt-in and are skipped unless `SDP_TEST_GUI=1`; existing hidden-input integration is covered with mocks. One symlink test is skipped when Windows symlink creation is unavailable.

The historical Windows unavailable-discovery failure documented in CONTRIBUTING.md is addressed by preserving the discovery result at recovery-menu EOF. Intentional interruption behavior retains its existing tests.

No live ESM compatibility, customer permission grants, migration acceptance, deployment or merge is asserted. The PR records available hosted CI separately from this local evidence.
