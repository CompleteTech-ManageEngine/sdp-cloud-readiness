"""Conservative, allowlisted GET transport for the ServiceDesk Plus v3 API.

The default 30 requests/minute is a local safety policy, not a claim about a
vendor-wide quota. Every HTTP attempt, including retries, shares one pacing
clock. Credentials are sent in headers only, and redirects are never followed.
"""

from __future__ import annotations

import datetime as _datetime
import email.utils
import http.client
import json
import math
import re
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from . import __version__


_BODY_LIMIT = 16 * 1024 * 1024
_READ_CHUNK = 64 * 1024
_RETRY_LIMIT = 3
_JSON_DEPTH_LIMIT = 128
_PATH = re.compile(r"/(?:[A-Za-z0-9_-]+)(?:/[A-Za-z0-9_-]+)*")
_CONTEXT_SEGMENT = re.compile(r"[A-Za-z0-9._~-]+")
_SUCCESS_CODES = {200, 201, 204, 2000}
_CREDENTIAL_PARAMETERS = {
    "authtoken", "apikey", "api_key", "api-key", "access_token",
    "authorization", "token", "portalid", "portal_id", "_method", "method", "http_method",
}
_USE_DEFAULT_PORTAL = object()
_CONTEXT_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}")
_DYNAMIC_METADATA_PATH = re.compile(r"/(?:asset_[a-z][a-z0-9_]{0,90}|custom_asset_[a-z0-9_]{1,90})/_metainfo", re.ASCII)
_CI_METADATA_PATH = re.compile(r"/cmdb(?:_[a-z0-9_]{1,100})?/_metadata", re.ASCII)
_ERROR_DEFAULTS = {
    "authentication": ("AUTHENTICATION_FAILED", "authentication", False),
    "forbidden": ("PERMISSION_DENIED", "authorization", False),
    "portal_context": ("PORTAL_CONTEXT_REQUIRED", "configuration", False),
    "portal_access": ("PORTAL_NOT_ACCESSIBLE", "portal_access", False),
    "module_disabled": ("MODULE_NOT_ENABLED", "module_availability", False),
    "license": ("MODULE_NOT_AVAILABLE", "licensing_or_module_availability", False),
    "unsupported": ("ENDPOINT_UNSUPPORTED", "api_compatibility_or_resource_availability", False),
    "version": ("API_VERSION_INCOMPATIBLE", "api_compatibility", False),
    "throttled": ("RATE_LIMITED", "rate_limit", True),
    "network": ("NETWORK_ERROR", "network", True),
    "tls": ("NETWORK_ERROR", "tls_configuration", False),
    "server": ("SERVER_ERROR", "server", True),
    "invalid_response": ("PARSE_ERROR", "api_compatibility_or_scanner", False),
}


def _safe_content_type(value: Any) -> str:
    """Classify a header without persisting arbitrary header text."""
    if not isinstance(value, str) or not value:
        return "not_supplied"
    token = value.split(";", 1)[0].strip().lower()
    known = {"application/json", "application/vnd.manageengine.sdp.v3+json",
             "text/html", "text/plain", "application/xml", "text/xml",
             "application/octet-stream"}
    return token if token in known else "other"


def _body_format(body: bytes) -> str:
    prefix = body.lstrip()[:64].lower()
    if not prefix:
        return "empty"
    if prefix.startswith((b"<!doctype html", b"<html", b"<head", b"<body")):
        return "html"
    if prefix.startswith(b"<?xml"):
        return "xml"
    return "non_json_or_malformed_json"


def _network_detail(error: Any) -> str:
    """Return an exception-type classification, never its dynamic message."""
    if isinstance(error, ssl.SSLCertVerificationError):
        return "TLS_CERTIFICATE_VERIFICATION_FAILED"
    if isinstance(error, ssl.SSLError):
        return "TLS_NEGOTIATION_FAILED"
    if isinstance(error, socket.gaierror):
        return "DNS_LOOKUP_FAILED"
    if isinstance(error, (socket.timeout, TimeoutError)):
        return "CONNECTION_TIMED_OUT"
    if isinstance(error, ConnectionRefusedError):
        return "CONNECTION_REFUSED"
    if isinstance(error, ConnectionResetError):
        return "CONNECTION_RESET"
    return "CONNECTION_FAILED"


def _json_integer(value: str) -> int:
    # Bound integer conversion independently of Python's version-specific
    # int-string safety setting. ServiceDesk identifiers need far fewer digits.
    if len(value.lstrip("-")) > 256:
        raise ValueError("JSON integer exceeds the parsing safety limit.")
    return int(value)


def _json_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("JSON numbers must be finite.")
    return result


def _json_constant(value: str) -> Any:
    # NaN/Infinity are accepted by Python's decoder, but are not valid JSON.
    raise ValueError("Nonstandard JSON numeric constant.")


class ApiError(Exception):
    """Structured diagnostic containing only safe, bounded metadata.

    ``kind`` and positional arguments are retained for older collectors.
    ``classification`` is the more precise, stable report outcome. The
    transport never passes arbitrary server text to this exception; the
    optional API message is canonical text recognized in the status envelope.
    """

    def __init__(
        self,
        kind: str,
        message: str,
        http_status: int | None = None,
        api_codes: tuple[int, ...] = (),
        *,
        classification: str | None = None,
        cause: str | None = None,
        retryable: bool | None = None,
        api_message: str | None = None,
        raw_message_omitted: bool = False,
        portal_id: str | None = None,
        endpoint: str | None = None,
        endpoint_name: str | None = None,
        module: str | None = None,
        response_format: str | None = None,
        content_type: str | None = None,
        has_sdp_status: bool = False,
        transport_detail: str | None = None,
        credential_scope: str | None = None,
    ) -> None:
        defaults = _ERROR_DEFAULTS.get(kind, ("UNKNOWN_API_ERROR", "unknown", False))
        self.kind = kind
        self.message = message
        self.http_status = http_status
        self.api_codes = tuple(api_codes)
        self.classification = classification or defaults[0]
        self.cause = cause or defaults[1]
        self.retryable = defaults[2] if retryable is None else bool(retryable)
        self.api_message = api_message
        self.raw_message_omitted = bool(raw_message_omitted)
        self.message_sanitized = True
        self.portal_id = portal_id
        self.endpoint = endpoint
        self.endpoint_name = endpoint_name
        self.module = module
        self.response_format = response_format
        self.content_type = content_type
        self.has_sdp_status = bool(has_sdp_status)
        self.transport_detail = transport_detail
        self.credential_scope = credential_scope
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "kind": self.kind,
            "http_status": self.http_status,
            "api_codes": list(self.api_codes),
            "api_message": self.api_message,
            "message": self.message,
            "message_sanitized": self.message_sanitized,
            "raw_message_omitted": self.raw_message_omitted,
            "portal_id": self.portal_id,
            "endpoint": self.endpoint,
            "endpoint_name": self.endpoint_name,
            "module": self.module,
            "retryable": self.retryable,
            "cause": self.cause,
            "response_format": self.response_format,
            "content_type": self.content_type,
            "has_sdp_status": self.has_sdp_status,
            "transport_detail": self.transport_detail,
            "credential_scope": self.credential_scope,
        }


