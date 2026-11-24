"""Browser tests for resources.html and the Resources links on every page."""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCREENS = ROOT / "reports" / "screens"
PAGES = ["index.html", "insights.html", "resources.html"]


@pytest.fixture
def res(base_url, make_page):
    page, errors = make_page()
    page.goto(base_url + "/resources.html")
    page.wait_for_load_state("networkidle")
    return page, errors


def test_loads_no_page_errors(res):
    page, errors = res
    assert page.locator("h1").count() == 1
    assert errors == []


def test_required_links_present(res):
    page, _ = res
    hrefs = page.eval_on_selector_all("main a", "els => els.map(a => a.href)")
    assert "https://github.com/angielira/2300CNLPFINALEXAM" in hrefs
    assert "https://claude.ai/artifact/NTCut33EUofio3qY7ZNCXQ" in hrefs
    for host in ("nltk.org", "spacy.io", "pyodide", "netlify", "scikit-learn.org"):
        assert any(host in h for h in hrefs), host


def test_every_link_opens_safely(res):
    page, _ = res
    bad = page.eval_on_selector_all(
        "main a", "els => els.filter(a => a.target !== '_blank' || !a.rel.includes('noopener')).map(a => a.href)")
    assert bad == []


@pytest.mark.parametrize("name", PAGES)
def test_resources_link_in_header_and_footer(base_url, make_page, name):
    page, errors = make_page()
    page.goto(base_url + "/" + name)
    for sel in ("header nav a[href='resources.html']", "footer a[href='resources.html']"):
        link = page.locator(sel)
        assert link.count() == 1, sel
        assert link.is_visible(), sel
        assert link.inner_text().strip() == "Resources"
    cur = page.locator("a[href='resources.html'][aria-current='page']").count()
    assert cur == (2 if name == "resources.html" else 0)
    assert errors == []


def test_no_horizontal_overflow_360(base_url, make_page):
    page, _ = make_page(width=360, height=800)
    page.goto(base_url + "/resources.html")
    page.wait_for_load_state("networkidle")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


@pytest.mark.parametrize("w,h", [(1440, 900), (390, 844)])
def test_screenshots(base_url, make_page, w, h):
    page, _ = make_page(width=w, height=h)
    page.goto(base_url + "/resources.html")
    page.wait_for_load_state("networkidle")
    SCREENS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENS / f"v3-resources-{w if w > 400 else 390}.png"), full_page=True)
