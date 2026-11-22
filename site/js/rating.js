// Rating form: static HTML form (name="rating") that Netlify detects; we only add AJAX and messages.
import { notice, icon } from "./dom.js";

export function initRating() {
  const form = document.getElementById("rating-form");
  if (!form) return { setContext() {}, show() {} };
  const section = document.getElementById("rating");
  const thanks = document.getElementById("rating-thanks");
  const value = document.getElementById("stars-value");
  const msg = document.getElementById("rating-message");
  const field = (n) => form.elements[n];

  form.addEventListener("change", (e) => {
    if (e.target.name === "stars") {
      const n = e.target.value;
      value.textContent = `${n} of 5 stars`;
      msg.replaceChildren();
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.replaceChildren();
    if (!form.querySelector('input[name="stars"]:checked')) {
      msg.append(notice("unsure", null, "Please pick a number of stars first.", "alert"));
      return;
    }
    const body = new URLSearchParams(new FormData(form)).toString();
    const send = form.querySelector('button[type="submit"]');
    send.disabled = true;
    try {
      const r = await fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
      if (!r.ok) throw new Error("status " + r.status);
      form.hidden = true; thanks.hidden = false; thanks.focus?.();
    } catch {
      msg.append(notice("error", null, "That didn't send. Your rating is still here, so you can try again.", "alert"));
    } finally { send.disabled = false; }
  });

  return {
    // Fill the hidden fields that tell the build what was rated.
    setContext({ question, category, format, generated }) {
      if (question != null) field("question").value = question.slice(0, 300);
      if (category != null) field("category").value = category;
      if (format != null) field("format").value = format;
      if (generated != null) field("model_generated_at").value = generated;
    },
    show() {
      section.hidden = false;
      // A new answer means a new rating
      if (form.hidden) { form.hidden = false; thanks.hidden = true; form.reset(); value.textContent = ""; }
    },
  };
}
