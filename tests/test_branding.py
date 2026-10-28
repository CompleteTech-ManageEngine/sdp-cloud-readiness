"""Operator brand files and branded copies; uses a fictional brand and a generated PNG."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
import unittest.mock
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
            manifest = json.loads((folder / "branded/Fictional-Advisory/branded-manifest.json").read_text(encoding="utf-8"))
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


class PresetTests(unittest.TestCase):
    def test_completetech_preset_resolves_with_local_logo_and_tile(self):
        from sdp_audit.branding import html_css, resolve_brand_path
        from sdp_audit.local_env import application_directory
        path = resolve_brand_path("completetech", application_directory())
        self.assertEqual(path.name, "branding.completetech.json")
        brand = load_brand(path, "Client")
        self.assertEqual(brand.name, "CompleteTech LLC")
        self.assertEqual(brand.logo_mime, "image/png")
        self.assertEqual(brand.tokens["accent"], "#1E3A8A")
        self.assertIn("background:#F8FAFC", html_css(brand))

    def test_unknown_preset_and_none(self):
        from sdp_audit.branding import resolve_brand_path
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                resolve_brand_path("no-such-brand", Path(directory))
            self.assertEqual(main(["--no-env", "--quiet", "--brand", "none", "--brand-assessment", directory]), 1)

    def test_entry_point_default_brand_applies_and_library_main_is_unbranded(self):
        import argparse
        from sdp_audit import cli
        from sdp_audit.branding import resolve_brand_path
        from sdp_audit.local_env import application_directory
        expected = load_brand(resolve_brand_path(cli.DEFAULT_BRAND, application_directory())).name
        args = argparse.Namespace(brand=None, prepared_for=None, brand_assessment=None)
        with unittest.mock.patch.dict("os.environ", {"SDP_BRAND_FILE": "", "SDP_PREPARED_FOR": ""}):
            self.assertIsNone(cli._brand(args))
            with unittest.mock.patch.object(cli, "_default_brand", cli.DEFAULT_BRAND):
                self.assertEqual(cli._brand(args).name, expected)
                self.assertIsNone(cli._brand(argparse.Namespace(brand="none", prepared_for=None, brand_assessment=None)))


class RerunSafetyTests(unittest.TestCase):
    """Re-running must not destroy a deliverable the consultant edited, nor stop on a file open in Word/Excel."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        for name, text in render_report_documents(analyze_environment(demo_environment("multi"))).items():
            (self.folder / name).write_text(text, encoding="utf-8")
        from sdp_audit.branding import Brand
        self.brand = Brand(name="Fictional Advisory", prepared_for="Client")
        self.out = self.folder / "branded" / "Fictional-Advisory"

    def test_edited_deliverable_is_kept_and_new_version_written_beside_it(self):
        write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        edited = self.out / "Client-Vendor-Questions.md"
        edited.write_text("consultant edits", encoding="utf-8")
        written = write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        self.assertEqual(edited.read_text(encoding="utf-8"), "consultant edits")
        self.assertIn("Client-Vendor-Questions.regenerated.md", written)
        manifest = json.loads((self.out / "branded-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["preserved_edits"], ["Client-Vendor-Questions.md"])
        unchanged = (self.out / "Client-Cloud-Readiness-Assessment.md").read_text(encoding="utf-8")
        self.assertTrue(unchanged.startswith("**Fictional Advisory**"))

    def test_locked_file_is_skipped_and_the_rest_is_written(self):
        from sdp_audit import artifacts
        original = artifacts.atomic_write_bytes

        def locked(destination, contents):
            if destination.name == "Client-Vendor-Questions.html":
                raise PermissionError(13, "in use")
            return original(destination, contents)

        with unittest.mock.patch("sdp_audit.branded.atomic_write_bytes", side_effect=locked):
            written = write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        self.assertNotIn("Client-Vendor-Questions.html", written)
        self.assertIn("Client-Cloud-Readiness-Assessment.html", written)
        manifest = json.loads((self.out / "branded-manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(any("Client-Vendor-Questions.html" in note and "open in another program" in note
                            for note in manifest["skipped"]))
        self.assertFalse(list(self.out.glob("*.partial*")))

    def test_interrupted_run_does_not_make_own_files_look_edited(self):
        write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        with unittest.mock.patch("sdp_audit.branded.markdown_header", side_effect=RuntimeError("interrupted")):
            # New evidence changes the HTML, which is rewritten before the run stops; no manifest is written for it.
            data = json.loads((self.folder / "assessment.json").read_text(encoding="utf-8"))
            data["generated_at"] = "2026-10-08T12:00:00+00:00"
            (self.folder / "assessment.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        write_branded_pack(self.folder, self.brand, pdf=False, log=lambda _: None)
        manifest = json.loads((self.out / "branded-manifest.json").read_text(encoding="utf-8"))
        self.assertNotIn("preserved_edits", manifest)
        self.assertFalse(list(self.out.glob("*.regenerated.*")))


class PdfPathTests(unittest.TestCase):
    @unittest.skipUnless(__import__("sdp_audit.branded", fromlist=["find_browser"]).find_browser(), "no Chromium browser")
    def test_prints_from_deep_folders(self):
        """A 265-character path (Windows long paths enabled) that Chromium could not open: the failure seen in use."""
        from sdp_audit.branded import find_browser, print_pdf
        with tempfile.TemporaryDirectory() as directory:
            deep = Path(directory)
            while len(str(deep)) < 240:
                deep = deep / "long-folder-name"
            source = deep / ("p" * max(1, 260 - len(str(deep))) + ".html")
            try:
                deep.mkdir(parents=True)
                source.write_text("<!doctype html><html><body><p>Deep folder</p></body></html>", encoding="utf-8")
            except OSError:
                self.skipTest("Windows long paths are not enabled on this machine")
            target = source.with_suffix(".pdf")
            print_pdf(source, target, find_browser())
            self.assertEqual(target.read_bytes()[:5], b"%PDF-")
