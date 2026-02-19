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

## Testing

- Mock Supabase client stores data in localStorage under `mockSupabaseStore` key
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- Mock Playwright locator chains with `MagicMock` + `side_effect` returning different mocks per CSS selector (from: playwright_20260218, 2026-02-18)

---
Last refreshed: 2026-02-18
