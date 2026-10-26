# Resume a stopped assessment

Resume is opt-in and works at **instance boundaries**, not individual pages. It preserves completed instance findings without saving source records, ticket text, or credentials. The normal assessment scheduler is unchanged when these options are absent.

## Start with checkpoints

With the same local `.env` setup used for an ordinary assessment:

```powershell
.\Run-All-Portals.cmd --non-interactive --checkpoint --max-requests 2000 --max-minutes 90
```

This mode finishes one instance at a time, including its configured detail, child-resource and metadata work. It gives list pagination the available budget before sampling, instead of reserving a fraction for sampling across all instances. Every request still passes through the existing GET allowlist, one shared rate limiter, retries and global attempt/time limits. Choose a budget large enough to finish at least one instance; repeated small budgets cannot advance past an instance that never finishes.

A verified `checkpoint.json` is written into the new assessment directory after scope resolution, after each instance, and when collection stops normally, reaches a budget, or handles Ctrl+C. The console prints its path. It contains only sanitized report evidence for finished instances, frozen instance scope, the non-secret collection contract and pass history. A finished instance can still have denied operations, unsupported endpoints, configured sampling limits, or other explicit coverage gaps; finished does not mean fully visible or migration-ready.

Press **Ctrl+C once** to stop and write the partial report. Wait for the process to exit before resuming. A hard kill can lose the in-progress instance, but previously committed instances remain in the checkpoint.

## Continue with a larger budget

Use the printed checkpoint path, for example:

```powershell
.\Run-All-Portals.cmd --non-interactive --resume ".\sdp-assessments\assessment-20261026-120000-example\checkpoint.json" --max-requests 4000 --max-minutes 180
```

Each continuation gets fresh global request/time budgets and produces a **new** report directory and checkpoint. The source checkpoint and earlier reports stay intact. Use the newest checkpoint for the next continuation; selecting an older one intentionally repeats work completed since that checkpoint. The run ID and original assessment timestamp persist; pass history records separate start times, HTTP attempt counts and stop reasons.

Completed instance evidence is reused without network reads or reauthentication. The interrupted instance restarts from its first read, replacing its old partial evidence rather than merging potentially overlapping pages. Pending instances follow. Independent instances still run when another key is missing or rejected. Finished gaps are retained by default. Use `--retry-failed` for transient/parser/capped gaps or `--retry-portals 7,42` for explicit instances after authorized permission changes. See [coverage recovery](coverage-recovery.md).

Global Orguser work remains separate and is saved once after a finished global pass. An interrupted global pass restarts; it does not borrow an instance key. Retained evidence records earlier access, not proof that today's credentials still have that access. Reports can combine observations from different times and are not a consistent database snapshot.

## Binding and limits

- Supply the original host, collection options, module selection and business answers again through the same supported configuration mechanisms. The checkpoint rejects a changed host/application context, instance selection, collection plan, credential mode or global request context. Request/time budgets, pacing and timeout may change. `--restart-all` explicitly permits collection-limit and metadata-limit changes by recollecting every instance and global scope; other binding rules remain.
- Credentials are reacquired through the existing `.env`, environment, credential-file or hidden-prompt paths. Key values and key hashes are never stored in the checkpoint. Key rotation is supported with the same explicit scope assignments. Existing host binding, precedence and conflict checks still apply.
- Scope is frozen to the checkpoint's selected instances. Resume does not refresh directory discovery or discover new instances, even when the launcher supplies `--all-portals`. A new assessment is needed for a changed inventory.
- `--diagnose`, `--demo`, `--check-output` and `--check-key-input` cannot be combined with checkpoint/resume. Reports created without `--checkpoint` cannot be retroactively resumed; `assessment.json` is not a checkpoint. An already running process cannot gain checkpoint support or a larger budget.
- Checkpoints use bounded JSON, schema/tool-version checks, a SHA-256 integrity check and atomic write/read-back verification. The checksum detects corruption, not malicious edits; treat checkpoints as local assessment artifacts and do not edit them.
- A `.lock` file prevents concurrent use of the same checkpoint. After a hard kill it may remain. Verify that no process is using that checkpoint before manually removing its `.lock` file; the scanner never steals a lock automatically.

Keep checkpoints as private as the assessment reports: they contain internal IDs, configuration metadata, findings and coverage, though no raw source records or credentials. Back up the whole assessment directory if durable progress is important. Checkpoint files are not included in the published report ZIP.
