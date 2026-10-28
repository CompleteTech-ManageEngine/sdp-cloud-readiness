# Branded deliverables and Scope of Work validation

Evidence for the branded-deliverable and Scope of Work features (pull requests #22 to #25). Client data is not reproduced here; the real-engagement checks below record only what was compared.

## Automated tests

`PYTHONUTF8=1 python -m unittest discover -s tests` in a clean checkout without a local `.env`: 581 tests, OK (6 skipped). Without `PYTHONUTF8=1` on Windows, five `test_report` tests fail on cp1252 decoding; this predates these changes.

| Test module | Covers |
| --- | --- |
| `tests/test_branding.py` | Brand file layouts, logo resolution and rejection (remote, `data:`, missing), colour validation, preset resolution, `--brand none`, entry-point default vs unbranded library `main()`, logo tile, offline CSP and escaping, unbranded output unchanged, per-brand folder, manifest and workbook |
| `tests/test_markdown_doc.py` | Markdown reader (escapes, code, numbered lists, angle-bracket and relative links, raw HTML, Mermaid, tables with escaped pipes, soft wraps and hard breaks) and Word writer (tables in reading order, complete text) |
| `tests/test_effort_estimate.py` | Evidence drivers, PERT expected / deviation / P80 / contingency arithmetic, validation, pack outputs, workbook formulas and input cells |
| `tests/test_scope_of_work.py` | Placeholder filling from brand and evidence, unknown placeholder / missing client / absent impact / incomplete inventory refusals, Markdown subset and HTML escaping, SoW in the pack with Word output, pack without a SoW |
| `tests/test_release.py` | Standard-library runtime, with `openpyxl` and `python-docx` allowed only in `branded_xlsx.py` / `branded_docx.py` behind `ImportError` guards; release manifest contents |
| `tests/test_local_env.py` | `.env` scaffold includes blank `SDP_BRAND_FILE` and `SDP_PREPARED_FOR` and matches `.env.example` |

## Manual checks

| Check | Result |
| --- | --- |
| Demo with CompleteTech, fictional and IT Impact brands | HTML, PDF and workbook produced; mastheads rendered and inspected |
| Extracted portable release (`.pyz` with `templates\` and `assets\`) | CompleteTech copies produced by default |
| Portable `.pyz` alone | Assessment succeeds; note printed; unbranded only |
| Branded layer vs an approved hand-branded report (same brand, same evidence) | Masthead, stripe, parties, footer and logo identical; remaining differences were scanner guidance text changed after that run |
| Real 12-portal assessment, both brands | Report PDF 469 pages and vendor questions 111 pages, each ending at the branded footer; workbook rows equal CSV rows; unbranded originals unchanged against `report-manifest.json` |
| Real engagement SoW converted to placeholders, refilled with its original brand | Text identical to the original except the evidence figures that differed in the newer complete assessment |
| Word copies of a real 12-portal report, vendor questions and SoW | Every source word present, none added (word-level comparison with the Markdown); exported through Microsoft Word to PDF: SoW 10 pages, report 791 pages, tables in reading order, header and page numbers on every page |
| Documentation build | 33 documents and a 64-page handbook rendered as HTML, PDF and Word; YAML front matter and Mermaid source omitted from print formats |
| Effort estimate workbook recalculated by Microsoft Excel | Totals identical to the Python engine (expected, contingency, P80, P90); no formula errors; editing a task's hours, adding a task in a spare row and setting a rate updated every total; an O > M entry was flagged |
| SoW rendered for both brands | 15 pages each; no other brand's name in PDF or Word; no unfilled placeholders; signature block names the rendering brand |

## Not covered

PDF pagination depends on the installed Edge/Chrome version. Word output was checked by reading the generated document, not by visual comparison in Microsoft Word. Reports print in the light palette only.
