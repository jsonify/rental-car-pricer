#!/usr/bin/env python3
"""
Unit tests for price_extractor.py — Playwright-based price extraction.
Run: python3 -m pytest test_price_extractor.py -v
"""

import pytest
from unittest.mock import MagicMock, patch


def _make_row_mock(category_name, price_str):
    """Return a mock Playwright Locator for a single results row."""
    name_locator = MagicMock()
    name_locator.text_content.return_value = category_name

    price_locator = MagicMock()
    price_locator.get_attribute.return_value = price_str

    row = MagicMock()

    def row_locator_side_effect(selector):
        if "inner" in selector:
            return name_locator
        return price_locator

    row.locator.side_effect = row_locator_side_effect
    return row


def _make_page_mock(rows):
    """Return a mock Playwright page whose div[role='row'] locator returns rows."""
    page = MagicMock()
    rows_locator = MagicMock()
    rows_locator.all.return_value = rows
    page.locator.return_value = rows_locator
    return page


class TestExtractLowestPrices:
    """Tests for extract_lowest_prices(page)."""

    def test_returns_dict_with_category_and_float_price(self):
        """Returns {category_name: float} for a single valid row."""
        row = _make_row_mock("Economy Car", "299.99")
        page = _make_page_mock([row])

        with patch("price_extractor.save_prices_to_file"):
            from price_extractor import extract_lowest_prices
            result = extract_lowest_prices(page)

        assert result == {"Economy Car": 299.99}

    def test_returns_multiple_categories(self):
        """Returns all categories found across multiple rows."""
        rows = [
            _make_row_mock("Economy Car", "299.99"),
            _make_row_mock("Full-size Car", "399.99"),
            _make_row_mock("Compact SUV", "449.00"),
        ]
        page = _make_page_mock(rows)

        with patch("price_extractor.save_prices_to_file"):
            from price_extractor import extract_lowest_prices
            result = extract_lowest_prices(page)

        assert result == {
            "Economy Car": 299.99,
            "Full-size Car": 399.99,
            "Compact SUV": 449.00,
        }

    def test_skips_row_when_price_element_missing(self):
        """Rows where get_attribute raises are silently skipped."""
        good_row = _make_row_mock("Economy Car", "299.99")

        bad_row = MagicMock()
        bad_row.locator.side_effect = Exception("element not found")

        page = _make_page_mock([bad_row, good_row])

        with patch("price_extractor.save_prices_to_file"):
            from price_extractor import extract_lowest_prices
            result = extract_lowest_prices(page)

        assert result == {"Economy Car": 299.99}

    def test_returns_empty_dict_when_no_rows(self):
        """Returns empty dict when no rows found on page."""
        page = _make_page_mock([])

        with patch("price_extractor.save_prices_to_file"):
            from price_extractor import extract_lowest_prices
            result = extract_lowest_prices(page)

        assert result == {}

    def test_price_is_parsed_as_float(self):
        """Price from data-price attribute is converted to float."""
        row = _make_row_mock("Standard Car", "350")
        page = _make_page_mock([row])

        with patch("price_extractor.save_prices_to_file"):
            from price_extractor import extract_lowest_prices
            result = extract_lowest_prices(page)

        assert isinstance(result["Standard Car"], float)
        assert result["Standard Car"] == 350.0

    def test_calls_save_prices_to_file(self):
        """Extracted prices are passed to save_prices_to_file."""
        row = _make_row_mock("Economy Car", "299.99")
        page = _make_page_mock([row])

        with patch("price_extractor.save_prices_to_file") as mock_save:
            from price_extractor import extract_lowest_prices
            extract_lowest_prices(page)

        mock_save.assert_called_once_with({"Economy Car": 299.99})
