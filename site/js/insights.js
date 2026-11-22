/* HelpMate Insights page (Vega). Reads the build's JSON and draws accessible charts.
   Any missing file or null section shows a friendly message and never throws. */
import { el, pct, num1, barList, chartBlock, emptyState, lineChart, heatTable } from "./charts.js";

const NAMES = {
  printer: "Printer", email: "Email", wifi: "Wi-Fi & Internet", passwords: "Passwords & Login",
  slow: "Slow computer", phone_apps: "Phone & Apps", files: "Files & Storage", video_calls: "Video calls",
};
const FORMATS = { see_it: "See it", hear_it: "Hear it", try_it: "Try it", read_it: "Read it" };
const CAT_ORDER = Object.keys(NAMES);
const LATER = "This appears after the Netlify build.";

const $ = (id) => document.getElementById(id);
const body = (id) => document.querySelector(`#${id} .chart-body`);
const name = (c) => NAMES[c] || c;
const setTitle = (id, text) => { const h = $(`${id}-title`); if (h) h.textContent = text; };
const setStat = (id, text) => { const n = $(id); if (n) n.textContent = text; };

async function load(file) {
  try {
    const r = await fetch(`data/${file}`, { cache: "no-cache" });
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    return null;
  }
}

function later(id, why) {
  const host = body(id);
  if (host) emptyState(host, why || LATER, "Not ready yet");
}

/* ---------- NLTK: words, phrases, topics ---------- */
function drawWords(stats) {
  const items = stats && Array.isArray(stats.items) ? stats.items.slice(0, 15) : [];
  if (!items.length) return later("chart-words");
  const top = items[0];
  setTitle("chart-words", `"${top.word}" is the word people use most`);
  chartBlock(body("chart-words"), {
    marks: barList(items.map((i) => ({ label: i.word, value: i.count, display: String(i.count) })), null,
      "Number of times each word appears in the questions"),
    caption: `Across ${stats.n_documents ?? "all"} questions, "${top.word}" appears ${top.count} times (counts are for the base form of each word).`,
    table: { caption: "Most common words in the questions", headers: ["Word", "Times used"],
      rows: stats.items.map((i) => [i.word, i.count]), numCols: [1] },
  });
}

function drawPhrases(stats) {
  const items = stats && Array.isArray(stats.top_phrases) ? stats.top_phrases : [];
  if (!items.length) return later("chart-phrases", "No word pairs showed up often enough yet. " + LATER);
  const top = items[0];
  setTitle("chart-phrases", `"${top.phrase}" is the pair of words people use together most`);
  chartBlock(body("chart-phrases"), {
    marks: barList(items.slice(0, 12).map((i) => ({ label: i.phrase, value: i.count, display: String(i.count) })), null,
      "Number of times each pair of words appears together"),
    caption: `"${top.phrase}" shows up ${top.count} times. Pairs are only listed if they appear at least 3 times.`,
    table: { caption: "Common word pairs", headers: ["Word pair", "Times together", "Strength score"],
      rows: items.map((i) => [i.phrase, i.count, num1(i.score)]), numCols: [1, 2] },
  });
}

function drawCategories(stats) {
  const bc = stats && stats.by_category;
  if (!bc || !Object.keys(bc).length) return later("chart-categories");
  const rows = CAT_ORDER.filter((c) => bc[c]).map((c) => ({ c, n: bc[c].n || 0, word: (bc[c].top_words || [])[0] }));
  rows.sort((a, b) => b.n - a.n);
  const top = rows[0];
  setTitle("chart-categories", `${name(top.c)} is the topic we have the most questions about`);
  chartBlock(body("chart-categories"), {
    marks: barList(rows.map((r) => ({ label: name(r.c), value: r.n, display: String(r.n) })), null, "Questions per topic"),
    caption: `${name(top.c)} has ${top.n} questions. Topics with fewer questions are harder for HelpMate to learn.`,
    table: { caption: "Questions studied per topic", headers: ["Topic", "Questions", "Top word"],
      rows: rows.map((r) => [name(r.c), r.n, r.word ? r.word.word : "-"]), numCols: [1] },
  });
}

