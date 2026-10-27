"""Small Markdown reader shared by the branded HTML and Word renderers.

Covers what this tool's own reports, the Scope of Work and the repository
documentation use: headings, paragraphs (two trailing spaces break a line),
``-``/``*`` and numbered lists, pipe tables, fenced code, ``**bold**``,
inline code, backslash escapes, ``[text](url)`` and ``[text](<url>)`` links
and ``<!-- pagebreak -->``. Raw HTML lines are dropped (the brand masthead
already carries the logo); HTML inside text is escaped, never executed.
Only http(s) links stay links; relative links render as their text.
"""

from __future__ import annotations

import html
import re
from typing import Any

PAGEBREAK = "<!-- pagebreak -->"
BULLET = re.compile(r"[-*] ")
NUMBERED = re.compile(r"\d+\. ")
# Inline tokens, in priority order: code, escape, link, bold.
INLINE = re.compile(r"(`[^`]+`|\\[\\`*_{}\[\]()#+\-.!|<>~]|\[[^\]]+\]\((?:<[^>\s]+>|[^)\s]+)\)|\*\*.+?\*\*)")
LINK = re.compile(r"\[([^\]]+)\]\(<?([^>)\s]+)>?\)")


def tokens(text: str) -> list[tuple[str, str, str]]:
    """Split inline text into (kind, text, url) runs: text, bold, code, link."""
    out: list[tuple[str, str, str]] = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(("code", part[1:-1], ""))
        elif len(part) == 2 and part[0] == "\\":
            out.append(("text", part[1], ""))
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            for kind, inner, url in tokens(part[2:-2]):
                out.append(("bold" if kind == "text" else kind, inner, url))
        elif (link := LINK.fullmatch(part)) is not None:
            label = "".join(t for _, t, _ in tokens(link.group(1)))
            url = link.group(2)
            out.append(("link", label, url) if url.startswith(("https://", "http://")) else ("text", label, ""))
        else:
            out.append(("text", part, ""))
    return out


def inline_html(text: str) -> str:
    out = []
    for kind, value, url in tokens(text):
        safe = html.escape(value, quote=False)
        if kind == "bold":
            out.append(f"<strong>{safe}</strong>")
        elif kind == "code":
            out.append(f"<code>{safe}</code>")
        elif kind == "link":
            out.append(f'<a href="{html.escape(url)}">{safe}</a>')
        else:
            out.append(safe)
    return "".join(out)


def parse(markdown: str) -> list[tuple[str, Any]]:
    """Blocks: heading (level, text), para [lines], list (ordered, [items]), table [[cells]], code [lines], pagebreak."""
    blocks: list[tuple[str, Any]] = []
    lines = markdown.replace("\r\n", "\n").split("\n")
    i = 0

    def starts_block(line: str) -> bool:
        s = line.strip()
        return (not s or s == PAGEBREAK or s.startswith(("|", "```", "<")) or bool(re.match(r"#{1,6} ", s))
                or bool(BULLET.match(s)) or bool(NUMBERED.match(s)))

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
        elif stripped == PAGEBREAK:
            blocks.append(("pagebreak", None))
            i += 1
        elif stripped.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            if stripped[3:].strip().lower() == "mermaid":
                # Diagram source: GitHub draws it; print and Word formats would only show the code.
                blocks.append(("para", ["The workflow diagram is drawn from its Mermaid source on GitHub."]))
            else:
                blocks.append(("code", code))
            i += 1
        elif stripped.startswith("<"):
            i += 1  # raw HTML line (e.g. a centred logo); the masthead already shows the brand
        elif re.match(r"#{1,6} ", stripped):
            level = len(stripped) - len(stripped.lstrip("#"))
            blocks.append(("heading", (level, stripped[level:].strip())))
            i += 1
        elif stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows))
        elif BULLET.match(stripped) or NUMBERED.match(stripped):
            ordered = bool(NUMBERED.match(stripped))
            pattern = NUMBERED if ordered else BULLET
            items: list[str] = []
            while i < len(lines) and lines[i].strip():
                s = lines[i].strip()
                if pattern.match(s):
                    items.append(pattern.sub("", s, count=1))
                elif starts_block(lines[i]) or not items:
                    break
                else:
                    items[-1] += " " + s  # continuation line of the previous item
                i += 1
            blocks.append(("list", (ordered, items)))
        else:
            para = []
            while i < len(lines) and not starts_block(lines[i]):
                para.append(lines[i])
                i += 1
            blocks.append(("para", para))
    return blocks


def _para_lines(lines: list[str]) -> list[str]:
    """Join soft-wrapped lines; keep a break only after two trailing spaces."""
    out: list[str] = []
    hard_break = True
    for line in lines:
        if out and not hard_break:
            out[-1] += " " + line.strip()
        else:
            out.append(line.strip())
        hard_break = line.endswith("  ")
    return out


def body_html(blocks: list[tuple[str, Any]]) -> str:
    out = []
    for kind, value in blocks:
        if kind == "pagebreak":
            out.append('<div class="page-break"></div>')
        elif kind == "heading":
            level, text = value
            out.append(f"<h{level}>{inline_html(text)}</h{level}>")
        elif kind == "para":
            out.append("<p>" + "<br>".join(inline_html(line) for line in _para_lines(value)) + "</p>")
        elif kind == "list":
            ordered, items = value
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline_html(item)}</li>" for item in items) + f"</{tag}>")
        elif kind == "code":
            out.append("<pre><code>" + html.escape("\n".join(value), quote=False) + "</code></pre>")
        elif kind == "table":
            head, *rows = value
            out.append('<div class="table-scroll"><table><thead><tr>' + "".join(f"<th>{inline_html(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in row) + "</tr>" for row in rows)
                       + "</tbody></table></div>")
    return "\n".join(out)


def document_title(blocks: list[tuple[str, Any]], default: str = "Document") -> str:
    for kind, value in blocks:
        if kind == "heading" and value[0] == 1:
            return "".join(text for _, text, _ in tokens(value[1]))
    return default


def paragraph_lines(lines: list[str]) -> list[str]:
    return _para_lines(lines)
