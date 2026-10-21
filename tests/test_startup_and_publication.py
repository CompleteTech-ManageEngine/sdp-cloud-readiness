"""2.0.2: discovery diagnostics and missing-output regressions.

All remote-like responses are synthetic, with one real localhost HTTP test.
No customer instance, real key or source records are used.
"""
from __future__ import annotations

import contextlib
import errno
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import socket
import ssl
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import zipfile

from sdp_audit import __version__
from sdp_audit.artifacts import (ArtifactError, REPORT_NAMES, atomic_write_bytes, failure_metadata,
                                 prepare_output, publish_documents, verify_bytes)
from sdp_audit.catalog import ALLOWED_PATTERNS
from sdp_audit.cli import _print_publication, main
from sdp_audit.diagnostics import diagnostic_lines, diagnostics_document, safe_diagnostic
from sdp_audit.environment import EnvironmentCollector, EnvironmentOptions
from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.models import EnvironmentSnapshot
from sdp_audit.progress import ProgressPrinter
from sdp_audit.report import render_report_documents, write_reports
from sdp_audit.synthetic import SYNTHETIC_KEY, SYNTHETIC_HOST, create_synthetic_client, run_synthetic
from sdp_audit.topology import discover_topology
from sdp_audit.transport import ApiError, ReadOnlyClient
from test_topology import FakeClient, page
from test_transport import FakeClock, FakeOpener, Response

CANARY = "PRIVATE-CANARY-do-not-disclose-738c29"


def make_client(responses, **options):
    clock = FakeClock()
    client = ReadOnlyClient(SYNTHETIC_HOST, SYNTHETIC_KEY, ALLOWED_PATTERNS,
                            clock=clock, sleep=clock.sleep, **options)
    opener = FakeOpener(clock, responses)
    client._opener = opener
    return client, opener, clock


def error_response(code, status=400, message="Invalid input", **kwargs):
    return Response({"response_status": {"status_code": code, "status": "failed", "message": message}}, status, **kwargs)


def snapshot_for(client):
    env = EnvironmentSnapshot("2026-10-14T08:30:00+00:00", {"product": "SYNTHETIC"},
                              {"max_requests": client.max_requests})
    EnvironmentCollector(client).collect(env)
    return env


def small_documents():
    # Explicit local publication payload, not serialized source records.
    return {name: "synthetic " + name + "\n" for name in REPORT_NAMES}


