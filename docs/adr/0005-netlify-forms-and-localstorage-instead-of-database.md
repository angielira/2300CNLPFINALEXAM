# 0005. Use Netlify Forms and localStorage instead of a database
Date: 2026-11-23
Status: accepted

## Context
- HelpMate needs two kinds of state: ratings from all users (to improve the app) and each user's own learning progress.
- There is no server (ADR 0001) and the project rules forbid a database.
- Netlify Forms stores form posts from static sites when the form is in the built HTML and form detection is on (docs/06-netlify-architecture.md).
- Users are anonymous; progress does not need to follow them between devices.

## Decision
We will collect ratings with **Netlify Forms**: a static form in `site/index.html` with `name="rating"`,
`data-netlify="true"` and `netlify-honeypot="bot-field"`, fields `stars`, `comment` (max 500), `question` (max 300),
`category`, `format`, `model_generated_at`. `site/js/rating.js` POSTs it to `/` as `application/x-www-form-urlencoded`.
We will keep progress in **localStorage** under `helpmate.progress.v1` (`site/js/progress.js`), with every read and write in try/catch.
The build reads ratings back through the Netlify API (ADR 0006) and publishes aggregates only (`ratings_summary.json`).

## Consequences
- Positive: no database to run, secure or pay for; spam filtering and a submissions UI come with Netlify.
- Positive: progress works offline, needs no account and never leaves the device.
- Negative: progress is per browser; clearing site data or changing device loses it. Private browsing may refuse writes (caught; a warning is logged).
- Negative: Forms has a metered free allowance; heavy use may need a paid plan.
- Negative: submissions hold free text. The build masks e-mails and phone numbers (`mask_pii` in `pipeline/feedback.py`) and the form asks users not to include personal details, but raw submissions stay in Netlify's Forms storage. Follow-up: security-reviewer to set a retention habit (delete old submissions).
- Follow-up: netlify-engineer must turn on "Enable form detection" in the Netlify UI; it applies from the next deploy.

## Alternatives considered
- **A hosted database (Supabase, Firebase, FaunaDB):** needs API keys in the browser or a server in between. Rejected.
- **Netlify Blobs via a function:** a function plus storage for something Forms already does. Rejected.
- **Cookies for progress:** sent with every request and small. Rejected in favour of localStorage.
