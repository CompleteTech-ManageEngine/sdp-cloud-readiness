"""Local, offline reports for an evidence-based ServiceDesk Plus assessment.

Only the summary Assessment contract is accepted. No network calls, template
engines, JavaScript, external stylesheets, or embedded raw API responses are
used. A small defensive redaction layer supplements the analyzer's allowlists;
callers must still avoid putting source record content into free-text summaries.
Each file is replaced atomically; a report set is not a filesystem transaction.
"""

from __future__ import annotations

import csv
import html
import io
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping
from urllib.parse import urlsplit, urlunsplit

from .models import Assessment
from .artifacts import verify_bytes
from .branding import Brand, html_css, html_footer, html_masthead, html_title
from .diagnostics import guidance


_STATUS_INFO = {
    "CONFIRMED_IMPACT": (
        "Confirmed impact",
        "Observed evidence matches a documented limitation or a confirmed local dependency.",
        "impact",
    ),
    "NO_ISSUE_OBSERVED": (
        "No issue observed",
        "No issue was found in the evidence examined. This is not proof of compatibility outside that scope.",
        "observed",
    ),
    "UNKNOWN": (
        "Unknown",
        "The API, permissions, scan budget, missing fields, or available evidence do not establish the answer.",
        "unknown",
    ),
    "MANUAL_CONFIRMATION": (
        "Manual confirmation",
        "An owner or ManageEngine must confirm a requirement, entitlement, migration behavior, or operational decision.",
        "manual",
    ),
}

_SCOPE_NOTES = (
    "A completed list traversal covers only records visible to this API key. "
    "It does not establish organization-wide completeness or access to every module.",
    "The scan is not a transactional snapshot. Source records may be added, changed, "
    "or removed while pagination and detail reads are in progress.",
    "List and detail coverage are separate. Counts and examples apply to the "
    "examined evidence; sampled observations must not be extrapolated into exact totals.",
    "Unknown and manual-confirmation items remain unresolved. This report does "
    "not assign an overall readiness score or approve a production migration.",
    "These artifacts contain assessment metadata, record identifiers, counts, and "
    "documented rules. Raw API records, credentials, ticket subjects, attachment "
    "filenames, and request bodies are excluded by the assessment contract.",
)

_SENSITIVE_KEYS = frozenset(
    {
        "apikey", "authtoken", "token", "accesstoken", "refreshtoken",
        "password", "passwd", "authorization", "cookie", "setcookie",
        "clientsecret", "secret", "credential", "credentials", "headers",
        "raw", "rawresponse", "rawrecords", "records", "requestbody",
        "responsebody", "body", "content", "subject", "description",
        "filename", "filenames", "attachmentfilename", "attachmentname",
        "requesteremail", "technicianemail", "email", "emailaddress",
        "firstname", "lastname", "displayname", "username",
    }
)
_SENSITIVE_KEY_PARTS = (
    "apikey", "authtoken", "password", "clientsecret", "authorization",
    "accesstoken", "refreshtoken",
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_ -]?key|authtoken|access[_ -]?token|refresh[_ -]?token|"
    r"password|authorization)\s*[:=]\s*(?:bearer\s+)?[^\s,;]+"
)
_REDACTED = "[redacted]"


def _credential_free_url(value: str) -> str:
    """Strip credentials and query/fragment payloads from whole HTTP(S) URLs."""
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
            return value
        hostname = parts.hostname
        if not hostname:
            return "[invalid URL]"
        host = f"[{hostname}]" if ":" in hostname else hostname
        port = parts.port
        if port is not None:
            host += f":{port}"
        return urlunsplit((parts.scheme.lower(), host, parts.path, "", ""))
    except ValueError:
        return "[invalid URL]"


def _clean_string(value: str) -> str:
    stripped = value.strip()
    if stripped.lower().startswith(("http://", "https://")) and not any(
        c.isspace() for c in stripped
    ):
        value = _credential_free_url(stripped)
    return _SECRET_ASSIGNMENT.sub(lambda m: f"{m.group(1)}={_REDACTED}", value)


def _sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return normalized in _SENSITIVE_KEYS or any(
        part in normalized for part in _SENSITIVE_KEY_PARTS
    )


def _sanitize(value: Any, depth: int = 0) -> Any:
    """Convert summary metadata into JSON-safe, credential-redacted primitives."""
    if depth > 40:
        return "[omitted: excessive nesting]"
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        return _clean_string(value)
    if isinstance(value, Mapping):
        return {
            str(key): _REDACTED if _sensitive_key(str(key)) else _sanitize(item, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize(item, depth + 1) for item in value]
    return f"[omitted: unsupported {type(value).__name__} value]"


def _sanitize_source_registry(value: Any) -> dict[str, dict[str, str]]:
    """Preserve source IDs as identifiers, rather than treating them as data keys.

    A documentation source can legitimately have an ID such as ``email`` or
    ``token``. Its metadata is schema-limited, so arbitrary records or credentials
    cannot be introduced through this exception to generic key redaction.
    Malformed entries are retained as explicit unavailable references; their raw
    values are never written to the report.
    """
    if not isinstance(value, Mapping):
        return {}
    registry = {}
    for key, source in value.items():
        source_id = str(key)
        if not isinstance(source, Mapping):
            registry[source_id] = {
                "title": source_id,
                "url": "",
                "reviewed_on": "Not supplied",
                "metadata_status": "Invalid source metadata; reference unavailable",
            }
            continue
        entry = {}
        for field in ("title", "url", "reviewed_on"):
            field_value = source.get(field)
            if isinstance(field_value, str):
                entry[field] = _clean_string(field_value)
        registry[source_id] = entry
    return registry


def _sanitize_assessment(assessment: Assessment) -> dict[str, Any]:
    raw = assessment.to_dict()
    sources = raw.pop("sources", {})
    data = _sanitize(raw)
    data["sources"] = _sanitize_source_registry(sources)
    return data


def _display(value: Any) -> str:
    if value is None:
        return "Not established"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(", ", ": "))
    return str(value)


def _h(value: Any) -> str:
    return html.escape(_display(value), quote=True)


def _md(value: Any) -> str:
    text = _display(value)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\\", "\\\\")
    for character in "`*_{}[]|#!":
        text = text.replace(character, "\\" + character)
    return text.replace("\r\n", " ⏎ ").replace("\r", " ⏎ ").replace("\n", " ⏎ ")


def _csv_cell(value: Any) -> str:
    """Neutralize spreadsheet formula prefixes, including hidden whitespace."""
    if value is None:
        return ""
    text = _display(value)
    trimmed = text
    while trimmed and (trimmed[0].isspace() or ord(trimmed[0]) < 32 or trimmed[0] == "\ufeff"):
        trimmed = trimmed[1:]
    if (
        trimmed.startswith(("=", "+", "-", "@"))
        or (text and (ord(text[0]) < 32 or text[0] == "\ufeff"))
    ):
        return "'" + text
    return text


def _safe_source_url(value: Any) -> str | None:
    if not isinstance(value, str) or any(
        c.isspace() or ord(c) < 32 or c in '<>"\'\\' for c in value
    ):
        return None
    try:
        parts = urlsplit(value)
        if (
            parts.scheme.lower() not in {"http", "https"}
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
        ):
            return None
        _ = parts.port
    except ValueError:
        return None
    return value


