---
name: agent-authoring
description: "Write or improve Claude Code subagents, skills and knowledge notes for the HelpMate team. Use when adding an agent, a skill, or missing knowledge."
---

# agent-authoring

Used by: orchestrator, meta-agent

## Subagent file (`.claude/agents/<name>.md`)
- YAML frontmatter: `name` and `description` are required; optional `tools`, `model` (`sonnet`, `opus`, `haiku`, full ID or `inherit`), `skills` (preloaded), `color`.
- The Markdown body is the system prompt.
- Keep descriptions short; they decide when Claude delegates.

## Skill (`.claude/skills/<skill-name>/SKILL.md`)
- Frontmatter starts on line 1; `description` says what it does and when to use it.
- Keep SKILL.md under 500 lines; put long references in sibling files.

## Knowledge note (`knowledge/<agent>/<topic>.md`)
- Real facts from official documentation, with a **Sources** list of links.

See `knowledge/meta-agent/` for the full format notes.
