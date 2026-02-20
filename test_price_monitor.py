#!/usr/bin/env python3
"""
Unit tests for price_monitor.py — Playwright-based browser setup and scraping.
Run: python3 -m pytest test_price_monitor.py -v
"""

import pytest
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Phase 2: setup_browser()
# ---------------------------------------------------------------------------

class TestSetupBrowser:
    """Tests for setup_browser() — the Playwright browser initializer."""

    def _make_mocks(self):
        """Return a tuple of mock objects wired up to simulate sync_playwright()."""
        mock_page = MagicMock(name="page")
        mock_context = MagicMock(name="context")
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock(name="browser")
        mock_browser.new_context.return_value = mock_context

        mock_pw = MagicMock(name="playwright_instance")
        mock_pw.chromium.launch.return_value = mock_browser

        mock_sync_playwright = MagicMock(name="sync_playwright")
        mock_sync_playwright.return_value.start.return_value = mock_pw

        return mock_sync_playwright, mock_pw, mock_browser, mock_context, mock_page

    def test_returns_four_tuple(self):
        """setup_browser() returns (playwright, browser, context, page)."""
        mock_sp, mock_pw, mock_browser, mock_context, mock_page = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            result = setup_browser()

        assert len(result) == 4
        pw, browser, context, page = result
        assert pw is mock_pw
        assert browser is mock_browser
        assert context is mock_context
        assert page is mock_page

    def test_launches_chromium_headless_by_default(self):
        """Chromium is launched headless=True by default."""
        mock_sp, mock_pw, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        assert mock_pw.chromium.launch.call_args[1]["headless"] is True

    def test_launches_chromium_headed_when_requested(self):
        """setup_browser(headless=False) launches headed."""
        mock_sp, mock_pw, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser(headless=False)

        assert mock_pw.chromium.launch.call_args[1]["headless"] is False

    def test_launch_args_include_ci_flags(self):
        """chromium.launch() args include the CI-required anti-detection flags."""
        mock_sp, mock_pw, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        launch_args = mock_pw.chromium.launch.call_args[1].get("args", [])
        assert "--no-sandbox" in launch_args
        assert "--disable-dev-shm-usage" in launch_args
        assert "--disable-blink-features=AutomationControlled" in launch_args

    def test_context_has_1920x1080_viewport(self):
        """Browser context is created with a 1920×1080 viewport."""
        mock_sp, mock_pw, mock_browser, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        call_kwargs = mock_browser.new_context.call_args[1]
        assert call_kwargs.get("viewport") == {"width": 1920, "height": 1080}

    def test_sets_60s_navigation_timeout(self):
        """page.set_default_navigation_timeout(60000) is called after page creation."""
        mock_sp, mock_pw, mock_browser, mock_context, mock_page = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        mock_page.set_default_navigation_timeout.assert_called_once_with(60000)

    def test_sets_mozilla_user_agent_on_context(self):
        """Browser context is created with a Mozilla user-agent string."""
        mock_sp, mock_pw, mock_browser, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        call_kwargs = mock_browser.new_context.call_args[1]
        assert "user_agent" in call_kwargs
        assert "Mozilla" in call_kwargs["user_agent"]

    def test_adds_webdriver_stealth_script(self):
        """add_init_script is called with the navigator.webdriver override."""
        mock_sp, mock_pw, mock_browser, mock_context, mock_page = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser()

        mock_context.add_init_script.assert_called_once()
        script_arg = mock_context.add_init_script.call_args[0][0]
        assert "navigator" in script_arg
        assert "webdriver" in script_arg
        assert "undefined" in script_arg


# ---------------------------------------------------------------------------
# Phase 3: Form automation helpers
# ---------------------------------------------------------------------------

def _mock_page():
    """Return a MagicMock wired to behave like a Playwright page."""
    page = MagicMock(name="page")
    locator = MagicMock(name="locator")
    page.locator.return_value = locator
    return page, locator


class TestEnterLocation:
    """Tests for enter_location(page, location)."""

    def test_types_with_positive_delay(self):
        """Location is typed character-by-character with a delay > 0."""
        page, locator = _mock_page()
        from price_monitor import enter_location
        enter_location(page, "KOA")

        locator.type.assert_called_once()
        _, kwargs = locator.type.call_args
        assert kwargs.get("delay", 0) > 0

    def test_types_correct_location_code(self):
        """The location string is passed to type()."""
        page, locator = _mock_page()
        from price_monitor import enter_location
        enter_location(page, "KOA")

        args, _ = locator.type.call_args
        assert "KOA" in args

    def test_clicks_dropdown_item(self):
        """A dropdown locator is clicked after typing."""
        page, locator = _mock_page()
        from price_monitor import enter_location
        enter_location(page, "KOA")

        # locator() is called multiple times — for the input field and dropdown
        assert page.locator.call_count >= 2

    def test_focuses_input_rather_than_clicking(self):
        """focus() activates the field instead of click() to bypass sticky-header
        pointer-event interception on Costco Travel."""
        page, locator = _mock_page()
        from price_monitor import enter_location
        enter_location(page, "KOA")
        locator.focus.assert_called()


