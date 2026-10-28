"""PERT effort estimate for an engagement, driven by assessment evidence.

The estimate is engagement content: ``effort-estimate.json`` in the client's
assessment folder, next to ``scope-of-work.md``. Each task names its SoW
deliverable, a quantity driver taken from the evidence and three-point hours
per unit:

    {"deliverable": "D05", "task": "Report disposition review",
     "driver": "inventory_total:reports", "optimistic": 0.03,
     "most_likely": 0.06, "pessimistic": 0.12, "basis": "why these hours"}

Drivers: ``fixed`` (quantity 1), ``portal_count``, ``inventory_total:KEY``,
``impact_total:RULE``, ``impact_portal_count:RULE``, or a number for a
quantity the evidence cannot supply (state why in ``basis``).

PERT per task: expected = quantity × (O + 4M + P) / 6 and standard deviation
= quantity × (P − O) / 6. The project standard deviation is the square root of
the summed variances (tasks treated as independent); P80 and P90 add 0.8416σ
and 1.2816σ to the expected total. Contingency is applied to the expected
total. Hours are planning figures for the consultant's review, never a quote.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping

from .branding import Brand
from .scope_of_work import Figures

ESTIMATE = "effort-estimate.json"
Z80, Z90 = 0.8416, 1.2816
DELIVERABLE = re.compile(r"D\d{2}\Z")


@dataclass(frozen=True)
class Task:
    deliverable: str
    task: str
    driver: str
    quantity: float
    optimistic: float
    most_likely: float
    pessimistic: float
    basis: str

    @property
    def expected_unit(self) -> float:
        return (self.optimistic + 4 * self.most_likely + self.pessimistic) / 6

    @property
    def expected(self) -> float:
        return self.quantity * self.expected_unit

    @property
    def deviation(self) -> float:
        return self.quantity * (self.pessimistic - self.optimistic) / 6


@dataclass(frozen=True)
class Estimate:
    title: str
    status: str
    deliverables: Mapping[str, str]
    tasks: list[Task]
    contingency_percent: float
    hourly_rate: float | None
    currency: str
    assumptions: list[str]
    exclusions: list[str]

    def group(self, code: str) -> list[Task]:
        return [t for t in self.tasks if t.deliverable == code]

    @property
    def expected(self) -> float:
        return sum(t.expected for t in self.tasks)

    @property
    def deviation(self) -> float:
        return math.sqrt(sum(t.deviation ** 2 for t in self.tasks))

    def totals(self) -> dict[str, float]:
        e, s = self.expected, self.deviation
        return {"optimistic": sum(t.quantity * t.optimistic for t in self.tasks),
                "most_likely": sum(t.quantity * t.most_likely for t in self.tasks),
                "pessimistic": sum(t.quantity * t.pessimistic for t in self.tasks),
                "expected": e, "deviation": s, "p80": e + Z80 * s, "p90": e + Z90 * s,
                "with_contingency": e * (1 + self.contingency_percent / 100)}


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"Effort estimate {label} must be a non-negative number.")
    return float(value)


def load_estimate(path: Path, data: Mapping[str, Any], brand: Brand) -> Estimate:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict) or not isinstance(raw.get("tasks"), list) or not raw["tasks"]:
        raise ValueError("effort-estimate.json needs a non-empty 'tasks' list.")
    deliverables = raw.get("deliverables") or {}
    if not isinstance(deliverables, dict) or not all(DELIVERABLE.fullmatch(k) for k in deliverables):
        raise ValueError("Effort estimate 'deliverables' must map codes like D01 to names.")
    figures = Figures(data, brand)
    tasks = []
    for index, item in enumerate(raw["tasks"], start=1):
        label = f"task {index}"
        if not isinstance(item, dict) or not DELIVERABLE.fullmatch(str(item.get("deliverable", ""))):
            raise ValueError(f"Effort estimate {label} needs a deliverable code like D01.")
        if item["deliverable"] not in deliverables:
            raise ValueError(f"Effort estimate {label} uses {item['deliverable']}, which is not in 'deliverables'.")
        driver = item.get("driver", "fixed")
        quantity = _number(driver, label + " quantity") if not isinstance(driver, str) else float(figures.quantity(driver))
        o, m, p = (_number(item.get(k), f"{label} {k}") for k in ("optimistic", "most_likely", "pessimistic"))
        if not o <= m <= p:
            raise ValueError(f"Effort estimate {label} needs optimistic ≤ most likely ≤ pessimistic.")
        tasks.append(Task(item["deliverable"], str(item.get("task") or label), driver if isinstance(driver, str) else "manual",
                          quantity, o, m, p, str(item.get("basis") or "")))
    rate = raw.get("hourly_rate")
    return Estimate(
        title=str(raw.get("title") or "Effort Estimate"), status=str(raw.get("status") or "Draft"),
        deliverables=deliverables, tasks=tasks,
        contingency_percent=_number(raw.get("contingency_percent", 0), "contingency_percent"),
        hourly_rate=None if rate in (None, "") else _number(rate, "hourly_rate"),
        currency=str(raw.get("currency") or "USD"),
        assumptions=[str(a) for a in raw.get("assumptions", [])], exclusions=[str(a) for a in raw.get("exclusions", [])])


def driver_label(driver: str) -> str:
    """Plain name of a quantity driver, for the workbook's quantity column."""
    name, _, arg = driver.partition(":")
    if name == "inventory_total":
        label = SCOPE_NOUNS.get(arg, arg.replace("+", " and ").replace("_", " "))
        return label[:1].upper() + label[1:]
    return {"fixed": "Fixed allowance", "manual": "Allowance", "portal_count": "Portals",
            "impact_total": "Affected records", "impact_portal_count": "Affected portals"}.get(name, driver)


