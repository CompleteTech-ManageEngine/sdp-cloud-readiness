"""Instance-boundary checkpoints containing report evidence, never source rows."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any
import uuid

from . import __version__
from .artifacts import atomic_write_bytes
from .collect import Collector
from .environment import EnvironmentCollector, _REASONS, _TERMINAL_STOPS
from .environment_analysis import analyze_environment
from .models import EnvironmentSnapshot, PortalInfo, PortalSnapshot, Snapshot, Topology, Finding
from .report import _sanitize_assessment
from .topology import discover_topology, portal_identifier
from .transport import _binding_host

MAX_CHECKPOINT_BYTES = 64 * 1024 * 1024


def contract(client, options, env_options, resources, answers):
    """No credential values, hashes, variable references, or input file paths."""
    return {
        "host": _binding_host(client.base_url, client._allow_http),
        "multi_key": client.multi_key,
        "allow_http": client._allow_http, "tls_verification": not client._insecure_tls,
        "global_portal_id": client.global_portal_id if client.multi_key else None,
        "collection": asdict(options), "environment": asdict(env_options),
        "resources": [asdict(spec) for spec in resources],
        # Business answers affect analysis. Bind them without retaining arbitrary text.
        "answers_digest": hashlib.sha256(json.dumps(answers, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest(),
    }


def read_checkpoint(path: Path) -> dict[str, Any]:
    """Read a bounded, versioned JSON document; never execute serialized code."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_CHECKPOINT_BYTES + 1)
        if len(raw) > MAX_CHECKPOINT_BYTES:
            raise ValueError
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError
                result[key] = value
            return result
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
        if (not isinstance(data, dict) or set(data) != {
                "schema_version", "tool_version", "run_id", "generated_at", "contract",
                "topology", "portals", "global_coverage", "global_done", "history", "sha256"}
                or type(data["schema_version"]) is not int or data["schema_version"] != 1
                or data["tool_version"] != __version__):
            raise ValueError
        checksum = data.pop("sha256")
        actual = hashlib.sha256(_encode(data)).hexdigest()
        data["sha256"] = checksum
        if checksum != actual:
            raise ValueError
        uuid.UUID(data["run_id"])
        datetime.fromisoformat(data["generated_at"])
        if (not isinstance(data["contract"], dict) or not isinstance(data["portals"], dict)
                or not isinstance(data["global_coverage"], list)
                or type(data["global_done"]) is not bool or not isinstance(data["history"], list)):
            raise ValueError
        if not data["global_done"] and data["global_coverage"]:
            raise ValueError
        topology = restore_topology(data["topology"])
        selected = {p.id for p in topology.portals if p.selected}
        if not selected or not set(data["portals"]).issubset(selected):
            raise ValueError
        for pid, entry in data["portals"].items():
            if (not isinstance(entry, dict) or entry.get("portal_id") != pid or
                    not {"metadata", "coverage", "findings", "fields", "diagnostics", "capabilities"}.issubset(entry)):
                raise ValueError
            if set(entry) - {"portal_id", "portal_name", "metadata", "summary", "coverage", "findings",
                             "fields", "diagnostics", "capabilities", "checkpoint_reused"}:
                raise ValueError
            for name in ("coverage", "findings", "fields", "diagnostics", "capabilities"):
                if not isinstance(entry[name], list) or any(not isinstance(row, dict) for row in entry[name]):
                    raise ValueError
            for row in entry["findings"]:
                if Finding(**row).portal_id != pid:
                    raise ValueError
            if any(row.get("portal_id") != pid for row in entry["coverage"]):
                raise ValueError
        if any(not isinstance(row, dict) or row.get("scope") != "environment" for row in data["global_coverage"]):
            raise ValueError
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError):
        raise ValueError("Invalid, damaged or incompatible checkpoint; no reads were sent.") from None
    return data


def restore_topology(value):
    fields = dict(value)
    fields["portals"] = [PortalInfo(**item) for item in fields["portals"]]
    ids = [portal_identifier(p.id) for p in fields["portals"]]
    if (len(ids) != len(set(ids)) or any(p.id != pid for p, pid in zip(fields["portals"], ids))
            or any(type(p.selected) is not bool or not isinstance(p.name, str) for p in fields["portals"])):
        raise ValueError
    return Topology(**fields)


