# HelpMate NLP quality report

Written by Vera (nlp-evaluator), 2026-11-22. This is the plan's phase 5b report (the plan calls it `reports/quality.md`; it lives here as `reports/nlp_quality.md`).

**Read this first.** NLTK and spaCy are not installed in this workspace. Every classifier number below is a **local run with the `simple_v1` tokenizer** (lowercase, regex tokens, small stop list, **no stemming**). The site Netlify ships uses `nltk_clean_v1` (NLTK stop words plus Porter stemming), so the deployed numbers will be different. VADER and spaCy have **not been measured yet**. Their sections give the evaluation method, the bugs fixed in the evaluation code, and predictions from reading the code and the data. Real numbers come from the first Netlify build (see the last section).

---

## 1. Data and splits

| Set | Size | Used for | Source |
|---|---|---|---|
| `data/seed_questions.csv`, `split=train` | 192 (24 per category) | classifier training; 5-fold CV for choosing settings | written for the project by the dataset-curator agent (original, synthetic) |
| `data/seed_questions.csv`, `split=test` | 48 (**6 per category**) | classifier test, looked at once per configuration; VADER "test" numbers | same |
| `seed_questions.csv`, `frustrated` column | 64 of 240 rows frustrated (14 of 48 in test) | VADER frustration precision/recall | same, hand-labeled |
| `data/spacy_gold.jsonl` | 91 questions, 125 entities, 74 with a gold problem (72 from train rows, 19 from test rows) | spaCy entity precision/recall, problem extraction | derived from the seed questions |
| `data/tickets_sample.csv` | 0 (not downloaded; no network) | would add public tickets (CC BY-NC 4.0) | not used |
| `data/feedback_sample.json` | 40 FAKE ratings | ratings pipeline only; adds 0 training rows | invented, marked `"sample": true` |

There are no formal tickets, so everything is measured on plain-language questions, which is what docs/04 asks for. The other side of that: every example was written by one author (an agent) who also labeled it. That makes the language more uniform than real users' questions and the labels more self-consistent than real annotation, so expect real-world accuracy to be **lower** than anything shown here.

---

## 2. Classifier (Neural network): local `simple_v1` numbers

### 2.1 What was measured
`nlp/classifier.train` is a TF-IDF vectorizer feeding an `MLPClassifier`. It is trained on the 192 train rows and tested once on the 48 test rows. The sklearn `predict_proba` output and `predict_numpy` (the browser path) agree to 1e-4 on every test row (`tests/test_classifier.py::test_parity_with_sklearn`).

### 2.2 How the settings were chosen (train split only)
I used repeated stratified 5-fold CV (5 repeats, 25 folds) on the **192 train rows only**. Each fold also gets its own network seed, so a setting can't win on one lucky initialization. Comparisons are **paired**: every setting sees the same folds. The test split was not used for any choice. Reproduce with `python pipeline/eval_classifier.py`.

| Setting (all lbfgs, 64 hidden units, sublinear TF, max_features 2000) | CV accuracy | vs old | paired s.e. | folds better / worse | "unsure" rate at 0.45 |
|---|---|---|---|---|---|
| **old:** word 1-2-grams, alpha 1e-3 | 0.729 | — | — | — | 0.12 |
| 1-2-grams, alpha 1e-2 | 0.753 | +0.024 | 0.012 | 14 / 7 | 0.21 |
| unigrams, alpha 1e-3 | 0.754 | +0.025 | 0.012 | 15 / 7 | 0.06 |
| **new:** unigrams, alpha 1e-2 | **0.780** | **+0.051** | 0.012 | **18 / 1** | 0.14 |
| unigrams, alpha 1e-1 | 0.788 | +0.059 | 0.012 | 19 / 2 | 0.24 |

Things I tried that did not help (3×5-fold, same protocol): the `adam` solver (0.52-0.53, much worse on 192 rows), 32 or 128 hidden units (no change), turning off sublinear TF (no change). With unigrams, any alpha from 0.01 to 1 gives 0.78-0.79, a flat plateau.

