# HelpMate security review

Reviewer: Kai (security-reviewer). Date: 2026-11-23.
Checklist: `.claude/skills/security-review/SKILL.md`. Sources: `knowledge/security-reviewer/`.

## Verdict

**No API keys, tokens, build-hook URLs or private data are exposed** in the working tree, the full git history (all branches), the built `site/` folder, the client JavaScript or the live site's JS and JSON files I checked. Nothing needs to be rotated.

The rest of this report covers hardening and privacy improvements. None of them is a leak.

## Scope

- Working tree of `/home/claude/2300cnlpfinalexam`, including untracked files (agents, skills, docs) and ignored build output (`site/data/`, `site/py/`).
- Git history: `git log -p --all`. There are 14 commits on `main` / `origin/main`, no other branches and no stashes.
- Built site: `site/*.html`, `site/js/*.js`, `site/data/*.json`.
- Build and function code: `pipeline/build.py`, `pipeline/feedback.py`, `netlify/functions/rebuild.mjs`, `netlify.toml`.
- Live site https://helpmate2300nlp.netlify.app: I fetched `/js/brain-worker.js` and `/data/ratings_summary.json`. I could not read the live response headers because the sandbox proxy blocks `curl` to that host (HTTP 403). The headers check is open (see R1).

## Method

1. **Strong secret patterns** in the tree and the history. I used one regex for Netlify PATs (`nfp_…`), build-hook URLs with an id (`api.netlify.com/build_hooks/<hex>`), PEM private keys, AWS (`AKIA…`), GitHub (`ghp_`, `github_pat_`), OpenAI/Anthropic (`sk-`, `sk-ant-`), Google (`AIza…`), Slack (`xox?-`) and JWTs (`eyJ….…`). Result: **0 hits** in the tree and 0 in the history.
2. **Keyword assignments** (`api_key|token|secret|password = <8+ chars>`) on added lines in the history. I redacted values while scanning. There were 3 hits, all harmless: a log message in `build.py`, a regex constant `_TOKEN` in NLTK code, and the fake test values `SECRET-TOKEN-123/456` in `tests/test_feedback.py`.
3. **Sensitive file names** ever committed (`.env`, `*.pem`, `*.key`, `id_rsa`, `credentials`, `.netrc`, `*.p12`): none. One file was ever deleted, a PNG screenshot.
4. **High-entropy strings** of 40+ characters added in the history: all are test function names, markdown rules or URL slugs. There are no UUIDs and no 24-character hex ids (the build-hook id format).
5. **Emails and phone numbers** in the history: only fictional addresses on reserved or test domains (`sam@example.com` in a lesson, `jo.smith@example.com`, `jo@x.org`, `+1 (555) 123-4567` in a PII-masking test) and the commit metadata (see F5).
6. **Built site** grep for `nfp_`, `build_hooks`, `NETLIFY_API_TOKEN`, `SITE_ID`, `BUILD_HOOK`, `api.netlify.com`, `PRIVATE KEY` and local paths (`/home/`, `/opt/build`). There are no secret hits. The only "password" hits are lesson and answer text such as "Never share your password".
7. **Environment variable reads**: `grep process.env|os.environ|getenv`.
8. **DOM sinks**: grep `site/js` for `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval(` and `new Function`.
9. **Tests**: `python3 -m pytest -q` passes after the fixes (163 passed, 24 skipped; the skipped tests are browser tests that need Playwright).

## Findings

