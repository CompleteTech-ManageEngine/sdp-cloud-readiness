"""Branded Scope of Work rendered from an engagement's own Markdown.

The SoW text is engagement content and lives with the client's assessment
(``<assessment>/scope-of-work.md``), not in this repository. Placeholders
keep names and evidence figures tied to the brand and to ``assessment.json``:

* ``{{consultant}}``, ``{{client}}``, ``{{source_url}}``, ``{{assessment_date}}``,
  ``{{portal_count}}``
* ``{{inventory_table}}``: per-portal templates, reports, support groups and
  technician memberships with a total row
* ``{{inventory_total:KEY}}`` (``KEY`` may join collections with ``+``)
* ``{{impact_total:RULE}}`` and ``{{impact_portals:RULE}}`` for confirmed
  impacts, e.g. ``DUPLICATE_SERVICE_TAGS``

An unknown placeholder, or an inventory figure whose list traversal was not
complete, stops rendering: contract figures must come from complete evidence.
Supported Markdown: headings, paragraphs (two trailing spaces break a line),
``-`` bullets, pipe tables, ``**bold**``, ``[text](https://...)`` links and
``<!-- pagebreak -->``.
"""

from __future__ import annotations

from datetime import datetime
import html
import re
from typing import Any, Mapping

from .branding import Brand

TOKEN = re.compile(r"\{\{\s*([a-z_]+)(?::([A-Za-z0-9_+]+))?\s*\}\}")
INVENTORY = (("incident_templates", "Incident templates"), ("service_templates", "Service templates"),
             ("reports", "Query-report entries"), ("support_groups", "Support groups"),
             ("technicians", "Technician memberships"))
PAGEBREAK = "<!-- pagebreak -->"


def _number(value: int) -> str:
    return f"{value:,}"


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + ", and " + items[-1]


class Figures:
    """Evidence figures for placeholders, computed from sanitized assessment data."""

    def __init__(self, data: Mapping[str, Any], brand: Brand):
        self.data, self.brand = data, brand
        self.used: dict[str, str] = {}

    def _coverage(self, key: str) -> list[tuple[str, int]]:
        rows, incomplete = [], []
        for portal in self.data.get("portals", []):
            row = next((r for r in portal.get("coverage", []) if r.get("key") == key), None)
            if row is None or row.get("list_complete") is not True or not isinstance(row.get("records_observed"), int):
                incomplete.append(str(portal.get("portal_id")))
                continue
            rows.append((str(portal.get("portal_id")), row["records_observed"]))
        if incomplete:
            raise ValueError(f"Scope of Work figure '{key}' is not complete for portal(s) {', '.join(incomplete)}; "
                             "complete the collection or remove the placeholder.")
        return rows

    def _impacts(self, rule: str) -> list[Mapping[str, Any]]:
        found = [f for f in self.data.get("findings", [])
                 if f.get("status") == "CONFIRMED_IMPACT" and str(f.get("id", "")).endswith(":" + rule)]
        if not found:
            raise ValueError(f"Scope of Work references {rule}, which has no confirmed impact in this assessment.")
        return found

    def value(self, name: str, arg: str | None) -> str:
        source = self.data.get("source", {})
        if name == "consultant" and not arg:
            return self.brand.name
        if name == "client" and not arg:
            if not self.brand.prepared_for:
                raise ValueError("Scope of Work needs a client name: pass --prepared-for or set SDP_PREPARED_FOR.")
            return self.brand.prepared_for
        if name == "source_url" and not arg:
            return str(source.get("host") or source.get("base_url") or "")
        if name == "assessment_date" and not arg:
            stamp = datetime.fromisoformat(str(self.data.get("generated_at")).replace("Z", "+00:00"))
            return f"{stamp.day} {stamp:%B %Y}"
        if name == "portal_count" and not arg:
            return _number(len(self.data.get("portals", [])))
        if name == "inventory_table" and not arg:
            return self.inventory_table()
        if name == "inventory_total" and arg:
            return _number(sum(count for key in arg.split("+") for _, count in self._coverage(key)))
        if name == "impact_total" and arg:
            return _number(sum(int(f.get("affected_count") or 0) for f in self._impacts(arg)))
        if name == "impact_portals" and arg:
            return _join(list(dict.fromkeys(str(f.get("portal_id")) for f in self._impacts(arg))))
        raise ValueError(f"Unknown Scope of Work placeholder: {{{{{name}{':' + arg if arg else ''}}}}}")

    def inventory_table(self) -> str:
        columns = [dict(self._coverage(key)) for key, _ in INVENTORY]
        portals = [str(p.get("portal_id")) for p in self.data.get("portals", [])]
        lines = ["| Source portal ID | " + " | ".join(label for _, label in INVENTORY) + " |",
                 "| --- |" + " --- |" * len(INVENTORY)]
        lines += ["| " + pid + " | " + " | ".join(_number(c[pid]) for c in columns) + " |" for pid in portals]
        lines.append("| **Total** | " + " | ".join(f"**{_number(sum(c.values()))}**" for c in columns) + " |")
        return "\n".join(lines)

    def fill(self, text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            value = self.value(match.group(1), match.group(2))
            self.used[match.group(0)] = value if match.group(1) != "inventory_table" else "(table)"
            return value
        return TOKEN.sub(replace, text)


def parse(markdown: str) -> list[tuple[str, Any]]:
    """Split the supported Markdown subset into blocks: heading, para, list, table, pagebreak."""
    blocks: list[tuple[str, Any]] = []
    lines = markdown.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
        elif stripped == PAGEBREAK:
            blocks.append(("pagebreak", None))
            i += 1
        elif re.match(r"#{1,6} ", stripped):
            level = len(stripped) - len(stripped.lstrip("#"))
            blocks.append(("heading", (level, stripped[level:].strip())))
            i += 1
        elif stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
        elif stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(("list", items))
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,6} |\||- |<!--)", lines[i].strip()):
                para.append(lines[i].rstrip("\n"))
                i += 1
            blocks.append(("para", para))
    return blocks


