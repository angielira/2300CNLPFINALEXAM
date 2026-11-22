# HelpMate data

Prepared by Tally (dataset-curator), 2026-11-22; second pass the same day (label consistency and spaCy gold cleanup). This folder holds the source data the team learns from and tests against. Nothing here is a build output.

## spaCy gold convention (read first)

These rules apply to `spacy_gold.jsonl`. They are written so a dependency-based extractor can output the same strings.

**Entities (`entities`)**
- Each device, app, OS or error code mention is listed once, as the writer typed it, without `my`, `the`, `a`, `new` or `old`. Example: "my new phone" gives `phone`.
- A generic `app` after a brand name is dropped: "the Gmail app" gives `Gmail`. A generic `app` with no brand stays: `authenticator app`, `app store`.
- Wi-Fi and Face ID are labeled `DEVICE`. A feature or a network connection that the user connects to counts as a device here.
- Every visible mention is listed, including the ones the question uses only as context ("the wifi is fine on my phone" lists `wifi` and `phone`).

**Problems (`problems`)**
- `thing` is always lower case. When the problem is about a listed entity, `thing` is that entity's text in lower case (`hp printer`, `gmail`, `iphone`). Otherwise it is a lower-case noun (`printer driver`, `file`, `email account`, `password`).
- `problem` is one lemma word with an optional prefix:
  - `not <verb lemma>`: the thing fails to do something. Examples: `not send`, `not open`, `not connect`, `not see`.
  - `keep <verb lemma>`: only when the question itself says "keep" or "keeps" right before that verb. Example: "keeps freezing" gives `keep freeze`. "Keeps saying X" does not count, so X gets its own form.
  - `<verb or adjective lemma>` otherwise. Examples: `crash`, `slow`, `full`, `ask`, `use`.
- Connection failures are always `not connect`: "no internet", "no network", "offline", "poor connection", "gone" (for wifi), "not connected to audio".
- Particles are dropped: "wake up" gives `not wake`, "log out" gives `keep log` (when "keeps" is present).
- One problem per question. Questions with no clear failure have an empty list.
- The gold file is the target. It is not a copy of what the extractor outputs today.

## Files

| File | What it is | Rows | Source | License |
|---|---|---|---|---|
| `seed_questions.csv` | Plain-language IT questions, labeled by category and frustration, with a fixed train/test split | 240 (192 train, 48 test) | Written by Tally for this project | Original work (see below) |
| `spacy_gold.jsonl` | Hand-checked devices, apps, OS and error codes, plus the problem each question is about, for scoring spaCy | 91 lines, 152 entities, 74 with a problem | Derived from the seed questions above | Original work |
| `feedback_sample.json` | FAKE rating submissions in the feedback shape from `reports/plan.md` section 4.4 | 40 | Invented by Tally, PII-free | Original work. Not real user feedback |
| `fetch_tickets.py` | One-off sampler for public IT tickets. Needs network, has not been run here | n/a | Hugging Face dataset (below) | Script: original. Data: CC BY-NC 4.0 |
| `tickets_sample.csv` | Public IT ticket sample. NOT created yet (see "Public tickets") | 0 | Not downloaded | n/a yet |
| `README.md` | This file | n/a | n/a | n/a |

## Sources and licenses

### 1. HelpMate seed set (`seed_questions.csv`, `spacy_gold.jsonl`)
- **Creator:** Tally, the dataset-curator agent, working for the HelpMate team.
- **Method:** written by hand to sound like real non-technical people: vague, misspelled, emotional, short and long. About a quarter are frustrated. Many name real devices, apps, operating systems and error codes so spaCy has material to find.
- **Personal data:** none. No names, emails or phone numbers.
- **License:** original work, no third-party text, so no attribution is required. The team may pick a project license for it. Record that choice here once made.
- **Date created:** 2026-11-22. Labels were corrected the same day (see "Label changes" below).

### 2. Sample feedback (`feedback_sample.json`)
- **Creator:** Tally, invented for tests and for offline builds.
- **Status:** FAKE. It has the shape of Netlify Form submissions and is marked `"sample": true` at the top level and on every row. The pipeline uses it only when no Netlify token is set. Never mix it with real ratings.
- **License:** original work.

### 3. Public IT tickets (not downloaded)
- **Dataset:** Customer Support Tickets, Hugging Face, `Tobi-Bueck/customer-support-tickets`
- **Link:** https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
- **Creator:** Softoft (listed on Hugging Face as Tobi-Bueck)
- **DOI:** 10.57967/hf/6184
- **License:** CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/). Non-commercial use with attribution. Fine for a class project, not for a commercial product.
- **Date accessed:** NOT accessed. This workspace has no network, so nothing was downloaded.
- **Caveat:** the dataset page does not clearly say whether the tickets are real or synthetic. Say so in the final report.

## Public tickets: how to add them later

The plan treats the public tickets as an optional extra. The classifier already trains on the seed set alone.

