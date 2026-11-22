---
name: charts
description: "Build clear, accessible charts for HelpMate's Insights page and reports. Use when visualizing problems, ratings or model metrics."
---

# charts

Used by: data-viz-expert, nlp-evaluator

## Rules
- One message per chart; the title states the finding.
- Bars for categories (most common problems), lines for trends over time (ratings by week).
- Label axes with units; start bars at zero.
- Add a one-sentence text summary under each chart and a data table fallback.
- Chart.js via CDN is fine: `new Chart(ctx, {type, data: {labels, datasets}, options})`.