class DiscoveryCompatibilityTests(unittest.TestCase):
    def test_initial_invalid_query_gets_one_minimal_same_endpoint_retry(self):
        client = FakeClient([ApiError("invalid_response", "Rejected", 400, (4008,), classification="INVALID_QUERY"), page([7, 11])])
        topology = discover_topology(client)
        self.assertTrue(topology.complete)
        self.assertEqual([p.id for p in topology.portals], ["7", "11"])
        self.assertEqual(len(client.calls), 2)
        self.assertEqual({call["path"] for call in client.calls}, {"/portals"})
        self.assertTrue(all(call["portal_id"] is None for call in client.calls))
        first = json.loads(client.calls[0]["params"]["input_data"])["list_info"]
        second = json.loads(client.calls[1]["params"]["input_data"])["list_info"]
        self.assertIn("sort_field", first)
        self.assertEqual(set(second), {"row_count", "start_index"})
        self.assertEqual(topology.diagnostics[0]["api_codes"], [4008])
        self.assertEqual(topology.diagnostics[0]["compatibility_retry"], "minimal_pagination_same_endpoint")

    def test_minimal_retry_is_not_repeated(self):
        error = ApiError("invalid_response", "Rejected", 400, (4008,), classification="INVALID_QUERY")
        client = FakeClient([error, error])
        result = discover_topology(client)
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(result.outcome, "INVALID_QUERY")
        self.assertFalse(result.complete)

    def test_no_query_rewrite_after_successful_first_page(self):
        client = FakeClient([page([7], True, 1), ApiError("invalid_response", "Rejected", 400, classification="INVALID_QUERY")])
        result = discover_topology(client, page_size=1)
        self.assertEqual(len(client.calls), 2)
        self.assertFalse(result.complete)
        self.assertEqual([p.id for p in result.portals], ["7"])

    def test_generic_denial_never_causes_fallback_or_bruteforce(self):
        client = FakeClient([ApiError("forbidden", "Denied", 403, (4002,))])
        result = discover_topology(client)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(result.outcome, "PERMISSION_DENIED")
        self.assertFalse(result.portals)

    def test_unsupported_path_never_causes_fallback(self):
        client = FakeClient([ApiError("unsupported", "Missing", 404, (4007,))])
        result = discover_topology(client)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(result.outcome, "ENDPOINT_UNSUPPORTED")

    def test_media_type_errors_do_not_trigger_pagination_fallback(self):
        for status in (406, 415):
            with self.subTest(status=status):
                client = FakeClient([ApiError("invalid_response", "Rejected", status, classification="INVALID_QUERY")])
                discover_topology(client)
                self.assertEqual(len(client.calls), 1)

    def test_retry_still_obeys_global_request_budget(self):
        client, opener, _ = make_client([error_response(4008)], max_requests=1)
        result = discover_topology(client)
        self.assertEqual(result.outcome, "REQUEST_BUDGET_REACHED")
        self.assertEqual(len(opener.calls), 1)
        self.assertFalse(result.portals)

    def test_retry_and_later_portal_share_global_limiter(self):
        client, opener, clock = make_client([error_response(4008), Response(page([7])), Response({"requests": [], "response_status": {"status_code": 2000, "status": "success"}})])
        result = discover_topology(client)
        client.get_json("/requests", portal_id=result.portals[0].id)
        self.assertEqual([row[0] for row in opener.calls], [0.0, 2.0, 4.0])
        self.assertEqual(opener.calls[-1][1].get_header("Portalid"), "7")
        self.assertTrue(all(row[1].get_method() == "GET" and row[1].data is None for row in opener.calls))
        self.assertTrue(all(SYNTHETIC_KEY not in row[1].full_url for row in opener.calls))

    def test_parse_error_retains_successful_http_protocol_evidence(self):
        client, _, _ = make_client([Response({"response_status": {"status_code": 2000, "status": "success"}}, headers={"Content-Type": "application/json"})])
        result = discover_topology(client)
        self.assertEqual(result.outcome, "PARSE_ERROR")
        diagnostic = result.diagnostics[-1]
        self.assertEqual(diagnostic["http_status"], 200)
        self.assertEqual(diagnostic["api_codes"], [2000])
        self.assertEqual(diagnostic["response_format"], "json_object")


