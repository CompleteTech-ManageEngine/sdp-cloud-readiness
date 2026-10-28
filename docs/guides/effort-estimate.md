# Effort estimate (PERT)

The effort estimate sizes the delivery described in the [Scope of Work](scope-of-work.md). Quantities come from the assessment evidence; hours per task are the consultant's three-point assumptions; PERT turns them into expected effort, a standard deviation and confidence figures. The tool renders it with the other [branded deliverables](branded-deliverables.md): an editable Excel workbook plus HTML, PDF, Word and Markdown.

## Where the estimate lives

Write `effort-estimate.json` in the client's assessment folder, next to `scope-of-work.md`. It is engagement content and never belongs in this repository. Copy the file from a previous engagement to start: quantities are recalculated from the new assessment automatically, and only the hours need review.

## Structure

```json
{
  "title": "ServiceDesk Plus Cloud Migration Effort Estimate",
  "status": "Draft for consultant review",
  "contingency_percent": 15,
  "hourly_rate": null,
  "currency": "USD",
  "deliverables": { "D01": "Project controls and portal mapping", "D02": "Approved migration and configuration design" },
  "tasks": [
    { "deliverable": "D02", "task": "Template disposition and design mapping",
      "driver": "inventory_total:incident_templates+service_templates",
      "optimistic": 0.1, "most_likely": 0.2, "pessimistic": 0.4,
      "basis": "Per template: migrate, rebuild or retire." }
  ],
  "assumptions": ["One trial migration cycle and one production cutover."],
  "exclusions": ["Licences and vendor fees."]
}
```

| Field | Meaning |
| --- | --- |
| `deliverables` | Codes and names, matching the Scope of Work (D01–D09) |
| `driver` | Where the quantity comes from (table below) |
| `optimistic`, `most_likely`, `pessimistic` | Hours **per unit** of the driver; must satisfy optimistic ≤ most likely ≤ pessimistic |
| `basis` | Why these hours: shown in every format so reviewers can challenge them |
| `contingency_percent` | Applied to the expected total |
| `hourly_rate` | Optional; gives an indicative cost only. Leave `null` when fees are agreed separately |

| Driver | Quantity |
| --- | --- |
| `fixed` | 1 (a one-off allowance) |
| `portal_count` | Portals assessed |
| `inventory_total:KEY` | Collection total across portals, e.g. `inventory_total:reports`; join keys with `+` |
| `impact_total:RULE` | Affected records of a confirmed impact, e.g. `impact_total:DUPLICATE_SERVICE_TAGS` |
| `impact_portal_count:RULE` | Portals where that impact was confirmed, e.g. `impact_portal_count:WORKFLOW_REBUILD` |
| a number, e.g. `1` | A quantity the read-only assessment cannot supply (interfaces, custom reports); say why in `basis` |

Inventory drivers require complete list collection, as for the Scope of Work; incomplete evidence stops rendering instead of producing a low quantity.

## How PERT is calculated

For each task: expected = quantity × (O + 4M + P) / 6 and standard deviation = quantity × (P − O) / 6, where O, M and P are optimistic, most likely and pessimistic hours per unit. Deliverable and project standard deviations are the square root of the summed variances, treating tasks as independent. The confidence figures add 0.84σ (P80) and 1.28σ (P90) to the expected total. Contingency is applied to the expected total.

## Adjust in the workbook

Open `<Client>-Effort-Estimate.xlsx` from `branded/<Brand>/`:

| Sheet | What you can change |
| --- | --- |
| **Summary** | Contingency % and the optional hourly rate (yellow cells). Deliverable totals, P80, P90 and cost update automatically |
| **Tasks** | Quantity and the three hour values for any task (yellow cells). Add tasks in the spare rows: pick a deliverable code, name the task, enter quantity and hours. The **Check** column flags rows where O ≤ M ≤ P does not hold |
| **Method** | Read-only explanation, assumptions and exclusions |

Every other figure is a formula. Excel recalculates on opening.

To keep the documents (HTML, PDF, Word, Markdown) in step with your changes, carry the final hours back into `effort-estimate.json` and re-run:

```powershell
python .\sdp_cloud_readiness.py --prepared-for "Client Name" --brand-assessment .\sdp-assessments\assessment-YYYYMMDD-HHMMSS-xxxxxx
```

## Review before sharing

`branded-manifest.json` records the totals under `effort_estimate_hours` and the SHA-256 of `effort-estimate.json`. Check the quantities against the assessment, the hours against your delivery experience, and the assumptions against the Scope of Work. The estimate is a planning figure, not a quotation; fees belong in the commercial agreement. Revisit it when D02 fixes the retained reports, interfaces and historical populations.
