// Progress and preferences in localStorage. Every read and write is wrapped in try/catch,
// and the app keeps working (in memory) if storage is blocked.
const KEY = "helpmate.progress.v1";
let memory = null;

function fresh() { return { version: 1, format_pref: "see_it", categories: {} }; }

export function load() {
  try {
    const raw = localStorage.getItem(KEY);
    const p = raw ? JSON.parse(raw) : null;
    if (p && typeof p === "object" && p.categories && typeof p.categories === "object") return p;
  } catch { /* blocked or corrupt: start fresh */ }
  return memory || fresh();
}
function save(p) {
  memory = p;
  try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { console.warn("Progress not saved:", e && e.name); }
}
function cat(p, id) {
  const c = p.categories[id] || (p.categories[id] = { done: [], correct: [], try: [], badge: false, updated: "" });
  c.done = c.done || []; c.correct = c.correct || []; c.try = c.try || [];
  return c;
}

export function getFormatPref() { return load().format_pref || "see_it"; }
export function setFormatPref(f) { const p = load(); p.format_pref = f; save(p); }

export function getCategory(id) { return cat(load(), id); }
export function markStep(id, n, correct, totalSteps = 10) {
  const p = load(); const c = cat(p, id);
  if (!c.done.includes(n)) c.done.push(n);
  if (correct && !c.correct.includes(n)) c.correct.push(n);
  c.done.sort((a, b) => a - b);
  const justEarned = !c.badge && c.done.length >= totalSteps;
  if (justEarned) c.badge = true;
  c.updated = new Date().toISOString();
  save(p);
  return { cat: c, justEarned };
}
export function getTry(id) { return new Set(getCategory(id).try); }
export function setTry(id, tryId, on) {
  const p = load(); const c = cat(p, id);
  c.try = c.try.filter((x) => x !== tryId);
  if (on) c.try.push(tryId);
  c.updated = new Date().toISOString();
  save(p);
}
