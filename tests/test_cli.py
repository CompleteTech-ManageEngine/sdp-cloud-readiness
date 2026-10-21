"""Credential-free entry point and configuration boundary regressions."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sdp_audit.cli import _cli_options, _cli_parser, main


class CliTests(unittest.TestCase):
    def test_portal_cli_overrides_config_and_combines_explicit_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "connection.json"
            config.write_text(json.dumps({"portal_ids": ["7"], "portal_id": "42"}), encoding="utf-8")
            args = _cli_parser().parse_args(["--config", str(config), "--portal-id", "3", "--portal-ids", "5,03"])
            self.assertEqual(_cli_options(args)["portal_ids"], ["3", "5"])
            defaults = _cli_options(_cli_parser().parse_args([]))
            self.assertEqual(defaults["portal_ids"], [])
            self.assertEqual(defaults["portal_discovery_mode"], "automatic")

    def test_default_two_prompt_invocation_discovers_all_visible_portals(self):
        from sdp_audit.synthetic import SYNTHETIC_HOST, SYNTHETIC_KEY, create_synthetic_client
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict("os.environ", {"SDP_HOST": "", "SDP_API_KEY": ""}), \
             patch("sdp_audit.cli.sys.stdin.isatty", return_value=True), \
             patch("sdp_audit.credentials.sys.platform", "linux"), \
             patch("builtins.input", return_value=SYNTHETIC_HOST) as host_prompt, \
             patch("sdp_audit.credentials._read_console", return_value=SYNTHETIC_KEY) as key_prompt, \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--quiet", "--output-dir", directory]), 0)
            host_prompt.assert_called_once()
            key_prompt.assert_called_once()
            self.assertEqual({call["portal_id"] for call in server.calls if call["portal_id"]}, {"1", "2", "3", "4"})
            report = next(Path(directory).glob("*/assessment.json"))
            self.assertNotIn(SYNTHETIC_KEY, report.read_text())

    def test_actual_cli_portal_override_restricts_scoped_reads(self):
        from sdp_audit.synthetic import SYNTHETIC_HOST, SYNTHETIC_KEY, create_synthetic_client
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             contextlib.redirect_stdout(io.StringIO()):
            code = main(["--host", SYNTHETIC_HOST, "--portal-id", "3", "--quiet", "--output-dir", directory])
            self.assertEqual(code, 0)
            self.assertTrue(server.calls)
            self.assertEqual({call["portal_id"] for call in server.calls}, {"3"})
            self.assertFalse(any(call["path"] in {"/portals", "/orgusers"} for call in server.calls))

    def test_unavailable_discovery_cli_writes_unknown_topology_without_default(self):
        from sdp_audit.synthetic import SYNTHETIC_HOST, SYNTHETIC_KEY, create_synthetic_client
        client, server, _ = create_synthetic_client("portal_discovery_unavailable")
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--host", SYNTHETIC_HOST, "--quiet", "--output-dir", directory]), 2)
            self.assertEqual(len(server.calls), 1)
            document = json.loads(next(Path(directory).glob("*/assessment.json")).read_text())
            self.assertEqual(document["portals"], [])
            self.assertEqual(document["environment"]["stop"]["classification"], "PORTAL_DISCOVERY_UNAVAILABLE")

    def test_invalid_command_line_never_echoes_arbitrary_value(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error), self.assertRaises(SystemExit):
            main(["--api-key", "PRIVATE_TOKEN_MUST_NOT_ECHO"])
        self.assertNotIn("PRIVATE_TOKEN_MUST_NOT_ECHO", error.getvalue())
        self.assertIn("Invalid command-line", error.getvalue())

    def test_interruption_during_analysis_recovers_collected_snapshot(self):
        from sdp_audit.environment_analysis import analyze_environment
        attempts = 0

        def analysis(snapshot):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise KeyboardInterrupt
            return analyze_environment(snapshot)

        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.cli.analyze_environment", side_effect=analysis), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--demo", "--quiet", "--output-dir", directory]), 2)
            document = json.loads(next(Path(directory).glob("*/assessment.json")).read_text())
            self.assertEqual(len(document["portals"]), 4)
            self.assertEqual(document["environment"]["stop"]["classification"], "INTERRUPTED")

    def test_demo_writes_six_reports_without_credentials_or_network_client(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError("network client prohibited")), \
                    patch("sdp_audit.credentials._read_console", side_effect=AssertionError("credential prompt prohibited")), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--demo", "--output-dir", directory]), 0)
            folders = [path for path in Path(directory).iterdir() if path.is_dir()]
            self.assertEqual(len(folders), 1)
            self.assertEqual({p.name for p in folders[0].iterdir()}, {
                "report.html", "report.md", "assessment.json", "findings.csv",
                "coverage.csv", "vendor-questions.md", "diagnostics.json", "report-manifest.json",
            })
            result = json.loads((folders[0] / "assessment.json").read_text(encoding="utf-8"))
            self.assertTrue(result["source"]["demo"])
            self.assertEqual(len(result["questions"]), 7)
            self.assertTrue(any("SYNTHETIC" in note for note in result["notes"]))

    def test_invalid_numeric_settings_fail_without_echoing_values(self):
        for value in ("secret-example-never-echo", {"nested": "secret-example-never-echo"}, True):
            with self.subTest(value_type=type(value).__name__), tempfile.TemporaryDirectory() as directory:
                config = Path(directory) / "connection.json"
                config.write_text(json.dumps({"rpm": value}), encoding="utf-8")
                error = io.StringIO()
                with patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError("network prohibited")), \
                        contextlib.redirect_stderr(error):
                    self.assertEqual(main(["--config", str(config), "--demo"]), 1)
                self.assertNotIn("secret-example-never-echo", error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())

    def test_endpoint_listing_does_not_prompt_or_create_network_client(self):
        output = io.StringIO()
        with patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError("network prohibited")), \
                patch("builtins.input", side_effect=AssertionError("prompt prohibited")), \
                contextlib.redirect_stdout(output):
            self.assertEqual(main(["--list-endpoints"]), 0)
        self.assertIn("GET /api/v3/requests", output.getvalue())
        self.assertIn("Not automatically certified", output.getvalue())


if __name__ == "__main__":
    unittest.main()
