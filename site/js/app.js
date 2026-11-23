// HelpMate main script: ask box, results, format buttons, side panel, rating form.
import { el, icon, badge, notice, getJSON, CATEGORIES, CATEGORY_NAMES } from "./dom.js";
import { compilePatterns, findEntities, hintCategory, kindName } from "./entities.js";
import { renderFormat, FORMATS, formatLabel } from "./formats.js";
import { getFormatPref, setFormatPref } from "./progress.js";
import { stopAllSpeech } from "./speech.js";
import { initPanel } from "./panel.js";
import { initRating } from "./rating.js";

const $ = (id) => document.getElementById(id);
const data = { answers: null, lessons: null, patterns: null, examples: null, generated: "" };
const state = { question: "", category: null, format: "see_it", frustrated: false, dispose: null };
const BRAIN_TIMEOUT_MS = 20000;        // answering, once the engine is running
const BRAIN_LOAD_TIMEOUT_MS = 120000;  // first start: Pyodide + NLTK + NumPy can be slow on a first visit
let brainReady = false;
let lastBrainError = "";
const rating = initRating();
const panel = initPanel(() => data.lessons);

// ---- brain.js (Pyodide: NLTK + NumPy). Loaded lazily; any failure means "use the fallback". ----
let brainPromise = null;
function loadBrain() {
  if (!brainPromise) {
    const p = import("./brain.js").then(async (m) => {
      if (typeof m.analyze !== "function") throw new Error("no analyze");
      if (typeof m.onProgress === "function") m.onProgress((t) => { if (!brainReady) setStatus(t, true); });
      if (typeof m.ready === "function") await m.ready();
      brainReady = true;
      return m;
    });
    brainPromise = p;
    p.catch((err) => {
      lastBrainError = (err && err.message) || String(err);
      console.error("HelpMate smart helper failed to start:", lastBrainError);
      if (brainPromise === p) brainPromise = null;   // let the next question retry
    });
  }
  return brainPromise;
}
const withTimeout = (p, ms) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), ms))]);

function setStatus(text, busy) {
  const s = $("engine-status");
  s.replaceChildren(...(busy ? [el("span", { class: "spinner", "aria-hidden": "true" })] : []), el("span", { text }));
}

// ---- data ----
async function loadData() {
  const [answers, lessons, patterns, examples, model] = await Promise.all([
    getJSON("data/answers.json"), getJSON("data/lessons.json"), getJSON("data/entity_patterns.json"),
    getJSON("data/examples.json"), getJSON("data/model.json").catch(() => null)]);
  Object.assign(data, { answers, lessons, examples });
  data.patterns = patterns ? compilePatterns(patterns) : null;
  data.generated = (answers && answers.generated_at) || "";
  if (model && model.generated_at) data.generated = model.generated_at;
  buildChips();
}
const answerFor = (cat) => ((data.answers && data.answers.items) || []).find((a) => a.category === cat);

function buildChips() {
  const list = $("chips-list");
  let texts = ((data.examples && data.examples.items) || []).filter((e) => e.text.length <= 80).map((e) => e.text);
  texts = [...new Set(texts)].slice(0, 4);
  if (!texts.length) texts = ["my printer will not print", "I forgot my password", "my computer is so slow", "my wifi keeps dropping"];
  list.replaceChildren(...texts.map((t) => el("li", {}, el("button", { class: "chip", type: "button", text: t, onclick: () => { $("question").value = t; updateCount(); ask(t); $("question").focus(); } }))));
}

// ---- ask ----
function updateCount() { $("ask-count").textContent = `${$("question").value.length} of 300`; }
$("question").addEventListener("input", () => { updateCount(); clearError(); });
function clearError() { const e = $("question-error"); e.hidden = true; e.replaceChildren(); $("question").removeAttribute("aria-invalid"); }
$("ask-form").addEventListener("submit", (e) => { e.preventDefault(); ask($("question").value); });

