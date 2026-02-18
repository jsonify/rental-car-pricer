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

        mock_pw.chromium.launch.assert_called_once_with(headless=True)

    def test_launches_chromium_headed_when_requested(self):
        """setup_browser(headless=False) launches headed."""
        mock_sp, mock_pw, *_ = self._make_mocks()
        with patch("price_monitor.sync_playwright", mock_sp):
            from price_monitor import setup_browser
            setup_browser(headless=False)

        mock_pw.chromium.launch.assert_called_once_with(headless=False)

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
