# HelpMate deploy steps (Netlify)

Owner: Nimbus (netlify-engineer). Settings come from `netlify.toml` at the repo root.

## What Netlify builds
- Command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm && python pipeline/build.py`
- Python: 3.12 (`PYTHON_VERSION` in `netlify.toml`)
- Publish folder: `site`
- Scheduled rebuild (optional): `netlify/functions/rebuild.mjs`, JavaScript only

## One-time setup

1. **Import the repo.** In Netlify: Add new project -> Import an existing project -> pick the GitHub repo.
2. **Check the settings come from the file.** On the build settings screen, the build command, publish directory and Python version should match `netlify.toml`. Do not type different values in the UI; the file wins.
3. **Enable form detection.** Site configuration -> Forms -> Form detection -> Enable form detection. It applies from the next deploy. Then deploy again.
4. **Set environment variables (optional, only if you want ratings to feed the rebuild).** Site configuration -> Environment variables. Add these as secrets. Never put them in the repo:
   - `NETLIFY_API_TOKEN`: a personal access token from your Netlify user settings (Applications -> Personal access tokens). Used to read rating submissions at build time.
   - `SITE_ID`: shown in Site configuration -> General -> Site details. Netlify may set this for you; check first.
   - `BUILD_HOOK_URL`: the URL from step 5. Used only by `rebuild.mjs`.
5. **Create a build hook.** Site configuration -> Build & deploy -> Continuous deployment -> Build hooks -> Add build hook. Name it "Ratings rebuild", branch `main`. Copy the URL and store it as `BUILD_HOOK_URL` (step 4). Treat it like a password.
6. **Trigger a test rebuild.** Either click the build hook URL once, or run `curl -X POST -d '{}' "$BUILD_HOOK_URL"` on your own computer with the variable set. Do not paste the URL into chat or into a file.

## Check the first deploy
- Open the deploy log. Look for the lines from `pipeline/build.py` and the NLTK download lines.
- Open `/data/` files on the live site (for example `/data/answers.json`). They should load.
- Submit one test rating through the site form, then check Forms -> Submissions in Netlify.

## If the build fails
Copy the first red error line from the deploy log and send it to Nimbus (netlify-engineer). Common causes and minimal fixes:

| Error in log | Likely cause | Minimal fix |
|---|---|---|
| `No matching distribution found for spacy` or a Python version error | Python version not 3.12 | Check `PYTHON_VERSION = "3.12"` in `netlify.toml` |
| `Can't find model 'en_core_web_sm'` | spaCy model step did not run | Check the build command still includes `python -m spacy download en_core_web_sm` |
| `LookupError` for stopwords, vader or wordnet | NLTK data download failed | Re-run the deploy once; if it repeats, the pipeline needs a fallback (build-pipeline-engineer) |
| `ModuleNotFoundError` for `nlp` or `pipeline` | Missing `__init__.py` or wrong working folder | Check that the build runs from the repo root |
| `--allow-missing is refused` | Local-only flag was used on Netlify | Remove the flag from the build command; it is only for local runs |
| Publish directory `site` not found | `site/` was not created by the build | Check `pipeline/build.py` writes to `site/` |
| Model file too large | `site/data/model.json` over the size limit | Lower `max_features` to 1500 (see plan section 8) |

Rollback: in Netlify -> Deploys, click an older successful deploy and choose Publish deploy. The site goes back to that version at once.

## Notes
- Netlify Forms (ratings) only work after form detection is on and the site has deployed with the hidden static form in `site/index.html`.
- Pyodide loads from cdn.jsdelivr.net. There is no Content-Security-Policy header, so nothing blocks it. If a CSP is added later, allow `'wasm-unsafe-eval'`, `'unsafe-eval'`, `cdn.jsdelivr.net`, `fonts.googleapis.com` and `fonts.gstatic.com`.

## Sources
- File-based configuration: https://docs.netlify.com/build/configure-builds/file-based-configuration/
- Python versions: https://www.netlify.com/blog/announcing-configurable-python-versions-in-netlify-builds
- Forms setup: https://docs.netlify.com/manage/forms/setup
- Build hooks: https://docs.netlify.com/build/configure-builds/build-hooks/
