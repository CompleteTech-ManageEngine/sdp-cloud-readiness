# Assess instances with separate credentials

Version 2.2.0 supports explicit per-instance collection credentials in one assessment on one ServiceDesk Plus host. An instance's SDAdmin key does not gain access to other instances by changing `PORTALID`. Separate servers still require separate runs.

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

The global assignment authorizes only the reviewed global resource operations, currently Orguser collection. Its portal ID is the administrator-supplied request context required by the published example; it does not turn global records into instance-local records. The [Orguser documentation](https://www.postman.com/servicedeskplus/servicedesk-plus-api/folder/dowvo47/orguser) describes Org admin access in the ESM directory after more than one instance has been created. See [the source review and limitations](../reference/multi-key-authorization.md).

No global credential is inferred from directory access or an instance's SDAdmin role. When multiple selected instances are observed, the global collection runs once with its explicit assignment, even if an instance's collection key fails. Missing/denied/invalid global access remains a coverage gap while independent instance work continues. Observing only one instance does not establish the multi-instance prerequisite, so the existing skip remains. Unsupported global resources are not added automatically.

## Results and failures

All keys share one transport, one rate limiter, and the same attempt/time budgets. A failed key stops its own assignments, including explicitly shared assignments; independent keys continue. Permission denial remains an operation-specific gap. Inventory, details, child resources, and field metadata all use the corresponding instance assignment.

HTML, Markdown and JSON include a credential-scope status table without key values or environment references. Instance rows in `coverage.csv` include `credential_status`. Authentication success is not proof of complete module visibility. Missing, failed, denied and unstarted work remains unknown; only a successful exhausted empty list establishes zero records. Existing people/asset overlap caveats still apply.

Run an offline demonstration with synthetic per-instance and global keys:

```powershell
python .\sdp_cloud_readiness.py --demo --demo-scenario multi_key
```

This demonstration verifies synthetic behavior, not any customer's permissions or live API compatibility.