class TestEnterDate:
    """Tests for enter_date(page, field_id, date_value)."""

    def _make_page_success(self, expected_date):
        page, locator = _mock_page()
        locator.input_value.return_value = expected_date
        return page, locator

    def _make_page_failure(self):
        page, locator = _mock_page()
        locator.input_value.return_value = ""  # Always wrong
        return page, locator

    def test_returns_true_when_date_entered_correctly(self):
        """Returns True when input_value() matches the expected date."""
        page, locator = self._make_page_success("04/01/2025")
        from price_monitor import enter_date
        result = enter_date(page, "pickUpDateWidget", "04/01/2025")
        assert result is True

    def test_returns_false_after_all_retries_exhausted(self):
        """Returns False when input never matches after max_retries attempts."""
        page, locator = self._make_page_failure()
        from price_monitor import enter_date
        result = enter_date(page, "pickUpDateWidget", "04/01/2025", max_retries=3)
        assert result is False

    def test_presses_tab_after_typing(self):
        """Tab key is pressed after typing to trigger blur events."""
        page, locator = self._make_page_success("04/01/2025")
        from price_monitor import enter_date
        enter_date(page, "pickUpDateWidget", "04/01/2025")
        page.keyboard.press.assert_called_with("Tab")

    def test_retries_correct_number_of_times(self):
        """Retries exactly max_retries times when date never matches."""
        page, locator = self._make_page_failure()
        from price_monitor import enter_date
        enter_date(page, "pickUpDateWidget", "04/01/2025", max_retries=3)
        assert locator.type.call_count == 3

    def test_types_with_positive_delay(self):
        """Date is typed with a positive delay for human-like behavior."""
        page, locator = self._make_page_success("04/01/2025")
        from price_monitor import enter_date
        enter_date(page, "pickUpDateWidget", "04/01/2025")
        _, kwargs = locator.type.call_args
        assert kwargs.get("delay", 0) > 0

    def test_focuses_date_field_rather_than_clicking(self):
        """focus() is used instead of click() to avoid sticky-header interception."""
        page, locator = self._make_page_success("04/01/2025")
        from price_monitor import enter_date
        enter_date(page, "pickUpDateWidget", "04/01/2025")
        locator.focus.assert_called()


class TestSetTimes:
    """Tests for set_times(page, pickup_time, dropoff_time)."""

    def test_selects_both_pickup_and_dropoff(self):
        """select_option is called twice — once for each time field."""
        page, _ = _mock_page()
        from price_monitor import set_times
        set_times(page, "12:00 PM", "12:00 PM")
        assert page.select_option.call_count == 2

    def test_passes_correct_time_values(self):
        """Correct time strings are passed to select_option."""
        page, _ = _mock_page()
        from price_monitor import set_times
        set_times(page, "10:00 AM", "2:00 PM")
        calls = [c[0] for c in page.select_option.call_args_list]
        assert any("10:00 AM" in str(c) for c in calls)
        assert any("2:00 PM" in str(c) for c in calls)


class TestCheckAgeCheckbox:
    """Tests for check_age_checkbox(page)."""

    def test_clicks_when_unchecked(self):
        """Checkbox is clicked when is_checked() returns False."""
        page, locator = _mock_page()
        locator.is_checked.return_value = False
        from price_monitor import check_age_checkbox
        check_age_checkbox(page)
        locator.click.assert_called_once()

    def test_skips_click_when_already_checked(self):
        """Checkbox is NOT clicked when is_checked() returns True."""
        page, locator = _mock_page()
        locator.is_checked.return_value = True
        from price_monitor import check_age_checkbox
        check_age_checkbox(page)
        locator.click.assert_not_called()


class TestClickSearch:
    """Tests for click_search(page)."""

    def test_scrolls_into_view_before_clicking(self):
        """scroll_into_view_if_needed() is called before click()."""
        page, locator = _mock_page()
        from price_monitor import click_search
        click_search(page)
        locator.scroll_into_view_if_needed.assert_called_once()
        locator.click.assert_called_once()


