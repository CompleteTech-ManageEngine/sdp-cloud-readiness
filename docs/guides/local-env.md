# Local `.env` setup

The source entry point and portable `.pyz` load a local `.env` automatically. The first normal assessment creates a blank file if it is absent. Existing files are never overwritten. You can also copy the repository's [blank example](../../.env.example) to `.env` before starting.

## Location and launchers

- Source: `.env` in the application root, beside `sdp_cloud_readiness.py`.
- Portable: `.env` beside the `.pyz` archive, even when launched from another working directory.
- Both Windows launchers use the same Python loader. They never execute `.env` as a batch file.
- `--env-file <path>` loads exactly that file. Relative paths use the current working directory. A missing explicit file is an error and is not created.
- `--no-env` disables local file loading and creation. Process environment variables still work.
- No parent-directory search is performed. Help, version, endpoint listing, demo and output self-test do not load or create `.env`. The local key-input check loads an existing file but does not create one.

If the application directory is read-only, supply a writable local file with `--env-file`, or use process environment variables with `--no-env`.

## Fill one file

Set `SDP_HOST` to the exact on-premises origin, including port and application context if applicable. Replace the fictional IDs below with administrator-verified portal IDs, then fill the key values locally:

```dotenv
SDP_HOST=https://helpdesk.example.org:8443/servicedesk
SDP_INSTANCE_01_PORTAL_ID=42
SDP_INSTANCE_01_API_KEY=
SDP_INSTANCE_02_PORTAL_ID=807
SDP_INSTANCE_02_API_KEY=
```

Run `python .\sdp_cloud_readiness.py --non-interactive`, or use a Windows launcher. With numbered assignments and no explicit scope, the scanner assesses those supplied IDs in one consolidated report. `Run-All-Portals.cmd` or `--all-portals` also discovers accessible portals; supplied IDs are seeds if discovery is unavailable. Other discovered portals without assigned keys remain coverage gaps in noninteractive mode. Use `--portal-id`, `--portal-ids`, or `--portal-file` to choose another explicit scope.

Slots are positions, not portal IDs. Slot 01 does not imply portal 1. Blank pairs are ignored; an ID without a key remains an explicit `CREDENTIAL_MISSING` gap and does not prompt for a replacement. A key without an ID is an error. The example has 20 slots; add `SDP_INSTANCE_21_PORTAL_ID` / `SDP_INSTANCE_21_API_KEY` and further pairs as needed (two to six digits, positive slot numbers). Duplicate portal IDs, including equivalent forms such as `42` and `042`, are rejected. Alternate spellings of the same slot are also rejected.

All slots belong to one source host/application context. Numbered/global credentials require matching `SDP_HOST`. File-provided API keys also require `SDP_HOST` in that same file; overriding the process or command-line host to another source is rejected before HTTP. Do not use one file to send credentials to unrelated servers.

## Separate directory and global access

```dotenv
# Optional primary single-key credential; directory discovery only in multi-key mode.
SDP_API_KEY=
# Optional recovery credential: GET /api/v3/portals only, without PORTALID.
SDP_DIRECTORY_API_KEY=
# Optional authorized global Orguser credential and its documented request context.
SDP_GLOBAL_API_KEY=
SDP_GLOBAL_PORTAL_ID=
```

Instance keys are never automatically reused for ESM global operations. A global key and its context must be supplied together. The directory key is used only for the existing bounded discovery-recovery attempt. All credentials still share the same request limiter and attempt/time budgets.

## Branded copies

```dotenv
# Brand JSON path, preset name or none; blank = CompleteTech LLC preset.
SDP_BRAND_FILE=
SDP_PREPARED_FOR=
```

`SDP_PREPARED_FOR` names the client on every branded copy and in the file names. Leave `SDP_BRAND_FILE` blank for the CompleteTech LLC identity, set it to an approved brand file or preset name, or to `none` for unbranded reports only. `--brand` and `--prepared-for` override these values for one run. These settings hold no secrets and are never sent anywhere. See [branded deliverables](branded-deliverables.md).

## Precedence and conflicts

1. Existing process environment variables win over file values, including an explicitly empty process variable. File values are available only for the duration of the command.
2. Existing CLI-over-JSON precedence for connection settings remains unchanged. A CLI/JSON host must still match the credential binding described above.
3. Numbered entries enable multi-key mode. Without numbered entries, a global key, `--multi-key`, or a credential file, the existing single-key behavior remains available.
4. A JSON credential file may supplement numbered entries with other portal IDs. Assigning the same portal in both places is rejected, even if the keys agree. Missing JSON references retain existing behavior.
5. A populated `SDP_GLOBAL_API_KEY`/`SDP_GLOBAL_PORTAL_ID` pair conflicts with explicit global CLI/JSON configuration. A populated `SDP_DIRECTORY_API_KEY` conflicts with a different `--directory-key-env` reference. These are errors, never silent substitutions.
6. Explicit `--key-input console|dialog` retains its prompt behavior for single-key mode and existing JSON setup. It is rejected when numbered slots are active; clear those slots to use interactive assignment. Noninteractive mode never asks for missing credentials.

Custom environment-variable references in existing JSON credential files can also receive their values from `.env`. Those files retain their own host binding and schema checks.

## Syntax and privacy

The parser accepts UTF-8 (with an optional BOM), blank lines, `#` comment lines and `NAME=value` assignments. Names use ASCII letters, digits and underscores and cannot start with a digit. Spaces around names/values are trimmed. Values may use single or double quotes; both forms are literal, with no escape decoding. An inline comment begins with `#` at the start of an unquoted value or after whitespace. Inside quotes, `#` is literal. Quotes must close on the same line; only a comment may follow the closing quote.

There is no `export` syntax, multiline value, variable interpolation, shell expansion, command substitution or code evaluation. `${NAME}`, `$()`, backticks and backslashes remain literal text. Duplicate names, malformed lines/quotes, invalid UTF-8, control characters, values over 8192 characters, files over 1 MiB and files over 10,000 lines fail locally. API-key validation still applies after parsing. Errors never repeat the input values.

`.env` is a plaintext secret file. Keep it local and out of shared report folders. Git ignores `.env` and `.env.*`, except the blank `.env.example`. Release archives exclude local environment files, including ones placed under example folders, and reject a filled `.env.example`. Reports, diagnostics and console messages do not include key values. New files request owner-only permissions on POSIX; Windows access follows the containing directory's ACL. Existing file permissions are not changed.
