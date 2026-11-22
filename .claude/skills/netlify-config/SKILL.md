---
name: netlify-config
description: "Write and fix netlify.toml for HelpMate's Python build and static publish folder. Use when configuring or debugging deploys."
---

# netlify-config

Used by: build-pipeline-engineer, netlify-engineer

## Template
```toml
[build]
  command = "pip install -r requirements.txt && python -m spacy download en_core_web_sm && python pipeline/build.py"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"
```
- `netlify.toml` overrides matching settings in the Netlify UI.
- Do not put secrets in `netlify.toml`; set them in the UI (environment variables).
