"""Whole-environment, same-run recovery from a denied directory. No live host."""
import contextlib
import io
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from sdp_audit.catalog import RESOURCES
from sdp_audit.cli import main, _cli_options, _cli_parser
from sdp_audit.collect import CollectionOptions
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.models import EnvironmentSnapshot, PortalInfo, Topology
from sdp_audit.portal_scope import (ScopeOptions, PortalScopeResolver, canonical_host,
    default_scope_path, parse_portal_list, read_scope, save_scope)
from sdp_audit.report import render_report_documents
from sdp_audit.synthetic import (create_synthetic_client, SyntheticResponse, SYNTHETIC_HOST,
    SYNTHETIC_KEY, SYNTHETIC_SENSITIVE_MARKERS)
from sdp_audit.topology import discover_topology
from sdp_audit.transport import ApiError, BudgetExceeded

DIRECTORY_KEY = "synthetic-directory-only-secret-735946"
DENIED = {"http_status": 403, "api_code": 4002, "message": "User does not have this permission"}


def denied_client(**kwargs):
    return create_synthetic_client({"scenario": "multi", "errors": {"global:/portals": DENIED}}, **kwargs)


def environment(client):
    return EnvironmentSnapshot("2026-10-14T12:00:00+00:00",
        {"host": client.base_url, "demo": True},
        {"max_requests": client.max_requests, "page_size": 2, "rpm": 30})


def scan(client, options, *, fields=True, cap=0):
    env = environment(client)
    resolver = PortalScopeResolver(client, options, page_size=2)
    resources = [replace(item, detail=False) for item in RESOURCES if item.key in {"requests", "projects"}]
    collector = EnvironmentCollector(client, resources,
        CollectionOptions(page_size=2, max_records=cap, subresource_parents=0, inventory_budget_fraction=1),
        EnvironmentOptions(discover_fields=fields, collect_orgusers=True), scope_resolver=resolver)
    return collector.collect(env)


class CredentialRouter:
    """Only retains credential classifications, never raw secrets, in its log."""
    def __init__(self, server, *, bad_directory=False, rate_once=False):
        self.server = server
        self.calls = []
        self.bad_directory = bad_directory
        self.rate_once = rate_once

    def open(self, request, timeout):
        path = urlsplit(request.full_url).path.removeprefix("/api/v3")
        key = request.get_header("Authtoken")
        scope = "directory" if key == DIRECTORY_KEY else "integration" if key == SYNTHETIC_KEY else "unexpected"
        self.calls.append((path, request.get_header("Portalid"), scope, self.server.clock()))
        assert key not in request.full_url
        assert request.get_method() == "GET" and request.data is None
        if scope == "directory":
            assert path == "/portals" and request.get_header("Portalid") is None
            if self.bad_directory:
                return SyntheticResponse({"response_status": [{"status_code": 4022, "status": "failed"}]}, 401)
            if self.rate_once:
                self.rate_once = False
                return SyntheticResponse({"response_status": [{"status_code": 4015, "status": "failed"}]}, 429, {"Retry-After": "7"})
            response = self.server.open(request, timeout)
            return response
        if path == "/portals":
            return SyntheticResponse({"response_status": [{"status_code": 4000, "status": "failed",
                "messages": [{"status_code": 4002, "message": "User does not have this permission"}]}]}, 403)
        return self.server.open(request, timeout)


