"""Shared Markdown reader and branded Word writer; synthetic content only."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from sdp_audit.branding import Brand
from sdp_audit.markdown_doc import body_html, document_title, paragraph_lines, parse, tokens

SAMPLE = """---
# Guide \\_title\\_

Intro line one
continues here.
Hard break **bold** and `code --flag` and [docs](<https://example.com/a b>) and [local](other.md).

1. First
2. Second
   wraps here
- Bullet

```powershell
python .\\tool.py --demo
```

```mermaid
flowchart LR
```

<p align="center"><img src="assets/logo.png"></p>

| Field | Value |
| --- | --- |
| portals\\_selected | 12 \\| 13 |

After table.
""".replace("continues here.\n", "continues here." + "  " + "\n")  # explicit hard break; editors strip trailing spaces


class MarkdownReaderTests(unittest.TestCase):
    def setUp(self):
        self.blocks = parse(SAMPLE)

    def test_blocks_and_title(self):
        kinds = [kind for kind, _ in self.blocks]
        self.assertEqual(document_title(self.blocks), "Guide _title_")
        self.assertIn(("list", (True, ["First", "Second wraps here"])), self.blocks)
        self.assertIn(("list", (False, ["Bullet"])), self.blocks)
        self.assertIn(("code", ["python .\\tool.py --demo"]), self.blocks)
        self.assertNotIn("flowchart LR", str(self.blocks))
        self.assertNotIn("<img", str(self.blocks))
        table = next(value for kind, value in self.blocks if kind == "table")
        self.assertEqual(table, [["Field", "Value"], ["portals\\_selected", "12 \\| 13"]])
        self.assertLess(kinds.index("table"), len(kinds) - 1)

    def test_paragraph_soft_wrap_and_hard_break(self):
        para = next(value for kind, value in self.blocks if kind == "para" and "Intro" in value[0])
        lines = paragraph_lines(para)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Intro line one continues here.")

    def test_inline_tokens(self):
        runs = tokens("**bold** `x` \\_ [a](<https://e.example/x>) [b](rel.md)")
        self.assertIn(("bold", "bold", ""), runs)
        self.assertIn(("code", "x", ""), runs)
        self.assertIn(("text", "_", ""), runs)
        self.assertIn(("link", "a", "https://e.example/x"), runs)
        self.assertIn(("text", "b", ""), runs)

    def test_html_escapes_and_links(self):
        html = body_html(parse("Text <script>alert(1)</script> [x](https://e.example)\n\n| a |\n| --- |\n| <b> |"))
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn('<a href="https://e.example">x</a>', html)
        self.assertIn("<td>&lt;b&gt;</td>", html)


@unittest.skipUnless(importlib.util.find_spec("docx"), "python-docx not installed")
class WordWriterTests(unittest.TestCase):
    def test_tables_stay_in_reading_order_and_text_is_complete(self):
        import docx
        from sdp_audit.branded_docx import write_docx
        brand = Brand(name="Fictional Advisory", website="fictional.example", prepared_for="Client")
        blocks = parse(SAMPLE)
        with tempfile.TemporaryDirectory() as directory:
            target = write_docx(blocks, brand, "Guide", "Documentation", Path(directory) / "guide.docx")
            document = docx.Document(str(target))
            body = list(document.element.body.iterchildren())
            tags = [element.tag.rsplit("}", 1)[1] for element in body]
            self.assertEqual(tags[-1], "sectPr")
            table_at = tags.index("tbl")
            after = "".join(t.text or "" for element in body[table_at + 1:] for t in element.iter() if t.tag.endswith("}t"))
            self.assertIn("After table.", after)
            text = "".join(t.text or "" for t in document.element.body.iter() if t.tag.endswith("}t"))
            self.assertIn("portals_selected", text)
            self.assertIn("12 | 13", text)
            self.assertIn("python .\\tool.py --demo", text)
            self.assertEqual(document.core_properties.author, "Fictional Advisory")


class DocumentMastheadTests(unittest.TestCase):
    def test_product_name_in_masthead(self):
        from sdp_audit.scope_of_work import render_document_html
        brand = Brand(name="Fictional Advisory", prepared_for="Client")
        blocks = parse("# Plan\n\nText.")
        self.assertIn("ServiceDesk Plus · Client", render_document_html(blocks, brand, "Plan", "Footer."))
        page = render_document_html(blocks, brand, "Plan", "Footer.", product="Zoho One")
        self.assertIn("Zoho One · Client", page)
        self.assertNotIn("ServiceDesk Plus", page)
