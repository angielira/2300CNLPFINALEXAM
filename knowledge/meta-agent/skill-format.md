# Skill format

- Location: `.claude/skills/<skill-name>/SKILL.md`; frontmatter must start on line 1.
- `description` (recommended): what it does and when to use it; key use case first. Truncated at 1,536 characters with `when_to_use`.
- Other fields: `name`, `when_to_use`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `context: fork`, `agent`, `paths`.
- Keep SKILL.md under 500 lines; put long reference material in sibling files.
- Don't name a folder `synced`; `anthropic-skills` names are reserved.
- Two ways subagents use skills: a skill with `context: fork` runs in a subagent, or a subagent preloads skills via its `skills` field.

## Sources
- https://code.claude.com/docs/en/skills
