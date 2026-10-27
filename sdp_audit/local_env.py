"""Bounded, literal local environment loading; never executes or expands values."""
from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path

from .credentials import prepare_api_key
from .topology import portal_identifier
from .transport import _binding_host

MAX_BYTES = 1024 * 1024
MAX_LINES = 10000
SLOT = re.compile(r"SDP_INSTANCE_([0-9]{2,6})_(API_KEY|PORTAL_ID)\Z", re.ASCII)
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}\Z", re.ASCII)


class _SecretValues(dict):
    def __repr__(self) -> str:
        return "LocalEnvironment(values=<redacted>)"


def scaffold() -> str:
    header = (
        "# Local credentials: never commit or share this file. Values are literal.\n"
        "# Set the exact source origin and application context before adding keys.\n"
        "SDP_HOST=\n"
        "# OPTIONAL SDP_API_KEY: single-key mode or deliberate directory-discovery key.\n"
        "# With numbered slots, blank = slots define scope; no automatic discovery.\n"
        "SDP_API_KEY=\n"
        "# OPTIONAL SDP_DIRECTORY_API_KEY: directory-only recovery; never module collection.\n"
        "# Blank = no separate directory-key recovery; ESM Directory needs no new key type.\n"
        "SDP_DIRECTORY_API_KEY=\n"
        "# OPTIONAL SDP_GLOBAL_API_KEY and SDP_GLOBAL_PORTAL_ID: explicit ESM Org access.\n"
        "# In multi-key mode, leave both blank = Orguser coverage gap when applicable.\n"
        "# Context ID is administrator-verified, never a slot number. See credential guide.\n"
        "SDP_GLOBAL_API_KEY=\nSDP_GLOBAL_PORTAL_ID=\n"
        "# OPTIONAL SDP_BRAND_FILE and SDP_PREPARED_FOR: branded copies after each run.\n"
        "# Brand JSON path, preset name or none; blank = CompleteTech LLC preset.\n"
        "SDP_BRAND_FILE=\nSDP_PREPARED_FOR=\n"
        "# Slot numbers are positions, NOT portal IDs. Add 21, 22, ... if needed.\n"
    )
    return header + "".join(
        f"\nSDP_INSTANCE_{i:02d}_PORTAL_ID=\nSDP_INSTANCE_{i:02d}_API_KEY=\n"
        for i in range(1, 21))


def application_directory() -> Path:
    root = Path(__file__).resolve().parent.parent
    # Under zipimport the package's parent is the archive, not a directory.
    return root if root.is_dir() else root.parent


def parse_env(path: Path) -> dict[str, str]:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Local environment file exceeds 1 MiB.")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeError:
        raise ValueError("Local environment file must be UTF-8.") from None
    if len(content.splitlines()) > MAX_LINES or any(
            ord(c) < 32 and c not in "\n\r\t" or ord(c) == 127 for c in content):
        raise ValueError("Local environment file exceeds line limits or contains control characters.")
    values: dict[str, str] = _SecretValues()
    for number, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, sep, value = line.partition("=")
        name, value = name.strip(), value.strip()
        if not sep or not NAME.fullmatch(name) or name in values:
            raise ValueError(f"Invalid or duplicate local environment assignment at line {number}.")
        if value.startswith(("'", '"')):
            end = value.find(value[0], 1)
            if end < 0 or value[end + 1:].strip() and not value[end + 1:].strip().startswith("#"):
                raise ValueError(f"Invalid local environment quoting at line {number}.")
            value = value[1:end]
        else:
            # A hash only begins a comment at the start or after whitespace.
            value = re.split(r"(?:^|\s)#", value, maxsplit=1)[0].rstrip()
        if len(value) > 8192:
            raise ValueError(f"Local environment value too long at line {number}.")
        values[name] = value
    return values


@contextmanager
def local_environment(path: str | None = None, *, disabled: bool = False,
                      create: bool = True):
    """Overlay only absent process variables, restoring them even on failure.

    Yield the original file host when file-provided credentials are active so
    a process host override cannot silently redirect those credentials.
    """
    added: list[str] = []
    file_host = None
    try:
        if not disabled:
            target = Path(path).expanduser().resolve() if path is not None else application_directory() / ".env"
            if path is None and create and not target.exists():
                try:
                    # Exclusive creation preserves concurrent setup and existing files.
                    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                except FileExistsError:
                    pass
                else:
                    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                        stream.write(scaffold())
            if target.exists() or path is not None:
                values = parse_env(target)
                file_credentials = [name for name, value in values.items()
                                    if value and name not in os.environ and
                                    (name.endswith("_API_KEY") or name == "SDP_API_KEY")]
                if file_credentials:
                    file_host = values.get("SDP_HOST")
                    if not file_host:
                        raise ValueError("File-provided credentials require SDP_HOST in the same local environment file.")
                for name, value in values.items():
                    if name not in os.environ:
                        os.environ[name] = value
                        added.append(name)
        yield file_host
    finally:
        for name in added:
            os.environ.pop(name, None)


def slot_assignments(host: str, *, allow_http: bool = False,
                     file_host: str | None = None) -> list[dict[str, str]]:
    slots: dict[int, dict[str, str]] = {}
    spellings: dict[int, str] = {}
    for name in os.environ:
        if not name.startswith("SDP_INSTANCE_"):
            continue
        match = SLOT.fullmatch(name)
        if not match or int(match[1]) < 1:
            raise ValueError("Invalid numbered instance environment-variable name.")
        index = int(match[1])
        if index in spellings and spellings[index] != match[1]:
            raise ValueError("Duplicate numbered instance slot.")
        spellings[index] = match[1]
        slot = slots.setdefault(index, {})
        if match[2] in slot:
            raise ValueError("Duplicate numbered instance slot.")
        slot[match[2]] = name
    entries = []
    seen = set()
    for _, slot in sorted(slots.items()):
        pid = os.environ.get(slot.get("PORTAL_ID", ""), "").strip()
        key_ref = slot.get("API_KEY", "")
        key = os.environ.get(key_ref, "")
        if not pid and not key:
            continue
        if not pid:
            raise ValueError("A populated instance key requires its explicit portal ID.")
        pid = portal_identifier(pid)
        if pid in seen:
            raise ValueError("Duplicate portal ID in numbered instance assignments.")
        seen.add(pid)
        if key:
            prepare_api_key(key)
        # An ID-only entry deliberately stays unassessed, including interactively.
        entries.append({"id": pid, "env": key_ref or slot["PORTAL_ID"].replace("_PORTAL_ID", "_API_KEY")})
    if entries or os.environ.get("SDP_GLOBAL_API_KEY"):
        expected = os.environ.get("SDP_HOST")
        if not expected or _binding_host(expected, allow_http) != _binding_host(host, allow_http):
            raise ValueError("Numbered/global credentials require a matching SDP_HOST and application context.")
    if file_host is not None and _binding_host(file_host, allow_http) != _binding_host(host, allow_http):
        raise ValueError("Local environment credential host/application context does not match this assessment.")
    return entries
