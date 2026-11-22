"""One-off sampler for data/tickets_sample.csv (dataset-curator, Tally).

Run this by hand on a machine WITH network access. It is not part of the Netlify build.

    pip install datasets
    python data/fetch_tickets.py --out data/tickets_sample.csv --n 400

Source: Hugging Face dataset Tobi-Bueck/customer-support-tickets
  https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
  License: CC BY-NC 4.0 (non-commercial use with attribution). Creator: Softoft.
  DOI: 10.57967/hf/6184. The page does not clearly say whether the tickets are real or synthetic.

What it does:
  * keeps English tickets (language == "en") in IT / technical queues,
  * maps the ticket text and tags onto HelpMate's 8 categories with keyword rules,
  * masks e-mail addresses and phone numbers,
  * writes at most --n rows with columns: id, text, category, source, orig_queue, orig_tags.
Tickets are used only as extra TRAINING rows. The test split is always the seed set.
"""
import argparse
import csv
import random
import re

DATASET = "Tobi-Bueck/customer-support-tickets"
IT_QUEUES = {"IT Support", "Technical Support"}

# Keyword rules, one list per HelpMate category id (see nlp/common.py section 2 of reports/plan.md).
KEYWORDS = {
    "printer": ["printer", "print", "toner", "ink", "paper jam", "scanner"],
    "email": ["email", "e-mail", "outlook", "inbox", "mailbox", "spam", "smtp"],
    "wifi": ["wifi", "wi-fi", "internet", "network", "router", "vpn", "connection", "dns"],
    "passwords": ["password", "login", "log in", "sign in", "locked", "two-factor", "2fa", "authentication"],
    "slow": ["slow", "performance", "freeze", "freezing", "crash", "lag", "memory", "speed"],
    "phone_apps": ["app", "phone", "iphone", "android", "mobile", "smartphone", "tablet"],
    "files": ["file", "folder", "storage", "backup", "drive", "disk", "upload", "download", "document"],
    "video_calls": ["video", "webcam", "microphone", "zoom", "teams", "meeting", "camera", "audio"],
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def mask(text: str) -> str:
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    return re.sub(r"\s+", " ", text).strip()


def map_category(text: str):
    low = text.lower()
    best, best_hits = None, 0
    for cat, words in KEYWORDS.items():
        hits = sum(1 for w in words if re.search(r"\b" + re.escape(w), low))
        if hits > best_hits:
            best, best_hits = cat, hits
    return best


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/tickets_sample.csv")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    from datasets import load_dataset  # imported here so the file compiles without the package

    ds = load_dataset(DATASET, split="train")
    rows = []
    for i, ex in enumerate(ds):
        if ex.get("language") != "en" or ex.get("queue") not in IT_QUEUES:
            continue
        subject = ex.get("subject") or ""
        body = ex.get("body") or ""
        text = mask(f"{subject}. {body}")[:400]
        tags = [str(ex[f"tag_{k}"]) for k in range(1, 9) if ex.get(f"tag_{k}")]
        cat = map_category(f"{text} {' '.join(tags)}")
        if cat is None or len(text) < 20:
            continue
        rows.append({
            "id": f"t{i:06d}",
            "text": text,
            "category": cat,
            "source": "tickets",
            "orig_queue": ex.get("queue"),
            "orig_tags": "|".join(tags),
        })

    random.Random(args.seed).shuffle(rows)
    rows = rows[: args.n]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "text", "category", "source", "orig_queue", "orig_tags"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