class BudgetExceeded(Exception):
    """The request or runtime budget does not permit another operation."""

    def __init__(
        self,
        message: str,
        reason: str = "REQUEST_BUDGET_REACHED",
        *,
        requests: int | None = None,
        max_requests: int | None = None,
        elapsed_seconds: float | None = None,
        max_runtime_seconds: float | None = None,
    ) -> None:
        self.reason = reason
        self.classification = reason
        self.message = message
        self.requests = requests
        self.max_requests = max_requests
        self.elapsed_seconds = elapsed_seconds
        self.max_runtime_seconds = max_runtime_seconds
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "message": self.message,
            "requests": self.requests,
            "max_requests": self.max_requests,
            "elapsed_seconds": self.elapsed_seconds,
            "max_runtime_seconds": self.max_runtime_seconds,
        }


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Returning None makes urllib raise HTTPError. The authtoken must never
        # be carried to a Location destination, including the same origin.
        return None


def _positive_number(name: str, value: Any, maximum: float | None = None) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive finite number.")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{name} must be a positive finite number.") from None
    if not math.isfinite(number) or number <= 0 or (maximum and number > maximum):
        suffix = f" no greater than {maximum:g}" if maximum else ""
        raise ValueError(f"{name} must be a positive finite number{suffix}.")
    return number


def _binding_host(base_url: str, allow_http: bool) -> str:
    normalized = _normalize_base_url(base_url, allow_http)
    parts = urllib.parse.urlsplit(normalized)
    if (parts.scheme, parts.port) in {("https", 443), ("http", 80)}:
        host = "[" + parts.hostname + "]" if ":" in parts.hostname else parts.hostname
        return urllib.parse.urlunsplit((parts.scheme, host, parts.path, "", ""))
    return normalized


def _normalize_base_url(base_url: str, allow_http: bool) -> str:
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("Provide a nonempty HTTP(S) base URL.")
    # urlsplit discards some control characters. Reject them before parsing.
    if (
        any(ord(ch) < 33 or ord(ch) > 126 for ch in base_url)
        or any(ch in base_url for ch in ("\\", "%", "?", "#"))
    ):
        raise ValueError("Base URL contains unsafe characters, encoding, or a query/fragment.")
    try:
        parts = urllib.parse.urlsplit(base_url)
        hostname = parts.hostname
        port = parts.port
    except ValueError:
        raise ValueError("Base URL is not a valid HTTP(S) URL.") from None
    if parts.scheme.lower() not in {"https", "http"} or not parts.netloc or not hostname:
        raise ValueError("Provide an absolute HTTP(S) base URL.")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise ValueError("Credentials are not allowed in the base URL.")
    if parts.scheme.lower() == "http" and not allow_http:
        raise ValueError("Plain HTTP requires allow_http=True; HTTPS is recommended.")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Base URL port must be between 1 and 65535.")
    if not re.fullmatch(r"[A-Za-z0-9.:-]+", hostname):
        raise ValueError("Base URL hostname must be an ASCII hostname or IP address.")
    path = parts.path
    if "//" in path:
        raise ValueError("Repeated slashes are not allowed in the base URL path.")
    segments = path.strip("/").split("/") if path.strip("/") else []
    if any(segment in {".", ".."} or not _CONTEXT_SEGMENT.fullmatch(segment) for segment in segments):
        raise ValueError("Unsafe base URL context path.")
    if len(segments) >= 2 and segments[-2:] == ["api", "v3"]:
        segments = segments[:-2]
    if any(segments[index:index + 2] == ["api", "v3"] for index in range(len(segments) - 1)):
        raise ValueError("The base URL may end with /api/v3, but must not contain an API resource path.")
    host = f"[{hostname.lower()}]" if ":" in hostname else hostname.lower()
    if port is not None:
        host += f":{port}"
    context = "/" + "/".join(segments) if segments else ""
    return f"{parts.scheme.lower()}://{host}{context}"


def _status_codes(payload: dict[str, Any]) -> tuple[tuple[int, ...], bool]:
    """Read only the response_status envelope, never fields on API records."""
    envelope = payload.get("response_status")
    if not isinstance(envelope, (dict, list)):
        return (), False
    found: set[int] = set()
    failed = False
    pending: list[Any] = [envelope]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if key in {"status_code", "code"} and not isinstance(value, bool):
                    if isinstance(value, int):
                        found.add(value)
                    elif isinstance(value, str) and re.fullmatch(r"[0-9]{1,12}", value):
                        found.add(int(value))
                elif key in {"status", "type"} and isinstance(value, str):
                    if value.lower() in {"failed", "failure", "error"}:
                        failed = True
                if isinstance(value, (dict, list)):
                    pending.append(value)
        elif isinstance(item, list):
            pending.extend(item)
    return tuple(sorted(found)), failed


