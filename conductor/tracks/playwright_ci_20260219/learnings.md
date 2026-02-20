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
