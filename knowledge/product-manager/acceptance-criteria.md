# Acceptance criteria

- Definition: "predefined requirements and conditions that a product or task must meet to be marked as complete and accepted by the user". They are testable statements about the final outcome, not the steps to get there.
- Good criteria are:
  - **Clear and concise:** plain language that every stakeholder reads the same way.
  - **Testable:** each one is "objectively verifiable".
  - **Outcome-focused:** "Describe the result, not the recipe."
  - **Measurable:** put a number on it where you can.
  - **Independent:** each can be tested on its own.
- Format in the source: bulleted, checklist-style statements. The source does not cover Given/When/Then.
- Who writes them: a joint effort. The product owner starts, the developers check that each one is feasible and testable, and the Scrum master facilitates if there is one.
- When: during backlog refinement or sprint planning, before development starts. Review and refine them as understanding grows.
- **Acceptance criteria are not the Definition of Done.** Acceptance criteria cover what one story must do. The "DoD establishes a broader set of quality standards for all development work", including code quality and documentation.

## HelpMate example (story: hear the steps)
- Pressing "Hear it" reads every step aloud with `speechSynthesis`.
- The button is at least 44 x 44 px and works with the keyboard.
- If the browser has no speech support, a plain message says so and offers "Read it".

## Sources
- https://www.atlassian.com/work-management/project-management/acceptance-criteria
- https://www.atlassian.com/agile/project-management/user-stories
