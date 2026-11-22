// "Learn more: 10 steps" side panel: lesson, quiz, progress bar, badge medals.
import { el, icon, badge, CATEGORY_NAMES } from "./dom.js";
import { getCategory, markStep, load } from "./progress.js";

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), textarea, select, [tabindex]:not([tabindex="-1"])';

export function initPanel(getLessons) {
  const panel = document.getElementById("learn-panel");
  const backdrop = document.getElementById("panel-backdrop");
  const openBtn = document.getElementById("learn-open");
  const closeBtn = document.getElementById("learn-close");
  const body = document.getElementById("learn-body");
  const title = document.getElementById("learn-title");
  const back = document.getElementById("learn-back");
  const next = document.getElementById("learn-next");
  const outside = () => ["site-header", "main", "site-footer"].map((s) => document.querySelector(s === "main" ? "main" : "." + s)).filter(Boolean);
  let category = null, step = 1, lesson = null, returnTo = null;

  const lessonFor = (id) => ((getLessons() || {}).items || []).find((l) => l.category === id);

  function render(focusLesson = false) {
    if (!lesson) return;
    const prog = getCategory(category);
    const total = lesson.steps.length;
    const s = lesson.steps.find((x) => x.n === step) || lesson.steps[0];
    const done = new Set(prog.done);
    title.textContent = lesson.title;
    body.replaceChildren();

    const fill = el("span", { class: "progress__fill" });
    fill.style.setProperty("--value", String(Math.round((100 * done.size) / total)));
    body.append(el("div", { class: "progress" },
      el("div", { class: "progress__label" }, el("span", { text: "Your progress" }), el("span", { id: "progress-text", text: `${done.size} of ${total} steps` })),
      el("div", { class: "progress__track", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(total), "aria-valuenow": String(done.size), "aria-label": "Mini-course progress" }, fill)));

    body.append(el("ol", { class: "dots" }, lesson.steps.map((x) => el("li", {},
      el("button", { class: "dot" + (done.has(x.n) ? " is-done" : ""), type: "button", "aria-label": `Step ${x.n}${done.has(x.n) ? ", done" : ""}`,
        "aria-current": x.n === s.n ? "step" : false, text: String(x.n), onclick: () => { step = x.n; render(true); } })))));

    // quiz
    const radios = [];
    const feedback = el("p", { class: "quiz__feedback", role: "status", hidden: true });
    const quiz = el("fieldset", { class: "quiz" }, el("legend", { class: "quiz__q", text: s.check_question }),
      s.choices.map((c, i) => {
        const r = el("input", { type: "radio", name: "check", value: String(i) }); radios.push(r);
        return el("label", { class: "choice" }, r, el("span", { text: c }));
      }));
    const check = el("button", { class: "btn btn--primary", type: "button", text: "Check my answer" });
    check.addEventListener("click", () => {
      const pick = radios.find((r) => r.checked);
      feedback.hidden = false; feedback.className = "quiz__feedback";
      if (!pick) { feedback.classList.add("is-try-again"); feedback.textContent = "Pick one answer first, then check."; return; }
      radios.forEach((r) => r.closest(".choice").classList.remove("is-correct", "is-wrong"));
      const ok = Number(pick.value) === s.answer;
      pick.closest(".choice").classList.add(ok ? "is-correct" : "is-wrong");
      if (ok) {
        feedback.classList.add("is-correct");
        feedback.textContent = "Yes! Nicely done." + (s.explain ? " " + s.explain : "");
        const res = markStep(category, s.n, true, total);
        refreshProgress(res.cat, total);
        if (res.justEarned) celebrate();
        updateMedals();
      } else {
        feedback.classList.add("is-try-again");
        feedback.textContent = "Not quite. Have another look at the example, then try again.";
      }
    });

    body.append(el("article", { class: "lesson", tabindex: "-1", id: "lesson-article" },
      el("p", { class: "lesson__kicker" }, `Step ${s.n} of ${total} `, (s.tags && s.tags.length) ? [badge("spacy"), el("span", { class: "visually-hidden", text: " Tags: " + s.tags.join(", ") })] : null),
      el("p", { class: "lesson__idea", text: s.idea }),
      el("p", { class: "lesson__example" }, el("strong", { text: "Think of it like this" }), s.example),
      quiz, check, feedback));

    body.append(el("h3", { text: "Your badges" }), el("ul", { class: "medals", id: "medals" }));
    body.append(el("div", { class: "celebrate", id: "celebrate", role: "status", hidden: true }));
    updateMedals();
    if (prog.badge) celebrate(true);
    back.disabled = step <= 1; next.disabled = step >= total;
    if (focusLesson) document.getElementById("lesson-article")?.focus();
  }

  function refreshProgress(c, total) {
    const n = new Set(c.done).size;
    document.getElementById("progress-text").textContent = `${n} of ${total} steps`;
    const bar = body.querySelector(".progress__track");
    bar.setAttribute("aria-valuenow", String(n));
    bar.querySelector(".progress__fill").style.setProperty("--value", String(Math.round((100 * n) / total)));
    body.querySelectorAll(".dot").forEach((d, i) => {
      const isDone = c.done.includes(i + 1);
      d.classList.toggle("is-done", isDone);
      d.setAttribute("aria-label", `Step ${i + 1}${isDone ? ", done" : ""}`);
    });
  }
  function celebrate() {
    const box = document.getElementById("celebrate");
    if (!box) return;
    box.hidden = false;
    box.textContent = `You earned the ${lesson.badge ? lesson.badge.name : "course"} badge. Well done!`;
  }
  function updateMedals() {
    const ul = document.getElementById("medals"); if (!ul) return;
    const cats = load().categories || {};
    ul.replaceChildren(...((getLessons() || {}).items || []).map((l) => {
      const earned = !!(cats[l.category] && cats[l.category].badge);
      return el("li", { class: "medal" + (earned ? " is-earned" : "") },
        el("span", { class: "medal__disc" }, icon("medal")),
        el("span", { text: l.badge ? l.badge.name : CATEGORY_NAMES[l.category] }),
        el("span", { class: "medal__state", text: earned ? "Earned" : "Not yet" }));
    }));
  }

  function trap(e) {
    if (e.key === "Escape") { close(); return; }
    if (e.key !== "Tab") return;
    const items = [...panel.querySelectorAll(FOCUSABLE)].filter((n) => n.offsetParent !== null || n === document.activeElement);
    if (!items.length) return;
    const first = items[0], last = items[items.length - 1];
    if (e.shiftKey && (document.activeElement === first || !panel.contains(document.activeElement))) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && (document.activeElement === last || !panel.contains(document.activeElement))) { e.preventDefault(); first.focus(); }
  }

  function open(cat) {
    lesson = lessonFor(cat);
    if (!lesson) return;
    category = cat;
    const done = new Set(getCategory(cat).done);
    step = (lesson.steps.find((x) => !done.has(x.n)) || lesson.steps[0]).n;
    returnTo = document.activeElement || openBtn;
    render();
    panel.removeAttribute("aria-hidden");
    panel.classList.add("is-open"); backdrop.classList.add("is-open");
    document.body.classList.add("has-panel-open");
    outside().forEach((n) => n.setAttribute("inert", ""));
    closeBtn.focus();
    document.addEventListener("keydown", trap);
  }
  function close() {
    panel.classList.remove("is-open"); backdrop.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("has-panel-open");
    outside().forEach((n) => n.removeAttribute("inert"));
    document.removeEventListener("keydown", trap);
    (returnTo && document.contains(returnTo) ? returnTo : openBtn).focus();
  }

  closeBtn.addEventListener("click", close);
  backdrop.addEventListener("click", close);
  back.addEventListener("click", () => { step = Math.max(1, step - 1); render(true); });
  next.addEventListener("click", () => { step = Math.min(lesson.steps.length, step + 1); render(true); });
  return { open, close };
}
