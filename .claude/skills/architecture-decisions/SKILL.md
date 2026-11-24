---
name: architecture-decisions
description: "Record HelpMate architecture decisions as short ADRs (context, decision, consequences) and check that changes respect the Netlify static boundary. Use when choosing tech or reviewing a design change."
---

# architecture-decisions

Used by: software-architect, orchestrator

## When to write an ADR
- Any choice that affects the stack, where code runs (build vs browser), data storage, third-party scripts or deployment.
- One decision per ADR.

## File
- `docs/adr/NNNN-<imperative-verb-phrase>.md`, numbered in order and never reused (for example `0001-run-python-only-at-build-time.md`).
- Keep a list of all ADRs in `docs/adr/README.md`.

## Template
```markdown
# NNNN. <Short title>
Date: YYYY-MM-DD
Status: proposed | accepted | superseded by NNNN

## Context
The forces at play: requirements, Netlify limits, team, course deadline.

## Decision
We will ...

## Consequences
Positive, negative and follow-up work (with owner agent).
```
- Keep it to one or two pages. Do not rewrite an accepted ADR. Write a new one that supersedes it.

## Boundary checklist (reject the change if any box fails)
- [ ] Python (NLTK, spaCy, training) runs only in the Netlify build command.
- [ ] spaCy output reaches the browser only as static JSON in `site/data/`.
- [ ] The browser runs only Pyodide (NLTK, NumPy) and JavaScript.
- [ ] No backend server, no database. Ratings use Netlify Forms, progress uses localStorage.
- [ ] No secret is injected into `site/`. Build-time variables stay in the build.
- [ ] Third-party scripts are pinned to an exact version.

See `knowledge/software-architect/` for sources.
