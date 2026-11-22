# Subagent file format

- Location: `.claude/agents/<file>.md` (filename need not match `name`).
- Frontmatter: only `name` and `description` are required. Optional: `tools` (allowlist), `disallowedTools`, `model`, `skills`, `color`, `permissionMode`, `maxTurns`, `memory`, and more.
- `model`: `sonnet`, `opus`, `haiku`, a full model ID, or `inherit`. If omitted, Claude Code falls back through its subagent model order to the main conversation's model.
- `color`: red, blue, green, yellow, purple, orange, pink or cyan.
- `skills`: preloads the full content of each listed skill (first 32 names). Skills with `disable-model-invocation: true` can't be preloaded. Don't put `Skill` in `tools` to preload.
- Claude Code picks up new agent files within seconds; restart if `.claude/agents/` was just created.
- Keep descriptions brief: combined descriptions over ~15,000 tokens trigger a warning.

## Sources
- https://code.claude.com/docs/en/sub-agents