| # | Check | Severity | Location | Result | Status / fix owner |
|---|---|---|---|---|---|
| F1 | Secrets in working tree | none | whole tree | Pass. No keys or tokens. Docs use placeholders such as `build_hooks/<id>`. | Done |
| F2 | Secrets in git history | none | all 14 commits | Pass. No secret was ever committed, so there is nothing to rotate. | Done |
| F3 | Secrets in built site and client JS | none | `site/`, live `/js/brain-worker.js` | Pass | Done |
| F4 | Env vars only read on the build or function side | none | `pipeline/feedback.py:114-115`, `pipeline/build.py:191` (only checks whether the token is set), `netlify/functions/rebuild.mjs:4` | Pass. The token is sent only in an `Authorization` header and is never logged. Error messages print only the HTTP status or exception type. `rebuild.mjs` logs the status, not the URL. Nothing is injected into `site/`. `netlify.toml` has no secret values and no `SECRETS_SCAN_*` overrides. | Done |
| F5 | Personal data in git metadata | Info | commit author field | The owner's personal email is the commit author. This is normal and public on GitHub, but it can be hidden. | Owner choice (R5) |
| F6 | Rating form privacy notice | Low | `site/index.html` rating section | The form asks for no name or email, and the honeypot is present. However, the notice did not say that the user's **question** is sent along with the rating (hidden field `question`). | **Fixed**: the notice now says what is sent. Owner: frontend-engineer to keep it. |
| F7 | `ratings_summary.json` free text | none | `pipeline/feedback.py` `summarize()`, live file | Pass. Aggregates only: counts, averages, ranks and flags. No comments or questions. The live file has `total: 0` and no text. | Done |
| F8 | Feedback PII masking | Low | `pipeline/feedback.py` `mask_pii` | Emails and phone numbers are masked, and comments and questions are cut to 500 and 300 characters. Names, street addresses and account numbers are **not** masked. | v2 (R3). Owner: feedback-loop-engineer |
| F9 | Rated questions reach public files indirectly | Low | `nlp/classifier.py` (`min_df=1`, `max_features=2000`), `site/data/model.json` `vocabulary`, `nltk_stats.json` | Well-rated real questions (4 stars or more) are added to training. The vocabulary has only 642 terms, below the 2000 cap, so every stemmed word or bigram from such a question (for example a surname) would be published in `model.json`. No raw sentences are published. `nltk_stats` shows only top-N counts, so a one-off word is unlikely to appear there. Today there are 0 real ratings, so nothing has leaked. | v2 (R3). Owner: ml-engineer + feedback-loop-engineer |
| F10 | Seed and sample data | none | `data/seed_questions.csv`, `data/feedback_sample.json`, `data/spacy_gold.jsonl` | Pass. Invented text with no real emails, phones or URLs. The sample is clearly marked FAKE and is excluded from training. | Done |
| F11 | CDN pinning | none | `site/js/brain-worker.js:7` | Pass. Pyodide is pinned to the exact version `v314.0.8` on jsDelivr, both in the repo and live. | Done |
| F12 | SRI on third-party code | Low | `brain-worker.js` (ES `import`), Google Fonts `<link>` | No SRI. A static `import` cannot carry an `integrity` attribute. Pyodide then fetches its own `.wasm`, stdlib and packages, so SRI on one file would not cover them. Google Fonts CSS varies by browser, so SRI on it is not feasible. | Accepted risk. v2 (R2). Owner: pyodide-engineer |
| F13 | Security headers | Medium (before fix) | `netlify.toml` | Only `X-Content-Type-Options` and `Referrer-Policy` were set. There was no frame protection and no CSP. | **Partly fixed**: added `X-Frame-Options: DENY` and `Permissions-Policy: camera=(), microphone=(), geolocation=()`. The CSP is proposed below but **not** added. Owner: netlify-engineer |
| F14 | User text in the DOM | none | `site/js/*.js` | Pass. The only `innerHTML` is in `dom.js` `icon()`, and it uses constant SVG strings. The question is shown with `textContent` (`app.js:88`), and `el()` sets text with `textContent`/`createTextNode`. There is no `eval` or `new Function`. User text goes to Pyodide as a function argument, never formatted into Python code. All 60 `target="_blank"` links have `rel` noopener. | Done |
| F15 | `.gitignore` gaps | Low | `.gitignore` | Only `.env` was covered. `.env.local`, `*.pem`, `*.key`, `.netlify/` (Netlify CLI state with the site id), `.claude/settings.local.json`, `node_modules/` and `.pytest_cache/` were not. | **Fixed** |
| F16 | Scheduled rebuild function | Info | `netlify/functions/rebuild.mjs` | It reads `BUILD_HOOK_URL` from env and is scheduled `@daily`. My understanding (not confirmed in my notes) is that Netlify scheduled functions cannot be called by URL on published deploys, so the public cannot trigger extra builds through it. | Confirm (R4) |

