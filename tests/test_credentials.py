"""Local key-input regressions; all credentials in these tests are synthetic."""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
import warnings
from unittest.mock import patch

from sdp_audit import credentials
from sdp_audit.cli import main
from sdp_audit.credentials import (
    CredentialInputError, MAX_KEY_LENGTH, acquire_api_key, prepare_api_key,
)

CANARY = "SYNTHETIC-KEY-NEVER-PRINT-7cb32"


class PreparationTests(unittest.TestCase):
    def check_error(self, value, code):
        with self.assertRaises(CredentialInputError) as caught:
            prepare_api_key(value)
        self.assertEqual(caught.exception.code, code)
        self.assertNotIn(CANARY, str(caught.exception))
        self.assertNotIn(CANARY, repr(caught.exception))

    def test_valid_key_unchanged(self):
        key = prepare_api_key(CANARY)
        self.assertEqual(key.value, CANARY)
        self.assertFalse(key.boundary_cleanup)
        self.assertNotIn(CANARY, repr(key))

    def test_visible_ascii_range_preserved_not_decoded(self):
        value = ''.join(chr(i) for i in range(33, 127))
        self.assertEqual(prepare_api_key(value).value, value)
        self.assertEqual(prepare_api_key("abc%20def+ghi==").value, "abc%20def+ghi==")

    def test_quotes_not_silently_removed(self):
        self.assertEqual(prepare_api_key('"' + CANARY + '"').value, '"' + CANARY + '"')

    def test_boundary_spaces_tabs_crlf_removed(self):
        key = prepare_api_key("\t \r\n" + CANARY + "\t \r\n")
        self.assertEqual(key.value, CANARY)
        self.assertTrue(key.boundary_cleanup)

    def test_boundary_nonbreaking_spaces_and_format_markers_removed(self):
        key = prepare_api_key("\ufeff\u200b\u00a0" + CANARY + "\u00a0\u200b\ufeff")
        self.assertEqual(key.value, CANARY)
        self.assertTrue(key.boundary_cleanup)

    def test_ctrl_v_control_is_not_silently_discarded(self):
        for value in ("\x16", "\x16" + CANARY, CANARY + "\x16", " \x16 "):
            with self.subTest(placement=len(value)):
                self.check_error(value, "PASTE_SHORTCUT")

    def test_all_other_ascii_controls_fail_closed(self):
        for value in [chr(i) for i in range(32) if i not in (9, 10, 13, 22)] + ["\x7f"]:
            self.check_error(value + CANARY, "CONTROL_CHARACTERS")

    def test_interior_whitespace_is_not_joined(self):
        for char in (" ", "\t", "\r", "\n", "\u00a0"):
            self.check_error(CANARY + char + "second", "INTERIOR_WHITESPACE")

    def test_interior_unicode_and_zero_width_fail_closed(self):
        for char in ("\u200b", "\ufeff", "é", "\u2060", "\u202e"):
            self.check_error(CANARY + char + "second", "NON_ASCII")

    def test_other_boundary_formatting_not_silently_removed(self):
        self.check_error("\u202e" + CANARY, "NON_ASCII")

    def test_unicode_lookalikes_not_transliterated(self):
        self.check_error("Ａ" + CANARY, "NON_ASCII")

    def test_empty_input(self):
        for value in ("", " \t\r\n", "\ufeff\u200b"):
            self.check_error(value, "EMPTY")

    def test_input_length_bound(self):
        self.assertEqual(len(prepare_api_key("a" * MAX_KEY_LENGTH).value), MAX_KEY_LENGTH)
        self.check_error(CANARY + "a" * MAX_KEY_LENGTH, "TOO_LONG")

    def test_non_text_input(self):
        for value in (None, 123, True, {}, b"key"):
            self.check_error(value, "INVALID_TYPE")

    def test_unknown_error_code_cannot_echo_arbitrary_text(self):
        error = CredentialInputError(CANARY)
        self.assertEqual(error.code, "INPUT_FAILED")
        self.assertNotIn(CANARY, str(error))


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"SDP_API_KEY": "", "CUSTOM_TEST_KEY": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.tty = patch("sdp_audit.credentials.sys.stdin.isatty", return_value=True)
        self.tty.start()
        self.addCleanup(self.tty.stop)
        self.log = io.StringIO()

    def test_windows_auto_uses_masked_dialog(self):
        with patch("sdp_audit.credentials.sys.platform", "win32"), \
             patch("sdp_audit.credentials._read_dialog", return_value=CANARY) as dialog, \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError):
            self.assertEqual(acquire_api_key(stream=self.log), CANARY)
        dialog.assert_called_once()
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_nonwindows_auto_uses_console(self):
        with patch("sdp_audit.credentials.sys.platform", "linux"), \
             patch("sdp_audit.credentials._read_console", return_value=CANARY) as console, \
             patch("sdp_audit.credentials._read_dialog", side_effect=AssertionError):
            self.assertEqual(acquire_api_key(stream=self.log), CANARY)
        console.assert_called_once()

    def test_explicit_console_bypasses_environment(self):
        with patch.dict(os.environ, {"SDP_API_KEY": "STALE-SYNTHETIC-KEY"}), \
             patch("sdp_audit.credentials._read_console", return_value=CANARY), \
             patch("sdp_audit.credentials._read_dialog", side_effect=AssertionError):
            self.assertEqual(acquire_api_key("console", stream=self.log), CANARY)
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_explicit_dialog_bypasses_environment(self):
        with patch.dict(os.environ, {"SDP_API_KEY": "STALE-SYNTHETIC-KEY"}), \
             patch("sdp_audit.credentials._read_dialog", return_value=CANARY):
            self.assertEqual(acquire_api_key("dialog", stream=self.log), CANARY)

    def test_auto_environment_takes_precedence_and_is_not_mutated(self):
        with patch.dict(os.environ, {"SDP_API_KEY": CANARY}), \
             patch("sdp_audit.credentials._read_dialog", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError):
            self.assertEqual(acquire_api_key(stream=self.log), CANARY)
            self.assertEqual(os.environ["SDP_API_KEY"], CANARY)
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_environment_variable_custom_name(self):
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": CANARY}):
            self.assertEqual(acquire_api_key(env_name="CUSTOM_TEST_KEY", stream=self.log), CANARY)

    def test_invalid_environment_key_does_not_silently_prompt_or_send(self):
        with patch.dict(os.environ, {"SDP_API_KEY": "\x16" + CANARY}), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_dialog", side_effect=AssertionError), \
             self.assertRaises(CredentialInputError) as caught:
            acquire_api_key(stream=self.log)
        self.assertEqual(caught.exception.code, "PASTE_SHORTCUT")
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_environment_boundaries_normalized_with_notice(self):
        with patch.dict(os.environ, {"SDP_API_KEY": " \ufeff" + CANARY + "\r\n"}):
            self.assertEqual(acquire_api_key(stream=self.log), CANARY)
        self.assertIn("Removed surrounding", self.log.getvalue())
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_ctrl_v_error_reprompts_then_accepts(self):
        with patch("sdp_audit.credentials._read_console", side_effect=["\x16", CANARY]) as reader:
            self.assertEqual(acquire_api_key("console", stream=self.log), CANARY)
        self.assertEqual(reader.call_count, 2)
        self.assertIn("Ctrl+V control character", self.log.getvalue())
        self.assertIn("No request was sent", self.log.getvalue())
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_retries_are_bounded(self):
        with patch("sdp_audit.credentials._read_console", return_value="\x16" + CANARY) as reader, \
             self.assertRaises(CredentialInputError) as caught:
            acquire_api_key("console", stream=self.log)
        self.assertEqual(reader.call_count, 3)
        self.assertEqual(caught.exception.code, "RETRIES_EXHAUSTED")
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_dialog_bad_input_reprompts(self):
        with patch("sdp_audit.credentials._read_dialog", side_effect=["", CANARY]) as reader:
            self.assertEqual(acquire_api_key("dialog", stream=self.log), CANARY)
        self.assertEqual(reader.call_count, 2)

    def test_interactive_boundary_cleanup_notice(self):
        with patch("sdp_audit.credentials._read_console", return_value="\u200b" + CANARY):
            self.assertEqual(acquire_api_key("console", stream=self.log), CANARY)
        self.assertIn("Removed surrounding", self.log.getvalue())
        self.assertNotIn(CANARY, self.log.getvalue())

    def test_auto_unavailable_dialog_falls_back_to_hidden_console_once(self):
        with patch("sdp_audit.credentials.sys.platform", "win32"), \
             patch("sdp_audit.credentials._read_dialog", side_effect=CredentialInputError("NO_DIALOG")) as dialog, \
             patch("sdp_audit.credentials._read_console", side_effect=["\x16", CANARY]) as console:
            self.assertEqual(acquire_api_key(stream=self.log), CANARY)
        dialog.assert_called_once()
        self.assertEqual(console.call_count, 2)
        self.assertIn("Edit > Paste", self.log.getvalue())

    def test_explicit_unavailable_dialog_does_not_change_input_mode(self):
        with patch("sdp_audit.credentials._read_dialog", side_effect=CredentialInputError("NO_DIALOG")), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError), \
             self.assertRaises(CredentialInputError) as caught:
            acquire_api_key("dialog", stream=self.log)
        self.assertEqual(caught.exception.code, "NO_DIALOG")

    def test_dialog_failure_does_not_fallback_to_console(self):
        with patch("sdp_audit.credentials.sys.platform", "win32"), \
             patch("sdp_audit.credentials._read_dialog", side_effect=CredentialInputError("INPUT_FAILED")), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError), \
             self.assertRaises(CredentialInputError):
            acquire_api_key(stream=self.log)

    def test_dialog_cancel_does_not_fallback(self):
        with patch("sdp_audit.credentials.sys.platform", "win32"), \
             patch("sdp_audit.credentials._read_dialog", side_effect=KeyboardInterrupt), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError), \
             self.assertRaises(KeyboardInterrupt):
            acquire_api_key(stream=self.log)

    def test_console_interrupt_propagates(self):
        with patch("sdp_audit.credentials._read_console", side_effect=KeyboardInterrupt), \
             self.assertRaises(KeyboardInterrupt):
            acquire_api_key("console", stream=self.log)

    def test_noninteractive_fails_without_echo_input(self):
        with patch("sdp_audit.credentials.sys.stdin.isatty", return_value=False), \
             patch("builtins.input", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_console", side_effect=AssertionError), \
             self.assertRaises(CredentialInputError) as caught:
            acquire_api_key(stream=self.log)
        self.assertEqual(caught.exception.code, "NO_INTERACTIVE_INPUT")

    def test_explicit_dialog_can_be_used_with_redirected_stdin(self):
        with patch("sdp_audit.credentials.sys.stdin.isatty", return_value=False), \
             patch("sdp_audit.credentials._read_dialog", return_value=CANARY):
            self.assertEqual(acquire_api_key("dialog", stream=self.log), CANARY)

    def test_getpass_warning_fails_before_echo_fallback(self):
        def warning_fallback(*args, **kwargs):
            warnings.warn("synthetic no-echo unavailable", credentials.getpass.GetPassWarning)
            self.fail("Echoing fallback must not execute")
        with patch("sdp_audit.credentials.getpass.getpass", side_effect=warning_fallback), \
             self.assertRaises(CredentialInputError) as caught:
            credentials._read_console()
        self.assertEqual(caught.exception.code, "NO_HIDDEN_INPUT")

    def test_getpass_unexpected_error_does_not_expose_contents(self):
        for error in (ValueError(CANARY), OSError(CANARY), RuntimeError(CANARY)):
            with patch("sdp_audit.credentials.getpass.getpass", side_effect=error), \
                 self.assertRaises(CredentialInputError) as caught:
                credentials._read_console()
            self.assertNotIn(CANARY, str(caught.exception))

    def test_missing_tk_fails_with_static_message(self):
        with patch.dict("sys.modules", {"tkinter": None}), self.assertRaises(CredentialInputError) as caught:
            credentials._read_dialog()
        self.assertEqual(caught.exception.code, "NO_DIALOG")
        self.assertNotIn("Traceback", str(caught.exception))

    def test_invalid_input_mode_has_static_error(self):
        with self.assertRaises(CredentialInputError) as caught:
            acquire_api_key(CANARY, stream=self.log)
        self.assertNotIn(CANARY, str(caught.exception))


class CliInputTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.error = io.StringIO()
        for manager in (
            patch.dict(os.environ, {"SDP_API_KEY": "", "SDP_HOST": ""}),
            patch("sdp_audit.credentials.sys.stdin.isatty", return_value=True),
            contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.error),
        ):
            manager.__enter__()
            self.addCleanup(manager.__exit__, None, None, None)

    def assert_private(self):
        for text in (self.output.getvalue(), self.error.getvalue()):
            self.assertNotIn(CANARY, text)
            self.assertNotIn("Traceback", text)

    def test_local_check_requires_neither_host_nor_http_nor_report_directory(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError), \
             patch("builtins.input", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_dialog", return_value=CANARY):
            self.assertEqual(main(["--key-input", "dialog", "--check-key-input", "--output-dir", directory]), 0)
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assertIn("authentication was NOT tested", self.output.getvalue())
        self.assert_private()

    def test_local_check_rejects_bad_input_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_console", return_value="\x16" + CANARY):
            self.assertEqual(main(["--key-input", "console", "--check-key-input", "--output-dir", directory]), 1)
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assert_private()

    def test_bad_key_normal_run_never_constructs_client_or_report_directory(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_console", return_value="\x16" + CANARY):
            self.assertEqual(main(["--host", "https://helpdesk.example.invalid", "--key-input", "console", "--output-dir", directory]), 1)
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assert_private()

    def test_cancel_before_collection_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError), \
             patch("sdp_audit.credentials._read_dialog", side_effect=KeyboardInterrupt):
            self.assertEqual(main(["--host", "https://helpdesk.example.invalid", "--key-input", "dialog", "--output-dir", directory]), 130)
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assert_private()

    def test_windows_dialog_default_reaches_multiportal_collection(self):
        from sdp_audit.synthetic import SYNTHETIC_KEY, create_synthetic_client
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.credentials.sys.platform", "win32"), \
             patch("sdp_audit.credentials._read_dialog", return_value=SYNTHETIC_KEY), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client) as factory:
            self.assertEqual(main(["--host", "https://helpdesk.example.invalid", "--output-dir", directory]), 0)
            self.assertEqual(factory.call_args.args[1], SYNTHETIC_KEY)
            self.assertEqual({c["portal_id"] for c in server.calls if c["portal_id"]}, {"1", "2", "3", "4"})
            for p in Path(directory).rglob("*"):
                if p.is_file():
                    if p.suffix == ".zip":
                        import zipfile
                        with zipfile.ZipFile(p) as archive:
                            for name in archive.namelist():
                                self.assertNotIn(SYNTHETIC_KEY.encode(), archive.read(name))
                    else:
                        self.assertNotIn(SYNTHETIC_KEY, p.read_text())
        self.assertNotIn(SYNTHETIC_KEY, self.output.getvalue() + self.error.getvalue())

    def test_retry_then_scan_uses_clean_key_and_preserves_reports(self):
        from sdp_audit.synthetic import SYNTHETIC_KEY, create_synthetic_client
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as directory, \
             patch("sdp_audit.credentials._read_console", side_effect=["\x16", "\ufeff" + SYNTHETIC_KEY + "\r\n"]) as reader, \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client) as factory:
            self.assertEqual(main(["--host", "https://helpdesk.example.invalid", "--key-input", "console", "--output-dir", directory]), 0)
            self.assertEqual(reader.call_count, 2)
            factory.assert_called_once()
            self.assertEqual(factory.call_args.args[1], SYNTHETIC_KEY)
            report_files = [p for p in Path(directory).rglob("*") if p.is_file()]
            self.assertEqual(len(report_files), 9)
            self.assertTrue(server.calls)
            for p in report_files:
                if p.suffix == ".zip":
                    import zipfile
                    with zipfile.ZipFile(p) as archive:
                        for name in archive.namelist():
                            self.assertNotIn(SYNTHETIC_KEY.encode(), archive.read(name))
                else:
                    self.assertNotIn(SYNTHETIC_KEY, p.read_text())
        self.assertNotIn(SYNTHETIC_KEY, self.output.getvalue() + self.error.getvalue())

    def test_invalid_environment_key_no_client_no_secret_output(self):
        with patch.dict(os.environ, {"SDP_API_KEY": CANARY + "\x16"}), \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError):
            self.assertEqual(main(["--check-key-input"]), 1)
        self.assert_private()

    def test_low_level_exception_no_secret_output(self):
        with patch("sdp_audit.credentials.getpass.getpass", side_effect=ValueError(CANARY)):
            self.assertEqual(main(["--key-input", "console", "--check-key-input"]), 1)
        self.assert_private()

    def test_startup_version_is_printed_before_prompts(self):
        from sdp_audit import __version__
        def key_reader():
            self.assertIn(__version__, self.output.getvalue())
            return CANARY
        with patch("sdp_audit.credentials._read_console", side_effect=key_reader):
            self.assertEqual(main(["--key-input", "console", "--check-key-input"]), 0)
        self.assert_private()

    def test_help_lists_recovery_flags(self):
        with self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("--check-key-input", self.output.getvalue())
        self.assertIn("--key-input", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
