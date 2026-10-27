# Start here: sdp-cloud-readiness

<p align="center"><img src="assets/logo.png" alt="CompleteTech LLC logo" width="260"></p>

**CompleteTech LLC Skills** — ServiceDesk Plus Cloud migration readiness.

[Overview](README.md) · [Agent instructions](SKILL.md) · [Branding and handoffs](BRANDING.md) · [Contributing](CONTRIBUTING.md)

## 1. Choose the right skill

Use this skill to assess a ManageEngine ServiceDesk Plus on-premises installation before migration to ServiceDesk Plus Cloud: it discovers every accessible portal, reads inventory and metadata with GET requests only, and produces offline evidence reports plus CompleteTech-branded client deliverables. Its activation and install-directory key is **`sdp-cloud-readiness`**; the repository is `CompleteTech-ManageEngine/sdp-cloud-readiness`. Install the whole directory, not only SKILL.md.

## 2. Prepare a full checkout

Python 3.10 or newer; the scanner needs only the standard library.

```bash
git clone https://github.com/CompleteTech-ManageEngine/sdp-cloud-readiness.git
cd sdp-cloud-readiness
python -m unittest discover -s tests
```

On Windows, run the tests with `PYTHONUTF8=1` (PowerShell: `$env:PYTHONUTF8=1`). Optional: `pip install openpyxl` for the branded workbook; Microsoft Edge or Google Chrome for branded PDFs. For Claude Code, place or link the checkout at `~/.claude/skills/sdp-cloud-readiness`.

## 3. Run the demonstration

```bash
python sdp_cloud_readiness.py --demo --prepared-for "Northwind Health"
```

The demonstration uses synthetic portals and touches no network. It writes the verified report set and, under `branded/`, CompleteTech-branded HTML, PDF and workbook copies. Open them and review the layout.

## 4. Start a real assessment separately

Before the first live run, relay the **Before you start** table in [SKILL.md](SKILL.md). Confirm the host, the portals in scope, how keys will be supplied (hidden prompt or local `.env`) and the client name. The operator runs the live command; keys are never placed on a command line or in chat.

Real assessments contain internal identifiers and configuration. `sdp-assessments/` and `.env` are ignored by Git; do not share outputs without review.

## Branding and downstream use

Branded copies carry the CompleteTech LLC identity unless an approved engagement brand is passed with `--brand`, or `--brand none` is used. Follow [BRANDING.md](BRANDING.md). When handing results to a proposal, scope or billing skill, carry the assessment folder, finding counts, open coverage gaps and vendor questions; an assessment is not migration approval.

## Verify changes

```bash
python -m unittest discover -s tests
python tools/build_release.py
```

Follow [CONTRIBUTING.md](CONTRIBUTING.md).
