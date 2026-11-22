// Renders the content of #format-panel for each of the four formats.
import { el, icon, notice } from "./dom.js";
import { speechSupported, createSpeaker } from "./speech.js";
import { getTry, setTry } from "./progress.js";

export const FORMATS = ["see_it", "hear_it", "try_it", "read_it"];
const LABEL = { see_it: "See it", hear_it: "Hear it", try_it: "Try it", read_it: "Read it" };
export const formatLabel = (f) => LABEL[f] || f;

function seeIt(a, frustrated) {
  const steps = (a.see_it && a.see_it.steps) || [];
  return el("div", {},
    el("h4", { class: "format-panel__title", text: "See it: steps to follow" }),
    frustrated && a.calm_intro ? el("p", { class: "format-panel__intro", text: a.calm_intro }) : null,
    el("ol", { class: "steps" }, steps.map((s) => el("li", { class: "step" },
      el("span", { class: "step__num", text: String(s.n), "aria-hidden": "true" }),
      el("div", {},
        el("p", { class: "step__label", text: `Step ${s.n}: ${s.label}` }),
        el("p", { class: "step__detail", text: s.detail }),
        s.image ? el("img", { class: "step__image", src: s.image, alt: s.alt || "", loading: "lazy" }) : null)))));
}

function hearIt(a, frustrated, ctx) {
  const h = a.hear_it || {};
  const lines = [h.intro, ...(h.script || []), h.outro].filter(Boolean);
  const root = el("div", {}, el("h4", { class: "format-panel__title", text: "Hear it: I'll read it to you" }),
    frustrated && a.calm_intro ? el("p", { class: "format-panel__intro", text: a.calm_intro }) : null);
  const list = el("ol", { class: "script" }, lines.map((t) => el("li", { class: "script__line", text: t })));
  if (!speechSupported()) {
    root.append(notice("info", null, "Your browser can't read aloud. The steps below are the same words."), list);
    return { node: root };
  }
  const status = el("p", { class: "visually-hidden", role: "status" });
  const play = el("button", { class: "btn", type: "button", "data-action": "play" }, icon("play"), el("span", { text: "Read it to me" }));
  const pause = el("button", { class: "btn btn--secondary", type: "button", "data-action": "pause", disabled: true }, icon("pause"), el("span", { text: "Pause" }));
  const stop = el("button", { class: "btn btn--secondary", type: "button", "data-action": "stop", disabled: true }, icon("stop"), el("span", { text: "Stop" }));
  const items = [...list.children];
  const speaker = createSpeaker(lines, {
    onLine(i) {
      items.forEach((li, k) => { li.classList.toggle("is-speaking", k === i); if (k === i) li.setAttribute("aria-current", "true"); else li.removeAttribute("aria-current"); });
    },
    onState(s) {
      play.querySelector("span").textContent = s === "paused" ? "Keep going" : "Read it to me";
      pause.disabled = s !== "playing"; stop.disabled = s === "stopped";
      status.textContent = s === "playing" ? "Reading." : s === "paused" ? "Paused." : "Stopped.";
    },
  });
  play.addEventListener("click", () => speaker.play());
  pause.addEventListener("click", () => speaker.pause());
  stop.addEventListener("click", () => speaker.stop());
  root.append(el("div", { class: "hear-controls" }, play, pause, stop), status,
    el("p", { class: "hear-note", text: "Your device's voice will read each step. The words stay on screen too." }), list);
  return { node: root, dispose: () => speaker.stop() };
}

function tryIt(a, frustrated, ctx) {
  const steps = (a.try_it && a.try_it.steps) || [];
  const saved = getTry(ctx.category);
  const fill = el("span", { class: "progress__fill" });
  const text = el("span");
  const track = el("div", { class: "progress__track", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(steps.length), "aria-label": "Try it progress" }, fill);
  const done = el("p", { class: "try-done notice notice--calm", role: "status", hidden: true, text: "All done! Well done. If it still isn't working, see the note below." });
  const boxes = [];
  const update = () => {
    const n = boxes.filter((b) => b.checked).length;
    text.textContent = `${n} of ${steps.length} done`;
    track.setAttribute("aria-valuenow", String(n));
    fill.style.setProperty("--value", steps.length ? String(Math.round((100 * n) / steps.length)) : "0");
    done.hidden = !(steps.length && n === steps.length);
  };
  const list = el("ul", { class: "check-list" }, steps.map((s) => {
    const box = el("input", { class: "check__box", type: "checkbox", id: s.id });
    box.checked = saved.has(s.id);
    box.addEventListener("change", () => { setTry(ctx.category, s.id, box.checked); update(); });
    boxes.push(box);
    return el("li", {}, el("label", { class: "check", for: s.id }, box, el("span", { class: "check__text", text: s.text })));
  }));
  const root = el("div", {}, el("h4", { class: "format-panel__title", text: "Try it: tick off each step" }),
    frustrated && a.calm_intro ? el("p", { class: "format-panel__intro", text: a.calm_intro }) : null,
    el("div", { class: "progress" }, el("div", { class: "progress__label" }, el("span", { text: "Your steps" }), text), track), list, done);
  update();
  return { node: root };
}

function readIt(a) {
  const r = a.read_it || {};
  return el("div", {},
    el("h4", { class: "format-panel__title", text: "Read it: a checklist to print" }),
    el("h4", { class: "print-title print-only", text: r.print_title || a.title }),
    el("ul", { class: "read-list" }, (r.checklist || []).map((t) => el("li", { class: "read-list__item", text: t }))),
    el("div", { class: "format-actions" },
      el("button", { class: "btn btn--secondary", type: "button", onclick: () => window.print() }, icon("print"), el("span", { text: "Print this checklist" }))));
}

// Returns { node, dispose? }.
export function renderFormat(format, answer, ctx) {
  const frustrated = !!ctx.frustrated;
  switch (format) {
    case "hear_it": return hearIt(answer, frustrated, ctx);
    case "try_it": return tryIt(answer, frustrated, ctx);
    case "read_it": return { node: readIt(answer) };
    default: return { node: seeIt(answer, frustrated) };
  }
}