1. On a machine with network access, install the library: `pip install datasets`.
2. Run the sampler from the repo root: `python data/fetch_tickets.py --out data/tickets_sample.csv --n 400`.
3. The script keeps English IT and technical-queue tickets, maps them to the 8 categories by keywords, masks emails and phone numbers, and writes up to 400 rows with `source = tickets`.
4. Add the attribution above to the final report, and keep the license note in this file.
5. Re-run the build. The tickets are added as training rows only. The test split stays seed-only.
6. Check the keyword mapping by hand on a sample of about 30 rows before you trust it. The keyword rules are rough.

## Column meanings

### `seed_questions.csv`
| Column | Meaning |
|---|---|
| `id` | Stable id `s001`..`s240`. Assigned after a seeded shuffle (random_state 42). |
| `text` | The question as a non-technical person might type it. |
| `category` | One of the 8 category ids (see below). |
| `frustrated` | `1` if the writer shows strong negative emotion, otherwise `0`. |
| `source` | Always `seed` in this file. Other sources are `tickets` and `feedback`. |
| `split` | `train` or `test`. Originally a stratified 20% test split by category, `random_state=42`. Never train on `test` rows. The label corrections below did not change any `split` value, so the test set is no longer exactly 6 per category (see "Known issues"). |

### `spacy_gold.jsonl` (one JSON object per line)
| Key | Meaning |
|---|---|
| `text` | A seed question, copied exactly. |
| `entities` | List of `{"text", "label"}`. `text` appears in the question (case-insensitive). Labels: `DEVICE`, `APP`, `OS`, `ERROR_CODE`. Rules are in the convention section above. |
| `problems` | List of `{"thing", "problem"}`, empty or one item. Forms are in the convention section above. Examples: `{"thing": "hp printer", "problem": "not connect"}`, `{"thing": "zoom", "problem": "keep freeze"}`. |

### `feedback_sample.json`
Top level: `sample` (true), `note`, `items`. Each item: `id`, `created_at` (ISO 8601 UTC), `stars` (1 to 5), `comment`, `question`, `category` (category id), `format` (`see_it`, `hear_it`, `try_it` or `read_it`), `sample` (true).

### `tickets_sample.csv` (when created)
`id`, `text` (subject and body, masked, max 400 characters), `category` (mapped id), `source` (`tickets`), `orig_queue` (original queue name), `orig_tags` (original tags joined with `|`).

## Label definitions

**Category (8 ids, in this order everywhere):**

| id | Display name | Use it when the user needs help with... |
|---|---|---|
| `printer` | Printer | printing, scanning, printer connection (including a printer that will not join a new router), ink, paper jams |
| `email` | Email | sending, receiving, syncing or setting up email (including on a phone), mailbox full, attachments |
| `wifi` | Wi-Fi & Internet | wifi, router, modem, no internet, slow internet, a device that cannot get online |
| `passwords` | Passwords & Login | forgotten or wrong passwords, lock-outs, two-step checks, sign-in loops (asked to sign in again and again) |
| `slow` | Slow computer | a slow, frozen, overheating or crashing computer |
| `phone_apps` | Phone & Apps | apps on a phone or tablet: installing, crashing, notifications, storage |
| `files` | Files & Storage | finding, saving, copying, backing up or recovering files and drives |
| `video_calls` | Video calls | camera, microphone, speakers and meeting apps (Zoom, Teams, Meet), including when the meeting app says there is no network but the internet works |

Rules, in the order to apply them:
1. One category per question: the thing the user needs fixed first.
2. If the question is about the **sign-in itself** (password rejected, asked for a password again and again, logged out again and again, locked out), the category is `passwords`, even when the app is email, Teams or Facebook.
3. If the **internet or router** is the cause (a device cannot get online, the wifi drops, the router light is wrong), the category is `wifi`, even when the symptom shows up in a video call. "My router keeps dropping the Zoom call" is `wifi`.
4. If the internet works and the **meeting app** itself fails, the category is `video_calls`.
5. If a **printer** will not connect or print, the category is `printer`, even when the cause is a new router.
6. Otherwise, the thing that must work (the mail, the file, the app, the computer) decides. "Email on my phone won't send" is `email`.

Frustrated (`frustrated`): `1` when the writer shows strong negative emotion, such as ALL CAPS words, repeated `!!`, "nothing works", "again", "every time", "useless" or "I'm done". Mild annoyance alone does not count. The flag is a human label. VADER is tested against it, not used to write it.

**Entity labels (`spacy_gold.jsonl`):**
- `DEVICE`: physical things (printer, laptop, router, phone, camera, webcam, microphone, mouse, computer, PC, Face ID, wifi).
- `APP`: software a user opens (Outlook, Zoom, WhatsApp, Windows Update).
- `OS`: operating systems (Windows 10, Windows 11, Android).
- `ERROR_CODE`: codes shown on screen (0x80070005, 0x800CCC0E).

## Label changes (second pass, 2026-11-22)

Six seed rows were changed to match the rules above. No `split` or `frustrated` value changed.

