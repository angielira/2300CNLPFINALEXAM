# HelpMate requirements, version 1

> **Note.** These requirements were written by the product manager after the version 1 build started and were checked against what the team built; future versions start from this document.

Owner: Nora (product-manager). Written 2026-11-23. Method: `.claude/skills/requirements-writing`, `knowledge/product-manager/` (user stories, acceptance criteria, MoSCoW).

## 1. Problem statement

Many people get stuck on everyday IT problems: a printer that won't print, an email that won't send, Wi-Fi that drops, a forgotten password. They don't know the right words to search for, help pages are full of jargon, and being stuck makes them anxious or annoyed. They usually wait for a relative or a colleague to fix it for them, so they never learn.

HelpMate lets them describe the problem in their own words and get calm, step-by-step help in the format they choose (See it, Hear it, Try it, Read it). An optional 10-step mini-course helps them understand the topic so they can fix it themselves next time.

## 2. Target users (personas)

| Persona | Who | What they need most |
|---|---|---|
| **Nervous first-time user on a phone** | Not technical, uses a phone, worried about breaking something | Plain words, big buttons, reassurance, short steps |
| **Busy office worker** | Uses a laptop at work, wants a fix fast | A quick, correct answer; a checklist to tick or print |
| **Older relative who prefers listening** | Low vision or low confidence with reading on screen | Steps read aloud, large text, text that stays on screen |
| **Course grader** | Marks the NLP final exam | Clear proof of what NLTK, spaCy and the neural network each do, honest quality numbers, a site that runs on Netlify |

## 3. Goals and non-goals

### Goals (version 1)
1. A non-technical person can type a question in plain words and get help for the right topic in one go, most of the time.
2. HelpMate recognizes the device, app, system or error code mentioned, and notices frustration so it can answer more calmly.
3. Help comes in four formats that the user can switch between freely. HelpMate makes no "learning styles" claim (docs/05).
4. An optional 10-step course per topic, with progress and badges saved on the device.
5. Ratings feed back into the app on every rebuild.
6. Everything runs on Netlify: Python only at build time, Pyodide and JavaScript in the browser, no server, no database (docs/06).
7. Every result says which library made it: NLTK, spaCy, Neural network, or both.
8. WCAG 2.2 AA for the main paths.

### Non-goals (version 1)
- Not a replacement for professional repair or a help desk; no live human help.
- No user accounts, logins or syncing progress between devices.
- No remote control of the user's device and no automatic fixes.
- No real-time learning: the app improves only when the site is rebuilt.
- No languages other than English.
- No storing or publishing what people type (only totals and averages of ratings).

## 4. How the v1 status was checked

| Check | Result |
|---|---|
| Local tests, `python3 -m pytest -q` (2026-11-23, no NLTK/spaCy installed here) | **163 passed, 24 skipped, 0 failed.** The skips need NLTK or spaCy and run on Netlify. |
| Live JSON, fetched from https://helpmate2300nlp.netlify.app on 2026-11-23 | `/data/metrics.json` (tokenizer `nltk_clean_v1`, generated 2026-11-23T03:35:20Z), `/data/nltk_stats.json`, `/data/ratings_summary.json`, `/data/nltk_manifest.json`, home page text |
| Live browser check by the lead, real Chrome, 2026-11-23 | The real Pyodide path on https://helpmate2300nlp.netlify.app (see US-07 evidence). Netlify Forms detection confirmed enabled on the project. |
| Not checked live yet | Real speech audio, a real rating submission and screen reader use. Stories that depend on them say so. |

Live numbers used below (Netlify build, 48 test questions):

| Measure | Value |
|---|---|
| Classifier accuracy / macro F1 | 0.75 / 0.757 |
| Classifier recall, weakest classes | passwords 0.44, video_calls 0.57, wifi 0.60 |
| VADER frustration, all 240 seed rows: precision / recall / F1 | 0.63 / 0.42 / 0.50 |
| VADER frustration, 48 test rows (14 frustrated): precision / recall | 0.67 / 0.29 |
| spaCy entities: precision / recall (tp 149, fp 3, fn 2) | 0.98 / 0.99 |
| spaCy problem extraction: exact / right thing | 0.36 / 0.45 |
| Ratings in `ratings_summary.json` | total **0** |

