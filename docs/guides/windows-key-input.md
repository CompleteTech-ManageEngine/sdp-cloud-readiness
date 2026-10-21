# Windows API-key entry and paste troubleshooting

## What the reported screen establishes

The old message `The API key must contain printable ASCII characters without whitespace` originates in the local `ReadOnlyClient` constructor, before it creates an HTTP request. It is not an SDP 401/403 response, and it does not establish an expired key, missing role, wrong portal or inaccessible module. The screen does not reveal the entered key or its exact character sequence.

One matching cause is the Windows console/Python `getpass()` Ctrl+V behavior. The CPython issue below documents that a raw console read can receive SYN (control character 0x16) rather than pasted text. Other invisible characters or interior whitespace can also trigger the old validation message. This release treats input diagnostics separately from server authentication.

## Normal invocation

```powershell
python .\sdp_cloud_readiness.pyz
```

The version banner should show **2.0.1**. Enter the URL normally. In automatic mode on Windows, a local key-entry dialog opens: paste **only the API key**, then select OK. The entry is masked with asterisks; the program does not display the key text. Cancel exits without making API requests.

The dialog uses the Python standard library's `tkinter` interface. It requires Tcl/Tk and a desktop; some minimal Python installations or service sessions omit those. Automatic mode falls back to a hidden console prompt if a dialog cannot be created. The program does not install anything, invoke PowerShell, read the clipboard automatically, or change Windows console settings.

## Console-only recovery

```powershell
python .\sdp_cloud_readiness.pyz --key-input console
```

At the hidden key prompt, use the console window menu **Edit > Paste**. Right-click paste also works in console configurations that enable it. Ctrl+Shift+V depends on the console host's settings. Do not assume plain Ctrl+V pastes into a legacy hidden console prompt. Input stays hidden; there is no plain-text fallback.

The reported Ctrl+V character is **not discarded to salvage a partial key**. The entire malformed entry is rejected and the key is requested again, up to three local attempts. Back out with Ctrl+C rather than restarting several whole assessments.

## Explicit GUI and local-only check

```powershell
python .\sdp_cloud_readiness.pyz --key-input dialog
python .\sdp_cloud_readiness.pyz --check-key-input
python .\sdp_cloud_readiness.pyz --key-input console --check-key-input
```

`--check-key-input` needs no host and writes no reports. It checks local input and header-safe format, **not** authentication, expiration, permissions or portal reachability. A valid-looking but incorrect key will pass this local check and may still be rejected by the server during an actual assessment.

Default `auto` preserves the existing environment-variable interface. A key already present in `SDP_API_KEY` (or the variable named by `--api-key-env`) is used without prompting, with a value-free notice. Explicit `console` and `dialog` modes ignore such an environment key and prompt anew. An invalid environment value fails once; it is not silently replaced by a different credential. Never type a real key into a shell command or a configuration file just to avoid the prompt.

## Input categories

| Local condition | Behavior |
|---|---|
| Empty or missing paste | Request a new entry; do not contact SDP |
| Ctrl+V control character | Explain the paste problem and retry; never strip it from a possible partial key |
| Other terminal controls | Reject the entry; do not print the characters or surrounding text |
| Leading/trailing whitespace, BOM or zero-width-space boundary markers | Remove only those boundaries, notify without showing the value |
| Interior whitespace or invisible/non-ASCII characters | Reject; never rejoin, transliterate or guess a key |
| Hidden console input unavailable | Fail closed instead of echoing the key |
| Dialog cannot be created | Auto may use hidden console; explicitly requested dialog fails with guidance |
| Dialog callback/read exception | Suppress exception text/tracebacks; stop safely |

The original 8192-character input safety bound and transport validation remain. Quotes, percent encoding and interior symbols are not decoded or rewritten. Key storage in Python/Tk memory cannot be guaranteed securely erasable; the application does not intentionally persist the key. Operating-system clipboard managers, screen capture, memory dumps, host instrumentation and environment management are outside that guarantee.

## Using the corrected file

Extract the new ZIP into a fresh folder, or replace the portable `.pyz` **and launcher** together. The new launcher selects `.pyz` first so old neighboring `.py` modules cannot shadow it. Direct execution of `python .\sdp_cloud_readiness.py` intentionally uses source. Use `--version` on the exact file being run before another scan. Old report folders can be kept separately; they are not upgraded or overwritten by this patch.

No portal roles, server configuration, TLS settings or integration keys need to be changed merely to resolve the screenshot's local character-validation error. After entry succeeds, actual HTTP/SDP diagnostics remain responsible for reporting server authentication and permissions.

## Primary references reviewed October 14, 2026

- CPython issue 81607, including maintainer explanations of raw Windows console input and paste workarounds: https://github.com/python/cpython/issues/81607
- Python getpass reference, including `GetPassWarning` for an echoing fallback: https://docs.python.org/3.12/library/getpass.html
- Python Tkinter dialogs reference: https://docs.python.org/3/library/dialog.html

These sources explain runtime/input behavior. They do not establish what the user actually typed or pasted. GUI tests are synthetic, and no customer server or key is used for testing.
