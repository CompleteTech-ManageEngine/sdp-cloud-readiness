"""Interactive and unattended command-line entry point."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .catalog import ALLOWED_PATTERNS, GLOBAL_RESOURCES, RESOURCES, UNEXPOSED_FEATURES
from .collect import CollectionOptions
from .credentials import acquire_api_key, prepare_api_key
from .credential_setup import CredentialSetup
from .local_env import local_environment, slot_assignments
from .environment import EnvironmentCollector, EnvironmentOptions
from .environment_analysis import analyze_environment
from .resume import ResumableAssessment
from .portal_scope import PortalScopeResolver, ScopeOptions
from .models import Assessment, EnvironmentSnapshot
from .progress import ProgressPrinter, print_environment_coverage
from .report import render_report_documents
from .artifacts import Publication, atomic_write_bytes, failure_metadata, prepare_output, publish_documents
from .diagnostics import diagnostics_document, print_topology_diagnostics
from .transport import ApiError, ReadOnlyClient


ANSWER_FIELDS = {
    "source_build", "target_edition", "target_region", "api_scope_confirmed",
    "required_history_years", "required_audit_years", "needs_power_bi",
    "max_dashboard_lag_minutes", "uses_local_scripts", "needs_full_descriptions",
    "requires_legacy_history", "full_backup_requirement",
}
CONNECTION_FIELDS = {
    "multi_key", "credential_file", "global_key_env", "global_portal_id",
    "host", "portal_id", "portal_ids", "portal_file", "max_portals", "metadata_limit", "ca_file", "rpm", "page_size", "max_records", "detail_limit",
    "max_requests", "max_minutes", "timeout", "subresource_parents", "max_child_records", "count_policy",
}


class _SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse's default can echo arbitrary argument values, including a
        # credential pasted into an unsupported option. Never repeat them.
        self.print_usage(sys.stderr)
        self.exit(2, "Invalid command-line options. Run --help for supported flags and value types.\n")


class _HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    def _get_help_string(self, action: argparse.Action) -> str:
        if action.default is None:
            return action.help
        return super()._get_help_string(action)


def _cli_read_json(path: str, allowed: set[str]) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8-sig")
    if len(raw) > 1024 * 1024:
        raise ValueError("Settings file exceeds 1 MiB.")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Settings must be a JSON object.")
    unexpected = set(data) - allowed
    if unexpected:
        # Do not echo user-supplied keys or values; either could contain a secret.
        raise ValueError("Settings contain unsupported keys. Use the supplied example; API keys belong only in the secure prompt or environment.")
    return {key: value for key, value in data.items() if value is not None}


def _cli_parser() -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(
        allow_abbrev=False,
        description="Discover and assess every accessible ServiceDesk Plus on-premises portal for Cloud migration. GET only; one global rate limiter; local reports; Python standard library only.",
        formatter_class=_HelpFormatter,
        epilog="Examples:\n  python sdp_cloud_readiness.py\n  python sdp_cloud_readiness.py --all-portals\n  python sdp_cloud_readiness.py --all-portals --portal-file portals.json\n  python sdp_cloud_readiness.py --all-portals --directory-key\n  python sdp_cloud_readiness.py --portal-id 3\n  python sdp_cloud_readiness.py --portal-id 1 --portal-id 3\n  python sdp_cloud_readiness.py --portal-ids 1,3\n  python sdp_cloud_readiness.py --demo\n  python sdp_cloud_readiness.py --key-input dialog\n  python sdp_cloud_readiness.py --check-key-input\n  python sdp_cloud_readiness.py --check-output --output-dir E:\\sdp-reports\n  python sdp_cloud_readiness.py --diagnose\n\nDefault invocation prompts only for host and hidden API key, discovers portals,\nand assesses every discovered portal subject to shared global budgets.\nDiscovery unavailable: continue the SAME run with a directory-only key, a verified\nportal list/file, or a previously consented host-bound profile. No IDs are guessed.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--host", help="On-premises origin and optional context path, e.g. https://helpdesk.example.org:8443")
    parser.add_argument("--portal-id", action="append", help="Restrict to this explicit portal ID; repeat for multiple IDs. Default: discover all portals. No ID is guessed.")
    parser.add_argument("--portal-ids", help="Comma-separated explicit portal IDs; combines with repeated --portal-id")
    parser.add_argument("--all-portals", action="store_true", help="Scan the entire discovered/verified scope in ONE run. With --portal-id(s), use those IDs as seeds instead of a restriction. Does not guess missing IDs or bypass permissions.")
    parser.add_argument("--portal-file", help="Non-secret host-bound JSON portal list; supplements discovery and avoids re-entering IDs. See portals.example.json.")
    parser.add_argument("--directory-key", action="store_true", help="If directory discovery fails, prompt for a separately authorized hidden key ONLY for /portals; original key still collects every module.")
    parser.add_argument("--directory-key-env", help="Optional environment variable for a directory-only key on discovery failure. The value is never printed or saved.")
    parser.add_argument("--multi-key", action="store_true", default=None, help="Explicit per-instance collection keys; unassigned instances remain unassessed. The primary key, if supplied, is for directory discovery only.")
    parser.add_argument("--credential-file", help="Host-bound non-secret per-instance environment-reference assignments; enables multi-key mode.")
    parser.add_argument("--global-key-env", help="Environment reference explicitly authorizing global Orguser collection in multi-key mode.")
    parser.add_argument("--global-portal-id", help="Documented request context for the explicitly assigned global credential; requires --global-key-env.")
    parser.add_argument("--save-portals", action="store_true", help="Consent to save selected portal IDs/names under the user home directory, bound to this host. No credentials are saved.")
    parser.add_argument("--no-portal-cache", action="store_true", help="Do not load saved portal scope or ask to save it; explicit --save-portals still authorizes a save.")
    parser.add_argument("--non-interactive", action="store_true", help="Disable portal-recovery questions; supply a portal file/list or environment directory key when enumeration is unavailable.")
    parser.add_argument("--max-portals", type=int, help="Maximum discovered portals to retain; default 100; further topology remains unknown")
    parser.add_argument("--metadata-limit", type=int, help="Metadata targets per portal/module; default 20, zero selects all observed targets within global budgets")
    parser.add_argument("--api-key-env", default="SDP_API_KEY", help="Environment variable containing the API key in auto mode; explicit console/dialog mode bypasses it")
    parser.add_argument("--key-input", choices=("auto", "console", "dialog"), default="auto", help="Auto: environment key, otherwise masked Windows dialog or hidden console. Explicit console/dialog always prompts, bypassing environment keys. Dialog requires desktop/Tcl-Tk.")
    parser.add_argument("--check-key-input", action="store_true", help="Check hidden key entry and formatting locally, then exit; no host, HTTP calls or report files. Does not authenticate the key.")
    parser.add_argument("--check-output", action="store_true", help="Create and verify a synthetic local report set and ZIP, then exit; no credentials, host or HTTP calls. Use to diagnose missing reports.")
    parser.add_argument("--checkpoint", action="store_true", help="Save sanitized instance-boundary checkpoints; finish one instance at a time. Interrupted instances restart on resume.")
    parser.add_argument("--retry-failed", action="store_true", help="With --resume, explicitly retry instances with retained transient, parse or row-cap gaps; permanent permission/unsupported results are excluded.")
    parser.add_argument("--retry-portals", help="With --resume, comma-separated checkpoint instance IDs to recollect, including permission gaps after access changes.")
    parser.add_argument("--restart-all", action="store_true", help="With --resume, recollect all checkpoint instances and global work; permits explicit collection-limit changes.")
    parser.add_argument("--resume", help="Resume a checkpoint.json with fresh budgets and current explicit credentials; completed instances are reused, not reauthenticated.")
    parser.add_argument("--diagnose", action="store_true", help="Directory GETs only; no module inventory or saved-list recovery. Honors --directory-key/--directory-key-env for one requested secondary-credential attempt when initial discovery is incomplete.")
    parser.add_argument("--config", help="Optional non-secret connection settings JSON")
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument("--env-file", help="Local UTF-8 environment file; relative paths use the working directory. Default: .env beside the source entry point or portable app.")
    env_group.add_argument("--no-env", action="store_true", help="Do not load or create a local environment file; existing process environment still applies.")
    parser.add_argument("--answers", help="Optional business/target answers JSON; unknown answers stay explicit")
    parser.add_argument("--source-build", type=int, help="Optional known source build; recorded as user-supplied")
    parser.add_argument("--target-edition", choices=("Standard", "Professional", "Enterprise"))
    parser.add_argument("--target-region", help="Optional planned Cloud region, e.g. US, IN, EU")
    parser.add_argument("--rpm", type=float, help="Global requests/minute; default 30, single-flight, maximum 60")
    parser.add_argument("--count-policy", choices=("first", "always", "never"), help="Request total_count on first page only (default), every page, or never. Never avoids optional count calculations; pagination still requires termination evidence.")
    parser.add_argument("--page-size", type=int, help="Rows/page; default 100, maximum 100")
    parser.add_argument("--max-records", type=int, help="Max records per collection; default 5000, zero removes this cap")
    parser.add_argument("--detail-limit", type=int, help="Detail records per collection; default 20, zero selects all observed records")
    parser.add_argument("--subresource-parents", type=int, help="Requests whose notes/tasks are inspected; default 10, zero skips")
    parser.add_argument("--max-child-records", type=int, help="Max notes/tasks per sampled request; default 200")
    parser.add_argument("--max-requests", type=int, help="Total HTTP attempt budget including retries; default 500")
    parser.add_argument("--max-minutes", type=float, help="Wall-time budget for network assessment; default 20")
    parser.add_argument("--timeout", type=float, help="Per-request timeout seconds; default 30")
    parser.add_argument("--full-inventory", "--full", action="store_true", help="Remove per-collection row cap; time/request budgets and detail sampling still apply")
    parser.add_argument("--modules", help="Comma-separated collection keys from --list-endpoints. Omit for all; field_definitions enables module-aware field discovery with its documented supporting inventories")
    parser.add_argument("--ca-file", help="PEM certificate bundle for an internal/private CA")
    parser.add_argument("--allow-http", action="store_true", help="Explicitly permit unencrypted HTTP to a legacy source; prefer HTTPS")
    parser.add_argument("--insecure-tls", action="store_true", help="Explicitly disable certificate verification; this exception is recorded in the report")
    parser.add_argument("--output-dir", default="sdp-assessments", help="Parent directory for a new timestamped report folder")
    parser.add_argument("--list-endpoints", action="store_true", help="Show the closed GET allowlist and unexposed areas without connecting")
    parser.add_argument("--demo", action="store_true", help="Run a synthetic multi-portal example with the actual read-only transport and mocked responses; no network or credentials")
    parser.add_argument("--demo-scenario", choices=("single", "multi", "recovery", "multi_key"), default="multi", help="Fixture used with --demo")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress lines; final result paths are still printed")
    return parser


def _cli_options(args: argparse.Namespace) -> dict[str, Any]:
    settings: dict[str, Any] = {
        "count_policy": "first", "rpm": 30.0, "page_size": 100, "max_records": 5000, "detail_limit": 20,
        "max_requests": 500, "max_minutes": 20.0, "timeout": 30.0,
        "subresource_parents": 10, "max_child_records": 200,
        "max_portals": 100, "metadata_limit": 20,
    }
    if args.config:
        settings.update(_cli_read_json(args.config, CONNECTION_FIELDS))
    for key in CONNECTION_FIELDS:
        value = getattr(args, key, None)
        if value is not None:
            settings[key] = value
    for key in ("rpm", "max_minutes", "timeout"):
        value = settings[key]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value <= 0):
            raise ValueError("Rate, timeout and duration must be finite positive numbers.")
        settings[key] = float(value)
    if settings["rpm"] > 60:
        raise ValueError("Client rate is capped at 60 requests/minute. Use a lower rate when required by your server.")
    for key in ("page_size", "max_records", "detail_limit", "max_requests", "subresource_parents", "max_child_records", "max_portals", "metadata_limit"):
        value = settings[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("Collection limits must be nonnegative integers.")
    if not 1 <= settings["page_size"] <= 100:
        raise ValueError("Page size must be between 1 and 100.")
    if settings["max_requests"] < 1 or settings["max_child_records"] < 1:
        raise ValueError("Request and child-record budgets must be positive.")
    if settings["max_portals"] < 1:
        raise ValueError("The portal-discovery limit must be positive.")
    if not isinstance(settings["count_policy"], str) or settings["count_policy"] not in {"first", "always", "never"}:
        raise ValueError("Count policy must be first, always, or never.")
    ids: list[str] = []
    configured_ids = (settings.pop("portal_id", None), settings.pop("portal_ids", None))
    if args.portal_id is not None or args.portal_ids is not None:
        configured_ids = (args.portal_id, args.portal_ids)
    for value in configured_ids:
        if value is None or value == []:
            continue
        values = value if isinstance(value, list) else str(value).split(",") if isinstance(value, (str, int)) and not isinstance(value, bool) else None
        if values is None:
            raise ValueError("Portal IDs must be positive decimal IDs or a list of IDs.")
        ids.extend(str(item).strip() for item in values)
    import re
    if any(not re.fullmatch(r"[0-9]{1,40}", item) or int(item) <= 0 for item in ids):
        raise ValueError("Portal IDs must be positive ASCII decimal identifiers; no IDs were queried.")
    settings["portal_ids"] = list(dict.fromkeys(str(int(item)) for item in ids))
    settings["portal_discovery_mode"] = "explicit" if ids and not args.all_portals else "automatic"
    settings["all_portals"] = bool(args.all_portals)
    if settings.get("portal_file") is not None and not isinstance(settings["portal_file"], str):
        raise ValueError("Portal file must be a path to a non-secret JSON scope file.")
    if ids and settings.get("portal_file") and not args.all_portals:
        raise ValueError("Use --all-portals to combine a portal file with ID seeds; omit ID overrides for automatic all-portal scanning.")
    if args.full_inventory:
        settings["max_records"] = 0
    settings["max_runtime_seconds"] = settings["max_minutes"] * 60
    settings["read_only_get_only"] = True
    settings["attachment_downloads"] = False
    settings["tls_verification"] = not args.insecure_tls
    settings["allow_http"] = args.allow_http
    settings["credential_visibility_verified"] = False
    return settings


def _cli_answers(args: argparse.Namespace) -> dict[str, Any]:
    answers = _cli_read_json(args.answers, ANSWER_FIELDS) if args.answers else {}
    for key in ("source_build", "target_edition", "target_region"):
        value = getattr(args, key)
        if value is not None:
            answers[key] = value
    for key in ("api_scope_confirmed", "needs_power_bi", "uses_local_scripts", "needs_full_descriptions", "requires_legacy_history"):
        if key in answers and not isinstance(answers[key], bool):
            raise ValueError("Boolean answers must be true, false, or null.")
    for key in ("required_history_years", "required_audit_years", "max_dashboard_lag_minutes", "source_build"):
        if key in answers:
            value = answers[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError("Numeric answers must be finite, nonnegative numbers or null.")
    return answers


def _print_publication(receipt: Publication) -> bool:
    # Never construct or print a guessed report.html path. Reopen all documents
    # once more at the user-visible success boundary.
    receipt.verify()
    if receipt.complete:
        print("  Report files verified: reopened and SHA-256 checked.")
    else:
        print("  REPORT OUTPUT INCOMPLETE: one or more files could not be verified.", file=sys.stderr)
        for name, diagnostic in sorted(receipt.failures.items()):
            print("    " + name + ": " + str(diagnostic["classification"])
                  + " (errno=" + str(diagnostic["errno"]) + ", winerror=" + str(diagnostic["winerror"]) + ")", file=sys.stderr)
        print("  Use --check-output --output-dir <a short writable local directory>. No file-retention or security-policy cause is assumed.", file=sys.stderr)
    if "report.html" in receipt.paths:
        print("  Open verified HTML: " + str(receipt.paths["report.html"]))
    if "diagnostics.json" in receipt.paths:
        print("  Sanitized diagnostics: " + str(receipt.paths["diagnostics.json"]))
    if receipt.bundle is not None:
        print("  Verified report ZIP: " + str(receipt.bundle))
        print("  The ZIP contains report.html and the other reports even when an individual file could not be kept.")
    if receipt.paths:
        print("  Reports folder: " + str(receipt.directory))
    print("  Verification is point-in-time; it cannot guarantee that another process will not remove files later.")
    return receipt.complete


def _finish_assessment(snapshot: EnvironmentSnapshot, output: Path, quiet: bool) -> int:
    # Diagnostics must be visible without relying on a file the user cannot
    # locate. This also runs with --quiet and before analysis/report rendering.
    print_topology_diagnostics(snapshot)
    diagnostic_text = diagnostics_document(snapshot)
    try:
        atomic_write_bytes(output / "diagnostics.json", diagnostic_text.encode("utf-8"))
    except OSError:
        print("Diagnostic file could not yet be verified; console diagnostics remain available. Report publication and ZIP copy will still be attempted.", file=sys.stderr)
    if not quiet:
        print("\nAnalyzing collected evidence and writing local reports...", flush=True)
    assessment = analyze_environment(snapshot)
    if snapshot.source.get("demo"):
        assessment.notes.insert(0, "SYNTHETIC DEMONSTRATION ONLY. No actual ServiceDesk Plus instance was contacted.")
    if snapshot.settings.get("diagnose_only"):
        assessment.notes.insert(0, "DISCOVERY-ONLY DIAGNOSTIC RUN. Module inventories and migration impacts were not assessed.")
    if snapshot.interrupted_reason:
        assessment.notes.insert(0, snapshot.interrupted_reason)
    documents = render_report_documents(assessment)
    documents["diagnostics.json"] = diagnostic_text
    receipt = publish_documents(documents, output)
    receipt.verify()
    counts: dict[str, int] = {}
    for finding in assessment.findings:
        counts[finding.status] = counts.get(finding.status, 0) + 1
    if snapshot.settings.get("diagnose_only"):
        print("\nDiscovery-only diagnostic run; no module inventory was requested.")
    elif not snapshot.portals:
        print("\nASSESSMENT NOT PERFORMED: no portal module data was collected. Diagnostic outputs follow.")
    elif receipt.complete:
        print("\nAssessment written and read-back checked. Counts describe findings, not unique impacted records.")
    else:
        print("\nAssessment analysis completed, but report publication is incomplete.")
    for state in ("CONFIRMED_IMPACT", "NO_ISSUE_OBSERVED", "UNKNOWN", "MANUAL_CONFIRMATION"):
        print("  {}: {}".format(state, counts.get(state, 0)))
    print_environment_coverage(snapshot)
    if not _print_publication(receipt):
        return 1
    # 0 means documents were verified, never that Cloud migration is safe.
    return 2 if snapshot.interrupted_reason else 0


def _check_output(output: Path) -> int:
    prepare_output(output)
    assessment = Assessment(
        generated_at=datetime.now(timezone.utc).isoformat(),
        source={"demo": True, "product": "SYNTHETIC LOCAL REPORT-OUTPUT SELF-TEST"},
        settings={}, findings=[], questions=[], coverage=[], stats={"http_attempts": 0}, sources={},
        notes=["LOCAL OUTPUT SELF-TEST ONLY. No host or credentials were requested; no HTTP requests or source assessment occurred."],
        schema_version="2.0",
    )
    documents = render_report_documents(assessment)
    documents["diagnostics.json"] = json.dumps({"tool_version": __version__, "mode": "LOCAL_OUTPUT_SELF_TEST",
                                               "http_attempts": 0, "credentials_requested": False}, indent=2) + "\n"
    receipt = publish_documents(documents, output)
    print("Local report-output self-test. No ServiceDesk Plus connection or credentials were used.")
    success = _print_publication(receipt)
    print("Local output test PASSED." if success else "Local output test FAILED.")
    return 0 if success else 1


def main(argv: list[str] | None = None) -> int:
    parser = _cli_parser()
    args = parser.parse_args(argv)
    offline = args.list_endpoints or args.demo or args.check_output
    try:
        with local_environment(args.env_file, disabled=args.no_env or offline,
                               create=not args.check_key_input) as file_host:
            return _run(args, file_host=file_host)
    except (ValueError, OSError):
        # Paths and decoding errors may themselves contain secret input.
        print("Local environment setup failed. Check file access, UTF-8 syntax, duplicate names and the SDP_HOST credential binding. No values were printed.", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace, *, file_host: str | None = None) -> int:
    if args.list_endpoints:
        print("Only these documented GET collection paths and their explicit allowlisted detail/metadata paths are callable:")
        print("  portals                GET /api/v3/portals [global discovery; no PORTALID]")
        for resource in RESOURCES + GLOBAL_RESOURCES:
            print("  {:22s} GET /api/v3{} [{} data; explicit PORTALID]".format(resource.key, resource.path, resource.scope))
        print("  field_definitions      Module-aware documented metadata/UDF strategies; never a bare universal /udf_fields read")
        print("\nNot automatically certified:")
        for item in UNEXPOSED_FEATURES:
            print("  - " + item)
        return 0
    snapshot: EnvironmentSnapshot | None = None
    output: Path | None = None
    try:
        if not args.quiet:
            print("ServiceDesk Plus Cloud Readiness v" + __version__, flush=True)
        if sum(bool(flag) for flag in (args.check_key_input, args.check_output, args.diagnose, args.demo)) > 1:
            raise ValueError("Choose only one of --check-key-input, --check-output, --diagnose or --demo.")
        if (args.checkpoint or args.resume) and (args.diagnose or args.demo or args.check_key_input or args.check_output):
            raise ValueError("Checkpoint/resume is supported only for live assessments, not diagnostics, demos or local checks.")
        if (args.retry_failed or args.retry_portals or args.restart_all) and not args.resume:
            raise ValueError("Retry and restart options require --resume.")
        if args.restart_all and (args.retry_failed or args.retry_portals):
            raise ValueError("Use --restart-all or selective retry options, not both.")
        if args.check_output:
            started = datetime.now(timezone.utc)
            output = Path(args.output_dir).expanduser().resolve() / ("output-check-" + started.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
            return _check_output(output)
        if args.check_key_input:
            key = acquire_api_key(args.key_input, args.api_key_env)
            del key
            print("Local API-key input check passed. Formatting only; authentication was NOT tested. No HTTP requests or report files were created.")
            return 0
        settings = _cli_options(args)
        settings["diagnose_only"] = bool(args.diagnose)
        answers = _cli_answers(args)
        if args.diagnose and (settings.get("portal_ids") or settings.get("portal_file") or args.save_portals):
            raise ValueError("--diagnose tests directory discovery only; it does not import or save portal lists. Remove portal-ID/file/save overrides. --directory-key and --directory-key-env are supported.")
        resources = list(RESOURCES)
        collect_orgusers = True
        if args.modules:
            requested = {key.strip() for key in args.modules.split(",")}
            valid = {resource.key for resource in resources} | {"orgusers", "field_definitions"}
            if not requested.issubset(valid):
                raise ValueError("Unknown module key. Run --list-endpoints for valid keys.")
            collect_orgusers = "orgusers" in requested
            if "field_definitions" in requested:
                requested |= {"incident_templates", "service_templates", "requests", "changes", "assets", "computers", "asset_modules", "ci_types", "cis"}
            resources = [resource for resource in resources if resource.key in requested]
        settings["collections_selected"] = [resource.key for resource in resources]
        started = datetime.now(timezone.utc)
        output = Path(args.output_dir).expanduser().resolve() / ("assessment-" + started.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
        if args.demo:
            prepare_output(output)
            from .synthetic import run_synthetic
            if not args.quiet:
                print("SYNTHETIC DEMONSTRATION: virtual pacing and API fixtures; no ServiceDesk Plus instance is contacted.\n", flush=True)
            snapshot, _ = run_synthetic(args.demo_scenario,
                                        progress=ProgressPrinter(max_requests=500, quiet=args.quiet))
        else:
            host = settings.pop("host", None) or os.environ.get("SDP_HOST")
            if not host:
                if args.non_interactive:
                    raise ValueError("Unattended assessment requires a configured host.")
                host = input("ServiceDesk Plus on-premises URL (https://host:port): ").strip()
            if not host:
                raise ValueError("A source host is required.")
            slots = slot_assignments(host, allow_http=args.allow_http, file_host=file_host)
            multi_key = settings.pop("multi_key", False)
            if not isinstance(multi_key, bool):
                raise ValueError("multi_key must be a boolean.")
            credential_file = settings.pop("credential_file", None)
            global_key_env = settings.pop("global_key_env", None)
            global_portal_id = settings.pop("global_portal_id", None)
            env_global_key = os.environ.get("SDP_GLOBAL_API_KEY")
            env_global_portal = os.environ.get("SDP_GLOBAL_PORTAL_ID")
            if env_global_key or env_global_portal:
                if global_key_env or global_portal_id:
                    raise ValueError("Global credentials are assigned by both numbered environment setup and explicit settings.")
                global_key_env = "SDP_GLOBAL_API_KEY" if env_global_key else None
                global_portal_id = env_global_portal
            if os.environ.get("SDP_DIRECTORY_API_KEY"):
                if args.directory_key_env and args.directory_key_env != "SDP_DIRECTORY_API_KEY":
                    raise ValueError("Directory credentials are assigned by both local environment setup and explicit settings.")
                args.directory_key_env = "SDP_DIRECTORY_API_KEY"
            multi_key = multi_key or credential_file is not None or bool(slots) or bool(env_global_key)
            if slots:
                if args.key_input != "auto":
                    raise ValueError("Numbered instance slots require automatic key input. Clear the slots to use explicit secure prompts.")
                if not args.diagnose and not settings["portal_ids"] and not settings.get("portal_file"):
                    settings["portal_ids"] = [entry["id"] for entry in slots]
                    settings["portal_discovery_mode"] = "automatic" if args.all_portals else "explicit"
            if (global_key_env or global_portal_id) and not multi_key:
                raise ValueError("Explicit global credentials require multi-key mode.")
            if args.non_interactive and (args.key_input != "auto" or
                                         not multi_key and not os.environ.get(args.api_key_env)):
                raise ValueError("Unattended assessment requires environment credentials and automatic key input.")
            if args.non_interactive and args.directory_key and not args.directory_key_env:
                raise ValueError("Unattended directory recovery requires --directory-key-env.")
            key = (None if multi_key and not os.environ.get(args.api_key_env)
                   else acquire_api_key(args.key_input, args.api_key_env))
            progress = ProgressPrinter(max_requests=settings["max_requests"], quiet=args.quiet)

            client = ReadOnlyClient(
                host, key, ALLOWED_PATTERNS, rpm=settings["rpm"], timeout=settings["timeout"],
                max_requests=settings["max_requests"], max_runtime=settings["max_runtime_seconds"],
                portal_id=None, ca_file=settings.get("ca_file"),
                allow_http=args.allow_http, insecure_tls=args.insecure_tls, progress=progress, multi_key=multi_key,
            )
            # Also redact an optional directory credential before it is needed
            # for recovery, so local paths and earlier responses cannot leak it.
            if args.directory_key_env and os.environ.get(args.directory_key_env):
                client.register_credential(prepare_api_key(os.environ[args.directory_key_env]).value)
            credential_setup = (CredentialSetup(client, path=credential_file, global_env=global_key_env,
                                global_portal=global_portal_id, non_interactive=args.non_interactive,
                                mode=args.key_input, slot_entries=slots) if multi_key else None)
            if client.sanitize_local_text(str(output)) != str(output):
                del key
                raise ValueError("The API key must not appear in the output path.")
            resume_path = Path(args.resume).expanduser().resolve() if args.resume else None
            if resume_path is not None and client.sanitize_local_text(str(resume_path)) != str(resume_path):
                raise ValueError("A credential must not appear in the checkpoint path.")
            del key
            # Fail local publication capability before consuming a single API
            # attempt. This checks directory creation plus write/read/replace.
            prepare_output(output)
            if not args.quiet:
                print("\nRead-only assessment v{}: one request at a time, at most {:g}/minute.".format(__version__, settings["rpm"]))
                print("Budgets: {} HTTP attempts, {:g} minutes; {} details per collection.".format(settings["max_requests"], settings["max_minutes"], settings["detail_limit"] or "all observed"))
                print("This is a conservative client policy, not a vendor guarantee. Rate-limit responses cause backoff.")
                print("Local report directory passed a write/read check: " + str(output))
                print("Press Ctrl+C once to stop collection and write a partial report.\n", flush=True)
            scope_resolver = PortalScopeResolver(client, ScopeOptions(
                all_portals=args.all_portals,
                seed_ids=settings.get("portal_ids") if args.all_portals else None,
                portal_file=settings.pop("portal_file", None),
                non_interactive=args.non_interactive, no_portal_cache=args.no_portal_cache,
                save_portals=args.save_portals, directory_key=args.directory_key,
                directory_key_env=args.directory_key_env, key_input=args.key_input,
            ), max_portals=settings["max_portals"], page_size=settings["page_size"], progress=progress)
            resolve_scope = scope_resolver
            if credential_setup is not None:
                def resolve_scope(topology, environment):
                    resolved = scope_resolver(topology, environment)
                    if not args.diagnose and resolved.outcome not in {
                        "INTERRUPTED", "REQUEST_BUDGET_REACHED", "TIME_BUDGET_REACHED"}:
                        credential_setup.resolve(resolved)
                    if client.sanitize_local_text(str(output)) != str(output):
                        raise ValueError("A credential must not appear in the output path.")
                    return resolved
            source = {"host": client.base_url, "product": "ServiceDesk Plus On-Premises", "build_origin": "user_supplied" if answers.get("source_build") else "not_exposed", "key_expiration": "not_exposed_by_verified_read_only_api", "demo": False}
            snapshot = EnvironmentSnapshot(started.isoformat(), source, settings, manual_answers=answers)
            if (slots and not args.diagnose and not args.resume and not os.environ.get(args.api_key_env)
                    and settings["portal_discovery_mode"] == "explicit"):
                print("Discovery skipped: no discovery key set; scope comes from numbered slots (or explicit scope overrides).", flush=True)
            if not args.quiet:
                if args.resume:
                    print("Scope: retained checkpoint selection; no directory refresh. Current credentials apply to remaining work.", flush=True)
                elif settings["portal_discovery_mode"] == "explicit":
                    print("Scope: EXPLICIT portal selection; directory discovery is skipped. Other portals will NOT be assessed. Use --all-portals for whole-scope discovery/recovery.", flush=True)
                else:
                    print("Scope: ALL discovered/verified portals in one run; directory access and shared budgets still apply.", flush=True)
                print("Optional total-count policy: " + settings["count_policy"] + "; counts are source snapshots, not frozen inventories.", flush=True)
            collector = EnvironmentCollector(client, resources, CollectionOptions(
                page_size=settings["page_size"], max_records=settings["max_records"],
                detail_limit=settings["detail_limit"], subresource_parents=settings["subresource_parents"],
                max_child_records=settings["max_child_records"], count_policy=settings["count_policy"],
            ), EnvironmentOptions(max_portals=settings["max_portals"], metadata_limit=settings["metadata_limit"],
                                  collect_orgusers=collect_orgusers, diagnose_only=args.diagnose), progress=progress,
                scope_resolver=resolve_scope)
            if args.checkpoint or args.resume:
                runner = ResumableAssessment(client, resources, collector.options, collector.env_options,
                    progress, resolve_scope, output, resume=resume_path,
                    requested_scope=settings.get("portal_ids") or [], retry_failed=args.retry_failed,
                    retry_portals=args.retry_portals, restart_all=args.restart_all)
                runner.credential_setup = credential_setup
                runner.collect(snapshot, None if args.all_portals else settings.get("portal_ids") or None)
                print("Verified instance-boundary checkpoint: " + str(output / "checkpoint.json"), flush=True)
            else:
                collector.collect(snapshot, None if args.all_portals else settings.get("portal_ids") or None)
        return _finish_assessment(snapshot, output, args.quiet)
    except (ValueError, OSError, ApiError, json.JSONDecodeError) as error:
        if isinstance(error, ApiError):
            print("Assessment could not start: " + error.kind + ". No credentials or response bodies were saved.", file=sys.stderr)
        elif isinstance(error, OSError):
            diagnostic = failure_metadata(error, "local-file-operation", "read_write_or_verify")
            print("Local file operation failed: " + str(diagnostic["classification"])
                  + " (errno=" + str(diagnostic["errno"]) + ", winerror=" + str(diagnostic["winerror"]) + ").", file=sys.stderr)
            print("No report path is being asserted. Check settings/certificate paths, then run --check-output with a short writable --output-dir.", file=sys.stderr)
        else:
            # json errors can include source snippets; report a generic parse error.
            if isinstance(error, json.JSONDecodeError):
                print("Settings JSON is invalid. Use the supplied example structure.", file=sys.stderr)
            else:
                print("Assessment could not start: " + str(error), file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        if snapshot is not None and output is not None:
            snapshot.stop_classification = "INTERRUPTED"
            snapshot.interrupted_reason = "Interrupted by user; collected evidence was preserved."
            snapshot.stats["stop_classification"] = "INTERRUPTED"
            try:
                return _finish_assessment(snapshot, output, args.quiet)
            except KeyboardInterrupt:
                print("Report writing cancelled by a second interrupt.", file=sys.stderr)
                return 130
            except Exception:
                print("Collected evidence could not be written after interruption. No response or exception contents were printed.", file=sys.stderr)
                return 1
        print("Assessment cancelled before collection.", file=sys.stderr)
        return 130
    except Exception:
        # Unexpected library/parser exceptions may contain response fragments;
        # never print their repr, traceback, or dynamic message.
        print("Assessment could not finish because of an unexpected local processing error. No exception contents or traceback were printed. Check the supplied synthetic tests and report the tool version.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