async function ask(raw) {
  const text = raw.trim().replace(/\s+/g, " ");
  if (!text) {
    const err = $("question-error");
    err.hidden = false; err.replaceChildren(icon("alert"), el("span", { text: "Please type a few words about your problem first." }));
    $("question").setAttribute("aria-invalid", "true"); $("question").focus();
    return;
  }
  clearError();
  stopAllSpeech();
  state.question = text;
  const results = $("results");
  results.hidden = false;
  $("empty-state").hidden = true;
  $("results-question").textContent = `You asked: “${text}”`;
  results.classList.remove("is-course");
  $("answer").hidden = true;
  $("results-notices").replaceChildren();
  $("understood").replaceChildren(el("p", { class: "visually-hidden", text: "Thinking about your question..." }),
    el("div", { class: "skeleton", style: "height:4rem" }), el("div", { class: "skeleton", style: "height:4rem" }));
  const btn = $("ask-button"); btn.disabled = true;

  if (!data.answers) await loadData();
  const entities = findEntities(text, data.patterns);
  let brain = null, failed = false;
  try {
    if (!brainReady) setStatus("Still getting the smart helper ready. The first visit can take up to a minute...", true);
    const m = await withTimeout(loadBrain(), BRAIN_LOAD_TIMEOUT_MS);
    brain = await withTimeout(m.analyze(text), BRAIN_TIMEOUT_MS);
  } catch (err) {
    failed = true;
    lastBrainError = (err && err.message) || lastBrainError || "unknown";
    console.error("Browser engine not used:", lastBrainError);
  }
  btn.disabled = false;
  if (failed) setStatus("HelpMate is ready (simple mode).", false); else setStatus("HelpMate is ready.", false);
  show(text, entities, failed ? null : brain);
  // On a phone the results sit below the question, so bring them into view.
  if (window.matchMedia("(max-width: 59.99rem)").matches) {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    results.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
  }
}

function show(text, entities, brain) {
  const notices = $("results-notices"), under = $("understood");
  notices.replaceChildren(); under.replaceChildren();
  if (!data.answers || !(data.answers.items || []).length) {
    notices.append(notice("info", null, "HelpMate's answers aren't ready yet. Please try again in a minute."));
    $("answer").hidden = true; return;
  }
  const frustrated = !!(brain && brain.mood && brain.mood.frustrated);
  let category = null, viaBrain = false, unsure = false;
  if (brain && brain.category) { category = brain.category; viaBrain = true; unsure = !!brain.unsure; }
  else {
    category = hintCategory(entities);
    notices.append(notice("error", null, "The smart helper couldn't start, so I matched your words instead. The answer may be less exact.", "alert"));
    if (lastBrainError) notices.append(el("details", { class: "notice-details" }, el("summary", { text: "Technical details" }), el("p", { text: lastBrainError })));
    unsure = !category;
  }
  if (frustrated) notices.append(notice("calm", null, "That sounds frustrating, and that's okay. We'll take it one small step at a time.", "info"));
  if (frustrated) notices.lastChild.append(badge("nltk"));

  // What I understood
  if (viaBrain && category) {
    const pct = Math.round((brain.confidence || 0) * 100);
    const meter = el("span", { class: "meter__track" }, el("span", { class: "meter__fill" }));
    meter.firstChild.style.setProperty("--value", String(pct));
    under.append(el("article", { id: "card-category", class: "card card--category", "aria-labelledby": "card-category-title" },
      el("header", { class: "card__head" }, el("h3", { id: "card-category-title", class: "card__title", text: "I think this is about" }), badge("nn")),
      el("div", { class: "card__body" }, el("p", { class: "card__big", text: CATEGORY_NAMES[category] || category }),
        el("div", { class: "meter" }, meter, el("span", { text: `${pct}% sure` })))));
  } else if (category) {
    under.append(el("article", { id: "card-category", class: "card card--category", "aria-labelledby": "card-category-title" },
      el("header", { class: "card__head" }, el("h3", { id: "card-category-title", class: "card__title", text: "I think this is about" }), badge("spacy")),
      el("div", { class: "card__body" }, el("p", { class: "card__big", text: CATEGORY_NAMES[category] || category }),
        el("p", { text: "I matched the device or app words in your question." }))));
  }
  if (brain && brain.mood) {
    under.append(el("article", { id: "card-mood", class: "card card--mood" },
      el("header", { class: "card__head" }, el("h3", { class: "card__title", text: "How you sound" }), badge("nltk")),
      el("div", { class: "card__body" }, el("p", { text: frustrated
        ? ((answerFor(category) || {}).calm_intro || "That sounds frustrating. Let's slow down and do this together.")
        : "You sound calm. Let's get started." }))));
  }
  if (entities.length) {
    under.append(el("article", { id: "card-things", class: "card card--things" },
      el("header", { class: "card__head" }, el("h3", { class: "card__title", text: "Things you mentioned" }), badge("spacy")),
      el("div", { class: "card__body" }, el("ul", { class: "tags" }, entities.map((e) => el("li", { class: "tag" },
        el("span", { class: "tag__kind", text: kindName(e.label) }), el("span", { text: e.text })))))));
  }
  const ex = ((data.examples && data.examples.items) || []).find((x) => x.text.trim().toLowerCase() === text.toLowerCase());
  if (ex) {
    const probs = ex.problems || [];
    under.append(el("article", { id: "card-breakdown", class: "card card--breakdown" },
      el("header", { class: "card__head" }, el("h3", { class: "card__title", text: "How I read that question" }), badge("both")),
      el("div", { class: "card__body" },
        el("p", { text: probs.length ? "What is wrong (found when the site was built):" : "No clear problem phrase was found in this one." }),
        probs.length ? el("ul", { class: "tags" }, probs.map((p) => el("li", { class: "tag" },
          el("span", { class: "tag__kind", text: p.negated ? "Not working" : "Problem" }), el("span", { text: `${p.thing}: ${p.problem}` })))) : null)));
  }

  if (unsure || !category) {
    notices.append(unsureNotice());
    $("answer").hidden = true;
    rating.show();
    return;
  }
  showAnswer(category, frustrated);
}