class TestFillSearchForm:
    """Tests for fill_search_form(page, booking)."""

    BOOKING = {
        "location": "KOA",
        "pickup_date": "04/01/2025",
        "dropoff_date": "04/08/2025",
        "pickup_time": "12:00 PM",
        "dropoff_time": "12:00 PM",
        "focus_category": "Economy Car",
    }

    def test_returns_true_on_success(self):
        """Returns True when all sub-steps succeed."""
        page, locator = _mock_page()
        locator.input_value.return_value = "04/01/2025"  # date entry succeeds
        locator.is_checked.return_value = True
        with patch("price_monitor.enter_location"), \
             patch("price_monitor.enter_date", return_value=True), \
             patch("price_monitor.set_times"), \
             patch("price_monitor.check_age_checkbox"):
            from price_monitor import fill_search_form
            result = fill_search_form(page, self.BOOKING)
        assert result is True

    def test_returns_false_when_date_entry_fails(self):
        """Returns False when enter_date() fails."""
        page, _ = _mock_page()
        with patch("price_monitor.enter_location"), \
             patch("price_monitor.enter_date", return_value=False), \
             patch("price_monitor.set_times"), \
             patch("price_monitor.check_age_checkbox"):
            from price_monitor import fill_search_form
            result = fill_search_form(page, self.BOOKING)
        assert result is False


class TestWaitForResults:
    """Tests for wait_for_results(page, current_url)."""

    def test_returns_true_on_successful_url_change(self):
        """Returns True when wait_for_url() succeeds."""
        page, _ = _mock_page()
        page.wait_for_url = MagicMock()  # does not raise
        from price_monitor import wait_for_results
        result = wait_for_results(page, "https://www.costcotravel.com/Rental-Cars")
        assert result is True

    def test_returns_false_on_timeout(self):
        """Returns False when wait_for_url() raises (timeout)."""
        page, _ = _mock_page()
        page.wait_for_url = MagicMock(side_effect=Exception("Timeout"))
        from price_monitor import wait_for_results
        result = wait_for_results(page, "https://www.costcotravel.com/Rental-Cars")
        assert result is False


# ---------------------------------------------------------------------------
# Phase 2: process_booking() error handling — cascade guard and nav retry
# ---------------------------------------------------------------------------

class TestProcessBooking:
    """Tests for process_booking() error path — cascade guard and nav retry."""

    BOOKING = {
        "location": "KOA",
        "pickup_date": "04/01/2025",
        "dropoff_date": "04/08/2025",
        "pickup_time": "12:00 PM",
        "dropoff_time": "12:00 PM",
        "focus_category": "Economy Car",
    }

    def _stub_price_extractor(self, prices=None):
        """Insert a stub price_extractor into sys.modules so process_booking can import it."""
        import sys, types as _t
        stub = _t.ModuleType("price_extractor")
        stub.extract_lowest_prices = MagicMock(return_value=prices or {})
        sys.modules["price_extractor"] = stub

    def test_returns_none_when_navigation_always_fails(self):
        """Returns None cleanly when goto() times out on all attempts."""
        self._stub_price_extractor()
        page = MagicMock()
        page.goto.side_effect = Exception("Timeout")

        from price_monitor import process_booking
        result = process_booking(page, self.BOOKING)
        assert result is None

    def test_error_screenshot_failure_does_not_propagate(self):
        """Exception from error screenshot is swallowed — returns None cleanly."""
        self._stub_price_extractor()
        page = MagicMock()
        page.goto.side_effect = Exception("Timeout")
        page.screenshot.side_effect = Exception("Screenshot timeout")

        from price_monitor import process_booking
        result = process_booking(page, self.BOOKING)
        assert result is None

    def test_retries_navigation_once_and_returns_prices_on_success(self):
        """On first goto timeout, retries once; prices returned when retry succeeds."""
        mock_prices = {"Economy Car": 299.99}
        self._stub_price_extractor(mock_prices)
        page = MagicMock()
        page.goto.side_effect = [Exception("Timeout"), None]  # first fails, retry succeeds
        page.url = "https://www.costcotravel.com/Rental-Cars"

        with patch("price_monitor.fill_search_form", return_value=True), \
             patch("price_monitor.click_search"), \
             patch("price_monitor.wait_for_results", return_value=True):
            from price_monitor import process_booking
            result = process_booking(page, self.BOOKING)

        assert result == mock_prices
        assert page.goto.call_count == 2  # first attempt + one retry
