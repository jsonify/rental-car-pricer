"""
Tests for format_email_body_text() in email_module/templates/formatters.py
Beads task: rental-car-pricer-126.3.1
"""

import sys
import types
import unittest

_supabase_stub = types.ModuleType("supabase")
_supabase_stub.create_client = lambda *a, **kw: None
_supabase_stub.Client = object
sys.modules.setdefault("supabase", _supabase_stub)

_sc_stub = types.ModuleType("supabase_client")
_sc_stub.get_supabase_client = lambda: None
sys.modules.setdefault("supabase_client", _sc_stub)

from email_module.templates.formatters import format_email_body_text


def make_booking_data(
    focus_price=250.00,
    holding_price=300.00,
    all_time_low=200.00,
    previous_price=260.00,
):
    """Helper to create a minimal bookings_data entry."""
    focus_category = "Economy Car"
    prices = {
        focus_category: focus_price,
        "Compact Car": focus_price + 20,
        "Full-size Car": focus_price + 50,
    }
    trends = {
        "focus_category": {
            "lowest": all_time_low,
            "highest": 400.00,
            "average": 280.00,
            "previous_price": previous_price,
        }
    }
    booking = {
        "location": "LAX",
        "location_full_name": "Los Angeles International Airport",
        "pickup_date": "2026-03-01",
        "dropoff_date": "2026-03-08",
        "pickup_time": "10:00 AM",
        "dropoff_time": "10:00 AM",
        "focus_category": focus_category,
        "holding_price": holding_price,
    }
    return {
        "booking": booking,
        "prices": prices,
        "trends": trends,
    }


class TestFormatEmailBodyText(unittest.TestCase):
    def test_status_line_rebook_when_price_below_holding(self):
        """Status line shows REBOOK NOW when current price is below holding price."""
        # price=250, holding=300 → price < holding → REBOOK NOW
        data = make_booking_data(focus_price=250.00, holding_price=300.00)
        output = format_email_body_text([data])
        self.assertIn(
            "REBOOK NOW",
            output,
            "Expected 'REBOOK NOW' status when price is below holding price",
        )
        self.assertIn(
            "✅", output, "Expected green checkmark emoji for REBOOK NOW status"
        )

    def test_status_line_waiting_when_price_above_holding(self):
        """Status line shows WAITING when current price is above holding price."""
        # price=350, holding=300 → price > holding → WAITING
        data = make_booking_data(focus_price=350.00, holding_price=300.00)
        output = format_email_body_text([data])
        self.assertIn(
            "WAITING",
            output,
            "Expected 'WAITING' status when price is above holding price",
        )
        self.assertIn("⚠️", output, "Expected warning emoji for WAITING status")

    def test_status_line_tracking_when_no_holding_price(self):
        """Status line shows Tracking when holding_price is None."""
        data = make_booking_data(focus_price=250.00, holding_price=None)
        # Override to remove holding_price key entirely from booking
        data["booking"]["holding_price"] = None
        output = format_email_body_text([data])
        self.assertIn(
            "Tracking",
            output,
            "Expected 'Tracking' status when no holding price is set",
        )
        self.assertIn("📊", output, "Expected chart emoji for Tracking status")

    def test_all_time_low_line_present(self):
        """All-time low line appears in output."""
        data = make_booking_data(focus_price=250.00, all_time_low=200.00)
        output = format_email_body_text([data])
        self.assertIn("All-time low", output, "Expected 'All-time low' line in output")
        self.assertIn("$200.00", output, "Expected all-time low value in output")

    def test_current_annotation_when_price_equals_all_time_low(self):
        """'← CURRENT' annotation present when current price equals all-time low."""
        # price=200, all_time_low=200 → should show ← CURRENT
        data = make_booking_data(
            focus_price=200.00, all_time_low=200.00, holding_price=300.00
        )
        output = format_email_body_text([data])
        self.assertIn(
            "← CURRENT",
            output,
            "Expected '← CURRENT' annotation when current price equals all-time low",
        )
        self.assertIn(
            "lowest ever seen",
            output,
            "Expected 'lowest ever seen' annotation when current == all-time low",
        )

    def test_output_is_clean_plain_text_no_html_tags(self):
        """Output contains no HTML tags."""
        data = make_booking_data()
        output = format_email_body_text([data])
        # Check for common HTML tag patterns
        import re

        html_tags = re.findall(r"<[a-zA-Z/][^>]*>", output)
        self.assertEqual(
            html_tags,
            [],
            f"Expected no HTML tags in plain text output, found: {html_tags}",
        )


if __name__ == "__main__":
    unittest.main()
