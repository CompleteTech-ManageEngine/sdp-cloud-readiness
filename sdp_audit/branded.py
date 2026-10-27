"""Branded client-ready copies of a finished assessment.

The six verified report files are never modified. Branded copies are written
to ``<assessment>/branded/`` from the assessment's own ``assessment.json``,
``findings.csv`` and ``coverage.csv``:

* ``<Client>-Cloud-Readiness-Assessment.html`` and ``.pdf``
* ``<Client>-Vendor-Questions.html`` and ``.pdf``
* ``<Client>-Assessment-Findings-and-Coverage.xlsx``
* ``branded-manifest.json`` with SHA-256 hashes of sources and outputs

HTML needs only the standard library. PDFs are printed from the branded HTML by
a locally installed Edge or Chrome in headless mode (no network: the pages load
nothing external and the browser runs with networking disabled). The workbook
needs ``openpyxl``. A missing optional tool is reported and skipped; it never
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
from .branding import Brand, slug
from .report import render_branded_questions_html, render_branded_report_html

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
    output = folder / "branded"
    output.mkdir(mode=0o700, exist_ok=True)
    stem = slug(brand.prepared_for)
    written: dict[str, Path] = {}
    skipped: list[str] = []

    pages = {
        f"{stem}-Cloud-Readiness-Assessment.html": render_branded_report_html(data, brand),
        f"{stem}-Vendor-Questions.html": render_branded_questions_html(data, brand),
    }
    for name, text in pages.items():
        atomic_write_bytes(output / name, text.encode("utf-8"))
        written[name] = output / name

    if pdf:
        browser = find_browser()
        if browser is None:
            skipped.append("PDF: no Edge or Chrome found (set SDP_PDF_BROWSER to a Chromium browser path)")
        else:
            for name in pages:
                target = output / name.replace(".html", ".pdf")
                try:
                    print_pdf(output / name, target, browser)
                    written[target.name] = target
                except (OSError, subprocess.SubprocessError):
                    skipped.append("PDF: " + target.name + " could not be printed by the local browser")

    findings, coverage = folder / "findings.csv", folder / "coverage.csv"
    if findings.is_file() and coverage.is_file():
        try:
            from .branded_xlsx import write_evidence_workbook
        except ImportError:
            skipped.append("Workbook: install openpyxl to add the branded findings and coverage workbook")
        else:
            target = output / f"{stem}-Assessment-Findings-and-Coverage.xlsx"
            write_evidence_workbook(findings, coverage, target, brand, folder.name)
            written[target.name] = target
    else:
        skipped.append("Workbook: findings.csv or coverage.csv is missing")

    sources = [path for path in (source, findings, coverage, folder / "vendor-questions.md",
                                 folder / "report-manifest.json") if path.is_file()]
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
    atomic_write_bytes(output / "branded-manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    written["branded-manifest.json"] = output / "branded-manifest.json"
    log("Branded copies (" + brand.name + (", prepared for " + brand.prepared_for if brand.prepared_for else "") + "):")
    for name in sorted(written):
        log("  " + str(written[name]))
    for note in skipped:
        log("  Skipped " + note)
    return written
