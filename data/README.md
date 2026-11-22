# HelpMate data

Prepared by Tally (dataset-curator), 2026-11-22. This folder holds the source data the team learns from and tests against. Nothing here is a build output.

## Files

| File | What it is | Rows | Source | License |
|---|---|---|---|---|
| `seed_questions.csv` | Plain-language IT questions, labeled by category and frustration, with a fixed train/test split | 240 | Written by Tally for this project | Original work (see below) |
| `spacy_gold.jsonl` | Hand-checked devices, apps, OS and error codes, plus the problem each question is about, for scoring spaCy | 91 lines, 125 entities | Derived from the seed questions above | Original work |
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
- **Date created:** 2026-11-22.

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
| `split` | `train` or `test`. Stratified 20% test split by category, `random_state=42`. Never train on `test` rows. |

### `spacy_gold.jsonl` (one JSON object per line)
| Key | Meaning |
|---|---|
| `text` | A seed question, copied exactly. |
| `entities` | List of `{"text", "label"}`. `text` appears in the question (case-insensitive). Labels: `DEVICE`, `APP`, `OS`, `ERROR_CODE`. |
| `problems` | List of `{"thing", "problem"}`. `thing` is the device or app (lower case, lemma-like). `problem` is the short description, e.g. `not print`, `keep freeze`. Empty list if none. |

### `feedback_sample.json`
Top level: `sample` (true), `note`, `items`. Each item: `id`, `created_at` (ISO 8601 UTC), `stars` (1 to 5), `comment`, `question`, `category` (category id), `format` (`see_it`, `hear_it`, `try_it` or `read_it`), `sample` (true).

### `tickets_sample.csv` (when created)
`id`, `text` (subject and body, masked, max 400 characters), `category` (mapped id), `source` (`tickets`), `orig_queue` (original queue name), `orig_tags` (original tags joined with `|`).

## Label definitions

**Category (8 ids, in this order everywhere):**

| id | Display name | Use it when the user needs help with... |
|---|---|---|
| `printer` | Printer | printing, scanning, printer connection, ink, paper jams |
| `email` | Email | sending, receiving, syncing or setting up email (including on a phone) |
| `wifi` | Wi-Fi & Internet | wifi, router, modem, no internet, slow internet |
| `passwords` | Passwords & Login | forgotten passwords, lock-outs, two-step checks, sign-in loops |
| `slow` | Slow computer | a slow, frozen, overheating or crashing computer |
| `phone_apps` | Phone & Apps | apps on a phone or tablet: installing, crashing, notifications, storage |
| `files` | Files & Storage | finding, saving, copying, backing up or recovering files and drives |
| `video_calls` | Video calls | camera, microphone, speakers and meeting apps (Zoom, Teams, Meet) |

Rule: one category per question, the thing the user needs fixed first. "Email on my phone won't send" is `email`, because the mail is what must work. "My router keeps dropping the Zoom call" is `wifi`.

**Frustrated (`frustrated`):** `1` when the writer shows strong negative emotion, such as ALL CAPS words, repeated `!!`, "nothing works", "again", "every time", "useless" or "I'm done". Mild annoyance alone does not count. The flag is a human label. VADER is tested against it, not used to write it.

**Entity labels (`spacy_gold.jsonl`):**
- `DEVICE`: physical things (printer, laptop, router, phone, camera).
- `APP`: software a user opens (Outlook, Zoom, WhatsApp).
- `OS`: operating systems (Windows 10, Windows 11, Android).
- `ERROR_CODE`: codes shown on screen (0x80070005, 0x800CCC0E).

## Terms for the spaCy expert (found in the seed set)

These come straight from `seed_questions.csv` and `spacy_gold.jsonl`. Use them as EntityRuler seeds and check them against the patterns.

- **DEVICE:** printer, HP printer, HP deskjet, Canon printer, Epson printer, shared printer, office printer, laptop, HP laptop, Dell laptop, gaming PC, PC, Mac, MacBook, Chromebook, iPhone, iPhone 15, iPad, tablet, Samsung Galaxy, router, modem, Xfinity box, smart TV, TV, webcam, camera, microphone, headphones, SD card, USB stick, external hard drive, phone.
- **OS:** Windows, Windows 10, Windows 11, Android.
- **APP:** Outlook, Gmail, Yahoo mail, Windows Mail, Google Drive, OneDrive, Dropbox, iCloud, Word, Excel, Chrome, Safari, Zoom, Microsoft Teams, Teams, Google Meet, Skype, WhatsApp, Instagram, Facebook, Snapchat, TikTok, Spotify, Google Maps, Google Play Services, Microsoft Defender, Windows Update, Task Manager, app store, file explorer, authenticator app, camera app.
- **ERROR_CODE:** 0x000003eb, 0x800CCC0E, 0x0000007E, 0x80070005, 0xA00F4244. Also DNS_PROBE_FINISHED_NO_INTERNET (not hex, a word-style code).
- **Phrases to consider:** print spooler, print queue, printer driver, two-step verification, 2FA, passkey, Face ID, conflicted copy.

## Checks run on 2026-11-22

Checked with Python (`csv` module, stdlib and scikit-learn):
- `seed_questions.csv`: 240 rows, all columns present, no empty fields, all ids unique, no duplicate texts.
- Rows per category: 30 each (8 categories, 240 total). Test rows: 6 each (48 total, train 192).
- Frustrated rows: 64 of 240 (26.7%). Per category: 8 each.
- Near-duplicates: none at a similarity of 0.85 or higher (difflib).
- `spacy_gold.jsonl`: 91 lines, every entity text appears in its question, every label is one of the four.
- `feedback_sample.json`: 40 items, stars 1 to 5, valid categories and formats.
- `fetch_tickets.py`: not run (no network). Compile check only.

## Not done yet

- The public ticket sample is not downloaded (no network). See "Public tickets" above.
- Feedback loop: the feedback-loop-engineer should accept the `items` wrapper in `feedback_sample.json`, or read the rows from `items`.
- The seed set has no project license yet. The team should decide one and write it here.
