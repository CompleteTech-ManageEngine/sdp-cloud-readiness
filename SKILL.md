---
name: sdp-cloud-readiness
description: >-
  Assess a ManageEngine ServiceDesk Plus on-premises installation (single portal or every ESM portal) for migration to ServiceDesk Plus Cloud with a read-only, GET-only, standard-library Python scanner, and produce offline HTML, Markdown, JSON and CSV reports and CompleteTech-branded client deliverables (HTML, PDF and an Excel findings/coverage workbook), or another approved brand on request. Disclosure: this skill calls only the ServiceDesk Plus host the operator names, with API keys the operator enters in a hidden prompt or a local .env; it never sends data elsewhere, never stores keys in reports, and writes everything to a local folder. Use when asked to assess SDP / ServiceDesk Plus cloud readiness, scan SDP portals before a cloud migration, produce SDP migration findings or vendor questions, resume or retry an SDP assessment, run the SDP demo, or brand an existing SDP assessment for a client.
version: 2.2.0
metadata:
  openclaw:
    skillKey: sdp-cloud-readiness
    requires:
      bins:
        - python3
---

# ServiceDesk Plus Cloud Readiness

A CompleteTech LLC skill. See [ONBOARDING.md](ONBOARDING.md) for first use.

## Purpose

| Use | Scope |
|---|---|
| Assessment | Read-only inventory and metadata collection from SDP on-premises (14.x/15.x ESM and earlier) across every accessible portal, analysed against documented Cloud migration limits. |
| Outputs | `report.html`, `report.md`, `assessment.json`, `findings.csv`, `coverage.csv`, `vendor-questions.md`, `diagnostics.json`, a manifest and a verified ZIP, in a new timestamped folder. |
| Branded copies | One folder per brand, CompleteTech by default: `branded/<Brand>/<Client>-Cloud-Readiness-Assessment.html/.pdf`, `<Client>-Vendor-Questions.html/.pdf`, `<Client>-Assessment-Findings-and-Coverage.xlsx` and `branded-manifest.json`. |
| Boundary | GET only, one global rate limiter, budgets on requests and time. An assessment is evidence, not migration approval. |

Run every command from this skill's folder (the repository root). Python 3.10+; the scanner uses only the standard library. Branded workbooks need `openpyxl`; branded PDFs need a local Edge or Chrome. Both are optional and skipped with a message when missing.

## Before you start

Relay this to the operator before the first live run:

| Topic | What the operator must hear |
|---|---|
| What is read | Only reviewed GET endpoints on the SDP host they name: portal directory, module inventories, sampled details and field metadata. No ticket descriptions, notes, attachment bodies or credentials are kept in reports. |
| Keys | You (the agent) never type, echo or store an API key. The operator enters keys in the tool's hidden prompt or in the local `.env` beside `sdp_cloud_readiness.py`. In Claude Code they run the live command themselves with a `!` prefix so the hidden prompt reaches their terminal. |
| What is written | A new folder under `sdp-assessments/` (Git-ignored). Reports contain internal structure, identifiers, counts and configuration findings: review before sharing. |
| Identity | Branded copies carry CompleteTech LLC unless the operator names another approved brand or `--brand none`. Confirm the client name. |
| Removal | Delete the assessment folder and its ZIP. Optional saved portal scope (`--save-portals`) lives in the user profile and holds no keys. |

## Commands

| Goal | Command |
|---|---|
| Offline demonstration, no network or keys | `python sdp_cloud_readiness.py --demo` |
| Check report output works on this machine | `python sdp_cloud_readiness.py --check-output` |
| Live assessment of every discovered portal (operator runs it) | `python sdp_cloud_readiness.py --all-portals` |
| Live, CompleteTech deliverables | `python sdp_cloud_readiness.py --all-portals --prepared-for "<Client>"` |
| Long run with resume points | add `--checkpoint`; continue with `--resume <checkpoint.json>` |
| Retry gaps after access changes | `--resume <checkpoint.json> --retry-failed` or `--retry-portals 3,5` |
| Brand an existing assessment, offline | `python sdp_cloud_readiness.py --prepared-for "<Client>" --brand-assessment sdp-assessments/<folder>` |
| Directory discovery diagnosis only | `python sdp_cloud_readiness.py --diagnose` |
| Every option | `python sdp_cloud_readiness.py --help` |

Exit code 0 means reports were written and read back, not that migration is safe; 2 means the assessment is incomplete or was stopped; 1 is a startup or local output error.

## Branding

Branded copies carry the CompleteTech LLC identity by default (preset `completetech`: [templates/branding.completetech.json](templates/branding.completetech.json) and `assets/logo.png`). Always ask for the client name (`--prepared-for` or `SDP_PREPARED_FOR`). An approved engagement brand takes precedence: pass its file with `--brand` or set `SDP_BRAND_FILE`; `--brand none` keeps only the unbranded evidence. Do not synthesize logos or fetch artwork. Layouts, palette and asset rules are in [BRANDING.md](BRANDING.md) and [BRAND_ASSETS.md](BRAND_ASSETS.md).

Branded copies are rendered from the run's own `assessment.json`, `findings.csv` and `coverage.csv`; the verified unbranded files are never modified, and `branded/<Brand>/branded-manifest.json` records the source and output hashes.

## Workflow

1. Confirm the goal: demo, live assessment, resume, or branding an existing folder. Relay Before you start for a live run.
2. Confirm the client name and whether the deliverables carry CompleteTech (default), another approved brand, or none.
3. Demo and `--brand-assessment` you may run yourself. For a live run, give the operator the exact command to run with `!` (or confirm their `.env` holds `SDP_HOST` and keys, in which case the run needs no prompt).
4. Read the console summary: counts per status, coverage gaps, and the paths printed. Open `report.html` (or the branded copy) for the operator.
5. Report back (below). Point coverage gaps at [docs/guides/coverage-recovery.md](docs/guides/coverage-recovery.md) and discovery problems at [docs/guides/troubleshooting.md](docs/guides/troubleshooting.md).

## Hard rules

1. Never place an API key on a command line, in a JSON config, in chat or in a report. Keys belong only in the hidden prompt or the local `.env`.
2. Never commit `.env`, `sdp-assessments/`, client brand files, logos or client deliverables.
3. Do not widen the GET allowlist, bypass permissions or guess portal IDs. Unknown stays unknown.
4. A rendered or branded report does not authorize sending it. The operator reviews and shares.

## Final report to the operator (short)

Folder path, portals assessed vs discovered, counts of Confirmed impact / No issue observed / Unknown / Manual confirmation, the largest coverage gaps and their recommended recovery, whether branded copies were written (and anything skipped, such as PDF or workbook), and what still needs a vendor or owner answer (`vendor-questions.md`).
