# displaCy

- `displacy.render(doc, style="dep" | "ent")` returns markup; `displacy.serve` starts a local server.
- Options: dep `compact`, `color`, `bg`, `font`; ent `ents` (filter labels) and `colors` (custom label colors).
- `page=True` wraps a full HTML page; SVG export works one Doc at a time.

## HelpMate use
Save a few dependency SVGs and an entity view to `reports/` to explain successes and failures.

## Sources
- https://spacy.io/usage/visualizers