function unsureNotice() {
  const n = notice("unsure", null, "I'm not sure yet. Which of these is closest to your problem?", "alert");
  n.querySelector("div").append(el("ul", { class: "chips__list" }, CATEGORIES.map(([id, name]) =>
    el("li", {}, el("button", { class: "chip", type: "button", text: name, onclick: () => { $("results-notices").replaceChildren(); showAnswer(id, false); } })))));
  return n;
}

function showAnswer(category, frustrated) {
  const a = answerFor(category);
  if (!a) { $("results-notices").append(notice("info", null, "HelpMate's answers aren't ready yet. Please try again in a minute.")); return; }
  state.category = category; state.frustrated = frustrated;
  $("answer-title").textContent = a.title;
  $("answer-summary").textContent = a.summary;
  $("answer-tags").replaceChildren(...(a.tags || []).map((t) => el("li", { class: "tag", text: t })));
  $("help-note").textContent = a.when_to_get_help || "";
  const rank = a.format_rank || FORMATS;
  document.querySelectorAll(".format-btn").forEach((b) => {
    const hint = b.querySelector(".format-btn__hint");
    hint.querySelector(".popular")?.remove();
    if (b.dataset.format === rank[0]) hint.append(el("span", { class: "popular", text: " (Popular)" }));
  });
  panel.setCategory(category);
  $("answer").hidden = false;
  const pref = getFormatPref();
  selectFormat(FORMATS.includes(pref) ? pref : "see_it", false);
  rating.show();
  rating.setContext({ question: state.question, category, format: state.format, generated: data.generated });
}

function selectFormat(format, focus) {
  const a = answerFor(state.category); if (!a) return;
  state.dispose?.(); stopAllSpeech();
  state.format = format;
  document.querySelectorAll(".format-btn").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.format === format)));
  const fp = $("format-panel");
  fp.dataset.format = format;
  const r = renderFormat(format, a, { category: state.category, frustrated: state.frustrated });
  state.dispose = r.dispose || null;
  fp.replaceChildren(el("p", { class: "visually-hidden", text: `${formatLabel(format)} help` }), r.node);
  setFormatPref(format);
  rating.setContext({ format });
  if (focus) fp.focus();
}
$("format-buttons").addEventListener("click", (e) => {
  const b = e.target.closest(".format-btn"); if (b) selectFormat(b.dataset.format, true);
});

// ---- start ----
(async function start() {
  await loadData();
  if (!data.answers) {
    $("results").hidden = false; $("empty-state").hidden = true;
    $("results-notices").append(notice("info", null, "HelpMate's answers aren't ready yet. Please try again in a minute."));
  }
  setStatus("Getting HelpMate ready. This can take a few seconds the first time.", true);
  try { await withTimeout(loadBrain(), BRAIN_LOAD_TIMEOUT_MS); setStatus("HelpMate is ready.", false); }
  catch { setStatus("HelpMate is ready (simple mode: it matches your words).", false); }
})();
