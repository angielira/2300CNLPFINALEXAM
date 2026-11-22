// Small DOM helpers. Text always goes in through textContent, never innerHTML.
const SVG_NS = "http://www.w3.org/2000/svg";

const ICONS = {
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  speaker: '<path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 010 7M19 6a8.5 8.5 0 010 12"/>',
  "check-square": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 12.5l3 3 5-6"/>',
  document: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
  play: '<path d="M7 4.5v15l12-7.5z"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="1"/>',
  x: '<path d="M6 6l12 12M18 6L6 18"/>',
  star: '<path d="M12 3.5l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-3-5.4 3 1.1-6L3.2 9.9l6.1-.8z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
  alert: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
  medal: '<circle cx="12" cy="9" r="6"/><path d="M8.5 14L7 21l5-3 5 3-1.5-7"/>',
  print: '<path d="M7 9V3h10v6M7 17H4v-7h16v7h-3"/><rect x="7" y="14" width="10" height="7"/>',
};
const FILLED = new Set(["play", "stop", "star-fill"]);

export function icon(name, extra = "") {
  const s = document.createElementNS(SVG_NS, "svg");
  s.setAttribute("class", "icon" + (FILLED.has(name) ? " icon--fill" : "") + (extra ? " " + extra : ""));
  s.setAttribute("aria-hidden", "true");
  s.setAttribute("focusable", "false");
  s.setAttribute("viewBox", "0 0 24 24");
  s.innerHTML = ICONS[name] || ""; // static constant strings only
  return s;
}

export function el(tag, attrs = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === false || v == null) continue;
    if (k === "class") n.className = v;
    else if (k === "text") n.textContent = v;
    else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : String(v));
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    n.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return n;
}

export const CATEGORIES = [
  ["printer", "Printer"], ["email", "Email"], ["wifi", "Wi-Fi & Internet"], ["passwords", "Passwords & Login"],
  ["slow", "Slow computer"], ["phone_apps", "Phone & Apps"], ["files", "Files & Storage"], ["video_calls", "Video calls"],
];
export const CATEGORY_NAMES = Object.fromEntries(CATEGORIES);

const BADGES = {
  nltk: ["badge--nltk", "NLTK", "made by NLTK in your browser"],
  spacy: ["badge--spacy", "spaCy", "made by spaCy when the site was built"],
  nn: ["badge--nn", "Neural network", "made by HelpMate's neural network in your browser"],
  both: ["badge--both", "NLTK + spaCy", "made by NLTK and spaCy"],
};
export function badge(kind) {
  const [cls, text, why] = BADGES[kind];
  return el("span", { class: "badge " + cls, title: why[0].toUpperCase() + why.slice(1) },
    el("span", { text }), el("span", { class: "visually-hidden", text: ", " + why }));
}

export function notice(kind, title, text, iconName = "info") {
  return el("div", { class: "notice notice--" + kind },
    icon(iconName, "notice__icon"),
    el("div", {}, title ? el("p", { class: "notice__title", text: title }) : null, text ? el("p", { class: "notice__text", text }) : null));
}

export async function getJSON(path) {
  try {
    const r = await fetch(path, { cache: "no-cache" });
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}