Status meanings: **Met** = every acceptance criterion is shown by a test, code or a live check. **Partly met** = some criteria are met, or a key criterion could not be verified. **Not met** = the main criterion is not built.

## 5. Stories

Priority: M = Must, S = Should, C = Could. Version: v1 = Must + Should; v2 = Could (per `knowledge/product-manager/moscow-prioritization.md`). Effort: S = 1, M = 2, L = 3 points.

### Epic A: Ask in plain words

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-01 | As a nervous first-time user on a phone, I want to type my problem in my own words so that I don't need to know technical terms. | M | v1 | M | frontend-engineer | 1. One text box with a visible label and a "Help me with this" button.<br>2. Up to 300 characters, with a live count.<br>3. An empty question gives a friendly message, not an error code.<br>4. Works at 360 px wide with no sideways scrolling.<br>5. A note asks people not to type passwords or personal details. | **Met** | `tests/browser/test_app.py::test_ask_printer_shows_cards_with_badges`, `::test_empty_question_shows_friendly_error`, `::test_no_horizontal_overflow_360`; `site/index.html` lines 43-52; live home page shows the box, "0 of 300" and the privacy note. |
| US-02 | As a nervous first-time user, I want example questions I can tap so that I know what to type. | S | v1 | S | frontend-engineer | 1. "Not sure what to type?" shows tappable example questions.<br>2. Tapping one asks it.<br>3. Each chip is at least 44 x 44 px. | **Met** | `site/js/app.js::buildChips` (line 60, from `examples.json`); live home page shows "Tap one"; 44 px rule in `reports/ux-spec.md` line 168, checked by `test_app.py::test_accessibility_basics`. |