/* ---------- NLTK: ratings ---------- */
function weighted(items, key) {
  const m = new Map();
  for (const it of items) {
    const k = it[key];
    const cur = m.get(k) || { count: 0, sum: 0 };
    cur.count += it.count || 0;
    cur.sum += (it.count || 0) * (it.avg_stars || 0);
    m.set(k, cur);
  }
  return [...m].map(([k, v]) => ({ key: k, count: v.count, avg: v.count ? v.sum / v.count : 0 }));
}

function drawRatings(r) {
  const noRatings = !r || !r.total;
  const msg = "No ratings yet. Be the first to rate an answer on the Get help page.";
  if (noRatings) {
    for (const id of ["chart-ratings", "chart-rating-categories", "chart-formats", "chart-sentiment"]) later(id, msg);
    return;
  }
  const weeks = (r.by_week || []).slice(-12);
  if (weeks.length) {
    const last = weeks[weeks.length - 1];
    setTitle("chart-ratings", weeks.length > 1
      ? `Average stars were ${num1(last.avg_stars)} in the latest week`
      : `Average stars so far: ${num1(last.avg_stars)}`);
    const pts = weeks.map((w) => ({ value: w.avg_stars, label: String(w.week).replace(/^\d{4}-/, "") }));
    chartBlock(body("chart-ratings"), {
      marks: lineChart(pts, { id: "line-weeks", xLabel: "Week of the year", yLabel: "Average stars (1 to 5)",
        title: "Average star rating by week",
        desc: pts.map((p, i) => `${weeks[i].week}: ${num1(p.value)} stars from ${weeks[i].count} ratings`).join(". ") }),
      caption: `${r.total} ratings in total. A higher line means people found the help more useful.`,
      table: { caption: "Ratings by week", headers: ["Week", "Ratings", "Average stars"],
        rows: weeks.map((w) => [w.week, w.count, num1(w.avg_stars)]), numCols: [1, 2] },
    });
  } else later("chart-ratings", "Ratings are in, but not yet grouped by week. " + LATER);

  const items = r.items || [];
  const cats = weighted(items, "category").sort((a, b) => b.avg - a.avg);
  if (cats.length) {
    setTitle("chart-rating-categories", `${name(cats[0].key)} answers get the best stars (${num1(cats[0].avg)})`);
    chartBlock(body("chart-rating-categories"), {
      marks: barList(cats.map((c) => ({ label: name(c.key), value: c.avg, display: `${num1(c.avg)} (${c.count})` })), 5,
        "Average stars by topic, out of 5, with the number of ratings in brackets"),
      caption: `Bars run from 0 to 5 stars; the number in brackets is how many ratings it is based on.`,
      table: { caption: "Average stars by topic", headers: ["Topic", "Ratings", "Average stars"],
        rows: cats.map((c) => [name(c.key), c.count, num1(c.avg)]), numCols: [1, 2] },
    });
  } else later("chart-rating-categories");

  const fmts = weighted(items, "format").sort((a, b) => b.avg - a.avg);
  if (fmts.length) {
    setTitle("chart-formats", `"${FORMATS[fmts[0].key] || fmts[0].key}" gets the best stars (${num1(fmts[0].avg)})`);
    chartBlock(body("chart-formats"), {
      marks: barList(fmts.map((c) => ({ label: FORMATS[c.key] || c.key, value: c.avg, display: `${num1(c.avg)} (${c.count})` })), 5,
        "Average stars by help format, out of 5"),
      caption: "HelpMate shows the best-rated format first for each topic on the next rebuild.",
      table: { caption: "Average stars by help format", headers: ["Format", "Ratings", "Average stars"],
        rows: fmts.map((c) => [FORMATS[c.key] || c.key, c.count, num1(c.avg)]), numCols: [1, 2] },
    });
  } else later("chart-formats");

  const s = r.sentiment;
  if (s && s.positive !== null && s.positive !== undefined) {
    const rows = [["Positive", s.positive], ["Neutral", s.neutral], ["Negative", s.negative]];
    const total = rows.reduce((a, x) => a + (x[1] || 0), 0) || 1;
    const best = [...rows].sort((a, b) => b[1] - a[1])[0];
    setTitle("chart-sentiment", `Most comments sound ${best[0].toLowerCase()} (${pct(best[1] / total)})`);
    chartBlock(body("chart-sentiment"), {
      marks: barList(rows.map(([l, v]) => ({ label: l, value: v || 0, display: `${v || 0} (${pct((v || 0) / total)})` })), null,
        "Number of comments by mood"),
      caption: "NLTK's VADER reads each comment and sorts it as positive, neutral or negative. Only counts are kept, never the comment text.",
      table: { caption: "Comment mood", headers: ["Mood", "Comments"], rows, numCols: [1] },
    });
  } else later("chart-sentiment", "Comment moods are not counted yet. " + LATER);
}

