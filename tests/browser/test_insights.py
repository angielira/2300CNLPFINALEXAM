"""Browser tests for insights.html."""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCREENS = ROOT / "reports" / "screens"


@pytest.fixture
def insights(base_url, make_page):
    page, errors = make_page()
    page.goto(base_url + "/insights.html")
    page.wait_for_load_state("networkidle")
    page.wait_for_function("!document.querySelector('#insights-status .spinner')", timeout=15000)
    return page, errors


def test_insights_loads_no_page_errors(insights):
    page, errors = insights
    assert page.locator("h1").count() == 1
    assert errors == []


def test_null_sections_show_netlify_build_notice(insights):
    page, _ = insights
    body = page.inner_text("main")
    # a local --allow-missing build has no NLTK stats / VADER / spaCy metrics
    assert "appears after the Netlify build" in body
    assert page.locator("#chart-vader, #chart-spacy, #chart-words").first.count() == 1
    for cid in ("chart-vader", "chart-spacy", "chart-words"):
        assert "appears after the Netlify build" in page.inner_text(f"#{cid}"), cid


def test_every_chart_section_has_a_library_badge(insights):
    page, _ = insights
    missing = page.evaluate("""() => [...document.querySelectorAll('section.chart-card')]
        .filter(s => !s.querySelector('.badge')).map(s => s.id)""")
    assert missing == []


def test_accessibility_basics(insights):
    page, _ = insights
    assert page.evaluate("[...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length") == 0
    assert page.evaluate("""() => [...document.querySelectorAll('button')].filter(b =>
        !(b.getAttribute('aria-label') || b.innerText || '').trim()).length""") == 0
    assert page.evaluate("document.documentElement.lang") == "en"
    small = page.evaluate("""() => [...document.querySelectorAll('button, .nav-link')].filter(b => b.offsetParent !== null)
        .map(b => { const r = b.getBoundingClientRect(); return {t: (b.innerText||'').trim().slice(0,20), w: Math.round(r.width), h: Math.round(r.height)}; })
        .filter(x => x.w < 44 || x.h < 44)""")
    assert small == [], small


def test_no_horizontal_overflow_360(base_url, make_page):
    page, _ = make_page(width=360, height=800)
    page.goto(base_url + "/insights.html")
    page.wait_for_load_state("networkidle")
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")


@pytest.mark.parametrize("w,h", [(1280, 900), (375, 800)])
def test_save_screenshots(base_url, make_page, w, h):
    SCREENS.mkdir(parents=True, exist_ok=True)
    page, errors = make_page(width=w, height=h)
    page.goto(base_url + "/insights.html")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(SCREENS / f"insights-{w}.png"), full_page=True)
    assert errors == []


def test_insights_draws_charts_when_nltk_data_is_present(base_url, make_page):
    """Simulates the Netlify build: routes in sample NLTK stats and VADER metrics, expects no notices and no errors."""
    import json
    stats = {"generated_at": "2026-01-01T00:00:00Z", "library": "NLTK", "schema_version": 1, "n_documents": 50,
             "items": [{"word": "printer", "count": 12}, {"word": "wifi", "count": 9}],
             "top_phrases": [{"phrase": "will not", "count": 5, "score": 3.2}],
             "by_category": {"printer": 12, "wifi": 9}, "frustration": {"rate": 0.2, "count": 10}}
    page, errors = make_page()
    page.route("**/data/nltk_stats.json", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(stats)))
    page.goto(base_url + "/insights.html")
    page.wait_for_load_state("networkidle")
    page.wait_for_function("!document.querySelector('#insights-status .spinner')", timeout=15000)
    assert "printer" in page.inner_text("#chart-words")
    assert "appears after the Netlify build" not in page.inner_text("#chart-words")
    assert errors == []
