# Plan: Playwright Migration

## Phase 1: Dependencies & Cleanup

- [x] Task 1: Update `requirements.txt`
  - Remove `selenium` and any selenium-related packages
  - Add `playwright`

- [x] Task 2: Delete `driver_setup.py` and `human_simulation.py`
  - Confirm no other files import from these modules before deleting
  - Commit: `chore(scraper): delete Selenium driver and human simulation modules`

- [ ] Task: Conductor - User Manual Verification 'Dependencies & Cleanup' (Protocol in workflow.md)

## Phase 2: Browser Setup

- [ ] Task 1: Write unit tests for new `setup_browser()` function
  - Mock `sync_playwright()` context manager
  - Assert Chromium launched with `headless=True`
  - Assert `add_init_script` called with webdriver override
  - Assert custom user agent set on context

- [ ] Task 2: Implement `setup_browser()` in `price_monitor.py`
  - `sync_playwright()` → `p.chromium.launch(headless=True)`
  - `browser.new_context(user_agent="Mozilla/5.0 ...")`
  - `context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")`
  - Returns `(playwright, browser, context, page)` — caller manages teardown
  - Commit: `feat(scraper): add Playwright browser setup`

- [ ] Task: Conductor - User Manual Verification 'Browser Setup' (Protocol in workflow.md)

## Phase 3: Port Form Automation

- [ ] Task 1: Write tests for form interaction helpers
  - Mock `page.locator()`, `page.wait_for_timeout()`, `page.select_option()`
  - Cover location typing + dropdown selection
  - Cover date entry retry logic (3 attempts)
  - Cover time selects and age checkbox

- [ ] Task 2: Port location input and autocomplete dropdown
  - `page.locator('#pickupLocationTextWidget').type(location, delay=150)`
  - `page.wait_for_selector('li:has-text("...")')` then click
  - Commit: `feat(scraper): port location autocomplete to Playwright`

- [ ] Task 3: Port date entry with retry logic
  - Clear via JS + fill with `type(delay=150)` + Tab to blur
  - Verify `input_element.input_value() == expected` — retry up to 3×
  - Commit: `feat(scraper): port date entry to Playwright`

- [ ] Task 4: Port time selects, age checkbox, and search button
  - `page.select_option('#pickupTimeWidget', '12:00 PM')`
  - Checkbox: check `.is_checked()` → click if unchecked
  - Search: `page.locator('#findMyCarButton').scroll_into_view_if_needed()` → click
  - Commit: `feat(scraper): port search form controls to Playwright`

- [ ] Task: Conductor - User Manual Verification 'Form Automation' (Protocol in workflow.md)

## Phase 4: Port Price Extraction

- [ ] Task 1: Write unit tests for `extract_lowest_prices(page)`
  - Mock `page.locator('div[role="row"]').all()` returning fake row locators
  - Assert returns `{category_name: float}` dict
  - Assert price parsed from `data-price` attribute

- [ ] Task 2: Update `price_extractor.py` to use Playwright API
  - `page.locator('div[role="row"]').all()` → iterate rows
  - `.locator('div.inner.text-center.h3-tag-style').text_content()` for name
  - `.locator('a.card.car-result-card.lowest-price').get_attribute('data-price')` for price
  - Return format unchanged: `{category_name: float}`
  - Commit: `feat(scraper): port price extraction to Playwright`

- [ ] Task: Conductor - User Manual Verification 'Price Extraction' (Protocol in workflow.md)

## Phase 5: CI Update

- [ ] Task 1: Update `.github/workflows/price-checker.yaml`
  - Remove the ~50-line "Setup Chrome and ChromeDriver" block
  - Add step: `playwright install chromium --with-deps`
  - Update pip install step: add `playwright`, remove `selenium`
  - Commit: `ci: replace selenium Chrome setup with playwright install`

- [ ] Task: Conductor - User Manual Verification 'CI Update' (Protocol in workflow.md)

## Phase 6: Validation

- [ ] Task 1: Verify no Selenium imports remain
  - Grep codebase: `from selenium` / `import selenium` returns zero matches

- [ ] Task 2: End-to-end validation
  - Run `python3 main.py` (or `python3 price_monitor.py`) locally
  - Confirm screenshot saved and prices extracted successfully
  - Confirm `price_history.json` updated with correct data

- [ ] Task: Conductor - User Manual Verification 'Validation' (Protocol in workflow.md)
