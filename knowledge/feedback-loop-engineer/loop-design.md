# HelpMate feedback loop

1. Rating form -> Netlify Forms.
2. Build hook -> rebuild.
3. `pipeline/feedback.py` fetches submissions (token in env var) or uses `data/sample_feedback.json`.
4. VADER scores comments; average stars per answer; low-rated answers flagged, high-rated ranked first.
5. New questions added to training data; classifier retrained and re-evaluated.
6. Output: `site/data/ratings_summary.json`, updated `answers.json` order, `reports/feedback.md`.

## Sources
- docs/06-netlify-architecture.md (this repo)
