# Configuration examples

These files contain fictional values and no working credentials. Copy only the templates you need to your working directory and edit the copies.

| Template | Purpose | CLI option |
| --- | --- | --- |
| [connection.example.json](connection.example.json) | Source URL, request budgets, and collection settings | `--config connection.json` |
| [answers.example.json](answers.example.json) | Optional business context for migration findings | `--answers answers.json` |
| [portals.example.json](portals.example.json) | Administrator-verified portal scope when discovery is unavailable | `--portal-file portals.json` |

Keep API keys out of JSON files. Use the masked/hidden prompt or the supported environment-variable mechanism. Local files named `connection.json`, `answers.json`, and `portals.json` are ignored by Git.

An explicit portal list does not establish complete directory visibility or grant access to a portal. See the [all-portals guide](../../docs/guides/all-portals.md).
