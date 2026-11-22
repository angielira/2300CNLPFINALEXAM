"""Browser fixtures: serve a temp copy of site/ on a free port and launch chromium."""
import functools
import http.server
import pathlib
import shutil
import threading

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    if not (ROOT / "site" / "data" / "answers.json").exists():
        pytest.skip("site/data not built")
    d = tmp_path_factory.mktemp("sitecopy") / "site"
    shutil.copytree(ROOT / "site", d)
    handler = functools.partial(Quiet, directory=str(d))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # browser not installed
            pytest.skip(f"chromium not available: {e}")
        yield b
        b.close()


EXTERNAL = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net")


def _block_external(route):
    if any(h in route.request.url for h in EXTERNAL):
        route.abort()
    else:
        route.continue_()


@pytest.fixture
def make_page(browser):
    """Returns a function creating (page, errors). errors collects uncaught page errors."""
    ctxs = []

    def _make(width=1280, height=900, stub_brain=None):
        ctx = browser.new_context(viewport={"width": width, "height": height})
        ctxs.append(ctx)
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.route("**/*", _block_external)
        if stub_brain:
            page.route("**/js/brain.js", lambda r: r.fulfill(
                status=200, content_type="text/javascript", body=stub_brain))
        return page, errors

    yield _make
    for c in ctxs:
        c.close()


@pytest.fixture
def page(make_page):
    return make_page()