def _status_message_evidence(payload: dict[str, Any]) -> tuple[str | None, bool, str | None]:
    """Normalize a few diagnostic phrases; never return arbitrary response text.

    The public on-premises code table does not assign unique codes to every
    portal/module error. Strong, explicit status-envelope wording can refine
    a generic HTTP error, but a bare 403 cannot. Exact phrases below are
    treated as observations, not as a promise that every build uses them.
    Unknown text, record names, addresses and supplied input values are omitted.
    """
    envelope = payload.get("response_status")
    if not isinstance(envelope, (dict, list)):
        return None, False, None
    exact = {
        "invalid api key": ("Invalid API Key", "authentication"),
        "user does not have this permission": ("User does not have this permission", "forbidden"),
        "user does not have permission": ("User does not have permission", "forbidden"),
        "access denied": ("Access denied", "forbidden"),
        "forbidden": ("Forbidden", "forbidden"),
        "internal error": ("Internal Error", "server"),
        "invalid url": ("Invalid URL", "unsupported"),
        "resource not found": ("Resource not found", "unsupported"),
        "api rate limit reached": ("API Rate Limit reached", "throttled"),
        "not allowed as per current license": ("Not allowed as per current license", "license"),
        "invalid input": ("Invalid input", "invalid_query"),
        "invalid query": ("Invalid query", "invalid_query"),
        "unable to parse the given data": ("Unable to parse the given data", "invalid_query"),
        "no such field": ("No such field", "invalid_query"),
        "data type mismatch": ("Data type mismatch", "invalid_query"),
    }
    portal_subject = r"(?:(?:the |specified |requested |selected )*(?:portalid|portal id|portal context|portal)(?: header)?(?: [0-9]{1,128})?)"
    known_module = r"(?:requests?|problems?|changes?|releases?|projects?|assets?|cmdb|purchases?|contracts?|reports?)"
    patterns = (
        (rf"{portal_subject}(?: is| was)? (?:required|missing|mandatory|not provided|not specified)",
         "Portal context is required", "portal_context"),
        (r"(?:missing|required|mandatory) (?:header |parameter )?portalid",
         "Portal context is required", "portal_context"),
        (r"(?:header|parameter) portalid (?:is )?(?:required|missing|mandatory|not provided)",
         "Portal context is required", "portal_context"),
        (rf"{portal_subject}(?: is)? (?:not accessible|not available|unavailable|invalid|not found|does not exist)",
         "The specified portal is not accessible or does not exist", "portal_access"),
        (r"(?:user |you )?(?:does |do )?not (?:have permission|have access|allowed) to (?:access |read )?(?:this |the |specified )?portal",
         "Access to the specified portal is denied", "portal_access"),
        (r"access to (?:the )?(?:this |specified |selected |requested )?portal (?:is )?denied",
         "Access to the specified portal is denied", "portal_access"),
        (r"access (?:is )?denied to (?:the )?(?:this |specified |selected |requested )?portal",
         "Access to the specified portal is denied", "portal_access"),
        (r"invalid (?:portalid|portal id|portal)",
         "The specified portal is not accessible or does not exist", "portal_access"),
        (rf"(?:(?:the )?(?:{known_module} )?module|{known_module})(?: is| has been)? (?:not enabled|disabled)",
         "The requested module is not enabled", "module_disabled"),
        (rf"(?:(?:the )?(?:{known_module} )?module|{known_module})(?: is)? (?:not available|unavailable|not licensed|not supported)(?: (?:under|in) (?:the |this |current )?(?:license|edition))?",
         "The requested module is unavailable under this configuration or license", "license"),
        (r"(?:the |this )?api version(?: is)? (?:unsupported|not supported|incompatible)",
         "The API version is not supported", "version"),
        (r"(?:the |this )?api(?: is)? not supported in (?:this |the current )?(?:build|version)",
         "The API is not supported in this build or version", "version"),
    )
    messages: list[str] = []
    hints: list[str] = []
    omitted = False
    required_portal_field = False
    pending: list[Any] = [envelope]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            code = item.get("status_code", item.get("code"))
            field = item.get("field")
            if str(code) == "4012" and isinstance(field, str) and field.casefold() in {"portalid", "portal_id", "portal.id"}:
                required_portal_field = True
            for key, value in item.items():
                if key == "message" and isinstance(value, str):
                    # Bounded recognition is intentionally not generic regex
                    # PII redaction: unknown free text cannot safely be kept.
                    if len(value) > 512:
                        omitted = True
                        continue
                    normalized = " ".join(value.casefold().split()).rstrip(".! ")
                    found = exact.get(normalized)
                    if found is None:
                        for pattern, safe_message, hint in patterns:
                            if re.fullmatch(pattern, normalized, flags=re.ASCII):
                                found = (safe_message, hint)
                                break
                    if found:
                        if found[0] not in messages:
                            messages.append(found[0])
                        hints.append(found[1])
                        omitted = omitted or normalized not in exact
                    elif normalized not in {"success", "successful", "failed", "failure", "error"}:
                        omitted = True
                elif isinstance(value, (dict, list)):
                    pending.append(value)
        elif isinstance(item, list):
            pending.extend(item)
    if required_portal_field:
        hints.append("portal_context")
        if "Portal context is required" not in messages:
            messages.append("Portal context is required")
    priority = ("authentication", "throttled", "license", "portal_context", "portal_access", "module_disabled", "version", "forbidden", "unsupported", "server", "invalid_query")
    hint = next((kind for kind in priority if kind in hints), None)
    return "; ".join(messages[:6]) or None, omitted or len(messages) > 6, hint


