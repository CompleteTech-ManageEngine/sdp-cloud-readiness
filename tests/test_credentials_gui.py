"""Opt-in real Tk tests: SDP_TEST_GUI=1; a desktop or Xvfb is required.

Only synthetic clipboard values are used. Application code does not access
clipboard APIs automatically. Native Windows console behavior is not simulated
by this graphical test; it exercises the alternative masked entry path.
"""
from __future__ import annotations

import contextlib
import io
import os
import unittest
from unittest.mock import patch

from sdp_audit.credentials import CredentialInputError, _read_dialog

GUI_ENABLED = os.environ.get("SDP_TEST_GUI") == "1"
CANARY = "SYNTHETIC-GUI-KEY-DO-NOT-PRINT-c229d"


@unittest.skipUnless(GUI_ENABLED, "Opt-in graphical test: set SDP_TEST_GUI=1 with a desktop or Xvfb")
class RealDialogTests(unittest.TestCase):
    def drive_dialog(self, action):
        import tkinter as tk
        native_tk = tk.Tk
        failures = []
        widgets_observed = []
        output, error = io.StringIO(), io.StringIO()

        def factory():
            root = native_tk()
            def timeout():
                failures.append("Graphical test exceeded its deadline")
                root.destroy()
            root.after(5000, timeout)
            def drive():
                candidates = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
                if not candidates or not hasattr(candidates[0], "secret_entry"):
                    root.after(15, drive)
                    return
                dialog = candidates[0]
                entry = dialog.secret_entry
                widgets_observed.append(True)
                try:
                    self.assertEqual(entry.cget("show"), "*")
                    self.assertFalse(bool(int(entry.cget("exportselection"))))
                    action(root, dialog, entry)
                except AssertionError as failure:
                    # Do not let the application's callback guard hide a failed test.
                    failures.append(str(failure))
                    dialog.cancel()
            root.after(40, drive)
            return root

        result, raised = None, None
        with patch("tkinter.Tk", side_effect=factory), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                result = _read_dialog()
            except BaseException as exception:
                raised = exception
        self.assertFalse(failures, "\n".join(failures))
        self.assertTrue(widgets_observed)
        self.assertNotIn(CANARY, output.getvalue() + error.getvalue())
        self.assertNotIn("Traceback", output.getvalue() + error.getvalue())
        return result, raised

    def test_masked_dialog_accepts_user_initiated_paste(self):
        def action(root, dialog, entry):
            root.clipboard_clear()
            root.clipboard_append(CANARY)
            entry.event_generate("<<Paste>>")
            root.update_idletasks()
            self.assertEqual(entry.get(), CANARY)
            root.clipboard_clear()  # Test fixture cleanup; not application behavior.
            dialog.ok()
        result, error = self.drive_dialog(action)
        self.assertIsNone(error)
        self.assertEqual(result, CANARY)

    def test_masked_dialog_accepts_entered_text_and_clears_widget(self):
        cleared = []
        def action(root, dialog, entry):
            entry.insert(0, CANARY)
            original_delete = entry.delete
            def delete(*args):
                result = original_delete(*args)
                if entry.winfo_exists():
                    cleared.append(entry.get() == "")
                return result
            entry.delete = delete
            dialog.ok()
        result, error = self.drive_dialog(action)
        self.assertIsNone(error)
        self.assertEqual(result, CANARY)
        self.assertTrue(cleared and all(cleared))

    def test_cancel_does_not_return_the_key(self):
        def action(root, dialog, entry):
            entry.insert(0, CANARY)
            dialog.cancel()
        result, error = self.drive_dialog(action)
        self.assertIsNone(result)
        self.assertIsInstance(error, KeyboardInterrupt)

    def test_empty_input_returns_empty_for_category_validation(self):
        result, error = self.drive_dialog(lambda root, dialog, entry: dialog.ok())
        self.assertIsNone(error)
        self.assertEqual(result, "")

    def test_callback_failure_does_not_print_exception_or_fall_back(self):
        def action(root, dialog, entry):
            entry.insert(0, CANARY)
            def fail():
                raise ValueError(CANARY)
            root.after(10, fail)
        result, error = self.drive_dialog(action)
        self.assertIsNone(result)
        self.assertIsInstance(error, CredentialInputError)
        self.assertEqual(error.code, "INPUT_FAILED")
        self.assertNotIn(CANARY, str(error))


if __name__ == "__main__":
    unittest.main()