/* ---------- Model quality ---------- */
function drawClassifier(c) {
  if (!c) { later("chart-nn"); later("chart-confusion"); return; }
  setStat("stat-accuracy", pct(c.accuracy));
  setTitle("chart-nn", `HelpMate is about ${pct(c.accuracy)} right on ${c.n_test} practice questions`);
  const labels = CAT_ORDER.filter((k) => c.per_class && c.per_class[k]);
  const rows = labels.map((k) => ({ k, ...c.per_class[k] })).sort((a, b) => a.recall - b.recall);
  const weak = rows[0];
  chartBlock(body("chart-nn"), {
    marks: barList(rows.map((r) => ({ label: name(r.k), value: r.recall * 100, display: pct(r.recall) })), 100,
      "Share of each topic's test questions that were found, in percent"),
    caption: `Accuracy ${pct(c.accuracy)}, macro F1 ${num1(c.macro_f1 * 100)}%, on ${c.n_test} new questions. Hardest topic: ${weak ? name(weak.k) + " (" + pct(weak.recall) + ")" : "n/a"}. Words are split by: ${c.tokenizer}.`,
    table: { caption: "Per-topic results on test questions", headers: ["Topic", "Test questions", "Found (recall)", "Precision", "F1"],
      rows: rows.map((r) => [name(r.k), r.support, pct(r.recall), pct(r.precision), pct(r.f1)]), numCols: [1, 2, 3, 4] },
  });
  const note = el("p", { class: "chart__caption" }, [
    `Trained on ${c.n_train} questions and tested on ${c.n_test} others. Test set: ${c.test_set}.`]);
  body("chart-nn").append(note);
  if (c.tokenizer === "simple_v1") {
    notes.push("The quality numbers below come from a local test run that used a simple word splitter. They will change after the Netlify build.");
  }

  const cm = c.confusion_matrix;
  if (cm && cm.labels && cm.matrix) {
    let worst = null;
    cm.matrix.forEach((row, i) => row.forEach((v, j) => {
      if (i !== j && (!worst || v > worst.v)) worst = { v, i, j };
    }));
    setTitle("chart-confusion", worst && worst.v > 0
      ? `${name(cm.labels[worst.i])} is most often mixed up with ${name(cm.labels[worst.j])}`
      : "HelpMate made no topic mix-ups on the test questions");
    const host = body("chart-confusion");
    host.replaceChildren(
      el("figure", { class: "chart" }, [
        heatTable(cm.labels, cm.matrix, NAMES),
        el("figcaption", { class: "chart__caption", text: worst && worst.v > 0
          ? `Darker cells hold more questions. The bold boxed cells are right guesses. The biggest mix-up: ${worst.v} ${name(cm.labels[worst.i])} question(s) were sorted as ${name(cm.labels[worst.j])}.`
          : "Every test question landed on its own topic (the bold boxed cells)." }),
      ]));
  } else later("chart-confusion");
}

