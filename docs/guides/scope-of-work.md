# Scope of Work

A Scope of Work (SoW) turns an assessment into a delivery commitment. The tool renders it in the chosen brand as HTML, PDF, an editable Word file and Markdown, alongside the other [branded deliverables](branded-deliverables.md). The SoW text itself is engagement content written by the consultant; the tool supplies names and evidence figures and the presentation.

## Where the SoW lives

Write the SoW as `scope-of-work.md` in the client's assessment folder, next to `assessment.json`:

```text
sdp-assessments\assessment-YYYYMMDD-HHMMSS-xxxxxx\
  assessment.json, findings.csv, coverage.csv, ...
  scope-of-work.md          <- engagement text, with placeholders
  branded\CompleteTech-LLC\...-Scope-of-Work.html / .pdf / .docx
```

It never belongs in this repository: it contains client names and commercial commitments. To start a new engagement, copy the `scope-of-work.md` from a previous engagement's folder; because names and figures are placeholders, it needs only the engagement-specific prose reviewed.

## Write with placeholders

Never type a client name, consultant name or evidence figure. Use a placeholder, so the same text renders for any brand and the figures always match the assessment they ship with.

| Placeholder | Renders as |
| --- | --- |
| `{{consultant}}` | The brand's company name, e.g. `CompleteTech LLC` |
| `{{client}}` | The `--prepared-for` name; `{{client}}'s` works for the possessive |
| `{{source_url}}` | The assessed ServiceDesk Plus address |
| `{{assessment_date}}` | Assessment date, e.g. `26 October 2026` |
| `{{portal_count}}` | Number of portals assessed |
| `{{inventory_table}}` | Table of incident templates, service templates, query reports, support groups and technician memberships per portal, with a total row |
| `{{inventory_total:KEY}}` | Total across portals for a collection key; join keys with `+`, e.g. `{{inventory_total:incident_templates+service_templates}}` |
| `{{impact_total:RULE}}` | Total affected count of a confirmed impact, e.g. `{{impact_total:DUPLICATE_SERVICE_TAGS}}` |
| `{{impact_portals:RULE}}` | The portals where that impact was confirmed, e.g. `1, 301, and 2101` |

Collection keys are listed by `python .\sdp_cloud_readiness.py --list-endpoints`. Rule names are the last part of a finding ID in `findings.csv`, for example `portal:1:HISTORY_WINDOW_ONE_YEAR` → `HISTORY_WINDOW_ONE_YEAR`; only findings with status `CONFIRMED_IMPACT` can be used.

Example:

```markdown
- **Asset identity:** Resolve the {{impact_total:DUPLICATE_SERVICE_TAGS}} observed computer records with
  duplicate service tags in portal {{impact_portals:DUPLICATE_SERVICE_TAGS}}.
```

## Supported formatting

| Markdown | Use |
| --- | --- |
| `#`, `##`, `###`, `####` | Title, sections, deliverables, sub-headings |
| Blank line | New paragraph; end a line with two spaces for a line break |
| `- item` | Bullet list |
| Pipe tables with a `| --- |` separator row | Tables, including the signature block |
| `**bold**` | Emphasis, labels |
| `[text](https://…)` | Links (https and http only) |
| `<!-- pagebreak -->` | Start a new page in PDF and Word |

Anything else is shown as plain text; HTML in the source is escaped, not executed.

## Render

```powershell
python .\sdp_cloud_readiness.py --prepared-for "Client Name" --brand-assessment .\sdp-assessments\assessment-YYYYMMDD-HHMMSS-xxxxxx
```

Add `--brand <file>` or run from the private IT Impact Consulting edition for another identity; run once per brand. A new assessment always writes a new folder, so after a fresh scan copy `scope-of-work.md` into it and run `--brand-assessment` on that folder.

## When rendering stops

Contract figures must come from complete evidence, so the SoW is not rendered (and the error names the cause) when:

| Cause | Fix |
| --- | --- |
| An inventory placeholder covers a portal whose list was not fully collected | Re-collect that portal (`--resume … --retry-portals`), or remove the figure from the SoW |
| `{{impact_…:RULE}}` names a rule with no confirmed impact in this assessment | The finding changed or disappeared: revise that sentence |
| An unknown placeholder | Check the spelling against the table above |
| `{{client}}` without a client name | Pass `--prepared-for` or set `SDP_PREPARED_FOR` |

## Review before signing

`branded-manifest.json` records every placeholder value used under `scope_of_work_figures`, and the SHA-256 of `scope-of-work.md` and `assessment.json`. When re-rendering against a newer assessment, compare these values with the version previously shared and tell the signatories which figures changed. A rendered SoW is a draft until both parties sign it.