| id | Question (short) | Was | Now | Reason |
|---|---|---|---|---|
| s146 | old printer won't see the new network | wifi | printer | Printer connection is Printer. Same case as s049 (printer). Train. |
| s048 | internet fine, but Zoom says no network | wifi | video_calls | Internet works and the meeting app fails. Same case as s097. Test. |
| s067 | video calls drop when son streams on the same wifi | video_calls | wifi | Rule 3: the router is the cause, and the guide's own example is `wifi`. Train. |
| s081 | Outlook keeps asking for my password again and again | email | passwords | Rule 2: a sign-in loop. Same case as s225 (Teams). Test. |
| s098 | can't log into email, password says wrong | email | passwords | Rule 2: the sign-in is what fails. Test. |
| s150 | Facebook app keeps logging me out | phone_apps | passwords | Rule 2: repeated sign-in. Test. This is the one call most open to debate. |

## Known issues

- **Test split is no longer 6 per category.** The split column was kept as it was, as instructed, so the label changes moved some test rows between categories. Current test counts: email 4, files 6, passwords 9, phone_apps 5, printer 6, slow 6, video_calls 7, wifi 5 (total 48). Train counts: printer 25, video_calls 23, the rest 24 (total 192). Any metric on the test split must be re-run; the earlier numbers in `reports/nlp_quality.md` were measured on the old labels.
- A future pass can re-draw the split (stratified, seed 42) after the labels settle. Do that only with Vera and Synapse, because it changes every reported number.
- The labeling guide (`knowledge/dataset-curator/labeling-guide.md`) does not yet contain rules 2 to 6 above or the gold conventions. The meta-agent should add a note there.

## Checks run on 2026-11-22

Checked with Python (`csv` and `json` modules, stdlib; `difflib` for similarity):

First pass (before the label changes):
- `seed_questions.csv`: 240 rows, all columns present, no empty fields, all ids unique, no duplicate texts.
- Rows per category: 30 each (8 categories, 240 total). Test rows: 6 each (48 total, train 192).
- Frustrated rows: 64 of 240 (26.7%). Per category: 8 each.
- Near-duplicates: none at a similarity of 0.85 or higher (difflib).
- `spacy_gold.jsonl`: 91 lines, every entity text appears in its question, every label is one of the four.
- `feedback_sample.json`: 40 items, stars 1 to 5, valid categories and formats.
- `fetch_tickets.py`: not run (no network). Compile check only.

Second pass (after the label changes and the gold cleanup):
- `seed_questions.csv`: still 240 rows, ids unique, no duplicate texts, 192 train and 48 test, 64 frustrated (14 in test), no near-duplicates at 0.85 (difflib). Only the six `category` values listed above changed.
- Cross-label scan: a content-word overlap scan (Jaccard at least 0.3, cross-label pairs) found 9 pairs. None is near-identical in wording. They were reviewed by hand and none is a contradiction.
- `spacy_gold.jsonl`: 91 lines, 152 entities (DEVICE 79, APP 53, OS 14, ERROR_CODE 6), 74 lines with one problem (58 from train rows, 16 from test rows). Every entity text appears in its question. No overlapping spans. Every problem is in an allowed form: a lemma, `not <lemma>` or `keep <lemma>`. Every `keep` appears in the question text. Every gold text is a seed text.
- Count sources: the earlier "72 train and 19 test" figures were line counts for all gold rows, not problem counts.
- `pytest tests/test_spacy_features.py tests/test_classifier.py`: 11 passed, 22 skipped (spaCy and NLTK are not installed in this workspace, so the spaCy-dependent tests skip).

## Terms for the spaCy expert (found in the seed set)

These come straight from `seed_questions.csv` and `spacy_gold.jsonl`. Use them as EntityRuler seeds and check them against the patterns.

- **DEVICE:** printer, HP printer, HP deskjet, Canon printer, Epson printer, shared printer, office printer, laptop, HP laptop, Dell laptop, shared family computer, computer, gaming PC, work PC, PC, Mac, MacBook, Chromebook, iPhone, iPhone 15, iPad, tablet, Samsung Galaxy, router, modem, Xfinity box, smart TV, TV, webcam, camera, microphone, mouse, headphones, phone, SD card, USB stick, external hard drive, Face ID, wifi.
- **OS:** Windows, Windows 10, Windows 11, Android.
- **APP:** Outlook, Gmail, Yahoo mail, Windows Mail, Google Drive, OneDrive, Dropbox, iCloud, Word, Excel, Chrome, Safari, Zoom, Microsoft Teams, Teams, Google Meet, Skype, WhatsApp, Instagram, Facebook, Snapchat, TikTok, Spotify, Google Maps, Google Play Services, Microsoft Defender, Windows Update, Task Manager, app store, file explorer, authenticator app, Camera app.
- **ERROR_CODE:** 0x000003eb, 0x800CCC0E, 0x0000007E, 0x80070005, 0xA00F4244. Also DNS_PROBE_FINISHED_NO_INTERNET (not hex, a word-style code).
- **Phrases to consider:** print spooler, print queue, printer driver, two-step verification, 2FA, passkey, conflicted copy. The "thing" forms in the gold file (`printer driver`, `print spooler`) are not entities.
