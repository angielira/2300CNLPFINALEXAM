---
name: build-hooks
description: "Trigger HelpMate rebuilds with a Netlify build hook, by hand or on a schedule. Use when wiring the self-improvement loop."
---

# build-hooks

Used by: feedback-loop-engineer, netlify-engineer

## Steps
1. Netlify: Project configuration -> Build & deploy -> Continuous deployment -> Build hooks -> Add build hook (branch `main`).
2. Trigger: `curl -X POST -d '{}' https://api.netlify.com/build_hooks/<id>`.
3. Schedule (optional): a JS scheduled function or a GitHub Actions cron that POSTs the hook.
- Treat the hook URL as a secret: store it as an env var / repository secret.