def _encode(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


@contextmanager
def checkpoint_lock(path: Path):
    """Fail closed for concurrent writers; never steal a possibly live lock."""
    lock = path.with_name(path.name + ".lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError("Checkpoint is locked by another run or a stopped process. Verify that no run uses it before removing its .lock file.") from None
    try:
        with os.fdopen(fd, "w", encoding="ascii") as stream:
            stream.write(str(os.getpid()))
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        lock.unlink()


class ResumableAssessment:
    """Finish one instance before the next, committing only sanitized evidence.

    A stopped instance is read again, not blended with its older partial rows.
    Checkpoint paths and contract are validated before directory/module reads.
    """
    def __init__(self, client, resources, options, env_options, progress, scope_resolver,
                 output: Path, *, resume: Path | None = None, requested_scope=None):
        self.client, self.resources = client, resources
        # In checkpoint mode, finish list pagination before sampling so a
        # sampling reservation cannot be mistaken for a completed instance.
        self.options, self.env_options = replace(options, inventory_budget_fraction=1.0), env_options
        self.progress, self.scope_resolver = progress, scope_resolver
        self.output, self.resume = output, resume
        self.credential_setup = None
        self.path = output / "checkpoint.json"
        self.requested_scope = sorted(requested_scope or [])

    def _save(self, env, completed, global_done, history, binding, run_id):
        # Use the exact report privacy projection, not dataclass serialization
        # of snapshots (which contain source records and raw descriptions).
        report = _sanitize_assessment(analyze_environment(env))
        portals = {p["portal_id"]: p for p in report["portals"] if p["portal_id"] in completed}
        data = {"schema_version": 1, "tool_version": __version__, "run_id": run_id,
                "generated_at": env.generated_at, "contract": binding,
                "topology": report["environment"]["topology"], "portals": portals,
                "global_coverage": report["global_resources"]["coverage"] if global_done else [],
                "global_done": global_done, "history": history}
        # The report topology contains derived evidence; keep only constructor fields.
        allowed = set(Topology.__dataclass_fields__)
        data["topology"] = {key: value for key, value in data["topology"].items() if key in allowed}
        # Registering secrets precedes this point. Scrub accidental echoes in all
        # metadata, including configured answers, numeric IDs and safe labels.
        data = self.client._redact_payload(data)
        data["sha256"] = hashlib.sha256(_encode(data)).hexdigest()
        payload = _encode(data)
        if len(payload) > MAX_CHECKPOINT_BYTES:
            raise ValueError("Checkpoint exceeds the supported size; prior checkpoint was preserved.")
        atomic_write_bytes(self.path, payload)
        if read_checkpoint(self.path)["sha256"] != data["sha256"]:
            raise ValueError("Checkpoint read-back failed.")

    def collect(self, env, portal_ids=None):
        # Lock the input for the whole continuation, as well as this output.
        if self.resume is not None:
            with checkpoint_lock(self.resume):
                return self._locked_collect(env, portal_ids)
        return self._locked_collect(env, portal_ids)

    def _locked_collect(self, env, portal_ids):
        with checkpoint_lock(self.path):
            return self._collect(env, portal_ids)

    def _collect(self, env, portal_ids):
        binding = contract(self.client, self.options, self.env_options, self.resources, env.manual_answers)
        binding["requested_scope"] = self.requested_scope
        history, completed, global_done = [], set(), False
        run_id = str(uuid.uuid4())
        if self.resume:
            data = read_checkpoint(self.resume)
            if data["contract"] != binding:
                raise ValueError("Checkpoint host, collection plan, credential mode/context or analysis answers differ. Reuse the original settings; only request/time budgets, pacing and timeout may change.")
            env.topology = restore_topology(data["topology"])
            if env.topology.outcome in _TERMINAL_STOPS:
                env.topology.directory_outcome = env.topology.directory_outcome or env.topology.outcome
                env.topology.outcome = "INCOMPLETE"
            selected = [p.id for p in env.topology.portals if p.selected]
            if portal_ids and set(portal_ids) != set(selected):
                raise ValueError("Checkpoint instance scope differs from the selected instance IDs.")
            env.generated_at, run_id = data["generated_at"], data["run_id"]
            env.retained_portals = deepcopy(data["portals"])
            env.retained_global_coverage = deepcopy(data["global_coverage"])
            if env.retained_global_coverage:
                env.source["orgusers_collection"] = "once_for_environment"
            history = list(data["history"])
            completed = set(env.retained_portals)
            global_done = data["global_done"]
            # Retained evidence describes its earlier credential, never proof
            # that today's key still has that access.
            for entry in env.retained_portals.values():
                entry["checkpoint_reused"] = True
        else:
            env.topology = discover_topology(self.client, portal_ids=portal_ids,
                page_size=self.options.page_size, max_portals=self.env_options.max_portals,
                progress=self.progress)
            if self.client.multi_key and env.topology.outcome == "AUTHENTICATION_FAILED":
                env.topology.directory_outcome = env.topology.outcome
                env.topology.outcome = "INCOMPLETE"
            if self.scope_resolver and env.topology.outcome not in _TERMINAL_STOPS:
                env.topology = self.scope_resolver(env.topology, env)
        selected = [p for p in env.topology.portals if p.selected]
        if not selected:
            raise ValueError("Resumable assessment requires a resolved instance scope. Resolve directory access or supply verified instance IDs first.")
        # Resolve current assignments through the existing binding mechanism,
        # even though completed evidence itself is not reauthenticated.
        setup = self.credential_setup
        if self.resume and setup is not None:
            setup.resolve(replace(env.topology, portals=[p for p in env.topology.portals
                if p.id not in completed]))
        for path in (self.path, self.resume):
            if path is not None and self.client.sanitize_local_text(str(path)) != str(path):
                raise ValueError("A credential must not appear in a checkpoint path.")
        for portal in selected:
            snapshot = Snapshot(env.generated_at, {**env.source, "portal_id": portal.id,
                "portal_name": portal.name}, env.settings, manual_answers=env.manual_answers, schema_version="2.0")
            Collector(self.client, self.resources, self.options).prepare(snapshot)
            env.portals[portal.id] = PortalSnapshot(portal, snapshot)
        attempt = {"pass": len(history) + 1, "started_at": datetime.now(timezone.utc).isoformat(),
                   "requests": 0, "elapsed_seconds": 0, "stop": None,
                   "reused_instances": len(completed), "run_id": run_id}
        history.append(attempt)
        env.resume_history = history
        def save():
            attempt.update(requests=self.client.stats.get("requests", 0),
                elapsed_seconds=self.client.stats.get("elapsed_seconds", 0), stop=env.stop_classification)
            self._save(env, completed, global_done, history, binding, run_id)
        print("Resumable assessment: instance-boundary checkpoints; {} completed instances reused. Interrupted instances restart.".format(len(completed)), flush=True)
        save()
        print("Checkpoint file: " + str(self.path), flush=True)
        try:
            for portal in selected:
                if portal.id in completed:
                    continue
                child = EnvironmentSnapshot(env.generated_at, dict(env.source), env.settings,
                                            manual_answers=env.manual_answers)
                topology = replace(deepcopy(env.topology), portals=[deepcopy(portal)])
                collector = EnvironmentCollector(self.client, self.resources, self.options,
                    replace(self.env_options, collect_orgusers=False), self.progress)
                collector.collect(child, topology=topology)
                env.portals[portal.id] = child.portals[portal.id]
                # Keep the canonical topology's operational evidence synchronized.
                portal.accessible = child.portals[portal.id].portal.accessible
                portal.access_status = child.portals[portal.id].portal.access_status
                portal.scan_status = child.portals[portal.id].portal.scan_status
                status = self.client.credential_status(portal.id) if self.client.multi_key else "valid"
                if child.stop_classification is None and status not in {"missing", "failed"}:
                    completed.add(portal.id)
                    print("Checkpoint progress: {}/{} instances finished (coverage gaps may remain).".format(
                        len(completed), len(selected)), flush=True)
                if child.stop_classification:
                    env.stop_classification, env.interrupted_reason = child.stop_classification, child.interrupted_reason
                self._stats(env)
                save()
                if child.stop_classification:
                    break
            if env.stop_classification is None and not global_done:
                global_env = EnvironmentSnapshot(env.generated_at, dict(env.source), env.settings,
                                                 manual_answers=env.manual_answers)
                collector = EnvironmentCollector(self.client, [], self.options,
                    replace(self.env_options, discover_fields=False), self.progress)
                collector.collect(global_env, topology=deepcopy(env.topology))
                env.global_snapshot = global_env.global_snapshot
                env.source["orgusers_collection"] = global_env.source.get("orgusers_collection", "not_selected")
                env.stop_classification, env.interrupted_reason = global_env.stop_classification, global_env.interrupted_reason
                state = env.source["orgusers_collection"]
                global_done = (global_env.stop_classification is None and state not in {
                    "credential_missing", "no_accessible_portal_context_confirmed"}
                    and (not self.client.multi_key or state != "once_for_environment"
                         or self.client.credential_status(global_scope=True) not in {"missing", "failed"}))
        except KeyboardInterrupt:
            env.stop_classification = "INTERRUPTED"
            env.interrupted_reason = _REASONS["INTERRUPTED"]
        finally:
            self._stats(env)
            save()
        return env

    def _stats(self, env):
        env.stats = dict(self.client.stats)
        env.authentication = str(env.stats.get("authentication", "unverified")).upper()
        env.stats.update(portals_discovered=sum(p.discovered for p in env.topology.portals),
            portals_selected=len(env.portals),
            portals_with_successful_scoped_reads=sum(p.portal.accessible is True for p in env.portals.values()),
            global_limiter_instances=1, stop_classification=env.stop_classification)
