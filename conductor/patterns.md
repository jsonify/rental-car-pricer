# Codebase Patterns

Reusable patterns discovered during development. Read this before starting new work.

## Code Conventions

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components (from: dashboard_20260217, 2026-02-17)
- `isDevelopment` flag exported from `src/lib/environment.ts` — use it to gate dev-only UI (from: dashboard_20260217, 2026-02-17)
- Wrap async data-fetching functions in `useCallback` with their dependency array to satisfy `react-hooks/exhaustive-deps` (from: dashboard_20260217, 2026-02-17)

## Architecture

- Dark mode toggled via `class="dark"` on `<html>` — all shadcn/ui components pick up dark CSS vars automatically (from: dashboard_20260217, 2026-02-17)
- Admin/utility UI should be collapsed by default; booking cards are primary content (from: dashboard_20260217, 2026-02-17)
- `EnvironmentContext` defaults to test mode when `VITE_SUPABASE_URL` is absent — safe for local dev without `.env` (from: dashboard_20260217, 2026-02-17)

## Gotchas

- **Date formats are mixed**: booking `pickup_date`/`dropoff_date` use `MM/DD/YYYY` (e.g. `04/01/2025`); `created_at` fields use ISO. Use `new Date()` for booking dates, `parseISO()` is safe only for `created_at` (from: dashboard_20260217, 2026-02-17)
- **`tsconfig.json` must include `"types": ["vite/client"]`** — without it, all `import.meta.env` references produce type errors (from: dashboard_20260217, 2026-02-17)
- **`node_modules` not committed** — always run `npm install` in a fresh clone before running typecheck or lint (from: dashboard_20260217, 2026-02-17)
- **`.eslintrc.cjs` was missing** — ESLint config must be committed; use `.eslintignore` to scope lint to new code when onboarding lint into legacy codebase (from: dashboard_20260217, 2026-02-17)

## Price Signal Colors

- Price **drops** → `text-green-400` + `↓` (good news — rebook opportunity)
- Price **rises** → `text-red-400` + `↑` (bad news — hold your booking)
- Down is always good (from: dashboard_20260217, 2026-02-17)

## Python Scraper Architecture

- All Costco Travel form automation lives in `price_monitor.py` — `main.py` is a thin orchestrator that imports from it (from: playwright_20260218, 2026-02-18)
- CSS selectors for Costco Travel results: `div[role="row"]` (rows), `div.inner.text-center.h3-tag-style` (category name), `a.card.car-result-card.lowest-price[data-price]` (price) (from: playwright_20260218, 2026-02-18)
- Use `sync_playwright().start()` (not context manager) when the browser must outlive the setup function — caller holds `playwright` reference and calls `playwright.stop()` in `finally` (from: playwright_20260218, 2026-02-18)

## CI

- `python3 -m playwright install chromium --with-deps` replaces all manual Chrome/ChromeDriver download steps in GitHub Actions — one line handles binary + OS dependencies (from: playwright_20260218, 2026-02-18)
- When removing browser env vars from a CI workflow, check both the step's `env:` block AND any inline Python/shell `.env` file writers in the same step (from: playwright_20260218, 2026-02-18)
- Playwright on GitHub Actions Linux **requires** `--no-sandbox` and `--disable-dev-shm-usage` in `chromium.launch(args=[...])` — without them `page.goto()` times out silently (from: playwright_ci_20260219, 2026-02-19)
- `gh workflow run <file>.yaml --ref <branch>` + `gh run watch <run-id>` is the full loop for triggering and monitoring CI from the terminal (from: playwright_ci_20260219, 2026-02-19)
- Use `channel="chrome"` in `playwright.chromium.launch()` in CI to get Google Chrome's real TLS fingerprint — Playwright's bundled Chromium may be blocked by bot detection on production sites (from: playwright_ci_20260219, archived 2026-02-20)

## Testing

- Mock Supabase client stores data in localStorage under `mockSupabaseStore` key
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- Mock Playwright locator chains with `MagicMock` + `side_effect` returning different mocks per CSS selector (from: playwright_20260218, 2026-02-18)
- **`sys.modules` stub scope**: only stub modules that *directly* import the unavailable package. Template submodules (`html_template.py`, `formatters.py`) don't import supabase — stubbing them as empty `types.ModuleType` causes `ImportError` in other test files that share the same pytest session. Use `setdefault` only for the exact modules in the broken import chain. (from: email_20260218, 2026-02-19)
- **Intra-function imports**: `from price_extractor import extract_lowest_prices` inside a function body creates a fresh binding on every call. Patch by injecting `sys.modules["price_extractor"] = stub` before calling the function — `patch("price_monitor.extract_lowest_prices")` won't work since no module-level name exists to intercept. (from: playwright_ci_20260219, 2026-02-19)
- **Playwright error-path cascade**: `page.screenshot()` in an `except` block can itself timeout (30 s default) when the page is already dead. Always wrap error screenshots in their own `try/except`. (from: playwright_ci_20260219, 2026-02-19)
- **Mock kwargs robustness**: assert `call_args[1]["key"] == value` rather than `assert_called_once_with(key=value)` — the latter breaks when unrelated kwargs are added to the same call in the future (from: playwright_ci_20260219, archived 2026-02-20)
- **`locator.focus()` + `keyboard.press("Enter")`** instead of `locator.click()` for buttons behind sticky headers — Playwright's `click()` always calls `scroll_into_view_if_needed()` internally, repositioning the element back under the header before clicking (from: playwright_ci_20260219, archived 2026-02-20)
- **`has-text()` is case-insensitive** — use `ArrowDown`+`Enter` keyboard nav to select the first autocomplete suggestion instead of `li:has-text("XYZ").click()`, which can match navigation items case-insensitively and open menus (from: playwright_ci_20260219, archived 2026-02-20)
- **`wait_for_url()` fast-path**: if a `wait_for_timeout` precedes the call, navigation may already be complete — check `page.url` against the pattern first and return immediately if it matches, otherwise `wait_for_url` will wait for a *new* navigation that never comes (from: playwright_ci_20260219, archived 2026-02-20)
- **`set_default_navigation_timeout`** belongs on `page`, not `context` or `browser` (from: playwright_ci_20260219, archived 2026-02-20)

---
Last refreshed: 2026-02-20
