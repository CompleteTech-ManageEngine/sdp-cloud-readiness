"""Secret-safe local credential input. No network, disk or automatic clipboard access.

Windows auto mode uses a masked local dialog, avoiding the legacy console's
Ctrl+V -> SYN character behavior. Console input remains available explicitly
and is the fallback if a graphical dialog cannot be created. Never replace
getpass with input(): failure to suppress echo must fail closed.
"""
from __future__ import annotations

import getpass
import os
import sys
import warnings
from dataclasses import dataclass
from typing import TextIO

MAX_KEY_LENGTH = 8192
# Only these invisible copy boundaries are removable, and only at the edges.
# Interior characters are never deleted, rejoined, decoded or transliterated.
BOUNDARY_MARKERS = frozenset(("\ufeff", "\u200b"))
MESSAGES = {
    "EMPTY": "No API key was received. Copy only the key and enter it again.",
    "TOO_LONG": "API-key input exceeds the scanner's 8192-character safety limit.",
    "PASTE_SHORTCUT": (
        "The input contains a Ctrl+V control character, not valid API-key text. "
        "Use the window menu Edit > Paste, right-click paste when enabled, "
        "or run with --key-input dialog."
    ),
    "CONTROL_CHARACTERS": (
        "The input contains terminal control characters. Re-copy only the API key; "
        "use --key-input dialog or the window menu Edit > Paste."
    ),
    "INTERIOR_WHITESPACE": (
        "The input contains whitespace inside the API key. Copy the key as one "
        "unbroken value; spaces or line breaks inside it are not removed."
    ),
    "NON_ASCII": (
        "The input contains non-ASCII or invisible characters inside the API key. "
        "Re-copy the original key without formatting; interior characters are not changed."
    ),
    "INVALID_TYPE": "API-key input must be text.",
    "NO_HIDDEN_INPUT": (
        "Hidden console input is unavailable. No echoing fallback was used. "
        "Use --key-input dialog on a desktop or supply the configured environment variable securely."
    ),
    "NO_DIALOG": (
        "A masked key-entry dialog is unavailable. A desktop and Python's optional "
        "Tcl/Tk component are required. Use --key-input console and the window menu Edit > Paste."
    ),
    "INPUT_FAILED": "Secret input could not be read. No input or exception contents were printed.",
    "NO_INTERACTIVE_INPUT": (
        "No API key is available in this non-interactive session. Supply the configured "
        "environment variable securely, or use --key-input dialog on a desktop."
    ),
    "RETRIES_EXHAUSTED": (
        "API-key input was not accepted after three local attempts. No authentication "
        "request was sent. Re-run with --key-input dialog or use Edit > Paste at the console prompt."
    ),
    "INVALID_MODE": "Unsupported key-input mode. Choose auto, console or dialog.",
}


class CredentialInputError(ValueError):
    """A bounded diagnostic with a fixed message; never stores the input."""
    def __init__(self, code: str) -> None:
        self.code = code if code in MESSAGES else "INPUT_FAILED"
        super().__init__(MESSAGES[self.code])


@dataclass(frozen=True, repr=False)
class PreparedKey:
    value: str
    boundary_cleanup: bool = False

    def __repr__(self) -> str:
        return "PreparedKey(value=<redacted>)"


def prepare_api_key(raw: str) -> PreparedKey:
    """Trim copy boundaries, validate locally and return a redacted-repr holder.

    This does not verify that the server accepts the key. The transport retains
    its own strict validation before any header is constructed.
    """
    if not isinstance(raw, str):
        raise CredentialInputError("INVALID_TYPE")
    if len(raw) > MAX_KEY_LENGTH:
        raise CredentialInputError("TOO_LONG")
    # Test controls before trimming: str.strip() considers a few ASCII control
    # characters whitespace. They must never be silently accepted at an edge.
    if "\x16" in raw:
        raise CredentialInputError("PASTE_SHORTCUT")
    if any((ord(c) < 32 and c not in "\t\r\n") or ord(c) == 127 for c in raw):
        raise CredentialInputError("CONTROL_CHARACTERS")
    start, end = 0, len(raw)
    while start < end and (raw[start].isspace() or raw[start] in BOUNDARY_MARKERS):
        start += 1
    while end > start and (raw[end - 1].isspace() or raw[end - 1] in BOUNDARY_MARKERS):
        end -= 1
    value = raw[start:end]
    if not value:
        raise CredentialInputError("EMPTY")
    if any(c.isspace() for c in value):
        raise CredentialInputError("INTERIOR_WHITESPACE")
    if any(not 33 <= ord(c) <= 126 for c in value):
        raise CredentialInputError("NON_ASCII")
    return PreparedKey(value, start != 0 or end != len(raw))


def _read_console() -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            return getpass.getpass("API key (hidden; not saved): ")
    except getpass.GetPassWarning:
        raise CredentialInputError("NO_HIDDEN_INPUT") from None
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        # Even a library or terminal exception can embed the input.
        raise CredentialInputError("INPUT_FAILED") from None


