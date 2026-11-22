# 3. Dataset: IT help questions

**Recommendation:** combine a small sample of a public ticket dataset with a hand-written "plain-language" seed set. Public tickets are written formally; HelpMate users write casually ("my printer won't print!!"), so the seed set is needed for realism and for testing.

## Option A (recommended): Customer Support Tickets, Hugging Face

| | |
|---|---|
| Link | https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets |
| License | CC BY-NC 4.0 (non-commercial use with attribution: fine for a class project) |
| Size | ~61,800 tickets, English and German |
| Useful fields | `subject`, `body`, `answer`, `type`, `queue`, `priority`, `language`, `tag_1`…`tag_8` |
| Useful queues | `IT Support`, `Technical Support`, `Product Support`, `Service Outages and Maintenance` |
| Credit | Creator: Softoft; DOI 10.57967/hf/6184 |

**How to use it:** keep `language == "en"` and the IT/technical queues, sample about 300–500 tickets, and map their tags into HelpMate's 8 categories (Printer, Email, Wi-Fi/Internet, Passwords/Login, Computer slow, Phone/Apps, Files/Storage, Video calls). The page does not clearly say whether the tickets are synthetic, so state that in the report.

## Option B: Super User (Stack Exchange data dump)

Real questions from everyday computer users, licensed CC BY-SA (version depends on post date). The full dump is large (tens of GB) and attribution rules require linking each question and author, so only use it if the team wants real-world text and can meet attribution. ([data dump on archive.org](https://archive.org/details/stackexchange_20251231), [license notes](https://huggingface.co/datasets/flymin/stackexchange_20260331))

## Option C (always do this): HelpMate seed set

The dataset curator writes ~10–15 plain-language questions per category (80–120 total), including frustrated ones ("I've tried EVERYTHING!!"), misspellings and vague ones ("computer is being weird"). This set is our own (no license issue), drives the demo, and is the honest test set for the classifier and VADER.

## Labels and splits

- Category label (8 classes) for the neural network.
- Optional frustration label (yes/no) on the seed set to measure VADER.
- Split 80/20 train/test with a fixed random seed; report accuracy and a confusion matrix.

## Sources
- https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
- https://archive.org/details/stackexchange_20251231
- https://stackoverflow.com/help/licensing
