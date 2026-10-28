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


def _h(value: float) -> str:
    return f"{value:,.1f}"


def _unit(value: float) -> str:
    return f"{value:g}"


DRIVER_LABELS = {
    "fixed": "Fixed", "portal_count": "Portals", "manual": "Manual quantity",
}


def driver_label(driver: str) -> str:
    if driver in DRIVER_LABELS:
        return DRIVER_LABELS[driver]
    name, _, arg = driver.partition(":")
    pretty = arg.replace("+", " + ").replace("_", " ").lower()
    return {"inventory_total": f"Inventory: {pretty}", "impact_total": f"Affected: {pretty}",
            "impact_portal_count": f"Portals with: {pretty}"}.get(name, driver)


def markdown(estimate: Estimate, brand: Brand, data: Mapping[str, Any]) -> str:
    totals = estimate.totals()
    figures = Figures(data, brand)
    client = brand.prepared_for or "the client"
    lines = [f"# {estimate.title}", "",
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
              "optimistic (O), most likely (M) and pessimistic (P). PERT gives each task an expected effort of quantity × (O + 4M + P) / 6 "
              "and a standard deviation of quantity × (P − O) / 6. The project standard deviation is the square root of the summed task "
              "variances, treating tasks as independent; the confidence figures add 0.84σ (P80) and 1.28σ (P90) to the expected total. "
              "The companion workbook recalculates every figure when a quantity or task time is changed.", "", "<!-- pagebreak -->", "",
              "## Task estimates", ""]
    for code, name in estimate.deliverables.items():
        group = estimate.group(code)
        if not group:
            continue
        lines += [f"### {code} {name}", "",
                  "| Task | Quantity basis | Qty | O h/unit | M h/unit | P h/unit | Expected h | Basis |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        lines += [f"| {t.task} | {driver_label(t.driver)} | {t.quantity:,.0f} | {_unit(t.optimistic)} | {_unit(t.most_likely)} | "
                  f"{_unit(t.pessimistic)} | {_h(t.expected)} | {t.basis} |" for t in group]
        lines.append("")
    if estimate.assumptions:
        lines += ["## Assumptions", ""] + [f"- {a}" for a in estimate.assumptions] + [""]
    if estimate.exclusions:
        lines += ["## Not included", ""] + [f"- {a}" for a in estimate.exclusions] + [""]
    lines += ["## Use of this estimate", "",
              "Hours are planning estimates derived from the assessment evidence and the stated assumptions. They are not a quotation; "
              "fees and payment terms belong in the commercial agreement. Revisit the estimate when D02 fixes the retained reports, "
              "interfaces and historical populations."]
    return "\n".join(lines) + "\n"
