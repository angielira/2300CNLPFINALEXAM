# 0006. Close the ratings loop through rebuilds, not in real time
Date: 2026-11-23
Status: accepted

## Context
- CLAUDE.md promises that "ratings improve the app on every rebuild".
- Learning (retraining, re-ranking) needs Python, which runs only at build time (ADR 0001, 0002).
- Ratings live in Netlify Forms (ADR 0005) and can be read with the Netlify API using a personal access token.
- The token and the build hook URL are secrets and must not reach `site/`.

## Decision
We will improve HelpMate only when the site rebuilds:
1. `netlify/functions/rebuild.mjs` runs `@daily` and POSTs to `process.env.BUILD_HOOK_URL` (skips if unset). A manual deploy or a push also rebuilds.
2. `pipeline/build.py` step 3 calls `pipeline/feedback.load_feedback()`, which uses `NETLIFY_API_TOKEN` and `SITE_ID` to read `GET /api/v1/sites/{site_id}/forms`, then `GET /api/v1/forms/{id}/submissions?state=verified&per_page=100&page=N` (stops at 200 pages). HTTP errors give a warning and no ratings, never a failed build. Without a token on Netlify the build uses no ratings.
3. `summarize()` scores comments with NLTK VADER (`satisfaction`), computes a smoothed score per category and format, flags poor ones and writes `ratings_summary.json`; `rank_answers` writes `format_rank` into `answers.json`.
4. `training_rows()` adds questions from 4-5 star ratings (valid category, at least 8 characters, deduplicated, fake sample rows excluded) to the training data, and the MLP is retrained and re-measured on the fixed seed test split.

## Consequences
- Positive: no live server; secrets stay in Netlify environment variables; every improvement is a reviewable deploy with new metrics.
- Positive: the test set never changes, so accuracy numbers stay comparable across rebuilds.
- Negative: improvement is delayed by up to a day. The report must say this plainly.
- Negative: **self-training risk.** The `category` field is the category HelpMate showed, so a 5-star rating teaches the model its own prediction. Anyone can also submit 5-star ratings with chosen questions (data poisoning). Mitigations today: honeypot, `state=verified`, length and dedupe filters. Follow-up: feedback-loop-engineer to cap feedback rows per category or require a minimum agreement before training, and nlp-evaluator to watch accuracy per rebuild.
- Negative: each scheduled build uses build minutes and re-downloads NLTK data and the spaCy model.

## Alternatives considered
- **Real-time learning in the browser:** each user would only improve their own copy; nothing is shared. Rejected.
- **A function that retrains on submission:** Functions cannot run Python. Rejected.
- **Netlify outgoing webhook on every submission to the build hook:** faster, but one build per rating wastes build minutes and is easy to abuse. Rejected in favour of a daily schedule.
- **Scheduled GitHub Action calling the build hook:** works too; the Netlify scheduled function keeps everything on one platform.