def _classify(
    status: int,
    codes: tuple[int, ...],
    failed: bool,
    hint: str | None = None,
) -> ApiError | None:
    # Specific documented codes outrank a generic HTTP status. Generic 403
    # never supplies evidence for a particular role, a missing portal, or a
    # disabled module. A successful status envelope is not changed by prose.
    error_response = not 200 <= status < 300 or failed or any(code not in _SUCCESS_CODES for code in codes)
    if not error_response:
        return None
    if status == 401 or 4022 in codes or 401 in codes or hint == "authentication":
        return ApiError("authentication", "Authentication failed. Verify the integration key and its account; collection must stop.")
    if status == 429 or 4015 in codes or hint == "throttled":
        return ApiError("throttled", "The server's request limit was reached; retry only after the required delay.")
    if 7001 in codes or hint == "license":
        return ApiError("license", "This operation is unavailable under the source license or module configuration.")
    if hint == "portal_context":
        return ApiError("portal_context", "The API explicitly requires portal context for this operation.")
    if hint == "portal_access":
        return ApiError("portal_access", "The API reports that the specified portal is inaccessible or unavailable to this operation.")
    if hint == "module_disabled":
        return ApiError("module_disabled", "The API explicitly reports that this module is not enabled.")
    if hint == "version":
        return ApiError("version", "The API explicitly reports that this operation is incompatible with the source build or API version.")
    if status == 403 or 4002 in codes or hint == "forbidden":
        return ApiError("forbidden", "The integration key's read operation was denied in this portal and resource scope; no specific required role can be inferred.")
    if status in {404, 405, 410, 501} or 4007 in codes or hint == "unsupported":
        return ApiError("unsupported", "The endpoint or requested object was not found or is unsupported; this alone does not prove that a module is disabled.")
    if 300 <= status < 400:
        return ApiError("network", "The server returned a redirect. Redirects are disabled; use the final base URL.", retryable=False, cause="configuration")
    if status >= 500 or 4004 in codes or hint == "server":
        return ApiError("server", "The server could not complete this read.")
    if status in {400, 406, 415, 422} or any(code in {4001, 4005, 4008, 4009, 4011, 4012, 4014, 4016, 4021} for code in codes) or hint == "invalid_query":
        return ApiError("invalid_response", "The API rejected the read query or its input; API compatibility or scanner query construction requires review.", classification="INVALID_QUERY")
    return ApiError("invalid_response", "The API reported an unsuccessful read that could not be classified safely.", classification="UNKNOWN_API_ERROR", cause="unknown")


