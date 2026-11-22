# HelpMate expert roster

**Decision:** everything runs on Netlify with no outside servers. NLTK and spaCy run at build time over the IT-help dataset and lesson library and save static JSON. NLTK and a small neural-network classifier also run live in the browser with Pyodide for the "Ask HelpMate" box. Ratings are collected with Netlify Forms, learning progress is saved in `localStorage`, and a rebuild (build hook or schedule) pulls in new ratings so the app improves itself. See [06-netlify-architecture.md](06-netlify-architecture.md).

## The team (16 agents)

| # | Agent (file name) | Group | One-line job |
|---|---|---|---|
| 1 | `orchestrator` | Lead | Breaks the work into tasks, hands each to the right expert, checks results and keeps the build moving. |
| 2 | `meta-agent` | Lead | Builds and improves the other agents, their skills and knowledge folders when gaps appear. |
| 3 | `nltk-expert` | NLP | Owns tokenizing, stopwords, VADER frustration and comment sentiment, FreqDist and collocations. |
| 4 | `spacy-expert` | NLP | Owns the EntityRuler (devices, apps, OS, error codes), dependency-parse problem extraction, noun chunks and lemmas. |
| 5 | `ml-engineer` | NLP | Trains the MLP question classifier at build time and exports it as JSON for the browser. |
| 6 | `dataset-curator` | Data | Samples and labels the public ticket data and writes the plain-language seed set, with licenses noted. |
| 7 | `instructional-designer` | Content | Writes every answer in four formats (See, Hear, Try, Read) and the 10-step mini-courses. |
| 8 | `ux-accessibility-designer` | Experience | Designs a warm, colorful, inviting UI that meets WCAG 2.2 for non-technical users. |
| 9 | `frontend-engineer` | Experience | Builds the static web app: question box, format buttons, side panel, progress and badges. |
| 10 | `data-viz-expert` | Experience | Builds the Insights page: common problems, rating trends, model accuracy. |
| 11 | `pyodide-engineer` | Platform | Makes NLTK and the classifier run live in the browser, with NLTK data shipped with the site. |
| 12 | `build-pipeline-engineer` | Platform | Writes the Python build that runs NLTK, spaCy and training and writes the static JSON. |
| 13 | `feedback-loop-engineer` | Platform | Connects Netlify Forms ratings to rebuilds: fetch, score, re-rank, retrain. |
| 14 | `netlify-engineer` | Platform | Owns `netlify.toml`, Python version, Forms setup, environment variables and build hooks. |
| 15 | `qa-engineer` | Quality | Writes and runs Python and browser tests; checks the live deploy works on desktop and phone. |
| 16 | `nlp-evaluator` | Quality | Measures quality honestly (classifier accuracy, VADER misses, spaCy entity errors) and reports it. |

### Roles we deliberately left out

- **Backend engineer / API developer:** Netlify Functions cannot run Python, and nothing live needs a server.
- **Database administrator:** ratings live in Netlify Forms, progress in each user's browser; there is no database.
- **DevOps / cloud engineer:** Netlify builds and hosts from GitHub automatically; the Netlify engineer covers configuration.
- **Security engineer:** the only secrets are the Netlify API token and build-hook URL, handled as environment variables by the Netlify and feedback-loop engineers.

## Skills and who shares them

| Skill | Description | Agents that use it |
|---|---|---|
| `task-planning` | Split work, assign agents, track progress | orchestrator, meta-agent |
| `agent-authoring` | Write subagents, skills and knowledge notes | meta-agent, orchestrator |
| `nltk-text-cleaning` | Tokenize, lower-case, remove stopwords, lemmatize | nltk-expert, ml-engineer, pyodide-engineer, build-pipeline-engineer |
| `vader-sentiment` | Score frustration and comments with VADER | nltk-expert, feedback-loop-engineer, nlp-evaluator |
| `frequency-and-collocations` | FreqDist and bigram collocations for common problems | nltk-expert, data-viz-expert |
| `spacy-pipeline` | Load `en_core_web_sm`, run it in batches | spacy-expert, build-pipeline-engineer |
| `entity-ruler-patterns` | Write and export IT entity patterns | spacy-expert, pyodide-engineer, dataset-curator |
| `dependency-parsing` | Extract (thing, problem) pairs | spacy-expert, nlp-evaluator |
| `topic-tagging` | Tag answers and lessons with noun chunks and lemmas | spacy-expert, instructional-designer |
| `mlp-training` | TF-IDF + MLPClassifier, train/test split | ml-engineer, feedback-loop-engineer |
| `model-export-json` | Export weights and vocabulary for NumPy inference | ml-engineer, pyodide-engineer |
| `dataset-licensing` | Check and record licenses and attribution | dataset-curator, nlp-evaluator |
| `data-labeling` | Label categories and frustration | dataset-curator, ml-engineer, nlp-evaluator |
| `pyodide-runtime` | Load Pyodide, packages and data files in the browser | pyodide-engineer, frontend-engineer |
| `static-json-output` | Write the JSON files the site reads | build-pipeline-engineer, spacy-expert, ml-engineer, feedback-loop-engineer |
| `netlify-config` | `netlify.toml`, Python version, publish folder | netlify-engineer, build-pipeline-engineer |
| `netlify-forms` | Rating form, detection, AJAX submit, API fetch | feedback-loop-engineer, netlify-engineer, frontend-engineer |
| `build-hooks` | Trigger and schedule rebuilds | feedback-loop-engineer, netlify-engineer |
| `instructional-content` | Four formats and 10-step microlessons | instructional-designer, ux-accessibility-designer |
| `web-speech` | Read steps aloud with `speechSynthesis` | frontend-engineer, instructional-designer |
| `local-progress` | Save progress and badges in `localStorage` | frontend-engineer, instructional-designer |
| `accessible-ui` | WCAG 2.2 contrast, 44 px targets, plain language | ux-accessibility-designer, frontend-engineer, data-viz-expert, qa-engineer |
| `brand-system` | HelpMate logo, colors, Nunito | ux-accessibility-designer, frontend-engineer, data-viz-expert |
| `charts` | Clear, labeled charts for Insights | data-viz-expert, nlp-evaluator |
| `testing` | pytest and browser tests | qa-engineer, nlp-evaluator, build-pipeline-engineer |
| `quality-reporting` | Accuracy, confusion matrix, error examples in `reports/` | nlp-evaluator, ml-engineer, qa-engineer |

## How the team works together

1. **Data:** the dataset curator prepares tickets and the seed set.
2. **NLP:** the NLTK expert, spaCy expert and ML engineer build their parts; the build-pipeline engineer runs them at build time.
3. **Content:** the instructional designer writes answers and mini-courses; the spaCy expert tags them.
4. **Experience:** the UX designer, frontend engineer and data-viz expert build the app; the Pyodide engineer makes the live box work.
5. **Platform:** the Netlify engineer and feedback-loop engineer set up deploys, Forms and the improvement loop.
6. **Quality:** the QA engineer and NLP evaluator test and measure; the orchestrator sends fixes back to the right expert.
