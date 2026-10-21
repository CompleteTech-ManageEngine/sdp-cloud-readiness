"""Non-secret, host-bound credential assignments for a single assessment.

Secret values are held only in memory. Profiles contain environment
references, never keys; a reference grants only its explicitly listed scope.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from .credentials import acquire_api_key, prepare_api_key
from .topology import portal_identifier
from .transport import _binding_host


def _portal(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Credential assignment requires a decimal portal ID.")
    return portal_identifier(value)


def _env(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", value, re.ASCII):
        raise ValueError("Credential assignment requires an environment-variable name.")
    return value


def read_assignments(path: str, host: str, *, allow_http: bool = False) -> dict[str, Any]:
    with Path(path).open("rb") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("Credential assignment file exceeds 1 MiB.")
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate credential assignment field.")
            result[key] = value
        return result
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique)
    if (not isinstance(data, dict) or set(data) - {"schema_version", "host", "portals", "global"}
            or type(data.get("schema_version")) is not int or data["schema_version"] != 1):
        raise ValueError("Unsupported credential assignment schema.")
    if not isinstance(data.get("host"), str) or _binding_host(data["host"], allow_http) != _binding_host(host, allow_http):
        raise ValueError("Credential assignment host/application context does not match this assessment.")
    portals = data.get("portals", [])
    if not isinstance(portals, list) or len(portals) > 10000:
        raise ValueError("Credential portals must be a bounded list.")
    seen = set()
    for entry in portals:
        if not isinstance(entry, dict) or set(entry) != {"id", "env"}:
            raise ValueError("Portal assignments accept only id and env, never secret values.")
        pid = _portal(entry["id"])
        entry["id"] = pid
        _env(entry["env"])
        if pid in seen:
            raise ValueError("Duplicate portal credential assignment.")
        seen.add(pid)
    global_entry = data.get("global")
    if global_entry is not None:
        if not isinstance(global_entry, dict) or set(global_entry) != {"portal_id", "env"}:
            raise ValueError("Global assignment accepts only portal_id and env.")
        global_entry["portal_id"] = _portal(global_entry["portal_id"])
        _env(global_entry["env"])
    return data


class CredentialSetup:
    """Bind configured keys before discovery and prompt after scope resolution."""

    def __init__(self, client: Any, *, path: str | None = None,
                 global_env: str | None = None, global_portal: str | None = None,
                 non_interactive: bool = False, mode: str = "auto",
                 slot_entries: list[dict[str, str]] | None = None):
        self.client = client
        self.interactive = not non_interactive and sys.stdin.isatty()
        self.mode = mode
        self._keys: dict[str, str] = {}
        data = read_assignments(path, client.base_url, allow_http=client._allow_http) if path else {}
        entries = list(data.get("portals", []))
        configured_ids = {entry["id"] for entry in entries}
        self._slot_ids = {entry["id"] for entry in slot_entries or []}
        if configured_ids & self._slot_ids:
            raise ValueError("Portal credential is assigned by both numbered slots and the credential file.")
        entries.extend(slot_entries or [])
        global_entry = data.get("global")
        if bool(global_env) != bool(global_portal):
            raise ValueError("Global key reference and portal context must be supplied together.")
        if global_env:
            if global_entry is not None:
                raise ValueError("Global credential must be assigned in only one place.")
            global_entry = {"env": _env(global_env), "portal_id": _portal(global_portal)}
        # Validate all references first, then register every available secret
        # before any network response, interactive scope entry or local output.
        references = {entry["env"] for entry in entries}
        if global_entry:
            references.add(global_entry["env"])
        values = {}
        for ref in references:
            raw = os.environ.get(ref)
            if raw:
                key = prepare_api_key(raw).value
                client.register_credential(key)
                values[ref] = key
        for entry in entries:
            pid = entry["id"]
            if entry["env"] in values:
                key = values[entry["env"]]
                client.bind_portal_credential(client.base_url, pid, key)
                self._keys[pid] = key
        if global_entry and global_entry["env"] in values:
            client.bind_global_credential(client.base_url, global_entry["portal_id"], values[global_entry["env"]])

    def __repr__(self) -> str:
        return "CredentialSetup(credentials=<redacted>)"

    def resolve(self, topology: Any) -> None:
        if not self.interactive:
            return
        for portal in topology.portals:
            pid = portal.id
            if not portal.selected or pid in self._keys or pid in self._slot_ids:
                continue
            # IDs come from the validated topology, but still pass the redactor.
            label = self.client.sanitize_local_text(pid)
            print("Collection credential for portal " + label + ".", flush=True)
            print("Enter = new hidden key; S = leave unassessed; or enter a previously assigned portal ID to reuse its key.", flush=True)
            choice = input("Credential assignment: ").strip()
            if choice.lower() == "s":
                continue
            if choice:
                if choice not in self._keys:
                    raise ValueError("Reuse requires a previously assigned portal ID.")
                key = self._keys[choice]
            else:
                mode = self.mode if self.mode != "auto" else "dialog" if sys.platform == "win32" else "console"
                key = acquire_api_key(mode)
            self.client.bind_portal_credential(self.client.base_url, pid, key)
            self._keys[pid] = key