### Epic B: Understanding the question

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-03 | As a busy office worker, I want HelpMate to point out the device, app, system or error code I mentioned so that I know it understood me. | M | v1 | M | spacy-expert | 1. "Things you mentioned" lists DEVICE, APP, OS and ERROR_CODE matches, labelled **spaCy**.<br>2. Matching ignores upper/lower case and plurals.<br>3. Entity precision and recall are each at least 0.80 on `data/spacy_gold.jsonl`.<br>4. spaCy runs only at build time; the browser uses the exported `entity_patterns.json`. | **Met** | Live `metrics.json`: precision 0.98, recall 0.99. `tests/test_spacy_features.py::test_entities_devices_apps_os_codes`, `::test_entities_are_case_insensitive_and_plural`, `::test_export_patterns_writes_contract` (skip locally, run on Netlify); `site/js/entities.js`. |
| US-04 | As a busy office worker, I want to see what HelpMate thinks is broken (for example "printer: not print") so that I can check it understood the problem. | S | v1 | M | spacy-expert | 1. For any question, a (thing, problem) pair is shown when one can be found, labelled **spaCy**.<br>2. Exact problem accuracy at least 0.50 on the gold file (best possible about 0.72, `reports/nlp_quality.md` 4.2).<br>3. The right broken thing is found at least 0.60 of the time.<br>4. When nothing is found, a plain message says so. | **Partly met** | Shown only when the typed text exactly matches a precomputed example (`site/js/app.js` lines 165-173), because spaCy cannot run in the browser. Live: exact 0.36, thing 0.45, both below target. Criterion 4 is met (`app.js` line 171). |
| US-05 | As a nervous first-time user, I want HelpMate to notice when I'm frustrated and answer more calmly so that I feel supported. | M | v1 | M | nltk-expert | 1. A frustrated question shows a calm notice and the topic's calm intro, labelled **NLTK**.<br>2. A calm question gets the normal tone.<br>3. Frustration recall at least 0.60 and precision at least 0.60 on the test split.<br>4. Spellings without apostrophes ("wont", "cant") count. | **Partly met** | Criteria 1, 2, 4 met: `test_app.py::test_stubbed_brain_frustrated_printer`, `app.js` lines 125-157, `tests/test_nltk_features.py::test_apostrophe_free_and_crashes`. Criterion 3 not met: live test-split recall **0.29** (precision 0.67); all rows recall 0.42. Live misses include "ink cartridge says empty but i just put a brand new one in!!!". |
| US-06 | As a busy office worker, I want my question sorted into the right topic (one of 8) so that I get the right help first time. | M | v1 | L | ml-engineer | 1. The category card says "This sounds like a ... question", labelled **Neural network**.<br>2. Accuracy at least 0.70 on the held-out test split.<br>3. The browser NumPy model gives the same probabilities as scikit-learn (within 1e-4).<br>4. The shipped model uses the NLTK tokenizer (`nltk_clean_v1`). | **Met** | Live `metrics.json`: accuracy 0.75, macro F1 0.757, tokenizer `nltk_clean_v1`. `tests/test_classifier.py::test_parity_with_sklearn`, `::test_export_schema`. Weak spots: passwords recall 0.44, video_calls 0.57 (48 test questions; ±12 points). |
| US-07 | As a nervous first-time user, I want the live box to work in my browser without installing anything so that I get help straight away. | M | v1 | L | pyodide-engineer | 1. The page loads Pyodide, NLTK and NumPy in a Web Worker and answers with the neural network and NLTK (no "couldn't start" notice).<br>2. The page stays usable while it loads.<br>3. NLTK data and Python files come from the site (`nltk_manifest.json`).<br>4. Build and browser use the same NLTK version (3.9.4).<br>5. No server is called. | **Met** | Criterion 1 verified by the lead on the live site in a real Chrome browser, 2026-11-23. The first classic-worker `importScripts` load failed ("NetworkError ... failed to load"); after switching to a module worker that imports `pyodide.mjs` (`site/js/brain-worker.js` line 7, ADR 0003) the live site loaded Pyodide 314.0.8 with nltk 3.9.4 and numpy 2.4.6. `brain.ready()` took about 12 s. `analyze("I've tried EVERYTHING and my printer STILL won't print!!")` gave printer, 0.999, frustrated via problem_phrase + exclaim. VADER compound -0.8807 for "This is terrible, I hate this stupid laptop" and +0.7906 for "thanks, the wifi works great now". The full UI question "My Outlook email WONT send and I've tried everything!!" showed the NLTK calm notice and the Neural network card "Email 100% sure". Criteria 3, 4, 5: live `nltk_manifest.json` (nltk 3.9.4, stopwords + VADER lexicon, 3 Python files); `tests/test_brain_python_path.py::test_worker_contract_shape`; `tests/test_build_outputs.py::test_browser_files_and_manifest`. Criterion 2: the work runs in a Web Worker (`site/js/brain.js` line 51). |
| US-08 | As a nervous first-time user, I want HelpMate to say "I'm not sure" and let me pick a topic when it can't tell so that I don't get the wrong help. | S | v1 | S | frontend-engineer | 1. Below 0.45 confidence, or with no known words, a plain "I'm not sure yet" message shows 8 topic chips.<br>2. Picking a chip shows that topic's answer.<br>3. No wrong category card is shown as certain. | **Met** | `site/js/app.js` lines 176-187 (`unsureNotice`); `tests/test_brain_python_path.py::test_unsure_when_no_known_words`, `::test_unsure_matches_threshold`; `tests/test_classifier.py::test_unsure_when_no_known_terms`. No browser test clicks a chip (test gap). |
| US-09 | As a nervous first-time user, I want numbered steps (See it) so that I can follow one small step at a time. | M | v1 | M | instructional-designer | 1. Every topic has 4-8 numbered steps, each with a short label and detail.<br>2. Every format of a topic has the same steps in the same order.<br>3. The button text describes what is actually shown. | **Met** | 1, 2: 8 topics x 6 steps; `tests/test_site_json.py::test_answers_cover_every_category_and_format`. 3: the See it button now says "Numbered steps" (`site/index.html` line 109) and no site file promises pictures any more. Pictures for each step are still a v2 item (US-32). |

