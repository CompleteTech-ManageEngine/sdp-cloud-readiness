"""Branded client-ready copies of a finished assessment.

The six verified report files are never modified. Branded copies are written
to ``<assessment>/branded/<Brand>/`` (one folder per brand, so several
identities can coexist) from the assessment's own ``assessment.json``,
``findings.csv`` and ``coverage.csv``:

* ``<Client>-Cloud-Readiness-Assessment.html`` and ``.pdf``
* ``<Client>-Vendor-Questions.html`` and ``.pdf``
* ``<Client>-Assessment-Findings-and-Coverage.xlsx``
* Word (``.docx``) and Markdown (``.md``) copies of the report, the vendor
  questions and the Scope of Work, with the brand in the header and footer
* ``<Client>-ServiceDesk-Plus-Cloud-Scope-of-Work.html``, ``.pdf``, ``.docx`` and ``.md``
  when the assessment folder holds an engagement ``scope-of-work.md``
* ``<Client>-Effort-Estimate.xlsx`` (editable PERT workbook) and ``.html``,
  ``.pdf``, ``.docx``, ``.md`` when it holds an ``effort-estimate.json``
* ``branded-manifest.json`` with SHA-256 hashes of sources and outputs

HTML needs only the standard library. PDFs are printed from the branded HTML by
a locally installed Edge or Chrome in headless mode (no network: the pages load
nothing external and the browser runs with networking disabled). The workbook
needs ``openpyxl`` and the Word copies ``python-docx``. A missing optional tool is reported and skipped; it never
fails the assessment.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

from . import __version__
from .artifacts import atomic_write_bytes
from .branding import Brand, markdown_header, slug
from .report import render_branded_questions_html, render_branded_report_html
from .effort_estimate import ESTIMATE, load_estimate, markdown as estimate_markdown
from .scope_of_work import Figures, document_title, parse, render_document_html, render_html as render_scope_html

SCOPE_OF_WORK = "scope-of-work.md"

PDF_TIMEOUT_SECONDS = 600
_BROWSERS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)


def find_browser() -> str | None:
    override = os.environ.get("SDP_PDF_BROWSER")
    if override:
        return override if Path(override).is_file() else None
    for name in ("msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return next((path for path in _BROWSERS if Path(path).is_file()), None)


def print_pdf(source: Path, target: Path, browser: str) -> None:
    """Print a local, self-contained HTML file to PDF with a headless browser."""
    with tempfile.TemporaryDirectory(prefix="sdp-pdf-") as profile:
        command = [
            browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
            "--disable-extensions", "--disable-sync", "--disable-background-networking",
            "--proxy-server=127.0.0.1:9", "--proxy-bypass-list=<-loopback>",
            "--user-data-dir=" + profile, "--no-pdf-header-footer", "--print-to-pdf-no-header",
            "--print-to-pdf=" + str(target), source.resolve().as_uri(),
        ]
        target.unlink(missing_ok=True)
        subprocess.run(command, check=True, timeout=PDF_TIMEOUT_SECONDS,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not target.is_file() or target.read_bytes()[:5] != b"%PDF-":
        raise OSError("The browser did not produce a PDF.")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


HASHES = ".branded-hashes.json"


def _previous_outputs(output: Path) -> dict[str, str]:
    """Hashes of the files this tool last wrote in the brand folder, to recognise deliverables edited since.

    The sidecar is updated after every file, so an interrupted run never makes the tool's own output look edited.
    Older folders without it fall back to the last manifest.
    """
    hashes: dict[str, str] = {}
    try:
        manifest = json.loads((output / "branded-manifest.json").read_text(encoding="utf-8"))
        hashes.update({item["name"]: item["sha256"] for item in manifest.get("outputs", [])})
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    try:
        sidecar = json.loads((output / HASHES).read_text(encoding="utf-8"))
        if isinstance(sidecar, dict):
            hashes.update({str(k): str(v) for k, v in sidecar.items()})
    except (OSError, ValueError):
        pass
    return hashes


def _record_output(output: Path, hashes: dict[str, str], target: Path) -> None:
    hashes[target.name] = _sha256(target)
    atomic_write_bytes(output / HASHES, (json.dumps(hashes, indent=1, sort_keys=True) + "\n").encode("utf-8"))


def write_branded_pack(assessment_dir: Path | str, brand: Brand, *, pdf: bool = True,
                       log: Callable[[str], None] = print) -> dict[str, Path]:
    """Render branded copies of an assessment folder; return the files written."""
    folder = Path(assessment_dir).expanduser().resolve()
    source = folder / "assessment.json"
    if not source.is_file():
        raise ValueError("No assessment.json in the selected folder; choose a completed assessment directory.")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("assessment.json is not an assessment object.")
    output = folder / "branded" / slug(brand.name, "Brand")
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    stem = slug(brand.prepared_for)
    written: dict[str, Path] = {}
    skipped: list[str] = []

    pages = {
        f"{stem}-Cloud-Readiness-Assessment.html": render_branded_report_html(data, brand),
        f"{stem}-Vendor-Questions.html": render_branded_questions_html(data, brand),
    }
    # Markdown documents for the Word and Markdown copies: (file stem, document type, Markdown).
    documents: list[tuple[str, str, str]] = []
    for name, doc_type, stem_suffix in (("report.md", "Cloud Readiness Assessment", "Cloud-Readiness-Assessment"),
                                        ("vendor-questions.md", "Vendor Questions", "Vendor-Questions")):
        if (folder / name).is_file():
            documents.append((f"{stem}-{stem_suffix}", doc_type, (folder / name).read_text(encoding="utf-8-sig")))
    scope_source = folder / SCOPE_OF_WORK
    scope_figures: dict[str, str] = {}
    if scope_source.is_file():
        figures = Figures(data, brand)
        scope_text = figures.fill(scope_source.read_text(encoding="utf-8-sig"))
        scope_figures = figures.used
        pages[f"{stem}-ServiceDesk-Plus-Cloud-Scope-of-Work.html"] = render_scope_html(parse(scope_text), brand)
        documents.append((f"{stem}-ServiceDesk-Plus-Cloud-Scope-of-Work", "Scope of Work", scope_text))
    estimate_source = folder / ESTIMATE
    estimate = None
    if estimate_source.is_file():
        estimate = load_estimate(estimate_source, data, brand)
        estimate_text = estimate_markdown(estimate, brand, data)
        pages[f"{stem}-Effort-Estimate.html"] = render_document_html(
            parse(estimate_text), brand, "Effort Estimate",
            "PERT effort estimate derived from the assessment evidence; the companion workbook recalculates every figure.")
        documents.append((f"{stem}-Effort-Estimate", "Effort Estimate", estimate_text))
    previous = _previous_outputs(output)
    preserved: list[str] = []

    def place(name: str) -> Path:
        """Where to write an output. A deliverable changed since the last run (for example edited in Word or
        Excel) is kept, and the new version is written beside it instead of over it."""
        target = output / name
        try:
            edited = target.is_file() and name in previous and _sha256(target) != previous[name]
        except OSError:
            edited = False  # unreadable now; the write below reports it
        if edited:
            base, _, extension = name.rpartition(".")
            preserved.append(name)
            return output / f"{base}.regenerated.{extension}"
        return target

    def attempt(name: str, write: Callable[[Path], object]) -> Path | None:
        """Write one output; a file that is open or read-only is skipped with a note, not fatal to the pack."""
        target = place(name)
        try:
            write(target)
        except OSError:
            for leftover in output.glob(target.name + ".partial*"):
                leftover.unlink(missing_ok=True)
            skipped.append(f"{target.name}: could not be replaced (is it open in another program?); close it and run again")
            return None
        written[target.name] = target
        _record_output(output, previous, target)
        return target

    html_paths = {name: attempt(name, lambda t, text=text: atomic_write_bytes(t, text.encode("utf-8")))
                  for name, text in pages.items()}

    if pdf:
        browser = find_browser()
        if browser is None:
            skipped.append("PDF: no Edge or Chrome found (set SDP_PDF_BROWSER to a Chromium browser path)")
        else:
            for name, html_path in html_paths.items():
                if html_path is None:
                    continue
                try:
                    attempt(name.replace(".html", ".pdf"), lambda t, h=html_path: print_pdf(h, t, browser))
                except subprocess.SubprocessError:
                    skipped.append("PDF: " + name.replace(".html", ".pdf") + " could not be printed by the local browser")

    for file_stem, doc_type, text in documents:
        attempt(f"{file_stem}.md", lambda t, d=doc_type, x=text: atomic_write_bytes(t, (markdown_header(brand, d) + x).encode("utf-8")))
    try:
        from .branded_docx import write_docx
    except ImportError:
        skipped.append("Word: install python-docx to add editable .docx copies")
    else:
        for file_stem, doc_type, text in documents:
            blocks = parse(text)
            attempt(f"{file_stem}.docx", lambda t, b=blocks, d=doc_type: write_docx(b, brand, document_title(b, d), d, t))

    if estimate is not None:
        try:
            from .estimate_xlsx import write_estimate_workbook
        except ImportError:
            skipped.append("Effort estimate workbook: install openpyxl to add the editable PERT workbook")
        else:
            baseline = f"PERT effort estimate · assessment of {data.get('generated_at', '')[:10]}"
            attempt(f"{stem}-Effort-Estimate.xlsx", lambda t: write_estimate_workbook(estimate, brand, t, baseline))

    findings, coverage = folder / "findings.csv", folder / "coverage.csv"
    if findings.is_file() and coverage.is_file():
        try:
            from .branded_xlsx import write_evidence_workbook
        except ImportError:
            skipped.append("Workbook: install openpyxl to add the branded findings and coverage workbook")
        else:
            attempt(f"{stem}-Assessment-Findings-and-Coverage.xlsx",
                    lambda t: write_evidence_workbook(findings, coverage, t, brand, folder.name))
    else:
        skipped.append("Workbook: findings.csv or coverage.csv is missing")

    sources = [path for path in (source, findings, coverage, folder / "vendor-questions.md",
                                 folder / "report-manifest.json", scope_source, estimate_source) if path.is_file()]
    manifest = {
        "tool_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prepared_by": brand.name,
        "prepared_for": brand.prepared_for,
        "note": "Branded presentation copies. The unbranded files in the parent folder remain the verified evidence.",
        "sources": [{"name": path.name, "sha256": _sha256(path)} for path in sources],
        "outputs": [{"name": name, "sha256": _sha256(path)} for name, path in sorted(written.items())],
        "skipped": skipped,
    }
    if preserved:
        manifest["preserved_edits"] = preserved
    if scope_figures:
        manifest["scope_of_work_figures"] = scope_figures
    if estimate is not None:
        manifest["effort_estimate_hours"] = {key: round(value, 1) for key, value in estimate.totals().items()}
    atomic_write_bytes(output / "branded-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    written["branded-manifest.json"] = output / "branded-manifest.json"
    log("Branded copies (" + brand.name + (", prepared for " + brand.prepared_for if brand.prepared_for else "") + "):")
    for name in sorted(written):
        log("  " + str(written[name]))
    for name in preserved:
        log("  Kept your edited " + name + "; the new version is beside it as .regenerated")
    for note in skipped:
        log("  Skipped " + note)
    return written
