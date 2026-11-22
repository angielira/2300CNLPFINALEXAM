# Playwright for Python

- `pip install pytest-playwright` then `playwright install`.
- Tests take a `page` fixture; `page.goto(url)`; `page.get_by_role("button", name="Hear it").click()`.
- `expect(locator).to_be_visible()`, `expect(page).to_have_title(...)`.
- Runs headless Chromium by default; Python 3.8+.

## Sources
- https://playwright.dev/python/docs/intro