### Epic C: Help in four formats

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-10 | As an older relative who prefers listening, I want the steps read aloud (Hear it) so that I can keep my eyes on the device. | S | v1 | M | frontend-engineer | 1. Play, Pause and Stop buttons, each at least 44 x 44 px and keyboard usable.<br>2. The text stays on screen while it is read.<br>3. Without speech support, a plain message says so and offers Read it.<br>4. Speech stops when the user switches format. | **Met** | `test_app.py::test_format_buttons_switch_and_hear_controls`; `site/js/speech.js` (text stays on screen, `stopAllSpeech`); `site/js/formats.js` line 29 (no-support message). Real audio has only been checked by design, not by a person on the live site. |
| US-11 | As a busy office worker, I want to tick off steps as I do them (Try it) so that I know where I am. | S | v1 | S | frontend-engineer | 1. One checkbox per step, with a progress bar.<br>2. Ticks are still there after reload.<br>3. When all are ticked, a "well done" message and the "if it still isn't working" note show. | **Met** | `site/js/formats.js` lines 56-74 (checkboxes, progressbar, done message); `site/js/progress.js::setTry/getTry` (localStorage). No automated test for persistence after reload (test gap; `reports/qa.md` checklist item 5). |
| US-12 | As a busy office worker, I want a printable checklist (Read it) so that I can follow it away from the screen. | S | v1 | S | frontend-engineer | 1. A plain checklist with a title.<br>2. A "Print this checklist" button prints only the checklist. | **Met** | `site/js/formats.js` lines 88-92 (`print-only` title, `window.print()`); `test_app.py::test_format_buttons_switch_and_hear_controls` opens Read it. |
| US-13 | As any user, I want to switch between See it, Hear it, Try it and Read it at any time so that I can use what works for me right now. | M | v1 | S | frontend-engineer | 1. Four buttons, one selected at a time (`aria-pressed`), each showing a different panel.<br>2. My last choice is remembered on this device.<br>3. Nothing on the site claims to diagnose a "learning style". | **Met** | `test_app.py::test_format_buttons_switch_and_hear_controls`; `progress.js::setFormatPref`; README "makes no learning styles claim"; docs/05. |
| US-14 | As a busy office worker, I want the format other people rated best to come first so that I start with what usually works. | C | v2 | M | feedback-loop-engineer | 1. `format_rank` per topic comes from ratings (stars + NLTK comment mood, smoothed).<br>2. The app shows formats in that order.<br>3. With no ratings, the default order is used. | **Partly met** | Code and tests exist: `tests/test_feedback.py::test_scores_rank_flags`. Live has 0 ratings, so ranks are the default. Not checked whether the buttons re-order. |

### Epic D: 10-step mini-course

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-15 | As a nervous first-time user, I want an optional 10-step course for my topic so that I understand it and can fix it myself next time. | S | v1 | L | instructional-designer | 1. Each of the 8 topics has exactly 10 steps: one idea, one example, one quick question with 3 choices.<br>2. Feedback after each answer, with a short reason.<br>3. The course opens and closes without losing the answer; Escape closes it.<br>4. Step tags are labelled **spaCy**. | **Met** | `tests/test_site_json.py::test_lessons_have_ten_steps_each`; `test_app.py::test_course_tab_open_close_and_progress_persists`, `::test_tabs_keyboard_arrows`; `site/js/panel.js` lines 62, 74. |
| US-16 | As a nervous first-time user, I want my progress and badges saved so that I can come back later and feel proud. | S | v1 | M | frontend-engineer | 1. Progress bar shows steps done, still there after reload.<br>2. Finishing 10 steps earns the topic's badge once, with a message.<br>3. A "Your badges" list shows Earned / Not yet.<br>4. Saved only in this browser (`helpmate.progress.v1`); if storage is blocked, the course still works. | **Met** | `test_app.py::test_course_tab_open_close_and_progress_persists` (key and reload); `site/js/progress.js` lines 15-39 (try/catch, badge at 10 steps); `site/js/panel.js` lines 80-116. Badge earning has no automated test (test gap; `reports/qa.md` item 6). |

