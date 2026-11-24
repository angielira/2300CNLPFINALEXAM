---
name: security-review
description: "Security checklist for HelpMate: scan the repo, git history, built site and client code for secrets; check env vars, PII in forms and logs, CDN pinning/SRI and security headers. Use before every deploy or when config changes."
---

# security-review

Used by: security-reviewer, qa-engineer, netlify-engineer

## 1. Secrets in the working tree
- Grep for likely secrets (adjust as needed):
  `grep -rInE "(api[_-]?key|token|secret|password|nfp_|api\.netlify\.com/build_hooks/)" --exclude-dir=.git --exclude-dir=node_modules .`
- `.env` and similar files are listed in `.gitignore` and are not tracked.
- `netlify.toml` holds no sensitive values. Those belong in the Netlify UI, CLI or API.

## 2. Git history
- `git log -p --all | grep -nE "(nfp_|build_hooks/|token|secret)"`. GitHub secret scanning also checks every branch's history.
- If a secret was ever committed: **rotate or revoke it first**. Rewriting history is optional once the secret is revoked.

## 3. Built site and client code
- After the build, grep `site/` (including `site/data/*.json` and the JS) for the same patterns. Nothing from `NETLIFY_API_TOKEN` or the build-hook URL may appear.
- Netlify secret scanning and smart detection fail the build if they find a secret. Flag any `SECRETS_SCAN_*OMIT*` or `SECRETS_SCAN_ENABLED=false` that has no written reason.

## 4. Environment variables
- Sensitive variables are marked "Contains secret values", with the narrowest scopes and contexts.
- Only non-sensitive values are injected into the site at build time.

## 5. Personal data (forms and logs)
- The rating form asks for no name, email or account details. The honeypot (`netlify-honeypot`) is present.
- Build logs and `site/data/` hold only aggregates or scrubbed text. No raw comments that could identify a person.
- Secrets are never printed in build logs.

## 6. Third-party scripts
- Every CDN URL (for example Pyodide) is pinned to an exact version. Scripts use `integrity="sha384-..."` with `crossorigin="anonymous"` where the file is static.
- Hash: `cat f.js | openssl dgst -sha384 -binary | openssl base64 -A`.

## 7. Security headers (`netlify.toml` [[headers]] for "/*")
- `Content-Security-Policy`: `default-src 'self'`, the pinned CDN in `script-src`/`connect-src`, `'wasm-unsafe-eval'` if Pyodide needs it, no `'unsafe-eval'` or `'unsafe-inline'` without a reason, `object-src 'none'`, `frame-ancestors 'none'`.
- Also `X-Frame-Options: DENY` (shown in the Netlify headers docs). Before adding any other header, ask the meta-agent for a note with a source.
- Check the live headers with `curl -sI https://<site>/`.

## 8. Injection
- User text is inserted with `textContent`, never `innerHTML`.

## Output
- `reports/security.md`: a table with Check | Result (pass/fail) | Evidence | Fix owner. Never paste a real secret value into the report.

See `knowledge/security-reviewer/` for sources.
