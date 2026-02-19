import sys
import types
import unittest

# ---------------------------------------------------------------------------
# Stub out heavy/unavailable dependencies before importing email_module.sender
# ---------------------------------------------------------------------------

# Stub 'supabase' package so supabase_client.py can be imported without the
# real supabase library being installed in this Python environment.
_supabase_stub = types.ModuleType('supabase')
_supabase_stub.create_client = lambda *a, **kw: None
_supabase_stub.Client = object
sys.modules.setdefault('supabase', _supabase_stub)

# Stub 'supabase_client' module (used directly by sender.py).
_sc_stub = types.ModuleType('supabase_client')
_sc_stub.get_supabase_client = lambda: None
sys.modules.setdefault('supabase_client', _sc_stub)

# Stub template modules imported by sender.py.
for _mod in (
    'email_module.templates',
    'email_module.templates.html_template',
    'email_module.templates.formatters',
):
    sys.modules.setdefault(_mod, types.ModuleType(_mod))

sys.modules['email_module.templates.html_template'].format_email_body_html = lambda *a, **kw: ''
sys.modules['email_module.templates.formatters'].format_email_body_text = lambda *a, **kw: ''

# Now import the function under test.
from email_module.sender import format_subject  # noqa: E402


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_booking_data(location, pickup_date, dropoff_date, focus_category,
                      current_price, holding_price):
    """Build a bookings_data entry in the shape expected by format_subject."""
    return {
        'booking': {
            'location': location,
            'pickup_date': pickup_date,
            'dropoff_date': dropoff_date,
            'focus_category': focus_category,
            'holding_price': holding_price,
        },
        'prices': {
            focus_category: current_price,
        },
        'trends': {
            'focus_category': focus_category,
            'lowest': current_price,
            'previous_price': current_price,
        },
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFormatSubject(unittest.TestCase):

    def test_price_below_holding_uses_checkmark_segment(self):
        """Price below holding price produces a checkmark segment."""
        data = [make_booking_data('SEA', '03/10/2026', '03/17/2026', 'Economy Car', 199.00, 215.00)]
        result = format_subject(data)
        self.assertEqual(result, '✅ SEA $199.00 (under holding)')

    def test_price_above_holding_uses_warning_segment_with_delta(self):
        """Price above holding price produces a warning segment with delta."""
        data = [make_booking_data('LAX', '04/05/2026', '04/12/2026', 'Economy Car', 310.00, 290.00)]
        result = format_subject(data)
        self.assertEqual(result, '⚠️ LAX $310.00 (over holding +$20.00)')

    def test_no_holding_price_uses_chart_segment(self):
        """No holding price (None) produces a chart segment."""
        data = [make_booking_data('ORD', '05/01/2026', '05/08/2026', 'Economy Car', 250.00, None)]
        result = format_subject(data)
        self.assertEqual(result, '📊 ORD $250.00')

    def test_multiple_bookings_pipe_separated_ordered_by_pickup_date(self):
        """Multiple bookings are pipe-separated and ordered chronologically by pickup_date."""
        data = [
            # LAX picks up later — April
            make_booking_data('LAX', '04/05/2026', '04/12/2026', 'Economy Car', 310.00, 290.00),
            # SEA picks up earlier — March
            make_booking_data('SEA', '03/10/2026', '03/17/2026', 'Economy Car', 199.00, 215.00),
        ]
        result = format_subject(data)
        self.assertEqual(
            result,
            '✅ SEA $199.00 (under holding) | ⚠️ LAX $310.00 (over holding +$20.00)',
        )

    def test_price_equal_to_holding_uses_checkmark_segment(self):
        """Price exactly equal to holding counts as under (<=) and produces a checkmark segment."""
        data = [make_booking_data('SFO', '06/15/2026', '06/22/2026', 'Economy Car', 215.00, 215.00)]
        result = format_subject(data)
        self.assertEqual(result, '✅ SFO $215.00 (under holding)')


if __name__ == '__main__':
    unittest.main()
