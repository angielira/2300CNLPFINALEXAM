---
name: quality-reporting
description: "Report HelpMate's NLP quality honestly with metrics and real error examples. Use for reports/ files and the final summary."
---

# quality-reporting

Used by: ml-engineer, qa-engineer, nlp-evaluator

## Report shape
1. What was measured and on which data (sizes, sources).
2. Metrics table (accuracy, macro precision/recall/F1; VADER frustration precision/recall).
3. Confusion matrix.
4. 3-5 real failure examples per component with the likely cause.
5. What we changed after measuring, and the new numbers.
- Never round up or hide weak results.
