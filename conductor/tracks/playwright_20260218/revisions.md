# Revisions: playwright_20260218

## Revision 1 — 2026-02-18
**Type:** Plan
**Triggered by:** Phase 1 Task 2 — discovered during file deletion
**Phase/Task:** Phase 1 / Task 2

### Issue
The plan assumed scraping logic lived in `price_monitor.py`. In reality, all form
automation functions (`fill_search_form`, `validate_category`, `get_available_categories`,
`process_booking`, `wait_for_results`) live in `main.py` and import from `driver_setup.py`
and `human_simulation.py`. The original `price_monitor.py` was a standalone prototype
with its own hardcoded Selenium setup, not used by `main.py`.

### Changes
- Phase 2 scope updated: `price_monitor.py` will be fully rewritten from scratch as the
  new Playwright-based scraper module (setup_browser + all form automation functions)
- Phase 3 scope updated: porting includes moving functions FROM `main.py` INTO
  `price_monitor.py`, then updating `main.py` imports
- `test-chrome.py` was also deleted (Selenium-specific test script, not in original plan)

### Rationale
Cleanest outcome: `price_monitor.py` becomes the Playwright module, `main.py` becomes
a thin orchestrator that calls into it.
