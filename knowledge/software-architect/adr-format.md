# Architecture Decision Records (ADRs)

## What they are
- An ADR "captures a single AD and its rationale". It explains why a choice was made, along with its trade-offs and consequences (adr.github.io).
- An architecture decision is "a software design choice that addresses a significant requirement" (joelparkerhenderson).
- An **architecturally significant requirement** is a requirement, functional or not, that "has a measurable effect on the architecture and quality".
- The **decision log** is "the collection of ADRs created and maintained in a project".

## Nygard format (2011)
1. **Title:** a short noun phrase.
2. **Status:** "proposed" until stakeholders agree, then "accepted". If a decision is reversed, keep the old ADR and mark it "superseded".
3. **Context:** "the forces at play, including technological, political, social, and project local."
4. **Decision:** full sentences in active voice, starting with "We will ...".
5. **Consequences:** "the resulting context, after applying the decision". List both positive and negative effects.
- Keep each one to "one or two pages long".
- Number them "sequentially and monotonically. Numbers will not be reused."
- Nygard stored them at `doc/arch/adr-NNN.md`. HelpMate uses `docs/adr/NNNN-<verb-phrase>.md`.

## Good practice (joelparkerhenderson)
- One ADR = one decision ("Each ADR should be about one AD, not multiple ADs").
- Give the rationale: context, pros and cons, cost and benefit.
- Add timestamps, especially next to costs, schedules and scaling.
- Treat ADRs as immutable. When a decision changes, write a new ADR that supersedes the old one. The same page notes that some teams find dated updates to an existing ADR work better in practice.
- File names: a present-tense imperative verb phrase, lowercase with dashes, `.md` (for example `choose-database.md`).

## Sources
- https://adr.github.io/
- https://github.com/joelparkerhenderson/architecture-decision-record
- https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