### Epic E: Ratings and self-improvement

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-17 | As a busy office worker, I want to rate the help with stars and an optional comment so that HelpMate gets better. | S | v1 | M | feedback-loop-engineer | 1. "Did this help?" form: 1-5 stars, comment up to 500 characters, honeypot, note about personal details.<br>2. Sends question, category, format and model date with it.<br>3. Netlify Forms detects the form and a real submission shows under Forms > rating.<br>4. A thank-you message shows; no page reload. | **Partly met** | 1, 2, 4: `test_app.py::test_rating_form_static_html_has_netlify_fields`, `::test_rating_form_dom_and_honeypot`, `::test_stars_radio_clickable_with_row_positioned`; `site/js/rating.js` lines 32-46. 3 **half shown**: Netlify Forms detection is enabled on the project (forms: enabled), but no real submission has been received yet; live `ratings_summary.json` total is 0. |
| US-18 | As the course grader, I want ratings to improve the app on every rebuild so that the self-improvement loop is real. | S | v1 | L | feedback-loop-engineer | 1. The build reads all submissions through the Netlify API (token from an environment variable, never printed).<br>2. Questions from 4-5 star ratings are added to training.<br>3. A build hook (by hand or daily) starts a rebuild.<br>4. After a rebuild with new ratings, Insights and `format_rank` change. | **Partly met** | 1, 2: `tests/test_feedback.py::test_api_pagination_verified_only`, `::test_training_rows`, `::test_http_error_returns_empty_and_token_never_printed`. 3: `netlify/functions/rebuild.mjs` (daily). 4 **not shown**: live total 0 ratings; no evidence that `NETLIFY_API_TOKEN` and `BUILD_HOOK_URL` are set. |
| US-19 | As any user, I want what I type to stay private so that I can ask without worry. | M | v1 | S | feedback-loop-engineer | 1. Published rating data holds only totals and averages: no comment or question text.<br>2. Emails and phone numbers are masked before scoring.<br>3. No tokens or secrets in the site files. | **Met** | `tests/test_build_outputs.py::test_no_comment_text_in_ratings`; `tests/test_feedback.py::test_pii_masked`, `::test_sentiment_callable_and_no_text_leak`; `tests/test_site_json.py::test_no_secrets_in_data`. |

