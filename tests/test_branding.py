"""Operator brand files and branded copies; uses a fictional brand and a generated PNG."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from sdp_audit.branded import write_branded_pack
from sdp_audit.branding import load_brand, slug
from sdp_audit.cli import main
from sdp_audit.report import render_branded_questions_html, render_branded_report_html, render_report_documents
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.synthetic import demo_environment


def _png(width: int = 30, height: int = 10) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\0" + b"\x10\x20\x30" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


SKILL_LAYOUT = {
    "company": {"name": "Fictional Advisory", "website": "fictional.example", "email": "hello@fictional.example",
                "tagline": "Synthetic test identity"},
    "logo": "assets/mark.png",
    "themes": {"light": {"band": "#102030", "accent": "#AA0000", "accent_2": "#00AACC", "ink": "#111111"},
               "dark": {"band": "#000000"}},
}


class BrandFileTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "assets").mkdir()
        (self.root / "assets/mark.png").write_bytes(_png())
        (self.root / "templates").mkdir()
        self.brand_file = self.root / "templates/branding.fictional.json"
        self.brand_file.write_text(json.dumps(SKILL_LAYOUT), encoding="utf-8")

    def test_skill_layout_resolves_logo_from_parent_and_palette(self):
        brand = load_brand(self.brand_file, "Client <One>")
        self.assertEqual(brand.name, "Fictional Advisory")
        self.assertEqual(brand.logo_size, (30, 10))
        self.assertEqual(brand.logo_mime, "image/png")
        self.assertEqual(brand.tokens["band"], "#102030")
        self.assertEqual(brand.tokens["line"], "#E2E8F0")
        self.assertEqual(brand.hex("accent"), "AA0000")

    def test_flat_layout_without_logo(self):
        flat = self.root / "flat.json"
        flat.write_text(json.dumps({"name": "Plain Co", "light": {"accent": "123456"}}), encoding="utf-8")
        brand = load_brand(flat)
        self.assertEqual((brand.name, brand.logo, brand.tokens["accent"]), ("Plain Co", b"", "#123456"))

    def test_rejects_remote_logo_bad_colour_and_missing_name(self):
        for change in ({"logo": "https://example.invalid/logo.png"}, {"logo": "data:image/png;base64,AAAA"},
                       {"themes": {"light": {"accent": "red"}}}, {"company": {"website": "x"}},
                       {"logo": "assets/missing.png"}):
            with self.subTest(change=change):
                self.brand_file.write_text(json.dumps({**SKILL_LAYOUT, **change}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_brand(self.brand_file)

    def test_slug(self):
        self.assertEqual(slug("Northwind Health, Inc."), "Northwind-Health-Inc")
        self.assertEqual(slug(""), "Assessment")


class BrandedRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        (root / "mark.png").write_bytes(_png())
        (root / "brand.json").write_text(json.dumps({**SKILL_LAYOUT, "logo": "mark.png"}), encoding="utf-8")
        cls.brand = load_brand(root / "brand.json", "Client <One>")
        cls.documents = render_report_documents(analyze_environment(demo_environment("multi")))
        cls.data = json.loads(cls.documents["assessment.json"])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_unbranded_reports_are_unchanged_and_carry_no_identity(self):
        html = self.documents["report.html"]
        self.assertNotIn("brand-band", html)
        self.assertIn("img-src 'none'", html)

    def test_branded_report_keeps_offline_csp_and_escapes_client(self):
        for page in (render_branded_report_html(self.data, self.brand), render_branded_questions_html(self.data, self.brand)):
            self.assertIn("img-src data:", page)
            self.assertIn("script-src 'none'", page)
            self.assertIn("connect-src 'none'", page)
            self.assertNotIn("<script", page.lower())
            self.assertIn('class="brand-band"', page)
            self.assertIn("Client &lt;One&gt;", page)
            self.assertNotIn("Client <One>", page)
            self.assertIn("Fictional Advisory", page)
            self.assertIn("--accent:#AA0000", page)

    def test_branded_report_preserves_every_unbranded_section(self):
        page = render_branded_report_html(self.data, self.brand)
        start = self.documents["report.html"].index("<header>")
        end = self.documents["report.html"].rindex("<footer>")
        self.assertIn(self.documents["report.html"][start:end], page)

    def test_pack_writes_html_manifest_and_optional_workbook(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name, text in self.documents.items():
                (folder / name).write_text(text, encoding="utf-8")
            written = write_branded_pack(folder, self.brand, pdf=False, log=lambda _: None)
            self.assertIn("Client-One-Cloud-Readiness-Assessment.html", written)
            self.assertIn("Client-One-Vendor-Questions.html", written)
            manifest = json.loads((folder / "branded/branded-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["prepared_for"], "Client <One>")
            self.assertIn("assessment.json", [item["name"] for item in manifest["sources"]])
            self.assertEqual(self.documents["report.html"], (folder / "report.html").read_text(encoding="utf-8"))
            if importlib.util.find_spec("openpyxl"):
                import openpyxl
                book = openpyxl.load_workbook(written["Client-One-Assessment-Findings-and-Coverage.xlsx"])
                self.assertEqual(book.sheetnames, ["Cover", "Findings", "Coverage"])
            else:
                self.assertTrue(any("openpyxl" in note for note in manifest["skipped"]))

    def test_cli_brand_assessment_requires_brand_file(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(main(["--no-env", "--quiet", "--brand-assessment", directory]), 1)