**Why unigrams help.** With 1-2-grams the vocabulary is 1,976 terms for 192 short questions, and almost every bigram appears once. The network can memorize those one-off bigrams, so they add noise rather than signal. Unigrams give 642 terms. A side benefit is that `model.json` shrinks from about 1 MB to 456 KB, which loads faster in the browser.

**Why alpha 1e-2 and not 1e-1.** The 0.008 CV difference between them is well inside the noise. Alpha 1e-1 makes the network less confident: 24% of questions fall under the `min_confidence` 0.45 "I'm not sure, pick a topic" threshold, against 12% today. In exchange, wrong-and-confident answers drop from 19% to 9% (CV). That is a UX trade-off, not something CV alone should settle. Alpha 1e-2 keeps the unsure rate near today's level (14%) and still cuts wrong-and-confident answers to 13.5%. If the team would rather the app say "I'm not sure" more often than guess wrong, alpha 1e-1 is a reasonable choice (pick it with the UX designer).

**Implemented:** `nlp/classifier.py` now has `NGRAM_RANGE = (1, 1)` and `MLP_ALPHA = 1e-2`. The parity test passes, and `tests/test_classifier.py` now checks `ngram_range` against the constant.

### 2.3 Test-set results (48 questions, looked at once per configuration)

| | Accuracy | Macro precision | Macro recall | Macro F1 | 95% bootstrap CI for accuracy |
|---|---|---|---|---|---|
| old (1-2-grams, alpha 1e-3) | 0.667 (32/48) | 0.698 | 0.667 | 0.639 | 0.54 - 0.79 |
| **new (unigrams, alpha 1e-2)** | **0.750 (36/48)** | 0.796 | 0.750 | 0.739 | 0.63 - 0.88 |

The new model fixes 5 test questions and breaks 1, a net gain of 4. **Do not read much into the size of the test gain.** With 48 questions, one question is 2.1 points, and the two confidence intervals overlap almost entirely. The evidence for the change is the CV result (better on 18 of 25 folds, worse on 1). The test set only agrees with it.

Per class, new model (6 test questions each, so **one question moves recall by 0.17**; differences of 1-2 questions between classes are noise):

| Category | Precision | Recall | F1 | Support | old recall |
|---|---|---|---|---|---|
| printer | 1.00 | 0.83 | 0.91 | 6 | 0.83 |
| email | 1.00 | **0.33** | 0.50 | 6 | 0.17 |
| wifi | 0.67 | 0.67 | 0.67 | 6 | 0.67 |
| passwords | 0.60 | 0.50 | 0.55 | 6 | 0.33 |
| slow | 1.00 | 0.83 | 0.91 | 6 | 1.00 |
| phone_apps | 0.67 | 1.00 | 0.80 | 6 | 0.83 |
| files | 0.60 | 1.00 | 0.75 | 6 | 0.67 |
| video_calls | 0.83 | 0.83 | 0.83 | 6 | 0.83 |

Email is the weakest category in both models, and that gap (2/6 vs 5-6/6 for most classes) is larger than noise. Section 2.4 explains why.

Confusion matrix, new model (rows = true, columns = predicted, order as in `CATEGORIES`):

| true \ pred | printer | email | wifi | passwords | slow | phone_apps | files | video_calls |
|---|---|---|---|---|---|---|---|---|
| printer | **5** | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| email | 0 | **2** | 0 | 2 | 0 | 1 | 1 | 0 |
| wifi | 0 | 0 | **4** | 0 | 0 | 1 | 1 | 0 |
| passwords | 0 | 0 | 0 | **3** | 0 | 1 | 1 | 1 |
| slow | 0 | 0 | 0 | 0 | **5** | 0 | 1 | 0 |
| phone_apps | 0 | 0 | 0 | 0 | 0 | **6** | 0 | 0 |
| files | 0 | 0 | 0 | 0 | 0 | 0 | **6** | 0 |
| video_calls | 0 | 0 | 1 | 0 | 0 | 0 | 0 | **5** |

