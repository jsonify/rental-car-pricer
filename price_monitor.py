# price_monitor.py
#
# Playwright-based browser automation for Costco Travel scraping.
# Replaces the old Selenium driver_setup.py + human_simulation.py.

import random
import re
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
    locator.focus()
    page.wait_for_timeout(random.randint(500, 1000))
    locator.type(location, delay=150)
    page.wait_for_timeout(random.randint(1500, 2500))
    # Click first dropdown item containing the location code
    dropdown = page.locator(f'li:has-text("{location}")').first
    dropdown.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(random.randint(500, 1000))
    dropdown.click()
    page.wait_for_timeout(random.randint(1000, 2000))


def enter_date(page, field_id, date_value, max_retries=3):
    """
    Clear a date field, type the value with delay, Tab to blur, verify.

    Returns True if the entered value matches date_value, False after
    max_retries unsuccessful attempts.
    """
    for attempt in range(max_retries):
        locator = page.locator(f"#{field_id}")
        locator.wait_for(state="attached")
        locator.focus()
        page.wait_for_timeout(random.randint(300, 700))
        # Clear via JS to avoid stale value issues
        page.eval_on_selector(f"#{field_id}", "el => el.value = ''")
        locator.focus()
        locator.type(date_value, delay=150)
        page.keyboard.press("Tab")
        page.wait_for_timeout(random.randint(1000, 1500))
        entered = locator.input_value()
        print(f"Entered date for {field_id}: {entered}")
        if entered == date_value:
            return True
        if attempt < max_retries - 1:
            print(f"Date entry failed, attempt {attempt + 1}/{max_retries}")
    return False


def set_times(page, pickup_time, dropoff_time):
    """Select pickup and dropoff times from the dropdown selects."""
    page.select_option("#pickupTimeWidget", pickup_time)
    page.wait_for_timeout(random.randint(500, 1000))
    page.select_option("#dropoffTimeWidget", dropoff_time)
    page.wait_for_timeout(random.randint(500, 1000))


def check_age_checkbox(page):
    """Ensure the 25+ age checkbox is checked."""
    checkbox = page.locator("#driversAgeWidget")
    if not checkbox.is_checked():
        page.wait_for_timeout(random.randint(500, 1000))
        checkbox.click()
        page.wait_for_timeout(random.randint(500, 1000))


def click_search(page):
    """Submit the search form via JS to bypass sticky-header interception.

    Playwright's locator.click() ALWAYS calls scroll_into_view_if_needed()
    internally as part of its actionability checks, placing #findMyCarButton
    at the viewport top — directly under the fixed sticky header — regardless
    of any prior scroll we do. Using el.click() in the browser JS context
    bypasses Playwright's scroll-and-click mechanism entirely, dispatching
    the event directly to the button element.
    """
    search_btn = page.locator("#findMyCarButton")
    search_btn.wait_for(state="visible")
    page.wait_for_timeout(random.randint(500, 1000))
    page.eval_on_selector("#findMyCarButton", "el => el.click()")


def fill_search_form(page, booking):
    """Fill the complete Costco Travel search form for a booking.

    Returns True on success, False on failure.
    """
    try:
        print(f"\nFilling form for {booking['location']}...")
        enter_location(page, booking["location"])

        pickup_ok = enter_date(page, "pickUpDateWidget", booking["pickup_date"])
        dropoff_ok = enter_date(page, "dropOffDateWidget", booking["dropoff_date"])
        if not (pickup_ok and dropoff_ok):
            print("Date entry failed after retries")
            return False

        set_times(page, booking["pickup_time"], booking["dropoff_time"])
        check_age_checkbox(page)
        return True
    except Exception as e:
        print(f"Error filling form: {str(e)}")
        traceback.print_exc()
        return False


def wait_for_results(page, current_url, timeout=60):
    """Wait for the search results URL. Returns True on success."""
    try:
        page.wait_for_url(
            re.compile(r"results|vehicles", re.IGNORECASE),
            timeout=timeout * 1000,
        )
        page.wait_for_timeout(5000)  # Let prices fully render
        return True
    except Exception as e:
        print(f"Error waiting for results: {str(e)}")
        return False


def get_available_categories(page):
    """Extract available vehicle category names from the results page."""
    categories = set()
    try:
        rows = page.locator('div[role="row"]').all()
        for row in rows:
            try:
                name = row.locator("div.inner.text-center.h3-tag-style").text_content()
                if name:
                    categories.add(name.strip())
            except Exception:
                continue
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
    return categories


def validate_category(page, category, location):
    """Navigate and verify that a category exists for the given location."""
    from datetime import timedelta

    try:
        page.goto("https://www.costcotravel.com/Rental-Cars")
        page.wait_for_timeout(random.randint(2000, 4000))

        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")

        enter_location(page, location)
        enter_date(page, "pickUpDateWidget", tomorrow)
        enter_date(page, "dropOffDateWidget", day_after)
        set_times(page, "12:00 PM", "12:00 PM")
        check_age_checkbox(page)

        current_url = page.url
        click_search(page)

        if not wait_for_results(page, current_url):
            return False

        available = get_available_categories(page)
        if category not in available:
            print(f"\nCategory '{category}' not available at {location}")
            print("Available categories:")
            for cat in sorted(available):
                print(f"  - {cat}")
            return False
        return True
    except Exception as e:
        print(f"Error validating category: {str(e)}")
        return False


