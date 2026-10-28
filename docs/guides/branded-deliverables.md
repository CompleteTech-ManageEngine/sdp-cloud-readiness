# Branded client deliverables

Every assessment produces two sets of files. The **verified evidence set** (`report.html`, `report.md`, `assessment.json`, the CSVs, `vendor-questions.md`, diagnostics, manifest and ZIP) is written, read back and hashed; it is never modified afterwards. The **branded set** is a presentation copy of that evidence for the client, written to `<assessment>/branded/<Brand>/`.

Identity rules, the CompleteTech palette and the brand file format are in [BRANDING.md](../../BRANDING.md). This guide covers day-to-day use.

## What you get

| File | Content | Needs |
| --- | --- | --- |
| `<Client>-Cloud-Readiness-Assessment.html` / `.pdf` / `.docx` / `.md` | The full report: masthead, prepared by/for, all findings, coverage and sources | PDF: Edge or Chrome; Word: `python-docx` |
| `<Client>-Vendor-Questions.html` / `.pdf` / `.docx` / `.md` | Answers and open questions, one question per printed page | PDF: Edge or Chrome; Word: `python-docx` |
| `<Client>-Assessment-Findings-and-Coverage.xlsx` | Cover sheet with counts, then every row of `findings.csv` and `coverage.csv`, filterable | `openpyxl` |
| `<Client>-ServiceDesk-Plus-Cloud-Scope-of-Work.html` / `.pdf` / `.docx` / `.md` | The engagement Scope of Work, when `scope-of-work.md` is present (see [Scope of Work](scope-of-work.md)) | PDF: Edge or Chrome; Word: `python-docx` |
| `<Client>-Effort-Estimate.xlsx` and `.html` / `.pdf` / `.docx` / `.md` | PERT effort estimate, when `effort-estimate.json` is present: an editable workbook with live formulas plus the client-ready document (see [Effort estimate](effort-estimate.md)) | Workbook: `openpyxl` |
| `<Client>-Effort-Estimate-Detailed.html` / `.pdf` / `.docx` / `.md` | The full PERT working table for internal review | — |
| `branded-manifest.json` | SHA-256 of every source and output, Scope of Work figures and estimate totals used, anything skipped | — |

`<Client>` is the `--prepared-for` name with spaces replaced by hyphens. `<Brand>` is the brand's company name, for example `CompleteTech-LLC`.

Install the optional packages once: `python -m pip install openpyxl python-docx`. Without them the run still succeeds and `branded-manifest.json` lists what was skipped.

Every document has the same text in each format. HTML and PDF are for reading and sending; the Word copy is for editing (brand band in the header, contact line and page numbers in the footer); the Markdown copy carries a brand line and suits version control or pasting into other tools. The Word report is long (several hundred pages for a large assessment) because it holds every evidence table; use it as an editable reference.

## Choose the identity

| Situation | Command |
| --- | --- |
| CompleteTech LLC (default) | `python .\sdp_cloud_readiness.py --all-portals --prepared-for "Client Name"` |
| Another approved brand | add `--brand C:\path\to\branding.json` (or a preset name from `templates\`) |
| Evidence only, no branded copies | add `--brand none` |
| Same settings on every run | set `SDP_PREPARED_FOR` and, if needed, `SDP_BRAND_FILE` in `.env` ([local environment](local-env.md#branded-copies)) |

Command-line values override `.env`. The private IT Impact Consulting edition of this repository uses the same options with its own default brand.

## Brand an existing assessment

Branded copies can be produced at any time from a finished assessment folder, without a host, keys or network:

```powershell
python .\sdp_cloud_readiness.py --prepared-for "Client Name" --brand-assessment .\sdp-assessments\assessment-YYYYMMDD-HHMMSS-xxxxxx
```

Run it once per brand to deliver the same evidence under several identities; each brand gets its own folder. Re-running for the same brand refreshes its files, which is how you update deliverables after editing `scope-of-work.md` or `effort-estimate.json`, or after upgrading the tool.

Re-running never destroys your own work:

- **Edited deliverables are kept.** If you changed a branded file after it was generated (for example edited the Word Scope of Work or adjusted the estimate workbook), the new version is written beside it as `….regenerated.docx` / `.xlsx` / … and your copy is left untouched. The console and `branded-manifest.json` (`preserved_edits`) list these files. Merge what you need, then delete or rename the one you no longer want.
- **Open files are skipped.** A file open in Word or Excel cannot be replaced; it is listed under `skipped` and every other file is still written. Close it and run again.

## Before you send anything

1. Open the branded report and Scope of Work and read them as the client will: masthead, client name, figures, signature block.
2. Compare `branded-manifest.json` → `scope_of_work_figures` with any earlier version you shared, and call out changed figures.
3. Confirm the branded set was built from the assessment you intend (the manifest lists the source `assessment.json` hash and the assessment folder).
4. Remember that reports contain internal identifiers, structure and configuration findings. A branded file does not authorize sending, publication or migration approval.

## Printable documentation

The repository documentation itself (README, onboarding, every guide, branding, reference and validation records) can be rendered in the same branded style, as HTML, PDF and Word, plus a combined handbook with a contents page:

```powershell
python .\tools\build_docs.py                 # CompleteTech LLC, into dist\docs\CompleteTech-LLC\
python .\tools\build_docs.py --no-pdf        # HTML and Word only
python .\tools\build_docs.py --brand <file>  # another approved brand
```

The handbook (`ServiceDesk-Plus-Cloud-Readiness-Handbook.pdf` / `.docx`) collects the user, operator and branding documents in reading order. `dist\` is not committed.

## PDFs

PDFs are printed from the branded HTML by a locally installed Microsoft Edge or Google Chrome in headless mode with networking disabled. The browser is found automatically on Windows and macOS; set `SDP_PDF_BROWSER` to a Chromium-based browser executable to choose one. Use `--no-pdf` to skip printing, for example on a server without a browser. A large assessment can produce a report PDF of several hundred pages; the HTML is the faster way to read it.

## Troubleshooting

| Message | Meaning and fix |
| --- | --- |
| `Skipped …: could not be replaced (is it open in another program?)` | Close the file in Word, Excel or the PDF viewer and run `--brand-assessment` again. |
| `Kept your edited …; the new version is beside it as .regenerated` | You changed that file since it was generated. Compare it with the `.regenerated` copy and keep the one you want. |
| `Branded copies need a brand file` | `--prepared-for` or `--brand-assessment` was used with branding disabled. Remove `--brand none` / `SDP_BRAND_FILE=none`, or pass `--brand`. |
| `Brand file or preset not found` | The `--brand` path or preset name does not exist. Check the path, or list `templates\`. |
| `Default branding preset not found beside the app` | A portable `.pyz` was copied without its `templates\` and `assets\` folders. Use the extracted release folder; the assessment itself is unaffected. |
| `Skipped PDF: no Edge or Chrome found` | Install Edge or Chrome, or set `SDP_PDF_BROWSER`. |
| `Skipped Workbook: install openpyxl` / `Word: install python-docx` | Install the optional package and re-run `--brand-assessment`. |
| `Scope of Work figure '…' is not complete` | See [Scope of Work](scope-of-work.md#when-rendering-stops). |