The biggest single mix-up is email sent to passwords (2). Files and phone_apps act as "catch-all" classes: they receive 4 and 3 wrong guesses.

### 2.4 Real errors (new model) and likely causes
1. **"Canon printer not connecting to wifi after i changed my router"**: true printer, predicted wifi (0.98). Three Wi-Fi words outvote one printer word. The labels also disagree with each other: the training row s146, *"I got a new router from my provider but my old printer won't see the new network"*, is labeled **wifi**. The model learned that pattern faithfully. This is a labeling problem, so the fix is a labeling rule, not a model change.
2. **"Zoom keeps saying "poor connection" even though my internet is fine"**: true video_calls, predicted wifi (0.97). Bag-of-words can't use "even though ... is fine". Training row s048, *"Internet is fine on the computer but Zoom says no network"*, has the same shape and is labeled **wifi**. Same label inconsistency as example 1.
3. **"I cant log into my email on my phone, it says the password is wrong but it's not"**: true email, predicted passwords (0.84). "log", "password" and "wrong" are strong password words. The data-labeling rule ("the thing to fix first") honestly allows either label. The same thing happens with *"Outlook keeps asking for my password over and over..."* (email, predicted passwords, 0.72). Together these explain most of email's low recall.
4. **"Why are the emails from my sister going to my spam folder every single time!!"**: true email, predicted files (0.45). `simple_v1` doesn't stem, so "emails" is a different feature from "email", and "folder" is a strong files word. Porter stemming in `nltk_clean_v1` maps "emails" to "email", so the Netlify model may get this one right.
5. **"Can I use Face ID to unlock my Windows laptop?"**: true passwords, predicted video_calls (0.82). "face" appears in video-call training rows ("my face is really dark on Zoom"), and "unlock" is rare in training. A real word-sense problem for bag-of-words.
6. (Broken by the change) **"the screen freezes for like 30 seconds and then comes back, over and over"**: true slow, predicted files (0.50). Without stemming, "freezes" doesn't match the training words "freezing"/"froze"; "over and over" appears in a files training row (s232, Dropbox copies).

Low-confidence errors such as *"my modem has 5 lights and only one is green, is that bad"* (0.30) and *"spam emails keep going into my inbox"* (0.41) fall under the 0.45 threshold. The app shows the "pick a topic" chips for these instead of a wrong answer. On the test set, 7 of 48 questions are "unsure", and 9 are wrong but above the threshold.

---

## 3. NLTK VADER frustration: not measured yet (needs the Netlify build)

### 3.1 How it is measured (`pipeline/build.py::vader_metrics`)
It runs `nltk_features.frustration(text)` on every seed row and compares the result with the `frustrated` column. Precision means "of the questions flagged, how many were really frustrated"; recall means "of the frustrated questions, how many were flagged". The rule flags a question if VADER compound ≤ -0.4, **or** if it contains a problem phrase together with `!!` or an ALL-CAPS word of 4+ letters.

**Changes to the evaluation code (this pass):**
- It now also reports `test`: precision, recall and F1 on the 48 test rows only. VADER isn't trained, but the phrase list and the -0.4 threshold were written while looking at these same seed questions, so the all-rows number is optimistic. The test-only number is the fairer one (14 frustrated rows, so it is also noisy).
- It now reports `n_frustrated` and `true_positive_reasons` (how many hits came from `vader_negative` and how many from the phrase rule).
- Labels are compared after `strip()`, so `"1 "` counts as frustrated.
- No counting bugs were found in the original code.

