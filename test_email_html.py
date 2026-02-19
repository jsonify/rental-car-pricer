"""
Tests for format_booking_card() in email_module/templates/html_template.py
Covers: status banner, price hero, history table removal, all-time low, better deals.
"""

import sys
import types
import unittest
import re

_supabase_stub = types.ModuleType("supabase")
_supabase_stub.create_client = lambda *a, **kw: None
_supabase_stub.Client = object
sys.modules.setdefault("supabase", _supabase_stub)

_sc_stub = types.ModuleType("supabase_client")
_sc_stub.get_supabase_client = lambda: None
sys.modules.setdefault("supabase_client", _sc_stub)

from email_module.templates.html_template import (
    format_booking_card,
    format_price_history_table,
)


def _make_booking_data(
    current_price: float = 200.00,
    holding_price=None,
    previous_price=None,
    all_time_low=None,
    cheaper_category_price=None,
):
    """Build a minimal bookings_data item for testing."""
    focus = "Economy Car"
    prices = {focus: current_price}
    if cheaper_category_price is not None:
        prices["Compact Car"] = cheaper_category_price

    price_history = []
    if previous_price is not None:
        price_history.append(
            {"timestamp": "2026-01-01T10:00:00", "prices": {focus: previous_price}}
        )
    # Current record is always the last entry
    price_history.append(
        {"timestamp": "2026-02-18T10:00:00", "prices": {focus: current_price}}
    )

    trends = {}
    if all_time_low is not None:
        trends = {"focus_category": {"lowest": all_time_low}}

    booking = {
        "location": "SEA",
        "location_full_name": "Seattle-Tacoma International Airport",
        "pickup_date": "2026-03-01",
        "dropoff_date": "2026-03-08",
        "pickup_time": "10:00 AM",
        "dropoff_time": "10:00 AM",
        "focus_category": focus,
        "price_history": price_history,
    }
    if holding_price is not None:
        booking["holding_price"] = holding_price

    return {
        "booking": booking,
        "prices": prices,
        "trends": trends,
        "has_significant_drop": False,
    }


class TestStatusBanner(unittest.TestCase):
    """Tests for the status banner (first element in card content)."""

    def test_green_banner_when_current_below_holding(self):
        """When current < holding, banner should use green styling."""
        data = _make_booking_data(current_price=180.00, holding_price=200.00)
        html = format_booking_card(data)
        # Green banner: must contain the rebook text
        self.assertIn("Rebook opportunity", html)
        # Green colour indicator
        self.assertTrue(
            "#16a34a" in html or "#22c55e" in html or "green" in html.lower(),
            "Expected a green colour in the status banner HTML",
        )

    def test_amber_banner_when_current_above_holding(self):
        """When current > holding, banner should use amber/warning styling."""
        data = _make_booking_data(current_price=250.00, holding_price=200.00)
        html = format_booking_card(data)
        self.assertIn("Waiting", html)
        # Amber colour indicator
        self.assertTrue(
            "#d97706" in html
            or "#f59e0b" in html
            or "amber" in html.lower()
            or "orange" in html.lower()
            or "#92400e" in html,
            "Expected an amber/warning colour in the status banner HTML",
        )

    def test_neutral_banner_when_no_holding_price(self):
        """When holding_price is None, show a neutral informational banner."""
        data = _make_booking_data(current_price=200.00, holding_price=None)
        html = format_booking_card(data)
        self.assertIn("No holding price set", html)


class TestPriceHistoryTableRemoved(unittest.TestCase):
    """The price history table should NOT appear in the card output."""

    def test_history_table_not_rendered_in_card(self):
        """format_booking_card should NOT include the price history table."""
        data = _make_booking_data(
            current_price=200.00,
            previous_price=210.00,
        )
        html = format_booking_card(data)
        # The table function uses a distinctive marker class/id or date patterns
        # We check that date-like timestamps from history are absent in a table context
        self.assertNotIn("price_history_table", html)
        # Check that the history timestamps are not rendered as table rows
        self.assertNotIn("2026-01-01T10:00:00", html)

    def test_format_price_history_table_function_still_exists(self):
        """The format_price_history_table function must still exist (not deleted)."""
        # If this import works, the function exists
        from email_module.templates.html_template import format_price_history_table  # noqa: F401

        self.assertTrue(callable(format_price_history_table))


class TestAllTimeLow(unittest.TestCase):
    """Tests for the all-time low display in the price hero."""

    def test_all_time_low_line_present(self):
        """The all-time low value should appear in the card output."""
        data = _make_booking_data(current_price=200.00, all_time_low=150.00)
        html = format_booking_card(data)
        self.assertIn("150.00", html)
        # Should have a label
        self.assertTrue(
            "all-time low" in html.lower() or "All-time low" in html,
            "Expected 'All-time low' label in card HTML",
        )

    def test_all_time_low_highlighted_when_current_equals_low(self):
        """When current price == all-time low, the display should be highlighted."""
        data = _make_booking_data(current_price=150.00, all_time_low=150.00)
        html = format_booking_card(data)
        # Highlighted style: gold/amber background
        self.assertTrue(
            "#fbbf24" in html
            or "#f59e0b" in html
            or "#fef3c7" in html
            or "gold" in html.lower()
            or "#d97706" in html,
            "Expected a gold/amber highlight when current price equals all-time low",
        )


class TestBetterDealsPreserved(unittest.TestCase):
    """The better deals section must still appear when cheaper alternatives exist."""

    def test_better_deals_section_present_when_cheaper_categories_exist(self):
        """When cheaper categories exist, the better deals section should appear."""
        data = _make_booking_data(
            current_price=200.00,
            cheaper_category_price=150.00,
        )
        html = format_booking_card(data)
        self.assertIn("Better Deals", html)
        self.assertIn("150.00", html)


if __name__ == "__main__":
    unittest.main()
