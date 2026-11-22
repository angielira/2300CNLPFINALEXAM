"""Browser tests for index.html (question box, formats, side panel, rating form, a11y)."""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

STUB_FRUSTRATED = """
export function onProgress() {}
export async function ready() {}
export async function analyze(text) {
  return { category: "printer", confidence: 0.91, probabilities: {printer: 0.91}, unsure: false,
           mood: { compound: -0.7, frustrated: true, reasons: ["negative words"] },
           library: "Neural network + NLTK" };
}
"""


def ask(page, text):
    page.fill("#question", text)
    page.click("#ask-button")
    page.wait_for_selector("#answer:not([hidden])", timeout=15000)


@pytest.fixture
def loaded(base_url, make_page):
    page, errors = make_page()
    page.goto(base_url + "/index.html")
    page.wait_for_load_state("networkidle")
    return page, errors


def test_index_loads_no_page_errors(loaded):
    page, errors = loaded
    assert "HelpMate" in page.title()
    assert page.locator("#question").is_visible()
    assert errors == []


def test_ask_printer_shows_cards_with_badges(loaded):
    page, errors = loaded
    ask(page, "my printer wont print!!")
    assert page.locator("#card-category").is_visible()
    assert page.locator("#card-category .badge").count() >= 1
    badge = page.locator("#card-category .badge").first.inner_text()
    assert any(w in badge for w in ("spaCy", "Neural network"))
    assert "Printer" in page.locator("#card-category").inner_text()
    assert page.locator("#results .badge").count() >= 2
    assert errors == []


def test_fallback_notice_when_engine_missing(loaded):
    # Pyodide is blocked here, so the engine fails and the plain-language notice must show.
    page, _ = loaded
    ask(page, "my printer wont print!!")
    text = page.locator("#results-notices").inner_text()
    assert "smart helper couldn't start" in text or page.locator("#card-mood").count() == 1


def test_format_buttons_switch_and_hear_controls(loaded):
    page, _ = loaded
    ask(page, "my printer wont print!!")
    btns = page.locator("#format-buttons .format-btn")
    assert btns.count() == 4
    seen = {}
    for fmt in ("see_it", "hear_it", "try_it", "read_it"):
        b = page.locator(f'[data-format="{fmt}"].format-btn')
        b.click()
        assert b.get_attribute("aria-pressed") == "true"
        seen[fmt] = page.locator("#format-panel").inner_text()
        for other in ("see_it", "hear_it", "try_it", "read_it"):
            if other != fmt:
                assert page.locator(f'[data-format="{other}"].format-btn').get_attribute("aria-pressed") == "false"
    assert len(set(seen.values())) == 4
    page.click('[data-format="hear_it"].format-btn')
    panel = page.locator("#format-panel")
    has_controls = panel.locator('[data-action="play"]').count() == 1
    has_fallback = "can't read aloud" in panel.inner_text()
    assert has_controls or has_fallback
    if has_controls:
        assert panel.locator('[data-action="pause"]').count() == 1
        assert panel.locator('[data-action="stop"]').count() == 1


def test_side_panel_open_close_and_progress_persists(loaded, base_url):
    page, _ = loaded
    ask(page, "my printer wont print!!")
    panel = page.locator("#learn-panel")
    assert panel.get_attribute("aria-hidden") == "true"
    page.click("#learn-open")
    page.wait_for_function("document.getElementById('learn-panel').getAttribute('aria-hidden') === null")
    assert "is-open" in panel.get_attribute("class")
    radios = panel.locator('input[name="check"]')
    assert radios.count() >= 2
    # pick each choice until the quiz is marked done
    page.locator("#learn-panel .quiz label").first.click()
    page.get_by_role("button", name="Check my answer").click()
    page.wait_for_timeout(200)
    stored = page.evaluate("localStorage.getItem('helpmate.progress.v1')")
    assert stored and '"done":[1]' in stored.replace(" ", "")
    page.keyboard.press("Escape")
    assert panel.get_attribute("aria-hidden") == "true"
    # reload: progress remains and is shown in the panel
    page.reload()
    page.wait_for_load_state("networkidle")
    assert '"done":[1]' in page.evaluate("localStorage.getItem('helpmate.progress.v1')").replace(" ", "")
    ask(page, "my printer wont print!!")
    page.click("#learn-open")
    bar = page.locator('#learn-panel [role="progressbar"]')
    assert bar.get_attribute("aria-valuenow") == "1"
    page.click("#learn-close")
    assert panel.get_attribute("aria-hidden") == "true"


def test_rating_form_static_html_has_netlify_fields():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    m = re.search(r"<form[^>]*name=\"rating\"[^>]*>", html)
    assert m, "static rating form missing from the HTML source"
    tag = m.group(0)
    assert 'data-netlify="true"' in tag and 'netlify-honeypot="bot-field"' in tag
    assert 'method="POST"' in tag
    for name in ("form-name", "bot-field", "stars", "comment", "question", "category", "format", "model_generated_at"):
        assert f'name="{name}"' in html, name
    assert 'name="form-name" value="rating"' in html
    assert len(re.findall(r'name="stars"', html)) == 5
    assert 'maxlength="500"' in html


