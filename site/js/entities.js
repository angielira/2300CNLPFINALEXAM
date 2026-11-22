// Finds device / app / OS / error-code words in a question, using the vocabulary that spaCy's
// EntityRuler uses (exported to data/entity_patterns.json at build time). spaCy itself never runs here.
const KIND = { DEVICE: "Device", APP: "App", OS: "System", ERROR_CODE: "Error code", ORG: "Company", PRODUCT: "Product" };
export const kindName = (label) => KIND[label] || "Thing";

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

export function compilePatterns(data) {
  const phrases = [];
  for (const it of (data && data.items) || []) {
    for (const p of it.phrases || []) {
      if (!p) continue;
      phrases.push({ phrase: p.toLowerCase(), id: it.id, label: it.label, hint: it.category_hint || null,
        re: new RegExp("(^|[^a-z0-9])" + esc(p.toLowerCase()) + "(?=[^a-z0-9]|$)", "g") });
    }
  }
  phrases.sort((a, b) => b.phrase.length - a.phrase.length); // longest first
  const regex = [];
  for (const r of (data && data.regex) || []) {
    try { regex.push({ label: r.label, re: new RegExp(r.pattern, (r.flags || "").replace(/[^gimsuy]/g, "") + "g") }); } catch { /* skip bad pattern */ }
  }
  return { phrases, regex };
}

export function findEntities(text, compiled) {
  if (!compiled) return [];
  const lower = text.toLowerCase();
  const taken = [], found = [];
  const free = (s, e) => !taken.some(([a, b]) => s < b && e > a);
  for (const p of compiled.phrases) {
    p.re.lastIndex = 0;
    let m;
    while ((m = p.re.exec(lower))) {
      const s = m.index + m[1].length, e = s + p.phrase.length;
      if (free(s, e)) { taken.push([s, e]); found.push({ text: text.slice(s, e), label: p.label, id: p.id, hint: p.hint, start: s }); }
      p.re.lastIndex = Math.max(p.re.lastIndex, e);
    }
  }
  for (const r of compiled.regex) {
    r.re.lastIndex = 0;
    let m;
    while ((m = r.re.exec(text))) {
      if (m[0] === "") { r.re.lastIndex++; continue; }
      const s = m.index, e = s + m[0].length;
      if (free(s, e)) { taken.push([s, e]); found.push({ text: m[0], label: r.label, id: null, hint: null, start: s }); }
    }
  }
  return found.sort((a, b) => a.start - b.start);
}

// The category most often hinted by the entities (first mention wins ties), or null.
export function hintCategory(entities) {
  const counts = new Map();
  for (const e of entities) if (e.hint) counts.set(e.hint, (counts.get(e.hint) || 0) + 1);
  let best = null, n = 0;
  for (const [k, v] of counts) if (v > n) { best = k; n = v; }
  return best;
}
