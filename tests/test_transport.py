"""Transport safety tests; all HTTP traffic is simulated in memory."""

from __future__ import annotations

import email.message
import concurrent.futures
import http.client
import io
import json
import ssl
import traceback
import unittest
import urllib.error
import urllib.request
import urllib.response
from unittest import mock

from sdp_audit.transport import ApiError, BudgetExceeded, ReadOnlyClient, _NoRedirectHandler


SECRET = "test-private-token-8ba421"


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, duration):
        self.sleeps.append(duration)
        self.now += duration


class Response(io.BytesIO):
    def __init__(self, payload=None, status=200, headers=None, raw=None):
        if payload is None:
            payload = {"response_status": {"status_code": 2000, "status": "success"}}
        super().__init__(raw if raw is not None else json.dumps(payload).encode("utf-8"))
        self.code = status
        self.headers = email.message.Message()
        for key, value in (headers or {}).items():
            self.headers[key] = value

    def getcode(self):
        return self.code


class FakeOpener:
    def __init__(self, clock, responses):
        self.clock = clock
        self.responses = list(responses)
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((self.clock(), request, timeout))
        if not self.responses:
            raise AssertionError("Unexpected HTTP attempt")
        result = self.responses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


class TransportTests(unittest.TestCase):
    def client(self, responses=(), **kwargs):
        clock = kwargs.pop("clock", FakeClock())
        base_url = kwargs.pop("base_url", "https://sdp.example.test")
        client = ReadOnlyClient(
            base_url,
            kwargs.pop("api_key", SECRET),
            kwargs.pop("allowed_patterns", [r"/requests", r"/requests/[0-9]+", r"/requests/_metainfo"]),
            clock=clock,
            sleep=clock.sleep,
            **kwargs,
        )
        opener = FakeOpener(clock, responses)
        client._opener = opener
        return client, opener, clock

    def test_header_auth_context_suffix_and_get(self):
        client, opener, _ = self.client(
            [Response({"requests": []})], base_url="https://SDP.example.test:8443/helpdesk/api/v3/", portal_id="9"
        )
        result = client.get_json("/requests", {"input_data": '{"list_info":{"row_count":1}}'})
        self.assertEqual(result, {"requests": []})
        self.assertEqual(client.base_url, "https://sdp.example.test:8443/helpdesk")
        _, request, _ = opener.calls[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertEqual(request.get_header("Authtoken"), SECRET)
        self.assertEqual(request.get_header("Portalid"), "9")
        self.assertEqual(request.get_header("Accept"), "application/vnd.manageengine.sdp.v3+json")
        self.assertTrue(request.full_url.startswith(client.base_url + "/api/v3/requests?input_data="))
        self.assertNotIn(SECRET, request.full_url)

    def test_malicious_paths_and_prefix_matches_are_rejected_without_requests(self):
        client, opener, _ = self.client(allowed_patterns=[r"/requests.*"])
        bad_paths = [
            "https://evil.example/requests", "//evil.example/requests", "requests", "/requests/../users",
            "/requests/./1", "/requests/%2e%2e/users", "/requests/%252e%252e/users", "/requests?operation=delete",
            "/requests#evil", "/requests\\users", "/requests//1", "/requests/", "/requests\n", "/requests/\x00",
            "/requests/１", "/requests;delete", "/requests/1.json",
        ]
        for path in bad_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                client.get_json(path)
        exact, exact_opener, _ = self.client()
        with self.assertRaises(ValueError):
            exact.get_json("/requests/123/delete")
        self.assertEqual(opener.calls, [])
        self.assertEqual(exact_opener.calls, [])

    def test_untrusted_base_url_variants_are_rejected(self):
        urls = [
            "https://user:password@sdp.example.test", "https://sdp.example.test?token=x", "https://sdp.example.test?",
            "https://sdp.example.test#", "https://sdp.example.test/../sdp", "https://sdp.example.test/%2e%2e",
            "https://sdp.example.test\\@evil.test", "https://sdp.example.test/\n", "ftp://sdp.example.test",
            "https://sdp.example.test//sdp", "https://sdp.example.test/api/v3/requests", "http://sdp.example.test",
            "https://sdp.example.test:999999", "https://sdp.example.test:0", "sdp.example.test", "//sdp.example.test",
        ]
        for url in urls:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.client(base_url=url)

    def test_credential_query_and_method_override_rejected(self):
        client, opener, _ = self.client()
        for params in [
            {"api_key": SECRET}, {"authtoken": "other"}, {"Authorization": "other"},
            {"input_data": json.dumps({"echo": SECRET})}, {"_method": "DELETE"}, {"method": "POST"},
        ]:
            with self.subTest(params=str(list(params))), self.assertRaises(ValueError) as raised:
                client.get_json("/requests", params)
            self.assertNotIn(SECRET, str(raised.exception))
        self.assertEqual(opener.calls, [])

    def test_echoed_secret_never_reaches_return_value_stats_repr_or_events(self):
        events = []
        data = {"requests": [{"description": f"The token was {SECRET}", SECRET: [SECRET, {"value": SECRET}]}]}
        client, _, _ = self.client([Response(data)], progress=events.append)
        result = client.get_json("/requests")
        for output in (json.dumps(result), json.dumps(client.stats), repr(client), json.dumps(events)):
            self.assertNotIn(SECRET, output)
        self.assertIn("[REDACTED]", json.dumps(result))

    def test_error_body_is_never_in_exception_or_progress(self):
        events = []
        client, _, _ = self.client([
            Response({"response_status": {"status_code": 4002, "message": f"secret: {SECRET}"}}, status=400)
        ], progress=events.append)
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests")
        self.assertEqual(raised.exception.kind, "forbidden")
        self.assertNotIn(SECRET, str(raised.exception))
        self.assertNotIn(SECRET, repr(raised.exception))
        self.assertNotIn(SECRET, json.dumps(events))

    def test_numeric_and_url_encoded_echoes_are_redacted(self):
        events = []
        numeric = "2345678901234567890"
        client, _, _ = self.client([
            Response({"response_status": {"status": "failed", "status_code": int(numeric)}})
        ], api_key=numeric, progress=events.append)
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests")
        self.assertNotIn(numeric, repr(raised.exception))
        self.assertNotIn(numeric, json.dumps(events))
        special = "api+key/with=reserved:characters"
        encoded = "api%2Bkey%2Fwith%3Dreserved%3Acharacters"
        client, _, _ = self.client([Response({"value": encoded})], api_key=special)
        self.assertEqual(client.get_json("/requests"), {"value": "[REDACTED]"})
        with self.assertRaises(ValueError):
            client.get_json("/requests", {"input_data": encoded})

    def test_all_redirect_codes_fail_without_following(self):
        for code in (301, 302, 303, 307, 308):
            for location in ("https://evil.example.test/leak", "https://sdp.example.test/new-path", "http://sdp.example.test/"):
                with self.subTest(code=code, location=location):
                    calls = []

                    class MockHTTPS(urllib.request.HTTPSHandler):
                        def https_open(self, req):
                            calls.append(req)
                            headers = email.message.Message()
                            headers["Location"] = location
                            response = urllib.response.addinfourl(io.BytesIO(b""), headers, req.full_url, code)
                            response.msg = "Redirect"
                            return response

                    client, _, _ = self.client()
                    client._opener = urllib.request.build_opener(_NoRedirectHandler(), MockHTTPS())
                    with self.assertRaises(ApiError) as raised:
                        client.get_json("/requests")
                    self.assertEqual(raised.exception.kind, "network")
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(client.stats["redirects_followed"], 0)
                    self.assertNotIn(location, str(raised.exception))

    def test_default_pacing_has_no_bursts_and_counts_every_request(self):
        client, opener, clock = self.client([Response(), Response(), Response(), Response()])
        client.get_json("/requests")
        client.get_json("/requests/1")
        clock.now += 20
        client.get_json("/requests/2")
        client.get_json("/requests/3")
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 22, 24])
        self.assertTrue(all(0 < duration <= 1 for duration in clock.sleeps))
        self.assertEqual(client.stats["requests"], 4)
        self.assertEqual(client.stats["successful_requests"], 4)

    def test_nested_limit_code_retries_even_with_http_200_or_400(self):
        for status in (200, 400):
            with self.subTest(status=status):
                client, opener, _ = self.client([
                    Response({"response_status": [{"status_code": 4000, "messages": [{"status_code": "4015"}]}]}, status=status),
                    Response(),
                ], rpm=60)
                client.get_json("/requests")
                self.assertEqual([call[0] for call in opener.calls], [0, 2])
                self.assertEqual(client.stats["retries"], 1)
                self.assertEqual(client.stats["failures_by_kind"], {"throttled": 1})

    def test_record_status_fields_are_not_api_errors(self):
        payload = {"requests": [{"status_code": 4022, "response_status": {"status_code": 4015}, "status": "failed"}]}
        client, opener, _ = self.client([Response(payload)])
        self.assertEqual(client.get_json("/requests"), payload)
        self.assertEqual(len(opener.calls), 1)

    def test_retry_after_seconds_and_http_date_are_honored(self):
        for header in ("7", "Thu, 01 Jan 1970 00:16:47 GMT"):
            with self.subTest(header=header), mock.patch("sdp_audit.transport.time.time", return_value=1000):
                client, opener, clock = self.client([
                    Response(status=429, headers={"Retry-After": header}), Response()
                ], rpm=60)
                client.get_json("/requests")
                self.assertEqual([call[0] for call in opener.calls], [0, 7])
                self.assertTrue(all(duration <= 1 for duration in clock.sleeps))

    def test_invalid_retry_after_still_uses_backoff(self):
        for header in ("invalid", "NaN", "-2"):
            with self.subTest(header=header):
                client, opener, _ = self.client([Response(status=429, headers={"Retry-After": header}), Response()])
                client.get_json("/requests")
                self.assertEqual([call[0] for call in opener.calls], [0, 2])

    def test_retry_after_cannot_be_shortened_to_fit_runtime_budget(self):
        client, opener, clock = self.client([Response(status=429, headers={"Retry-After": "120"})], max_runtime=10)
        with self.assertRaises(BudgetExceeded):
            client.get_json("/requests")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(clock.sleeps, [])

    def test_retry_count_is_bounded_and_exponential(self):
        client, opener, _ = self.client([Response(status=429) for _ in range(4)], rpm=60)
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests")
        self.assertEqual(raised.exception.kind, "throttled")
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 6, 14])
        self.assertEqual(client.stats["retries"], 3)

    def test_service_unavailable_and_network_errors_are_retried(self):
        client, opener, _ = self.client([
            Response(status=503, raw=b"temporarily unavailable"),
            urllib.error.URLError("simulated connection reset"),
            Response(),
        ])
        client.get_json("/requests")
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 6])

    def test_http_protocol_failures_retry_safely_and_can_recover(self):
        class IncompleteBody(Response):
            def read1(self, size=-1):
                raise http.client.IncompleteRead(SECRET.encode(), 123)

        events = []
        incomplete = IncompleteBody()
        client, opener, _ = self.client([
            http.client.BadStatusLine("Malformed status line " + SECRET),
            incomplete,
            Response({"requests": []}),
        ], progress=events.append)
        self.assertEqual(client.get_json("/requests"), {"requests": []})
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 6])
        self.assertEqual(client.stats["failures_by_kind"], {"network": 2})
        self.assertTrue(incomplete.closed)
        self.assertNotIn(SECRET, json.dumps(events))

    def test_exhausted_http_protocol_errors_cannot_leak_server_text(self):
        cases = (
            lambda: http.client.BadStatusLine("Malformed status line " + SECRET),
            lambda: http.client.IncompleteRead(SECRET.encode(), 123),
            lambda: http.client.RemoteDisconnected("Connection closed " + SECRET),
        )
        for factory in cases:
            with self.subTest(error=type(factory()).__name__):
                events = []
                client, opener, _ = self.client([factory() for _ in range(4)], progress=events.append)
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests")
                error = raised.exception
                self.assertEqual(error.kind, "network")
                self.assertEqual(len(opener.calls), 4)
                for output in (
                    str(error), repr(error), "".join(traceback.format_exception(type(error), error, error.__traceback__)),
                    json.dumps(client.stats), json.dumps(events),
                ):
                    self.assertNotIn(SECRET, output)

    def test_incomplete_body_retries_are_request_budgeted(self):
        class IncompleteBody(Response):
            def read1(self, size=-1):
                raise http.client.IncompleteRead(SECRET.encode(), 123)

        client, opener, clock = self.client([IncompleteBody()], max_requests=1)
        with self.assertRaises(BudgetExceeded):
            client.get_json("/requests")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(clock.sleeps, [])

    def test_malformed_unicode_deep_json_and_parser_limits_are_safe(self):
        bodies = (
            b'{"value":"\xff"}',
            b'{"value":"\\ud800"}',
            b'{"\\udfff":"value"}',
            b'{"nested":' + b'[' * 2000 + b'"' + SECRET.encode() + b'"' + b']' * 2000 + b'}',
            b'{"number":' + b'9' * 1000 + b'}',
            b'{"number":1e999}',
            b'{"number":NaN}',
            b'{"number":Infinity}',
        )
        for index, body in enumerate(bodies):
            with self.subTest(case=index):
                response = Response(raw=body)
                client, opener, _ = self.client([response])
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests")
                error = raised.exception
                self.assertEqual(error.kind, "invalid_response")
                self.assertEqual(len(opener.calls), 1)
                self.assertTrue(response.closed)
                self.assertNotIn(SECRET, "".join(traceback.format_exception(type(error), error, error.__traceback__)))

    def test_auth_failure_is_terminal_across_resources_and_never_retried(self):
        for response in (
            Response(status=401, raw=SECRET.encode()),
            Response({"response_status": [{"messages": [{"status_code": 4022}]}]}, status=400),
        ):
            with self.subTest(http=response.code):
                client, opener, _ = self.client([response])
                for path in ("/requests", "/requests/1"):
                    with self.assertRaises(ApiError) as raised:
                        client.get_json(path)
                    self.assertEqual(raised.exception.kind, "authentication")
                    self.assertNotIn(SECRET, str(raised.exception))
                self.assertEqual(len(opener.calls), 1)

    def test_permission_unsupported_license_and_invalid_response_kinds(self):
        cases = [
            (403, {}, "forbidden"), (200, {"response_status": {"status_code": 4002}}, "forbidden"),
            (404, {}, "unsupported"), (200, {"response_status": {"status_code": 4007}}, "unsupported"),
            (200, {"response_status": {"status_code": 7001}}, "license"),
            (400, {}, "invalid_response"),
            (200, {"response_status": {"status": "failed"}}, "invalid_response"),
        ]
        for status, payload, kind in cases:
            with self.subTest(status=status, kind=kind):
                client, opener, _ = self.client([Response(payload, status=status)])
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests")
                self.assertEqual(raised.exception.kind, kind)
                self.assertEqual(len(opener.calls), 1)

    def test_request_budget_includes_failed_attempts_and_retries(self):
        client, opener, clock = self.client([Response(status=503)], max_requests=1)
        with self.assertRaises(BudgetExceeded):
            client.get_json("/requests")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(clock.sleeps, [])
        with self.assertRaises(BudgetExceeded):
            client.get_json("/requests")
        self.assertEqual(len(opener.calls), 1)

    def test_runtime_budget_prevents_next_call_and_clamps_socket_timeout(self):
        client, opener, clock = self.client([Response()], max_runtime=4, timeout=30)
        clock.now = 2.5
        client.get_json("/requests")
        self.assertEqual(opener.calls[0][2], 1.5)
        with self.assertRaises(BudgetExceeded):
            client.get_json("/requests")
        self.assertEqual(len(opener.calls), 1)

    def test_oversized_and_nonobject_responses_are_rejected(self):
        responses = [
            Response(headers={"Content-Length": str(16 * 1024 * 1024 + 1)}),
            Response(raw=b"x" * (16 * 1024 * 1024 + 1)),
            Response(raw=b"[]"), Response(raw=b"not json"),
        ]
        for response in responses:
            with self.subTest(length=response.headers.get("Content-Length")):
                client, opener, _ = self.client([response])
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests")
                self.assertEqual(raised.exception.kind, "invalid_response")
                self.assertEqual(len(opener.calls), 1)
                self.assertTrue(response.closed)

    def test_tls_failure_never_falls_back_or_retries(self):
        client, opener, _ = self.client([
            urllib.error.URLError(ssl.SSLCertVerificationError("certificate verify failed " + SECRET))
        ])
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests")
        self.assertEqual(raised.exception.kind, "tls")
        self.assertNotIn(SECRET, str(raised.exception))
        self.assertEqual(len(opener.calls), 1)

    def test_security_settings_are_explicit_and_reported(self):
        client, _, _ = self.client(base_url="http://sdp.example.test", allow_http=True)
        self.assertTrue(client.stats["http_allowed"])
        self.assertTrue(client.stats["tls_verification"])
        with mock.patch("sdp_audit.transport.urllib.request.build_opener") as builder:
            client = ReadOnlyClient("https://sdp.example.test", SECRET, ["/requests"], insecure_tls=True)
        tls_handler = builder.call_args.args[1]
        self.assertFalse(tls_handler._context.check_hostname)
        self.assertEqual(tls_handler._context.verify_mode, ssl.CERT_NONE)
        self.assertFalse(client.stats["tls_verification"])
        with self.assertRaises(ValueError):
            self.client(ca_file="does-not-exist", insecure_tls=True)

    def test_invalid_pacing_timeout_and_budgets_fail_before_network(self):
        for rpm in (0, -1, 60.01, float("nan"), float("inf"), True):
            with self.subTest(rpm=rpm), self.assertRaises(ValueError):
                self.client(rpm=rpm)
        for kwargs in ({"timeout": 0}, {"max_runtime": float("nan")}, {"max_requests": 1.1}, {"max_requests": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.client(**kwargs)

    def test_per_call_portal_context_and_global_omission_share_one_pacer(self):
        client, opener, _ = self.client([Response() for _ in range(4)], portal_id="9")
        client.get_json("/requests", portal_id=None, endpoint_name="topology", module="topology")
        client.get_json("/requests", portal_id="3", endpoint_name="requests", module="requests")
        client.get_json("/requests", portal_id="7")
        client.get_json("/requests")  # Legacy constructor default remains usable.
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 4, 6])
        self.assertEqual([call[1].get_header("Portalid") for call in opener.calls], [None, "3", "7", "9"])
        self.assertEqual(client.stats["requests_by_scope"], {"global": 1, "portal:3": 1, "portal:7": 1, "portal:9": 1})
        self.assertEqual(client.last_response["portal_id"], "9")
        for _, request, _ in opener.calls:
            self.assertEqual(request.get_method(), "GET")
            self.assertIsNone(request.data)
            self.assertNotIn(SECRET, request.full_url)

    def test_concurrent_portal_calls_still_use_single_global_slots(self):
        client, opener, _ = self.client([Response() for _ in range(8)])
        def read(portal):
            return client.get_json("/requests", portal_id=str(portal))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(read, range(1, 9)))
        self.assertEqual(len(results), 8)
        self.assertEqual([call[0] for call in opener.calls], list(range(0, 16, 2)))
        self.assertEqual({call[1].get_header("Portalid") for call in opener.calls}, {str(i) for i in range(1, 9)})

    def test_permission_error_retains_actual_safe_context_and_does_not_abort_other_portals(self):
        events = []
        payload = {"response_status": {"status_code": 4000, "status": "failed", "messages": [{
            "status_code": 4002, "message": "User does not have this permission",
        }]}}
        client, opener, _ = self.client([Response(payload, status=403), Response()], progress=events.append)
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests", portal_id="7", endpoint_name="projects", module="projects")
        diagnostic = raised.exception.to_dict()
        self.assertEqual(diagnostic["classification"], "PERMISSION_DENIED")
        self.assertEqual(diagnostic["http_status"], 403)
        self.assertEqual(diagnostic["api_codes"], [4000, 4002])
        self.assertEqual(diagnostic["api_message"], "User does not have this permission")
        self.assertEqual(diagnostic["portal_id"], "7")
        self.assertEqual(diagnostic["endpoint_name"], "projects")
        self.assertEqual(diagnostic["module"], "projects")
        self.assertFalse(diagnostic["retryable"])
        self.assertFalse(diagnostic["raw_message_omitted"])
        self.assertNotIn("Project Admin", json.dumps(diagnostic))
        client.get_json("/requests", portal_id="8")
        self.assertEqual(len(opener.calls), 2)
        self.assertEqual(client.stats["authentication"], "valid")
        self.assertNotIn(SECRET, json.dumps(events))

    def test_arbitrary_status_message_is_omitted_in_all_diagnostic_surfaces(self):
        private = "Patient private clinical note; person@example.test; confidential.pdf"
        events = []
        payload = {"response_status": {"status_code": 4002, "message": f"{private}; token={SECRET}"}}
        client, _, _ = self.client([Response(payload, status=403)], progress=events.append)
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests", portal_id="3", endpoint_name="requests", module="requests")
        error = raised.exception
        self.assertEqual(error.classification, "PERMISSION_DENIED")
        self.assertTrue(error.raw_message_omitted)
        self.assertIsNone(error.api_message)
        for result in (str(error), repr(error), json.dumps(error.to_dict()), json.dumps(events),
                       json.dumps(client.stats), json.dumps(client.last_response),
                       "".join(traceback.format_exception(type(error), error, error.__traceback__))):
            self.assertNotIn(SECRET, result)
            self.assertNotIn("private clinical note", result)
            self.assertNotIn("person@example.test", result)
            self.assertNotIn("confidential.pdf", result)

    def test_specific_status_envelope_evidence_refines_generic_403(self):
        cases = (
            (7001, "Not allowed as per current license", "MODULE_NOT_AVAILABLE"),
            (4002, "PORTALID header is required", "PORTAL_CONTEXT_REQUIRED"),
            (4002, "Portal is not accessible", "PORTAL_NOT_ACCESSIBLE"),
            (4002, "Access to portal is denied", "PORTAL_NOT_ACCESSIBLE"),
            (4002, "Access to the specified portal is denied", "PORTAL_NOT_ACCESSIBLE"),
            (4002, "Access to the selected portal is denied", "PORTAL_NOT_ACCESSIBLE"),
            (4002, "Projects module is not enabled", "MODULE_NOT_ENABLED"),
            (4002, "Releases module is not licensed", "MODULE_NOT_AVAILABLE"),
            (4002, "API version is not supported", "API_VERSION_INCOMPATIBLE"),
            (4002, "Unknown access policy condition", "PERMISSION_DENIED"),
        )
        for code, message, classification in cases:
            with self.subTest(message=message):
                payload = {"response_status": {"status_code": code, "message": message}}
                client, opener, _ = self.client([Response(payload, status=403)])
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests", portal_id="3")
                self.assertEqual(raised.exception.classification, classification)
                self.assertEqual(raised.exception.http_status, 403)
                self.assertEqual(raised.exception.api_codes, (code,))
                self.assertEqual(len(opener.calls), 1)

    def test_mandatory_portalid_field_evidence_does_not_retain_input_values(self):
        payload = {"response_status": {"status_code": 4000, "messages": [{
            "status_code": 4012, "field": "portalid", "message": "PRIVATE FIELD INPUT",
        }], "status": "failed"}}
        client, opener, _ = self.client([Response(payload, status=400)])
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests", portal_id=None)
        self.assertEqual(raised.exception.classification, "PORTAL_CONTEXT_REQUIRED")
        self.assertIsNone(raised.exception.portal_id)
        self.assertNotIn("PRIVATE FIELD INPUT", json.dumps(raised.exception.to_dict()))
        self.assertIsNone(opener.calls[0][1].get_header("Portalid"))
        self.assertEqual(len(opener.calls), 1)  # No guessed portal retries.

    def test_nonpermission_http_and_api_outcomes_are_distinct(self):
        cases = (
            (404, 4007, "ENDPOINT_UNSUPPORTED"),
            (400, 4001, "INVALID_QUERY"),
            (400, 4012, "INVALID_QUERY"),
            (400, 4021, "INVALID_QUERY"),
            (200, 4999, "UNKNOWN_API_ERROR"),
        )
        for http, code, classification in cases:
            with self.subTest(http=http, code=code):
                client, opener, _ = self.client([Response({"response_status": {"status_code": code}}, status=http)])
                with self.assertRaises(ApiError) as raised:
                    client.get_json("/requests", portal_id="11")
                self.assertEqual(raised.exception.classification, classification)
                self.assertNotEqual(raised.exception.kind, "forbidden")
                self.assertEqual(len(opener.calls), 1)

    def test_authentication_failure_retains_401_api_codes_and_stays_global(self):
        payload = {"response_status": {"status_code": 4022, "message": "Invalid API Key"}}
        client, opener, _ = self.client([Response(payload, status=401)])
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests", portal_id="3")
        self.assertEqual(raised.exception.classification, "AUTHENTICATION_FAILED")
        self.assertEqual(raised.exception.api_codes, (4022,))
        self.assertEqual(raised.exception.api_message, "Invalid API Key")
        with self.assertRaises(ApiError):
            client.get_json("/requests", portal_id="8")
        self.assertEqual(len(opener.calls), 1)

    def test_api_server_failure_is_retried_even_with_http_200(self):
        payload = {"response_status": {"status_code": 4004, "message": "Internal Error"}}
        client, opener, _ = self.client([Response(payload) for _ in range(4)])
        with self.assertRaises(ApiError) as raised:
            client.get_json("/requests", portal_id="3")
        self.assertEqual(raised.exception.classification, "SERVER_ERROR")
        self.assertEqual(raised.exception.api_codes, (4004,))
        self.assertEqual([call[0] for call in opener.calls], [0, 2, 6, 14])
        self.assertEqual(client.stats["failures_by_classification"], {"SERVER_ERROR": 4})

    def test_request_budget_is_explicit_and_shared_by_portals(self):
        client, opener, _ = self.client([Response(), Response()], max_requests=2)
        client.get_json("/requests", portal_id=None)
        client.get_json("/requests", portal_id="3")
        with self.assertRaises(BudgetExceeded) as raised:
            client.get_json("/requests", portal_id="7")
        diagnostic = raised.exception.to_dict()
        self.assertEqual(diagnostic["reason"], "REQUEST_BUDGET_REACHED")
        self.assertEqual(diagnostic["requests"], 2)
        self.assertEqual(diagnostic["max_requests"], 2)
        self.assertEqual(len(opener.calls), 2)

    def test_time_budget_is_explicit_and_shared_by_portals(self):
        client, opener, clock = self.client([Response()], max_runtime=3)
        client.get_json("/requests", portal_id="3")
        clock.now = 3
        with self.assertRaises(BudgetExceeded) as raised:
            client.get_json("/requests", portal_id="7")
        self.assertEqual(raised.exception.reason, "TIME_BUDGET_REACHED")
        self.assertEqual(raised.exception.elapsed_seconds, 3)
        self.assertEqual(raised.exception.max_runtime_seconds, 3)
        self.assertEqual(len(opener.calls), 1)

    def test_retry_after_cooldown_continues_across_portal_switch(self):
        client, opener, _ = self.client([
            Response(status=429, headers={"Retry-After": "7"}), Response(), Response(),
        ])
        client.get_json("/requests", portal_id="3")
        client.get_json("/requests", portal_id="7")
        self.assertEqual([call[0] for call in opener.calls], [0, 7, 9])
        self.assertEqual([call[1].get_header("Portalid") for call in opener.calls], ["3", "3", "7"])

    def test_discovered_metadata_registration_is_exact_and_portal_scoped(self):
        path = "/custom_asset_medical_devices/_metainfo"
        client, opener, _ = self.client([Response()])
        with self.assertRaises(ValueError):
            client.get_json(path, portal_id="3")
        client.allow_metadata_path(path, portal_id="3", provenance="asset_modules")
        for portal in (None, "7"):
            with self.subTest(portal=portal), self.assertRaises(ValueError):
                client.get_json(path, portal_id=portal)
        client.get_json(path, portal_id="3", endpoint_name="asset_metadata", module="assets")
        self.assertEqual(len(opener.calls), 1)
        self.assertEqual(opener.calls[0][1].get_method(), "GET")
        self.assertEqual(opener.calls[0][1].get_header("Portalid"), "3")
        self.assertEqual(client.stats["discovered_metadata_paths_registered"], 1)

    def test_discovered_metadata_registration_rejects_actions_global_and_unproven_paths(self):
        client, opener, _ = self.client()
        bad_paths = (
            "/asset_computers", "/asset_computers/_execute", "/asset_computers/_metainfo/1",
            "/requests/_metainfo", "/asset_computers/../_metainfo", "/asset_computers/%2e%2e/_metainfo",
            "/asset_computers//_metainfo", "/Asset_computers/_metainfo", "/asset_computers/_metainfo?sql=x",
            "https://evil.example/asset_computers/_metainfo", "/asset_computers/１２/_metainfo",
        )
        for path in bad_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                client.allow_metadata_path(path, portal_id="3")
        for portal in (None, "0", "-1", True, "3\r\nAuthtoken: secret"):
            with self.subTest(portal=portal), self.assertRaises(ValueError):
                client.allow_metadata_path("/asset_computers/_metainfo", portal_id=portal)
        with self.assertRaises(ValueError):
            client.allow_metadata_path("/asset_computers/_metainfo", portal_id="3", provenance="untrusted-href")
        self.assertEqual(opener.calls, [])

    def test_portal_and_diagnostic_context_cannot_contain_credentials_or_injection(self):
        client, opener, _ = self.client()
        for params in ({"PORTALID": "3"}, {"portal_id": "3"}):
            with self.assertRaises(ValueError):
                client.get_json("/requests", params)
        for portal in ("3\r\nAuthtoken: x", "https://host", "3/4", SECRET, True):
            with self.subTest(portal=type(portal).__name__), self.assertRaises(ValueError) as raised:
                client.get_json("/requests", portal_id=portal)
            self.assertNotIn(SECRET, str(raised.exception))
        for context in ({"endpoint_name": SECRET}, {"module": SECRET}, {"module": "person@example.test"}):
            with self.assertRaises(ValueError):
                client.get_json("/requests", **context)
        self.assertEqual(opener.calls, [])


if __name__ == "__main__":
    unittest.main()
