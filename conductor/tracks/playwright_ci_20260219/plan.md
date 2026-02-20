# Plan: Fix Playwright CI Navigation + gh CLI Workflow

## Phase 1: Browser Hardening

- [ ] Task 1: Update tests for setup_browser() in test_price_monitor.py
  <!-- files: test_price_monitor.py -->
  - Assert chromium.launch() args include '--disable-blink-features=AutomationControlled'
  - Assert args include '--no-sandbox' and '--disable-dev-shm-usage'
  - Assert new_context() called with viewport={"width": 1920, "height": 1080}
  - Assert page.set_default_navigation_timeout(60000) is called

- [ ] Task 2: Update setup_browser() in price_monitor.py
  <!-- files: price_monitor.py -->
  <!-- depends: task1 -->
  - Add args list to chromium.launch()
  - Add viewport to new_context()
  - Call page.set_default_navigation_timeout(60000) on the new page
  - Commit: `fix(scraper): add CI-safe launch args and 60s nav timeout to Playwright`

- [ ] Task: Conductor - User Manual Verification 'Browser Hardening' (Protocol in workflow.md)

## Phase 2: Error Handling Fix

- [ ] Task 1: Add tests for cascade-free error path in test_price_monitor.py
  <!-- files: test_price_monitor.py -->
  - Simulate page.goto() raising TimeoutError → assert process_booking returns None cleanly
  - Assert error screenshot failure does NOT propagate (wrapped in try/except)
  - Simulate first goto fails, second succeeds → assert prices returned (retry works)

- [ ] Task 2: Fix process_booking() in price_monitor.py
  <!-- files: price_monitor.py -->
  <!-- depends: task1 -->
  - Wrap error screenshot in its own try/except
  - Add one navigation retry: on TimeoutError, wait 5 s and try page.goto once more
  - Commit: `fix(scraper): guard error screenshot from cascade, add nav retry`

- [ ] Task: Conductor - User Manual Verification 'Error Handling Fix' (Protocol in workflow.md)

## Phase 3: gh CLI + CI Validation
<!-- depends: phase1, phase2 -->

- [ ] Task 1: Install and authenticate gh CLI
  - brew install gh
  - gh auth login (personal access token with repo + workflow scope)
  - Verify with: gh workflow list

- [ ] Task 2: Trigger price-checker on feature branch and confirm it passes
  - gh workflow run price-checker.yaml \
      --ref feature/2026-02-19-version \
      -f action=check-prices
  - gh run watch  (monitor live log)
  - Confirm: scraper completes, email arrives with new subject line format

- [ ] Task: Conductor - User Manual Verification 'CI Validation' (Protocol in workflow.md)
