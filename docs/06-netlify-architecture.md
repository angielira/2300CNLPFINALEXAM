# 6. What Netlify can run, and the recommended architecture

## What Netlify can and cannot run

| Capability | Can it run Python? | What HelpMate uses it for |
|---|---|---|
| **Build step** | **Yes.** Any official Python 3 version via `PYTHON_VERSION`, `runtime.txt` or `Pipfile`; pip is included. ([docs](https://docs.netlify.com/build/configure-builds/available-software-at-build-time/)) | Run NLTK, spaCy and train the neural network; write static JSON |
| **Netlify Functions** | **No.** TypeScript, JavaScript and Go only. ([docs](https://docs.netlify.com/functions/build/)) | Optional: a small JS scheduled function to trigger rebuilds |
| **Edge Functions** | No (JavaScript/TypeScript on Deno) | Not needed |
| **The browser (Pyodide)** | **Yes**, Python compiled to WebAssembly; includes NLTK, NumPy, scikit-learn, but **not spaCy**. ([packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)) | Live "Ask HelpMate" box: NLTK + the neural network |
| **Netlify Forms** | n/a | Collect ratings and comments without a server |
| **localStorage** | n/a (browser) | Save each user's learning progress |

**Key finding:** Python runs on Netlify **only at build time**. Anything live must run in the browser, so spaCy's work is done during the build and saved as files.

## Recommended architecture

```
                         BUILD (Netlify, Python 3.12)
  dataset + seed set ──► NLTK (stats, VADER) ──┐
                         spaCy (entities,     ├──► site/data/*.json + model.json
                         problems, tags)       │    + entity patterns + NLTK data
  new ratings (Forms API)► retrain MLP ────────┘
                                   │
                                   ▼  publish site/
                         BROWSER (user)
  question ─► Pyodide: NLTK clean + VADER + MLP ─► category, mood
           ─► JS: match entity patterns, look up answers.json
           ─► 4 formats + 10-step panel (progress in localStorage)
           ─► rating form ─► Netlify Forms
```

## netlify.toml (starting point)

```toml
[build]
  command = "pip install -r requirements.txt && python -m spacy download en_core_web_sm && python pipeline/build.py"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"
```

Setting `PYTHON_VERSION` in `netlify.toml` is the documented way to pick the version. ([Netlify blog](https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds))

## Ratings with Netlify Forms

- Turn on **Forms → Enable form detection** in the Netlify UI; it applies from the next deploy.
- The `<form>` needs `name="rating"` and `data-netlify="true"`. Netlify finds forms by parsing the built HTML, so a form created only by JavaScript also needs a hidden static HTML copy with matching field names.
- AJAX submit: POST URL-encoded data (not JSON) with `Content-Type: application/x-www-form-urlencoded` and a `form-name` field. ([Forms setup](https://docs.netlify.com/manage/forms/setup))
- Free usage is metered; check the Forms usage page for the current allowance. ([usage and billing](https://docs.netlify.com/manage/forms/usage-and-billing/))

## The self-improvement loop

1. Users submit ratings (stars, comment, the question, category shown, format used).
2. A rebuild is triggered by a **build hook** (a URL that starts a deploy when it receives a POST), either by hand, from a small scheduled function, or from a scheduled GitHub Action.
3. The Python build reads new submissions from the Netlify API (`GET https://api.netlify.com/api/v1/sites/{site_id}/submissions`, paginated, 100 per page) using a personal access token stored as an environment variable. ([API blog](https://www.netlify.com/blog/2021/12/17/handling-form-submissions-via-the-netlify-api/))
4. NLTK VADER scores comments; low-rated answers and lessons are flagged and ranked lower; well-rated ones are ranked higher.
5. Questions people asked are added to the training data and the MLP is retrained; accuracy is re-measured and written to `reports/`.
6. The new static files are published. HelpMate improves on each rebuild, not in real time; say this plainly in the report.

**Security:** never put the API token or build-hook URL in the site's code; store them as Netlify environment variables.

## Sources
- Available software at build time: https://docs.netlify.com/build/configure-builds/available-software-at-build-time/
- Configurable Python versions: https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds
- Functions overview: https://docs.netlify.com/functions/build/
- Forms setup: https://docs.netlify.com/manage/forms/setup
- Forms usage and billing: https://docs.netlify.com/manage/forms/usage-and-billing/
- Form submissions via the API: https://www.netlify.com/blog/2021/12/17/handling-form-submissions-via-the-netlify-api/
- Scheduling deploys with build hooks: https://www.netlify.com/blog/how-to-schedule-deploys-with-netlify
- Pyodide packages: https://pyodide.org/en/stable/usage/packages-in-pyodide.html
