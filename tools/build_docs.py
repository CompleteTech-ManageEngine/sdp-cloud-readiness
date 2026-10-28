#!/usr/bin/env python3
"""Render the repository documentation as branded HTML, PDF and Word.

Writes one file set per document and a combined handbook to
``dist/docs/<Brand>/`` (ignored by Git):

    python tools/build_docs.py                      # CompleteTech LLC
    python tools/build_docs.py --brand path/to/branding.json --no-pdf

PDFs need a local Edge or Chrome (as for branded deliverables); Word copies
need python-docx. Relative links between documents render as their text.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sdp_audit.branded import find_browser, print_pdf  # noqa: E402
from sdp_audit.branding import load_brand, resolve_brand_path, slug  # noqa: E402
from sdp_audit.markdown_doc import PAGEBREAK, document_title, parse  # noqa: E402
from sdp_audit.scope_of_work import render_document_html  # noqa: E402

# Reading order of the handbook: start, use, operate, brand, reference, maintain.
HANDBOOK = [
    "README.md", "ONBOARDING.md", "docs/guides/usage.md", "docs/guides/local-env.md",
    "docs/guides/all-portals.md", "docs/guides/multiple-credentials.md", "docs/guides/resume.md",
    "docs/guides/coverage-recovery.md", "docs/guides/branded-deliverables.md", "docs/guides/scope-of-work.md",
    "docs/guides/effort-estimate.md",
    "docs/guides/troubleshooting.md", "docs/guides/windows-key-input.md", "BRANDING.md", "BRAND_ASSETS.md",
]
EXTRA = ["SKILL.md", "CONTRIBUTING.md", "CHANGELOG.md", "examples/config/README.md"]


def documents() -> list[Path]:
    paths = [ROOT / p for p in HANDBOOK + EXTRA]
    for folder in ("docs/reference", "docs/development", "docs/releases"):
        paths += sorted((ROOT / folder).glob("*.md"))
    return [p for p in dict.fromkeys(paths) if p.is_file()]


def strip_front_matter(text: str) -> str:
    """Drop a leading YAML block (SKILL.md metadata); it is not reader-facing text."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def output_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return "-".join(part for part in relative.parts if part not in ("docs",)) or "README"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brand", default="completetech", help="Brand JSON path or preset name (default: completetech)")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "docs")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF printing")
    parser.add_argument("--no-docx", action="store_true", help="Skip Word copies")
    args = parser.parse_args()

    brand = load_brand(resolve_brand_path(args.brand, ROOT))
    output = args.output_dir.resolve() / slug(brand.name, "Brand")
    output.mkdir(parents=True, exist_ok=True)
    write_docx = None
    if not args.no_docx:
        try:
            from sdp_audit.branded_docx import write_docx
        except ImportError:
            print("Skipping Word copies: install python-docx.", file=sys.stderr)
    browser = None if args.no_pdf else find_browser()
    if not args.no_pdf and browser is None:
        print("Skipping PDFs: no Edge or Chrome found (set SDP_PDF_BROWSER).", file=sys.stderr)

    footer = f"{brand.name} · ServiceDesk Plus Cloud Readiness documentation, rendered from the repository Markdown."
    items: list[tuple[str, str]] = [(output_name(p), strip_front_matter(p.read_text(encoding="utf-8-sig"))) for p in documents()]
    handbook_text = f"\n\n{PAGEBREAK}\n\n".join(text for name, text in items
                                                 if name in {output_name(ROOT / p) for p in HANDBOOK})
    contents = "\n".join(f"{n}. {document_title(parse(text), name)}" for n, (name, text) in enumerate(
        ((name, text) for name, text in items if name in {output_name(ROOT / p) for p in HANDBOOK}), start=1))
    cover = (f"# ServiceDesk Plus Cloud Readiness Handbook\n\nUser, operator and branding documentation for the read-only "
             f"ServiceDesk Plus on-premises Cloud migration assessment, by {brand.name}.\n\n## Contents\n\n{contents}\n")
    items.insert(0, ("ServiceDesk-Plus-Cloud-Readiness-Handbook", cover + "\n" + PAGEBREAK + "\n\n" + handbook_text))

    written = []
    for name, text in items:
        blocks = parse(text)
        html_path = output / f"{name}.html"
        html_path.write_text(render_document_html(blocks, brand, "Documentation", footer), encoding="utf-8")
        written.append(html_path)
        if browser:
            pdf_path = output / f"{name}.pdf"
            try:
                print_pdf(html_path, pdf_path, browser)
                written.append(pdf_path)
            except (OSError, subprocess.SubprocessError):
                print(f"PDF failed: {pdf_path.name}", file=sys.stderr)
        if write_docx:
            docx_path = output / f"{name}.docx"
            write_docx(blocks, brand, document_title(blocks, name), "Documentation", docx_path)
            written.append(docx_path)
    print(f"Documentation ({brand.name}): {len(items)} documents, {len(written)} files in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