### 3.2 What I can already compute exactly (the phrase rule is plain regex)
- The phrase + `!!`/CAPS rule fires on **8 of 64** frustrated rows (12.5%) and on **0** non-frustrated rows. It fires on **0 of the 14 frustrated test rows**. So recall on the test split depends entirely on VADER.
- **A gap that is a real bug in practice:** the phrase list only has the apostrophe forms (`won't`, `can't`, `doesn't work`). People who don't type apostrophes are missed:
  - *s206 "my laptop says limited connectivity and it WONT let me go online at all!!"* has `!!` and CAPS, but "WONT" isn't in the list.
  - *s035 "print queue is stuck ... and I cant cancel them"*: "stuck" matches, but there is no `!!`/CAPS.
  - *s013 "I dont know why my printer isnt working..."*: "isnt working" isn't in the list.
  - *s022 / s220 "... crashes ... EVERY SINGLE TIME" / "THE EMAIL APP CRASHES ..."*: the list has "crashed" but not "crashes".

### 3.3 Predicted VADER misses (to confirm against the build)
These are predictions from VADER's design (social-media lexicon; boosts for caps, `!` and degree words; negation flips the next ~3 words; "but" shifts weight to the second clause). They are not measurements.
- **Technical failures with no emotion words** score near neutral: *s091 "my Zoom call keeps freezing and nobody can hear me"*, *s231 "the printer keeps printing the same page over and over and I cannot stop it!"*, *s232 "the Dropbox folder keeps making copies ... over and over"*, *s041 "the screen freezes for like 30 seconds ... over and over"*, *s143 "Teams keeps asking me to allow the microphone and I already did!"*. All five are frustrated **test** rows.
- **Positive words used sarcastically or politely** push the score up: *s235 "my router is blinking red and the wifi is GONE. Great."* ("Great" is strongly positive), *s064 "...PLEASE tell me how to undo that"* and *s229 "...Please!"* ("please" is positive and boosted by caps/!).
- **Negation flips a negative word**: *s096 "My Mac says disk is almost full and it's not even my fault!!!"* ("not ... fault" counts as positive).
- **Contrast with "but"/"even though" plus a positive word**: *s097 "Zoom keeps saying "poor connection" even though my internet is fine"*, *s098 "...it says the password is wrong but it's not"*.
- **Emphasis without lexicon words**: *s053 "I clicked print in Word and NOTHING came out of the printer. Nothing!!"* ("nothing" carries no sentiment score).
- **Likely caught** (strong lexicon words such as tired, annoying, crazy, useless, sick, ridiculous, scam, stressed): s013, s055, s077, s089, s150, s163, s179, s052, s036.
- **Likely false positives** (calm questions with a negative word): *s014 "my modem has 5 lights and only one is green, is that bad"*, *s050 "I deleted a photo folder by accident..."*, *s151 "My mum's account says "Access denied" and she is in a panic"*, *s084 "...They're a mess"*.

**My expectation:** recall on all seed rows somewhere around 0.3-0.5, and lower on the test split, which contains mostly emotion-free complaints. Precision is probably higher than recall. If the build confirms this, the cheapest fixes (for the nltk-expert) are: add apostrophe-free forms (`wont`, `cant`, `isnt working`, `doesnt work`, `dont work`) and `crashes`/`keeps crashing`; count repetition (`over and over`, `every single time`, `again`) as a frustration signal on its own; re-tune the -0.4 threshold on the train rows only.

---

## 4. spaCy entities and problem extraction: not measured yet (needs the Netlify build)

### 4.1 How it is measured (`pipeline/build.py::spacy_metrics`)
For each of the 91 gold questions, it compares the `(text, label)` entity pairs (DEVICE, APP, OS, ERROR_CODE only; the statistical ORG/PRODUCT spans are ignored) case-insensitively, and pools TP/FP/FN into precision and recall. For problems, it counts a question as correct if any extracted `(thing, problem)` pair exactly equals a gold pair.