class StartupDiagnosticTests(unittest.TestCase):
    def test_tls_error_has_type_evidence_without_exception_text(self):
        client, opener, _ = make_client([urllib.error.URLError(ssl.SSLCertVerificationError(1, CANARY))])
        result = discover_topology(client)
        diagnostic = result.diagnostics[-1]
        self.assertEqual(diagnostic["classification"], "NETWORK_ERROR")
        self.assertEqual(diagnostic["cause"], "tls_configuration")
        self.assertEqual(diagnostic["transport_detail"], "TLS_CERTIFICATE_VERIFICATION_FAILED")
        self.assertIsNone(diagnostic["http_status"])
        self.assertEqual(len(opener.calls), 1)
        self.assertNotIn(CANARY, json.dumps(diagnostic))
        self.assertIn("--ca-file", "\n".join(diagnostic_lines(diagnostic)))

    def test_html_is_identified_without_body_or_header_leak(self):
        client, _, _ = make_client([Response(raw=("<!DOCTYPE html><html>" + CANARY + "</html>").encode(), headers={"Content-Type": "text/html; private=" + CANARY})])
        result = discover_topology(client)
        diagnostic = result.diagnostics[-1]
        self.assertEqual(result.outcome, "PARSE_ERROR")
        self.assertEqual(diagnostic["http_status"], 200)
        self.assertEqual(diagnostic["response_format"], "html")
        self.assertEqual(diagnostic["content_type"], "text/html")
        self.assertNotIn(CANARY, json.dumps(diagnostic))
        self.assertEqual(client.stats["authentication"], "unverified")

    def test_json_without_sdp_envelope_does_not_confirm_authentication(self):
        client, _, _ = make_client([Response({"gateway": "alive"})])
        discover_topology(client)
        self.assertEqual(client.stats["authentication"], "unverified")

    def test_sdp_success_can_confirm_authentication(self):
        client, _, _ = make_client([Response(page([7]))])
        discover_topology(client)
        self.assertEqual(client.stats["authentication"], "valid")

    def test_redirect_is_diagnosed_without_location_disclosure(self):
        client, opener, _ = make_client([Response(status=302, headers={"Location": "https://example.invalid/" + CANARY})])
        result = discover_topology(client)
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(result.diagnostics[-1]["transport_detail"], "REDIRECT_BLOCKED")
        self.assertNotIn(CANARY, json.dumps(result.diagnostics))

    def test_unknown_content_type_is_not_retained(self):
        client, _, _ = make_client([Response(raw=b"not json", headers={"Content-Type": CANARY})])
        result = discover_topology(client)
        self.assertEqual(result.diagnostics[-1]["content_type"], "other")
        self.assertNotIn(CANARY, json.dumps(result.diagnostics))

    def test_dns_exception_is_classified_without_text(self):
        error = urllib.error.URLError(socket.gaierror(-2, CANARY))
        client, opener, _ = make_client([error] * 4)
        result = discover_topology(client)
        self.assertEqual(result.diagnostics[-1]["transport_detail"], "DNS_LOOKUP_FAILED")
        self.assertNotIn(CANARY, json.dumps(result.diagnostics))

    def test_request_has_documented_get_headers_and_no_body(self):
        client, opener, _ = make_client([Response(page([7]))])
        discover_topology(client)
        request = opener.calls[0][1]
        self.assertEqual(request.get_header("Content-type"), "application/x-www-form-urlencoded")
        self.assertIsNone(request.data)
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.get_header("Portalid"))

    def test_console_diagnostics_do_not_trust_arbitrary_message_strings(self):
        item = {"classification": "PERMISSION_DENIED", "http_status": 403, "api_codes": [4002],
                "endpoint": "/portals", "module": "topology", "message": CANARY,
                "api_message": CANARY, "cause": CANARY, "message_sanitized": True,
                "content_type": CANARY, "transport_detail": CANARY}
        text = "\n".join(diagnostic_lines(item))
        self.assertNotIn(CANARY, text)
        self.assertIn("403", text)
        self.assertIn("4002", text)
        self.assertNotIn("Project Admin", text)

    def test_recognized_sdp_message_remains_visible(self):
        lines = diagnostic_lines({"classification": "PERMISSION_DENIED", "http_status": 403,
                                  "api_codes": [4002], "api_message": "User does not have this permission",
                                  "endpoint": "/portals", "message_sanitized": True})
        self.assertIn("User does not have this permission", "\n".join(lines))

    def test_progress_names_failure_instead_of_only_zero_selected(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            ProgressPrinter(500)({"event": "topology_complete", "portals": 0,
                                  "outcome": "ENDPOINT_UNSUPPORTED", "complete": False})
        self.assertIn("ENDPOINT_UNSUPPORTED", stream.getvalue())
        self.assertIn("source coverage is unknown", stream.getvalue())

    def test_no_portals_creates_unknown_acceptance_blocker(self):
        client, _, _ = create_synthetic_client("portal_discovery_unavailable")
        assessment = analyze_environment(snapshot_for(client))
        gap = next(item for item in assessment.findings if item.id == "TOPOLOGY_COVERAGE")
        self.assertEqual(gap.status, "UNKNOWN")
        self.assertIsNone(gap.affected_count)
        self.assertTrue(any(item["finding_id"] == gap.id for item in assessment.environment["acceptance_blockers"]))
        self.assertIn(gap.id, next(q for q in assessment.questions if q["id"] == "Q7")["finding_ids"])

    def test_no_customer_content_in_small_diagnostics_json(self):
        client, _, _ = create_synthetic_client("multi")
        env = snapshot_for(client)
        text = diagnostics_document(env)
        self.assertNotIn(SYNTHETIC_KEY, text)
        self.assertNotIn("description", text)
        self.assertIn("PERMISSION_DENIED", text)
        self.assertEqual(json.loads(text)["tool_version"], __version__)


class VerifiedArtifactTests(unittest.TestCase):
    def test_output_preflight_writes_reads_and_cleans_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "fresh"
            prepare_output(output)
            self.assertEqual(list(output.iterdir()), [])

    def test_preflight_error_metadata_never_contains_underlying_text(self):
        error = PermissionError(errno.EACCES, CANARY, CANARY)
        self.assertEqual(failure_metadata(error, "local-file-operation", "prepare")["classification"], "ACCESS_DENIED")
        self.assertNotIn(CANARY, json.dumps(failure_metadata(error, "local-file-operation", "prepare")))

    def test_verified_publication_contains_all_formats_manifest_and_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "assessment-test"
            receipt = publish_documents(small_documents(), output)
            self.assertTrue(receipt.complete)
            self.assertTrue(receipt.bundle.is_file())
            self.assertTrue(receipt.manifest.is_file())
            with zipfile.ZipFile(receipt.bundle) as archive:
                self.assertEqual(set(archive.namelist()), {*REPORT_NAMES, "report-manifest.json"})
                self.assertEqual(archive.read("report.html").decode(), small_documents()["report.html"])
            manifest = json.loads(receipt.manifest.read_text())
            for row in manifest["files"]:
                self.assertEqual(row["sha256"], hashlib.sha256(receipt.paths[row["name"]].read_bytes()).hexdigest())

    def test_report_write_requires_readback(self):
        assessment = analyze_environment(run_synthetic("single")[0])
        original_replace = __import__("os").replace
        def remove_html(source, target):
            original_replace(source, target)
            if Path(target).name == "report.html":
                Path(target).unlink()
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.report.os.replace", side_effect=remove_html):
            with self.assertRaises(FileNotFoundError):
                write_reports(assessment, temp)

    def test_byte_mismatch_is_detected_without_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "report.html"
            path.write_bytes(b"changed")
            with self.assertRaises(ArtifactError) as caught:
                verify_bytes(path, b"original")
            self.assertEqual(caught.exception.code, "OUTPUT_CONTENT_MISMATCH")

    def test_symlink_is_not_a_verified_report(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "target"
            link = Path(temp) / "link"
            target.write_bytes(b"test")
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaises(ArtifactError):
                verify_bytes(link, b"test")

    def test_zip_is_built_without_directory_sweep(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "assessment-test"
            output.mkdir()
            (output / "private.txt").write_text(CANARY)
            receipt = publish_documents(small_documents(), output)
            with zipfile.ZipFile(receipt.bundle) as archive:
                self.assertNotIn("private.txt", archive.namelist())
                self.assertTrue(all(CANARY.encode() not in archive.read(name) for name in archive.namelist()))

    def test_html_write_failure_still_produces_zip_with_html(self):
        original = atomic_write_bytes
        def fail_html(path, content):
            if path.name == "report.html":
                raise PermissionError(errno.EACCES, CANARY)
            return original(path, content)
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.artifacts.atomic_write_bytes", side_effect=fail_html):
            receipt = publish_documents(small_documents(), Path(temp) / "assessment-test")
            self.assertFalse(receipt.complete)
            self.assertNotIn("report.html", receipt.paths)
            self.assertIsNotNone(receipt.bundle)
            self.assertNotIn(CANARY, json.dumps(receipt.failures))
            with zipfile.ZipFile(receipt.bundle) as archive:
                self.assertIn("report.html", archive.namelist())
                self.assertEqual(archive.read("report.html").decode(), small_documents()["report.html"])

    def test_failed_zip_does_not_remove_successful_report_formats(self):
        original = atomic_write_bytes
        def fail_zip(path, content):
            if path.suffix == ".zip":
                raise PermissionError(errno.EACCES, CANARY)
            return original(path, content)
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.artifacts.atomic_write_bytes", side_effect=fail_zip):
            receipt = publish_documents(small_documents(), Path(temp) / "assessment-test")
            self.assertFalse(receipt.complete)
            self.assertIsNone(receipt.bundle)
            self.assertTrue(set(REPORT_NAMES).issubset(receipt.paths))

    def test_deleted_report_is_not_printed_as_openable(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = publish_documents(small_documents(), Path(temp) / "assessment-test")
            receipt.paths["report.html"].unlink()
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertFalse(_print_publication(receipt))
            self.assertNotIn("Open verified HTML:", output.getvalue())
            self.assertIn("Verified report ZIP:", output.getvalue())
            self.assertIn("FILE_NOT_FOUND", errors.getvalue())

    def test_partial_publication_errors_contain_only_fixed_names(self):
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.artifacts.atomic_write_bytes", side_effect=OSError(errno.ENOSPC, CANARY, CANARY)):
            receipt = publish_documents(small_documents(), Path(temp) / "assessment-test")
            text = json.dumps(receipt.failures)
            self.assertNotIn(CANARY, text)
            self.assertFalse(receipt.complete)
            self.assertFalse(receipt.paths)

    def test_no_arbitrary_file_can_be_published(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                publish_documents({**small_documents(), "../bad": CANARY}, Path(temp))

    def test_bundle_keeps_dots_in_directory_name(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = publish_documents(small_documents(), Path(temp) / "reports.v2")
            self.assertEqual(receipt.bundle.name, "reports.v2.zip")


class StartupCliTests(unittest.TestCase):
    def invoke(self, client, directory, *extra):
        output, errors = io.StringIO(), io.StringIO()
        with patch("sdp_audit.cli.ReadOnlyClient", return_value=client), \
             patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main(["--host", SYNTHETIC_HOST, "--output-dir", str(directory), *extra])
        return code, output.getvalue(), errors.getvalue()

    def test_unavailable_directory_prints_actual_http_sdp_and_verified_output(self):
        client, server, _ = create_synthetic_client("portal_discovery_unavailable")
        with tempfile.TemporaryDirectory() as temp:
            code, output, errors = self.invoke(client, temp, "--quiet")
            self.assertEqual(code, 2)
            self.assertEqual(len(server.calls), 1)
            self.assertIn("HTTP: 404", output)
            self.assertIn("4007", output)
            self.assertIn("ASSESSMENT NOT PERFORMED", output)
            self.assertNotIn("Assessment written.", output)
            path = Path(output.split("Open verified HTML: ", 1)[1].splitlines()[0])
            self.assertTrue(path.is_file())
            self.assertEqual(path.parent.parent, Path(temp))
            self.assertIn("UNKNOWN: 1", output)
            self.assertNotIn(SYNTHETIC_KEY, output + errors)

    def test_tls_stop_is_explained_without_requiring_report(self):
        client, _, _ = make_client([urllib.error.URLError(ssl.SSLCertVerificationError(1, CANARY))])
        with tempfile.TemporaryDirectory() as temp:
            code, output, errors = self.invoke(client, temp, "--quiet")
            self.assertEqual(code, 2)
            self.assertIn("TLS_CERTIFICATE_VERIFICATION_FAILED", output)
            self.assertIn("--ca-file", output)
            self.assertIn("NOT ESTABLISHED", output)
            self.assertNotIn(CANARY, output + errors)

    def test_diagnose_does_not_query_portal_modules(self):
        client, server, _ = create_synthetic_client("multi")
        with tempfile.TemporaryDirectory() as temp:
            code, output, _ = self.invoke(client, temp, "--diagnose", "--quiet")
            self.assertEqual(code, 0)
            self.assertEqual({call["path"] for call in server.calls}, {"/portals"})
            self.assertTrue(all(call["portal_id"] is None for call in server.calls))
            self.assertIn("no module inventory was requested", output)
            document = json.loads(next(Path(temp).glob("*/diagnostics.json")).read_text())
            self.assertEqual(document["mode"], "DISCOVERY_ONLY")
            self.assertEqual(document["topology"]["portals_observed"], 4)

    def test_local_output_check_uses_no_host_credential_or_http_client(self):
        output, errors = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temp, \
             patch("builtins.input", side_effect=AssertionError("no prompt")), \
             patch("sdp_audit.cli.acquire_api_key", side_effect=AssertionError("no key")), \
             patch("sdp_audit.cli.ReadOnlyClient", side_effect=AssertionError("no client")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertEqual(main(["--check-output", "--output-dir", temp]), 0)
            self.assertTrue(next(Path(temp).glob("*/report.html")).is_file())
            self.assertTrue(next(Path(temp).glob("*.zip")).is_file())
            self.assertIn("PASSED", output.getvalue())

    def test_preflight_failure_uses_no_api_attempt(self):
        client, opener, _ = make_client([])
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.cli.prepare_output", side_effect=PermissionError(errno.EACCES, CANARY)):
            code, output, errors = self.invoke(client, temp)
            self.assertEqual(code, 1)
            self.assertEqual(opener.calls, [])
            self.assertNotIn("Open verified HTML", output)
            self.assertIn("ACCESS_DENIED", errors)
            self.assertNotIn(CANARY, output + errors)

    def test_missing_html_returns_nonzero_but_preserves_zip(self):
        client, _, _ = create_synthetic_client("portal_discovery_unavailable")
        original = atomic_write_bytes
        def fail_html(path, content):
            if path.name == "report.html":
                raise PermissionError(errno.EACCES, CANARY)
            return original(path, content)
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.artifacts.atomic_write_bytes", side_effect=fail_html):
            code, output, errors = self.invoke(client, temp)
            self.assertEqual(code, 1)
            self.assertNotIn("Open verified HTML", output)
            self.assertIn("Verified report ZIP", output)
            self.assertNotIn(CANARY, output + errors)
            with zipfile.ZipFile(next(Path(temp).glob("*.zip"))) as archive:
                self.assertIn("report.html", archive.namelist())

    def test_all_output_failures_keep_console_diagnostics_without_secret(self):
        client, _, _ = create_synthetic_client("portal_discovery_unavailable")
        with tempfile.TemporaryDirectory() as temp, \
             patch("sdp_audit.cli.atomic_write_bytes", side_effect=PermissionError(errno.EACCES, CANARY)), \
             patch("sdp_audit.artifacts.publish_documents", wraps=publish_documents), \
             patch("sdp_audit.artifacts.atomic_write_bytes", side_effect=PermissionError(errno.EACCES, CANARY)), \
             patch("sdp_audit.cli.prepare_output", side_effect=lambda p: p.mkdir(parents=True)):
            code, output, errors = self.invoke(client, temp)
            self.assertEqual(code, 1)
            self.assertIn("HTTP: 404", output)
            self.assertNotIn("Open verified HTML", output)
            self.assertNotIn("Verified report ZIP:", output)
            self.assertNotIn(CANARY, output + errors)

    def test_no_conflicting_self_test_modes(self):
        with tempfile.TemporaryDirectory() as temp, patch("sdp_audit.cli.acquire_api_key", side_effect=AssertionError), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--check-output", "--check-key-input", "--output-dir", temp]), 1)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_actual_local_http_404_cli_uses_only_get_and_writes_files(self):
        calls = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                calls.append((self.command, self.path, self.headers.get("authtoken"), self.headers.get("PORTALID")))
                payload = json.dumps({"response_status": {"status_code": 4007, "status": "failed", "message": "Invalid URL"}}).encode()
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            output = io.StringIO()
            with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", {"SDP_API_KEY": SYNTHETIC_KEY}), contextlib.redirect_stdout(output):
                code = main(["--host", "http://127.0.0.1:" + str(server.server_port), "--allow-http", "--quiet", "--output-dir", temp])
                self.assertEqual(code, 2)
                self.assertEqual(len(calls), 1)
                self.assertEqual(calls[0][0], "GET")
                self.assertNotIn(SYNTHETIC_KEY, calls[0][1])
                self.assertIsNone(calls[0][3])
                self.assertTrue(next(Path(temp).glob("*/report.html")).is_file())
                self.assertTrue(next(Path(temp).glob("*.zip")).is_file())
                self.assertIn("HTTP: 404", output.getvalue())
                self.assertNotIn(SYNTHETIC_KEY, output.getvalue())
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