class PortalScopeFileTests(unittest.TestCase):
    def test_all_ids_in_one_entry_are_deduplicated_without_ranges(self):
        self.assertEqual([p.id for p in parse_portal_list("7,42 007;99", SYNTHETIC_HOST)], ["7", "42", "99"])

    def test_ranges_negative_zero_unicode_and_text_are_rejected(self):
        for value in ("1-100", "range(1,50)", "0", "-2", "١", "True", "not-a-token", "1,2\x00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_portal_list(value, SYNTHETIC_HOST)

    def test_same_host_links_extract_ids_locally(self):
        ids = parse_portal_list(SYNTHETIC_HOST + "/HomePage.do?PORTALID=7 " + SYNTHETIC_HOST + ":443/?portalid=42", SYNTHETIC_HOST)
        self.assertEqual([p.id for p in ids], ["7", "42"])
        self.assertTrue(all(not p.discovered for p in ids))

    def test_foreign_urls_credentials_other_queries_and_missing_context_fail(self):
        values = ["https://other.invalid/?PORTALID=7", SYNTHETIC_HOST + "/?PORTALID=7&authtoken=secret",
                  "https://secret@synthetic.example.invalid/?PORTALID=7", SYNTHETIC_HOST + "/?PORTALID=7#secret",
                  SYNTHETIC_HOST + "/?id=7", SYNTHETIC_HOST + "/?PORTALID=7&PORTALID=8"]
        for value in values:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_portal_list(value, SYNTHETIC_HOST)
        with self.assertRaises(ValueError):
            parse_portal_list(SYNTHETIC_HOST + "/other/?PORTALID=7", SYNTHETIC_HOST + "/sdp")

    def test_default_ports_and_host_case_have_same_profile_but_contexts_differ(self):
        self.assertEqual(default_scope_path(SYNTHETIC_HOST), default_scope_path(SYNTHETIC_HOST.upper() + ":443/"))
        self.assertNotEqual(default_scope_path(SYNTHETIC_HOST), default_scope_path(SYNTHETIC_HOST + "/sdp"))
        self.assertNotEqual(default_scope_path(SYNTHETIC_HOST), default_scope_path(SYNTHETIC_HOST.replace("https", "http")))

    def test_profile_roundtrip_keeps_only_safe_nonsecret_metadata(self):
        client, _, _ = create_synthetic_client()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "portals.json"
            save_scope(path, SYNTHETIC_HOST, [PortalInfo("7", "HR " + SYNTHETIC_KEY)], client.sanitize_local_text)
            raw = path.read_text()
            self.assertNotIn(SYNTHETIC_KEY, raw)
            self.assertNotIn("accessible", raw)
            self.assertEqual(set(json.loads(raw)), {"schema_version", "host", "saved_at", "portals"})
            result = read_scope(path, SYNTHETIC_HOST)
            self.assertEqual(result[0].id, "7")
            self.assertIsNone(result[0].accessible)

    def test_mismatched_host_or_unknown_fields_fail_without_echo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scope.json"
            for data in (
                {"schema_version": 1, "host": "https://other.invalid", "portals": [{"id": "7"}]},
                {"schema_version": 1, "host": SYNTHETIC_HOST, "api_key": DIRECTORY_KEY, "portals": [{"id": "7"}]},
                {"schema_version": 1, "host": SYNTHETIC_HOST, "portals": [{"id": "7", "token": DIRECTORY_KEY}]},
                {"schema_version": True, "host": SYNTHETIC_HOST, "portals": [{"id": "7"}]},
                {"schema_version": 1, "host": SYNTHETIC_HOST, "portals": [{"id": True}]},
            ):
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError) as caught:
                    read_scope(path, SYNTHETIC_HOST)
                self.assertNotIn(DIRECTORY_KEY, str(caught.exception))

    def test_oversized_profile_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scope.json"
            path.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                read_scope(path, SYNTHETIC_HOST)

    def test_save_failure_does_not_assert_success(self):
        client, _, _ = create_synthetic_client()
        resolver = PortalScopeResolver(client, ScopeOptions(save_portals=True))
        output = io.StringIO()
        with patch("sdp_audit.portal_scope.save_scope", side_effect=OSError("PRIVATE")), contextlib.redirect_stdout(output):
            resolver._save(Topology(portals=[PortalInfo("7", "HR")]), False)
        self.assertIn("could not be saved", output.getvalue())
        self.assertNotIn("PRIVATE", output.getvalue())


