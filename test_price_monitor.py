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
