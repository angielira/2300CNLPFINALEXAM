# MoSCoW prioritization (DSDM / Agile Business Consortium)

- **Must Have:** the "Minimum Usable SubseT (MUST) of requirements which the project guarantees to deliver". If one is missing, the solution is not worth deploying on the planned date.
- **Should Have:** "Important but not vital." The solution still works without it, though people need a workaround.
- **Could Have:** "Wanted or desirable but less important." Leaving one out matters less. Could Haves are the main contingency pool.
- **Won't Have this time:** requirements the team "has agreed will not be delivered (as part of this timeframe)". Write them down so the scope is clear.

## Effort guidance
- Typically "no more than 60% Must Have effort".
- Typically "around 20% Could Have effort", as contingency.
- Leave Won't Haves out of the effort calculation.

## Tips
- Consider starting with every requirement as a Won't Have and justifying each upgrade.
- For each proposed Must Have, ask "what happens if this requirement is not met?"
- If a workaround exists, it is not a Must Have.
- A Must Have should depend only on other Must Haves.
- Different acceptance criteria of the same requirement can have different priorities.

## HelpMate use
- Version 1 = Must + Should. Version 2 = Could + Won't-this-time, recorded in `docs/requirements.md`.

## Sources
- https://www.agilebusiness.org/dsdm-project-framework/moscow-prioririsation.html