**Changes to the evaluation code (this pass):**
- Gold and predicted strings are now normalized the same way (lowercase, collapsed whitespace) for both entities and problems. Previously the problem side wasn't lowercased.
- New `problem_thing_accuracy`: is the broken *thing* right, even if the problem wording differs? This separates "found the right device" from "used the exact gold wording".
- New `problem_errors` (up to 5). Before, `errors` only listed entity mismatches, so problem-extraction failures were never shown anywhere.
- New `entity_counts` (tp/fp/fn) and `problem_n`.
- The build log summary now prints the NLTK and spaCy numbers, not just classifier accuracy.

### 4.2 Problems with the gold file itself (they will distort the numbers)
I approximated the EntityRuler by longest-first phrase matching with the exported `entity_patterns.json`. That is not spaCy, only an upper-bound sketch. Against the gold file it gives precision ≈ 0.80 and recall ≈ 0.98. About **28 of the 30 "false positives" are real mentions the gold file leaves out**: wifi (5), phone (4), printer (3), computer (3), camera (3), PC (2), microphone (2), Face ID, mouse, laptop, webcam, "Camera app". Example: *"the wifi is fine on my phone but my smart TV can't get on"* lists only "smart TV". **So spaCy entity precision on Netlify will understate the ruler's real precision.** The dataset-curator should add the missing mentions. There are 2 real disagreements: "family computer" (ruler) vs "computer" (gold), and "windows update" (ruler APP) vs "windows" (gold OS) in *"since the last windows update"*.

For problems:
- **21 of the 74 gold problems use wordings the extractor can never produce.** It only outputs `lemma`, `not lemma`, or `aspect-verb lemma`, but the gold includes "no internet", "ask password", "not wake up", "not see network", "in use", "access denied", "almost full", "poor connection", "log out", "black screen", "make copy" and others. **The best possible exact problem accuracy is 53/74 = 0.716.** Read the Netlify number against that ceiling, not against 1.0.
- **The gold wording is inconsistent:** "Xfinity box keeps restarting" is "keep restart", but "my Zoom call keeps freezing" is "freeze" and "my iPhone keeps crashing" is "crash". "Teams ... asks me to sign in again" is "keep ask" although the text has no "keep". The extractor outputs "keep freeze" and "keep crash", so it will be marked wrong on lines where the gold drops "keep".
- **The gold naming of things is inconsistent:** "hp deskjet ..." has thing "printer", but the code uses the entity root ("deskjet"); "the Zoom app on my iPad is blank" has thing "zoom", but the code builds "zoom app" from the compound; "Gmail app"/"Instagram app"/"Spotify app" keep "app" in the gold.

### 4.3 Predicted extraction failures (from reading `nlp/spacy_features.py`)
- **Pronoun subjects give nothing.** *"My Word document got saved as a weird .tmp file and I can't open it"*: the negated verb "open" has subject "I" and object "it". Both are pronouns, so `_thing_name` rejects them and nothing is extracted. Many "I can't ..." questions will fail this way.
- **Negated verbs inside reported speech have no subject.** *Gmail says "couldn't send" every time I attach a photo*: "send" has no subject or object of its own, and "says" isn't a problem verb, so nothing is extracted.
- **Problem verbs missing from `PROBLEM_VERBS`:** close ("Instagram app closes on its own"), drain ("battery drains like crazy"), spin ("Mac is spinning the rainbow wheel"), wipe ("authenticator app got wiped"). Each gives no problem.
- **Apostrophe-free negation:** in *"hp deskjet wont wake up"*, spaCy splits "wont" into "wo" + "nt". `NEGATION_WORDS` has "n't" but not "nt", so negation relies on the parser tagging it `neg`. The particle "up" is also dropped ("not wake", while the gold says "not wake up"). Check this one in the build output.
- **Verb-less questions** ("printer broken") are handled by fallback 7, but it only runs when nothing else was found, and only for DEVICE/APP/OS entities within 3 tokens.

---

