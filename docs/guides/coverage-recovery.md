# Resolving collection coverage gaps

Collection completion and source visibility are separate. A finished checkpoint may retain row caps, unsupported APIs, failed reads or successful samples that do not cover the full population. These outcomes must not become zero-record or complete-visibility claims.

## Retry a finished instance

Ordinary `--resume` reuses finished instances. To explicitly retry instances with network/server failures, parser failures, rate limits or row caps:

```powershell
.\Run-All-Portals.cmd --non-interactive --resume .\sdp-assessments\previous-run\checkpoint.json --retry-failed --max-requests 4000 --max-minutes 180
```

`--retry-failed` checks retained collection outcomes and metadata diagnostics. It does not automatically retry permanent permission or unsupported-operation outcomes. It restarts each selected instance, including its other collections, because checkpoints do not retain source rows for individual-page continuation. All reads still use the current explicit credentials.

After an administrator changes permissions, or to choose particular instances, use verified IDs from your own checkpoint (these examples are fictional):

```powershell
.\Run-All-Portals.cmd --non-interactive --resume .\sdp-assessments\previous-run\checkpoint.json --retry-portals 7,42 --max-requests 4000 --max-minutes 180
```

Earlier committed evidence remains in the next checkpoint until its replacement finishes; pending retries are recorded and continue on a later resume. Old report directories are never overwritten. Pass history records the selected retries and previous collection outcomes. The report for an interrupted retry shows the current partial observations, while the checkpoint retains the earlier committed evidence marked pending.

## Row caps versus request budgets

`RECORD_LIMIT_REACHED` is the per-collection row cap (5,000 by default), even when HTTP attempts remain. `--full-inventory` removes that row cap; it does not remove request/time limits or detail/metadata sampling. A bigger HTTP budget alone does not lift row caps.

Changing collection limits invalidates ordinary checkpoint reuse. To deliberately re-collect the entire frozen scope with new limits:

```powershell
.\Run-All-Portals.cmd --non-interactive --resume .\sdp-assessments\previous-run\checkpoint.json --restart-all --full-inventory --max-requests 6000 --max-minutes 240
```

`--restart-all` permits collection-option and metadata-limit changes, replaces all instance/global evidence, and leaves previous reports intact. Host, TLS policy, credential mode/global context, selected scope, module plan and analysis answers remain bound. It cannot be combined with selective retry flags. Start a new assessment to change those other boundaries.

## Expected child sampling

`SAMPLE_COMPLETE` means all configured sampled parent reads finished. It does not mean all source parents were inspected. The report shows completed/selected parent counts separately from full-list coverage. Zero sampled notes/tasks means no children were seen for those parents; other parents remain unknown. `--subresource-parents` controls sampled parents, and `--max-child-records` caps each parent's child list. Changes to these options require a new assessment or explicit `--restart-all` on resume.

## Network and server failures

For User timeouts, inspect the sanitized transport category and retained page count. `--timeout 90`, a smaller `--page-size`, or `--count-policy never` may help slow reads; these are troubleshooting choices, not proof of the cause. Page-size/count-policy changes require a new assessment or `--restart-all`. A timeout retry preserves successful earlier pages within a pass. `--retry-failed` starts the affected instance again on a new pass.

Computer reads first use `/asset_computers`. Only an unsupported response permits the documented `/asset_workstations` list fallback, then the legacy `/workstations` fallback. Both initial and subsequent diagnostics remain visible. The modern workstation fallback is list-only; it does not establish full computer detail visibility. A 403 or 500 does not trigger endpoint guessing. If documented fallbacks still fail, give the administrator/vendor the installed build, operation path, HTTP status, SDP codes and safe transport category from `diagnostics.json`. Do not send keys or raw bodies. A server-side failure may require a product fix; increasing permissions or the budget is not a demonstrated remedy.

## Project permissions

An administrator should confirm the key was generated in the intended instance, verify its assigned roles and Project read visibility against that build, and distinguish module access from directory or organization-wide access. Successful reads of other modules establish neither Project permission nor complete Project visibility. A generic 403 does not identify a specific required role. The scanner never changes permissions; after an authorized change, explicitly retry that instance with `--retry-portals`.

## Optional directory and organization scopes

Missing directory credentials do not invalidate successful reads using explicit instance assignments. They leave whole-directory completeness unverified. Missing Orguser credentials leave optional organization-user coverage unknown. Neither scope borrows an instance key automatically. Orguser access needs an explicit authorized ESM Org credential and verified global context; adding that context changes the resume contract and requires a new assessment. A checkpoint with `global_done=false` and no global assignment cannot be repaired by giving it more attempts. See [credential setup](multiple-credentials.md).

## Metadata parsing

Asset-module collection accepts the current `asset_modules` list and the earlier `all_product_types` list on the same reviewed endpoint. Conflicting simultaneous wrappers and unknown wrappers remain errors. Successfully observed API names can support the existing bounded type-specific metadata discovery.

Change metadata diagnostics retain a fixed structural reason and value-free response shape. On the inspected build, `roles.fields` used numeric role IDs for lookup definitions. These are now accepted only inside Change role metadata, with matching role IDs and lookup types; free-text role names never become internal identifiers. Numeric keys elsewhere remain invalid. Do not infer an empty field registry or publish source values when a different contract remains unverified.
