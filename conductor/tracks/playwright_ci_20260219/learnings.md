# Track Learnings: playwright_ci_20260219

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- All Costco Travel form automation lives in `price_monitor.py` — `main.py` is a thin orchestrator (from: playwright_20260218)
- CSS selectors for results: `div[role="row"]`, `div.inner.text-center.h3-tag-style`, `a.card.car-result-card.lowest-price[data-price]` (from: playwright_20260218)
- Use `sync_playwright().start()` (not context manager) — caller holds reference and calls `playwright.stop()` in `finally` (from: playwright_20260218)
- Mock Playwright locator chains with `MagicMock` + `side_effect` returning different mocks per CSS selector (from: playwright_20260218)
- `--no-sandbox` and `--disable-dev-shm-usage` are required for Chromium on GitHub Actions Linux runners (from: patterns.md)
- `python3 -m playwright install chromium --with-deps` handles all CI browser setup (from: playwright_20260218)

---

<!-- Learnings from implementation will be appended below -->

## [2026-02-19] - Phase 2 Tasks 1+2: Error Handling Fix (process_booking)
- **Implemented:** Cascade screenshot guard + one navigation retry in `process_booking()`
- **Files changed:** `price_monitor.py`, `test_price_monitor.py`
- **Commit:** 2632718
- **Learnings:**
  - Patterns: Inner try/except around `page.goto()` lets a retry succeed; if retry also fails it propagates naturally to outer except — no duplicate error handling needed
  - Gotchas: When mocking an intra-function import (`from price_extractor import ...`), inject via `sys.modules["price_extractor"] = stub` before calling the function — `patch("price_monitor.extract_lowest_prices")` won't work since the binding is created fresh on each call
  - Context: `page.screenshot()` in an error handler can itself timeout if the page is dead (Playwright default screenshot timeout is also 30s); always wrap in try/except
---

## [2026-02-19] - Phase 1 Tasks 1+2: Browser Hardening (setup_browser)
- **Implemented:** Added CI-required Chromium launch args, 1920×1080 viewport, and 60s nav timeout to `setup_browser()`
- **Files changed:** `price_monitor.py`, `test_price_monitor.py`
- **Commit:** 21cb404
- **Learnings:**
  - Patterns: When adding kwargs to a mock call, update tests from `assert_called_once_with(headless=True)` to `call_args[1]["headless"]` to stay robust against future arg additions
  - Gotchas: Playwright `set_default_navigation_timeout` is on `page`, not `context` or `browser`
  - Context: `--no-sandbox` and `--disable-dev-shm-usage` are mandatory on GitHub Actions Linux; `--disable-blink-features=AutomationControlled` prevents Cloudflare bot detection
---
