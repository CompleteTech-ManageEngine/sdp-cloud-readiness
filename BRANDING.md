# CompleteTech LLC Skills: branding and handoffs

[Start here](ONBOARDING.md) · [Asset rights](BRAND_ASSETS.md) · [Specialist instructions](SKILL.md)

## Identity of branded copies

Every run of the entry points writes client-ready copies to `<assessment>/branded/<Brand>/` (for example `branded/CompleteTech-LLC/`) with the **CompleteTech LLC** identity: the preset [templates/branding.completetech.json](templates/branding.completetech.json) and the local `assets/logo.png`. An approved engagement brand takes precedence. Preserve the operator's explicit settings and confirm the client name before producing deliverables.

| Choice | How |
|---|---|
| CompleteTech LLC (default) | Nothing to set; name the client with `--prepared-for "Client"` or `SDP_PREPARED_FOR` |
| Another approved brand | `--brand <brand.json>` or `SDP_BRAND_FILE=<brand.json>`; a preset name from `templates/` also works |
| Unbranded evidence only | `--brand none` or `SDP_BRAND_FILE=none` |
| Brand an existing assessment, offline | `--prepared-for "Client" --brand-assessment <assessment folder>` |

Use the existing local `assets/logo.png` for authorized CompleteTech output. Do not synthesize replacement marks, fetch remote artwork, redistribute fonts, or move brand assets between repositories. The MIT code license does not replace the asset policy in [BRAND_ASSETS.md](BRAND_ASSETS.md). A logo must be a local PNG or JPEG of at most 2 MB; remote and data-URI logos are rejected.

## Branded copies

Each brand gets its own folder under `branded/`, so the same assessment can be delivered under several identities (run `--brand-assessment` once per brand).

| File | Content | Needs |
|---|---|---|
| `<Client>-Cloud-Readiness-Assessment.html` / `.pdf` / `.docx` / `.md` | The full report with brand band, accent stripe, prepared by/for block and footer | PDF: local Edge or Chrome; Word: `python-docx` |
| `<Client>-Vendor-Questions.html` / `.pdf` / `.docx` / `.md` | Vendor questions, one question per printed page | PDF: local Edge or Chrome; Word: `python-docx` |
| `<Client>-Assessment-Findings-and-Coverage.xlsx` | Cover sheet with counts, then every row of `findings.csv` and `coverage.csv` | `openpyxl` |
| `<Client>-ServiceDesk-Plus-Cloud-Scope-of-Work.html` / `.pdf` / `.docx` / `.md` | The engagement Scope of Work, when the assessment folder holds `scope-of-work.md` | PDF: Edge or Chrome; Word: `python-docx` |
| `<Client>-Effort-Estimate.xlsx` / `.html` / `.pdf` / `.docx` / `.md` | PERT effort estimate when the assessment folder holds `effort-estimate.json`; the workbook recalculates as task hours change | Workbook: `openpyxl` |
| `branded-manifest.json` | SHA-256 of the source files and every output, the Scope of Work figures and estimate totals used, and anything skipped | — |

Branded copies are rendered from the run's own `assessment.json`, `findings.csv` and `coverage.csv`. The unbranded reports, manifest and ZIP are never modified; they remain the verified evidence. Branded HTML keeps the offline Content-Security-Policy (no scripts, no network) and only allows `data:` images for the embedded logo. PDFs are printed by a headless browser with networking disabled; `SDP_PDF_BROWSER` selects a Chromium-based browser and `--no-pdf` skips printing.

## Scope of Work

The Scope of Work is engagement content: write it as `scope-of-work.md` in the client's assessment folder (it never belongs in this repository). Placeholders keep it tied to the brand and the evidence, so the same text renders for any approved identity and its figures cannot drift from `assessment.json`:

| Placeholder | Value |
|---|---|
| `{{consultant}}`, `{{client}}` | Brand name and `--prepared-for` client |
| `{{source_url}}`, `{{assessment_date}}`, `{{portal_count}}` | Assessed host, assessment date, portals assessed |
| `{{inventory_table}}` | Per-portal incident and service templates, query reports, support groups and technician memberships, with totals |
| `{{inventory_total:KEY}}` | Total for a collection key; join keys with `+`, e.g. `incident_templates+service_templates` |
| `{{impact_total:RULE}}`, `{{impact_portals:RULE}}` | Affected count and portals of a confirmed impact, e.g. `DUPLICATE_SERVICE_TAGS` |

Supported Markdown: headings, paragraphs (two trailing spaces break a line), `-` bullets, pipe tables, `**bold**`, `[text](https://…)` links and `<!-- pagebreak -->`. Rendering stops on an unknown placeholder, a missing client name, an absent impact, or an inventory figure whose list traversal was incomplete: contract figures must come from complete evidence. The values used are recorded in `branded-manifest.json`. A rendered Scope of Work is a draft until both parties sign it. Step-by-step guides: [branded deliverables](docs/guides/branded-deliverables.md) and [Scope of Work](docs/guides/scope-of-work.md).

## CompleteTech palette

The preset uses the established library colors and the logo's blue:

| Token | Value | Used for |
|---|---|---|
| `band` | `#0F172A` | Masthead band and table headers |
| `accent` | `#1E3A8A` | Stripe (left), heading rules, labels, impact cards |
| `accent_2` | `#0A84F0` | Stripe (right), client reference, action boxes |
| `ink`, `ink_2`, `ink_3` | `#0F172A`, `#1E293B`, `#64748B` | Headings, body text, muted text |
| `line`, `surface`, `surface_2` | `#E2E8F0`, `#F8FAFC`, `#EEF2FF` | Borders, alternating rows, page tint |
| `logo_background` | `#F8FAFC` | Tile behind the opaque logo on the dark band |

Reports print in the light palette; the preset's `dark` tokens are reserved for a future dark rendering.

## Other brand files

Two layouts are accepted, so another skill's brand file can be used as is.

Skill layout:

```json
{
  "company": { "name": "Example Consulting", "website": "example.com", "email": "hello@example.com", "tagline": "" },
  "logo": "assets/logo.png",
  "logo_background": "",
  "themes": { "light": { "band": "#1F2937", "band_ink": "#FFFFFF", "accent": "#B91C1C", "accent_2": "#0EA5E9" } }
}
```

Flat layout: the same keys without the `company` and `themes` wrappers. See the fictional [examples/config/brand.example.json](examples/config/brand.example.json). A relative logo path resolves against the brand file's folder and then up to three parent folders. Colours are 6-digit hex values; missing tokens fall back to neutral defaults and unknown tokens are ignored. The client name is escaped everywhere and becomes the file-name prefix.

## Handoff to the next skill

Carry verified facts and their sources, the assessment folder and tool version, the identity used and the client name, confidentiality, intended audience, approval owner and status, open coverage gaps and vendor questions, and the next specialist. A rendered, branded or hash-verified deliverable does not authorize sending, publication or migration approval. Review the actual output for clipping, contrast, placeholders and factual accuracy before approved use.