## 5. Claims in the UI that the numbers don't support
1. **Insights, spaCy chart (`site/js/insights.js::drawSpacy`):** `problem_accuracy` can be `null`, and `pct(x || 0)` turns that into "0%". It should say "not measured". The caption *"Spotting what is broken is harder than spotting the device or app"* is hard-coded. It should be shown only when the numbers say so, and it should mention the 0.716 ceiling.
2. **Insights, entity precision** will look low (about 0.8) mostly because the gold file is incomplete (section 4.2). Until the gold file is fixed, the chart should say so.
3. **Insights headline "HelpMate picks the right topic N% of the time"** comes from 48 synthetic questions, with a ±12-point uncertainty. Suggest "about N% on 48 practice questions". The "Hardest topic" line is chosen from 6 questions per topic, and 1-2 question differences are noise.
4. **Insights, VADER chart "Checked on 240 questions"** uses rows the rule was designed on. Show `vader.test` too, or say so.
5. `reports/plan.md` section 4.3 still specifies `ngram_range=(1, 2)` and `alpha=1e-3`, and its `model.json` example shows a bigram. It needs updating to match `nlp/classifier.py`.
6. The README is empty, so there are no claims to check there.

## 6. Limitations
- Small, synthetic, single-author data. 6 test questions per class means per-class numbers move in steps of 0.17. Treat class-to-class differences of 1-2 questions as noise.
- The settings were chosen with `simple_v1`. Stemming in `nltk_clean_v1` changes the vocabulary, so the unigram/alpha choice should be re-checked with `python pipeline/eval_classifier.py --tokenizer nltk_clean_v1` (the ML engineer should do this on a machine with NLTK).
- Some labels are genuinely ambiguous (printer vs wifi, email vs passwords, video_calls vs wifi), and the training rows contradict each other on those boundaries (section 2.4). Better labeling rules would help more than any setting.
- Frustration labels are one person's judgement. No second annotator, so no agreement score.
- The four help formats (See it / Hear it / Try it / Read it) are offered as user choices. Nothing here measures or relies on "learning styles", so that research caveat doesn't affect any number in this report.

## 7. To fill in after the Netlify build
The first deploy log and the deployed `data/metrics.json` will have the real numbers. To copy them in:
1. **Build log** (Netlify → Deploys → the deploy → "Deploy log"): under `[build] Summary`, look for
   - `tokenizer=nltk_clean_v1  accuracy=...`. If it says `simple_v1`, something is wrong.
   - `NLTK frustration (all seed): precision=... recall=... f1=... n=240; test split: precision=... recall=... n=48`
   - `spaCy entities: precision=... recall=... {'tp': .., 'fp': .., 'fn': ..}; problems: exact=... thing=... n=74`
2. **Insights page** (`/insights.html`, "Model quality" section): the same numbers as charts, with the confusion matrix and "Where HelpMate gets it wrong" (up to 5 errors per tool).
3. **Full detail:** open `https://<your-site>.netlify.app/data/metrics.json`. `classifier.per_class`, `classifier.confusion_matrix`, `vader.false_negatives` / `false_positives`, `spacy.errors` and `spacy.problem_errors` hold the real examples. `reports/classifier.md` is rewritten by the build, but on Netlify that copy is not published, so use metrics.json.
4. Replace the tables below, keeping the "local simple_v1" tables above for comparison. Check the predictions in 3.3 and 4.3 against the listed errors and mark each one confirmed or wrong.

| Netlify build (nltk_clean_v1) | Value |
|---|---|
| Classifier accuracy / macro F1 (48 test) | _to fill_ |
| Email recall (weakest locally) | _to fill_ |
| VADER frustration precision / recall / F1 (240 seed) | _to fill_ |
| VADER frustration precision / recall (48 test, 14 frustrated) | _to fill_ |
| spaCy entity precision / recall (91 gold, 125 entities) | _to fill_ |
| spaCy problem exact accuracy (ceiling 0.716) / thing accuracy (74) | _to fill_ |
