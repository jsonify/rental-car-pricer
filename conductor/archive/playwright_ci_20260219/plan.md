# Plan: Fix Playwright CI Navigation + gh CLI Workflow

## Phase 1: Browser Hardening

- [x] Task 1: Update tests for setup_browser() in test_price_monitor.py (21cb404)
  <!-- files: test_price_monitor.py -->
  - Assert chromium.launch() args include '--disable-blink-features=AutomationControlled'
  - Assert args include '--no-sandbox' and '--disable-dev-shm-usage'
  - Assert new_context() called with viewport={"width": 1920, "height": 1080}
  - Assert page.set_default_navigation_timeout(60000) is called

- [x] Task 2: Update setup_browser() in price_monitor.py (21cb404)
  <!-- files: price_monitor.py -->
  <!-- depends: task1 -->
  - Add args list to chromium.launch()
  - Add viewport to new_context()
  - Call page.set_default_navigation_timeout(60000) on the new page
  - Commit: `fix(scraper): add CI-safe launch args and 60s nav timeout to Playwright`

- [x] Task: Conductor - User Manual Verification 'Browser Hardening' (Protocol in workflow.md)

## Phase 2: Error Handling Fix

- [x] Task 1: Add tests for cascade-free error path in test_price_monitor.py (2632718)
  <!-- files: test_price_monitor.py -->
  - Simulate page.goto() raising TimeoutError → assert process_booking returns None cleanly
  - Assert error screenshot failure does NOT propagate (wrapped in try/except)
  - Simulate first goto fails, second succeeds → assert prices returned (retry works)

- [x] Task 2: Fix process_booking() in price_monitor.py (2632718)
  <!-- files: price_monitor.py -->
  <!-- depends: task1 -->
  - Wrap error screenshot in its own try/except
  - Add one navigation retry: on TimeoutError, wait 5 s and try page.goto once more
  - Commit: `fix(scraper): guard error screenshot from cascade, add nav retry`

- [x] Task: Conductor - User Manual Verification 'Error Handling Fix' (Protocol in workflow.md)

## Phase 3: gh CLI + CI Validation
<!-- depends: phase1, phase2 -->

- [x] Task 1: Install and authenticate gh CLI
  - brew install gh
  - gh auth login (personal access token with repo + workflow scope)
  - Verify with: gh workflow list

- [x] Task 2: Trigger price-checker on feature branch and confirm it passes (run 22207657779)
  - gh workflow run price-checker.yaml --ref feature/2026-02-19-version
  - gh run watch 22207657779
  - Result: ✓ success in 6m9s — Run price checker passed, no timeout

- [x] Task: Conductor - User Manual Verification 'CI Validation' (Protocol in workflow.md)
