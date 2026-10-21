# Documentation

Run commands from the repository root or the root of an extracted release, rather than from a documentation subdirectory. Portable `.pyz` examples assume an extracted release; in a source checkout use `sdp_cloud_readiness.py`, or build first and use `dist/sdp_cloud_readiness.pyz`.

## User guides

- [Full usage guide](guides/usage.md)
- [Separate credentials per instance](guides/multiple-credentials.md)
- [Default local environment file](guides/local-env.md)
- [All portals in one run](guides/all-portals.md)
- [Discovery and output troubleshooting](guides/troubleshooting.md)
- [Windows API-key input](guides/windows-key-input.md)
- [Configuration examples](../examples/config/README.md)

## Technical reference

- [API catalog](reference/api-catalog.md)
- [Topology and authorization research](reference/topology.md)
- [Field discovery research](reference/fields.md)
- [Diagnostics and coverage](reference/diagnostics-and-coverage.md)

## Development and releases

- [Contributing and local checks](../CONTRIBUTING.md)
- [Historical validation evidence](development/validation.md)
- [Release verification](development/release-verification.md)
- [Changelog](../CHANGELOG.md)
- [2.1.1 diagnostic context and count policy](releases/2.1.1.md)
- [2.1.2 directory credential recovery](releases/2.1.2.md)

- [2.2.0 per-instance credentials](releases/2.2.0.md)
- [Multi-key authorization source review](reference/multi-key-authorization.md)
- [2.2.0 validation evidence](development/multi-key-validation.md)
- [Local environment validation](development/local-env-validation.md)