def _status_counts(data: Mapping[str, Any]) -> dict[str, int]:
    counts = {key: 0 for key in _STATUS_INFO}
    for finding in data.get("findings", []):
        status = str(finding.get("status", "UNKNOWN"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _status_label(status: str) -> str:
    return _STATUS_INFO.get(status, ("Unrecognized status: " + status, "", "unknown"))[0]


def _source_links(ids: list[str], sources: Mapping[str, Any], mode: str) -> str:
    links = []
    for source_id in ids:
        source = sources.get(source_id, {})
        url = _safe_source_url(source.get("url")) if isinstance(source, dict) else None
        if mode == "html":
            if url:
                links.append(
                    f'<a href="{_h(url)}" rel="noopener noreferrer" referrerpolicy="no-referrer">'
                    f"{_h(source_id)}</a>"
                )
            else:
                links.append(_h(source_id) + " (source link unavailable)")
        elif url:
            links.append(f"[{_md(source_id)}](<{url}>)")
        else:
            links.append(_md(source_id) + " (source link unavailable)")
    return ", ".join(links) if links else "No source reference supplied"


def _html_key_values(values: Mapping[str, Any]) -> str:
    if not values:
        return '<p class="muted">No metadata supplied.</p>'
    rows = "".join(
        f"<tr><th scope=\"row\">{_h(key)}</th><td>{_h(value)}</td></tr>"
        for key, value in values.items()
    )
    return '<table class="key-values"><tbody>' + rows + "</tbody></table>"


def _md_key_values(values: Mapping[str, Any]) -> list[str]:
    if not values:
        return ["No metadata supplied.", ""]
    return ["| Field | Value |", "| --- | --- |"] + [
        f"| {_md(key)} | {_md(value)} |" for key, value in values.items()
    ] + [""]


def _finding_counts(finding: Mapping[str, Any]) -> str:
    affected = finding.get("affected_count")
    examined = finding.get("examined_count", 0)
    affected_text = "Not established" if affected is None else str(affected)
    return f"Affected: {affected_text} | Examined: {examined}"


def _html_findings(data: Mapping[str, Any]) -> str:
    sections = []
    sources = data.get("sources", {})
    for index, finding in enumerate(data.get("findings", []), 1):
        status = str(finding.get("status", "UNKNOWN"))
        css = _STATUS_INFO.get(status, ("", "", "unknown"))[2]
        evidence_rows = "".join(
            f'<tr><th scope="row">{number}</th><td>{_html_key_values(evidence)}</td></tr>'
            for number, evidence in enumerate(finding.get("evidence", []), 1)
            if isinstance(evidence, dict)
        )
        evidence = (
            '<div class="table-scroll"><table class="evidence"><caption>Observed evidence</caption>'
            '<thead><tr><th scope="col">Example</th><th scope="col">Identifiers and measured values</th>'
            f"</tr></thead><tbody>{evidence_rows}</tbody></table></div>"
            if evidence_rows else '<p class="muted">No record-level evidence supplied for this finding.</p>'
        )
        finding_anchor = re.sub(r"[^A-Za-z0-9_-]", "-", str(finding.get("id", index)))
        scope = (f'Portal {_display(finding.get("portal_name"))} (ID {_display(finding.get("portal_id"))})'
                 if finding.get("portal_id") is not None else "Environment-wide" if finding.get("scope") == "environment"
                 else "API-visible source scope")
        sections.append(
            f'<article class="finding" id="finding-{finding_anchor}">'
            '<div class="finding-heading">'
            f'<span class="badge {css}">{_h(_status_label(status))}</span>'
            f'<span class="severity">Severity: {_h(finding.get("severity", "Unspecified"))}</span>'
            "</div>"
            f'<h3>{_h(finding.get("id", index))} · {_h(finding.get("title", "Untitled finding"))}</h3>'
            f'<p class="category">{_h(finding.get("category", "Unspecified"))}</p>'
            f'<p class="category">{_h(scope)} · Module: {_h(finding.get("module"))} · '
            f'Evidence basis: {_h(finding.get("evidence_basis", "SOURCE_OBSERVATION"))}</p>'
            f'<p>{_h(finding.get("summary", ""))}</p>'
            f'<p class="counts">{_h(_finding_counts(finding))}</p>'
            f'<p><strong>Coverage:</strong> {_h(finding.get("coverage", "Not established"))}</p>'
            f'{evidence}<p class="action"><strong>Recommended action:</strong> '
            f'{_h(finding.get("action") or "No action supplied; review with the assessment owner.")}</p>'
            f'<p class="sources-inline"><strong>Sources:</strong> '
            f'{_source_links(finding.get("sources", []), sources, "html")}</p></article>'
        )
    return "\n".join(sections) or (
        '<p class="callout">No findings were produced. This is not an acceptance decision.</p>'
    )


def _html_coverage(data: Mapping[str, Any]) -> str:
    coverage = data.get("coverage", [])
    if not coverage:
        return '<p class="callout">No dataset coverage was supplied. Completeness is not established.</p>'
    headers = (
        "Dataset / endpoint", "Collection status", "List records examined", "API-reported total",
        "Pages", "List traversal complete for API scope", "Details examined / attempted", "Notes / sampling",
    )
    rows = []
    for item in coverage:
        notes = []
        if item.get("sampling"):
            notes.append("Sampling: " + _display(item["sampling"]))
        notes.extend(_display(issue) for issue in item.get("issues", []))
        represented = {
            "key", "endpoint", "status", "records_examined", "api_reported_total", "pages",
            "list_complete_for_api_scope", "details_examined", "details_attempted", "sampling", "issues", "source",
        }
        notes.extend(f"{key}: {_display(value)}" for key, value in item.items() if key not in represented)
        values = (
            _display(item.get("key", "Unspecified")) + "\n" + _display(item.get("endpoint", "")),
            item.get("status", "Not established"), item.get("records_examined", 0),
            item.get("api_reported_total"), item.get("pages", 0),
            item.get("list_complete_for_api_scope", False),
            f'{item.get("details_examined", 0)} / {item.get("details_attempted", 0)}',
            "\n".join(notes) or "No additional notes",
        )
        rows.append("<tr>" + "".join(f"<td>{_h(value)}</td>" for value in values) + "</tr>")
    return (
        '<div class="table-scroll"><table class="coverage"><caption>API collection coverage</caption><thead><tr>'
        + "".join(f'<th scope="col">{_h(header)}</th>' for header in headers)
        + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _html_questions(data: Mapping[str, Any]) -> str:
    questions = data.get("questions", [])
    if not questions:
        return '<p class="muted">No structured questions were supplied. Review unknown findings and coverage gaps.</p>'
    sections = []
    for index, question in enumerate(questions, 1):
        question_id = question.get("id", f"Q{index}")
        title = question.get("title", question.get("question", "Confirmation needed"))
        other = {key: value for key, value in question.items() if key not in {"id", "title"}}
        sections.append(
            f'<article class="question"><h3>{_h(question_id)} · {_h(title)}</h3>'
            + _html_key_values(other) + "</article>"
        )
    return "\n".join(sections)


def _html_sources(data: Mapping[str, Any]) -> str:
    entries = []
    for source_id, source in data.get("sources", {}).items():
        if not isinstance(source, Mapping):
            source = {}
        url = _safe_source_url(source.get("url"))
        title = source.get("title", source_id)
        name = (
            f'<a href="{_h(url)}" rel="noopener noreferrer" referrerpolicy="no-referrer">{_h(title)}</a>'
            if url else _h(title) + " (link unavailable)"
        )
        entries.append(
            f'<li><strong>{_h(source_id)}</strong> — {name}. '
            f'Reviewed: {_h(source.get("reviewed_on", "Not supplied"))}.</li>'
        )
    return "<ul>" + "".join(entries) + "</ul>" if entries else "<p>No source registry supplied.</p>"


_STYLE = """
:root { color-scheme: light; --ink:#172c3d; --muted:#526777; --line:#d7e1e8; --paper:#fff; --tint:#f2f6f9; }
* { box-sizing:border-box; }
body { margin:0; background:var(--tint); color:var(--ink); font:15px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
main { max-width:1280px; margin:32px auto; padding:40px; background:var(--paper); border:1px solid var(--line); border-radius:12px; }
header { border-bottom:4px solid #177d8d; padding-bottom:26px; margin-bottom:28px; }
h1 { font-size:34px; line-height:1.15; margin:8px 0 14px; letter-spacing:-.5px; }
h2 { font-size:23px; margin:36px 0 16px; padding-bottom:8px; border-bottom:1px solid var(--line); }
h3 { font-size:18px; line-height:1.35; margin:14px 0 6px; overflow-wrap:anywhere; }
p { margin:9px 0 14px; white-space:pre-wrap; overflow-wrap:anywhere; }
a { color:#075b80; text-decoration:underline; overflow-wrap:anywhere; }
li { margin:8px 0; overflow-wrap:anywhere; }
.eyebrow { text-transform:uppercase; font-size:12px; font-weight:750; letter-spacing:1.2px; color:#176675; }
.subtitle,.muted,.category { color:var(--muted); }
.category { font-size:13px; margin-top:0; }
.status-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:20px 0; }
.status-card { border:1px solid var(--line); border-top:4px solid #55728c; border-radius:8px; padding:16px; }
.status-card .number { display:block; font-size:30px; line-height:1.2; font-weight:750; }
.status-card .label { display:block; font-weight:700; margin-top:8px; }
.status-card p { font-size:12px; line-height:1.5; margin:8px 0 0; }
.status-card.impact { border-top-color:#b03b37; }
.status-card.observed { border-top-color:#3e7c74; }
.status-card.unknown { border-top-color:#ac791a; }
.status-card.manual { border-top-color:#7054a0; }
.callout { border-left:4px solid #ac791a; padding:13px 18px; background:#fff8e8; }
.meta-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:22px; }
.meta-grid>section { min-width:0; }
.finding,.question { border:1px solid var(--line); border-radius:8px; padding:20px; margin:18px 0; }
.finding-heading { display:flex; gap:12px; justify-content:space-between; flex-wrap:wrap; align-items:center; }
.badge { display:inline-block; padding:4px 9px; border-radius:4px; font-size:12px; font-weight:750; }
.badge.impact { color:#8a2926; background:#fcecea; }
.badge.observed { color:#245d54; background:#eaf5f2; }
.badge.unknown { color:#76500c; background:#fff2d6; }
.badge.manual { color:#5f3d92; background:#f1eaf9; }
.severity { color:var(--muted); font-size:13px; font-weight:650; }
.counts { font-weight:700; font-variant-numeric:tabular-nums; }
.action { background:#edf5f8; border-radius:4px; padding:12px; }
.sources-inline { font-size:12px; margin-bottom:0; }
.table-scroll { max-width:100%; overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:13px; margin:12px 0; text-align:left; }
caption { text-align:left; font-weight:700; padding:6px 0; }
th,td { padding:9px 10px; border:1px solid var(--line); vertical-align:top; overflow-wrap:anywhere; white-space:pre-wrap; }
thead th { background:#eaf0f4; font-weight:750; }
.key-values th { width:34%; background:#f5f8fa; }
.key-values td { word-break:break-word; }
.evidence .key-values { margin:0; }
.evidence>tbody>tr>th { width:8%; }
.coverage { min-width:930px; font-size:12px; }
footer { margin-top:34px; border-top:1px solid var(--line); padding-top:15px; color:var(--muted); font-size:12px; }
@media (max-width:850px) { main { margin:0; padding:22px; border-radius:0; } .status-grid,.meta-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width:540px) { .status-grid,.meta-grid { grid-template-columns:1fr; } h1 { font-size:27px; } }
@media print { body { background:white; font-size:10pt; } main { margin:0; padding:0; max-width:none; border:0; } h1 { font-size:25pt; } h2 { break-after:avoid; } h3 { break-after:avoid; } .status-grid { grid-template-columns:repeat(4,minmax(0,1fr)); } .table-scroll { overflow:visible; } .coverage { min-width:0; font-size:8pt; } thead { display:table-header-group; } tr { break-inside:avoid; } .finding-heading { break-after:avoid; } a { color:inherit; } }
"""


def _known(value: Any) -> Any:
    return "—" if value is None else value


def _table_html(headers: tuple[str, ...], rows: list[tuple[Any, ...]]) -> str:
    if not rows:
        return '<p class="muted">No observations supplied for this section; this is not proof of absence.</p>'
    return ('<div class="table-scroll"><table><thead><tr>'
            + "".join(f'<th scope="col">{_h(header)}</th>' for header in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{_h(_known(value))}</td>" for value in row) + "</tr>" for row in rows)
            + "</tbody></table></div>")


def _table_md(headers: tuple[str, ...], rows: list[tuple[Any, ...]]) -> list[str]:
    if not rows:
        return ["No observations supplied; absence is not established.", ""]
    return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
        "| " + " | ".join(_md(_known(value)) for value in row) + " |" for row in rows
    ] + [""]


def _scope_label(item: Mapping[str, Any]) -> str:
    portal_id = item.get("portal_id")
    if portal_id is None:
        return "Environment"
    return f'{item.get("portal_name") or "Portal"} (ID {portal_id})'


def _environment_coverage_rows(data: Mapping[str, Any]) -> list[tuple[Any, ...]]:
    rows = []
    for item in data.get("coverage", []):
        complete = item.get("list_complete", False)
        details = item.get("detail_complete")
        detail_text = (f'{item.get("detail_records_successful", 0)} successful / '
                       f'{item.get("detail_records_attempted", 0)} attempted; '
                       + ("complete for listed scope" if details is True else
                          "incomplete or sampled" if details is False else "completeness unknown"))
        if item.get("sample_complete"):
            detail_text = str(item.get("detail_records_successful", 0)) + " / " + str(item.get("sampled_parents")) + " sampled parents complete; unsampled parents unknown"
        reason = " ".join(str(v) for v in (item.get("reason"), item.get("next_step")) if v)
        rows.append((_scope_label(item), item.get("resource", item.get("key")),
                     item.get("records_observed"), "Complete" if complete else "Incomplete / not established",
                     detail_text, item.get("outcome", item.get("status")),
                     item.get("http_status"), item.get("api_codes"), reason, item.get("confidence")))
    return rows


_COVERAGE_HEADINGS = ("Portal / scope", "Resource", "Records observed", "List coverage", "Detail coverage",
                      "Result", "HTTP", "SDP codes", "Reason", "Confidence")
_FINDING_HEADINGS = ("Portal / scope", "Module", "Finding", "Status", "Affected observations", "Required action")


def _finding_rows(findings: list[Mapping[str, Any]]) -> list[tuple[Any, ...]]:
    return [(_scope_label(item), item.get("module"), item.get("title"),
             _status_label(str(item.get("status", "UNKNOWN"))), item.get("affected_count"), item.get("action"))
            for item in findings]


def _diagnostic_rows(data: Mapping[str, Any]) -> list[tuple[Any, ...]]:
    authentication = data.get("environment", {}).get("permissions", {}).get("authentication")
    return [(_scope_label(item), item.get("module"), item.get("endpoint") or item.get("endpoint_name"),
             item.get("classification"), item.get("http_status"), item.get("api_codes"),
             item.get("api_message") or item.get("message"), item.get("cause"),
             item.get("parse_reason"), item.get("response_shape"), guidance(item, authentication=authentication),
             item.get("raw_message_omitted", False))
            for item in data.get("diagnostics", [])]


_DIAGNOSTIC_HEADINGS = ("Portal / scope", "Module", "Operation", "Classification", "HTTP", "SDP codes",
                        "Sanitized diagnostic", "Likely category", "Contract issue", "Shape (types only)",
                        "Operation-specific next step", "Raw text omitted")
_QUESTION_CATEGORIES = (
    ("confirmed_source_evidence", "Confirmed source evidence"),
    ("api_coverage_limitations", "API coverage limitations"),
    ("target_cloud_unknowns", "Target-cloud unknowns"),
    ("vendor_confirmation_required", "Vendor confirmation required"),
    ("project_decisions_required", "Project/business decision required"),
)


def _question_item(item: Any) -> str:
    if not isinstance(item, Mapping):
        return _display(item)
    pieces = [_scope_label(item)]
    if item.get("module"):
        pieces.append(str(item["module"]))
    prefix = " / ".join(pieces)
    detail = item.get("summary") or item.get("reason") or item.get("outcome") or "Evidence not established."
    result = prefix + ": " + str(detail)
    if item.get("finding_id"):
        result += " [" + str(item["finding_id"]) + "]"
    if "records_observed" in item:
        result += " Records observed: " + str(_known(item["records_observed"])) + "."
    if "list_complete" in item:
        result += " List complete: " + str(bool(item["list_complete"])).lower() + "."
    return result


def _environment_questions_html(data: Mapping[str, Any]) -> str:
    output = []
    for question in data.get("questions", []):
        output.append(f'<article class="question"><h3>{_h(question.get("id"))} · {_h(question.get("title"))}</h3>')
        for key, title in _QUESTION_CATEGORIES:
            output.append(f"<h4>{_h(title)}</h4>")
            items = question.get(key, [])
            if items:
                output.append("<ul>" + "".join("<li>" + _h(_question_item(item)) + "</li>" for item in items) + "</ul>")
            else:
                output.append('<p class="muted">No applicable evidence established in this category. This does not certify absence or target compatibility.</p>')
        output.append("</article>")
    return "\n".join(output)


def _environment_questions_markdown(data: Mapping[str, Any], standalone: bool = False) -> str:
    lines = ["# ServiceDesk Plus migration — portal-aware answers and confirmation questions", "",
             f"Generated: {_md(data.get('generated_at'))}", "",
             "Each answer separates source evidence, API coverage, target unknowns, vendor commitments and project decisions. "
             "Source-only reads cannot prove future migration behavior.", ""] if standalone else []
    for question in data.get("questions", []):
        lines.extend([f"### {_md(question.get('id'))} · {_md(question.get('title'))}", ""])
        for key, title in _QUESTION_CATEGORIES:
            lines.extend([f"#### {title}", ""])
            items = question.get(key, [])
            lines.extend("- " + _md(_question_item(item)) for item in items)
            if not items:
                lines.append("No applicable evidence established; absence or target compatibility is not certified.")
            lines.append("")
    return "\n".join(lines)


def _field_summary_rows(data: Mapping[str, Any]) -> list[tuple[Any, ...]]:
    return [(_scope_label(item), item.get("module"), item.get("additional_fields_observed"),
             item.get("custom_fields_confirmed"),
             f'{item.get("metadata_targets_successful", 0)} / {item.get("metadata_targets_total", 0)}',
             item.get("status"), item.get("completeness"), item.get("registry_complete", False))
            for item in data.get("field_inventory", [])]


_FIELD_SUMMARY_HEADINGS = ("Portal", "Module", "Additional fields observed", "Explicitly custom fields",
                           "Metadata targets successful / known", "Result", "Metadata coverage", "Registry complete")
_IMPACT_SECTIONS = (
    ("configuration", "Configuration/customization impact", {"configuration", "identity", "data quality", "relationships"}),
    ("reporting", "Reporting impact", {"reporting"}),
    ("automation", "Automation/integration impact", {"automation", "integrations"}),
    ("history", "Historical-data exposure", {"historical data", "retention", "attachments"}),
    ("assets", "Assets/CMDB exposure", {"assets", "scope", "operations"}),
)


def _environment_section_data(data: Mapping[str, Any]) -> dict[str, Any]:
    env = data.get("environment", {})
    topology = env.get("topology", {})
    discovered = [
        (item.get("name"), item.get("id"), item.get("instance_type"), item.get("state"),
         item.get("active"), item.get("edition"), item.get("selected"), item.get("accessible"),
         item.get("scan_status"), item.get("discovery_endpoint"))
        for item in topology.get("portals", [])
    ]
    assessed = [
        (item.get("portal_name"), item.get("portal_id"), item.get("metadata", {}).get("scan_status"),
         item.get("summary", {}).get("collections_complete"), item.get("summary", {}).get("collections_with_gaps"),
         item.get("summary", {}).get("findings_by_status"))
        for item in data.get("portals", [])
    ]
    capabilities = [
        (_scope_label(item), item.get("module"), item.get("availability") or item.get("status"),
         operation.get("resource"), operation.get("endpoint"), operation.get("status"),
         item.get("discovery_method"))
        for portal in data.get("portals", []) for item in portal.get("capabilities", [])
        for operation in item.get("operations", []) or [{}]
    ]
    volumes = [
        (item.get("scope"), item.get("resource"), item.get("records_observed"),
         item.get("collections_complete"), item.get("collections"), item.get("collections_unknown"),
         item.get("count_semantics"))
        for item in env.get("volume_by_module", [])
    ]
    risks = [
        (item.get("title"), item.get("portals_with_confirmed_impact"), item.get("affected_observations"),
         item.get("portals_with_unknown_evidence"), item.get("portals_requiring_confirmation"))
        for item in env.get("risk_rollup", [])
    ]
    blockers = [
        (_scope_label(item), item.get("module"), item.get("finding_id"), item.get("blocker_type"),
         item.get("reason"), item.get("required_resolution"))
        for item in env.get("acceptance_blockers", [])
    ]
    return {"env": env, "topology": topology, "discovered": discovered, "assessed": assessed,
            "capabilities": capabilities,
            "volumes": volumes, "risks": risks, "blockers": blockers}


_TOPOLOGY_HEADINGS = ("Portal", "ID", "Instance type", "State", "Active", "Source edition",
                       "Selected", "Accessible", "Scan status", "Discovery endpoint")
_ASSESSED_HEADINGS = ("Portal", "ID", "Scan status", "Complete lists", "Lists with gaps", "Finding statuses")
_CAPABILITY_HEADINGS = ("Portal", "Module", "Availability evidence", "Collector", "Endpoint",
                         "Operation result", "Discovery method")
_VOLUME_HEADINGS = ("Scope", "Resource", "Records observed", "Complete lists", "Selected collections",
                     "Collections with unknown count", "Population semantics")
_RISK_HEADINGS = ("Rule", "Portals with confirmed impact", "Affected observations",
                   "Portals with unknown evidence", "Portals needing confirmation")
_BLOCKER_HEADINGS = ("Portal / scope", "Module", "Reference", "Acceptance item", "Reason", "Required resolution")


def _render_environment_html(data: Mapping[str, Any]) -> str:
    sections = _environment_section_data(data)
    env, topology = sections["env"], sections["topology"]
    body = [
        '<header><p class="eyebrow">Read-only environment assessment</p>',
        "<h1>ServiceDesk Plus<br>Cloud migration readiness</h1>",
        '<p class="subtitle">Portal topology, source impact, field metadata, permissions and evidence coverage.</p>',
        f'<p>Generated: {_h(data.get("generated_at"))} · Assessment schema: {_h(data.get("schema_version"))}</p></header>',
        "<section><h2>Executive summary</h2>",
        '<p>Discovery and collection cover only the integration key’s accessible scope. A dash means the count was not established. '
        'Finding counts are separate from record counts; source-only evidence cannot approve a future migration.</p>',
        _html_key_values(env.get("summary", {})),
        "<h3>Environment scan stop status</h3>", _html_key_values(env.get("stop", {})), "</section>",
        "<section><h2>Environment topology</h2>",
        _html_key_values({key: value for key, value in topology.items() if key not in {"portals", "diagnostics"}}),
        "<h3>Source and scan configuration</h3>",
        '<div class="meta-grid"><section>' + _html_key_values(data.get("source", {}))
        + "</section><section>" + _html_key_values(data.get("settings", {})) + "</section></div>",
        "<h3>Global request usage</h3>", _html_key_values(data.get("stats", {})), "</section>",
        "<section><h2>Portals discovered</h2>", _table_html(_TOPOLOGY_HEADINGS, sections["discovered"]), "</section>",
        "<section><h2>Portals assessed</h2>", _table_html(_ASSESSED_HEADINGS, sections["assessed"]),
        "<h3>Module availability and discovery evidence</h3>",
        "<p>Documented first-page reads establish observed operation availability. A denied or unsupported operation alone "
        "does not establish whether the module is licensed or enabled.</p>",
        _table_html(_CAPABILITY_HEADINGS, sections["capabilities"]), "</section>",
        "<section><h2>Portal access gaps and permissions diagnostics</h2>",
        _table_html(["Credential scope", "Authentication status"],
                    [[row["scope"], row["status"]] for row in env.get("permissions", {}).get("credential_scopes", [])]),
        _html_key_values({key: value for key, value in env.get("permissions", {}).items()
                          if key not in {"denied_operations", "unsupported_operations", "credential_scopes"}}),
        "<p>Generic HTTP 403 identifies a denied operation. It does not establish a required role. "
        "Unsupported endpoints, unavailable modules and missing portal context remain distinct. Earlier failed fallback attempts "
        "remain in the diagnostic history even when the final collection succeeds.</p>",
        _table_html(_DIAGNOSTIC_HEADINGS, _diagnostic_rows(data)), "</section>",
        "<section><h2>Per-portal migration risks</h2>",
    ]
    for portal in data.get("portals", []):
        body.extend([
            f'<h3>{_h(_scope_label(portal))}</h3>',
            _table_html(_FINDING_HEADINGS, _finding_rows(portal.get("findings", []))),
            "<details><summary>Detailed findings, measured evidence and documentation</summary>",
            _html_findings({"findings": portal.get("findings", []), "sources": data.get("sources", {})}),
            "</details>",
        ])
    body.extend([
        "</section><section><h2>Environment-wide aggregated risks</h2>",
        "<p>Each row aggregates the same rule across portals. Overlapping findings, Assets, Computers, CIs "
        "and identity memberships must not be added as unique objects.</p>",
        _table_html(_RISK_HEADINGS, sections["risks"]),
        "<h3>Environment-wide target and operational decisions</h3>",
        _html_findings({"findings": [item for item in data.get("findings", []) if item.get("scope") == "environment"],
                        "sources": data.get("sources", {})}),
        "</section><section><h2>Data-volume summary</h2>",
        _table_html(_VOLUME_HEADINGS, sections["volumes"]), "</section>",
    ])
    for _, title, categories in _IMPACT_SECTIONS[:1]:
        body.extend([f"<section><h2>{title}</h2>", _table_html(_FINDING_HEADINGS,
                     _finding_rows([item for item in data.get("findings", []) if item.get("category") in categories])), "</section>"])
    body.extend([
        "<section><h2>Field/UDF impact</h2>",
        "<p>Additional fields, explicitly custom fields and built-in fields are distinct. Form metadata can reveal a lower bound "
        "without proving a complete registry. Case-folded UDF labels are mapping candidates unless the documented Incident/Service "
        "duplicate condition is established. Larger declared lengths do not prove oversized stored values.</p>",
        _table_html(_FIELD_SUMMARY_HEADINGS, _field_summary_rows(data)),
        _table_html(_FINDING_HEADINGS, _finding_rows([item for item in data.get("findings", []) if item.get("category") == "fields"])),
    ])
    for inventory in data.get("field_inventory", []):
        body.append(f'<details><summary>{_h(_scope_label(inventory))} / {_h(inventory.get("module"))}: observed field schema</summary>')
        body.append(_html_key_values({key: inventory.get(key) for key in ("completeness", "evidence_basis", "sources", "limitations")}))
        body.append(_table_html(
            ("Internal path", "Field ID", "Display label", "Type / control", "Maximum length",
             "Option count", "Mandatory", "Read-only", "Additional / custom", "Metadata source", "Completeness"),
            [(field.get("field_path"), field.get("field_id"), field.get("display_label"),
              str(field.get("data_type")) + " / " + str(field.get("display_type")), field.get("maximum_length"),
              field.get("allowed_value_count"), field.get("mandatory"), field.get("read_only"),
              str(field.get("is_additional")) + " / " + str(field.get("custom")), field.get("metadata_source"),
              field.get("completeness"))
             for field in inventory.get("fields", [])]))
        body.append("</details>")
    body.append("</section>")
    for _, title, categories in _IMPACT_SECTIONS[1:]:
        body.extend([f"<section><h2>{title}</h2>", _table_html(_FINDING_HEADINGS,
                     _finding_rows([item for item in data.get("findings", []) if item.get("category") in categories])), "</section>"])
    body.extend([
        "<section><h2>Coverage and confidence</h2>",
        "<p>Completed lists remain completed if a later global budget stops the scan. Unstarted, denied, unsupported or unavailable "
        "collections have unknown counts. Details and nested subresources have separate coverage. A successful empty list alone proves "
        "zero records within that response’s account/portal/filter scope.</p>",
        _table_html(_COVERAGE_HEADINGS, _environment_coverage_rows(data)),
        "<h3>Interpretation notes</h3><ul>",
        "".join("<li>" + _h(note) + "</li>" for note in list(_SCOPE_NOTES) + list(data.get("notes", []))),
        "</ul></section><section><h2>Vendor/project questions</h2>",
        _environment_questions_html(data), "</section><section><h2>Acceptance blockers</h2>",
        "<p>These are unresolved source exceptions, evidence gaps and required agreements. The project must resolve or explicitly accept "
        "each applicable item and validate target behavior. This source assessment does not issue a go-live approval.</p>",
        _table_html(_BLOCKER_HEADINGS, sections["blockers"]), "</section>",
        "<section><h2>Documentation sources</h2>", _html_sources(data), "</section>",
        "<footer>Standalone offline report. No external scripts, styles, images or analytics are loaded. "
        "Documentation links open only when selected. Full structured evidence is also available in the JSON and CSV files.</footer>",
    ])
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="referrer" content="no-referrer">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'none\'; '
            'style-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
            '<title>ServiceDesk Plus environment migration readiness</title>'
            f"<style>{_STYLE}\ndetails{{margin:16px 0;padding:12px;border:1px solid var(--line);border-radius:6px;}}"
            "summary{cursor:pointer;font-weight:650;}h4{font-size:15px;margin:20px 0 8px;}</style>"
            "</head><body><main>" + "\n".join(body) + "</main></body></html>\n")


def _render_environment_markdown(data: Mapping[str, Any]) -> str:
    sections = _environment_section_data(data)
    env, topology = sections["env"], sections["topology"]
    lines = ["# ServiceDesk Plus Cloud migration readiness", "",
             "Read-only environment assessment across the discovered and selected portal scope.", "",
             f"Generated: {_md(data.get('generated_at'))} · Schema {_md(data.get('schema_version'))}", "",
             "## Executive summary", "",
             "A dash means a count is unknown. Source reads cannot approve a future Cloud migration.", ""]
    lines.extend(_md_key_values(env.get("summary", {})))
    lines.extend(["### Environment scan stop status", ""] + _md_key_values(env.get("stop", {})))
    lines.extend(["## Environment topology", ""] + _md_key_values(
        {key: value for key, value in topology.items() if key not in {"portals", "diagnostics"}}))
    lines.extend(["### Source", ""] + _md_key_values(data.get("source", {})))
    lines.extend(["### Global budgets and usage", ""] + _md_key_values(data.get("settings", {}))
                 + _md_key_values(data.get("stats", {})))
    lines.extend(["## Portals discovered", ""] + _table_md(_TOPOLOGY_HEADINGS, sections["discovered"]))
    lines.extend(["## Portals assessed", ""] + _table_md(_ASSESSED_HEADINGS, sections["assessed"]))
    lines.extend(["### Module availability and discovery evidence", "",
                  "Documented first-page reads establish operation availability. A denied or unsupported operation alone does not establish licensing or enablement.", ""]
                 + _table_md(_CAPABILITY_HEADINGS, sections["capabilities"]))
    lines.extend(["## Portal access gaps and permissions diagnostics", "",
                  "A generic 403 does not establish a required role. Historical fallback failures remain available even when the final read succeeds.", ""]
                 + _md_key_values({key: value for key, value in env.get("permissions", {}).items()
                                   if key not in {"denied_operations", "unsupported_operations", "credential_scopes"}})
                 + _table_md(["Credential scope", "Authentication status"],
                             [[row["scope"], row["status"]] for row in env.get("permissions", {}).get("credential_scopes", [])])
                 + _table_md(_DIAGNOSTIC_HEADINGS, _diagnostic_rows(data)))
    lines.extend(["## Per-portal migration risks", ""])
    for portal in data.get("portals", []):
        lines.extend([f"### {_md(_scope_label(portal))}", ""]
                     + _table_md(_FINDING_HEADINGS, _finding_rows(portal.get("findings", []))))
    lines.extend(["## Environment-wide aggregated risks", "",
                  "Rule observations may overlap. Global objects are counted once; user memberships and asset resource types are separate populations.", ""]
                 + _table_md(_RISK_HEADINGS, sections["risks"]))
    lines.extend(["## Data-volume summary", ""] + _table_md(_VOLUME_HEADINGS, sections["volumes"]))
    for _, title, categories in _IMPACT_SECTIONS[:1]:
        lines.extend([f"## {title}", ""] + _table_md(_FINDING_HEADINGS, _finding_rows(
            [item for item in data.get("findings", []) if item.get("category") in categories])))
    lines.extend(["## Field/UDF impact", "",
                  "Field observations are scoped by portal and module. Form coverage is separate from complete registry coverage. "
                  "Declared lengths and case-folded labels alone do not prove failed record migration.", ""]
                 + _table_md(_FIELD_SUMMARY_HEADINGS, _field_summary_rows(data)))
    for inventory in data.get("field_inventory", []):
        lines.extend([f"### {_md(_scope_label(inventory))} / {_md(inventory.get('module'))}", ""])
        lines.extend(_md_key_values({key: inventory.get(key) for key in ("status", "completeness", "sources", "limitations")}))
        lines.extend(_table_md(
            ("Internal path", "Field ID", "Label", "Type", "Maximum length", "Options", "Mandatory", "Read-only", "Metadata source"),
            [(item.get("field_path"), item.get("field_id"), item.get("display_label"),
              item.get("display_type") or item.get("data_type"), item.get("maximum_length"),
              item.get("allowed_value_count"), item.get("mandatory"), item.get("read_only"), item.get("metadata_source"))
             for item in inventory.get("fields", [])]))
    for _, title, categories in _IMPACT_SECTIONS[1:]:
        lines.extend([f"## {title}", ""] + _table_md(_FINDING_HEADINGS, _finding_rows(
            [item for item in data.get("findings", []) if item.get("category") in categories])))
    lines.extend(["## Coverage and confidence", "",
                  "List completion survives later global budget exhaustion. Detail/subresource coverage remains separate. "
                  "Failed or unstarted reads do not establish zero records.", ""]
                 + _table_md(_COVERAGE_HEADINGS, _environment_coverage_rows(data)))
    lines.extend("- " + _md(note) for note in list(_SCOPE_NOTES) + list(data.get("notes", [])))
    lines.extend(["", "## Vendor/project questions", "", _environment_questions_markdown(data), "",
                  "## Acceptance blockers", "",
                  "Resolve or explicitly accept applicable source exceptions and evidence gaps, then validate the target. This is not a go-live approval.", ""]
                 + _table_md(_BLOCKER_HEADINGS, sections["blockers"]))
    lines.extend(["## Detailed findings and measured evidence", ""])
    for finding in data.get("findings", []):
        lines.extend([f"### {_md(finding.get('id'))} · {_md(finding.get('title'))}", "",
                      f"**Scope:** {_md(_scope_label(finding))} / {_md(finding.get('module'))}  ",
                      f"**Status:** {_md(finding.get('status'))}  ",
                      f"**Evidence basis:** {_md(finding.get('evidence_basis'))}", "",
                      _md(finding.get("summary")), "", _md(_finding_counts(finding)), "",
                      "**Coverage:** " + _md(finding.get("coverage")), ""])
        for evidence in finding.get("evidence", []):
            lines.extend(_md_key_values(evidence))
        lines.extend(["**Action:** " + _md(finding.get("action")), "",
                      "**Sources:** " + _source_links(finding.get("sources", []), data.get("sources", {}), "md"), ""])
    lines.extend(["## Documentation sources", ""])
    for source_id, source in data.get("sources", {}).items():
        lines.append("- " + _source_links([source_id], data.get("sources", {}), "md")
                     + " · " + _md(source.get("title")) + " · Reviewed " + _md(source.get("reviewed_on")))
    return "\n".join(lines).rstrip() + "\n"


def _render_html(data: Mapping[str, Any]) -> str:
    if data.get("environment"):
        return _render_environment_html(data)
    counts = _status_counts(data)
    cards = []
    for status, (label, explanation, css) in _STATUS_INFO.items():
        cards.append(
            f'<section class="status-card {css}" data-status="{status}">'
            f'<span class="number">{counts[status]}</span><span class="label">{label}</span>'
            f"<p>{explanation}</p></section>"
        )
    others = {key: value for key, value in counts.items() if key not in _STATUS_INFO}
    additional = (
        '<p class="callout">Unrecognized finding statuses are unresolved: ' + _h(others) + "</p>"
        if others else ""
    )
    notes = list(_SCOPE_NOTES) + list(data.get("notes", []))
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        'script-src \'none\'; style-src \'unsafe-inline\'; img-src \'none\'; '
        'connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
        '<title>ServiceDesk Plus Cloud migration readiness</title>'
        f"<style>{_STYLE}</style></head><body><main>"
        '<header><p class="eyebrow">Read-only source assessment</p>'
        '<h1>ServiceDesk Plus<br>Cloud migration readiness</h1>'
        '<p class="subtitle">Observed source impact, collection coverage, and questions to resolve.</p>'
        f'<p>Generated: {_h(data.get("generated_at"))} · Assessment schema: {_h(data.get("schema_version"))}</p>'
        '</header><section aria-labelledby="outcomes"><h2 id="outcomes">Assessment outcomes</h2>'
        '<p>Counts below are findings, not affected records. Review each finding’s severity, evidence, '
        'and coverage before making a migration decision.</p>'
        '<div class="status-grid">' + "".join(cards) + "</div>" + additional + "</section>"
        '<section><h2>Scope and interpretation</h2><ul>'
        + "".join(f"<li>{_h(note)}</li>" for note in notes) + "</ul></section>"
        '<div class="meta-grid"><section><h2>Source metadata</h2>'
        + _html_key_values(data.get("source", {}))
        + '</section><section><h2>Configured budgets and scan settings</h2>'
        + _html_key_values(data.get("settings", {})) + "</section></div>"
        '<section><h2>Actual API usage and scan statistics</h2>'
        + _html_key_values(data.get("stats", {})) + "</section>"
        '<section><h2>Pagination and detail coverage</h2>'
        '<p>“Complete” refers to list traversal within the API key’s visible scope. '
        'An API-reported total is a reported value, not an independently verified inventory.</p>'
        + _html_coverage(data) + "</section>"
        '<section><h2>Findings and recommended actions</h2>' + _html_findings(data) + "</section>"
        '<section><h2>Answers and questions requiring confirmation</h2>'
        '<p>Observed answers summarize available evidence. Confirmation requirements identify the '
        'remaining decisions for the service owner, integration owners, or ManageEngine.</p>'
        + _html_questions(data) + "</section>"
        '<section><h2>Documentation sources</h2>' + _html_sources(data) + "</section>"
        '<footer>This is a standalone offline report. It loads no external scripts, styles, images, '
        'or analytics. Documentation links open only when you choose to follow them.</footer>'
        "</main></body></html>\n"
    )


def _question_markdown(data: Mapping[str, Any], standalone: bool = False) -> str:
    if data.get("environment"):
        return _environment_questions_markdown(data, standalone)
    lines = []
    if standalone:
        lines.extend([
            "# ServiceDesk Plus migration — answers and confirmation questions", "",
            f"Generated: {_md(data.get('generated_at'))}", "",
            "Observed answers summarize the read-only scan. Items requiring confirmation remain open "
            "until the responsible owner or ManageEngine supplies evidence. A local answer is not "
            "proof of a vendor entitlement or a supported migration behavior.", "",
        ])
    for index, question in enumerate(data.get("questions", []), 1):
        question_id = question.get("id", f"Q{index}")
        title = question.get("title", question.get("question", "Confirmation needed"))
        lines.extend([f"### {_md(question_id)} · {_md(title)}", ""])
        lines.extend(_md_key_values({key: value for key, value in question.items() if key not in {"id", "title"}}))
    if not data.get("questions"):
        lines.extend(["No structured questions were supplied. Review unknown findings and coverage gaps.", ""])
    return "\n".join(lines)


def _render_markdown(data: Mapping[str, Any]) -> str:
    if data.get("environment"):
        return _render_environment_markdown(data)
    lines = [
        "# ServiceDesk Plus Cloud migration readiness", "",
        "Read-only source assessment: observed impact, collection coverage, and questions to resolve.", "",
        f"Generated: {_md(data.get('generated_at'))}  ",
        f"Assessment schema: {_md(data.get('schema_version'))}", "",
        "## Assessment outcomes", "",
        "Counts are findings, not affected records. There is no overall readiness score.", "",
        "| Status | Findings | Meaning |", "| --- | ---: | --- |",
    ]
    for status, count in _status_counts(data).items():
        description = _STATUS_INFO.get(status, ("", "Unrecognized status; treat as unresolved.", ""))[1]
        lines.append(f"| {_md(_status_label(status))} | {count} | {_md(description)} |")
    lines.extend(["", "## Scope and interpretation", ""])
    lines.extend("- " + _md(note) for note in list(_SCOPE_NOTES) + list(data.get("notes", [])))
    lines.extend(["", "## Source metadata", ""])
    lines.extend(_md_key_values(data.get("source", {})))
    lines.extend(["## Configured budgets and scan settings", ""])
    lines.extend(_md_key_values(data.get("settings", {})))
    lines.extend(["## Actual API usage and scan statistics", ""])
    lines.extend(_md_key_values(data.get("stats", {})))
    lines.extend(["## Pagination and detail coverage", ""])
    if not data.get("coverage"):
        lines.extend(["No dataset coverage was supplied. Completeness is not established.", ""])
    for item in data.get("coverage", []):
        lines.extend([f"### {_md(item.get('key', 'Unspecified dataset'))}", ""])
        lines.extend(_md_key_values(item))
    lines.extend(["## Findings and recommended actions", ""])
    if not data.get("findings"):
        lines.extend(["No findings were produced. This is not an acceptance decision.", ""])
    for finding in data.get("findings", []):
        lines.extend([
            f"### {_md(finding.get('id'))} · {_md(finding.get('title'))}", "",
            f"**Status:** {_md(_status_label(str(finding.get('status', 'UNKNOWN'))))}  ",
            f"**Severity:** {_md(finding.get('severity'))}  ",
            f"**Category:** {_md(finding.get('category'))}", "",
            _md(finding.get("summary", "")), "",
            f"**{_md(_finding_counts(finding))}**", "",
            f"**Coverage:** {_md(finding.get('coverage'))}", "",
        ])
        if finding.get("evidence"):
            lines.extend(["**Observed evidence**", ""])
            for number, item in enumerate(finding["evidence"], 1):
                lines.extend([f"Evidence {number}:", ""])
                lines.extend(_md_key_values(item))
        else:
            lines.extend(["No record-level evidence supplied for this finding.", ""])
        lines.extend([
            f"**Recommended action:** {_md(finding.get('action') or 'No action supplied; review with the assessment owner.')}", "",
            "**Sources:** " + _source_links(finding.get("sources", []), data.get("sources", {}), "markdown"), "",
        ])
    lines.extend(["## Answers and questions requiring confirmation", "", _question_markdown(data), ""])
    lines.extend(["## Documentation sources", ""])
    for source_id, source in data.get("sources", {}).items():
        if not isinstance(source, Mapping):
            source = {}
        url = _safe_source_url(source.get("url"))
        title = _md(source.get("title", source_id))
        link = f"[{title}](<{url}>)" if url else title + " (link unavailable)"
        lines.append(f"- **{_md(source_id)}** — {link}. Reviewed: {_md(source.get('reviewed_on', 'Not supplied'))}.")
    if not data.get("sources"):
        lines.append("No source registry supplied.")
    return "\n".join(lines).rstrip() + "\n"


def _csv_document(headers: list[str], rows: list[Mapping[str, Any]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow([_csv_cell(header) for header in headers])
    for row in rows:
        writer.writerow([_csv_cell(row.get(header)) for header in headers])
    return buffer.getvalue()


def _atomic_write(destination: Path, contents: str) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
        verify_bytes(destination, contents.encode("utf-8"))
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


_CSP_NO_IMAGES = "img-src 'none'"
_DOC_TYPE = "Cloud Readiness Assessment"


def _brand_reference(brand: Brand) -> str:
    return "ServiceDesk Plus · " + brand.prepared_for if brand.prepared_for else "ServiceDesk Plus"


def _apply_brand(document: str, brand: Brand, title: str, doc_type: str, gutter: int = 40) -> str:
    """Add an operator brand to a finished offline report without changing its content.

    The CSP is widened only to data: images so the embedded logo can render;
    scripts, connections and external styles remain blocked.
    """
    if _CSP_NO_IMAGES not in document or "<body><main>" not in document or "</footer>" not in document:
        raise ValueError("Report layout is not recognized for branding.")
    document = document.replace(_CSP_NO_IMAGES, "img-src data:" if brand.logo else _CSP_NO_IMAGES, 1)
    document = re.sub(r"<title>.*?</title>", lambda _: "<title>" + _h(html_title(brand, title)) + "</title>", document, count=1)
    head, _, tail = document.partition("</style>")
    document = head + html_css(brand, gutter) + "</style>" + tail
    document = document.replace("<body><main>", "<body><main>" + html_masthead(brand, doc_type, _brand_reference(brand)), 1)
    if brand.logo:
        document = document.replace("No external scripts, styles, images or analytics are loaded.",
                                    "No external scripts, styles, images or analytics are loaded (the logo is embedded).", 1)
        document = document.replace("It loads no external scripts, styles, images, or analytics.",
                                    "It loads no external scripts, styles, images, or analytics (the logo is embedded).", 1)
    head, _, tail = document.rpartition("</footer>")
    return head + html_footer(brand) + "</footer>" + tail


def render_branded_report_html(data: Mapping[str, Any], brand: Brand) -> str:
    """Branded copy of report.html from sanitized assessment data (assessment.json)."""
    return _apply_brand(_render_html(data), brand, "SDP Cloud Readiness", _DOC_TYPE)


def render_branded_questions_html(data: Mapping[str, Any], brand: Brand) -> str:
    """Branded vendor-questions document with the same content as vendor-questions.md."""
    if data.get("environment"):
        title = "ServiceDesk Plus migration — portal-aware answers and confirmation questions"
        intro = ("Each answer separates source evidence, API coverage, target unknowns, vendor commitments and project decisions. "
                 "Source-only reads cannot prove future migration behavior.")
        questions = _environment_questions_html(data) or '<p class="muted">No structured questions were produced.</p>'
    else:
        title = "ServiceDesk Plus migration — answers and confirmation questions"
        intro = ("Observed answers summarize the read-only scan. Items requiring confirmation remain open "
                 "until the responsible owner or ManageEngine supplies evidence. A local answer is not "
                 "proof of a vendor entitlement or a supported migration behavior.")
        questions = _html_questions(data)
    document = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'none\'; '
        'style-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
        "<title>Vendor questions</title>"
        f"<style>{_STYLE}\nh4{{font-size:15px;margin:20px 0 8px;color:var(--accent);}}"
        ".question{break-inside:auto;}@media print{.question{break-before:page;}.question:first-of-type{break-before:auto;}}</style>"
        "</head><body><main>"
        f'<header><p class="eyebrow">Read-only environment assessment</p><h1>{_h(title)}</h1>'
        f'<p class="subtitle">{_h(intro)}</p><p>Generated: {_h(data.get("generated_at"))}</p></header>'
        f"<section>{questions}</section>"
        "<footer>Standalone offline document. No external scripts, styles, images or analytics are loaded. "
        "The Markdown and JSON files remain the authoritative evidence.</footer>"
        "</main></body></html>\n"
    )
    return _apply_brand(document, brand, "SDP Migration Vendor Questions", "Vendor Questions")


def render_report_documents(assessment: Assessment) -> dict[str, str]:
    """Render exactly six sanitized offline documents without filesystem I/O."""
    if not isinstance(assessment, Assessment):
        raise TypeError("assessment must be an Assessment")
    data = _sanitize_assessment(assessment)
    findings_headers = [
        "id", "scope", "portal_id", "portal_name", "module", "evidence_basis",
        "title", "category", "severity", "status", "affected_count", "examined_count",
        "summary", "coverage", "evidence", "action", "sources",
    ]
    coverage_headers = [
        "key", "endpoint", "status", "records_examined", "api_reported_total", "pages",
        "list_complete_for_api_scope", "details_attempted", "details_examined", "issues", "sampling", "source",
    ]
    if data.get("environment"):
        coverage_headers = [
            "portal_id", "portal_name", "scope", "resource", "module", "endpoint",
            "status", "outcome", "records_observed", "pages_observed", "list_complete",
            "detail_records_attempted", "detail_records_successful", "detail_complete",
            "http_status", "api_codes", "error_class", "reason", "confidence",
            *[key for key in coverage_headers if key not in {"endpoint", "status"}],
        ]
    for item in data.get("coverage", []):
        coverage_headers.extend(key for key in item if key not in coverage_headers)
    documents = {
        "report.html": _render_html(data),
        "report.md": _render_markdown(data),
        "assessment.json": json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        "findings.csv": _csv_document(findings_headers, data.get("findings", [])),
        "coverage.csv": _csv_document(coverage_headers, [
            {**item, "status": item.get("outcome", item.get("status"))} if data.get("environment") else item
            for item in data.get("coverage", [])
        ]),
        "vendor-questions.md": _question_markdown(data, standalone=True).rstrip() + "\n",
    }
    return documents


def write_reports(assessment: Assessment, output_dir: Path | str) -> dict[str, str]:
    """Write, reopen and verify six report files; return only verified paths.

    Existing callers keep the six-file contract. The CLI adds an explicit
    diagnostic file, publication manifest and ZIP recovery copy separately.
    """
    documents = render_report_documents(assessment)
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    paths = {}
    for filename, contents in documents.items():
        destination = output / filename
        _atomic_write(destination, contents)
        paths[filename] = str(destination)
    for filename, contents in documents.items():
        verify_bytes(output / filename, contents.encode("utf-8"))
    return paths
