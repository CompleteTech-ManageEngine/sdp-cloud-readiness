"""Local setup, literal parsing and real CLI routing with synthetic transport."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from sdp_audit.cli import main
from sdp_audit.credential_setup import CredentialSetup
from sdp_audit.local_env import local_environment, parse_env, scaffold, slot_assignments
from sdp_audit.synthetic import SYNTHETIC_HOST as HOST, create_synthetic_client
from tools.build_release import build

ROOT = Path(__file__).resolve().parents[1]
KEY1, KEY2 = "synthetic-dotenv-key-one+/=", "synthetic-dotenv-key-two+/="


class LocalEnvTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / ".env"
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def write(self, text):
        self.path.write_text(text, encoding="utf-8")
        return str(self.path)

    def values(self, extra=""):
        return (f"SDP_HOST={HOST}\nSDP_INSTANCE_01_PORTAL_ID=1\n"
                f"SDP_INSTANCE_01_API_KEY={KEY1}\n" + extra)

    def run_cli(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = main(args)
        return code, output.getvalue()

    def test_template_has_twenty_blank_pairs_and_separate_credentials(self):
        self.write(scaffold())
        values = parse_env(self.path)
        self.assertEqual(len(values), 47)
        self.assertIn("SDP_BRAND_FILE", values)
        self.assertIn("SDP_PREPARED_FOR", values)
        self.assertTrue(all(value == "" for value in values.values()))
        for i in range(1, 21):
            self.assertIn(f"SDP_INSTANCE_{i:02d}_PORTAL_ID", values)
            self.assertIn(f"SDP_INSTANCE_{i:02d}_API_KEY", values)
        self.assertEqual((ROOT / ".env.example").read_text(), scaffold())

    def test_default_scaffold_is_exclusive_and_preserves_existing_file(self):
        with patch("sdp_audit.local_env.application_directory", return_value=self.root):
            with local_environment():
                self.assertTrue(self.path.exists())
            self.write(self.values())
            before = self.path.read_bytes()
            with local_environment():
                self.assertEqual(os.environ["SDP_INSTANCE_01_API_KEY"], KEY1)
            self.assertEqual(self.path.read_bytes(), before)
            self.assertNotIn("SDP_INSTANCE_01_API_KEY", os.environ)

    def test_no_parent_search(self):
        self.write("INVALID INPUT")
        child = self.root / "application"
        child.mkdir()
        with patch("sdp_audit.local_env.application_directory", return_value=child):
            with local_environment():
                self.assertNotIn("INVALID", os.environ)
        self.assertEqual((child / ".env").read_text(), scaffold())

    def test_override_opt_out_and_missing_explicit_file(self):
        path = self.write(self.values())
        with local_environment(path):
            self.assertEqual(os.environ["SDP_HOST"], HOST)
        with local_environment(path, disabled=True):
            self.assertEqual(dict(os.environ), {})
        with self.assertRaises(OSError):
            with local_environment(str(self.root / "missing")):
                pass
        self.assertFalse((self.root / "missing").exists())

    def test_process_environment_including_empty_values_wins_and_restores(self):
        self.write(self.values())
        os.environ.update(SDP_INSTANCE_01_API_KEY=KEY2, SDP_API_KEY="")
        with local_environment(str(self.path)):
            self.assertEqual(os.environ["SDP_INSTANCE_01_API_KEY"], KEY2)
            self.assertEqual(os.environ["SDP_API_KEY"], "")
        self.assertEqual(dict(os.environ), {"SDP_INSTANCE_01_API_KEY": KEY2, "SDP_API_KEY": ""})

    def test_cleanup_on_failure(self):
        self.write(self.values())
        with self.assertRaises(RuntimeError):
            with local_environment(str(self.path)):
                raise RuntimeError
        self.assertEqual(dict(os.environ), {})

    def test_literals_quotes_comments_and_redacted_repr(self):
        self.write('A="x # y" # comment\nB=plain#hash\nC=two # comment\n'
                   "D='$(echo secret)'\nE=${NOT_EXPANDED}\nF=`whoami`\nG= # blank\n")
        data = parse_env(self.path)
        self.assertEqual(dict(data), {"A": "x # y", "B": "plain#hash", "C": "two",
                                     "D": "$(echo secret)", "E": "${NOT_EXPANDED}",
                                     "F": "`whoami`", "G": ""})
        self.assertNotIn("secret", repr(data))

    def test_malformed_inputs_never_echo_secret(self):
        for text in (f"{KEY1}\n", f"A={KEY1}\nA=again", f"A='{KEY1}",
                     f'A="{KEY1}" trailing', f"export A={KEY1}",
                     f"A={KEY1}\x00", "A=" + "x" * 8193):
            with self.subTest(text=text[:10]):
                self.write(text)
                with self.assertRaises(ValueError) as caught:
                    parse_env(self.path)
                self.assertNotIn(KEY1, str(caught.exception))

    def test_file_size_line_and_encoding_bounds(self):
        for content in (b"x" * (1024 * 1024 + 1), b"\n" * 10001, b"A=\xff"):
            self.path.write_bytes(content)
            with self.assertRaises(ValueError):
                parse_env(self.path)

    def test_all_twenty_slots_and_additional_slot(self):
        os.environ["SDP_HOST"] = HOST
        for i in range(1, 22):
            os.environ[f"SDP_INSTANCE_{i:02d}_PORTAL_ID"] = str(100 + i)
            os.environ[f"SDP_INSTANCE_{i:02d}_API_KEY"] = f"synthetic-slot-key-{i}"
        entries = slot_assignments(HOST)
        self.assertEqual([e["id"] for e in entries], [str(100 + i) for i in range(1, 22)])
        client, _, _ = create_synthetic_client(multi_key=True)
        setup = CredentialSetup(client, slot_entries=entries, non_interactive=True)
        self.assertEqual(len(client._portal_keys), 21)
        self.assertNotIn("synthetic-slot-key", repr(setup))

    def test_blank_and_partial_slots(self):
        self.write(scaffold() + "\n")
        with local_environment(str(self.path)):
            self.assertEqual(slot_assignments(HOST), [])
        os.environ.update(SDP_HOST=HOST, SDP_INSTANCE_07_PORTAL_ID="42")
        entries = slot_assignments(HOST)
        client, _, _ = create_synthetic_client(multi_key=True)
        with patch("sys.stdin.isatty", return_value=True):
            setup = CredentialSetup(client, slot_entries=entries)
        from sdp_audit.topology import discover_topology
        topology = discover_topology(client, portal_ids=["42"])
        with patch("builtins.input", side_effect=AssertionError("Must remain unassessed")):
            setup.resolve(topology)
        self.assertEqual(client.credential_status("42"), "missing")

    def test_key_without_id_duplicate_ids_and_alias_slots_fail(self):
        for values in ({"SDP_INSTANCE_01_API_KEY": KEY1},
                       {"SDP_INSTANCE_01_PORTAL_ID": "7", "SDP_INSTANCE_02_PORTAL_ID": "007"},
                       {"SDP_INSTANCE_01_PORTAL_ID": "7", "SDP_INSTANCE_001_PORTAL_ID": "8"},
                       {"SDP_INSTANCE_01_PORTAL_ID": "7", "SDP_INSTANCE_001_API_KEY": KEY1},
                       {"SDP_INSTANCE_00_PORTAL_ID": "7"},
                       {"SDP_INSTANCE_01_PORTAL_ID": KEY1}):
            with patch.dict(os.environ, {"SDP_HOST": HOST, **values}, clear=True):
                with self.assertRaises(ValueError) as caught:
                    slot_assignments(HOST)
                self.assertNotIn(KEY1, str(caught.exception))

    def test_host_binding_covers_context_and_process_override(self):
        self.write(self.values())
        for host in (HOST + "/other", "https://other.invalid"):
            with local_environment(str(self.path)) as file_host:
                with self.assertRaises(ValueError):
                    slot_assignments(host, file_host=file_host)
            with patch.dict(os.environ, {"SDP_HOST": host}):
                with local_environment(str(self.path)) as file_host:
                    with self.assertRaises(ValueError):
                        slot_assignments(host, file_host=file_host)
        self.write(f"SDP_INSTANCE_01_PORTAL_ID=1\nSDP_INSTANCE_01_API_KEY={KEY1}")
        with self.assertRaises(ValueError):
            with local_environment(str(self.path)):
                pass

    def test_json_duplicate_assignment_rejected(self):
        self.write(self.values())
        profile = self.root / "credentials.json"
        profile.write_text(json.dumps({"schema_version": 1, "host": HOST,
            "portals": [{"id": "1", "env": "SDP_INSTANCE_01_API_KEY"}]}))
        client, _, _ = create_synthetic_client(multi_key=True)
        with local_environment(str(self.path)):
            with self.assertRaises(ValueError):
                CredentialSetup(client, path=str(profile), slot_entries=slot_assignments(HOST))

    def test_two_slots_route_correctly_and_publish_without_secrets(self):
        # Slots 03 and 19 explicitly bind real fixture IDs 1 and 2.
        self.write(f"SDP_HOST={HOST}\nSDP_INSTANCE_03_PORTAL_ID=1\n"
                   f"SDP_INSTANCE_03_API_KEY={KEY1}\nSDP_INSTANCE_19_PORTAL_ID=2\n"
                   f"SDP_INSTANCE_19_API_KEY={KEY2}\nSDP_INSTANCE_20_PORTAL_ID=3\n"
                   "SDP_INSTANCE_20_API_KEY=\nSDP_INSTANCE_02_PORTAL_ID=\nSDP_INSTANCE_02_API_KEY=\n")
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        received = []
        original_open = server.open
        def record(request, timeout):
            received.append((request.get_header("Portalid"), request.get_header("Authtoken")))
            return original_open(request, timeout)
        server.open = record
        with patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             patch("builtins.input", side_effect=AssertionError("Unexpected prompt")):
            code, output = self.run_cli(["--env-file", str(self.path), "--non-interactive", "--quiet",
                                        "--modules", "requests,orgusers", "--output-dir", str(self.root / "reports")])
        self.assertEqual(code, 0, output)
        self.assertEqual(set(received), {("1", KEY1), ("2", KEY2)})
        self.assertIn("Discovery skipped: no discovery key set; scope comes from numbered slots", output)
        report = next(self.root.glob("reports/*/assessment.json"))
        document = json.loads(report.read_text())
        self.assertEqual({p["portal_id"] for p in document["portals"]}, {"1", "2", "3"})
        self.assertIn("CREDENTIAL_MISSING", report.read_text())
        for secret in (KEY1, KEY2):
            self.assertNotIn(secret, output)
            for path in report.parent.iterdir():
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as archive:
                        for name in archive.namelist():
                            self.assertNotIn(secret.encode(), archive.read(name))
                else:
                    self.assertNotIn(secret.encode(), path.read_bytes())

    def test_conflicting_global_directory_and_prompt_inputs_fail_before_http(self):
        for extra, args in (("SDP_GLOBAL_API_KEY=synthetic-global\nSDP_GLOBAL_PORTAL_ID=1\n",
                             ["--global-key-env", "OTHER", "--global-portal-id", "1"]),
                            ("SDP_DIRECTORY_API_KEY=synthetic-directory\n", ["--directory-key-env", "OTHER"]),
                            ("", ["--key-input", "console"])):
            self.write(self.values(extra))
            with patch("sdp_audit.cli.ReadOnlyClient") as factory:
                code, output = self.run_cli(["--env-file", str(self.path), "--non-interactive", *args])
            self.assertEqual(code, 1, output)
            factory.assert_not_called()
            self.assertNotIn(KEY1, output)

    def test_explicit_global_and_directory_credentials_keep_their_scopes(self):
        global_key, directory_key = "synthetic-global-key", "synthetic-directory-key"
        self.write(self.values(f"SDP_GLOBAL_API_KEY={global_key}\nSDP_GLOBAL_PORTAL_ID=1\n"
                               f"SDP_DIRECTORY_API_KEY={directory_key}\n"))
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        received = []
        original_open = server.open
        def record(request, timeout):
            received.append((request.full_url, request.get_header("Portalid"), request.get_header("Authtoken")))
            return original_open(request, timeout)
        server.open = record
        with patch("sdp_audit.cli.ReadOnlyClient", return_value=client):
            code, output = self.run_cli(["--env-file", str(self.path), "--all-portals", "--non-interactive",
                "--no-portal-cache", "--modules", "requests,orgusers", "--quiet", "--output-dir", str(self.root / "reports")])
        self.assertEqual(code, 0, output)
        self.assertNotIn("Discovery skipped: no discovery key set", output)
        self.assertTrue(any("/portals" in url and pid is None and key == directory_key for url, pid, key in received))
        self.assertTrue(any("/orgusers" in url and pid == "1" and key == global_key for url, pid, key in received))
        self.assertTrue(any("/requests" in url and pid == "1" and key == KEY1 for url, pid, key in received))
        self.assertEqual(client.sanitize_local_text(directory_key), "[REDACTED]")
        for url, pid, key in received:
            if key == directory_key:
                self.assertIn("/portals", url)
                self.assertIsNone(pid)
        for secret in (KEY1, global_key, directory_key):
            self.assertNotIn(secret, output)

    def test_diagnose_with_slots_remains_directory_only(self):
        self.write(self.values("SDP_DIRECTORY_API_KEY=synthetic-directory-key\n"))
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        with patch("sdp_audit.cli.ReadOnlyClient", return_value=client):
            code, output = self.run_cli(["--env-file", str(self.path), "--diagnose", "--non-interactive",
                "--quiet", "--output-dir", str(self.root / "reports")])
        self.assertEqual(code, 0, output)
        self.assertTrue(server.calls)
        self.assertTrue(all(call["path"] == "/portals" for call in server.calls))

    def test_diagnose_without_discovery_keys_does_not_borrow_slots(self):
        self.write(self.values())
        client, server, _ = create_synthetic_client(multi_key=True, api_key=None)
        with patch("sdp_audit.cli.ReadOnlyClient", return_value=client):
            code, output = self.run_cli(["--env-file", str(self.path), "--diagnose", "--non-interactive",
                "--quiet", "--no-portal-cache", "--output-dir", str(self.root / "reports")])
        self.assertEqual(code, 2, output)
        self.assertIn("CREDENTIAL_MISSING", output)
        self.assertFalse(server.calls)
        self.assertNotIn("Discovery skipped: no discovery key set", output)
        self.assertNotIn(KEY1, output)

    def test_no_env_disables_file_loading_but_keeps_process_configuration(self):
        self.write("INVALID INPUT")
        os.environ["SDP_API_KEY"] = KEY1
        with patch("sdp_audit.local_env.application_directory", return_value=self.root):
            code, output = self.run_cli(["--no-env", "--check-key-input"])
        self.assertEqual(code, 0, output)
        self.assertNotIn(KEY1, output)

    def test_offline_operations_ignore_invalid_file_and_do_not_scaffold(self):
        with patch("sdp_audit.local_env.application_directory", return_value=self.root):
            for args in (["--list-endpoints"], ["--help"], ["--version"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        main(args)
                    except SystemExit as error:
                        self.assertEqual(error.code, 0)
            self.assertFalse(self.path.exists())


class EnvLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        with contextlib.redirect_stdout(io.StringIO()):
            artifacts = build(ROOT, cls.root / "dist")
        cls.portable = artifacts["sdp_cloud_readiness.pyz"]
        cls.source = cls.root / "source"
        cls.source.mkdir()
        shutil.copytree(ROOT / "sdp_audit", cls.source / "sdp_audit", ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("sdp_cloud_readiness.py", "Run-Assessment.cmd", "Run-All-Portals.cmd"):
            shutil.copyfile(ROOT / name, cls.source / name)

    def invoke(self, entry, *args, env_extra=None):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("SDP_")}
        environment.update(env_extra or {})
        return subprocess.run([sys.executable, str(entry), *args], cwd=self.root, env=environment,
                              capture_output=True, text=True, timeout=30)

    def test_source_and_portable_default_location_and_scaffold(self):
        for entry in (self.source / "sdp_cloud_readiness.py", self.portable):
            with self.subTest(entry=entry):
                target = entry.parent / ".env"
                target.unlink(missing_ok=True)
                result = self.invoke(entry, "--non-interactive", "--quiet")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(target.read_text(), scaffold())
                target.write_text(f"SDP_HOST={HOST}\nSDP_API_KEY={KEY1}\n")
                before = target.read_bytes()
                result = self.invoke(entry, "--check-key-input", "--quiet")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(KEY1, result.stdout + result.stderr)
                self.assertEqual(target.read_bytes(), before)

    def test_source_and_portable_explicit_path_process_precedence_and_opt_out(self):
        alternate = self.root / "alternate.env"
        alternate.write_text(f"SDP_HOST={HOST}\nSDP_API_KEY=invalid key\n")
        for entry in (self.source / "sdp_cloud_readiness.py", self.portable):
            result = self.invoke(entry, "--env-file", str(alternate), "--check-key-input",
                                 env_extra={"SDP_API_KEY": KEY2})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(KEY2, result.stdout + result.stderr)
            (entry.parent / ".env").write_text("INVALID CONTENT")
            result = self.invoke(entry, "--no-env", "--check-key-input", env_extra={"SDP_API_KEY": KEY2})
            self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(sys.platform == "win32", "Windows command launchers")
    def test_both_windows_launchers_load_default_file(self):
        (self.source / ".env").write_text(f"SDP_HOST={HOST}\nSDP_API_KEY={KEY1}\n")
        environment = {k: v for k, v in os.environ.items() if not k.startswith("SDP_")}
        for name in ("Run-Assessment.cmd", "Run-All-Portals.cmd"):
            result = subprocess.run(["cmd", "/c", str(self.source / name), "--check-key-input"],
                cwd=self.root, env=environment, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn(KEY1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
