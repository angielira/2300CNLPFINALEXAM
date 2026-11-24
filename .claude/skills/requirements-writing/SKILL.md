---
name: requirements-writing
description: "Write HelpMate user stories with testable acceptance criteria and scope them with MoSCoW into version 1 and version 2. Use when defining or prioritizing features."
---

# requirements-writing

Used by: product-manager

## User story
- Template: "As a [persona], I want [goal] so that [reason]."
- One persona per story. Keep it small enough for one sprint, with no implementation details. Group big work into an epic.
- HelpMate personas: nervous first-time user on a phone, busy office worker, older relative who prefers listening, course grader.

## Acceptance criteria (per story)
- 2-6 bullet points. Each one is clear, testable, outcome-focused, measurable where possible and independent.
- Describe the result, not the recipe.
- Always include, where they apply: the library label shown (NLTK / spaCy / Neural network), accessibility (WCAG 2.2, 44 px targets), and that it works on Netlify with no server.
- Keep the Definition of Done separate (tests pass, docs updated, deployed).

## MoSCoW scoping
- Must: without it, version 1 is not worth deploying. Should: important, but a workaround exists. Could: nice to have, the contingency pool. Won't (this time): goes to version 2.
- Aim for no more than 60% Must effort and about 20% Could effort.
- Ask of each Must: "what happens if it is not met?" If there is a workaround, it is not a Must.
- A Must depends only on other Musts.

## Output
- `docs/requirements.md` has two tables:
  - Stories: ID | Story | Priority | Version | Owner agent | Acceptance criteria.
  - Out of scope (Won't this time), with the reason for each.

See `knowledge/product-manager/` for sources.
