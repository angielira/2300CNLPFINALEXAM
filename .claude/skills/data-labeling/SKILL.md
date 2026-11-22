---
name: data-labeling
description: "Label questions with HelpMate's 8 categories and a frustration flag, consistently. Use when building or extending training and test data."
---

# data-labeling

Used by: ml-engineer, dataset-curator, nlp-evaluator

## Categories
Printer · Email · Wi-Fi/Internet · Passwords/Login · Computer slow · Phone/Apps · Files/Storage · Video calls

## Rules
- One category per question: the thing the user needs fixed first.
- `frustrated = yes` if the writer shows strong negative emotion (caps, "!!", "nothing works", "again").
- Keep a `source` column: `seed`, `tickets`, or `feedback`.
- Hold out 20% (stratified, seed 42) as the test set; never train on it.