def process_booking(page, booking):
    """Run a full price scrape for one booking. Returns price dict or None."""
    from price_extractor import extract_lowest_prices

    try:
        print(f"\nChecking prices for {booking['location']}")
        print(f"{booking['pickup_date']} to {booking['dropoff_date']}")
        print(f"Focus category: {booking['focus_category']}")

        try:
            page.goto("https://www.costcotravel.com/Rental-Cars")
        except Exception:
            print("Navigation timed out — retrying once after 5 s...")
            page.wait_for_timeout(5000)
            page.goto("https://www.costcotravel.com/Rental-Cars")  # may raise → caught by outer except

        page.wait_for_timeout(random.randint(2000, 4000))

        if not fill_search_form(page, booking):
            raise Exception("Failed to fill search form")

        # Verify form values
        print("\nVerifying form fields:")
        print(f"  Pickup:  {page.locator('#pickUpDateWidget').input_value()}")
        print(f"  Dropoff: {page.locator('#dropOffDateWidget').input_value()}")

        current_url = page.url
        print("\nInitiating search...")
        click_search(page)

        if not wait_for_results(page, current_url):
            raise Exception("Failed to load results")

        print("Results loaded successfully")

        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"results_{booking['location']}_{timestamp}.png"
        page.screenshot(path=f"screenshots/{screenshot_name}")
        print(f"Screenshot saved: {screenshot_name}")

        prices = extract_lowest_prices(page)

        if booking["focus_category"] not in prices:
            print(f"\nWarning: '{booking['focus_category']}' not in results!")
            print("Available:", sorted(prices.keys()))

        return prices

    except Exception as e:
        print(f"Error processing booking: {str(e)}")
        traceback.print_exc()

        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_name = f"error_{booking['location']}_{timestamp}.png"
        try:
            page.screenshot(path=f"screenshots/{error_name}")
            print(f"Error screenshot saved: {error_name}")
        except Exception:
            print("Error screenshot failed (page already closed)")

        return None


def run_price_checks(tracker, active_bookings):
    """Launch Playwright browser and run price checks for all active bookings."""
    from services.price_alert_service import PriceAlertService
    from email_module import send_price_alert

    # Use real Google Chrome in CI for proper TLS fingerprint (Playwright's
    # bundled Chromium is blocked by Costco Travel's bot-detection on GH Actions)
    channel = "chrome" if os.environ.get("CI") == "true" else None
    playwright, browser, context, page = setup_browser(headless=True, channel=channel)
    alert_service = PriceAlertService(price_threshold=10.0)

    deleted_bookings = tracker.cleanup_expired_bookings()
    if deleted_bookings:
        print("\nCleaned up expired bookings:")
        for booking_id in deleted_bookings:
            print(f"  - {booking_id}")

    try:
        bookings_data = []

        for booking in active_bookings:
            try:
                from datetime import datetime as _dt
                dropoff_date = _dt.strptime(booking["dropoff_date"], "%m/%d/%Y").date()
                if dropoff_date < _dt.now().date():
                    print(f"Skipping expired: {booking['location']} - {booking['dropoff_date']}")
                    continue
            except ValueError:
                print(f"Error parsing date for booking: {booking['location']}")
                continue

            prices = process_booking(page, booking)

            if prices:
                category_slug = re.sub(r"[^a-zA-Z0-9]", "", booking["focus_category"])
                booking_id = (
                    f"{booking['location']}_{booking['pickup_date']}_"
                    f"{booking['dropoff_date']}_{category_slug}"
                ).replace("/", "")

                tracker.update_prices(booking_id, prices)
                trends = tracker.get_price_trends(booking_id)

                current_price = prices.get(booking["focus_category"])
                previous_price = None
                if booking.get("price_history"):
                    prev = booking["price_history"][-2] if len(booking["price_history"]) > 1 else None
                    if prev and "prices" in prev:
                        previous_price = prev["prices"].get(booking["focus_category"])

                has_significant_drop = False
                if current_price is not None and previous_price is not None:
                    drop = previous_price - current_price
                    if drop >= alert_service.price_threshold:
                        has_significant_drop = True
                        print(f"Significant drop for {booking['location']}: ${drop:.2f}")

                bookings_data.append({
                    "booking": booking,
                    "prices": prices,
                    "trends": trends,
                    "has_significant_drop": has_significant_drop,
                })
                print(f"\nPrices updated for {booking['location']}")
            else:
                print(f"\nFailed to get prices for {booking['location']}")

            page.wait_for_timeout(random.randint(2000, 4000))

        if bookings_data:
            print(f"\nSending email for {len(bookings_data)} bookings")
            send_price_alert(bookings_data)
        else:
            print("\nNo bookings data to send")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        print("\nClosing browser...")
        browser.close()
        playwright.stop()

    return bool(bookings_data)


def setup_browser(headless=True, channel=None):
    """
    Launch a Playwright browser with stealth settings.

    Pass channel="chrome" to use the installed Google Chrome binary instead
    of Playwright's bundled Chromium (required in CI to match the TLS
    fingerprint that Costco Travel's bot-detection expects).

    Returns (playwright, browser, context, page). The caller is responsible
    for teardown:
        browser.close()
        playwright.stop()
    """
    playwright = sync_playwright().start()
    launch_kwargs = {
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            "--window-size=1920,1080",
        ],
    }
    if channel:
        launch_kwargs["channel"] = channel
    browser = playwright.chromium.launch(**launch_kwargs)
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1920, "height": 1080},
    )
    context.add_init_script(WEBDRIVER_STEALTH_SCRIPT)
    page = context.new_page()
    page.set_default_navigation_timeout(60000)
    return playwright, browser, context, page