def inline_html(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', out)


def body_html(blocks: list[tuple[str, Any]]) -> str:
    out = []
    for kind, value in blocks:
        if kind == "pagebreak":
            out.append('<div class="page-break"></div>')
        elif kind == "heading":
            level, text = value
            out.append(f"<h{level}>{inline_html(text)}</h{level}>")
        elif kind == "para":
            out.append("<p>" + "<br>".join(inline_html(line.strip()) for line in value) + "</p>")
        elif kind == "list":
            out.append("<ul>" + "".join(f"<li>{inline_html(item)}</li>" for item in value) + "</ul>")
        elif kind == "table":
            head, *rows = value
            out.append('<div class="table-scroll"><table><thead><tr>' + "".join(f"<th>{inline_html(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in row) + "</tr>" for row in rows)
                       + "</tbody></table></div>")
    return "\n".join(out)


def document_title(blocks: list[tuple[str, Any]]) -> str:
    for kind, value in blocks:
        if kind == "heading" and value[0] == 1:
            return value[1]
    return "Scope of Work"


def render_html(blocks: list[tuple[str, Any]], brand: Brand) -> str:
    from .report import _STYLE, _apply_brand
    title = document_title(blocks)
    document = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'none\'; '
        'style-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
        "<title>Scope of Work</title>"
        f"<style>{_STYLE}\n"
        "p{white-space:normal;}h2{margin-top:30px;}h3{font-size:18px;margin:26px 0 8px;color:var(--accent);}"
        "td,th{white-space:normal;}.page-break{height:0;}"
        "@media print{.page-break{break-after:page;}h2,h3{break-after:avoid;}table{font-size:9pt;}}</style>"
        "</head><body><main>"
        f"{body_html(blocks)}"
        "<footer>Scope of Work rendered from the engagement's Markdown source. Evidence figures are filled from the "
        "assessment's assessment.json; see branded-manifest.json.</footer>"
        "</main></body></html>\n"
    )
    return _apply_brand(document, brand, title + " · Scope of Work", "Scope of Work")