SCOPE_NOUNS = {
    "incident_templates+service_templates": "templates", "service_templates+incident_templates": "templates",
    "incident_templates": "incident templates", "service_templates": "service templates", "reports": "query reports",
    "support_groups": "support groups", "ci_types": "configuration item types", "technicians": "technician memberships",
}


def scope_label(task: Task) -> str:
    """Plain-language scope for a client reader, e.g. '417 templates' or 'Fixed allowance'."""
    name, _, arg = task.driver.partition(":")
    count = f"{task.quantity:,.0f}"
    if task.driver == "fixed":
        return "Fixed allowance"
    if task.driver == "manual":
        return "Allowance" if task.quantity == 1 else f"{count} (allowance)"
    if name in ("portal_count", "impact_portal_count"):
        return f"{count} portal" + ("" if task.quantity == 1 else "s")
    if name == "inventory_total":
        return f"{count} " + SCOPE_NOUNS.get(arg, arg.replace("+", " and ").replace("_", " "))
    if name == "impact_total":
        return f"{count} affected record" + ("" if task.quantity == 1 else "s")
    return count


def _whole(value: float) -> str:
    return f"{value:,.0f}"


def rounded_parts(values: list[float], total: int) -> list[int]:
    """Round parts to whole hours so they add up to the rounded total (largest-remainder method)."""
    floors = [math.floor(v) for v in values]
    shortfall = total - sum(floors)
    order = sorted(range(len(values)), key=lambda i: values[i] - floors[i], reverse=True)
    for i in order[:max(shortfall, 0)]:
        floors[i] += 1
    return floors


def _range(low: float, high: float) -> str:
    # Word joiners keep "24–144" on one line in narrow table cells.
    return f"{_whole(low)}\u2060\u2013\u2060{_whole(high)}"


