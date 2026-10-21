# One-run multi-portal assessment — updated for 2.1.2

## Normal start

```powershell
.\Run-All-Portals.cmd
```

One host, one primary integration-key prompt, one `EnvironmentCollector`, one global `ReadOnlyClient`, one report family. Every selected portal keeps its own pagination, module diagnostics, field metadata and provenance. The existing breadth-first module/portal scheduling and round-robin list pagination prevent one large portal from consuming every inventory page before others start. A slow request can still delay the shared sequential client; retries and timeouts remain bounded, and the retry message now includes portal/endpoint context.

## Directory permission is separate from module permission

The supplied live logs show `/portals` denied with 403/4002 while explicit portal 1 Requests and field metadata work. This is evidence of a directory-operation gap, not evidence that only portal 1 exists. It is also not enough evidence to prescribe a particular role or prove that all other modules are denied.

The existing directory contract is published by Netskope for its on-premises integration. No alternative universal discovery contract or required minimum role was established from the reviewed public ManageEngine V3/Postman documentation. This release does not add guessed endpoints, scrape sessions or probe integer IDs. Instead it resolves missing topology through authorized directory access or a supplied verified scope, within the original run.

- **D**: read a separate credential through the existing masked/hidden input component. Only `/portals` without `PORTALID` can use it. The transport rejects any attempt to apply it to a module, detail or metadata operation. A failed directory credential does not mark the original integration credential invalid. Both keys' raw and URL-encoded forms enter the in-memory redactor. As with other Python secrets, this is not a guarantee of secure memory erasure; keys are never written to disk.
- **L**: enter all verified IDs together. Same-host portal links are accepted only for local ID extraction with a single `PORTALID` query field. Different origins, userinfo, fragments, token-bearing query fields, numeric ranges, invalid IDs and arbitrary URLs are rejected without requests. Input is not repeated in error messages. This input is **not an API-key prompt**.
- **F**: use a strict non-secret scope file. `portals.example.json` contains fictional values and is never used implicitly. Edit its host and every ID before use. Files are bounded to 1 MiB and admit only the documented schema; there is no import of raw server responses or browser captures.

After a secondary credential is attempted, D is no longer offered; the menu becomes L/F/Enter. A blank answer with no known IDs explicitly finishes with diagnostic reports only.

When there are no selected IDs and no usable authorized discovery/list, no implicit portal is scanned. Reports continue to say assessment not performed/unknown rather than zero records passed.

## Save only with consent

A consented profile stores:

```json
{
  "schema_version": 1,
  "host": "https://helpdesk.example.org",
  "portals": [
    {"id": "7", "name": "EXAMPLE ONLY - IT"},
    {"id": "42", "name": "EXAMPLE ONLY - HR"}
  ]
}
```

These are examples, not suggested IDs for a live environment. Saved files additionally include `saved_at`. Only IDs actually supplied or returned by the directory are used. The profile is bound to scheme, host, port and application context; equivalent explicit/default ports normalize to the same host, different contexts do not. Each run tries live discovery first. A successful live directory supersedes a stale automatic cache. An explicitly supplied file supplements discovery by user request.

A profile stores **no access grants**. Each portal's actual module access is tested again using the primary integration key. Cached/supplied scope is reported as `assisted`, not a complete live directory. To refresh, run with `--no-portal-cache` and enter the new complete verified list; `--save-portals` explicitly authorizes replacing the saved profile. A portal selection truncated by `--max-portals` is not written over a whole-portal profile.

## Single invocation alternatives

```powershell
# Fill portals.json with the actual verified values first.
.\Run-All-Portals.cmd --portal-file .\portals.json --non-interactive

# Keep the verified scope for future host/key runs; no keys are saved.
.\Run-All-Portals.cmd --portal-file .\portals.json --save-portals

# Ask for a separately authorized directory key only after discovery fails.
.\Run-All-Portals.cmd --directory-key

# Existing supported multi-ID selection in one invocation.
$ids = Read-Host "Enter all verified portal IDs, comma-separated"
.\Run-Assessment.cmd --portal-ids $ids
```

The last command deliberately skips directory discovery and covers only the supplied list. `Run-All-Portals.cmd` adds `--all-portals`, so any explicit ID flags become seeds rather than a restriction. `--diagnose` retains its directory-only meaning; it never enters module collection, list/cache recovery, or profile saving. From 2.1.2 it honors explicitly requested `--directory-key` / `--directory-key-env` after incomplete initial discovery. It does not implicitly ask for a secondary credential without one of those flags.

`--non-interactive` suppresses only the recovery menu. Fully unattended use also needs the host and primary key supplied through the existing supported configuration/environment interface. Configure secrets in the environment without entering their literal values in shell history. JSON scope/configuration files do not accept credentials.

## Coverage and budget boundaries

Default global limits remain 30 requests/minute, one in-flight request, 500 HTTP attempts and 20 minutes. Directory reads with either key, compatibility retries, all portals, metadata and details consume those same limits. Waiting for interactive input also does not reset the elapsed global clock. Increase time/attempt budgets explicitly before a large assessment when necessary.

The portal directory is not duplicated per portal. Global Orguser data is collected at most once; primary-key access to that resource remains independent of secondary directory-key privileges. User memberships are not presented as unique people, and overlapping Asset/Computer/CI collections are not summed as unique devices.

Completed lists stay complete after a later global stop. Never-started, denied and unavailable collections retain unknown counts. Successful empty lists are the only valid complete-zero lists. Reports show both the original directory denial and the resolved source of the selected portal list. All seven migration questions keep source evidence distinct from target-Cloud and vendor commitments.

## Offline demonstrations

```powershell
python .\sdp_cloud_readiness.pyz --demo --demo-scenario multi
python .\sdp_cloud_readiness.pyz --demo --demo-scenario recovery
```

`recovery` simulates a denied directory plus a fixture-supplied verified four-portal list. It exercises the real collector, shared virtual clock, permission gaps and consolidated reports. Fixture IDs are explicit synthetic input; the scanner does not infer or enumerate them from a denied response. Demos never contact a customer instance.