class SameRunRecoveryTests(unittest.TestCase):
    def test_denied_directory_prompts_once_and_scans_entire_list_in_same_collector(self):
        client, server, _ = denied_client()
        with patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=["l", "1,2,3,4"]), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(no_portal_cache=True))
        self.assertEqual(set(env.portals), {"1", "2", "3", "4"})
        self.assertEqual(sum(call["path"] == "/portals" for call in server.calls), 1)
        self.assertEqual(sum(item.portal.accessible is True for item in env.portals.values()), 3)
        self.assertFalse(env.topology.complete)
        self.assertEqual(env.topology.mode, "assisted")
        self.assertEqual(env.topology.directory_outcome, "PERMISSION_DENIED")
        self.assertEqual(env.portals["2"].snapshot.datasets["projects"].outcome, "PERMISSION_DENIED")
        self.assertEqual(env.portals["3"].snapshot.datasets["projects"].outcome, "COMPLETE")
        self.assertTrue(all(call["portal_id"] is not None for call in server.calls if call["path"] != "/portals"))

    def test_interactive_profile_is_remembered_only_after_consent_then_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "scope.json"
            client, _, _ = denied_client()
            with patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
                 patch("builtins.input", side_effect=["l", "1,2,3", "y"]), contextlib.redirect_stdout(io.StringIO()):
                first = scan(client, ScopeOptions(cache_path=cache))
            self.assertTrue(cache.is_file())
            client2, server, _ = denied_client()
            with patch("builtins.input", side_effect=AssertionError("must not prompt")), contextlib.redirect_stdout(io.StringIO()):
                second = scan(client2, ScopeOptions(cache_path=cache))
            self.assertEqual(set(first.portals), set(second.portals))
            self.assertEqual(second.topology.selection_source, "saved host-bound portal profile")
            self.assertTrue(any(call["portal_id"] == "3" for call in server.calls))

    def test_rejecting_save_does_not_write_a_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "scope.json"
            client, _, _ = denied_client()
            with patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
                 patch("builtins.input", side_effect=["l", "1,3", "n"]), contextlib.redirect_stdout(io.StringIO()):
                scan(client, ScopeOptions(cache_path=cache))
            self.assertFalse(cache.exists())

    def test_bad_profile_does_not_get_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "scope.json"
            save_scope(cache, "https://other.invalid", [PortalInfo("777", "Other")])
            client, server, _ = denied_client()
            with contextlib.redirect_stdout(io.StringIO()):
                env = scan(client, ScopeOptions(cache_path=cache, non_interactive=True))
            self.assertFalse(env.portals)
            self.assertEqual(len(server.calls), 1)

    def test_successful_discovery_does_not_prompt_or_reuse_stale_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "scope.json"
            save_scope(cache, SYNTHETIC_HOST, [PortalInfo("777", "Removed")])
            client, server, _ = create_synthetic_client("multi")
            with patch("builtins.input", side_effect=AssertionError("must not prompt")):
                env = scan(client, ScopeOptions(cache_path=cache))
            self.assertTrue(env.topology.complete)
            self.assertNotIn("777", env.portals)

    def test_portal_file_scans_all_without_ui_or_multiple_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scope.json"
            save_scope(path, SYNTHETIC_HOST, [PortalInfo("1", "IT"), PortalInfo("3", "Facilities")])
            client, server, _ = denied_client()
            with patch("builtins.input", side_effect=AssertionError("must not prompt")), contextlib.redirect_stdout(io.StringIO()):
                env = scan(client, ScopeOptions(portal_file=str(path), non_interactive=True))
            self.assertEqual(set(env.portals), {"1", "3"})
            self.assertEqual(env.portals["3"].portal.name, "Facilities")
            self.assertEqual(len([call for call in server.calls if call["path"] == "/orgusers"]), 1)

    def test_budget_and_time_stops_preserve_portal_lists_without_false_zeros(self):
        for kwargs, expected in (({"max_requests": 7}, "REQUEST_BUDGET_REACHED"),
                                 ({"max_runtime": 12}, "TIME_BUDGET_REACHED")):
            with self.subTest(expected=expected):
                client, _, _ = denied_client(**kwargs)
                with contextlib.redirect_stdout(io.StringIO()):
                    env = scan(client, ScopeOptions(seed_ids=["1", "2", "3", "4"], non_interactive=True, no_portal_cache=True))
                self.assertEqual(env.stop_classification, expected)
                complete = [ds for portal in env.portals.values() for ds in portal.snapshot.datasets.values() if ds.list_complete]
                self.assertTrue(complete)
                for portal in env.portals.values():
                    for ds in portal.snapshot.datasets.values():
                        if not ds.read_attempted:
                            self.assertIsNone(ds.coverage()["records_observed"])
                self.assertTrue(all(ds.outcome in {"COMPLETE", "EMPTY"} for ds in complete))

    def test_interruption_after_recovery_keeps_scope_and_records(self):
        client, _, _ = create_synthetic_client({"scenario": "multi", "errors": {"global:/portals": DENIED}, "interrupt_at_attempt": 8})
        with contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(seed_ids=["1", "2", "3"], non_interactive=True, no_portal_cache=True))
        self.assertEqual(env.stop_classification, "INTERRUPTED")
        self.assertEqual(set(env.portals), {"1", "2", "3"})
        self.assertTrue(any(p.snapshot.datasets["requests"].records for p in env.portals.values()))
        self.assertIn("report.html", render_report_documents(analyze_environment(env)))

    def test_unknown_ids_are_never_probed_on_empty_input(self):
        client, server, _ = denied_client()
        with patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
             patch("builtins.input", return_value=""), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(no_portal_cache=True))
        self.assertEqual(len(server.calls), 1)
        self.assertFalse(env.portals)

    def test_noninteractive_missing_ids_remains_unknown(self):
        client, server, _ = denied_client()
        with patch("builtins.input", side_effect=AssertionError("must not prompt")), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(non_interactive=True, no_portal_cache=True))
        self.assertFalse(env.portals)
        self.assertEqual(len(server.calls), 1)

    def test_authentication_failure_never_prompts_or_guesses(self):
        client, server, _ = create_synthetic_client({"scenario": "multi", "errors": {"global:/portals": {
            "http_status": 401, "api_code": 4022, "message": "Invalid API Key"}}})
        with patch("builtins.input", side_effect=AssertionError("must not prompt")):
            env = scan(client, ScopeOptions())
        self.assertEqual(env.stop_classification, "AUTHENTICATION_FAILED")
        self.assertEqual(len(server.calls), 1)

    def test_reports_keep_all_portal_provenance_and_secrets_out(self):
        client, _, _ = denied_client()
        with contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(seed_ids=["1", "2", "3", "4"], non_interactive=True, no_portal_cache=True))
        assessment = analyze_environment(env)
        self.assertEqual(len(assessment.questions), 7)
        self.assertEqual({p["portal_id"] for p in assessment.portals}, {"1", "2", "3", "4"})
        self.assertTrue(any(f.id == "TOPOLOGY_COVERAGE" and f.status == "UNKNOWN" for f in assessment.findings))
        self.assertTrue(any(f.portal_id == "1" for f in assessment.findings))
        documents = render_report_documents(assessment)
        for text in documents.values():
            for marker in SYNTHETIC_SENSITIVE_MARKERS:
                self.assertNotIn(marker, text)
        self.assertTrue(any(row.get("module") == "topology" for row in assessment.questions[0]["api_coverage_limitations"]))



    def test_existing_seed_still_offers_recovery_of_the_full_list(self):
        client, server, _ = denied_client()
        with patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=["l", "2,3,4"]), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(all_portals=True, seed_ids=["1"], no_portal_cache=True))
        self.assertEqual(set(env.portals), {"1", "2", "3", "4"})
        self.assertEqual(sum(call["path"] == "/portals" for call in server.calls), 1)

    def test_capped_scope_does_not_overwrite_the_saved_whole_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scope.json"
            save_scope(path, SYNTHETIC_HOST, [PortalInfo("1", "IT"), PortalInfo("3", "Facilities")])
            original = path.read_bytes()
            client, _, _ = denied_client()
            resolver = PortalScopeResolver(client, ScopeOptions(save_portals=True, cache_path=path), max_portals=1)
            topology = discover_topology(client)
            topology = resolver._merge(topology, [PortalInfo("1", "IT"), PortalInfo("3", "Facilities")], "verified test list")
            with contextlib.redirect_stdout(io.StringIO()):
                resolver._save(topology, False)
            self.assertEqual(topology.outcome, "RECORD_LIMIT_REACHED")
            self.assertEqual(path.read_bytes(), original)

    def test_topology_preserves_existing_positional_constructor(self):
        portal = PortalInfo("7", "IT")
        self.assertEqual(Topology([portal]).portals, [portal])