def markdown(estimate: Estimate, brand: Brand, data: Mapping[str, Any]) -> str:
    """Client-facing estimate document. The workbook carries the three-point inputs for adjustment."""
    totals = estimate.totals()
    figures = Figures(data, brand)
    client = brand.prepared_for or "the client"
    contingency = f"{estimate.contingency_percent:g}%"
    # Prepared by/for is carried by the brand masthead and Word header, so the text starts with the basis.
    position = ("above the 90% confidence level" if totals["with_contingency"] >= totals["p90"]
                else "above the 80% confidence level" if totals["with_contingency"] >= totals["p80"]
                else "below the 80% confidence level")
    lines = [f"# {estimate.title}", "",
             f"Prepared for {client}, based on the Cloud Readiness Assessment dated {figures.value('assessment_date', None)} "
             f"covering {figures.value('portal_count', None)} portals.", "",
             "## Summary", "",
             f"We estimate the delivery described in the Scope of Work at **{_whole(totals['with_contingency'])} hours**, "
             f"including {contingency} contingency on an expected effort of {_whole(totals['expected'])} hours. "
             f"Allowing for the range of every task, there is an 80% likelihood that the work is completed within "
             f"{_whole(totals['p80'])} hours and a 90% likelihood within {_whole(totals['p90'])} hours; the total estimate "
             f"is {position}.", "",
             "| Deliverable | Estimated hours | Range |", "| --- | --- | --- |"]
    # Displayed figures add up: deliverables to the total, tasks to their deliverable, contingency to the estimate.
    groups = [(code, name, estimate.group(code)) for code, name in estimate.deliverables.items() if estimate.group(code)]
    expected_total = round(totals["expected"])
    shown = dict(zip((code for code, _, _ in groups),
                     rounded_parts([sum(t.expected for t in group) for _, _, group in groups], expected_total)))
    for code, name, group in groups:
        lines.append(f"| {code} {name} | {_whole(shown[code])} | "
                     f"{_range(sum(t.quantity * t.optimistic for t in group), sum(t.quantity * t.pessimistic for t in group))} |")
    estimate_total = round(totals["with_contingency"])
    lines += [f"| **Total** | **{_whole(expected_total)}** | |", "",
              "Ranges are not added together: it is very unlikely that every task reaches its optimistic or pessimistic "
              "estimate at the same time. The confidence levels below give the realistic spread for the whole delivery.", "",
              "| Estimate | Hours |", "| --- | --- |",
              f"| Expected effort | {_whole(expected_total)} |",
              f"| Contingency ({contingency}) | {_whole(estimate_total - expected_total)} |",
              f"| **Total estimate** | **{_whole(estimate_total)}** |",
              f"| 80% confidence | {_whole(totals['p80'])} |", f"| 90% confidence | {_whole(totals['p90'])} |"]
    if estimate.hourly_rate is not None:
        lines.append(f"| Indicative cost at {estimate.currency} {estimate.hourly_rate:,.2f} per hour, including contingency | "
                     f"{estimate.currency} {estimate_total * estimate.hourly_rate:,.0f} |")
    lines += ["", "## How the estimate was prepared", "",
              "Each task is sized from the scope measured in the assessment, such as the number of portals, templates and "
              "query reports, or as a fixed allowance where the scope is confirmed during design. Every task has an optimistic, "
              "a most likely and a pessimistic estimate. These are combined with the PERT (three-point) method, which weights the "
              "most likely value and reflects the uncertainty in each range. Each range runs from the optimistic to the "
              "pessimistic estimate; the confidence levels show the total effort that is unlikely to be exceeded.", "",
              "<!-- pagebreak -->", "", "## Estimate by deliverable", ""]
    for code, name, group in groups:
        task_hours = rounded_parts([t.expected for t in group], shown[code])
        lines += [f"### {code} {name}", "", "| Task | Scope | Estimated hours | Range | Notes |", "| --- | --- | --- | --- | --- |"]
        lines += [f"| {t.task} | {scope_label(t)} | {_whole(hours)} | {_range(t.quantity * t.optimistic, t.quantity * t.pessimistic)} | "
                  f"{t.basis} |" for t, hours in zip(group, task_hours)]
        lines += [f"| **Subtotal** | | **{_whole(shown[code])}** | | |", ""]
    if estimate.assumptions:
        lines += ["## Assumptions", ""] + [f"- {a}" for a in estimate.assumptions] + [""]
    if estimate.exclusions:
        lines += ["## Not included", ""] + [f"- {a}" for a in estimate.exclusions] + [""]
    lines += ["## Basis of this estimate", "",
              "This estimate is based on the Cloud Readiness Assessment and the assumptions above. It will be confirmed once "
              "design (D02) fixes the retained reports, interfaces and historical records, and updated if the confirmed scope "
              "differs. Fees and payment terms are set out in the commercial proposal."]
    return "\n".join(lines) + "\n"


def _h(value: float) -> str:
    return f"{value:,.1f}"


def _unit(value: float) -> str:
    return f"{value:g}"


