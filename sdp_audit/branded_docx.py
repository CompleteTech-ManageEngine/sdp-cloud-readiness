"""Editable branded Word copies of Markdown documents (requires python-docx).

Uses the same parsed blocks as the HTML/PDF rendering, so every format
carries identical text. Header: brand band with logo, document type and
client; footer: contact line and "Page n of N". Large tables are written
directly as table XML because python-docx's per-cell API is quadratic.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

from .branding import Brand
from .markdown_doc import paragraph_lines, tokens

FONT = "Arial"
MONO = "Consolas"


def _rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value.lstrip("#").upper())


def _shade(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), fill.lstrip("#"))
    props.append(shading)


def _field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, instruction), ("end", None)):
        if kind:
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), kind)
        else:
            element = OxmlElement("w:instrText")
            element.set(qn("xml:space"), "preserve")
            element.text = text
        run._r.append(element)


def _hyperlink(paragraph, url: str, text: str, colour: str, size: float | None) -> None:
    rel = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                   is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rel)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    for tag, value in (("w:color", colour.lstrip("#")), ("w:u", "single")):
        element = OxmlElement(tag)
        element.set(qn("w:val"), value)
        props.append(element)
    if size:
        element = OxmlElement("w:sz")
        element.set(qn("w:val"), str(int(size * 2)))
        props.append(element)
    run.append(props)
    content = OxmlElement("w:t")
    content.text = text
    content.set(qn("xml:space"), "preserve")
    run.append(content)
    link.append(run)
    paragraph._p.append(link)


def _inline(paragraph, text: str, brand: Brand, size: float | None = None, colour: str | None = None,
            bold: bool = False) -> None:
    for kind, value, url in tokens(text):
        if kind == "link":
            _hyperlink(paragraph, url, value, brand.tokens["link"], size)
            continue
        run = paragraph.add_run(value)
        run.bold = bold or kind == "bold"
        run.font.name = MONO if kind == "code" else FONT
        if size:
            run.font.size = Pt(size)
        if colour:
            run.font.color.rgb = _rgb(colour)


def _runs_xml(text: str, brand: Brand, size: float, colour: str, bold: bool = False) -> str:
    """WordprocessingML runs for a table cell (links become coloured text)."""
    out = []
    for kind, value, _ in tokens(text):
        props = f'<w:rFonts w:ascii="{MONO if kind == "code" else FONT}" w:hAnsi="{MONO if kind == "code" else FONT}"/>'
        if bold or kind == "bold":
            props += "<w:b/>"
        props += f'<w:color w:val="{(brand.tokens["link"] if kind == "link" else colour).lstrip("#")}"/>'
        props += f'<w:sz w:val="{int(size * 2)}"/>'
        out.append(f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(value)}</w:t></w:r>')
    return "".join(out)


def _column_widths(rows: list[list[str]], cols: int, width_twips: int) -> list[int]:
    """Share the width by typical content length, so short codes do not take as much room as long text."""
    weights = []
    for index in range(cols):
        lengths = sorted(len(r[index]) if index < len(r) else 0 for r in rows[:400])
        typical = lengths[int(len(lengths) * 0.9)] if lengths else 1
        weights.append(min(max(typical, len(rows[0][index]) // 2 if index < len(rows[0]) else 1, 4), 60))
    total = sum(weights)
    widths = [max(int(width_twips * w / total), 600) for w in weights]
    widths[-1] += width_twips - sum(widths)
    return widths


def _table(document, rows: list[list[str]], brand: Brand, width_twips: int) -> None:
    t = brand.tokens
    head, *body = rows
    cols = max(len(r) for r in rows)
    widths = _column_widths(rows, cols, width_twips)
    size = 8.5 if cols < 7 else 7
    border = f'w:val="single" w:sz="4" w:space="0" w:color="{t["line"].lstrip("#")}"'
    xml = [f'<w:tbl {nsdecls("w")}><w:tblPr><w:tblW w:w="{width_twips}" w:type="dxa"/>'
           f'<w:tblBorders><w:top {border}/><w:left {border}/><w:bottom {border}/><w:right {border}/>'
           f'<w:insideH {border}/><w:insideV {border}/></w:tblBorders>'
           '<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar>'
           '<w:tblLook w:val="04A0" w:firstRow="1"/></w:tblPr><w:tblGrid>'
           + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]

    def row(cells: list[str], header: bool, shade: str | None) -> str:
        cells = cells + [""] * (cols - len(cells))
        fill = f'<w:shd w:val="clear" w:color="auto" w:fill="{shade.lstrip("#")}"/>' if shade else ""
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if header else ""
        colour = t["band_ink"] if header else t["ink_2"]
        return ("<w:tr>" + trpr + "".join(
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{fill}</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>{_runs_xml(c, brand, size, colour, header)}</w:p></w:tc>'
            for c, w in zip(cells, widths)) + "</w:tr>")

    xml.append(row(head, True, t["band"]))
    xml.extend(row(r, False, t["surface"] if i % 2 else None) for i, r in enumerate(body))
    xml.append("</w:tbl>")
    # Insert in reading order (before the spacer paragraph), never after the body's final section properties.
    spacer = document.add_paragraph()
    spacer.paragraph_format.space_after = Pt(4)
    spacer.paragraph_format.line_spacing = Pt(2)
    spacer._p.addprevious(parse_xml("".join(xml)))


def _header(section, brand: Brand, doc_type: str) -> None:
    t = brand.tokens
    header = section.header
    header.is_linked_to_previous = False
    table = header.add_table(rows=1, cols=2, width=section.page_width - section.left_margin - section.right_margin)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    left, right = table.rows[0].cells
    for cell in (left, right):
        _shade(cell, t["band"])
    para = left.paragraphs[0]
    if brand.logo:
        para.add_run().add_picture(BytesIO(brand.logo), height=Inches(0.55))
    else:
        _inline(para, brand.name, brand, 12, t["band_ink"], bold=True)
    title = right.paragraphs[0]
    title.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _inline(title, doc_type, brand, 14, t["band_ink"])
    if brand.prepared_for:
        ref = right.add_paragraph()
        ref.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _inline(ref, brand.prepared_for.upper(), brand, 7.5, t["accent_2"], bold=True)


def _footer(section, brand: Brand) -> None:
    footer = section.footer
    footer.is_linked_to_previous = False
    para = footer.paragraphs[0]
    muted = brand.tokens["ink_3"]
    _inline(para, brand.contact + ("  ·  Prepared for " + brand.prepared_for if brand.prepared_for else "") + "    ",
            brand, 7.5, muted)
    _inline(para, "Page ", brand, 7.5, muted)
    _field(para, "PAGE")
    _inline(para, " of ", brand, 7.5, muted)
    _field(para, "NUMPAGES")


def write_docx(blocks: list[tuple[str, Any]], brand: Brand, title: str, doc_type: str, target: Path) -> Path:
    t = brand.tokens
    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.left_margin = section.right_margin = Inches(0.85)
    section.top_margin, section.bottom_margin = Inches(1.1), Inches(0.8)
    width_twips = int((section.page_width - section.left_margin - section.right_margin) / 635)
    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(10)
    normal.font.color.rgb = _rgb(t["ink_2"])
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    _header(section, brand, doc_type)
    _footer(section, brand)
    sizes = {1: (24, t["ink"]), 2: (16, t["ink"]), 3: (12.5, t["accent"]), 4: (11, t["ink"])}
    for kind, value in blocks:
        if kind == "pagebreak":
            document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        elif kind == "heading":
            level, text = value
            size, colour = sizes.get(level, (10.5, t["ink"]))
            para = document.add_paragraph()
            para.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
            para.paragraph_format.space_after = Pt(6)
            para.paragraph_format.keep_with_next = True
            _inline(para, text, brand, size, colour, bold=True)
        elif kind == "para":
            para = document.add_paragraph()
            para.paragraph_format.space_after = Pt(6)
            for index, line in enumerate(paragraph_lines(value)):
                if index:
                    para.add_run().add_break()
                _inline(para, line, brand)
        elif kind == "list":
            ordered, items = value
            for item in items:
                _inline(document.add_paragraph(style="List Number" if ordered else "List Bullet"), item, brand)
        elif kind == "code":
            para = document.add_paragraph()
            para.paragraph_format.left_indent = Inches(0.15)
            for index, line in enumerate(value):
                if index:
                    para.add_run().add_break()
                run = para.add_run(line)
                run.font.name, run.font.size = MONO, Pt(8.5)
            props = para._p.get_or_add_pPr()
            shading = OxmlElement("w:shd")
            shading.set(qn("w:val"), "clear")
            shading.set(qn("w:fill"), t["surface"].lstrip("#"))
            props.append(shading)
        elif kind == "table" and value:
            _table(document, value, brand, width_twips)
    props = document.core_properties
    props.title = title
    props.author = props.last_modified_by = brand.name
    props.subject = doc_type + (f" for {brand.prepared_for}" if brand.prepared_for else "")
    temp = target.with_name(target.name + ".partial.docx")
    document.save(str(temp))
    temp.replace(target)
    return target


def write_scope_docx(blocks: list[tuple[str, Any]], brand: Brand, title: str, target: Path) -> Path:
    return write_docx(blocks, brand, title, "Scope of Work", target)
