"""Synthetic transport, configuration and consolidated-report scope regressions."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote

from sdp_audit.catalog import RESOURCES
from sdp_audit.cli import main
from sdp_audit.collect import CollectionOptions
from sdp_audit.credential_setup import CredentialSetup, read_assignments
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.models import EnvironmentSnapshot
from sdp_audit.portal_scope import PortalScopeResolver, ScopeOptions
from sdp_audit.report import render_report_documents
from sdp_audit.synthetic import (SYNTHETIC_HOST as HOST, SYNTHETIC_KEY, SyntheticResponse,
                                 create_synthetic_client, run_synthetic)
from sdp_audit.transport import ApiError, BudgetExceeded


KEY1, KEY2, GLOBAL = "synthetic-key-one+/=", "synthetic-key-two+/=", "synthetic-org+/="


def client_and_server(**kwargs):
    return create_synthetic_client("multi", multi_key=True, **kwargs)


def scan(client, *, fields=False, ids=None, resolver=None):
    resources = [replace(r, detail=True) for r in RESOURCES
                 if r.key in {"requests", "incident_templates", "service_templates"}]
    env = EnvironmentSnapshot("2026-10-21T12:00:00Z", {"host": HOST}, {"max_requests": 500})
    EnvironmentCollector(client, resources,
        CollectionOptions(page_size=100, detail_limit=1, subresource_parents=1,
                          inventory_budget_fraction=1),
        EnvironmentOptions(discover_fields=fields), scope_resolver=resolver).collect(env, ids)
    return env


class RecordingOpener:
    """Capture synthetic authorization for assertions only; never report it."""
    def __init__(self, server, reject=None, reject_path=None):
        self.server, self.reject, self.reject_path = server, reject, reject_path
        self.calls = []

    def open(self, request, timeout):
        key = request.get_header("Authtoken")
        self.calls.append((request.full_url, request.get_header("Portalid"), key))
        if key == self.reject and (self.reject_path is None or self.reject_path in request.full_url):
            return SyntheticResponse({"response_status": [{"status_code": 4001, "status": "failed"}]}, 401)
        return self.server.open(request, timeout)


class MultiCredentialTests(unittest.TestCase):
    def test_routing_covers_inventory_details_children_and_metadata(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client.bind_global_credential(HOST, "1", GLOBAL)
        recorder = RecordingOpener(server)
        client._opener = recorder
        env = scan(client, fields=True, ids=["1", "2"])
        self.assertIsNone(env.stop_classification)
        self.assertTrue(any("metainfo" in url for url, _, _ in recorder.calls))
        self.assertTrue(any("/requests/101" in url for url, _, _ in recorder.calls))
        self.assertTrue(any("/notes" in url for url, _, _ in recorder.calls))
        for url, pid, key in recorder.calls:
            self.assertEqual(key, GLOBAL if "/orgusers" in url else {"1": KEY1, "2": KEY2}[pid])
        self.assertEqual(sum("/orgusers" in url for url, _, _ in recorder.calls), 1)
        docs = render_report_documents(analyze_environment(env))
        for secret in (KEY1, KEY2, GLOBAL, SYNTHETIC_KEY):
            self.assertNotIn(secret, "".join(docs.values()))
            self.assertNotIn(quote(secret, safe=""), "".join(docs.values()))
        self.assertIn("credential_status", docs["coverage.csv"])
        self.assertIn("Credential scope", docs["report.html"])

    def test_bad_key_does_not_stop_other_instance(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client._opener = RecordingOpener(server, KEY1)
        env = scan(client, ids=["1", "2"])
        self.assertIsNone(env.stop_classification)
        self.assertEqual(env.portals["1"].portal.scan_status, "AUTHENTICATION_FAILED")
        self.assertTrue(env.portals["2"].snapshot.datasets["requests"].list_complete)
        self.assertEqual(client.credential_status("1"), "failed")
        self.assertEqual(client.credential_status("2"), "valid")
        self.assertEqual(env.authentication, "MIXED")

    def test_explicitly_shared_valid_key_works_for_both_instances(self):
        client, server, _ = client_and_server()
        for pid in ("1", "2"):
            client.bind_portal_credential(HOST, pid, KEY1)
        recorder = RecordingOpener(server)
        client._opener = recorder
        env = scan(client, ids=["1", "2"])
        self.assertTrue(all(item.snapshot.datasets["requests"].list_complete for item in env.portals.values()))
        self.assertEqual({key for _, _, key in recorder.calls}, {KEY1})

    def test_failure_during_detail_sampling_is_isolated(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client._opener = RecordingOpener(server, KEY1, "/requests/101")
        env = scan(client, ids=["1", "2"])
        self.assertIsNone(env.stop_classification)
        self.assertEqual(client.credential_status("1"), "failed")
        self.assertGreater(env.portals["2"].snapshot.datasets["requests"].detail_succeeded, 0)

    def test_later_auth_failure_preserves_prior_permission_diagnostic(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        class DeniedThenExpired(RecordingOpener):
            def open(self, request, timeout):
                if request.get_header("Authtoken") == KEY1 and "/request_templates" in request.full_url:
                    return SyntheticResponse({"response_status": [{"status_code": 4002, "status": "failed"}]}, 403)
                return super().open(request, timeout)
        client._opener = DeniedThenExpired(server, KEY1, "/requests")
        env = scan(client, ids=["1", "2"])
        self.assertEqual(env.portals["1"].snapshot.datasets["incident_templates"].outcome, "PERMISSION_DENIED")
        self.assertEqual(env.portals["1"].portal.scan_status, "AUTHENTICATION_FAILED")

    def test_response_redacts_all_registered_keys_and_encoded_forms(self):
        client, _, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client.bind_global_credential(HOST, "1", GLOBAL)
        class Echo:
            def open(self, request, timeout):
                return SyntheticResponse({"response_status": {"status_code": 2000},
                    "requests": [{"id": "100", "description": KEY1 + KEY2 + quote(GLOBAL, safe="")}],
                    "list_info": {"has_more_rows": False}})
        client._opener = Echo()
        payload = json.dumps(client.get_json("/requests", portal_id="1"))
        for key in (KEY1, KEY2, GLOBAL):
            self.assertNotIn(key, payload)
            self.assertNotIn(quote(key, safe=""), payload)

    def test_bad_directory_key_does_not_prevent_verified_scope_recovery(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client._opener = RecordingOpener(server, SYNTHETIC_KEY)
        resolver = PortalScopeResolver(client, ScopeOptions(seed_ids=["1", "2"],
                        non_interactive=True, no_portal_cache=True))
        with contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, resolver=resolver)
        self.assertIsNone(env.stop_classification)
        self.assertEqual(env.topology.directory_outcome, "AUTHENTICATION_FAILED")
        self.assertTrue(env.portals["2"].snapshot.datasets["requests"].list_complete)

    def test_shared_failed_key_stops_all_its_assignments_only(self):
        client, server, _ = client_and_server()
        for pid, key in (("1", KEY1), ("2", KEY1), ("3", KEY2)):
            client.bind_portal_credential(HOST, pid, key)
        recorder = RecordingOpener(server, KEY1)
        client._opener = recorder
        env = scan(client, ids=["1", "2", "3"])
        self.assertEqual(sum(key == KEY1 for _, _, key in recorder.calls), 1)
        self.assertEqual(env.portals["2"].portal.scan_status, "AUTHENTICATION_FAILED")
        self.assertTrue(env.portals["3"].snapshot.datasets["requests"].list_complete)

    def test_failure_during_metadata_continues_other_instances(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client._opener = RecordingOpener(server, KEY1, "metainfo")
        env = scan(client, fields=True, ids=["1", "2"])
        self.assertIsNone(env.stop_classification)
        self.assertEqual(client.credential_status("1"), "failed")
        self.assertTrue(env.portals["2"].snapshot.fields)

    def test_missing_binding_never_uses_primary_or_another_portal(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        env = scan(client, ids=["1", "2"])
        self.assertFalse(any(call["portal_id"] == "2" for call in server.calls))
        ds = env.portals["2"].snapshot.datasets["requests"]
        self.assertEqual(ds.outcome, "CREDENTIAL_MISSING")
        self.assertIsNone(ds.coverage()["records_observed"])
        self.assertEqual(env.global_snapshot.datasets["orgusers"].outcome, "CREDENTIAL_MISSING")

    def test_direct_transport_rejects_missing_binding(self):
        client, server, _ = client_and_server()
        with self.assertRaises(ApiError) as caught:
            client.get_json("/requests", portal_id="2")
        self.assertEqual(caught.exception.classification, "CREDENTIAL_MISSING")
        self.assertEqual(server.calls, [])

    def test_global_failure_is_independent_and_context_is_explicit(self):
        client, server, _ = client_and_server()
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        client.bind_global_credential(HOST, "1", GLOBAL)
        client._opener = RecordingOpener(server, GLOBAL)
        env = scan(client, ids=["1", "2"])
        self.assertIsNone(env.stop_classification)
        self.assertEqual(env.global_snapshot.datasets["orgusers"].outcome, "AUTHENTICATION_FAILED")
        assessment = analyze_environment(env)
        self.assertIn("global_key", {item.get("credential_scope") for item in assessment.diagnostics})
        self.assertTrue(env.portals["2"].snapshot.datasets["requests"].list_complete)
        with self.assertRaises(ValueError):
            client.get_json("/orgusers", portal_id="2")

    def test_global_key_is_not_used_for_portal_and_directory_key_is_restricted(self):
        client, server, _ = client_and_server()
        client.bind_global_credential(HOST, "1", GLOBAL)
        with self.assertRaises(ApiError):
            client.get_json("/requests", portal_id="1")
        reader = client.directory_reader(KEY1)
        with self.assertRaises(ValueError):
            reader.get_json("/orgusers")
        with self.assertRaises(ValueError):
            reader.get_json("/requests", portal_id="1")
        self.assertFalse(server.calls)

    def test_bindings_reject_wrong_host_context_and_conflicts(self):
        client, _, _ = client_and_server()
        for host in ("https://other.invalid", HOST + "/other"):
            with self.assertRaises(ValueError):
                client.bind_portal_credential(host, "1", KEY1)
        client.bind_portal_credential(HOST + ":443", "1", KEY1)
        with self.assertRaises(ValueError):
            client.bind_portal_credential(HOST, "1", KEY2)
        with self.assertRaises(ValueError):
            client.bind_portal_credential(HOST, "0", KEY1)

    def test_shared_attempt_and_time_budgets(self):
        for options, reason in (({"max_requests": 1}, "REQUEST_BUDGET_REACHED"),
                                ({"max_runtime": 1}, "TIME_BUDGET_REACHED")):
            client, _, _ = client_and_server(**options)
            client.bind_portal_credential(HOST, "1", KEY1)
            client.bind_portal_credential(HOST, "2", KEY2)
            env = scan(client, ids=["1", "2"])
            self.assertEqual(env.stop_classification, reason)
            self.assertEqual(client.stats["requests"], 1)

    def test_denied_directory_verified_list_recovers_without_primary_key(self):
        client, _, _ = client_and_server(api_key=None)
        client.bind_portal_credential(HOST, "1", KEY1)
        client.bind_portal_credential(HOST, "2", KEY2)
        resolver = PortalScopeResolver(client, ScopeOptions(seed_ids=["1", "2"],
                        non_interactive=True, no_portal_cache=True))
        with contextlib.redirect_stdout(io.StringIO()):
            env = scan(client, resolver=resolver)
        self.assertEqual(set(env.portals), {"1", "2"})
        self.assertFalse(env.topology.complete)
        self.assertTrue(env.portals["2"].snapshot.datasets["requests"].list_complete)

    def test_explicit_multi_key_demo(self):
        env, server = run_synthetic("multi_key")
        self.assertTrue(env.portals["1"].snapshot.datasets["requests"].list_complete)
        self.assertEqual(env.portals["2"].snapshot.datasets["projects"].outcome, "PERMISSION_DENIED")
        self.assertEqual(env.stats["global_limiter_instances"], 1)
        text = "".join(render_report_documents(analyze_environment(env)).values())
        self.assertNotIn("synthetic-portal-key-", text)
        self.assertNotIn("synthetic-org-key", text)


class CredentialSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "credentials.json"

    def write(self, **changes):
        data = {"schema_version": 1, "host": HOST,
                "portals": [{"id": "1", "env": "TEST_SDP_ONE"}, {"id": "2", "env": "TEST_SDP_TWO"}]}
        data.update(changes)
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return str(self.path)

    def test_environment_references_and_missing_values(self):
        client, _, _ = client_and_server()
        with patch.dict(os.environ, {"TEST_SDP_ONE": KEY1, "TEST_SDP_TWO": ""}):
            CredentialSetup(client, path=self.write(), non_interactive=True)
        self.assertEqual(client.credential_status("1"), "unverified")
        self.assertEqual(client.credential_status("2"), "missing")
        self.assertEqual(client.sanitize_local_text(quote(KEY1, safe="")), "[REDACTED]")

    def test_schema_duplicate_literal_key_and_wrong_host_rejected(self):
        for changes in ({"host": HOST + "/other"}, {"api_key": KEY1},
                        {"portals": [{"id": "1", "env": "A"}, {"id": "1", "env": "B"}]},
                        {"portals": [{"id": "1", "api_key": KEY1}]},
                        {"portals": [{"id": "1", "env": "not a name"}]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                read_assignments(self.write(**changes), HOST)
        self.path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        with self.assertRaises(ValueError):
            read_assignments(str(self.path), HOST)

    def test_normalized_id_duplicates_rejected(self):
        path = self.write(portals=[{"id": "1", "env": "A"}, {"id": "01", "env": "B"}])
        with self.assertRaises(ValueError):
            read_assignments(path, HOST)

    def test_invalid_nonempty_environment_key_fails_before_network(self):
        client, server, _ = client_and_server()
        with patch.dict(os.environ, {"TEST_SDP_ONE": "bad\x16key"}), self.assertRaises(ValueError):
            CredentialSetup(client, path=self.write(), non_interactive=True)
        self.assertEqual(server.calls, [])

    def test_unattended_missing_host_never_prompts(self):
        with patch.dict(os.environ, {"SDP_HOST": ""}), \
             patch("builtins.input", side_effect=AssertionError("Unexpected prompt")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--multi-key", "--non-interactive"]), 1)

    def test_interactive_new_key_and_explicit_reuse(self):
        client, _, _ = client_and_server()
        from sdp_audit.topology import discover_topology
        topology = discover_topology(client, portal_ids=["1", "2"])
        with patch("sys.stdin.isatty", return_value=True), \
             patch("builtins.input", side_effect=["", "1"]), \
             patch("sdp_audit.credential_setup.acquire_api_key", return_value=KEY1) as prompt, \
             contextlib.redirect_stdout(io.StringIO()):
            setup = CredentialSetup(client)
            setup.resolve(topology)
        self.assertEqual(prompt.call_count, 1)
        self.assertEqual(client._portal_keys["1"], client._portal_keys["2"])

    def test_global_configuration_is_explicit_and_conflicts_fail(self):
        client, _, _ = client_and_server()
        with patch.dict(os.environ, {"TEST_ORG": GLOBAL}):
            CredentialSetup(client, global_env="TEST_ORG", global_portal="1", non_interactive=True)
        self.assertEqual(client.global_portal_id, "1")
        with self.assertRaises(ValueError):
            CredentialSetup(client, global_env="TEST_ORG")

    def test_cli_unattended_assignments_and_reports(self):
        client, server, _ = client_and_server(api_key=None)
        with patch.dict(os.environ, {"SDP_API_KEY": "", "TEST_SDP_ONE": KEY1, "TEST_SDP_TWO": KEY2}), \
             patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             patch("builtins.input", side_effect=AssertionError("Unexpected prompt")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = main(["--host", HOST, "--credential-file", self.write(),
                         "--portal-ids", "1,2", "--non-interactive", "--quiet",
                         "--modules", "requests,orgusers", "--output-dir", self.temp.name])
        self.assertEqual(code, 0)
        document = json.loads(next(Path(self.temp.name).glob("*/assessment.json")).read_text())
        self.assertEqual(document["environment"]["permissions"]["orgusers_collection"], "credential_missing")
        self.assertEqual({row["scope"] for row in document["environment"]["permissions"]["credential_scopes"]},
                         {"directory", "global", "portal:1", "portal:2"})
        self.assertNotIn(KEY1, json.dumps(document))


if __name__ == "__main__":
    unittest.main()
