---
name: task-planning
description: "Plan HelpMate work as small tasks with an owner, input and output, then track them. Use when starting or re-planning a phase."
---

# task-planning

Used by: orchestrator, meta-agent, product-manager

## Steps
1. Read `docs/README.md`, `docs/expert-roster.md` and `docs/06-netlify-architecture.md`.
2. Write the plan as a numbered list: task, owner agent, inputs, output path, done-when check.
3. Order by dependency: data -> NLP (NLTK, spaCy, classifier) -> content -> build pipeline -> frontend/Pyodide -> Netlify -> QA/evaluation.
4. Delegate one task at a time with the exact paths. After each, verify the output file exists and is valid.
5. Keep a running status in `reports/progress.md`.

## Guardrails
- Python runs on Netlify only at build time. spaCy never runs in the browser.
- No backend server, no database.