function drawVader(v, stats) {
  if (stats && stats.frustration && stats.frustration.n) {
    setStat("stat-frustration", pct(stats.frustration.rate));
  }
  if (!v) return later("chart-vader");
  setTitle("chart-vader", `NLTK catches ${pct(v.recall)} of frustrated questions`);
  const t = v.test;
  const rows = [["Precision, all rows", v.precision], ["Recall, all rows", v.recall], ["F1 score, all rows", v.f1]];
  if (t) rows.push([`Precision, ${t.n} test questions`, t.precision], [`Recall, ${t.n} test questions`, t.recall],
    [`F1 score, ${t.n} test questions`, t.f1]);
  const testNote = t
    ? ` The fairer check is the ${t.n} test questions (${t.n_frustrated} frustrated): precision ${pct(t.precision)}, recall ${pct(t.recall)}. The all-rows scores are probably too good, because the rules were written while looking at those questions.`
    : " These rows were also used to write the rules, so the scores are probably too good.";
  chartBlock(body("chart-vader"), {
    marks: barList(rows.map(([l, x]) => ({ label: l, value: x * 100, display: pct(x) })), 100,
      "Frustration spotting scores, in percent"),
    caption: `Of the questions NLTK flagged, ${pct(v.precision)} really were frustrated (precision). Of all frustrated questions, it found ${pct(v.recall)} (recall). Checked on ${v.n} questions.${testNote}`,
    table: { caption: "Frustration spotting scores", headers: ["Measure", "Score"],
      rows: rows.map(([l, x]) => [l, pct(x)]), numCols: [1] },
  });
}

function drawSpacy(s) {
  if (!s) return later("chart-spacy");
  setTitle("chart-spacy", `spaCy finds ${pct(s.entity_recall)} of the devices and apps people mention`);
  if (s.entity_recall === null || s.entity_recall === undefined) setTitle("chart-spacy", "spaCy device and app finding is not measured yet");
  const has = (x) => x !== null && x !== undefined;
  const rows = [["Entity recall (found)", s.entity_recall], ["Entity precision (correct)", s.entity_precision],
    ["Problem accuracy (exact wording)", s.problem_accuracy]];
  if (has(s.problem_thing_accuracy)) rows.push(["Broken thing found", s.problem_thing_accuracy]);
  const show = (x) => (has(x) ? pct(x) : "not measured");
  let cap = `Checked against ${s.n} hand-labelled questions.`;
  if (!has(s.problem_accuracy)) {
    cap += " Problem accuracy is not measured, because no questions had a hand-labelled problem.";
  } else {
    const n = s.problem_n ? ` (${s.problem_n} questions)` : "";
    cap += ` Exact problem accuracy is ${pct(s.problem_accuracy)}${n}.`;
    if (has(s.problem_thing_accuracy)) cap += ` Finding the right broken thing, even with different wording, is ${pct(s.problem_thing_accuracy)}.`;
    if (has(s.problem_accuracy) && has(s.entity_recall) && s.problem_accuracy < s.entity_recall) {
      cap += " Spotting what is broken is harder than spotting the device or app.";
    }
    cap += has(s.problem_ceiling)
      ? ` Exact matching is strict: the best possible exact score on this answer key is about ${num1(s.problem_ceiling)}.`
      : " Exact matching is strict: a correct answer worded differently from the answer key counts as wrong, so this score is a low estimate.";
  }
  if (has(s.entity_precision) && s.entity_precision < 0.9) {
    cap += " Precision may look low because the answer key leaves out some real mentions.";
  }
  chartBlock(body("chart-spacy"), {
    marks: barList(rows.map(([l, x]) => ({ label: l, value: (x || 0) * 100, display: show(x) })), 100,
      "spaCy scores against hand-checked answers, in percent"),
    caption: cap,
    table: { caption: "spaCy scores against hand-checked answers", headers: ["Measure", "Score"],
      rows: rows.map(([l, x]) => [l, show(x)]), numCols: [1] },
  });
}

function errorList(title, badgeClass, badgeText, items, render) {
  const sec = el("section", { class: "error-group" }, [
    el("h3", { class: "card__title" }, [title + " "]),
  ]);
  sec.firstChild.append(el("span", { class: `badge ${badgeClass}`, text: badgeText }));
  const ul = el("ul", { class: "error-list" }, items.slice(0, 5).map((it) => el("li", { text: render(it) })));
  sec.append(ul);
  return sec;
}

