# HelpMate expert roster

**Decision:** everything runs on Netlify with no outside servers. NLTK and spaCy run at build time over the IT-help dataset and lesson library and save static JSON. NLTK and a small neural-network classifier also run live in the browser with Pyodide for the "Ask HelpMate" box. Ratings are collected with Netlify Forms, learning progress is saved in `localStorage`, and a rebuild (build hook or schedule) pulls in new ratings so the app improves itself. See [06-netlify-architecture.md](06-netlify-architecture.md).

## The team (19 agents)

| # | Agent (file name) | Group | One-line job |
|---|---|---|---|
| 1 | `orchestrator` | Lead | Breaks the work into tasks, hands each to the right expert, checks results and keeps the build moving. |
| 2 | `meta-agent` | Lead | Builds and improves the other agents, their skills and knowledge folders when gaps appear. |
| 3 | `product-manager` | Lead | Writes user stories and acceptance criteria, sets priorities (MoSCoW) and decides what ships in version 1 vs version 2. |
| 4 | `software-architect` | Lead | Chooses and documents the Netlify-friendly stack as ADRs and guards the build-time/browser boundary. |
| 5 | `nltk-expert` | NLP | Owns tokenizing, stopwords, VADER frustration and comment sentiment, FreqDist and collocations. |
| 6 | `spacy-expert` | NLP | Owns the EntityRuler (devices, apps, OS, error codes), dependency-parse problem extraction, noun chunks and lemmas. |
| 7 | `ml-engineer` | NLP | Trains the MLP question classifier at build time and exports it as JSON for the browser. |
| 8 | `dataset-curator` | Data | Samples and labels the public ticket data and writes the plain-language seed set, with licenses noted. |
| 9 | `instructional-designer` | Content | Writes every answer in four formats (See, Hear, Try, Read) and the 10-step mini-courses. |
| 10 | `ux-accessibility-designer` | Experience | Designs a warm, colorful, inviting UI that meets WCAG 2.2 for non-technical users. |
| 11 | `frontend-engineer` | Experience | Builds the static web app: question box, format buttons, side panel, progress and badges. |
| 12 | `data-viz-expert` | Experience | Builds the Insights page: common problems, rating trends, model accuracy. |
| 13 | `pyodide-engineer` | Platform | Makes NLTK and the classifier run live in the browser, with NLTK data shipped with the site. |
| 14 | `build-pipeline-engineer` | Platform | Writes the Python build that runs NLTK, spaCy and training and writes the static JSON. |
| 15 | `feedback-loop-engineer` | Platform | Connects Netlify Forms ratings to rebuilds: fetch, score, re-rank, retrain. |
| 16 | `netlify-engineer` | Platform | Owns `netlify.toml`, Python version, Forms setup, environment variables and build hooks. |
| 17 | `qa-engineer` | Quality | Writes and runs Python and browser tests; checks the live deploy works on desktop and phone. |
| 18 | `nlp-evaluator` | Quality | Measures quality honestly (classifier accuracy, VADER misses, spaCy entity errors) and reports it. |
| 19 | `security-reviewer` | Quality | Checks the repo, git history, built site and client code for exposed secrets or personal data; reviews Forms privacy, CDN pinning and security headers. |

### Professional roles and who covers them

- **Product manager:** `product-manager` (Nora).
- **Software architect:** `software-architect` (Theo).
- **Security reviewer:** `security-reviewer` (Kai), with `qa-engineer` and `netlify-engineer` sharing the `security-review` checklist.
- **DevOps / cloud engineer:** covered by `netlify-engineer`. Netlify builds and hosts from GitHub automatically, so there is no separate infrastructure to run.
- **Back-end / build engineer:** covered by `build-pipeline-engineer`. There is no server; the only back-end work is the Python build that writes static JSON.

### Roles we deliberately left out

- **Backend API developer:** Netlify Functions cannot run Python, and nothing live needs a server.
- **Database administrator:** ratings live in Netlify Forms, progress in each user's browser; there is no database.

## Skills and who shares them

| Skill | Description | Agents that use it |
|---|---|---|
| `task-planning` | Split work, assign agents, track progress | orchestrator, meta-agent, product-manager |
| `agent-authoring` | Write subagents, skills and knowledge notes | meta-agent, orchestrator |
| `requirements-writing` | User stories, acceptance criteria, MoSCoW / v1-v2 scoping | product-manager |
| `architecture-decisions` | ADRs (context, decision, consequences) and the boundary checklist | software-architect, orchestrator |
| `security-review` | Secrets scan (tree, git history, built site), env vars, PII, CDN pinning/SRI, headers | security-reviewer, qa-engineer, netlify-engineer |
| `nltk-text-cleaning` | Tokenize, lower-case, remove stopwords (keep negations), stem | nltk-expert, ml-engineer, pyodide-engineer, build-pipeline-engineer |
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
| `static-json-output` | Write the JSON files the site reads | build-pipeline-engineer, spacy-expert, ml-engineer, feedback-loop-engineer, software-architect |
| `netlify-config` | `netlify.toml`, Python version, publish folder | netlify-engineer, build-pipeline-engineer, software-architect |
| `netlify-forms` | Rating form, detection, AJAX submit, API fetch | feedback-loop-engineer, netlify-engineer, frontend-engineer, security-reviewer |
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

0. **Scope and design:** the product manager writes requirements and v1/v2 scope; the software architect records ADRs and the data contracts.
1. **Data:** the dataset curator prepares tickets and the seed set.
2. **NLP:** the NLTK expert, spaCy expert and ML engineer build their parts; the build-pipeline engineer runs them at build time.
3. **Content:** the instructional designer writes answers and mini-courses; the spaCy expert tags them.
4. **Experience:** the UX designer, frontend engineer and data-viz expert build the app; the Pyodide engineer makes the live box work.
5. **Platform:** the Netlify engineer and feedback-loop engineer set up deploys, Forms and the improvement loop.
6. **Quality:** the QA engineer and NLP evaluator test and measure, and the security reviewer checks for exposed secrets and data before each deploy; the orchestrator sends fixes back to the right expert.
