# HelpMate: NLP final exam project

HelpMate is a friendly self-help IT coach for non-technical users. A user types an IT question in plain words; the app finds the device or app and the problem (spaCy), notices frustration (NLTK VADER), sorts the question with a small neural network, and gives help in the format they choose: See it, Hear it, Try it or Read it. An optional 10-step mini-course tracks learning progress, and ratings improve the app on every rebuild.

## Architecture (read docs/06-netlify-architecture.md)
- **Build time on Netlify (Python):** NLTK, spaCy and model training write static JSON to `site/data/`.
- **Browser:** Pyodide runs NLTK + the NumPy classifier for the live box; JavaScript renders everything else.
- **Netlify Forms** collects ratings; **localStorage** keeps progress; a **build hook** triggers rebuilds.
- No backend server, no database. spaCy never runs in the browser. Never commit secrets.

## The team (16 agents in `.claude/agents/`)

| Name | Invoke | Model | Job |
|---|---|---|---|
| Atlas | `@agent-orchestrator` | opus | Break the HelpMate build into tasks, hand each to the right expert, check every result against the docs, and keep the project moving until it deploys on Netlify. |
| Forge | `@agent-meta-agent` | opus | Create and improve the team's agents (.claude/agents), skills (.claude/skills) and knowledge folders (knowledge/) so every expert has what it needs. |
| Lex | `@agent-nltk-expert` | sonnet | Own every NLTK feature in HelpMate: cleaning questions, detecting frustration with VADER, scoring rating comments, and finding the most common problems and phrases. |
| Sage | `@agent-spacy-expert` | sonnet | Own every spaCy feature in HelpMate: recognize devices, apps, operating systems and error codes, extract what is broken, and tag answers and lessons. |
| Synapse | `@agent-ml-engineer` | sonnet | Train, evaluate and export the neural-network question classifier that routes each question to one of 8 IT categories. |
| Tally | `@agent-dataset-curator` | haiku | Prepare the data the team learns from: a labeled sample of public IT tickets plus a plain-language seed set, with licenses recorded. |
| Maya | `@agent-instructional-designer` | sonnet | Write every answer in four formats and a 10-step mini-course per category, in plain language for non-technical people. |
| Iris | `@agent-ux-accessibility-designer` | sonnet | Design a warm, colorful, inviting interface that meets WCAG 2.2 for non-technical users, using the HelpMate brand. |
| Pixel | `@agent-frontend-engineer` | sonnet | Build the static web app in site/: question box, four format buttons, the 10-step side panel with progress and badges, and the rating form. |
| Vega | `@agent-data-viz-expert` | sonnet | Build the Insights page that shows the most common problems, rating trends and model quality, with accessible charts. |
| Pip | `@agent-pyodide-engineer` | sonnet | Make the live 'Ask HelpMate' box work in the browser: load Pyodide, NLTK and NumPy, ship NLTK data, and run the classifier. |
| Brick | `@agent-build-pipeline-engineer` | sonnet | Write the Python build (pipeline/build.py) that runs NLTK, spaCy and training at Netlify build time and writes every static JSON file. |
| Echo | `@agent-feedback-loop-engineer` | sonnet | Close the self-improvement loop: collect ratings with Netlify Forms, pull them in at build time, score them, re-rank answers and retrain the classifier. |
| Nimbus | `@agent-netlify-engineer` | haiku | Own deployment: netlify.toml, Python version, build command, publish folder, Forms detection and environment variables. |
| Quinn | `@agent-qa-engineer` | sonnet | Prove HelpMate works: Python tests for the pipeline and NLP, browser tests for the app, and checks on the live site. |
| Vera | `@agent-nlp-evaluator` | opus | Measure NLP quality honestly and write it up: classifier accuracy, VADER frustration errors, spaCy entity and problem-extraction errors. |

Start with `@agent-orchestrator`; it delegates to the others. Every agent preloads its skills from `.claude/skills/` and must read its folder in `knowledge/` before answering.

## Repository map
- `docs/`: research, roster (`expert-roster.md`), agent brains (`agent-brains.md`)
- `.claude/agents/`, `.claude/skills/`: the team and its 26 skills
- `knowledge/<agent>/`: reference notes from official documentation, with sources
- `assets/brand/`: logo and favicon
- To be built: `data/`, `nlp/`, `pipeline/`, `site/`, `tests/`, `reports/`, `netlify.toml`

## Brand
Logo `assets/brand/helpmate-mark.svg`, favicon `assets/brand/favicon.svg`. Font Nunito. Colors: navy #14213D, blue #2F7BF5 (See it), coral #FF6A4D (Hear it; use #C2410C for coral text on light; blue, teal and purple text use #1D5FD0, #0B7A63, #6D3FD6), teal #12A889 (Try it), purple #8A5CF6 (Read it), background #FFF8F0.

## Labels
Every result shown to users says which library made it: **NLTK**, **spaCy**, **Neural network**, or both.
