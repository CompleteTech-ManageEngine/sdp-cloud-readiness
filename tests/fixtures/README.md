# Synthetic API fixture configurations

These JSON files configure the deterministic in-memory `SyntheticServer` in `sdp_audit/synthetic.py`. They contain no customer records or credentials. The common generator supplies fictional source records, repeated IDs across portals, and deliberately sensitive-looking canary strings for privacy tests.

`run_synthetic()` runs the actual `ReadOnlyClient`, shared virtual request clock, topology discovery, `EnvironmentCollector`, field strategies and detail/subresource collectors. It does not construct pre-aggregated report data and opens no network connection. JSON specifications can be loaded directly:

```python
import json
from pathlib import Path
from sdp_audit.synthetic import run_synthetic

config = json.loads(Path("tests/fixtures/multi.json").read_text(encoding="utf-8"))
environment, server = run_synthetic(config)
```

The portable `.pyz` does not depend on these test files: built-in scenarios use the same configuration generator. `run_synthetic("single")`, `run_synthetic("multi")` and `run_synthetic("recovery")` provide the CLI demonstrations. The original `demo.py` is retained for equivalent single-portal rule regressions.

| Fixture | Main evidence |
| --- | --- |
| `single.json` | One portal, successful empty Projects, metadata and migration risk signals |
| `recovery.json` | Denied directory plus explicit synthetic full-list input; all four portals scheduled in the same collector |
| `multi.json` | IT, HR, Facilities and inaccessible Security; reused local IDs; global Orgusers collected once |
| `mixed_permissions.json` | Denied HR Projects; explicit Security portal access denial; other work continues |
| `module_unavailable.json` | SDP 7001/license unavailability remains distinct from zero rows or ordinary forbidden |
| `module_not_enabled.json` | Explicit disabled-module message with HTTP 403 |
| `unsupported_metadata.json` | Unsupported definition endpoints, retained observed UDF names and unknown registry coverage |
| `udf_primary.json` | Request-template and current Asset/CI metadata; fixture supports exact Space-module UDF selectors |
| `udf_fallback.json` | Modern Asset metadata fails; observed product type selects legacy metadata; Change record metadata fallback |
| `budget_exhaustion.json` | Shared attempt cap stops at eight attempts; earlier completed lists and never-started scope remain distinct |
| `time_budget.json` | Virtual global runtime exhausts after completed work |
| `rate_limiting.json` | A 429/4015 response on discovery has `Retry-After: 7`; the retry consumes the same scheduler/budget |
| `large_pagination.json` | 1,207 IT Requests and 613 HR Requests paginate independently |
| `portal_discovery_unavailable.json` | One unsupported global discovery response; no implicit/default portal reads |
| `portal_context_required.json` | Explicit required-PORTALID response evidence remains a context diagnostic |
| `asset_catalog_gap.json` | Unsafe/unusable type API name is not followed and prevents a false schema-completeness claim |
| `empty_directory.json` | A successful complete empty directory is distinct from failed discovery |
| `interrupted.json` | Ctrl+C is simulated during collection; reports remain usable |

The multi-portal fixture includes IT CI-type metadata through the observed `/cmdb_demo/_metadata` route, while other portals lack an exposed type API name. Asset metadata includes a discovered custom type, and HR exercises the legacy metadata fallback. Unattached administrator field registries remain unproven even after successful form/type reads.

The common fixture inserts canaries in ticket subjects/descriptions, notes, addresses, filenames, SQL/script text, field defaults/options, topology owners/tokens, and arbitrary error text. Assertions scan all six output formats and the assessment object to ensure those raw values are absent. Only safe metadata and measurements should survive.

`server.calls` records method, API-relative path, portal ID, non-secret selectors, virtual time and header/body-presence booleans. It deliberately excludes credential header values and raw responses. Tests can append a scripted response with `server.queue_response()` or edit `server.datasets[portal_id][collection]`; those changes stay local to that server instance.