class DirectoryCredentialTests(unittest.TestCase):
    def routed(self, **kwargs):
        client, server, clock = create_synthetic_client("multi")
        router = CredentialRouter(server, **kwargs)
        client._opener = router
        return client, server, router, clock

    def test_directory_key_discovers_all_module_reads_keep_original_key(self):
        client, server, router, _ = self.routed()
        with patch.dict("os.environ", {"SDP_DIRECTORY_KEY": DIRECTORY_KEY}), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(directory_key_env="SDP_DIRECTORY_KEY", no_portal_cache=True, non_interactive=True))
        self.assertEqual(set(env.portals), {"1", "2", "3", "4"})
        self.assertTrue(env.topology.complete)
        self.assertEqual(env.topology.credential_scope, "directory_key")
        self.assertTrue(all(scope == "integration" for path, pid, scope, t in router.calls if path != "/portals"))
        self.assertEqual(client.stats["authentication"], "valid")
        self.assertEqual(client.stats["directory_key_authentication"], "valid")
        self.assertTrue(all(b[3] - a[3] >= 2 for a, b in zip(router.calls, router.calls[1:])))
        for text in render_report_documents(analyze_environment(env)).values():
            self.assertNotIn(DIRECTORY_KEY, text)
            self.assertNotIn(SYNTHETIC_KEY, text)

    def test_directory_success_does_not_establish_original_key_authentication(self):
        client, _, _, _ = self.routed()
        with contextlib.redirect_stdout(io.StringIO()), patch.dict("os.environ", {"SDP_DIRECTORY_KEY": DIRECTORY_KEY}):
            topo = discover_topology(client)
            env = environment(client)
            resolver = PortalScopeResolver(client, ScopeOptions(directory_key_env="SDP_DIRECTORY_KEY", non_interactive=True, no_portal_cache=True))
            topo = resolver(topo, env)
        self.assertTrue(topo.complete)
        self.assertEqual(client.stats["authentication"], "unverified")

    def test_invalid_directory_key_does_not_poison_original_key(self):
        client, _, _, _ = self.routed(bad_directory=True)
        with patch.dict("os.environ", {"SDP_DIRECTORY_KEY": DIRECTORY_KEY}), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(directory_key_env="SDP_DIRECTORY_KEY", seed_ids=["1", "3"], non_interactive=True, no_portal_cache=True))
        self.assertEqual(set(env.portals), {"1", "3"})
        self.assertTrue(env.portals["1"].portal.accessible)
        self.assertEqual(client.stats["authentication"], "valid")
        self.assertEqual(client.stats["directory_key_authentication"], "failed")

    def test_directory_credential_is_blocked_from_other_paths_and_portal_headers(self):
        client, _, router, _ = self.routed()
        reader = client.directory_reader(DIRECTORY_KEY)
        for path, portal in (("/requests", None), ("/portals", "1"), ("/projects", "1")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                reader.get_json(path, portal_id=portal)
        self.assertEqual(len(router.calls), 0)
        reader.close()
        with self.assertRaises(ValueError):
            reader.get_json("/portals")
        self.assertNotIn(DIRECTORY_KEY, repr(reader))

    def test_directory_secret_never_allowed_in_urls_or_portal_context(self):
        client, _, router, _ = self.routed()
        reader = client.directory_reader(DIRECTORY_KEY)
        with self.assertRaises(ValueError):
            reader.get_json("/portals", {"input_data": DIRECTORY_KEY})
        with self.assertRaises(ValueError):
            client.get_json("/portals/" + DIRECTORY_KEY, portal_id=None)
        self.assertEqual(len(router.calls), 0)

    def test_both_credentials_redacted_in_api_responses(self):
        client, server, router, _ = self.routed()
        server.portals[0]["name"] = SYNTHETIC_KEY + " " + DIRECTORY_KEY
        reader = client.directory_reader(DIRECTORY_KEY)
        topo = discover_topology(reader)
        self.assertNotIn(DIRECTORY_KEY, topo.portals[0].name)
        self.assertNotIn(SYNTHETIC_KEY, topo.portals[0].name)

    def test_directory_retry_after_and_budget_share_original_scheduler(self):
        client, _, router, _ = self.routed(rate_once=True)
        client.max_requests = 3
        with patch.dict("os.environ", {"SDP_DIRECTORY_KEY": DIRECTORY_KEY}), contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, ScopeOptions(directory_key_env="SDP_DIRECTORY_KEY", non_interactive=True, no_portal_cache=True))
        self.assertEqual(client.stats["requests"], 3)
        self.assertGreaterEqual(router.calls[2][3] - router.calls[1][3], 7)
        self.assertEqual(env.stop_classification, "REQUEST_BUDGET_REACHED")


