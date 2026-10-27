# Branding

[Agent instructions](SKILL.md) · [Usage guide](docs/guides/usage.md) · [Configuration examples](examples/config/README.md)

This repository ships **no company identity**: no names, logos or brand palettes. Reports are unbranded unless the operator supplies a brand file that lives outside the code base. An approved engagement brand is the operator's choice; do not apply one silently.

## Produce branded copies

```powershell
# After a live run or demo
python .\sdp_cloud_readiness.py --all-portals --brand C:\path\to\branding.json --prepared-for "Client Name"

# For an assessment that already exists (offline; no host or keys)
python .\sdp_cloud_readiness.py --brand C:\path\to\branding.json --prepared-for "Client Name" --brand-assessment .\sdp-assessments\assessment-YYYYMMDD-HHMMSS-xxxxxx
```

To brand every run, set `SDP_BRAND_FILE` and `SDP_PREPARED_FOR` in the local `.env` (both are blank by default). Command-line values take precedence. Add `--no-pdf` to skip PDF printing.

Copies go to `<assessment>/branded/`:

| File | Content | Needs |
| --- | --- | --- |
| `<Client>-Cloud-Readiness-Assessment.html` / `.pdf` | The full report with brand band, accent stripe, prepared by/for and footer | PDF: local Edge or Chrome |
| `<Client>-Vendor-Questions.html` / `.pdf` | The vendor questions, one question per printed page | PDF: local Edge or Chrome |
| `<Client>-Assessment-Findings-and-Coverage.xlsx` | Cover sheet with counts, then every row of `findings.csv` and `coverage.csv` | `openpyxl` |
| `branded-manifest.json` | SHA-256 of the source files and every output, plus anything skipped | — |

The unbranded reports, manifest and ZIP are never modified; they remain the verified evidence. Branded HTML keeps the offline Content-Security-Policy (no scripts, no network) and only allows `data:` images for the embedded logo. PDFs are printed by a headless browser with networking disabled; set `SDP_PDF_BROWSER` to choose a Chromium-based browser.

## Brand file

Two layouts are accepted, so an existing branding skill's file can be used as is.

Skill layout (for example `templates/branding.<name>.json` in a branding skill):

```json
{
  "company": { "name": "Example Consulting", "website": "example.com", "email": "hello@example.com", "tagline": "" },
  "logo": "assets/logo.png",
  "themes": { "light": { "band": "#1F2937", "band_ink": "#FFFFFF", "accent": "#B91C1C", "accent_2": "#0EA5E9" } }
}
```

Flat layout: the same keys without the `company` and `themes` wrappers (`name`, `website`, `email`, `tagline`, `logo`, `light`). See [examples/config/brand.example.json](examples/config/brand.example.json).

| Token | Used for | Default |
| --- | --- | --- |
| `band`, `band_ink` | Masthead band and table headers, and their text | `#1F2937`, `#FFFFFF` |
| `accent` | Stripe (left 38%), headings rule, labels, impact cards | `#177D8D` |
| `accent_2` | Stripe (right 62%), client reference, action boxes | `#55728C` |
| `ink`, `ink_2`, `ink_3` | Headings, body text, muted text | `#0F172A`, `#334155`, `#64748B` |
| `line`, `surface`, `surface_2`, `page`, `link` | Borders, alternating rows, page tint, paper, links | neutral greys, `#0E7490` |

Rules:

- `logo` must be a local PNG or JPEG of at most 2 MB. A relative path is resolved against the brand file's folder and then up to three parent folders, so `assets/logo.png` works from a skill's `templates/` folder. Remote and `data:` logos are rejected; nothing is fetched.
- Colours are 6-digit hex values. Unknown tokens are ignored; a `dark` palette is accepted but reports print in the light palette.
- The client name is escaped everywhere and becomes the file-name prefix (`Client Name` → `Client-Name-…`).

## Keep brands out of Git

Brand files, logos and client deliverables belong to their owners. Keep them in the owning skill or a private location, not in this repository. `sdp-assessments/` is already ignored. A logo or name in a branded copy does not authorize sending it: review the actual output for clipping, contrast and factual accuracy first.