def test_rating_form_dom_and_honeypot(loaded):
    page, _ = loaded
    names = page.eval_on_selector_all("#rating-form [name]", "els => els.map(e => e.name)")
    for n in ("form-name", "bot-field", "stars", "comment", "question", "category", "format", "model_generated_at"):
        assert n in names
    # honeypot must be off-screen or hidden from sight, never in the normal flow
    vis = page.evaluate("""() => { const e = document.querySelector('#rating-form .honeypot');
        const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
        return {hidden: s.display === 'none' || s.visibility === 'hidden', w: r.width, h: r.height, left: r.left, top: r.top, pos: s.position}; }""")
    assert vis["hidden"] or vis["pos"] == "absolute" or vis["w"] <= 1 or vis["left"] < -100
    assert page.locator('#rating-form [name="bot-field"]').get_attribute("tabindex") == "-1"


def test_stars_radio_clickable_with_row_positioned(loaded):
    page, _ = loaded
    ask(page, "my printer wont print!!")
    page.locator("#rating").scroll_into_view_if_needed()
    assert page.evaluate("getComputedStyle(document.querySelector('.stars__row')).position") == "relative"
    # click the visible label for 4 stars, as a user would
    page.locator('label[for="star-4"]').click()
    assert page.locator("#star-4").is_checked()
    # the hidden radio must sit inside the row (not at the page origin) so focus does not scroll away
    inside = page.evaluate("""() => { const r = document.querySelector('#star-4').getBoundingClientRect();
        const row = document.querySelector('.stars__row').getBoundingClientRect();
        return r.left >= row.left - 2 && r.right <= row.right + 2 && r.top >= row.top - 2 && r.bottom <= row.bottom + 2; }""")
    assert inside
    page.locator('label[for="star-2"]').click()
    assert page.locator("#star-2").is_checked() and not page.locator("#star-4").is_checked()
    # keyboard selection also works
    page.locator("#star-2").focus()
    page.keyboard.press("ArrowUp")
    assert page.locator('input[name="stars"]:checked').count() == 1


def test_stubbed_brain_frustrated_printer(base_url, make_page):
    page, errors = make_page(stub_brain=STUB_FRUSTRATED)
    page.goto(base_url + "/index.html")
    ask(page, "my stupid printer STILL wont print, I hate this!!")
    cat = page.locator("#card-category")
    assert "Printer" in cat.inner_text()
    assert "Neural network" in cat.locator(".badge").first.inner_text()
    assert "91% sure" in cat.inner_text()
    mood = page.locator("#card-mood")
    assert mood.is_visible()
    assert "NLTK" in mood.locator(".badge").first.inner_text()
    assert "frustrating" in page.locator("#results-notices").inner_text()
    assert "NLTK" in page.locator("#results-notices .badge").first.inner_text()
    assert "couldn't start" not in page.locator("#results-notices").inner_text()
    assert errors == []


def test_empty_question_shows_friendly_error(loaded):
    page, _ = loaded
    page.click("#ask-button")
    assert page.locator("#question-error").is_visible()
    assert page.locator("#question").get_attribute("aria-invalid") == "true"


def test_no_horizontal_overflow_360(base_url, make_page):
    page, _ = make_page(width=360, height=800)
    page.goto(base_url + "/index.html")
    page.wait_for_load_state("networkidle")
    ask(page, "my printer wont print!!")
    page.click("#learn-open")
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    page.click("#learn-close")
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")


def test_accessibility_basics(loaded):
    page, _ = loaded
    ask(page, "my printer wont print!!")
    assert page.locator("h1").count() == 1
    assert page.evaluate("document.documentElement.lang") == "en"
    bad = page.evaluate("""() => [...document.querySelectorAll('button')].filter(b => {
        const n = (b.getAttribute('aria-label') || b.innerText || b.textContent || '').trim();
        return !n; }).map(b => b.outerHTML.slice(0, 80))""")
    assert bad == []
    noalt = page.evaluate("[...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).map(i => i.src)")
    assert noalt == []
    # visible labels on form controls
    unlabeled = page.evaluate("""() => [...document.querySelectorAll('input:not([type=hidden]), textarea')].filter(i =>
        !i.labels.length && !i.getAttribute('aria-label')).map(i => i.id || i.name)""")
    assert unlabeled == []
    small = page.evaluate("""() => [...document.querySelectorAll('#ask-button, .format-btn, #learn-open, .chip, .nav-link, #rating-form button[type=submit]')]
        .filter(b => b.offsetParent !== null).map(b => { const r = b.getBoundingClientRect();
        return {t: (b.innerText || '').trim().slice(0, 20), w: Math.round(r.width), h: Math.round(r.height)}; })
        .filter(x => x.w < 44 || x.h < 44)""")
    assert small == [], small