class MultiportalCliTests(unittest.TestCase):
    def test_all_portals_overrides_restrictive_flag_as_seed_not_guess(self):
        settings = _cli_options(_cli_parser().parse_args(["--all-portals", "--portal-id", "1"]))
        self.assertEqual(settings["portal_discovery_mode"], "automatic")
        self.assertEqual(settings["portal_ids"], ["1"])

    def test_cli_interactive_recovery_uses_one_client_and_one_key_prompt(self):
        client, server, _ = denied_client()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"SDP_HOST": "", "SDP_API_KEY": ""}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client) as factory, \
             patch("sdp_audit.cli.acquire_api_key", return_value=SYNTHETIC_KEY) as key_prompt, \
             patch("sdp_audit.portal_scope.sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=[SYNTHETIC_HOST, "l", "1,2,3,4"]), contextlib.redirect_stdout(output):
            code = main(["--all-portals", "--no-portal-cache", "--modules", "requests,projects", "--output-dir", tmp])
            self.assertEqual(code, 0)
            factory.assert_called_once()
            key_prompt.assert_called_once()
            doc = json.loads(next(Path(tmp).glob("*/assessment.json")).read_text())
            self.assertEqual(len(doc["portals"]), 4)
            self.assertTrue(next(Path(tmp).glob("*.zip")).is_file())
            self.assertNotIn(SYNTHETIC_KEY, output.getvalue())
            self.assertEqual(len([c for c in server.calls if c["path"] == "/portals"]), 1)

    def test_legacy_single_portal_override_remains_restrictive(self):
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--host", SYNTHETIC_HOST, "--portal-id", "3", "--modules", "requests", "--output-dir", tmp]), 0)
        self.assertEqual({c["portal_id"] for c in server.calls}, {"3"})

    def test_all_portals_seed_does_not_reduce_successfully_discovered_scope(self):
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--host", SYNTHETIC_HOST, "--all-portals", "--portal-id", "1", "--modules", "requests", "--output-dir", tmp]), 0)
        self.assertEqual({c["portal_id"] for c in server.calls if c["portal_id"]}, {"1", "2", "3", "4"})

    def test_recovery_demo_needs_no_host_key_or_network(self):
        with tempfile.TemporaryDirectory() as tmp, \
             patch("sdp_audit.cli.acquire_api_key", side_effect=AssertionError("no credential input")), \
             contextlib.redirect_stdout(io.StringIO()):
            code = main(["--demo", "--demo-scenario", "recovery", "--output-dir", tmp])
            self.assertEqual(code, 0)
            doc = json.loads(next(Path(tmp).glob("*/assessment.json")).read_text())
            self.assertEqual(len(doc["portals"]), 4)
            self.assertEqual(doc["environment"]["topology"]["mode"], "assisted")
            self.assertTrue(next(Path(tmp).glob("*.zip")).is_file())


if __name__ == "__main__":
    unittest.main()
