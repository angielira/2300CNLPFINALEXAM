---
name: local-progress
description: "Save learning progress and badges in localStorage safely. Use for the Learn-more side panel."
---

# local-progress

Used by: instructional-designer, frontend-engineer

## Recipe
```js
const KEY = "helpmate.progress.v1";
function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } }
function save(p) { try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { console.warn(e.name); } }
// p = { "Printer": { done: [1,2,3], badge: false }, ... }
```
- Values are strings: always JSON.stringify / JSON.parse.
- Storage is per origin and may be cleared in private browsing: the app must still work without it.
