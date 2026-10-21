"""Offline multi-portal report structure, coverage and privacy."""

from __future__ import annotations

import csv
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest

from sdp_audit.environment_analysis import analyze_environment
from sdp_audit.fields import FieldInventory
from sdp_audit.report import write_reports
from tests.test_environment_analysis import PRIVATE, field, inventory, multi_environment


class _Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.headings = []
        self._heading = False

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag == "h2":
            self._heading = True

    def handle_endtag(self, tag):
        if tag == "h2":
            self._heading = False

    def handle_data(self, data):
        if self._heading:
            self.headings.append(data)


class EnvironmentReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.environment = multi_environment()
        self.environment.portals["3"].snapshot.fields["requests"] = inventory(
            [field(1, maximum_length=1000, default_character_count=300, custom=True)])
        self.environment.portals["7"].snapshot.fields["projects"] = FieldInventory(
            "projects", "7", "HR", status="ENDPOINT_UNSUPPORTED")

    def reports(self):
        return write_reports(analyze_environment(self.environment), self.temp.name)

    def test_all_requested_environment_sections_render_without_active_content(self):
        paths = self.reports()
        self.assertEqual(len(paths), 6)
        parser = _Elements()
        parser.feed(Path(paths["report.html"]).read_text())
        for title in (
            "Executive summary", "Environment topology", "Portals discovered", "Portals assessed",
            "Portal access gaps and permissions diagnostics", "Per-portal migration risks",
            "Environment-wide aggregated risks", "Data-volume summary",
            "Configuration/customization impact", "Field/UDF impact", "Reporting impact",
            "Automation/integration impact", "Historical-data exposure", "Assets/CMDB exposure",
            "Coverage and confidence", "Vendor/project questions", "Acceptance blockers",
        ):
            self.assertIn(title, parser.headings)
        self.assertFalse(any(tag in {"script", "img", "iframe", "object", "embed", "link"} for tag, _ in parser.elements))
        self.assertFalse(any(key.lower().startswith("on") for _, attrs in parser.elements for key in attrs))
        ids = [attrs["id"] for _, attrs in parser.elements if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_coverage_csv_uses_portal_scope_and_unknown_counts(self):
        paths = self.reports()
        with Path(paths["coverage.csv"]).open(newline="") as handle:
            reader = csv.DictReader(handle)
            headings = reader.fieldnames
            rows = list(reader)
        self.assertEqual(len(headings), len(set(headings)))
        for key in ("portal_id", "portal_name", "module", "resource", "endpoint", "status",
                    "records_observed", "pages_observed", "list_complete", "detail_complete",
                    "detail_records_attempted", "detail_records_successful", "http_status",
                    "api_codes", "error_class", "reason", "confidence"):
            self.assertIn(key, headings)
        lookup = {(row["portal_id"], row["resource"]): row for row in rows}
        denied = lookup["7", "projects"]
        self.assertEqual(denied["records_observed"], "")
        self.assertEqual(denied["status"], "PERMISSION_DENIED")
        self.assertEqual(denied["http_status"], "403")
        self.assertIn("4002", denied["api_codes"])
        self.assertEqual(lookup["3", "projects"]["records_observed"], "0")
        self.assertEqual(lookup["3", "projects"]["status"], "EMPTY")

    def test_capabilities_and_expiration_limit_are_visible_in_human_reports(self):
        self.environment.portals["3"].snapshot.capabilities["requests"] = {
            "availability": "AVAILABLE", "discovery_method": "documented_inventory_first_page_reused",
            "operations": [{"resource": "requests", "endpoint": "/requests", "status": "COMPLETE",
                            "capability": "AVAILABLE"}],
        }
        paths = self.reports()
        for filename in ("report.html", "report.md"):
            text = Path(paths[filename]).read_text()
            self.assertIn("Module availability and discovery evidence", text)
            self.assertIn("documented_inventory_first_page_reused", text.replace("\\_", "_"))
            self.assertIn("No verified read-only expiration mechanism is implemented", text)

    def test_findings_csv_and_json_preserve_provenance_without_raw_records(self):
        paths = self.reports()
        document = json.loads(Path(paths["assessment.json"]).read_text())
        self.assertEqual(document["schema_version"], "2.0")
        self.assertEqual({item["portal_id"] for item in document["portals"]}, {"3", "7"})
        self.assertEqual(document["field_inventory"][0]["fields"][0]["display_label"], "Additional field 1")
        self.assertIsNone(document["field_inventory"][1]["additional_fields_observed"])
        self.assertEqual(document["field_inventory"][0]["fields"][0]["default_character_count"], 300)
        with Path(paths["findings.csv"]).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        portal_finding = next(row for row in rows if row["id"] == "portal:3:FIELD_REQUESTS_DEFAULT_OPTION_SIZE")
        self.assertEqual(portal_finding["portal_name"], "IT Helpdesk")
        self.assertEqual(portal_finding["module"], "requests")
        self.assertEqual(portal_finding["evidence_basis"], "API_METADATA")
        self.assertFalse(any('"records":' in Path(path).read_text() for path in paths.values()))

    def test_all_outputs_exclude_source_content_and_credentials(self):
        # Synthetic input includes source content plus disallowed optional keys.
        credential = "SYNTHETIC-UNIQUE-CREDENTIAL-ONLY"
        self.environment.stats["api_key"] = credential
        self.environment.source["authtoken"] = credential
        self.environment.settings["password"] = credential
        paths = self.reports()
        for filename, path in paths.items():
            text = Path(path).read_text()
            for secret in (PRIVATE, "private@example.test", credential):
                self.assertNotIn(secret, text, filename)
        self.assertIn("[redacted]", Path(paths["assessment.json"]).read_text())

    def test_portal_labels_are_html_escaped_and_csv_formulas_neutralized(self):
        self.environment.portals["3"].portal.name = '=HYPERLINK("x")<script>alert(1)</script>'
        self.environment.portals["3"].snapshot.fields["requests"].fields[0].display_label = "<img src=x onerror=alert(1)>"
        paths = self.reports()
        html = Path(paths["report.html"]).read_text()
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<img src=x", html)
        with Path(paths["coverage.csv"]).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        label = next(row["portal_name"] for row in rows if row["portal_id"] == "3")
        self.assertTrue(label.startswith("'="))

    def test_questions_markdown_separates_five_evidence_categories_and_portals(self):
        paths = self.reports()
        text = Path(paths["vendor-questions.md"]).read_text()
        for heading in ("Confirmed source evidence", "API coverage limitations", "Target-cloud unknowns",
                        "Vendor confirmation required", "Project/business decision required"):
            self.assertEqual(text.count("#### " + heading), 7)
        self.assertIn("HR (ID 7)", text)
        self.assertIn("projects", text)
        self.assertIn("IT Helpdesk (ID 3)", text)
        self.assertNotIn("confirmed_source_evidence", text)
        markdown = Path(paths["report.md"]).read_text()
        self.assertIn("## Field/UDF impact", markdown)
        self.assertIn("## Detailed findings and measured evidence", markdown)


if __name__ == "__main__":
    unittest.main()
