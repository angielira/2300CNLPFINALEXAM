// The 10-step mini-course, shown inline in the results panel (a second tab next to the answer):
// lesson, quiz, progress bar, step path, badge medals.
import { el, icon, badge, CATEGORY_NAMES } from "./dom.js";
import { getCategory, markStep, load } from "./progress.js";

export function initPanel(getLessons) {
  const panel = document.getElementById("learn-panel");
  const openBtn = document.getElementById("learn-open");
  const closeBtn = document.getElementById("learn-close");
  const body = document.getElementById("learn-body");
  const title = document.getElementById("learn-title");
  const back = document.getElementById("learn-back");
  const next = document.getElementById("learn-next");
  const nav = back.parentElement;
  const tabAnswer = document.getElementById("tab-answer");
  const tabCourse = document.getElementById("tab-course");
  const answerPane = document.getElementById("answer-pane");
  const tabProgress = document.getElementById("tab-course-progress");
  const ctaProgress = document.getElementById("learn-cta-progress");
  let category = null, step = 1, lesson = null, isOpen = false;

  const lessonFor = (id) => ((getLessons() || {}).items || []).find((l) => l.category === id);

  function render(focusLesson = false) {
    if (!lesson) return;
    const prog = getCategory(category);
    const total = lesson.steps.length;
    const s = lesson.steps.find((x) => x.n === step) || lesson.steps[0];
    const done = new Set(prog.done);
    title.textContent = lesson.title;
    body.replaceChildren();
    body.dataset.stepCount = String(total);

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
    body.append(nav);   // Back / Next sit right under the lesson

    body.append(el("h3", { text: "Your badges" }), el("ul", { class: "medals", id: "medals" }));
    body.append(el("div", { class: "celebrate", id: "celebrate", role: "status", hidden: true }));
    updateMedals();
    if (prog.badge) celebrate(true);
    back.disabled = step <= 1; next.disabled = step >= total;
    showProgress(done.size, total);
    if (focusLesson) document.getElementById("lesson-article")?.focus();
  }

  function refreshProgress(c, total) {
    const n = new Set(c.done).size;
    document.getElementById("progress-text").textContent = `${n} of ${total} steps`;
    const bar = body.querySelector(".progress__track");
    bar.setAttribute("aria-valuenow", String(n));
    bar.querySelector(".progress__fill").style.setProperty("--value", String(Math.round((100 * n) / total)));
    showProgress(n, total);
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

  function showProgress(n, total) {
    tabProgress.textContent = `(${n} of ${total})`;
    ctaProgress.textContent = n ? `You have finished ${n} of ${total} steps.` : "";
  }

  // Pick the course for a category (called for every new answer). Always shows the answer tab.
  function setCategory(cat) {
    category = cat;
    lesson = lessonFor(cat);
    const has = !!lesson;
    tabCourse.disabled = !has; openBtn.disabled = !has;
    if (has) showProgress(new Set(getCategory(cat).done).size, lesson.steps.length);
    else { tabProgress.textContent = ""; ctaProgress.textContent = ""; }
    select("answer", false);
  }

  function select(which, focus) {
    const course = which === "course" && !!lesson;
    isOpen = course;
    tabAnswer.setAttribute("aria-selected", String(!course));
    tabCourse.setAttribute("aria-selected", String(course));
    tabAnswer.tabIndex = course ? -1 : 0;
    tabCourse.tabIndex = course ? 0 : -1;
    answerPane.hidden = course;
    panel.hidden = !course;
    document.getElementById("results").classList.toggle("is-course", course);
    if (course) {
      const done = new Set(getCategory(category).done);
      step = (lesson.steps.find((x) => !done.has(x.n)) || lesson.steps[0]).n;
      render();
      if (focus) title.focus();
    }
  }

  function open(cat) {
    if (cat && cat !== category) { category = cat; lesson = lessonFor(cat); }
    if (!lesson) return;
    select("course", true);
  }
  function close() {
    select("answer", false);
    openBtn.focus();
  }

  tabAnswer.addEventListener("click", () => select("answer", false));
  tabCourse.addEventListener("click", () => select("course", false));
  document.querySelector(".tabs").addEventListener("keydown", (e) => {
    const order = [tabAnswer, tabCourse].filter((t) => !t.disabled);
    const i = order.indexOf(document.activeElement);
    if (i < 0) return;
    let n = null;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") n = order[(i + 1) % order.length];
    else if (e.key === "ArrowLeft" || e.key === "ArrowUp") n = order[(i - 1 + order.length) % order.length];
    else if (e.key === "Home") n = order[0];
    else if (e.key === "End") n = order[order.length - 1];
    if (!n) return;
    e.preventDefault(); n.focus(); n.click();
  });
  closeBtn.addEventListener("click", close);
  openBtn.addEventListener("click", () => open(category));
  back.addEventListener("click", () => { step = Math.max(1, step - 1); render(true); });
  next.addEventListener("click", () => { step = Math.min(lesson.steps.length, step + 1); render(true); });
  return { open, close, setCategory, isOpen: () => isOpen };
}
