## Ratings loop

HelpMate gets better every time it is rebuilt, because the people who use it rate the help they get.

1. **Rate.** Under each answer there is a small form: 1 to 5 stars, an optional comment, and the question, category and format (See it, Hear it, Try it, Read it). It is a Netlify Form named `rating` (spam is blocked with a hidden honeypot field). Please tell users not to type personal details.
2. **Collect.** At build time `pipeline/feedback.py` reads the verified submissions through the Netlify API (100 per page, all pages). Email addresses and phone numbers are masked before anything else happens.
3. **Score.** NLTK VADER reads each comment (positive, neutral or negative). Stars and comment mood are combined and smoothed so one rating cannot swing a result: `score = (5*0.6 + n*raw) / (5 + n)`.
4. **Re-rank.** For each category, the formats are listed best first (`format_rank` in `answers.json`). Formats with 3 or more ratings averaging under 2.5 stars are flagged on the Insights page.
5. **Retrain.** Questions from ratings of 4 or 5 stars are added to the training data for the neural network.
6. **Publish.** `site/data/ratings_summary.json` holds only totals and averages. No comments or questions are published.

### Set it up on Netlify
- Turn on **Forms -> Enable form detection**; it applies from the next deploy. The form must exist as static HTML in `site/index.html`.
- Create a personal access token (User settings -> Applications) and save it as `NETLIFY_API_TOKEN` in **Project configuration -> Environment variables**. `SITE_ID` is set by Netlify.
- Create a build hook (**Build & deploy -> Continuous deployment -> Build hooks**, branch `main`) and save its URL as `BUILD_HOOK_URL`. The optional scheduled function `netlify/functions/rebuild.mjs` posts to it once a day so new ratings are picked up.
- Treat the token and the hook URL as secrets. Never commit them.

### Offline and local builds
Without `NETLIFY_API_TOKEN`, the build uses `data/feedback_sample.json` (fake ratings, marked `sample`). They show up in the Insights charts but are never used to train the model. `HELPMATE_FEEDBACK_FILE=path.json` reads a different file. If nltk is not installed, comment sentiment is skipped and the sentiment counts are `null`.

### Privacy
Netlify stores submissions with the form. Export and delete old ones from the Forms tab from time to time.