def _read_dialog() -> str:
    """Local masked entry; ordinary user-initiated paste; never auto-reads clipboard."""
    root = None
    callback_failed = False
    try:
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()

        def callback_error(_exc_type: object, _exc_value: object, _traceback: object) -> None:
            nonlocal callback_failed
            callback_failed = True
            # Tk's default callback handler prints a traceback. Never allow it
            # to reveal data included in an exception by the widget/library.
            try:
                root.destroy()
            except Exception:
                pass

        root.report_callback_exception = callback_error

        class KeyDialog(simpledialog.Dialog):
            def body(self, master: object) -> object:
                tk.Label(master, text=(
                    "ServiceDesk Plus integration API key\n"
                    "Paste only the key (Ctrl+V), then select OK.\n"
                    "Input is masked. The scanner does not save the key."
                ), justify="left").grid(row=0, column=0, padx=10, pady=(8, 5))
                self.secret_entry = tk.Entry(master, show="*", width=60, exportselection=False)
                self.secret_entry.grid(row=1, column=0, padx=10, pady=(0, 10))
                return self.secret_entry

            def apply(self) -> None:
                self.result = self.secret_entry.get()
                self.secret_entry.delete(0, "end")

            def destroy(self) -> None:
                # Best-effort removal from the widget. Python/Tk strings and
                # OS clipboard/history are not guaranteed securely erasable.
                try:
                    if hasattr(self, "secret_entry"):
                        self.secret_entry.delete(0, "end")
                except Exception:
                    pass
                super().destroy()

        dialog = KeyDialog(root, title="ServiceDesk Plus - hidden API-key entry")
        value = dialog.result
        dialog.result = None
        if callback_failed:
            raise CredentialInputError("INPUT_FAILED")
        if value is None:
            raise KeyboardInterrupt
        return value
    except (KeyboardInterrupt, EOFError, CredentialInputError):
        raise
    except Exception:
        # Do not expose Tcl errors, import paths, entered text or tracebacks.
        raise CredentialInputError("INPUT_FAILED" if callback_failed else "NO_DIALOG") from None
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass


def acquire_api_key(mode: str = "auto", env_name: str = "SDP_API_KEY", *,
                    stream: TextIO | None = None) -> str:
    """Acquire locally, retry bad interactive input, never retry invalid env data.

    Explicit console/dialog mode deliberately bypasses a possibly stale env
    credential. Auto preserves the existing environment-variable interface.
    All diagnostics are fixed category descriptions, not values or characters.
    """
    out = stream if stream is not None else sys.stderr
    if mode not in {"auto", "console", "dialog"}:
        raise CredentialInputError("INVALID_MODE")
    environment_key = os.environ.get(env_name) if mode == "auto" else None
    if environment_key:
        try:
            prepared = prepare_api_key(environment_key)
        except CredentialInputError:
            print("Configured environment API-key input was rejected locally; it was not sent.", file=out)
            raise
        if prepared.boundary_cleanup:
            print("Removed surrounding copy/paste whitespace or invisible boundary markers; key content is not displayed.", file=out)
        print("Using API key from the configured environment variable; no key value is displayed.", file=out)
        return prepared.value
    if mode != "dialog" and not sys.stdin.isatty():
        raise CredentialInputError("NO_INTERACTIVE_INPUT")
    selected = "dialog" if mode == "dialog" or (mode == "auto" and sys.platform == "win32") else "console"
    if selected == "dialog":
        print("API key: opening a local masked entry dialog. Paste the key there, then select OK.", file=out)
    elif sys.platform == "win32":
        print("Hidden console input: use Edit > Paste (window menu), not Ctrl+V in a legacy console. --key-input dialog is also available.", file=out)
    for attempt in range(3):
        try:
            raw = _read_dialog() if selected == "dialog" else _read_console()
        except CredentialInputError as error:
            if mode == "auto" and selected == "dialog" and error.code == "NO_DIALOG":
                print("Masked dialog unavailable; using hidden console input. Paste using the window menu Edit > Paste, not Ctrl+V.", file=out)
                selected = "console"
                raw = _read_console()
            else:
                raise
        try:
            prepared = prepare_api_key(raw)
        except CredentialInputError as error:
            raw = ""
            print("API-key input rejected locally: " + str(error), file=out)
            print("No request was sent to ServiceDesk Plus.", file=out)
            if attempt < 2:
                print("Enter the key again, or cancel with Ctrl+C / the dialog Cancel button.", file=out)
            continue
        raw = ""
        if prepared.boundary_cleanup:
            print("Removed surrounding copy/paste whitespace or invisible boundary markers; key content is not displayed.", file=out)
        return prepared.value
    raise CredentialInputError("RETRIES_EXHAUSTED")
