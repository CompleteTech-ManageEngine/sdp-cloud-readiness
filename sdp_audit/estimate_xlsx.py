"""Editable branded PERT effort-estimate workbook (requires openpyxl).

Yellow cells are inputs: quantity and optimistic / most likely / pessimistic
hours per unit on the Tasks sheet, contingency and an optional hourly rate on
the Summary sheet. Every other figure is an Excel formula, so changing a task
time, adding a task in a spare row, or changing contingency recalculates the
expected hours, standard deviations, deliverable totals and P80/P90 figures.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import PageSetupProperties

from .branded_xlsx import _Style, _add_company, _fill, _header_footer
from .branding import Brand
from .effort_estimate import Z80, Z90, Estimate, driver_label

INPUT = "FFF2CC"  # yellow input cells: a semantic convention, not a brand colour
SPARE_ROWS = 25
TASK_HEADER = ("Deliverable", "Task", "Quantity basis", "Quantity", "Optimistic h/unit", "Most likely h/unit",
               "Pessimistic h/unit", "Expected h/unit (PERT)", "Optimistic h", "Most likely h", "Pessimistic h",
               "Expected h (PERT)", "Std. deviation h", "Variance", "Check", "Basis")
TASK_WIDTHS = (12, 46, 26, 10, 11, 11, 11, 13, 11, 11, 11, 13, 12, 10, 18, 60)


def _band(ws, s: _Style, brand: Brand, title: str, subtitle: str, last_col: int) -> int:
    for row, height in {1: 12, 2: 44, 3: 8, 4: 28, 5: 18, 6: 10}.items():
        ws.row_dimensions[row].height = height
        for col in range(1, last_col + 1):
            ws.cell(row=row, column=col).fill = _fill(s.band)
    if brand.logo:
        logo = XLImage(BytesIO(brand.logo))
        width, height = brand.logo_size
        logo.height = 42
        logo.width = round(42 * width / height) if height else 126
        ws.add_image(logo, "B2")
    else:
        ws.cell(row=2, column=2, value=brand.name).font = s.font(16, s.band_ink, bold=True)
    if brand.prepared_for:
        tag = ws.cell(row=2, column=last_col - 1, value=brand.prepared_for.upper())
        tag.font = s.font(9, s.accent_2, bold=True)
        tag.alignment = Alignment(horizontal="right", vertical="center")
    ws.cell(row=4, column=2, value=title).font = s.font(18, s.band_ink, bold=True)
    ws.cell(row=5, column=2, value=subtitle).font = s.font(10, s.accent_2)
    ws.row_dimensions[7].height = 4
    split = max(2, round(last_col * 0.38))
    for col in range(1, last_col + 1):
        ws.cell(row=7, column=col).fill = _fill(s.accent if col <= split else s.accent_2)
    return 9


def _input(cell, s: _Style, number_format: str = "0.00") -> None:
    cell.fill = _fill(INPUT)
    cell.border = s.cell_border
    cell.number_format = number_format
    cell.font = s.font(10, s.ink)


def _tasks_sheet(wb, s: _Style, brand: Brand, estimate: Estimate) -> tuple[str, int, int]:
    ws = wb.create_sheet("Tasks")
    ws.sheet_properties.tabColor = s.accent
    last_col = len(TASK_HEADER)
    start = _band(ws, s, brand, "Effort estimate — tasks (PERT)",
                  "Yellow cells are inputs. Add tasks in the spare rows; totals update automatically.", last_col)
    for index, width in enumerate(TASK_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    header = start
    for col, name in enumerate(TASK_HEADER, start=1):
        cell = ws.cell(row=header, column=col, value=name)
        cell.font, cell.fill, cell.border = s.font(9.5, s.band_ink, bold=True), _fill(s.band), s.header_border
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center" if 4 <= col <= 14 else "left")
    ws.row_dimensions[header].height = 32
    first = header + 1
    last = first + len(estimate.tasks) + SPARE_ROWS - 1
    tasks = list(estimate.tasks) + [None] * SPARE_ROWS
    for offset, task in enumerate(tasks):
        r = first + offset
        filled = f'OR($D{r}="",$E{r}="",$F{r}="",$G{r}="")'
        values = {
            8: f'=IF({filled},"",($E{r}+4*$F{r}+$G{r})/6)',
            9: f'=IF({filled},"",$D{r}*$E{r})',
            10: f'=IF({filled},"",$D{r}*$F{r})',
            11: f'=IF({filled},"",$D{r}*$G{r})',
            12: f'=IF({filled},"",$D{r}*$H{r})',
            13: f'=IF({filled},"",$D{r}*($G{r}-$E{r})/6)',
            14: f'=IF($M{r}="","",$M{r}^2)',
            15: f'=IF({filled},"",IF(AND($E{r}<=$F{r},$F{r}<=$G{r}),"OK","Check O ≤ M ≤ P"))',
        }
        if task is not None:
            values.update({1: task.deliverable, 2: task.task, 3: driver_label(task.driver), 4: task.quantity,
                           5: task.optimistic, 6: task.most_likely, 7: task.pessimistic, 16: task.basis})
        for col in range(1, last_col + 1):
            cell = ws.cell(row=r, column=col, value=values.get(col))
            cell.border = s.cell_border
            cell.font = s.font(9.5)
            cell.alignment = Alignment(vertical="top", wrap_text=col in (2, 3, 16))
            if col in (4, 5, 6, 7):
                _input(cell, s, "#,##0" if col == 4 else "0.00")
            elif 8 <= col <= 14:
                cell.number_format = "#,##0.0"
                if offset % 2:
                    cell.fill = _fill(s.light)
            elif col in (1, 2, 3, 16) and task is None:
                cell.fill = _fill(INPUT)
    total = last + 1
    ws.cell(row=total, column=2, value="Total").font = s.font(10, s.ink, bold=True)
    for col in range(9, 15):
        letter = get_column_letter(col)
        cell = ws.cell(row=total, column=col, value=f"=SUM({letter}{first}:{letter}{last})")
        cell.font, cell.number_format = s.font(10, s.ink, bold=True), "#,##0.0"
        cell.border = Border(top=Side(style="thin", color=s.ink), bottom=Side(style="double", color=s.ink))
    codes = DataValidation(type="list", formula1='"' + ",".join(estimate.deliverables) + '"', allow_blank=True)
    ws.add_data_validation(codes)
    codes.add(f"A{first}:A{last}")
    ws.conditional_formatting.add(f"O{first}:O{last}", FormulaRule(formula=[f'$O{first}="Check O ≤ M ≤ P"'],
                                                                    fill=_fill("FDE2E1"), font=Font(color="9B1C1C", bold=True)))
    ws.freeze_panes = ws.cell(row=first, column=3)
    ws.auto_filter.ref = f"A{header}:{get_column_letter(last_col)}{last}"
    ws.print_title_rows = f"{header}:{header}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    _header_footer(ws, brand, s, ((brand.prepared_for + " · ") if brand.prepared_for else "") + estimate.title, "Tasks")
    return "Tasks", first, last


def _summary_sheet(wb, s: _Style, brand: Brand, estimate: Estimate, first: int, last: int, baseline: str) -> None:
    ws = wb.active
    ws.title = "Summary"
    ws.sheet_properties.tabColor = s.band
    ws.sheet_view.showGridLines = False
    widths = (3, 12, 44, 14, 14, 14, 16, 16, 3)
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    row = _band(ws, s, brand, estimate.title, baseline, len(widths))
    details = [("Prepared for", brand.prepared_for), ("Prepared by", brand.name), ("Status", estimate.status)]
    for label, value in details:
        if value:
            ws.cell(row=row, column=2, value=label).font = s.font(10, s.muted, bold=True)
            ws.cell(row=row, column=4, value=value).font = s.font(10, s.ink)
            row += 1
    row += 1
    ws.cell(row=row, column=2, value="Inputs").font = s.font(12, s.ink, bold=True)
    row += 1
    ws.cell(row=row, column=2, value="Contingency %").font = s.font(10, s.ink)
    contingency = ws.cell(row=row, column=4, value=estimate.contingency_percent / 100)
    _input(contingency, s, "0%")
    c_ref = f"$D${row}"
    row += 1
    ws.cell(row=row, column=2, value=f"Hourly rate ({estimate.currency}, optional)").font = s.font(10, s.ink)
    rate = ws.cell(row=row, column=4, value=estimate.hourly_rate)
    _input(rate, s, "#,##0.00")
    r_ref = f"$D${row}"
    row += 2

    head = ("Code", "Deliverable", "Optimistic h", "Most likely h", "Pessimistic h", "Expected h (PERT)", "Std. deviation h")
    for col, name in enumerate(head, start=2):
        cell = ws.cell(row=row, column=col, value=name)
        cell.font, cell.fill, cell.border = s.font(9.5, s.band_ink, bold=True), _fill(s.band), s.header_border
        cell.alignment = Alignment(horizontal="left" if col <= 3 else "right", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 28
    row += 1
    rng = lambda col: f"Tasks!${col}${first}:${col}${last}"  # noqa: E731
    top = row
    for index, (code, name) in enumerate(estimate.deliverables.items()):
        ws.cell(row=row, column=2, value=code)
        ws.cell(row=row, column=3, value=name)
        for col, source in zip(range(4, 8), ("I", "J", "K", "L")):
            ws.cell(row=row, column=col, value=f'=SUMIF({rng("A")},$B{row},{rng(source)})')
        ws.cell(row=row, column=8, value=f'=SQRT(SUMIF({rng("A")},$B{row},{rng("N")}))')
        for col in range(2, 9):
            cell = ws.cell(row=row, column=col)
            cell.font, cell.border = s.font(10), s.cell_border
            if col >= 4:
                cell.number_format = "#,##0.0"
            if index % 2:
                cell.fill = _fill(s.light)
        row += 1
    bottom = row - 1
    ws.cell(row=row, column=2, value="Total")
    for col in range(4, 8):
        letter = get_column_letter(col)
        ws.cell(row=row, column=col, value=f"=SUM({letter}{top}:{letter}{bottom})")
    ws.cell(row=row, column=8, value=f'=SQRT(SUM({rng("N")}))')
    for col in range(2, 9):
        cell = ws.cell(row=row, column=col)
        cell.font = s.font(10, s.ink, bold=True)
        cell.number_format = "#,##0.0"
        cell.border = Border(top=Side(style="thin", color=s.ink), bottom=Side(style="double", color=s.ink))
    total_row = row
    unassigned = row + 1
    ws.cell(row=unassigned, column=2,
            value=f'=IF(SUM({rng("L")})-G{total_row}>0.05,"Some task rows use a deliverable code missing from this table","")'
            ).font = s.font(9, "9B1C1C", italic=True)
    row += 3

    ws.cell(row=row, column=2, value="Planning figures").font = s.font(12, s.ink, bold=True)
    row += 1
    e, sd = f"$G${total_row}", f"$H${total_row}"
    planning = [
        ("Expected effort (PERT)", f"={e}", "#,##0.0 \"h\""),
        ("Contingency", f"={e}*{c_ref}", "#,##0.0 \"h\""),
        ("Expected effort with contingency", f"={e}*(1+{c_ref})", "#,##0.0 \"h\""),
        ("80% confidence (P80)", f"={e}+{Z80}*{sd}", "#,##0.0 \"h\""),
        ("90% confidence (P90)", f"={e}+{Z90}*{sd}", "#,##0.0 \"h\""),
        (f"Indicative cost with contingency ({estimate.currency})", f'=IF({r_ref}="","",{e}*(1+{c_ref})*{r_ref})', "#,##0.00"),
    ]
    for label, formula, fmt in planning:
        ws.cell(row=row, column=2, value=label).font = s.font(10, s.ink, bold=label.startswith("Expected effort with"))
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=5)
        cell = ws.cell(row=row, column=6, value=formula)
        cell.number_format, cell.font = fmt, s.font(10, s.ink, bold=label.startswith("Expected effort with"))
        cell.border = s.cell_border
        row += 1
    row += 1
    note = ws.cell(row=row, column=2, value="Planning estimate derived from the assessment evidence and stated assumptions; not a "
                                            "quotation. Fees and payment terms belong in the commercial agreement.")
    note.font, note.alignment = s.font(9, s.muted, italic=True), Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
    ws.row_dimensions[row].height = 28
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    _header_footer(ws, brand, s, ((brand.prepared_for + " · ") if brand.prepared_for else "") + estimate.title, "Summary")


def _method_sheet(wb, s: _Style, brand: Brand, estimate: Estimate) -> None:
    ws = wb.create_sheet("Method")
    ws.sheet_properties.tabColor = s.accent_2
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 3, 120
    row = _band(ws, s, brand, "Method and assumptions", estimate.title, 3)
    sections = [
        ("How the estimate works", [
            "Each task has a quantity (from the assessment evidence, or 1 for a fixed allowance) and three-point hours per unit: "
            "optimistic (O), most likely (M) and pessimistic (P).",
            "PERT expected effort = quantity × (O + 4M + P) / 6. Standard deviation = quantity × (P − O) / 6.",
            "Deliverable and project standard deviations are the square root of the summed task variances (tasks treated as "
            f"independent). P80 = expected + {Z80} × σ; P90 = expected + {Z90} × σ.",
            "Contingency is applied to the expected total. The optional hourly rate gives an indicative cost only.",
            "To adjust: change the yellow cells on Tasks (quantity or hours) or Summary (contingency, rate). To add a task, fill "
            "a spare row on Tasks with a deliverable code, task, quantity and the three hour values.",
        ]),
        ("Assumptions", estimate.assumptions),
        ("Not included", estimate.exclusions),
    ]
    for heading, items in sections:
        if not items:
            continue
        ws.cell(row=row, column=2, value=heading).font = s.font(12, s.ink, bold=True)
        row += 1
        for item in items:
            cell = ws.cell(row=row, column=2, value="• " + item)
            cell.font, cell.alignment = s.font(10), Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[row].height = 15 * max(1, -(-len(item) // 130))
            row += 1
        row += 1


def write_estimate_workbook(estimate: Estimate, brand: Brand, target: Path, baseline: str) -> Path:
    style = _Style(brand)
    wb = openpyxl.Workbook()
    _, first, last = _tasks_sheet(wb, style, brand, estimate)
    _summary_sheet(wb, style, brand, estimate, first, last, baseline)
    _method_sheet(wb, style, brand, estimate)
    wb.move_sheet("Summary", offset=-wb.index(wb["Summary"]))
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    props = wb.properties
    props.title = " · ".join(part for part in (brand.prepared_for, estimate.title) if part)
    props.subject = "PERT effort estimate derived from the ServiceDesk Plus cloud readiness assessment"
    props.creator = props.lastModifiedBy = brand.name
    temp = target.with_name(target.name + ".partial.xlsx")
    wb.save(temp)
    _add_company(temp, brand.name)
    temp.replace(target)
    return target