### Epic F: Insights and Resources

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-20 | As the course grader, I want to see the most common problem words and phrases so that I can see what NLTK found. | S | v1 | M | data-viz-expert | 1. Charts for top words, word pairs and questions per topic, each labelled **NLTK**.<br>2. Each chart has a "Show this as a table" alternative.<br>3. Works at 360 px with no sideways page scroll. | **Met** | Live `nltk_stats.json`: 192 documents, top phrases "video call", "keep saying". `tests/browser/test_insights.py::test_insights_draws_charts_when_nltk_data_is_present`, `::test_every_chart_section_has_a_library_badge`, `::test_no_horizontal_overflow_360`. |
| US-21 | As the course grader, I want to see rating trends (stars over time, by topic, by format, comment mood) so that I can see how users feel. | S | v1 | M | data-viz-expert | 1. Four rating charts, labelled **NLTK** (comment mood).<br>2. With no ratings, a plain "no ratings yet" message instead of an empty chart.<br>3. Real ratings appear after a rebuild. | **Partly met** | Charts and badges exist (`site/insights.html` lines 83-113; `test_insights.py::test_null_sections_show_netlify_build_notice`). 3 not shown: live total 0, so all rating charts are empty. |
| US-22 | As the course grader, I want honest model-quality numbers so that I can judge each library fairly. | S | v1 | M | data-viz-expert | 1. Separate sections for Neural network, NLTK (VADER) and spaCy, each with its own label.<br>2. Headline says how many questions the number comes from ("about N% on 48 practice questions").<br>3. Missing numbers say "not measured", never "0%".<br>4. VADER shows the test-split number; spaCy problem accuracy shows its ceiling.<br>5. Tables are readable at 1280 px without cut-off columns. | **Partly met** | 1-3 met: `site/js/insights.js` lines 159, 222-229; `test_insights.py::test_every_chart_section_has_a_library_badge`. 4 half met: VADER test shown (`insights.js` line 203), but the build never writes `problem_ceiling` (absent from live `metrics.json`; not in `pipeline/build.py`), so the ceiling note never shows. 5 not met: confusion-matrix headers break mid-word and columns are cut off (`reports/qa.md`, Bugs). |
| US-23 | As the course grader, I want a Resources page with every source the project relies on so that I can check the work. | S | v1 | S | frontend-engineer | 1. Links to the live app, repository, README, research, roster, quality report and official NLTK, spaCy, scikit-learn, NumPy and Pyodide docs.<br>2. Links open in a new tab safely (`rel="noopener"`) and say so to screen readers.<br>3. Linked from the header and footer of every page. | **Met** | `tests/browser/test_resources.py::test_required_links_present`, `::test_every_link_opens_safely`, `::test_resources_link_in_header_and_footer`; live home page nav shows Resources. |

### Epic G: Accessibility, platform and labels

