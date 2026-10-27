"""Bounded packaging gates for the portable, deterministic distribution."""

from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
import zipfile

from sdp_audit import __version__
from tools.build_release import BASE_FILES, PATTERNS, STAMP, build


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.work = Path(cls.temporary.name)
        cls.stage = cls.work / "source"
        cls.stage.mkdir()
        paths = {ROOT / name for name in BASE_FILES}
        for pattern in PATTERNS:
            paths.update(path for path in ROOT.glob(pattern) if path.is_file())
        for source in paths:
            destination = cls.stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        # Packaging tests need a deterministic safe example, not a report
        # generated during another test or a customer assessment on disk.
        example = cls.stage / "examples/synthetic-assessment/report.html"
        example.write_text("<!doctype html><title>Synthetic packaging fixture</title><p>No source data.</p>\n", encoding="utf-8")
        cls.private_marker = "PRIVATE_REPORT_" + uuid.uuid4().hex
        private = cls.stage / "sdp-assessments/customer-readiness/private"
        private.mkdir(parents=True)
        (private / "assessment.json").write_text(json.dumps({"secret": cls.private_marker}), encoding="utf-8")
        (cls.stage / ".env").write_text("SDP_API_KEY=" + cls.private_marker, encoding="utf-8")
        for folder in (cls.stage, cls.stage / "examples/synthetic-assessment", cls.stage / "examples/recovery-assessment"):
            (folder / ".env.customer").write_text("SDP_API_KEY=" + cls.private_marker, encoding="utf-8")
        (cls.stage / "examples/synthetic-assessment/.env").write_text(cls.private_marker, encoding="utf-8")
        (cls.stage / "examples/synthetic-assessment/credentials.env").write_text(cls.private_marker, encoding="utf-8")
        cache = cls.stage / "sdp_audit/__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "private.pyc").write_bytes(cls.private_marker.encode("ascii"))
        with contextlib.redirect_stdout(io.StringIO()):
            cls.first = build(cls.stage, cls.work / "build-one")
            # Filesystem timestamps never contribute to the deterministic ZIP.
            os.utime(cls.stage / "README.md", (1000000000, 1000000000))
            cls.second = build(cls.stage, cls.work / "build-two")
        cls.runtime = cls.work / "isolated-runtime"
        cls.runtime.mkdir()
        cls.portable = cls.runtime / "standalone.pyz"
        shutil.copyfile(cls.first["sdp_cloud_readiness.pyz"], cls.portable)

    def invoke(self, *arguments):
        environment = {key: value for key, value in os.environ.items()
                       if not key.upper().startswith("SDP_") and key not in {"PYTHONPATH", "PYTHONHOME"}}
        environment["PYTHONPATH"] = str(self.work / "nonexistent-import-path")
        result = subprocess.run([sys.executable, "-I", str(self.portable), *arguments],
                                cwd=self.runtime, env=environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=45, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_archive_and_zipapp_are_reproducible(self):
        for name in ("sdp_cloud_readiness.pyz", "sdp-cloud-readiness.zip", "SHA256SUMS.txt"):
            with self.subTest(name=name):
                self.assertEqual(self.first[name].read_bytes(), self.second[name].read_bytes())

    def test_outer_sha256_manifest_covers_every_published_artifact(self):
        lines = self.first["SHA256SUMS.txt"].read_text(encoding="utf-8").splitlines()
        entries = dict(line.split("  ", 1)[::-1] for line in lines)
        self.assertEqual(set(entries), set(self.first) - {"SHA256SUMS.txt"})
        for name, digest in entries.items():
            self.assertEqual(hashlib.sha256(self.first[name].read_bytes()).hexdigest(), digest)

    def test_distribution_contains_source_docs_fixtures_launcher_and_inner_manifest(self):
        prefix = "sdp-cloud-readiness/"
        with zipfile.ZipFile(self.first["sdp-cloud-readiness.zip"]) as archive:
            names = set(archive.namelist())
            required = {
                "sdp_cloud_readiness.py", "sdp_cloud_readiness.pyz", "__main__.py",
                "sdp_audit/cli.py", "sdp_audit/environment.py", "sdp_audit/fields.py", "sdp_audit/transport.py",
                "Run-Assessment.cmd", "Run-All-Portals.cmd", "README.md", "examples/config/connection.example.json", "examples/config/answers.example.json",
                "examples/config/portals.example.json", "sdp_audit/portal_scope.py", "docs/guides/all-portals.md", "tests/test_multiportal_run.py",
                "tests/fixtures/recovery.json",
                "sdp_audit/credentials.py", "sdp_audit/artifacts.py", "sdp_audit/diagnostics.py",
                "docs/guides/troubleshooting.md", "tests/test_startup_and_publication.py", "docs/guides/windows-key-input.md", "tests/test_credentials.py", "tests/test_credentials_gui.py",
                "CHANGELOG.md", "docs/reference/topology.md", "docs/reference/fields.md",
                "tests/test_fields.py", "tests/test_environment_safety.py", "tests/test_release.py",
                "tests/fixtures/single.json", "tests/fixtures/multi.json", "tests/fixtures/udf_primary.json",
                "tests/fixtures/udf_fallback.json", "tools/build_release.py",
                "examples/synthetic-assessment/report.html", "SHA256SUMS.txt",
                "CONTRIBUTING.md", "docs/README.md", "docs/guides/usage.md",
                "docs/development/validation.md", "docs/development/release-verification.md",
                "docs/reference/api-catalog.md", "docs/reference/diagnostics-and-coverage.md",
                "docs/releases/2.1.1.md", "docs/releases/2.1.2.md", "examples/config/README.md",
                "sdp_audit/credential_setup.py", "examples/config/credentials.example.json",
                "docs/guides/multiple-credentials.md", "docs/reference/multi-key-authorization.md",
                "docs/releases/2.2.0.md", "tests/test_multi_credentials.py",
                ".env.example", "sdp_audit/local_env.py", "tests/test_local_env.py",
            }
            self.assertTrue({prefix + name for name in required}.issubset(names))
            self.assertTrue(all(name.startswith(prefix) and ".." not in Path(name).parts for name in names))
            hashes = dict(line.split("  ", 1)[::-1]
                          for line in archive.read(prefix + "SHA256SUMS.txt").decode("utf-8").splitlines())
            self.assertEqual({prefix + name for name in hashes}, names - {prefix + "SHA256SUMS.txt"})
            for name, digest in hashes.items():
                self.assertEqual(hashlib.sha256(archive.read(prefix + name)).hexdigest(), digest)
            self.assertEqual(archive.read(prefix + "sdp_cloud_readiness.pyz"), self.first["sdp_cloud_readiness.pyz"].read_bytes())

    def test_all_portals_launcher_adds_scope_flag_and_forwards_arguments(self):
        raw = (ROOT / "Run-All-Portals.cmd").read_bytes()
        self.assertIn(b"\r\n", raw)
        text = raw.decode("ascii")
        self.assertIn('call "%~dp0Run-Assessment.cmd" --all-portals %*', text)
        self.assertIn('DisableDelayedExpansion', text)
        self.assertNotIn('SDP_API_KEY', text)
        self.assertNotIn('for /', text.casefold())

    def test_portable_recovery_demo_has_all_four_selected_portals(self):
        folder = self.runtime / "recovery-output"
        self.invoke("--demo", "--demo-scenario", "recovery", "--output-dir", str(folder))
        report = next(folder.glob("*/assessment.json"))
        document = json.loads(report.read_text())
        self.assertEqual(len(document["portals"]), 4)
        self.assertEqual(document["environment"]["topology"]["mode"], "assisted")
        self.assertFalse(document["environment"]["topology"]["complete"])
        self.assertEqual(len(document["questions"]), 7)

    def test_portable_multi_key_demo_uses_separate_scopes_without_secrets(self):
        folder = self.runtime / "multi-key-output"
        self.invoke("--demo", "--demo-scenario", "multi_key", "--output-dir", str(folder))
        report = next(folder.glob("*/assessment.json"))
        document = json.loads(report.read_text())
        scopes = document["environment"]["permissions"]["credential_scopes"]
        self.assertEqual(len(scopes), 6)
        self.assertEqual(next(row["status"] for row in scopes if row["scope"] == "global"), "valid")
        for path in report.parent.iterdir():
            if path.suffix in {".json", ".html", ".md", ".csv"}:
                self.assertNotIn("synthetic-portal-key-", path.read_text(encoding="utf-8"))
                self.assertNotIn("synthetic-org-key", path.read_text(encoding="utf-8"))


    def test_customer_reports_environment_files_and_caches_are_excluded(self):
        for artifact in ("sdp-cloud-readiness.zip", "sdp_cloud_readiness.pyz"):
            with self.subTest(artifact=artifact), zipfile.ZipFile(self.first[artifact]) as archive:
                for member in archive.infolist():
                    self.assertNotIn("sdp-assessments/", member.filename)
                    self.assertNotIn("__pycache__/", member.filename)
                    self.assertFalse(member.filename.lower().endswith(".env"))
                    self.assertFalse(Path(member.filename).name.startswith(".env.") and not member.filename.endswith("/.env.example"))
                    self.assertNotIn(self.private_marker.encode("ascii"), archive.read(member))
                    self.assertEqual(member.date_time, STAMP)

    def test_filled_environment_example_cannot_be_packaged(self):
        target = self.stage / ".env.example"
        original = target.read_bytes()
        try:
            target.write_text("SDP_API_KEY=" + self.private_marker, encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                build(self.stage, self.work / "reject-filled-example")
            self.assertNotIn(self.private_marker, str(caught.exception))
        finally:
            target.write_bytes(original)

    def test_zipapp_is_self_contained_and_has_only_runtime_python_members(self):
        with zipfile.ZipFile(self.portable) as archive:
            names = archive.namelist()
            self.assertIn("__main__.py", names)
            self.assertIn("sdp_audit/synthetic.py", names)
            self.assertTrue(all(name == "__main__.py" or name.startswith("sdp_audit/") and name.endswith(".py") for name in names))
            self.assertNotIn("tests/fixtures/multi.json", names)
        version = self.invoke("--version")
        self.assertEqual(version.stdout.strip(), __version__)
        self.assertEqual(version.stderr, "")
        help_result = self.invoke("--help")
        for option in ("--portal-id", "--portal-ids", "--metadata-limit", "--source-build", "--max-requests", "--demo", "--key-input", "--check-key-input", "--check-output", "--diagnose"):
            self.assertIn(option, help_result.stdout)
        self.assertNotIn("Traceback", help_result.stderr)

    def test_standalone_demo_builds_all_report_formats_without_source_tree_or_credentials(self):
        output = self.runtime / "offline-demo"
        result = self.invoke("--demo", "--quiet", "--output-dir", str(output))
        folders = [path for path in output.glob("assessment-*") if path.is_dir()]
        self.assertEqual(len(folders), 1)
        expected = {"report.html", "report.md", "assessment.json", "coverage.csv", "findings.csv", "vendor-questions.md"}
        self.assertTrue(expected.issubset({path.name for path in folders[0].iterdir()}))
        assessment = json.loads((folders[0] / "assessment.json").read_text(encoding="utf-8"))
        self.assertEqual(assessment.get("schema_version"), "2.0")
        self.assertEqual(len(assessment.get("portals", [])), 4)
        self.assertIn("Assessment written", result.stdout)
        self.assertNotIn("API key (hidden", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_python_310_syntax_and_stdlib_only_runtime_imports(self):
        runtime_paths = [self.stage / "__main__.py", self.stage / "sdp_cloud_readiness.py"]
        runtime_paths.extend(sorted((self.stage / "sdp_audit").glob("*.py")))
        allowed = set(sys.stdlib_module_names) | {"sdp_audit"}
        # The branded workbook is optional: only this module may import openpyxl,
        # and branded.py imports it behind an ImportError guard.
        optional = {"branded_xlsx.py": {"openpyxl"}}
        # A module existing only in newer Python cannot satisfy the 3.10 floor.
        unavailable_in_310 = {"tomllib", "annotationlib", "compression", "_interpreters", "interpreters"}
        for path in runtime_paths:
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=path.name, feature_version=(3, 10))
                for node in ast.walk(tree):
                    imports = []
                    if isinstance(node, ast.Import):
                        imports = [alias.name.split(".", 1)[0] for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                        imports = [node.module.split(".", 1)[0]]
                    for imported in imports:
                        self.assertIn(imported, allowed | optional.get(path.name, set()), f"Non-standard runtime import {imported} in {path.name}")
                        self.assertNotIn(imported, unavailable_in_310)
        guarded = (self.stage / "sdp_audit" / "branded.py").read_text(encoding="utf-8")
        self.assertIn("from .branded_xlsx import write_evidence_workbook\n        except ImportError:", guarded)


    def test_portable_local_key_check_is_offline_and_secret_safe(self):
        canary = "SYNTHETIC-PORTABLE-KEY-INPUT-1234"
        environment = {key: value for key, value in os.environ.items()
                       if not key.upper().startswith("SDP_") and key not in {"PYTHONPATH", "PYTHONHOME"}}
        environment["SDP_API_KEY"] = canary
        target = self.runtime / "must-not-create-local-check"
        result = subprocess.run([sys.executable, "-I", str(self.portable), "--check-key-input", "--output-dir", str(target)],
                                cwd=self.runtime, env=environment, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("authentication was NOT tested", result.stdout)
        self.assertNotIn(canary, result.stdout + result.stderr)
        self.assertFalse(target.exists())

    def test_windows_launcher_prefers_self_contained_runner(self):
        launcher = self.first["Run-Assessment.cmd"].read_text(encoding="utf-8")
        self.assertIn('set "SDP_ASSESSMENT_ENTRY=sdp_cloud_readiness.pyz"', launcher)
        self.assertIn('if not exist "%SDP_ASSESSMENT_ENTRY%" set "SDP_ASSESSMENT_ENTRY=sdp_cloud_readiness.py"', launcher)
        self.assertIn("setlocal DisableDelayedExpansion", launcher)

    def test_windows_launcher_supports_extracted_and_portable_entrypoints(self):
        launcher = self.first["Run-Assessment.cmd"].read_text(encoding="utf-8")
        self.assertIn('cd /d "%~dp0"', launcher)
        self.assertIn("sdp_cloud_readiness.py", launcher)
        self.assertIn("sdp_cloud_readiness.pyz", launcher)
        self.assertIn("py -3", launcher)
        self.assertIn("python ", launcher)
        self.assertIn("%*", launcher)
        self.assertIn("%ERRORLEVEL%", launcher)


if __name__ == "__main__":
    unittest.main()