## Fixes made (not committed)

1. **`.gitignore`**: added `.env.*` (with `!.env.example`), `*.pem`, `*.key`, `.netlify/`, `.claude/settings.local.json`, `node_modules/` and `.pytest_cache/`.
2. **`netlify.toml`** `[[headers]] for = "/*"`: added `X-Frame-Options = "DENY"` and `Permissions-Policy = "camera=(), microphone=(), geolocation=()"`. HelpMate uses no frames, camera, microphone or location. "Hear it" uses `speechSynthesis`, which needs no permission. The file still parses as valid TOML.
3. **`site/index.html`** rating privacy text now reads: "Your stars, your comment and the question you asked are sent together. We never ask for your name or email, so please don't include personal details. …"
4. Tests: `python3 -m pytest -q` gives 163 passed and 24 skipped.

## Proposed Content-Security-Policy (not applied)

I did not add this because it cannot be tested against the CDN from here. Try it first as `Content-Security-Policy-Report-Only` on a deploy preview, test the live box, the worker, the Insights page and the rating POST, then switch it to enforcing.

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'wasm-unsafe-eval'; worker-src 'self'; connect-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
```

Notes:
- `'wasm-unsafe-eval'` is for Pyodide's WebAssembly. If the browser console shows that Pyodide needs `'unsafe-eval'` (some Pyodide JS-to-Python glue has used `new Function`), add it only with a written reason.
- There are no inline `<script>` or `style="…"` attributes in the HTML. JS changes only CSS custom properties via `style.setProperty`, which CSP allows. So no `'unsafe-inline'` is needed.
- `img-src data:` covers the SVG data-URIs in `app.css`.
- `connect-src 'self'` covers the `site/data`, `nltk_data` and `py` fetches and the Netlify Forms POST to `/`.

## Recommendations for v2

- **R1** Check the live headers from a normal network: `curl -sI https://helpmate2300nlp.netlify.app/` should show `X-Frame-Options` and `Permissions-Policy` after the next deploy. Then roll out the CSP above (report-only first).
- **R2** Self-host the pinned Pyodide files (or a trimmed set) in `site/` so they are served from `'self'`. That removes the jsDelivr trust and lets you drop it from the CSP. Alternatively, keep the exact version pin and record the accepted risk. Self-host Nunito/Fredoka too (removes Google Fonts and the request that shares the visitor's IP with Google).
- **R3** Before real ratings grow, stop rated-question words from showing up in `model.json`. Any one of these works: use `min_df=2` (or "a term must also appear in seed or ticket data") for feedback-only terms; mask more PII (spaCy `PERSON`/`GPE` at build time, long digit runs and street patterns); or train only on questions whose tokens are already in the seed vocabulary.
- **R4** Confirm in Netlify's docs that scheduled functions are not URL-invokable in production. Keep `BUILD_HOOK_URL` and `NETLIFY_API_TOKEN` marked "Contains secret values", scoped to Builds/Functions only. Use a token with the least privilege available, and rotate it each term.
- **R5** Optionally, set the GitHub "Keep my email address private" option and use the `noreply` address for future commits.
- **R6** Add a pre-commit or CI secret scan (for example `detect-secrets` or gitleaks) and turn on GitHub secret scanning and push protection on the public repo.
- **R7** Knowledge gap: my notes cover `X-Frame-Options` and CSP but have no sourced note on `Permissions-Policy` or on scheduled-function URL access. Ask the meta-agent (Forge) to add both to `knowledge/security-reviewer/`.

## Next steps for other agents

- netlify-engineer (Nimbus): deploy, verify the new headers live (R1) and own the CSP trial.
- feedback-loop-engineer (Echo) + ml-engineer (Synapse): R3.
- pyodide-engineer (Pip): R2 and testing the CSP against Pyodide.
- meta-agent (Forge): R7.