| ID | Story | Pri | Ver | Effort | Owner | Acceptance criteria | v1 status | Evidence |
|---|---|---|---|---|---|---|---|---|
| US-24 | As an older relative with low vision, I want the site to meet WCAG 2.2 AA so that I can use it with large text, a keyboard or a screen reader. | M | v1 | M | ux-accessibility-designer | 1. Text contrast at least 4.5:1 for every text and background pair.<br>2. Every button, chip and link target at least 44 x 44 px.<br>3. Everything works with the keyboard, with a visible focus ring and a skip link.<br>4. One h1, `lang="en"`, named buttons, labelled fields, alt text.<br>5. Results are announced (`aria-live`).<br>6. A keyboard-only and a screen reader pass on the live site find no blockers. | **Partly met** | 1-5: `tests/test_contrast.py::test_pair`; `test_app.py::test_accessibility_basics`, `::test_tabs_keyboard_arrows`; `test_insights.py::test_accessibility_basics`; `site/index.html` lines 2, 88, 144. 6 **not done** (`reports/qa.md`, post-deploy items 9-10). |
| US-25 | As a nervous first-time user, I want plain, friendly words so that I'm not scared off by jargon. | M | v1 | S | instructional-designer | 1. Answers and lessons avoid unexplained technical terms.<br>2. Error and empty states say what to do next in one short sentence.<br>3. Reading level is measured and is about age 11-12 (US grade 6-7) or lower. | **Partly met** | 1, 2: content written to `.claude/skills/instructional-content`; examples in `app.js` lines 78, 186. 3 **not measured**: no readability check exists. |
| US-26 | As a nervous first-time user on a phone, I want every page to fit my screen so that I don't have to scroll sideways. | M | v1 | S | frontend-engineer | 1. Home (with the course open), Insights and Resources have no sideways scrolling at 360 px.<br>2. Layout stacks below 960 px and uses two columns on desktop. | **Met** | `test_app.py::test_no_horizontal_overflow_360`, `::test_stacked_below_960`, `::test_two_column_workspace_on_desktop`; `test_insights.py::test_no_horizontal_overflow_360`; `test_resources.py::test_no_horizontal_overflow_360`. |
| US-27 | As the course grader, I want HelpMate to run entirely on Netlify with no server or database so that it is cheap and simple to host. | M | v1 | M | netlify-engineer | 1. `netlify.toml` builds with Python 3.12 and publishes `site/`.<br>2. Python (NLTK, spaCy, training) runs only at build time; spaCy never runs in the browser.<br>3. The only Netlify Function is JavaScript (optional rebuild).<br>4. The live build uses real NLTK and spaCy (no `--allow-missing`, tokenizer `nltk_clean_v1`). | **Met** | `netlify.toml`; `netlify/functions/rebuild.mjs`; `tests/test_build_outputs.py::test_allow_missing_refused_on_netlify`, `::test_missing_nltk_fails_without_flag`; live `metrics.json` has `nltk_clean_v1` and spaCy numbers; all live pages and `/data/*.json` load. |
| US-28 | As the course grader, I want every result to say which library made it so that I can see what NLTK, spaCy and the neural network each do. | M | v1 | S | frontend-engineer | 1. Category card: **Neural network** (or **spaCy** in fallback). Mood and calm notice: **NLTK**. Things mentioned, topics, tags: **spaCy**. Insights: one label per section.<br>2. Labels are text pills, never color alone, with a screen-reader description. | **Met** | `test_app.py::test_ask_printer_shows_cards_with_badges`, `::test_stubbed_brain_frustrated_printer`; `test_insights.py::test_every_chart_section_has_a_library_badge`; `site/index.html` line 94 (visually-hidden text). |
| US-29 | As a nervous first-time user, I want HelpMate to still help me if the smart helper can't start so that I'm never stuck. | S | v1 | S | pyodide-engineer | 1. If Pyodide fails, a plain notice says so and the category comes from the device/app match, labelled **spaCy**.<br>2. The answer and formats still work. | **Met** | `test_app.py::test_fallback_notice_when_engine_missing`; README "If Pyodide cannot start". |
| US-30 | As any user, I want no secret keys in the site so that HelpMate can't be misused. | M | v1 | S | security-reviewer | 1. No API token or build-hook URL in the repo or the published site.<br>2. The build never prints the token.<br>3. Secrets live only in Netlify environment variables. | **Met** | `tests/test_site_json.py::test_no_secrets_in_data`; `tests/test_feedback.py::test_source_has_no_token_logging`; `reports/deploy.md` step 4. A git-history review by Kai (security-reviewer) is still recommended. |
| US-31 | As a nervous first-time user, I want a warm, consistent look so that the site feels friendly and trustworthy. | C | v2 | S | ux-accessibility-designer | 1. Uses the HelpMate logo, favicon, colors and the Nunito font (CLAUDE.md, Brand).<br>2. Each format keeps its color (See blue, Hear coral, Try teal, Read purple). | **Partly met** | Logo, favicon and colors used (`site/index.html`, `site/css/design-tokens.css`). The pages also load **Fredoka** for headings (`site/index.html` line 11), which the brand does not list. |
| US-32 | As a nervous first-time user, I want a simple picture for each See it step so that I can see where to click. | C | v2 | L | instructional-designer | 1. Every See it step has an image under `assets/steps/` with alt text.<br>2. Images are small (under 50 KB each) and readable at 360 px. | **Not met** | 0 of 48 steps have `image` set; `site/assets/steps/` does not exist. |

## 6. Summary by status

| Status | Count | Stories |
|---|---|---|
| Met | 21 | US-01, 02, 03, 06, 07, 08, 09, 10, 11, 12, 13, 15, 16, 19, 20, 23, 26, 27, 28, 29, 30 |
| Partly met | 10 | US-04, 05, 14, 17, 18, 21, 22, 24, 25, 31 |
| Not met | 1 | US-32 |
| **Total** | **32** | |

Of the 14 Must stories, 11 are Met and 3 are Partly met (US-05, 24, 25). Updated 2026-11-23 after the lead's live Chrome check: US-07 and US-09 moved from Partly met to Met.

### Effort split (MoSCoW check)

| Priority | Stories | Points | Share |
|---|---|---|---|
| Must | 14 | 24 | 43% |
| Should | 14 | 26 | 46% |
| Could | 4 | 6 | 11% |