class ReadOnlyClient:
    """One paced, single-flight connection path; the only public request is GET.

    ``allowed_patterns`` contains regular expressions matched in their entirety
    against API-relative paths, such as ``/requests`` or ``/requests/[0-9]+``.
    ``progress`` receives small credential-free event dictionaries. For tests,
    inject ``clock``/``sleep`` and replace ``_opener`` with a fake opener.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        allowed_patterns: list[str],
        rpm: float = 30.0,
        timeout: float = 30.0,
        max_requests: int = 500,
        max_runtime: float = 1200.0,
        portal_id: str | None = None,
        ca_file: str | None = None,
        allow_http: bool = False,
        insecure_tls: bool = False,
        progress: Callable[[dict[str, Any]], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        multi_key: bool = False,
    ) -> None:
        self.multi_key = multi_key
        self._portal_keys: dict[str, str] = {}
        self._global_key: str | None = None
        self._global_portal_id: str | None = None
        self._credential_states: dict[str, str] = {}
        if api_key is None and multi_key:
            api_key = ""
        if not isinstance(api_key, str) or (not api_key and not multi_key) or len(api_key) > 8192:
            raise ValueError("Provide a nonempty API key of at most 8192 characters.")
        if any(ord(ch) < 33 or ord(ch) > 126 for ch in api_key):
            raise ValueError("The API key must contain printable ASCII characters without whitespace.")
        self.base_url = _normalize_base_url(base_url, allow_http)
        if api_key and api_key in self.base_url:
            raise ValueError("The API key must not appear in the base URL.")
        self._api_key = api_key
        self._secret_forms = tuple(sorted({
            api_key,
            urllib.parse.quote(api_key, safe=""),
            urllib.parse.quote_plus(api_key, safe=""),
        } - {""}, key=len, reverse=True))
        self.rpm = _positive_number("rpm", rpm, 60)
        self.timeout = _positive_number("timeout", timeout)
        self.max_runtime = _positive_number("max_runtime", max_runtime)
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests < 1:
            raise ValueError("max_requests must be a positive integer.")
        self.max_requests = max_requests
        if not isinstance(allowed_patterns, list) or not allowed_patterns:
            raise ValueError("Provide an explicit nonempty list of allowed API path patterns.")
        try:
            if not all(isinstance(pattern, str) and pattern for pattern in allowed_patterns):
                raise ValueError
            self._allowed = tuple(re.compile(pattern, re.ASCII) for pattern in allowed_patterns)
        except (ValueError, re.error):
            raise ValueError("Allowed API path patterns must be nonempty valid regular expressions.") from None
        portal_id = self._portal_value(portal_id)
        if ca_file and insecure_tls:
            raise ValueError("Choose a trusted CA file or insecure TLS, not both.")
        try:
            tls_context = ssl.create_default_context(cafile=ca_file)
        except (OSError, ssl.SSLError):
            raise ValueError("The TLS CA file could not be loaded.") from None
        if insecure_tls:
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
        self._opener = urllib.request.build_opener(
            _NoRedirectHandler(), urllib.request.HTTPSHandler(context=tls_context)
        )
        self._portal_id = portal_id
        self._clock = clock
        self._sleep = sleep
        self._progress = progress
        self._started = clock()
        self._deadline = self._started + self.max_runtime
        self._next_attempt = self._started
        self._lock = threading.Lock()
        self._dynamic_metadata_paths: set[tuple[str, str]] = set()
        self._requests = 0
        self._successes = 0
        self._authenticated_successes = 0
        self._retries = 0
        self._wait_seconds = 0.0
        self._failures: dict[str, int] = {}
        self._failures_by_classification: dict[str, int] = {}
        self._requests_by_scope: dict[str, int] = {}
        self._active_context: dict[str, Any] = {}
        self._last_response: dict[str, Any] = {}
        self._authentication_failed = False
        self._directory_authentication = "unverified"
        self._directory_credential_used = False
        self._allow_http = bool(allow_http)
        self._insecure_tls = bool(insecure_tls)

    def __repr__(self) -> str:
        return f"ReadOnlyClient(rpm={self.rpm:g}, max_requests={self.max_requests}, credentials=<redacted>)"

    def register_credential(self, key: str) -> None:
        """Register redaction before any request, without granting a scope."""
        if (not isinstance(key, str) or not key or len(key) > 8192
                or any(ord(ch) < 33 or ord(ch) > 126 for ch in key)):
            raise ValueError("Invalid collection credential.")
        if key in self.base_url:
            raise ValueError("A credential must not appear in the source URL.")
        forms = {key, urllib.parse.quote(key, safe=""), urllib.parse.quote_plus(key, safe="")}
        self._secret_forms = tuple(sorted(set(self._secret_forms) | forms, key=len, reverse=True))

    def bind_portal_credential(self, host: str, portal_id: str, key: str) -> None:
        if not self.multi_key or _binding_host(host, self._allow_http) != _binding_host(self.base_url, self._allow_http):
            raise ValueError("Credential binding must match this multi-key source host and application context.")
        self.register_credential(key)
        portal = self._portal_value(portal_id)
        if portal is None or int(portal) <= 0:
            raise ValueError("A portal credential requires an explicit portal ID.")
        portal = str(int(portal))
        if portal in self._portal_keys and self._portal_keys[portal] != key:
            raise ValueError("Conflicting portal credential assignments.")
        self._portal_keys[portal] = key

    def bind_global_credential(self, host: str, portal_id: str, key: str) -> None:
        if not self.multi_key or _binding_host(host, self._allow_http) != _binding_host(self.base_url, self._allow_http):
            raise ValueError("Global credential binding must match this multi-key source host.")
        self.register_credential(key)
        portal = self._portal_value(portal_id)
        if portal is None or int(portal) <= 0:
            raise ValueError("Global collection requires an explicit documented portal context.")
        portal = str(int(portal))
        if self._global_key is not None and (self._global_key != key or self._global_portal_id != portal):
            raise ValueError("Conflicting global credential assignments.")
        self._global_key, self._global_portal_id = key, portal

    @property
    def global_portal_id(self) -> str | None:
        return self._global_portal_id

    def credential_status(self, portal_id: str | None = None, *, global_scope: bool = False) -> str:
        key = self._global_key if global_scope else self._portal_keys.get(portal_id) if portal_id else self._api_key
        return self._credential_states.get(key, "unverified") if key else "missing"

    @property
    def credential_coverage(self) -> dict[str, Any]:
        coverage = {"mode": "per_instance" if self.multi_key else "single_key",
                "directory": self.credential_status(),
                "global": self.credential_status(global_scope=True),
                "portals": {portal: self.credential_status(portal) for portal in self._portal_keys}}
        if self._directory_credential_used:
            coverage["directory_recovery"] = self._directory_authentication
        return coverage

    @property
    def stats(self) -> dict[str, Any]:
        authentication = "failed" if self._authentication_failed else "valid" if self._authenticated_successes else "unverified"
        if self.multi_key:
            states = set(self._credential_states.values())
            authentication = ("mixed" if {"failed", "valid"}.issubset(states) else
                              "failed" if "failed" in states else "valid" if "valid" in states else "unverified")
        return {
            "requests": self._requests,
            "directory_key_authentication": self._directory_authentication,
            "credential_coverage": self.credential_coverage,
            "successful_requests": self._successes,
            "retries": self._retries,
            "failures_by_kind": dict(self._failures),
            "failures_by_classification": dict(self._failures_by_classification),
            "requests_by_scope": dict(self._requests_by_scope),
            "authentication": authentication,
            "elapsed_seconds": round(max(0.0, self._clock() - self._started), 3),
            "wait_seconds": round(self._wait_seconds, 3),
            "requests_per_minute_policy": self.rpm,
            "max_requests": self.max_requests,
            "max_runtime_seconds": self.max_runtime,
            "http_allowed": self._allow_http,
            "tls_verification": not self._insecure_tls,
            "redirects_followed": 0,
            "discovered_metadata_paths_registered": len(self._dynamic_metadata_paths),
        }

    @property
    def last_response(self) -> dict[str, Any]:
        """Safe metadata for the last completed HTTP response, never its body."""
        return dict(self._last_response)

    def _portal_value(self, portal_id: Any) -> str | None:
        if portal_id is None:
            return None
        if isinstance(portal_id, bool) or not isinstance(portal_id, (str, int)):
            raise ValueError("portal_id must be a decimal identifier or None for a global operation.")
        value = str(portal_id)
        if not re.fullmatch(r"[0-9]{1,128}", value, flags=re.ASCII):
            raise ValueError("portal_id must be a decimal identifier or None for a global operation.")
        if any(secret in value for secret in self._secret_forms):
            raise ValueError("The API key must not be used as a portal identifier.")
        return value

    def _context_value(self, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str) or not _CONTEXT_NAME.fullmatch(value):
            raise ValueError("Logical endpoint and module names must be short internal identifiers.")
        if any(secret in value for secret in self._secret_forms):
            raise ValueError("The API key must not appear in diagnostic context.")
        return value

    def allow_metadata_path(self, path: str, *, portal_id: Any, provenance: str = "asset_modules") -> None:
        """Register one discovered asset/CI schema path for one portal.

        The field collector calls this only for ``api_plural_name`` values
        returned by documented ``/asset_modules`` or ``/ci_types`` inventories. It cannot
        admit a record operation, action, arbitrary URL or a global/cross-
        portal path. Only the documented metadata GET family is supported.
        Registration does not make an HTTP request or create rate allowances.
        """
        portal = self._portal_value(portal_id)
        if portal is None or int(portal) <= 0:
            raise ValueError("Discovered metadata paths require an explicit positive portal identifier.")
        pattern = {"asset_modules": _DYNAMIC_METADATA_PATH, "ci_types": _CI_METADATA_PATH}.get(provenance)
        if pattern is None:
            raise ValueError("Discovered metadata paths require documented asset_modules or ci_types provenance.")
        if not isinstance(path, str) or not pattern.fullmatch(path):
            raise ValueError("Only the documented metadata path family matching the discovery provenance may be registered.")
        if any(secret in path for secret in self._secret_forms):
            raise ValueError("The API key must not appear in metadata paths.")
        with self._lock:
            self._dynamic_metadata_paths.add((path, portal))

    def _emit(self, event: str, **extra: Any) -> None:
        if self._progress is not None:
            self._progress({
                "event": event,
                "requests": self._requests,
                "elapsed_seconds": round(max(0.0, self._clock() - self._started), 3),
                **self._active_context,
                **extra,
            })

    def _budget_error(self, reason: str, message: str) -> BudgetExceeded:
        return BudgetExceeded(
            message,
            reason,
            requests=self._requests,
            max_requests=self.max_requests,
            elapsed_seconds=round(max(0.0, self._clock() - self._started), 3),
            max_runtime_seconds=self.max_runtime,
        )

    def _check_budget(self, before_request: bool = True) -> float:
        remaining = self._deadline - self._clock()
        if remaining <= 0:
            raise self._budget_error("TIME_BUDGET_REACHED", "Runtime budget reached; collection stopped.")
        if before_request and self._requests >= self.max_requests:
            raise self._budget_error("REQUEST_BUDGET_REACHED", "Request budget reached; collection stopped.")
        return remaining

    def _wait_until(self, target: float) -> None:
        self._check_budget()
        if target >= self._deadline:
            raise self._budget_error("TIME_BUDGET_REACHED", "Runtime budget would expire before the next permitted request.")
        # Short slices keep interruption and CLI progress responsive. No burst
        # credits accumulate if the caller or network takes longer than a slot.
        while True:
            remaining = target - self._clock()
            if remaining <= 0:
                return
            self._check_budget()
            duration = min(remaining, 1.0)
            self._emit("wait", remaining_seconds=round(remaining, 3))
            before = self._clock()
            self._sleep(duration)
            self._wait_seconds += max(0.0, self._clock() - before)

    def _url(self, path: str, params: dict[str, Any] | None, portal_id: str | None = None) -> str:
        if not isinstance(path, str) or not _PATH.fullmatch(path):
            raise ValueError("Use a safe API-relative path without URLs, encoding, query, or fragment.")
        if any(secret in path for secret in self._secret_forms):
            raise ValueError("The API key must not appear in a request path.")
        if not any(pattern.fullmatch(path) for pattern in self._allowed) and (path, portal_id) not in self._dynamic_metadata_paths:
            raise ValueError("The API path is outside the explicit read-only allowlist.")
        url = self.base_url + "/api/v3" + path
        if params is not None:
            if not isinstance(params, dict):
                raise ValueError("Query parameters must be a dictionary.")
            clean: dict[str, str] = {}
            for key, value in params.items():
                if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", key):
                    raise ValueError("Unsafe query parameter name.")
                if key.casefold() in _CREDENTIAL_PARAMETERS:
                    raise ValueError("Credential and HTTP method parameters are forbidden.")
                if not isinstance(value, (str, int, float, bool)):
                    raise ValueError("Query parameter values must be scalar; serialize input_data as JSON.")
                string = str(value)
                if any(secret in key or secret in string for secret in self._secret_forms):
                    raise ValueError("The API key must be sent in its header, never in query parameters.")
                clean[key] = string
            if clean:
                url += "?" + urllib.parse.urlencode(clean)
        return url

    def _redact_string(self, value: str) -> str:
        # Escaped lone surrogates can pass json.loads but later break UTF-8
        # report generation. Reject them while the response is still bounded
        # by the transport's safe error contract.
        try:
            value.encode("utf-8")
        except UnicodeError:
            raise ApiError("invalid_response", "API returned invalid Unicode text.") from None
        for secret in self._secret_forms:
            value = value.replace(secret, "[REDACTED]")
        return value

    def sanitize_local_text(self, value: str) -> str:
        """Remove active credential spellings before parsing local portal input."""
        return self._redact_string(value)

    def directory_reader(self, api_key: str) -> "DirectoryReader":
        """Restricted view: a separately authorized key can ONLY read /portals.

        The same transport lock, clock, retries and budgets remain in force.
        This never changes the integration key used for module collection.
        """
        if (not isinstance(api_key, str) or not api_key or len(api_key) > 8192
                or any(ord(ch) < 33 or ord(ch) > 126 for ch in api_key)):
            raise ValueError("The directory key must be nonempty printable ASCII without whitespace.")
        forms = {api_key, urllib.parse.quote(api_key, safe=""), urllib.parse.quote_plus(api_key, safe="")}
        if any(value in self.base_url for value in forms):
            raise ValueError("A directory key must not appear in the base URL.")
        with self._lock:
            self._secret_forms = tuple(sorted(set(self._secret_forms) | forms, key=len, reverse=True))
            self._directory_credential_used = True
        return DirectoryReader(self, api_key)

    def _redact_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Servers can echo headers or tokens in fields. Scrub values and keys
        # before a collector can persist them. Iterative traversal also avoids
        # adding recursion failures to otherwise valid large responses.
        pending: list[tuple[Any, int]] = [(payload, 1)]
        while pending:
            current, depth = pending.pop()
            if depth > _JSON_DEPTH_LIMIT:
                raise ApiError("invalid_response", "API response exceeds the 128-level nesting safety limit.")
            if isinstance(current, dict):
                for key in list(current):
                    value = current.pop(key)
                    safe_key = self._redact_string(key)
                    if isinstance(value, str):
                        value = self._redact_string(value)
                    elif isinstance(value, (dict, list)):
                        pending.append((value, depth + 1))
                    elif isinstance(value, (int, float)) and str(value) in self._secret_forms:
                        value = "[REDACTED]"
                    current[safe_key] = value
            elif isinstance(current, list):
                for index, value in enumerate(current):
                    if isinstance(value, str):
                        current[index] = self._redact_string(value)
                    elif isinstance(value, (dict, list)):
                        pending.append((value, depth + 1))
                    elif isinstance(value, (int, float)) and str(value) in self._secret_forms:
                        current[index] = "[REDACTED]"
        return payload

    def _read_body(self, response: Any) -> bytes:
        length = response.headers.get("Content-Length") if response.headers else None
        if length is not None:
            try:
                if int(length) > _BODY_LIMIT:
                    raise ApiError("invalid_response", "API response exceeds the 16 MiB safety limit.")
            except (ValueError, TypeError):
                pass
        chunks: list[bytes] = []
        size = 0
        read = getattr(response, "read1", response.read)
        while True:
            self._check_budget(before_request=False)
            chunk = read(min(_READ_CHUNK, _BODY_LIMIT + 1 - size))
            if not chunk:
                break
            if not isinstance(chunk, bytes):
                raise ApiError("invalid_response", "API returned an invalid response body.")
            chunks.append(chunk)
            size += len(chunk)
            if size > _BODY_LIMIT:
                raise ApiError("invalid_response", "API response exceeds the 16 MiB safety limit.")
        self._check_budget(before_request=False)
        return b"".join(chunks)

    @staticmethod
    def _retry_after(value: Any) -> float:
        if not isinstance(value, str):
            return 0.0
        try:
            seconds = float(value.strip())
            if math.isfinite(seconds):
                return max(0.0, seconds)
        except (ValueError, OverflowError):
            pass
        try:
            parsed = email.utils.parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=_datetime.timezone.utc)
            return max(0.0, parsed.timestamp() - time.time())
        except (ValueError, TypeError, OverflowError):
            return 0.0

    def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        portal_id: Any = _USE_DEFAULT_PORTAL,
        endpoint_name: str | None = None,
        module: str | None = None,
        _directory_key: str | None = None,
    ) -> dict[str, Any]:
        """Read one allowlisted API path through the shared global scheduler.

        A per-call ``portal_id`` selects explicit portal context. ``None``
        omits PORTALID for a documented global endpoint. Omitting the keyword
        retains the constructor's default solely for backward compatibility.
        The caller must select scope from the documented endpoint catalog;
        this transport never discovers or guesses portal IDs by itself.
        """
        effective_portal = self._portal_id if portal_id is _USE_DEFAULT_PORTAL else self._portal_value(portal_id)
        if _directory_key is not None:
            if path != "/portals" or effective_portal is not None or _directory_key not in self._secret_forms:
                raise ValueError("The directory credential is restricted to the global portal-directory GET.")
        url = self._url(path, params, effective_portal)
        context = {
            "portal_id": effective_portal,
            "endpoint": path,
            "endpoint_name": self._context_value(endpoint_name),
            "module": self._context_value(module),
            "credential_scope": ("directory_key" if _directory_key is not None else
                                 "global_key" if self.multi_key and (path == "/orgusers" or path.startswith("/orgusers/")) else
                                 "portal_key" if self.multi_key and effective_portal is not None else "integration_key"),
        }
        credential = _directory_key if _directory_key is not None else self._api_key
        if self.multi_key and _directory_key is None:
            if path == "/portals" and effective_portal is None:
                credential = self._api_key
            elif (path == "/orgusers" or path.startswith("/orgusers/")) and effective_portal == self._global_portal_id:
                credential = self._global_key
            elif path == "/orgusers" or path.startswith("/orgusers/"):
                raise ValueError("Global resource request does not match its explicit context.")
            else:
                credential = self._portal_keys.get(effective_portal)
        if not credential:
            raise ApiError("credential_missing", "No credential is assigned to this operation's scope.",
                           classification="CREDENTIAL_MISSING", cause="credential_configuration", **context)
        with self._lock:
            self._active_context = context
            self._last_response = {}
            if (self._credential_states.get(credential) == "failed" if self.multi_key else self._authentication_failed):
                raise ApiError("authentication", "Authentication previously failed; no further requests are permitted.", **context)
            retries = 0
            while True:
                self._wait_until(self._next_attempt)
                remaining = self._check_budget()
                headers = {
                    "authtoken": credential,
                    "Accept": "application/vnd.manageengine.sdp.v3+json",
                    "Accept-Encoding": "identity",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": f"SDP-Cloud-Readiness/{__version__} (read-only)",
                }
                if effective_portal is not None:
                    headers["portalid"] = effective_portal
                request = urllib.request.Request(url, headers=headers, method="GET")
                attempt_at = self._clock()
                self._next_attempt = attempt_at + 60.0 / self.rpm
                self._requests += 1
                scope = f"portal:{effective_portal}" if effective_portal is not None else "global"
                self._requests_by_scope[scope] = self._requests_by_scope.get(scope, 0) + 1
                if retries:
                    self._retries += 1
                self._emit("request")
                response = None
                status = None
                codes: tuple[int, ...] = ()
                retry_after = 0.0
                transient = False
                response_format = "not_received"
                content_type = None
                has_sdp_status = False
                error: ApiError | None = None
                try:
                    try:
                        response = self._opener.open(request, timeout=min(self.timeout, remaining))
                    except urllib.error.HTTPError as http_error:
                        response = http_error
                    status = response.getcode()
                    if isinstance(status, bool) or not isinstance(status, int) or not 100 <= status <= 599:
                        raise ApiError("invalid_response", "API response has no valid HTTP status.")
                    retry_after = self._retry_after(response.headers.get("Retry-After") if response.headers else None)
                    content_type = _safe_content_type(response.headers.get("Content-Type") if response.headers else None)
                    response_format = "not_inspected"
                    # Redirect bodies/Location are not needed. A 401 body may
                    # safely supply status codes; malformed text never weakens
                    # the HTTP authentication failure below.
                    if 300 <= status < 400:
                        raise _classify(status, (), False)
                    try:
                        body = self._read_body(response)
                        response_format = _body_format(body)
                        payload = json.loads(
                            body,
                            parse_int=_json_integer,
                            parse_float=_json_float,
                            parse_constant=_json_constant,
                        )
                        if not isinstance(payload, dict):
                            response_format = "json_array" if isinstance(payload, list) else "json_scalar"
                            raise ValueError
                        response_format = "json_object"
                    except (ValueError, UnicodeError, RecursionError):
                        known = _classify(status, (), False)
                        if known:
                            error = known
                            error.raw_message_omitted = bool(body)
                            transient = error.retryable
                        else:
                            error = ApiError("invalid_response", "API did not return a JSON object.", http_status=status)
                    else:
                        # Sanitize before status extraction too: a server can
                        # echo a numeric credential inside a status envelope.
                        payload = self._redact_payload(payload)
                        codes, failed = _status_codes(payload)
                        has_sdp_status = isinstance(payload.get("response_status"), (dict, list))
                        api_message, raw_omitted, hint = _status_message_evidence(payload)
                        known = _classify(status, codes, failed, hint)
                        if known:
                            error = known
                            error.api_codes = codes
                            error.api_message = api_message
                            error.raw_message_omitted = raw_omitted
                            transient = error.retryable
                        else:
                            self._successes += 1
                            # An arbitrary HTTP 200 JSON document (e.g. from a
                            # gateway) is not evidence that SDP accepted the key.
                            if 2000 in codes:
                                self._credential_states[credential] = "valid"
                                if _directory_key is None:
                                    self._authenticated_successes += 1
                                else:
                                    self._directory_authentication = "valid"
                            self._last_response = {
                                **context,
                                "classification": "SUCCESS",
                                "http_status": status,
                                "api_codes": list(codes),
                                "response_format": response_format,
                                "content_type": content_type,
                                "has_sdp_status": has_sdp_status,
                            }
                            self._emit("success", http_status=status, api_codes=list(codes))
                            return payload
                except BudgetExceeded:
                    raise
                except ApiError as exc:
                    # A known HTTP denial/authentication/server result still
                    # applies when its response body exceeds parsing limits.
                    error = _classify(status, (), False) if isinstance(status, int) and not 200 <= status < 300 else None
                    if error is None:
                        error = exc
                    else:
                        error.raw_message_omitted = True
                    transient = error.retryable
                except (ssl.SSLError, ssl.CertificateError) as exc:
                    error = ApiError("tls", "TLS verification or negotiation failed; configure a trusted CA certificate.",
                                     transport_detail=_network_detail(exc))
                except urllib.error.URLError as exc:
                    if isinstance(exc.reason, (ssl.SSLError, ssl.CertificateError)):
                        error = ApiError("tls", "TLS verification or negotiation failed; configure a trusted CA certificate.",
                                         transport_detail=_network_detail(exc.reason))
                    else:
                        error = ApiError("network", "The API host could not be reached or the connection failed.",
                                         transport_detail=_network_detail(exc.reason))
                        transient = True
                except http.client.HTTPException as exc:
                    # BadStatusLine can contain arbitrary server text;
                    # IncompleteRead can retain a partial response body. Never
                    # propagate either exception or interpolate its message.
                    error = ApiError("network", "The API connection returned an incomplete or malformed HTTP response.",
                                     transport_detail="HTTP_RESPONSE_INCOMPLETE" if isinstance(exc, http.client.IncompleteRead) else "HTTP_RESPONSE_MALFORMED")
                    transient = True
                except UnicodeError:
                    error = ApiError("invalid_response", "API returned invalid Unicode text.")
                except (OSError, socket.timeout, TimeoutError) as exc:
                    error = ApiError("network", "The API connection failed or timed out.",
                                     transport_detail=_network_detail(exc))
                    transient = True
                finally:
                    if response is not None:
                        try:
                            response.close()
                        except (OSError, ValueError, http.client.HTTPException):
                            # Cleanup errors must not replace a safe diagnostic
                            # with server-controlled exception text.
                            pass
                if error is None:
                    error = ApiError("invalid_response", "API read failed without a usable response.")
                error.http_status = status
                error.response_format = response_format
                error.content_type = content_type
                error.has_sdp_status = has_sdp_status
                if isinstance(status, int) and 300 <= status < 400:
                    error.transport_detail = "REDIRECT_BLOCKED"
                error.portal_id = effective_portal
                error.endpoint = path
                error.endpoint_name = context["endpoint_name"]
                error.module = context["module"]
                error.credential_scope = context["credential_scope"]
                self._failures[error.kind] = self._failures.get(error.kind, 0) + 1
                classification = error.classification
                self._failures_by_classification[classification] = self._failures_by_classification.get(classification, 0) + 1
                self._last_response = error.to_dict()
                self._emit("error", **error.to_dict())
                if error.kind == "authentication":
                    self._credential_states[credential] = "failed"
                    if _directory_key is None and not self.multi_key:
                        self._authentication_failed = True
                    elif _directory_key is not None:
                        self._directory_authentication = "failed"
                if not transient or retries >= _RETRY_LIMIT:
                    raise error from None
                delay = max(2.0 * (2 ** retries), retry_after)
                retries += 1
                self._next_attempt = max(self._next_attempt, self._clock() + delay)
                self._emit("retry", delay_seconds=round(delay, 3), kind=error.kind)
                # The next loop checks both budgets before waiting or sending.


class DirectoryReader:
    """A directory-only credential view, not another network client or scheduler."""

    def __init__(self, shared: ReadOnlyClient, api_key: str) -> None:
        self._shared = shared
        self._key = api_key

    def __repr__(self) -> str:
        return "DirectoryReader(credentials=<redacted>, endpoint=/portals)"

    @property
    def stats(self) -> dict[str, Any]:
        return self._shared.stats

    @property
    def last_response(self) -> dict[str, Any]:
        return self._shared.last_response

    def get_json(self, path: str, params: dict[str, Any] | None = None, *,
                 portal_id: str | None = None, endpoint_name: str | None = None,
                 module: str | None = None) -> dict[str, Any]:
        if path != "/portals" or portal_id is not None or not self._key:
            raise ValueError("The directory credential is restricted to the global portal-directory GET.")
        return self._shared.get_json(path, params, portal_id=None, endpoint_name="portals",
                                     module="topology", _directory_key=self._key)

    def close(self) -> None:
        # Python cannot guarantee memory erasure. Response redaction retains
        # secret spellings in process memory only until the client exits.
        self._key = ""
