# Spec: Fix Playwright CI Navigation + gh CLI Workflow

## Overview

The Playwright-based scraper times out navigating to Costco Travel in GitHub Actions
while the previous Selenium implementation worked. Root causes:

1. `setup_browser()` is missing CI-essential and anti-detection launch args that
   Selenium had (`--disable-blink-features=AutomationControlled`, `--no-sandbox`,
   `--disable-dev-shm-usage`, viewport, etc.)
2. When `page.goto()` times out, the `except` block calls `page.screenshot()` on
   the dead page, causing a second timeout cascade instead of a clean failure.
3. No `gh` CLI workflow exists for triggering/monitoring runs from the terminal.

## Functional Requirements

### 1. Playwright Browser Hardening

- Add CI/headless launch args to `setup_browser()`:
  - `--disable-blink-features=AutomationControlled`
  - `--no-sandbox` (required in CI Linux runners)
  - `--disable-dev-shm-usage` (prevents shared-memory OOM in CI)
  - `--disable-infobars`
  - `--window-size=1920,1080`
- Set explicit viewport: `viewport={"width": 1920, "height": 1080}`
- Increase default navigation timeout to 60 s (from default 30 s)
- Keep existing `user_agent` and `WEBDRIVER_STEALTH_SCRIPT`

### 2. Resilient Error Handling

- Wrap the error screenshot in its own `try/except` so a dead page does not
  cascade into a second timeout
- Add one automatic retry on navigation failure before returning `None`

### 3. gh CLI Local Workflow

- Install `gh` CLI and authenticate
- Trigger a run: `gh workflow run price-checker.yaml --ref <branch> -f action=check-prices`
- Monitor live logs: `gh run watch` / `gh run view --log`

## Non-Functional Requirements

- No new Python dependencies
- `gh` commands used operationally (not scripted into production code)

## Acceptance Criteria

- `price-checker` workflow completes successfully on `feature/2026-02-19-version`
- Navigation timeout no longer causes a cascade screenshot failure
- A single `gh` command can trigger and monitor a run from the terminal

## Out of Scope

- Proxy / residential IP rotation
- Full Playwright stealth library (`playwright-stealth` package)
