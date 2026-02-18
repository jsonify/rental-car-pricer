# price_monitor.py
#
# Playwright-based browser automation for Costco Travel scraping.
# Replaces the old Selenium driver_setup.py + human_simulation.py.

import random
import time
import traceback
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

WEBDRIVER_STEALTH_SCRIPT = (
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)


def enter_location(page, location):
    """Type location code into the pickup field and select from autocomplete."""
    locator = page.locator("#pickupLocationTextWidget")
    locator.wait_for(state="visible")
    locator.click()
    page.wait_for_timeout(random.randint(500, 1000))
    locator.type(location, delay=150)
    page.wait_for_timeout(random.randint(1500, 2500))
    # Click first dropdown item containing the location code
    dropdown = page.locator(f'li:has-text("{location}")').first
    dropdown.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(random.randint(500, 1000))
    dropdown.click()
    page.wait_for_timeout(random.randint(1000, 2000))


def setup_browser(headless=True):
    """
    Launch a Playwright Chromium browser with stealth settings.

    Returns (playwright, browser, context, page). The caller is responsible
    for teardown:
        browser.close()
        playwright.stop()
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(user_agent=USER_AGENT)
    context.add_init_script(WEBDRIVER_STEALTH_SCRIPT)
    page = context.new_page()
    return playwright, browser, context, page
