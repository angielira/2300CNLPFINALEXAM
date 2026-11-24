# 0001. Ship HelpMate as a static site on Netlify, with no server
Date: 2026-11-23
Status: accepted

## Context
- HelpMate is a course final project with a deadline, built by a small team; it must deploy on Netlify (CLAUDE.md).
- Netlify runs Python only at build time. Netlify Functions run TypeScript, JavaScript and Go, not Python (docs/06-netlify-architecture.md).
- The app needs NLTK, spaCy and a trained classifier, which are all Python.
- Users are non-technical; the site must be cheap to run, have no logins and hold no secrets in the page.

## Decision
We will publish HelpMate as plain static files from the `site/` folder (`publish = "site"` in `netlify.toml`).
We will not run any backend server. All Python runs in the build command
(`pip install -r requirements.txt && python -m spacy download en_core_web_sm && python pipeline/build.py`) with
`PYTHON_VERSION = "3.12"`. The only Netlify Function is `netlify/functions/rebuild.mjs`, a scheduled JavaScript
function that POSTs to a build hook; it serves no user requests.

## Consequences
- Positive: one host, CDN delivery, no servers to patch or pay for, no runtime secrets in the page.
- Positive: every deploy is a fixed snapshot; a bad build can be rolled back in the Netlify UI.
- Negative: nothing can be computed per request on our side. Live features must run in the browser (ADR 0003) or be precomputed (ADR 0002).
- Negative: no Content-Security-Policy is set (`netlify.toml` comment), because Pyodide needs WebAssembly and eval from cdn.jsdelivr.net. Only `X-Content-Type-Options` and `Referrer-Policy` are set. Follow-up: security-reviewer to propose a CSP that allows `'wasm-unsafe-eval'` and cdn.jsdelivr.net.
- Follow-up: netlify-engineer keeps `netlify.toml` free of secrets (it currently is).

## Alternatives considered
- **A Python web server (Flask/FastAPI) on another host:** live spaCy would be possible, but it adds a second platform, cost, uptime and secrets. Rejected.
- **Python in Netlify Functions:** not supported by Netlify Functions.
- **JavaScript functions that call an NLP API:** adds a paid third-party service and an API key. Rejected.