def detailed_markdown(estimate: Estimate, brand: Brand, data: Mapping[str, Any]) -> str:
    """Detailed working estimate: the full PERT table with per-unit hours, drivers and standard deviations."""
    totals = estimate.totals()
    figures = Figures(data, brand)
    client = brand.prepared_for or "the client"
    lines = [f"# {estimate.title}: detailed working estimate", "",
             f"**Prepared for {client}**  ", f"**Prepared by {brand.name}**  ",
             f"**Status:** {estimate.status}  ",
             f"**Evidence baseline:** Cloud Readiness Assessment dated {figures.value('assessment_date', None)}, "
             f"{figures.value('portal_count', None)} portals", "",
             "## Summary", "",
             f"The expected effort is **{_h(totals['expected'])} hours** (PERT). With {estimate.contingency_percent:g}% contingency "
             f"the planning figure is **{_h(totals['with_contingency'])} hours**. There is an estimated 80% likelihood that "
             f"delivery completes within {_h(totals['p80'])} hours and 90% within {_h(totals['p90'])} hours.", "",
             "| Deliverable | Optimistic | Most likely | Pessimistic | Expected (PERT) | Std. deviation |",
             "| --- | --- | --- | --- | --- | --- |"]
    for code, name in estimate.deliverables.items():
        group = estimate.group(code)
        if not group:
            continue
        lines.append(f"| {code} {name} | {_h(sum(t.quantity * t.optimistic for t in group))} | "
                     f"{_h(sum(t.quantity * t.most_likely for t in group))} | {_h(sum(t.quantity * t.pessimistic for t in group))} | "
                     f"{_h(sum(t.expected for t in group))} | {_h(math.sqrt(sum(t.deviation ** 2 for t in group)))} |")
    lines += [f"| **Total** | **{_h(totals['optimistic'])}** | **{_h(totals['most_likely'])}** | **{_h(totals['pessimistic'])}** | "
              f"**{_h(totals['expected'])}** | **{_h(totals['deviation'])}** |", "",
              "| Planning figure | Hours |", "| --- | --- |",
              f"| Expected (PERT) | {_h(totals['expected'])} |",
              f"| Contingency ({estimate.contingency_percent:g}%) | {_h(totals['with_contingency'] - totals['expected'])} |",
              f"| **Expected with contingency** | **{_h(totals['with_contingency'])}** |",
              f"| 80% confidence (P80) | {_h(totals['p80'])} |", f"| 90% confidence (P90) | {_h(totals['p90'])} |"]
    if estimate.hourly_rate is not None:
        lines.append(f"| Indicative cost at {estimate.currency} {estimate.hourly_rate:,.2f}/hour (with contingency) | "
                     f"{estimate.currency} {totals['with_contingency'] * estimate.hourly_rate:,.2f} |")
    lines += ["", "## Method", "",
              "Each task has a quantity taken from the assessment evidence (or a fixed allowance) and three-point hours per unit: "
              "optimistic (O), most likely (M) and pessimistic (P). PERT gives each task an expected effort of quantity \u00d7 (O + 4M + P) / 6 "
              "and a standard deviation of quantity \u00d7 (P \u2212 O) / 6. The project standard deviation is the square root of the summed "
              "task variances, treating tasks as independent; the confidence figures add 0.84\u03c3 (P80) and 1.28\u03c3 (P90) to the "
              "expected total. The companion workbook recalculates every figure when a quantity or task time is changed.", "",
              "<!-- pagebreak -->", "", "## Task estimates", ""]
    for code, name in estimate.deliverables.items():
        group = estimate.group(code)
        if not group:
            continue
        lines += [f"### {code} {name}", "",
                  "| Task | Quantity basis | Qty | O h/unit | M h/unit | P h/unit | Expected h | Std. dev. h | Basis |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        lines += [f"| {t.task} | {driver_label(t.driver)} | {t.quantity:,.0f} | {_unit(t.optimistic)} | {_unit(t.most_likely)} | "
                  f"{_unit(t.pessimistic)} | {_h(t.expected)} | {_h(t.deviation)} | {t.basis} |" for t in group]
        lines += [f"| **Subtotal** | | | | | | **{_h(sum(t.expected for t in group))}** | "
                  f"**{_h(math.sqrt(sum(t.deviation ** 2 for t in group)))}** | |", ""]
    if estimate.assumptions:
        lines += ["## Assumptions", ""] + [f"- {a}" for a in estimate.assumptions] + [""]
    if estimate.exclusions:
        lines += ["## Not included", ""] + [f"- {a}" for a in estimate.exclusions] + [""]
    lines += ["## Use of this estimate", "",
              "Detailed working estimate for review and adjustment. Hours are planning estimates derived from the assessment "
              "evidence and the stated assumptions, not a quotation. The client-ready estimate presents the same figures without "
              "the per-unit working detail."]
    return "\n".join(lines) + "\n"
