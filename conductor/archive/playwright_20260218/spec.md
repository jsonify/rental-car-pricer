# Spec: Playwright Migration

## Overview

Replace the Selenium-based browser automation with Microsoft Playwright. The current
Selenium implementation has three core problems:

1. **Hardcoded binary paths** — `driver_setup.py` and `price_monitor.py` reference local
   machine paths for Chrome and ChromeDriver, making the scraper non-portable.
2. **Fragile CI setup** — `price-checker.yaml` has ~50 lines of manual Chrome/ChromeDriver
   download logic that must stay in sync with each other's versions.
3. **Custom human simulation** — `human_simulation.py` implements char-by-char typing
   delays that Playwright provides natively.

Playwright solves all three: it self-manages browser binaries, provides a single install
command for CI, and has built-in `delay` support for human-like typing.

## Functional Requirements

### FR-1: Browser Management
- Playwright manages Chromium via `playwright install chromium`
- No hardcoded binary or chromedriver paths anywhere in the codebase
- Browser launches headless in CI, headless by default locally (configurable)

### FR-2: Form Automation
All existing form interactions ported to Playwright API:
- Location autocomplete: type into field + wait for and click dropdown item
- Date fields: clear + fill with built-in typing delay + Tab to blur
- Time dropdowns: select by value using `page.select_option()`
- Age checkbox: check state + click if unchecked
- Search button: scroll into view + click
- Retain retry logic (up to 3 attempts) for date entry verification

### FR-3: Price Extraction
CSS selectors from `price_extractor.py` are preserved and ported to Playwright's
`page.locator()` API:
- `div[role="row"]` — category rows
- `div.inner.text-center.h3-tag-style` — category name
- `a.card.car-result-card.lowest-price` — lowest-price card per category
- `data-price` attribute — price value
Extracted prices returned as the same `{category_name: float}` dict.

### FR-4: Human-Like Behavior
- Delete `human_simulation.py`; replace with Playwright built-ins:
  - `page.locator(sel).type(text, delay=150)` for character-by-character typing
  - `page.wait_for_timeout(ms)` for pauses between actions
- Retain randomized wait durations (uniform random in existing ranges)
- Stealth via `add_init_script`:
  ```python
  context.add_init_script(
      "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
  )
  ```

### FR-5: Screenshots
- Error screenshots: `error_{LOCATION}_{TIMESTAMP}.png` via `page.screenshot(path=...)`
- Results screenshots: `results_{LOCATION}_{TIMESTAMP}.png` via `page.screenshot(path=...)`

### FR-6: GitHub Actions CI
Replace the manual Chrome/ChromeDriver download block in `price-checker.yaml` with:
```yaml
- name: Install Playwright Chromium
  run: playwright install chromium --with-deps
```
Update the pip install step to include `playwright` instead of `selenium`.

## Non-Functional Requirements

- **NFR-1 — No ChromeDriver management**: Zero hardcoded paths, zero manual download steps
- **NFR-2 — Behavioral parity**: Same bookings scraped, same data format returned, Supabase
  sync and email notifications unaffected
- **NFR-3 — Sync API**: Use Playwright's synchronous Python API (not async) to match
  existing code style

## Files Changed

| File | Action |
|------|--------|
| `driver_setup.py` | Delete |
| `human_simulation.py` | Delete |
| `price_monitor.py` | Rewrite — port all Selenium → Playwright |
| `price_extractor.py` | Update — replace selenium imports with Playwright page calls |
| `requirements.txt` | Remove `selenium`, add `playwright` |
| `.github/workflows/price-checker.yaml` | Replace Chrome setup block with `playwright install chromium` |

## Acceptance Criteria

- [ ] `driver_setup.py` and `human_simulation.py` are deleted
- [ ] No `from selenium` or `import selenium` anywhere in the codebase
- [ ] `playwright install chromium --with-deps` is the only browser setup needed in CI
- [ ] Price scraping runs successfully end-to-end (confirmed via test run or screenshot)
- [ ] `price_history.json` and Supabase receive correct prices after a run
- [ ] Screenshots saved on both success and error paths
- [ ] GitHub Actions workflow passes without manual Chrome download steps

## Out of Scope

- Switching to Playwright's async API
- Proxy/VPN support at the browser level
- Changes to Supabase sync, email alerts, or booking management logic
- Adding new price categories or changing scraping targets
