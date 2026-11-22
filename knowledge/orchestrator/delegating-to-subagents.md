# Delegating to subagents (Claude Code)

- Project subagents live in `.claude/agents/*.md`; the frontmatter configures them and the Markdown body is their system prompt.
- Claude decides when to delegate from each agent's `description`.
- Invoke explicitly with `@agent-<name>` (for example `@agent-nltk-expert`) or in natural language ("Use the spacy-expert subagent to ...").
- The @-mention chooses which subagent runs; Claude writes the task prompt it receives, so include paths and done-when checks in your request.
- Skills listed in an agent's `skills` field are preloaded in full at startup.

## Sources
- https://code.claude.com/docs/en/sub-agents
