# Assess instances with separate credentials

Version 2.2.0 supports explicit per-instance collection credentials in one assessment on one ServiceDesk Plus host. An instance's SDAdmin key does not gain access to other instances by changing `PORTALID`. Separate servers still require separate runs.

## Creating keys on 14.x/15.x ESM

For 14.x/15.x ESM setup, use the instance's integration-key screen where available. The following path was confirmed by an operator on **15.2 build 15240, Enterprise, ESM**; menu labels on other builds may differ:

1. Open the intended instance, then **Admin > Developer Space > Integration Key > New**.
2. Enter a Name, select one or more Roles, choose an expiry date (or “Never expires”), and optionally add a Description. Generate the key and place it only in that instance's local numbered slot.
3. Verify that the new key appears in that instance's Integration Key list.

On that build, **Admin > Developer Space > API** links to documentation; the profile menu has no “Generate API Key”. Older technician-key instructions in the [vendor API introduction](https://www.manageengine.com/products/service-desk/sdpop-v3-api/) describe a different UI.

**Browser session caution:** `?PORTALID=<id>` changes the server-side current portal for the whole browser session, including other tabs. An older tab can still display its previous portal while key generation targets the newly selected instance. Work on one instance at a time, check the instance name in the header immediately before Generate, and check the resulting key in that instance's list before moving on.

### Choosing roles and expiry

Roles are defined separately in each instance. The reported build has no built-in read-only role; do not assume another instance's role list is identical. For broad assessment, an instance **SDAdmin** key is the practical broad-access choice described in setup guidance, not a guarantee of directory or ESM Org access. The scanner needs read visibility for the selected inventories, configuration/metadata, details and child resources; it never needs write operations. There is no verified universal minimum-role recipe across builds and modules. A custom narrower role can grant the relevant read/view permissions, but denied operations remain operation-specific coverage gaps in the report. Successful authentication alone does not establish full visibility. The [vendor authentication documentation](https://www.manageengine.com/products/service-desk/sdpop-v3-api/) explains that API operations depend on the user's role.

Prefer a dedicated assessment key with a short expiry, even though the UI offers “Never expires”. Revoke the keys after the assessment. GET-only scanner behavior does not reduce the privileges of a key outside this tool.

## Local credential file

The default `.env` beside the application supports 20 blank numbered instance slots, with additional slots allowed. Fill each key with its explicit portal ID and set `SDP_HOST`; the loader connects these values to the same credential-binding mechanism described below. See [local environment setup](local-env.md) for exact lookup, scope, process precedence and conflict rules. Never place key values in the JSON assignment file.

### Which `.env` keys are optional?

With numbered instance slots, only `SDP_HOST` and the intended instance ID/key assignments are needed for instance collection. Slots enable multi-key mode automatically. Slot positions are not portal IDs.

| Variable | Purpose and blank behavior in multi-key mode |
| --- | --- |
| `SDP_API_KEY` | **Optional** discovery credential. With slots and no scope override, blank means the numbered slots define scope; no automatic discovery. In default single-key mode this is instead the collection key. |
| `SDP_DIRECTORY_API_KEY` | **Optional** separate directory-only recovery credential. Blank means no separate credential recovery attempt. It never collects instance modules. |
| `SDP_GLOBAL_API_KEY` / `SDP_GLOBAL_PORTAL_ID` | **Optional** explicitly authorized ESM Org credential and verified request context. Leave both blank if unavailable; applicable Orguser collection is reported as a coverage gap. |

A discovery key is an existing integration key authorized to read `GET /api/v3/portals` without a `PORTALID` header. Deliberately copy it into `SDP_API_KEY` if you want discovery (and use `--all-portals` to discover beyond slot scope). The tool never automatically borrows a numbered key. The directory-only recovery variable likewise takes an explicitly authorized existing key; it is not a special key obtained from an ESM Directory key page. Instance access does not prove directory access.

### Leaving instances out

Comment out **both** lines of a slot to exclude its assignment, or leave its portal ID populated and its key blank to retain a known unassigned instance. Remove any equivalent process-environment assignment too: process values take precedence and commenting a file does not unset them.

Known instances supplied by discovery, a verified `--portal-file` inventory, or ID-only slots remain unassessed/unknown when no collection credential is assigned. Commented-out lines are ignored, so the tool cannot list their IDs from comments. With slot-only scope, excluded instances are not individually enumerable; the report retains incomplete/unknown overall directory coverage rather than claiming they were assessed. Supply a verified full inventory to list every omitted instance explicitly. In interactive assignment, choose `S` to skip a known instance.

## Check credentials without collecting

`--diagnose` works in multi-key mode without `SDP_API_KEY`, but **does not test numbered slot keys or their instance bindings**. It only checks directory discovery via GET `/api/v3/portals`, including its existing pagination/retry rules and an explicitly configured directory-only recovery attempt. Without either discovery or directory credentials, authentication is not established and directory coverage remains unknown; no slot key is borrowed. This unavailable-discovery result exits with status 2, not a successful per-slot authentication result. It does not read module inventories or import/save portal lists. Do not combine it with explicit portal-ID/file/save options.

A possible future per-slot authentication check (not implemented) would make at most one read-only request per key using its explicitly assigned instance context and a reviewed existing endpoint, without pagination, retries or fallback credentials. It would report sanitized per-slot authentication/context evidence and permission gaps. One successful request would establish only that operation's access, not complete visibility or universal proof of instance identity.

## Interactive collection

```powershell
.\Run-All-Portals.cmd --multi-key
```

Provide the host. In this mode a configured primary key (`SDP_API_KEY`, or the variable selected by `--api-key-env`) is used for initial directory discovery only. Without one, discovery records a missing-credential gap and offers the existing directory-key or verified-list/file recovery. `--directory-key` requests a hidden directory-only key on discovery failure. That credential is restricted to `GET /api/v3/portals` without `PORTALID`.

Once the portal scope is resolved, each unassigned portal prompts for a collection assignment. Press Enter for a new hidden key, enter an already assigned portal ID to explicitly reuse its key, or enter `S` to leave that portal unassessed. A configured file can preassign some or all portals. Automatic reuse of the discovery key does not occur. Keys are held in memory and never saved in portal profiles.

If discovery is unavailable, obtain actual IDs from an administrator. Use the existing recovery menu or supply `--portal-file` with a verified full list. The credential assignment file alone is not a portal inventory and does not prove that all instances are known. Explicit `--portal-ids` restricts the scan unless `--all-portals` is also used.

## Unattended collection

Copy [credentials.example.json](../../examples/config/credentials.example.json). Replace the fictional host, IDs and environment-variable names. The file accepts only:

```json
{
  "schema_version": 1,
  "host": "https://helpdesk.example.org:8443",
  "portals": [
    {"id": "7", "env": "SDP_IT_KEY"},
    {"id": "42", "env": "SDP_HR_KEY"}
  ],
  "global": {"portal_id": "7", "env": "SDP_ORG_KEY"}
}
```

Populate the named variables through your existing secret mechanism. Do not paste key values into shell commands or JSON. To deliberately share a key, use the same variable reference for each intended portal. Omit `global` if organization-wide collection is not authorized.

```powershell
.\Run-All-Portals.cmd --credential-file .\credentials.json --portal-file .\portals.json --non-interactive
```

`--credential-file` enables multi-key mode. The file is bound to the normalized scheme, host, port and application context; default ports are equivalent, different application paths are not. Duplicate assignments and unsupported fields are rejected. Missing or empty environment variables leave the relevant scope unassigned, with explicit unknown coverage and no fallback. Malformed nonempty keys fail local validation before network collection.

These options are also accepted in the non-secret connection configuration: `multi_key`, `credential_file`, `global_key_env`, and `global_portal_id`. Supply the global assignment either in the credential file or with both `--global-key-env SDP_ORG_KEY --global-portal-id <verified-context-id>`, never both. The existing default single-key mode is unchanged.

## Organization-wide ESM information

The global assignment is optional. Do not assume there is a separate ESM Directory key-creation page or that every instance key qualifies. An administrator must supply a credential with the Org admin access documented for the ESM Directory and a verified request context; if unavailable, leave both global variables blank. The global assignment authorizes only the reviewed global resource operations, currently Orguser collection. Its portal ID is the administrator-supplied request context required by the published example; it does not turn global records into instance-local records. The [Orguser documentation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser) describes Org admin access in the ESM directory after more than one instance has been created. See [the source review and limitations](../reference/multi-key-authorization.md).

No global credential is inferred from directory access or an instance's SDAdmin role. When multiple selected instances are observed, the global collection runs once with its explicit assignment, even if an instance's collection key fails. Missing/denied/invalid global access remains a coverage gap while independent instance work continues. Observing only one instance does not establish the multi-instance prerequisite, so the existing skip remains. Unsupported global resources are not added automatically.

## Results and failures

All keys share one transport, one rate limiter, and the same attempt/time budgets. A failed key stops its own assignments, including explicitly shared assignments; independent keys continue. Permission denial remains an operation-specific gap. Inventory, details, child resources, and field metadata all use the corresponding instance assignment.

HTML, Markdown and JSON include a credential-scope status table without key values or environment references. Instance rows in `coverage.csv` include `credential_status`. Authentication success is not proof of complete module visibility. Missing, failed, denied and unstarted work remains unknown; only a successful exhausted empty list establishes zero records. Existing people/asset overlap caveats still apply.

Run an offline demonstration with synthetic per-instance and global keys:

```powershell
python .\sdp_cloud_readiness.py --demo --demo-scenario multi_key
```

This demonstration verifies synthetic behavior, not any customer's permissions or live API compatibility.
