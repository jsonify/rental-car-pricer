# Track Learnings: playwright_20260218

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values (from: dashboard_20260217)
- Date formats are mixed: `pickup_date`/`dropoff_date` use `MM/DD/YYYY`; `created_at` uses ISO (from: dashboard_20260217)
- `EnvironmentContext` defaults to test mode when `VITE_SUPABASE_URL` is absent (from: dashboard_20260217)
- Python scraper entry point: `main.py` orchestrates bookings; `price_monitor.py` is the core Selenium/Playwright logic
- CSS selectors for Costco Travel results page: `div[role="row"]` (rows), `div.inner.text-center.h3-tag-style` (category name), `a.card.car-result-card.lowest-price` (cheapest card), `data-price` attr (price value)
- Selenium hardcoded paths live in `driver_setup.py` (local Chrome binary) and `price_monitor.py` (setup_driver function) — both being replaced

---

## [2026-02-18 00:00] - Phase 1 Task 1: Update requirements.txt
- **Implemented:** Removed selenium==4.18.1 and selenium-wire==5.1.0, added playwright>=1.41.0
- **Files changed:** requirements.txt
- **Commit:** e041185
- **Learnings:**
  - Patterns: Use `playwright>=1.41.0` (unpinned minor) since Playwright releases frequently
  - Gotchas: selenium-wire was also in requirements — don't forget to remove it

---

## [2026-02-18] - Phase 5 Task 1: Update price-checker.yaml CI workflow
- **Implemented:** Replaced ~50-line "Setup Chrome and ChromeDriver" block with single `playwright install chromium --with-deps` step. Removed selenium/webdriver_manager from pip install. Removed CHROME_BINARY_PATH, CHROMEDRIVER_PATH, USER_AGENT env vars from "Run price checker" step and from inline .env generation.
- **Files changed:** .github/workflows/price-checker.yaml
- **Commit:** a820eca
- **Learnings:**
  - Patterns: `playwright install chromium --with-deps` handles all OS-level browser deps in one command — replaces 40+ lines of curl/unzip/apt-get
  - Gotchas: Selenium vars appeared in two places: the step's `env:` block AND an inline Python `.env` file writer — both must be cleaned

---

## [2026-02-18 00:00] - Phase 1 Task 2: Delete driver_setup.py and human_simulation.py
- **Implemented:** Deleted driver_setup.py, human_simulation.py, test-chrome.py. Cleared price_monitor.py. Stripped broken imports from main.py and price_extractor.py.
- **Files changed:** driver_setup.py (deleted), human_simulation.py (deleted), test-chrome.py (deleted), price_monitor.py (cleared), main.py, price_extractor.py
- **Commit:** 37c64b5
- **Learnings:**
  - Patterns: All form automation (fill_search_form, validate_category, get_available_categories, process_booking, wait_for_results) lives in main.py — NOT in price_monitor.py
  - Context: price_monitor.py was a Selenium prototype with hardcoded paths; main.py is the real orchestrator
  - Plan revision: Phase 3 must MOVE functions from main.py INTO price_monitor.py (plus port to Playwright), then update main.py to import from price_monitor.py

---
