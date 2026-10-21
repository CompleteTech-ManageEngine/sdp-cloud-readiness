"""Report-level tests: coverage semantics, output safety, and atomic files."""

from __future__ import annotations

import csv
from html import escape
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sdp_audit.models import Assessment, Finding
from sdp_audit.report import write_reports


class _HTMLInventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, dict(attrs)))


def _assessment() -> Assessment:
    return Assessment(
        generated_at="2026-10-05T17:00:00Z",
        source={"host": "https://servicedesk.example.test", "deployment": "on-premises", "build": "14810"},
        settings={"max_requests": 500, "requests_per_minute": 30, "max_records_per_dataset": 2000, "page_size": 100},
        findings=[
            Finding(
                id="ATTACHMENT-LIMIT", title="Attachment totals exceed the migration limit",
                category="Migration data", severity="HIGH", status="CONFIRMED_IMPACT",
                summary="One of two examined entities exceeds the 48 MB documented migration threshold.",
                affected_count=1, examined_count=2,
                evidence=[{"entity_id": "123", "attachment_bytes": 60000000, "limit_bytes": 48000000}],
                action="Confirm the vendor's exact units and preserve the complete source attachments.",
                sources=["migration_limits"], coverage="Two details examined; 12 visible requests listed.",
            ),
            Finding(
                id="FIELD-LIMIT", title="Request additional-field count", category="Configuration",
                severity="LOW", status="NO_ISSUE_OBSERVED", summary="Eight visible fields were counted.",
                affected_count=0, examined_count=8, evidence=[{"field_count": 8, "limit": 250}],
                action="Validate Cloud mapping in the trial migration.", sources=["migration_limits"],
            ),
            Finding(
                id="HISTORY", title="History inspection", category="History", severity="HIGH", status="UNKNOWN",
                summary="The API key could not inspect this module.", examined_count=0,
                action="Use the administrator inventory and trial migration to resolve the gap.",
            ),
            Finding(
                id="RECOVERY", title="Recovery arrangement", category="Operations", severity="MEDIUM",
                status="MANUAL_CONFIRMATION", summary="Recovery targets cannot be established by the source API.",
                action="Obtain the tenant-specific recovery terms from ManageEngine.",
            ),
        ],
        questions=[
            {
                "id": "Q-ATTACHMENTS", "title": "Will all required attachments migrate?",
                "status": "MANUAL_CONFIRMATION", "observed": "One entity exceeds the configured threshold.",
                "requires_confirmation": "Confirm size units and the exception-handling procedure.",
                "finding_ids": ["ATTACHMENT-LIMIT"],
            }
        ],
        coverage=[
            {
                "key": "requests", "endpoint": "/api/v3/requests", "status": "ok",
                "records_examined": 12, "api_reported_total": 12, "pages": 1,
                "list_complete_for_api_scope": True, "details_attempted": 2, "details_examined": 2,
                "issues": [], "sampling": "Bounded selection across listed records",
                "source": "https://docs.example.test/api/requests",
            },
            {
                "key": "changes", "endpoint": "/api/v3/changes", "status": "forbidden",
                "records_examined": 0, "api_reported_total": None, "pages": 0,
                "list_complete_for_api_scope": False, "details_attempted": 0, "details_examined": 0,
                "issues": ["HTTP 403; API-key visibility does not establish that the module is unused."],
                "sampling": "Not sampled", "source": "https://docs.example.test/api/changes",
                "skipped_reason": "API permissions",
            },
        ],
        stats={"requests_sent": 11, "retries": 1, "rate_limit_responses": 1, "elapsed_seconds": 33.5},
        sources={
            "migration_limits": {
                "title": "ManageEngine migration limitations", "url": "https://docs.example.test/migration-limitations",
                "reviewed_on": "2026-10-05",
            }
        },
        notes=["Synthetic test fixture. Not a real environment assessment."],
    )


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name) / "20261005T170000Z"
        self.addCleanup(self.temp.cleanup)

    def _write(self, assessment: Assessment | None = None) -> dict[str, str]:
        return write_reports(assessment or _assessment(), self.output)

    def test_all_files_and_exact_coverage_are_present(self) -> None:
        paths = self._write()
        self.assertEqual(
            set(paths), {"report.html", "report.md", "assessment.json", "findings.csv", "coverage.csv", "vendor-questions.md"}
        )
        for name, filename in paths.items():
            self.assertTrue(Path(filename).is_absolute())
            self.assertEqual(Path(filename).name, name)
            self.assertTrue(Path(filename).is_file())
        data = json.loads(Path(paths["assessment.json"]).read_text())
        self.assertEqual(data["settings"]["max_requests"], 500)
        self.assertEqual(data["stats"]["requests_sent"], 11)
        self.assertEqual(data["findings"][0]["evidence"][0]["entity_id"], "123")
        self.assertIsNone(data["findings"][2]["affected_count"])
        with Path(paths["coverage.csv"]).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["records_examined"], "12")
        self.assertEqual(rows[0]["list_complete_for_api_scope"], "true")
        self.assertEqual(rows[0]["details_attempted"], "2")
        self.assertEqual(rows[1]["api_reported_total"], "")
        self.assertEqual(rows[1]["list_complete_for_api_scope"], "false")
        self.assertEqual(rows[1]["skipped_reason"], "API permissions")
        markdown = Path(paths["report.md"]).read_text()
        for text in ("requests\\_sent", "max\\_requests", "60000000", "48000000", "Q-ATTACHMENTS", "API key", "transactional snapshot"):
            self.assertIn(text, markdown)
        questions = Path(paths["vendor-questions.md"]).read_text()
        self.assertIn("One entity exceeds the configured threshold.", questions)
        self.assertIn("Confirm size units", questions)
        self.assertFalse(list(self.output.glob(".*.tmp")))

    def test_html_is_offline_with_csp_and_escapes_untrusted_values(self) -> None:
        assessment = _assessment()
        payload = '\"><script>alert("ticket")</script><img src="https://attacker.invalid/tracker">'
        assessment.findings[0].title = payload
        assessment.findings[0].evidence[0]["entity_id"] = "<b>unsafe-id</b>"
        assessment.questions[0]["observed"] = "</td><svg onload=alert(1)>"
        assessment.sources["unsafe"] = {"title": "Unsafe link", "url": "javascript:alert(1)", "reviewed_on": "2026-10-05"}
        assessment.findings[0].sources.append("unsafe")
        paths = self._write(assessment)
        document = Path(paths["report.html"]).read_text()
        self.assertNotIn("<script>", document)
        self.assertIn("&lt;script&gt;", document)
        self.assertIn("&lt;b&gt;unsafe-id&lt;/b&gt;", document)
        parser = _HTMLInventory()
        parser.feed(document)
        self.assertFalse(any(tag in {"script", "img", "iframe", "object", "embed", "link"} for tag, _ in parser.elements))
        self.assertFalse(any("onload" in attrs for _, attrs in parser.elements))
        policy = [attrs for tag, attrs in parser.elements if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"]
        self.assertEqual(len(policy), 1)
        self.assertIn("default-src 'none'", policy[0]["content"])
        self.assertIn("script-src 'none'", policy[0]["content"])
        self.assertIn("connect-src 'none'", policy[0]["content"])
        links = [attrs["href"] for tag, attrs in parser.elements if tag == "a"]
        self.assertTrue(links)
        self.assertTrue(all(link.startswith(("https://", "http://")) for link in links))
        self.assertNotIn("javascript:alert(1)", links)
        self.assertNotIn('<img src="https://attacker.invalid/tracker">', Path(paths["report.md"]).read_text())

    def test_statuses_are_counted_separately_and_unknown_is_not_zero(self) -> None:
        paths = self._write()
        markdown = Path(paths["report.md"]).read_text()
        for status in ("Confirmed impact", "No issue observed", "Unknown", "Manual confirmation"):
            self.assertIn(f"| {status} | 1 |", markdown)
        self.assertIn("Affected: Not established", markdown)
        self.assertIn("not assign an overall readiness score", markdown)
        self.assertNotIn("100% ready", markdown)

    def test_unrecognized_status_is_explicitly_unresolved(self) -> None:
        assessment = _assessment()
        assessment.findings[0].status = "VENDOR_PENDING"
        paths = self._write(assessment)
        document = Path(paths["report.html"]).read_text()
        self.assertIn("Unrecognized finding statuses are unresolved", document)
        self.assertIn("Unrecognized status: VENDOR_PENDING", document)

    def test_csv_neutralizes_formula_prefixes_and_control_whitespace(self) -> None:
        prefixes = ('=HYPERLINK("https://example.test")', "+cmd", "-cmd", "@SUM(A1:A2)", "\t=cmd", " \r\n=cmd", "\ufeff@cmd", "\x01text")
        for index, payload in enumerate(prefixes):
            with self.subTest(payload=repr(payload)):
                assessment = _assessment()
                assessment.findings[0].title = payload
                assessment.coverage[0]["key"] = payload
                paths = write_reports(assessment, self.output / str(index))
                with Path(paths["findings.csv"]).open(newline="") as handle:
                    findings = list(csv.DictReader(handle))
                self.assertTrue(findings[0]["title"].startswith("'"))
                with Path(paths["coverage.csv"]).open(newline="") as handle:
                    coverage = list(csv.DictReader(handle))
                self.assertTrue(coverage[0]["key"].startswith("'"))

    def test_credentials_and_raw_record_content_are_redacted_in_every_artifact(self) -> None:
        assessment = _assessment()
        assessment.source["host"] = "https://USER_SECRET:PASSWORD_SECRET@servicedesk.example.test/path?api_key=QUERY_SECRET#TOKEN_SECRET"
        assessment.source["api_key"] = "PRIVATE_API_SECRET"
        assessment.settings["headers"] = {"Authorization": "Bearer HEADER_SECRET"}
        assessment.findings[0].evidence[0].update({
            "subject": "PRIVATE_SUBJECT", "description": "PRIVATE_BODY",
            "filename": "PRIVATE_FILENAME.pdf", "requester_email": "PRIVATE_ADDRESS",
        })
        assessment.notes.append("Diagnostic was password=INLINE_SECRET")
        paths = self._write(assessment)
        for path in paths.values():
            text = Path(path).read_text()
            for secret in (
                "USER_SECRET", "PASSWORD_SECRET", "QUERY_SECRET", "TOKEN_SECRET", "PRIVATE_API_SECRET",
                "HEADER_SECRET", "PRIVATE_SUBJECT", "PRIVATE_BODY", "PRIVATE_FILENAME", "PRIVATE_ADDRESS", "INLINE_SECRET",
            ):
                self.assertNotIn(secret, text)
        data = json.loads(Path(paths["assessment.json"]).read_text())
        self.assertEqual(data["source"]["host"], "https://servicedesk.example.test/path")
        self.assertEqual(data["source"]["api_key"], "[redacted]")
        self.assertEqual(data["findings"][0]["evidence"][0]["entity_id"], "123")

    def test_atomic_replace_failure_keeps_previous_file_and_cleans_temporary_file(self) -> None:
        self.output.mkdir(parents=True)
        destination = self.output / "report.html"
        destination.write_text("Previous complete report")
        with patch("sdp_audit.report.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                self._write()
        self.assertEqual(destination.read_text(), "Previous complete report")
        self.assertFalse(list(self.output.glob(".*.tmp")))

    def test_empty_assessment_is_not_presented_as_ready(self) -> None:
        assessment = _assessment()
        assessment.findings = []
        assessment.coverage = []
        assessment.questions = []
        assessment.sources = {}
        paths = self._write(assessment)
        text = Path(paths["report.html"]).read_text()
        self.assertIn("No findings were produced. This is not an acceptance decision.", text)
        self.assertIn("Completeness is not established.", text)
        self.assertEqual(len(list(csv.reader(io.StringIO(Path(paths["findings.csv"]).read_text())))), 1)

    def test_input_assessment_is_not_mutated(self) -> None:
        assessment = _assessment()
        assessment.source["api_key"] = "UNCHANGED_SOURCE_SECRET"
        before = assessment.to_dict()
        self._write(assessment)
        self.assertEqual(assessment.to_dict(), before)

    def test_integrated_demo_preserves_email_source_id_handles_bad_metadata_and_shows_answers(self) -> None:
        from sdp_audit.analyze import analyze
        from sdp_audit.demo import demo_snapshot

        assessment = analyze(demo_snapshot())
        assessment.sources["email"] = {
            "title": "Official email behavior documentation",
            "url": "https://docs.example.test/email-behavior",
            "reviewed_on": "2026-10-05",
            "api_key": "DO_NOT_EMIT_SOURCE_SECRET",
        }
        assessment.sources["broken"] = "DO_NOT_EMIT_MALFORMED_SOURCE_VALUE"  # type: ignore[assignment]
        assessment.findings[0].sources.extend(["email", "broken"])
        paths = self._write(assessment)
        data = json.loads(Path(paths["assessment.json"]).read_text())
        self.assertEqual(data["sources"]["email"]["title"], "Official email behavior documentation")
        self.assertEqual(data["sources"]["email"]["url"], "https://docs.example.test/email-behavior")
        self.assertNotIn("api_key", data["sources"]["email"])
        self.assertIn("unavailable", data["sources"]["broken"]["metadata_status"])
        document = Path(paths["report.html"]).read_text()
        markdown = Path(paths["report.md"]).read_text()
        questions = Path(paths["vendor-questions.md"]).read_text()
        self.assertIn('href="https://docs.example.test/email-behavior"', document)
        self.assertIn("[email](<https://docs.example.test/email-behavior>)", markdown)
        self.assertIn("broken (source link unavailable)", document)
        self.assertEqual(len(assessment.questions), 7)
        for question in assessment.questions:
            self.assertIn(escape(question["observed"], quote=True), document)
            self.assertIn(escape(question["requires_confirmation"], quote=True), document)
            self.assertIn(question["observed"], markdown)
            self.assertIn(question["requires_confirmation"], markdown)
            self.assertIn(question["observed"], questions)
            self.assertIn(question["requires_confirmation"], questions)
        for path in paths.values():
            text = Path(path).read_text()
            self.assertNotIn("DO_NOT_EMIT_SOURCE_SECRET", text)
            self.assertNotIn("DO_NOT_EMIT_MALFORMED_SOURCE_VALUE", text)
            self.assertNotIn("SYNTHETIC PRIVATE SUBJECT", text)
            self.assertNotIn("SYNTHETIC_PRIVATE_ATTACHMENT", text)


if __name__ == "__main__":
    unittest.main()
