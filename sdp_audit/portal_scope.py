"""Resolve an entire portal scope once, without restarting or guessing IDs.

Directory enumeration remains an authorization boundary. On a denied or
unsupported directory, accept a directory-only credential or a complete
user-verified scope, and continue through the ORIGINAL collector and scheduler.
Only non-secret host-bound IDs/labels can be saved, with explicit consent.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from .artifacts import atomic_write_bytes
from .credentials import acquire_api_key
from .models import EnvironmentSnapshot, PortalInfo, Topology
from .topology import _label, discover_topology, portal_identifier
from .transport import _normalize_base_url

MAX_SCOPE_BYTES = 1024 * 1024
STOP_OUTCOMES = {"AUTHENTICATION_FAILED", "INTERRUPTED", "TIME_BUDGET_REACHED", "REQUEST_BUDGET_REACHED"}


def canonical_host(host: str) -> str:
    """Bind profiles to scheme, origin AND context, normalizing default ports."""
    parts = urlsplit(_normalize_base_url(host, allow_http=True))
    hostname = parts.hostname or ""
    netloc = "[" + hostname + "]" if ":" in hostname else hostname
    if parts.port and (parts.scheme, parts.port) not in {("https", 443), ("http", 80)}:
        netloc += ":" + str(parts.port)
    return urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def default_scope_path(host: str) -> Path:
    name = hashlib.sha256(canonical_host(host).encode("utf-8")).hexdigest() + ".json"
    return Path.home() / ".sdp-cloud-readiness" / "portal-scopes" / name


def _portal(identifier: Any, name: Any = None) -> PortalInfo:
    value = portal_identifier(identifier)
    return PortalInfo(id=value, name=_label(name) or "Portal " + value,
                      discovered=False, discovery_source="user-verified portal scope")


def _unique(portals: list[PortalInfo]) -> list[PortalInfo]:
    result: dict[str, PortalInfo] = {}
    for portal in portals:
        if portal.id not in result:
            result[portal.id] = portal
    return list(result.values())


def parse_portal_list(text: str, host: str) -> list[PortalInfo]:
    """Parse only positive IDs or same-origin URLs with an explicit PORTALID.

    URLs are NEVER fetched. Ranges, numerical sequences and alias guessing are
    not supported. Unknown URL query parameters are rejected to avoid accepting
    tokens/cookies or record content as a purported portal directory.
    """
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_SCOPE_BYTES:
        raise ValueError("Portal list exceeds the local input limit.")
    if any(ord(ch) < 32 and ch not in "\r\n\t" for ch in text):
        raise ValueError("Portal list contains unsupported control characters.")
    entries = [part for part in re.split(r"[,;\s]+", text.strip()) if part]
    if not entries:
        raise ValueError("Provide at least one verified portal ID or portal link.")
    result = []
    for entry in entries:
        if re.fullmatch(r"[0-9]{1,128}", entry, flags=re.ASCII):
            result.append(_portal(entry))
            continue
        try:
            url = urlsplit(entry)
            if url.scheme not in {"https", "http"} or url.username is not None or url.password is not None or url.fragment:
                raise ValueError
            base = urlsplit(canonical_host(host))
            origin = canonical_host(urlunsplit((url.scheme, url.netloc, "", "", "")))
            expected = canonical_host(urlunsplit((base.scheme, base.netloc, "", "", "")))
            if origin != expected or (base.path and not url.path.startswith(base.path + "/") and url.path != base.path):
                raise ValueError
            params = parse_qsl(url.query, keep_blank_values=True, strict_parsing=True)
            if len(params) != 1 or params[0][0].casefold() != "portalid":
                raise ValueError
            result.append(_portal(params[0][1]))
        except (ValueError, UnicodeError):
            raise ValueError("Use verified numeric IDs or same-host links containing only a PORTALID query parameter. Ranges and arbitrary URLs are not supported.") from None
    return _unique(result)


def read_scope(path: Path, host: str, sanitize: Callable[[str], str] = lambda value: value) -> list[PortalInfo]:
    """Read a bounded, strict, non-secret manifest; never import raw API dumps."""
    with path.open("rb") as stream:
        raw = stream.read(MAX_SCOPE_BYTES + 1)
    if len(raw) > MAX_SCOPE_BYTES:
        raise ValueError("Portal scope file exceeds 1 MiB.")
    try:
        data = json.loads(sanitize(raw.decode("utf-8-sig")))
        if not isinstance(data, dict) or set(data) - {"schema_version", "host", "portals", "saved_at"}:
            raise ValueError
        if data.get("schema_version") != 1 or isinstance(data.get("schema_version"), bool):
            raise ValueError
        if not isinstance(data.get("host"), str) or canonical_host(data["host"]) != canonical_host(host):
            raise ValueError("Portal scope file does not match this host and application context.")
        rows = data.get("portals")
        if not isinstance(rows, list) or not rows:
            raise ValueError
        portals = []
        for row in rows:
            if not isinstance(row, dict) or set(row) - {"id", "name"}:
                raise ValueError
            if row.get("name") is not None and not isinstance(row["name"], str):
                raise ValueError
            portals.append(_portal(row.get("id"), row.get("name")))
        return _unique(portals)
    except (ValueError, UnicodeError, RecursionError, TypeError):
        raise ValueError("Invalid or mismatched portal scope file. Use the host-bound portals.example.json format; no keys, raw API responses or other fields are accepted.") from None


def save_scope(path: Path, host: str, portals: list[PortalInfo],
               sanitize: Callable[[str], str] = lambda value: value) -> None:
    """Write only normalized host, IDs, bounded labels and a save timestamp."""
    safe_host = canonical_host(host)
    if sanitize(safe_host) != safe_host or sanitize(str(path)) != str(path):
        raise ValueError("Credentials must not appear in a portal scope path or host.")
    rows = []
    for portal in _unique(portals):
        identifier = portal_identifier(sanitize(portal.id))
        rows.append({"id": identifier, "name": _label(sanitize(portal.name)) or "Portal " + identifier})
    if not rows:
        raise ValueError("An empty portal scope cannot be saved.")
    data = {"schema_version": 1, "host": safe_host,
            "saved_at": datetime.now(timezone.utc).isoformat(), "portals": rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(path, (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    # Read-back validates format and host binding too; no success on a failed write.
    read_scope(path, host, sanitize)


@dataclass
class ScopeOptions:
    all_portals: bool = False
    seed_ids: list[str] | None = None
    portal_file: str | None = None
    non_interactive: bool = False
    no_portal_cache: bool = False
    save_portals: bool = False
    directory_key: bool = False
    directory_key_env: str | None = None
    key_input: str = "auto"
    cache_path: Path | None = None  # Test injection; runtime uses host-bound home path.


class PortalScopeResolver:
    def __init__(self, client: Any, options: ScopeOptions, *, max_portals: int = 100,
                 page_size: int = 100, progress: Callable[..., Any] | None = None):
        self.client = client
        self.options = options
        self.max_portals = max_portals
        self.page_size = page_size
        self.progress = progress
        self._directory_attempted = False
        self._file_portals = (read_scope(Path(options.portal_file).expanduser(), client.base_url,
                                        client.sanitize_local_text) if options.portal_file else None)

    @property
    def interactive(self) -> bool:
        return not self.options.non_interactive and sys.stdin.isatty()

    def _sanitize(self, value: str) -> str:
        return self.client.sanitize_local_text(value)

    def _merge(self, topology: Topology, portals: list[PortalInfo], source: str) -> Topology:
        before = {portal.id for portal in topology.portals}
        additions = [p for p in portals if p.id not in before]
        if not additions:
            return topology
        combined = _unique(topology.portals + additions)
        for portal in additions:
            portal.discovery_source = source
        topology.portals = combined[:self.max_portals]
        topology.directory_outcome = topology.directory_outcome or topology.outcome
        topology.complete = False  # A supplied list cannot certify directory visibility.
        topology.mode = "assisted"
        topology.selection_source = source
        topology.outcome = "RECORD_LIMIT_REACHED" if len(combined) > self.max_portals else "INCOMPLETE"
        topology.limitations = [note for note in topology.limitations
                               if not note.startswith("No portal identifiers were obtained")]
        topology.limitations.append(
            "A verified local portal list supplements directory discovery. Every selected portal is tested with its assigned collection credential; "
            "other portals may exist, and a saved list is not a live directory or proof of module access.")
        if len(combined) > self.max_portals:
            topology.limitations.append("The explicit max-portals limit restricted this list; omitted portals were not assessed.")
        return topology

    def _directory(self, topology: Topology) -> Topology:
        self._directory_attempted = True
        print("Directory key: used only for GET /api/v3/portals. Collection credential assignments are unchanged.", flush=True)
        mode = "auto" if self.options.directory_key_env else self.options.key_input
        if mode == "auto" and not self.options.directory_key_env:
            # Avoid silently reusing SDP_API_KEY instead of asking for a different key.
            mode = "dialog" if sys.platform == "win32" else "console"
        name = self.options.directory_key_env or "SDP_DIRECTORY_KEY"
        key = acquire_api_key(mode, name)
        reader = self.client.directory_reader(key)
        del key
        try:
            resolved = discover_topology(reader, page_size=self.page_size, max_portals=self.max_portals,
                                        progress=self.progress)
        finally:
            reader.close()
        original = topology
        resolved.credential_scope = "directory_key"
        resolved.selection_source = "directory_key"
        resolved.directory_outcome = resolved.outcome
        for diagnostic in resolved.diagnostics:
            diagnostic["credential_scope"] = "directory_key"
        resolved.diagnostics = original.diagnostics + resolved.diagnostics
        resolved.limitations.append(
            "A separate directory-only credential was attempted. Its identity, role assignments and relationship to the initial key are not inferred. "
            "Only a successful directory response establishes directory visibility; module inventories use their assigned collection credentials.")
        # Preserve known IDs if the second credential has narrower directory visibility.
        missing = [p for p in original.portals if p.id not in {q.id for q in resolved.portals}]
        if resolved.outcome in {"TIME_BUDGET_REACHED", "REQUEST_BUDGET_REACHED", "INTERRUPTED"}:
            resolved.portals = _unique(resolved.portals + missing)[:self.max_portals]
            return resolved
        if resolved.outcome == "AUTHENTICATION_FAILED":
            # A bad DIRECTORY key must not poison the successfully usable scan key.
            resolved.outcome = "INCOMPLETE"
        return self._merge(resolved, missing, "earlier verified portal metadata")

    def _save(self, topology: Topology, ask: bool) -> None:
        if not topology.portals:
            return
        if topology.outcome == "RECORD_LIMIT_REACHED":
            print("The portal selection was capped. A partial list will not overwrite a saved whole-portal profile.", flush=True)
            return
        want = self.options.save_portals
        if ask and not want and not self.options.no_portal_cache:
            want = input("Remember this entire portal list for this host (IDs/names only, no keys)? [y/N]: ").strip().lower() in {"y", "yes"}
        if not want:
            return
        path = self.options.cache_path or default_scope_path(self.client.base_url)
        try:
            save_scope(path, self.client.base_url, topology.portals, self._sanitize)
        except (OSError, ValueError):
            print("Portal list could not be saved. The current scan will still use the selected portals; no saved path is being asserted.", flush=True)
        else:
            print("Verified non-secret portal profile saved for this host. Future runs refresh directory discovery and use this list only when needed.", flush=True)

    def __call__(self, topology: Topology, env: EnvironmentSnapshot) -> Topology:
        if topology.outcome in STOP_OUTCOMES:
            return topology
        # A legacy explicit target without --all-portals remains a restriction.
        if topology.mode == "explicit":
            return topology
        if env.settings.get("diagnose_only"):
            # Discovery-only mode suppresses local-list/cache recovery and ALL
            # module reads, not a separately requested directory comparison.
            # The caller still owns the sole shared transport and budgets.
            if (not topology.complete
                    and (self.options.directory_key or self.options.directory_key_env)):
                try:
                    topology = self._directory(topology)
                except (ValueError, OSError):
                    print("The separate directory attempt could not be completed. No key was displayed or saved.", flush=True)
            return topology
        if self.options.seed_ids:
            topology = self._merge(topology, [_portal(value) for value in self.options.seed_ids], "user-supplied all-portals seeds")
        if self.options.portal_file:
            portals = self._file_portals or []
            topology = self._merge(topology, portals, "user-supplied portal file")
        if topology.complete:
            self._save(topology, False)
            return topology
        if self.options.directory_key or self.options.directory_key_env:
            try:
                topology = self._directory(topology)
            except (ValueError, OSError):
                print("Directory-key input was not accepted. No key was displayed or saved; verified-list recovery remains available.", flush=True)
            if topology.complete or topology.outcome in STOP_OUTCOMES:
                self._save(topology, False)
                return topology
        used_cache = False
        if not self.options.no_portal_cache and not self.options.portal_file:
            path = self.options.cache_path or default_scope_path(self.client.base_url)
            try:
                if path.exists():
                    portals = read_scope(path, self.client.base_url, self._sanitize)
                    topology = self._merge(topology, portals, "saved host-bound portal profile")
                    used_cache = True
                    print("Directory discovery is incomplete; reusing the saved portal list for this host. Module permissions are rechecked now.", flush=True)
            except (OSError, ValueError):
                print("Saved portal profile is invalid, inaccessible or for a different host; it was not used.", flush=True)
        supplied = bool(self.options.portal_file or used_cache)
        if self.interactive and not supplied:
            print("\nAutomatic portal discovery is incomplete (" + topology.outcome + "). No portal IDs will be guessed.", flush=True)
            if self._directory_attempted:
                print("A separate directory-only credential has already been attempted and did not establish a complete list. D is unavailable for this run; no additional credential retry is required.", flush=True)
            else:
                print("D = try one separate directory-only credential (directory visibility is not guaranteed).", flush=True)
            print("Continue this SAME run: L = all verified portal IDs/links; F = a portal scope JSON file.", flush=True)
            print("Selected portals use their assigned collection credentials. Enter finishes with only already-known IDs; with none, only diagnostic reports are written.", flush=True)
            for attempt in range(3):
                choices = "L/F/Enter" if self._directory_attempted else "D/L/F/Enter"
                try:
                    choice = input("Portal scope [" + choices + "]: ").strip().casefold()
                except EOFError:
                    # An input stream closing is not a user interrupt or an
                    # authentication receipt. Preserve the discovery outcome.
                    break
                if not choice:
                    if not topology.portals:
                        print("No portal IDs are available. Finishing with diagnostic reports only; no module assessment will run.", flush=True)
                    break
                try:
                    if choice == "d" and self._directory_attempted:
                        print("A directory-only credential was already attempted in this run. No repeat request was made. Choose L or F for the complete verified scope, or Enter to finish.", flush=True)
                        continue
                    if choice == "d":
                        topology = self._directory(topology)
                        if topology.complete or topology.outcome in STOP_OUTCOMES:
                            break
                        print("Directory credential did not establish a complete list. Supply verified IDs or a file to continue without restarting.", flush=True)
                        continue
                    if choice == "l":
                        text = input("All verified portal IDs or same-host PORTALID links, separated by commas (NOT an API key): ")
                        portals = parse_portal_list(self._sanitize(text), self.client.base_url)
                        topology = self._merge(topology, portals, "interactive verified portal list")
                    elif choice == "f":
                        path = input("Local portal scope JSON file: ").strip().strip('"')
                        portals = read_scope(Path(path).expanduser(), self.client.base_url, self._sanitize)
                        topology = self._merge(topology, portals, "interactive verified portal file")
                    else:
                        print("Choose " + ("L or F" if self._directory_attempted else "D, L or F") + "; no request was made.", flush=True)
                        continue
                    self._save(topology, True)
                    break
                except (ValueError, OSError):
                    print("Portal input was not accepted. Use the verified list/file format; supplied input is not repeated.", flush=True)
        elif not supplied and not topology.complete and not topology.portals:
            print("Directory discovery is unavailable. Unattended runs require --portal-file or --portal-ids with the full verified list; no IDs were guessed.", flush=True)
        if self.options.save_portals:
            self._save(topology, False)
        env.settings["portal_discovery_mode"] = topology.mode
        if topology.portals:
            print("One assessment will cover " + str(len(topology.portals)) + " selected portals using assigned collection credentials and shared global budgets.", flush=True)
        return topology
