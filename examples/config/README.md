# Configuration examples

These files contain fictional values and no working credentials. Copy only the templates you need to your working directory and edit the copies.

For keys, use the root [`.env.example`](../../.env.example) or the blank `.env` created on the first normal run. It contains 20 numbered key/portal-ID pairs and separate directory/global slots. Fill real keys only in your local `.env`, never in these JSON examples. See [local environment setup](../../docs/guides/local-env.md).

| Template | Purpose | CLI option |
| --- | --- | --- |
| [connection.example.json](connection.example.json) | Source URL, request budgets, and collection settings | `--config connection.json` |
| [answers.example.json](answers.example.json) | Optional business context for migration findings | `--answers answers.json` |
| [portals.example.json](portals.example.json) | Administrator-verified portal scope when discovery is unavailable | `--portal-file portals.json` |

Keep API keys out of JSON files. Use the masked/hidden prompt or the supported environment-variable mechanism. Local files named `connection.json`, `answers.json`, and `portals.json` are ignored by Git.

An explicit portal list does not establish complete directory visibility or grant access to a portal. See the [all-portals guide](../../docs/guides/all-portals.md).

## Separate collection keys

Copy `credentials.example.json` and replace all fictional host/portal values. The file contains environment-variable references only; provision their values through your secret mechanism. Repeating a reference explicitly shares that key across those portals. The optional `global` assignment is separate from instance keys and requires a verified global request context.

Run `python .\sdp_cloud_readiness.py --credential-file .\credentials.json --portal-file .\portals.json --non-interactive`. The credential file is not a discovered or verified portal list. See [the complete guide](../../docs/guides/multiple-credentials.md).