function drawErrors(m) {
  const host = body("chart-errors");
  if (!m) return later("chart-errors");
  const groups = [];
  const mis = m.classifier && m.classifier.misclassified;
  if (mis && mis.length) groups.push(errorList("Topic mix-ups", "badge--nn", "Neural network", mis,
    (e) => `"${e.text}" is about ${name(e.true)}, but HelpMate guessed ${name(e.pred)} (${pct(e.confidence)} sure).`));
  const fn = m.vader && m.vader.false_negatives;
  if (fn && fn.length) groups.push(errorList("Frustration missed", "badge--nltk", "NLTK", fn,
    (t) => `"${t}" sounds frustrated, but HelpMate did not notice.`));
  const fp = m.vader && m.vader.false_positives;
  if (fp && fp.length) groups.push(errorList("Frustration guessed wrongly", "badge--nltk", "NLTK", fp,
    (t) => `"${t}" was flagged as frustrated, but it was not.`));
  const se = m.spacy && m.spacy.errors;
  if (se && se.length) groups.push(errorList("Devices and apps","badge--spacy", "spaCy", se,
    (e) => `"${e.text}": expected ${JSON.stringify(e.expected)}, got ${JSON.stringify(e.got)}.`));
  const pe = m.spacy && m.spacy.problem_errors;
  if (pe && pe.length) groups.push(errorList("What is broken (problems)", "badge--spacy", "spaCy", pe,
    (e) => `"${e.text}": expected ${JSON.stringify(e.expected)}, got ${JSON.stringify(e.got)}.`));
  if (!groups.length) return emptyState(host, "No mistakes were recorded for the test questions. " + LATER, "Nothing to show yet");
  setTitle("chart-errors", "Where HelpMate gets it wrong");
  host.replaceChildren(el("p", { text: "Showing mistakes openly helps us fix them. Up to five examples from each tool:" }), ...groups);
}

/* ---------- main ---------- */
const notes = [];

async function main() {
  const [stats, ratings, metrics] = await Promise.all([load("nltk_stats.json"), load("ratings_summary.json"), load("metrics.json")]);
  const status = $("insights-status");

  if (stats) {
    setStat("stat-questions", String(stats.n_documents ?? "-"));
  }
  setStat("stat-ratings", ratings ? String(ratings.total ?? 0) : "-");

  drawWords(stats); drawPhrases(stats); drawCategories(stats);
  drawRatings(ratings);
  drawClassifier(metrics && metrics.classifier);
  drawVader(metrics && metrics.vader, stats);
  drawSpacy(metrics && metrics.spacy);
  drawErrors(metrics);

  if (!stats && !ratings && !metrics) {
    status.replaceChildren(el("span", { text: "The charts are not ready yet. " + LATER }));
    status.className = "notice notice--info";
    return;
  }
  const missing = [];
  if (!stats) missing.push("common words");
  if (!ratings) missing.push("ratings");
  if (!metrics) missing.push("quality checks");
  const sample = [stats, ratings, metrics].some((d) => d && d.fixture === true);
  if (sample) notes.push("Some of these numbers are sample data used to show how the page works. Real numbers appear after the Netlify build.");
  if (ratings && !ratings.total) notes.push("No ratings yet. Be the first to rate an answer.");
  if (missing.length) notes.push(`Not ready yet: ${missing.join(", ")}. ${LATER}`);
  status.replaceChildren(el("span", { text: notes.length ? "Charts are ready. See the notes below." : "Charts are ready." }));
  const host = $("insights-notes");
  for (const n of notes) {
    host.append(el("div", { class: "notice notice--info" }, [el("p", { class: "notice__text", text: n })]));
  }
}

main().catch((e) => {
  const status = $("insights-status");
  status.replaceChildren(el("span", { text: "Something went wrong while drawing the charts. Please try again in a minute." }));
  status.className = "notice notice--error";
});