Must is under the 60% limit. Could is below the usual 20% contingency, so there is little slack; if v1 work runs late, drop Should items in this order: US-14, US-21, US-04.

Why some features are not Must: Hear it, Try it and Read it are Should because See it plus format switching is a workaround (MoSCoW rule: "if a workaround exists, it is not a Must"). Frustration tone (US-05) stays Must because without a working NLTK feature the course grader cannot accept the project. The ratings loop is Should because the app is useful without ratings.

## 7. Top gaps to close next

1. ~~**The live NLTK + neural-network path in the browser has never been verified** (US-07).~~ **Closed 2026-11-23:** verified by the lead in real Chrome on the live site (module worker, Pyodide 314.0.8, nltk 3.9.4). Still worth doing: an automated browser test against the live URL (qa-engineer).
2. **Frustration detection misses most frustrated questions** (US-05): live recall 0.29 on the test split, 0.42 overall. Owner: nltk-expert: add repetition signals ("every time", "over and over", "again"), quoted error text, and re-tune the threshold on train rows only; nlp-evaluator re-measures.
3. **The ratings loop is not proven live** (US-17, 18, 21, 14): Forms detection is now enabled, but 0 ratings in the live summary, no confirmed submission, token and build hook not confirmed. Owner: netlify-engineer + feedback-loop-engineer: submit a test rating, set `NETLIFY_API_TOKEN` and `BUILD_HOOK_URL`, rebuild, and check Insights changes.
4. **"What's broken" is only shown for precomputed examples, and it is often wrong** (US-04): exact 0.36, thing 0.45. Owner: spacy-expert (extractor and gold-file wording), then decide with the software-architect whether a JS rule for typed questions is worth it in v2.
5. ~~**See it promises pictures it does not have** (US-09).~~ **Closed 2026-11-23:** the button now says "Numbered steps". Pictures stay a v2 item (US-32; instructional-designer + ux-accessibility-designer).

Also open: a live keyboard-only and screen-reader pass (US-24), a reading-level check (US-25), the Insights problem-accuracy ceiling and confusion-matrix layout (US-22), and Fredoka vs Nunito (US-31).

## 8. Won't have this time (version 2 or later)

| Item | Reason |
|---|---|
| User accounts and syncing progress between devices | Needs a server and a database, which the architecture rules out. localStorage is enough for v1. |
| spaCy analysis of any typed question in the browser | spaCy does not run in Pyodide (docs/06). Would need a server or a different library. |
| Learning in real time from each rating | Netlify runs Python only at build time; the app improves on rebuild, and the docs say so. |
| Live chat or human help desk | Out of scope for a self-help coach and needs staff and a server. |
| Remote control of the user's device or automatic fixes | Risky for non-technical users and not possible from a static site. |
| Languages other than English | Seed data, VADER lexicon and content are English only. |
| Public IT ticket data in training | `data/tickets_sample.csv` was not downloaded (no network) and its license is non-commercial; the seed set is used alone. |
| Personal format recommendations by "learning style" | Not supported by evidence (docs/05). Users choose formats themselves. |

## 9. Definition of Done (all stories)

Kept separate from acceptance criteria, as the knowledge notes require.
- `pytest -q` passes, or each skip has a stated reason (NLTK or spaCy not installed).
- The Netlify deploy log shows `tokenizer=nltk_clean_v1` and no "SKIPPED" lines.
- The feature is checked on the live site, and the check is written in `reports/qa.md`.
- Docs that describe the feature (README, reports) are updated, and quality claims match `reports/nlp_quality.md`.
- No secrets in the repo or the built site.

## 10. Next steps for other agents

- **software-architect (Theo):** review every story against the build-time/browser boundary before this document is accepted, especially US-04 and the Won't items.
- **qa-engineer (Quinn):** turn the acceptance criteria into tests; add the missing ones (Try it ticks after reload, badge after 10 steps, unsure chip click, live-URL run).
- **orchestrator (Atlas):** assign the top 5 gaps in section 7.
