# email_module/templates/html_template.py
from typing import Dict, List, Optional
import json
import traceback
from datetime import datetime
from ..styles.css_styles import EMAIL_CSS
from .formatters import format_price_change_html

# ── Color palette (blue-tinted dark, inline for email client compat) ───────────
BODY_BG      = "#141521"
CARD_BG      = "#1c1d2e"
CARD_BORDER  = "#2a2b3d"
DIVIDER      = "#232438"
TEXT_PRIMARY = "#e8e8ed"
TEXT_SEC     = "#8b8ca0"
TEXT_MUTED   = "#6b6c80"
COLOR_GREEN  = "#34d399"
COLOR_AMBER  = "#fbbf24"
COLOR_RED    = "#f87171"
DEAL_BG      = "#172324"
DEAL_BORDER  = "#1f3635"
PILL_BG      = "#0d2d22"
PILL_BORDER  = "#1a4d3a"
FOCUS_ROW_BG = "#162e24"
ROW_A        = "#1c1d2e"
ROW_B        = "#191a2b"
FONT         = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO         = "'JetBrains Mono', 'Courier New', monospace"


# ── Utility ────────────────────────────────────────────────────────────────────

def calculate_better_deals(prices: Dict[str, float], focus_category: str) -> List[Dict]:
    """Return categories cheaper than focus_category, sorted by savings desc."""
    better_deals = []
    if focus_category in prices:
        focus_price = prices[focus_category]
        for category, price in prices.items():
            if price < focus_price and category != focus_category:
                savings = focus_price - price
                savings_pct = (savings / focus_price) * 100
                better_deals.append(
                    {
                        "category": category,
                        "price": price,
                        "savings": savings,
                        "savings_pct": savings_pct,
                    }
                )
    return sorted(better_deals, key=lambda x: x["savings"], reverse=True)


# ── Summary stats ──────────────────────────────────────────────────────────────

def _calculate_summary_stats(bookings_data: List[Dict]) -> Dict:
    """Compute best/avg/worst across all bookings."""
    all_prices = []
    focus_prices = []

    for bd in bookings_data:
        booking = bd["booking"]
        prices = bd.get("prices", {})
        focus_category = booking.get("focus_category", "")

        for cat, price in prices.items():
            all_prices.append((price, cat, booking.get("location", "")))

        if focus_category in prices:
            focus_prices.append(prices[focus_category])

    if not all_prices:
        return {}

    best  = min(all_prices, key=lambda x: x[0])
    worst = max(all_prices, key=lambda x: x[0])
    market_avg = sum(focus_prices) / len(focus_prices) if focus_prices else 0

    return {
        "best_price":    best[0],
        "best_category": best[1],
        "market_avg":    market_avg,
        "max_price":     worst[0],
        "max_category":  worst[1],
    }


# ── Header (centered/stacked) ──────────────────────────────────────────────────

def _format_header(bookings_data: List[Dict]) -> str:
    n   = len(bookings_data)
    now = datetime.now().strftime("%b %d, %Y at %-I:%M %p")
    return f"""
        <tr>
          <td style="padding: 0 0 24px 0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background-color:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:12px; overflow:hidden;">
              <tr>
                <td style="padding:24px 24px 20px 24px; text-align:center;">
                  <div style="font-size:22px; font-weight:800; color:{TEXT_PRIMARY}; letter-spacing:-0.5px; margin-bottom:4px; font-family:{FONT};">
                    &#128663; Costco Travel Car Rental Update
                  </div>
                  <div style="font-size:12px; color:{TEXT_SEC}; font-family:{FONT};">
                    Last checked: {now}
                  </div>
                  <div style="margin-top:8px;">
                    <span style="display:inline-block; background-color:#0d2d22; border:1px solid #1a4d3a; border-radius:20px; padding:4px 14px; font-size:11px; font-weight:600; color:{COLOR_GREEN}; letter-spacing:0.3px; font-family:{FONT};">
                      &#128737; Tracking {n} booking{"s" if n != 1 else ""}
                    </span>
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
    """


# ── Summary bar ────────────────────────────────────────────────────────────────

def _dot(color: str) -> str:
    return f'<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background-color:{color}; margin-right:6px; vertical-align:middle;"></span>'


def _format_summary_bar(stats: Dict) -> str:
    if not stats:
        return ""
    return f"""
        <tr>
          <td style="padding: 0 0 20px 0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background-color:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:12px; overflow:hidden;">
              <tr>
                <td style="padding:14px 24px;">
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td style="font-size:12px; color:{TEXT_SEC}; vertical-align:middle; font-family:{FONT};">
                        {_dot(COLOR_GREEN)}Best:
                        <strong style="color:{COLOR_GREEN}; font-family:{MONO};">&nbsp;${stats['best_price']:.2f}</strong>
                        <span style="color:{TEXT_MUTED};">&nbsp;({stats['best_category']})</span>
                      </td>
                      <td style="font-size:12px; color:{TEXT_SEC}; text-align:center; vertical-align:middle; font-family:{FONT};">
                        {_dot(COLOR_AMBER)}Avg:
                        <strong style="color:{TEXT_PRIMARY}; font-family:{MONO};">&nbsp;${stats['market_avg']:.0f}</strong>
                      </td>
                      <td style="font-size:12px; color:{TEXT_SEC}; text-align:right; vertical-align:middle; font-family:{FONT};">
                        {_dot(COLOR_RED)}High:
                        <strong style="color:{TEXT_SEC}; font-family:{MONO};">&nbsp;${stats['max_price']:.0f}</strong>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
    """


# ── Status badge ───────────────────────────────────────────────────────────────

def _get_status_badge(current_price: float, holding_price: Optional[float]) -> str:
    if holding_price is None:
        return (
            f'<table cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="background-color:#27272a; border-radius:20px; padding:4px 12px; '
            f'font-size:11px; font-weight:600; color:{TEXT_MUTED}; font-family:{FONT};">No Hold</td>'
            f'</tr></table>'
        )
    if current_price <= holding_price:
        return (
            f'<table cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="background-color:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.2); '
            f'border-radius:20px; padding:4px 12px; font-size:11px; font-weight:600; color:{COLOR_GREEN}; '
            f'text-transform:uppercase; letter-spacing:0.5px; font-family:{FONT};">Under Hold</td>'
            f'</tr></table>'
        )
    return (
        f'<table cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="background-color:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.2); '
        f'border-radius:20px; padding:4px 12px; font-size:11px; font-weight:600; color:{COLOR_AMBER}; '
        f'text-transform:uppercase; letter-spacing:0.5px; font-family:{FONT};">Above Hold</td>'
        f'</tr></table>'
    )


# ── Card header ────────────────────────────────────────────────────────────────

def _format_card_header(booking: Dict, status_badge: str) -> str:
    location  = booking.get("location", "")
    full_name = booking.get("location_full_name", "Airport")
    pickup    = booking.get("pickup_date", "")
    dropoff   = booking.get("dropoff_date", "")
    p_time    = booking.get("pickup_time", "")
    d_time    = booking.get("dropoff_time", "")

    return f"""
      <tr>
        <td style="padding:16px 20px; border-bottom:1px solid {DIVIDER};">
          <table cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
              <td style="vertical-align:middle;">
                <div style="font-size:15px; font-weight:700; color:{TEXT_PRIMARY}; margin-bottom:4px; font-family:{FONT};">
                  &#128205; {location} - {full_name}
                </div>
                <div style="font-size:12px; color:{TEXT_SEC}; font-family:{FONT};">
                  &#128197; {pickup} - {dropoff} &nbsp;&nbsp; &#128336; {p_time} - {d_time}
                </div>
              </td>
              <td style="padding:0; vertical-align:middle; text-align:right;">
                {status_badge}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    """


# ── Price hero ─────────────────────────────────────────────────────────────────

def _format_price_hero(
    current_price: float,
    focus_category: str,
    previous_price: Optional[float],
    holding_price: Optional[float],
) -> str:
    # Price change line
    if previous_price is None or previous_price == current_price:
        change_html = f'<span style="color:{TEXT_SEC}; font-size:13px; font-family:{FONT};">&#8594; No change</span>'
    else:
        diff = current_price - previous_price
        pct  = abs(diff / previous_price * 100)
        if diff < 0:
            change_html = f'<span style="color:{COLOR_GREEN}; font-size:13px; font-family:{FONT};">&#8595; -${abs(diff):.2f} (-{pct:.1f}%)</span>'
        else:
            change_html = f'<span style="color:{COLOR_RED}; font-size:13px; font-family:{FONT};">&#9650; +${diff:.2f} (+{pct:.1f}%)</span>'

    left_col = f"""
      <td style="vertical-align:top; width:55%;">
        <div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:{TEXT_MUTED}; margin-bottom:4px; font-family:{FONT};">{focus_category}</div>
        <div style="font-size:36px; font-weight:800; color:{TEXT_PRIMARY}; font-family:{MONO}; line-height:1.1;">${current_price:.2f}</div>
        <div style="margin-top:6px;">{change_html}</div>
      </td>
    """

    if holding_price is not None:
        hold_diff = current_price - holding_price
        if hold_diff > 0:
            hold_delta = f'<span style="color:{COLOR_AMBER};">${hold_diff:.2f} above</span>'
        else:
            hold_delta = f'<span style="color:{COLOR_GREEN};">${abs(hold_diff):.2f} below</span>'

        right_col = f"""
          <td style="vertical-align:top; text-align:right;">
            <div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:{TEXT_MUTED}; margin-bottom:4px; font-family:{FONT};">Your Hold</div>
            <div style="font-size:26px; font-weight:800; color:{TEXT_PRIMARY}; font-family:{MONO}; line-height:1.1;">${holding_price:.2f}</div>
            <div style="margin-top:6px; font-size:12px; font-family:{FONT};">{hold_delta}</div>
          </td>
        """
    else:
        right_col = ""

    return f"""
      <tr>
        <td style="padding:20px;">
          <table cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
              {left_col}
              {right_col}
            </tr>
          </table>
    """
    # NOTE: range bar is appended inside the same <td> padding block, closed below


def _close_price_section() -> str:
    return """
        </td>
      </tr>
    """


# ── Range bar (table-based fill — no absolute positioning) ────────────────────

def _format_range_bar(
    current_price: float,
    all_time_low: Optional[float],
    all_time_high: Optional[float],
    holding_price: Optional[float],
) -> str:
    gradient = f"linear-gradient(to right, {COLOR_GREEN}, {COLOR_AMBER}, {COLOR_RED})"

    # Right-side label: holding price if available, else generic
    if holding_price is not None:
        right_label = f"Your hold: ${holding_price:.2f}"
    else:
        right_label = "All-time high"

    if all_time_low is None or all_time_high is None or all_time_high <= all_time_low:
        left_label = "Range data unavailable"
        fill_pct   = "50%"
    else:
        pct        = (current_price - all_time_low) / (all_time_high - all_time_low) * 100
        fill_pct   = f"{max(2.0, min(98.0, pct)):.2f}%"
        left_label = f"All-time low: ${all_time_low:.2f}"

    return f"""
          <!-- Range bar -->
          <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:16px;">
            <tr>
              <td style="padding:0;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%"
                       style="border-radius:6px; overflow:hidden;">
                  <tr>
                    <td style="background-color:{DIVIDER}; height:8px; border-radius:6px; padding:0;">
                      <table cellpadding="0" cellspacing="0" border="0" width="{fill_pct}"
                             style="border-radius:6px;">
                        <tr>
                          <td style="background:{gradient}; height:8px; border-radius:6px; padding:0;"></td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding-top:6px;">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr>
                    <td style="font-size:10px; color:{COLOR_GREEN}; text-transform:uppercase; letter-spacing:1px; font-weight:600; font-family:{FONT};">{left_label}</td>
                    <td style="font-size:10px; color:{TEXT_SEC}; text-transform:uppercase; letter-spacing:1px; text-align:right; font-family:{FONT};">{right_label}</td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
    """


# ── Better deals ───────────────────────────────────────────────────────────────

def _format_better_deals_dark(
    better_deals: List[Dict],
    holding_price: Optional[float],
    focus_price: float,
) -> str:
    if not better_deals:
        return ""

    top_deals        = better_deals[:5]
    below_hold_count = sum(1 for d in better_deals if holding_price and d["price"] <= holding_price) if holding_price else 0
    extra            = max(0, below_hold_count - 5)

    rows = []
    for i, deal in enumerate(top_deals):
        pad_top = "0" if i == 0 else "6px 0 0 0"
        rows.append(f"""
            <tr>
              <td style="padding:{pad_top};">
                <table cellpadding="0" cellspacing="0" border="0" width="100%"
                       style="background-color:{DEAL_BG}; border:1px solid {DEAL_BORDER}; border-radius:8px;">
                  <tr>
                    <td style="padding:10px 12px;">
                      <table cellpadding="0" cellspacing="0" border="0" width="100%">
                        <tr>
                          <td style="font-size:13px; font-weight:500; color:{TEXT_PRIMARY}; font-family:{FONT};">{deal["category"]}</td>
                          <td style="text-align:right; white-space:nowrap;">
                            <span style="font-size:13px; font-weight:700; color:{TEXT_PRIMARY}; font-family:{MONO};">${deal["price"]:.2f}</span>
                            <span style="display:inline-block; background-color:{PILL_BG}; border:1px solid {PILL_BORDER}; border-radius:12px; padding:2px 8px; font-size:10px; font-weight:600; color:{COLOR_GREEN}; margin-left:8px; font-family:{FONT};">-${deal["savings"]:.2f} ({deal["savings_pct"]:.1f}%)</span>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
        """)

    extra_html = ""
    if extra > 0:
        extra_html = f'<tr><td style="padding-top:8px; text-align:center; font-size:12px; color:{TEXT_MUTED}; font-family:{FONT};">+{extra} more deals below your holding price</td></tr>'

    return f"""
      <tr>
        <td style="padding:16px 20px 16px 20px; border-top:1px solid {DIVIDER};">
          <table cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
              <td style="padding-bottom:12px;">
                <span style="color:{COLOR_GREEN}; font-size:14px; font-weight:700; font-family:{FONT};">&#9889; {len(better_deals)} Better Deal{"s" if len(better_deals) != 1 else ""} Available</span>
              </td>
            </tr>
            {"".join(rows)}
            {extra_html}
          </table>
        </td>
      </tr>
    """


# ── All categories ─────────────────────────────────────────────────────────────

def _format_all_categories_dark(
    prices: Dict[str, float],
    focus_category: str,
    holding_price: Optional[float],
) -> str:
    sorted_prices = sorted(prices.items(), key=lambda x: x[1])
    n = len(sorted_prices)

    rows = []
    for idx, (category, price) in enumerate(sorted_prices):
        is_focus  = category == focus_category
        row_color = ROW_A if idx % 2 == 0 else ROW_B

        if is_focus:
            label = f'<span style="display:inline-block; width:6px; height:6px; border-radius:50%; background-color:{COLOR_GREEN}; margin-right:4px;"></span>{category}{"  (your hold)" if holding_price else ""}'
            rows.append(f"""
              <tr>
                <td style="background-color:{FOCUS_ROW_BG}; border-left:3px solid {COLOR_GREEN}; padding:8px 12px; font-size:12px; font-weight:700; color:{TEXT_PRIMARY}; border-bottom:1px solid {DIVIDER}; font-family:{FONT};">
                  {label}
                </td>
                <td style="background-color:{FOCUS_ROW_BG}; padding:8px 12px; font-size:12px; font-weight:700; color:{COLOR_GREEN}; text-align:right; font-family:{MONO}; border-bottom:1px solid {DIVIDER};">
                  ${price:.2f}
                </td>
              </tr>
            """)
        else:
            rows.append(f"""
              <tr>
                <td style="background-color:{row_color}; padding:8px 12px; font-size:12px; font-weight:400; color:{TEXT_SEC}; border-bottom:1px solid {DIVIDER}; font-family:{FONT};">
                  {category}
                </td>
                <td style="background-color:{row_color}; padding:8px 12px; font-size:12px; font-weight:400; color:{TEXT_SEC}; text-align:right; font-family:{MONO}; border-bottom:1px solid {DIVIDER};">
                  ${price:.2f}
                </td>
              </tr>
            """)

    return f"""
      <tr>
        <td style="padding:16px 20px; border-top:1px solid {DIVIDER};">
          <table cellpadding="0" cellspacing="0" border="0" width="100%"
                 style="font-size:11px; color:{TEXT_MUTED}; text-transform:uppercase; letter-spacing:1px; font-weight:600; font-family:{FONT};">
            <tr>
              <td style="padding-bottom:8px;">All {n} Categories</td>
              <td style="padding-bottom:8px; text-align:right;">Price</td>
            </tr>
          </table>
          <table cellpadding="0" cellspacing="0" border="0" width="100%"
                 style="border-radius:8px; overflow:hidden; border:1px solid {DIVIDER};">
            {"".join(rows)}
          </table>
        </td>
      </tr>
    """


# ── Card assembly ──────────────────────────────────────────────────────────────

def format_booking_card(booking_data: Dict) -> str:
    """Assemble a single dark-themed booking card (full-width, stacked)."""
    try:
        booking  = booking_data["booking"]
        prices   = booking_data["prices"]
        trends   = booking_data.get("trends", {})

        focus_category = booking["focus_category"]
        holding_price  = booking.get("holding_price")
        current_price  = prices.get(focus_category, 0)

        focus_trends   = trends.get("focus_category", {})
        previous_price = focus_trends.get("previous_price")
        all_time_low   = focus_trends.get("lowest")
        all_time_high  = focus_trends.get("highest")

        better_deals = calculate_better_deals(prices, focus_category)
        status_badge = _get_status_badge(current_price, holding_price)

        card_header     = _format_card_header(booking, status_badge)
        price_hero      = _format_price_hero(current_price, focus_category, previous_price, holding_price)
        range_bar       = _format_range_bar(current_price, all_time_low, all_time_high, holding_price)
        close_section   = _close_price_section()
        better_deals_html = _format_better_deals_dark(better_deals, holding_price, current_price)
        all_categories  = _format_all_categories_dark(prices, focus_category, holding_price)

        inner = (
            f'<table cellpadding="0" cellspacing="0" border="0" width="100%"'
            f' style="background-color:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:12px; overflow:hidden; margin-bottom:20px;">'
            + card_header
            + price_hero
            + range_bar
            + close_section
            + better_deals_html
            + all_categories
            + '</table>'
        )

        return inner

    except Exception as e:
        print(f"Error formatting booking card: {str(e)}")
        traceback.print_exc()
        return f'<p style="color:{COLOR_RED}; font-family:{FONT};">Error formatting booking card: {str(e)}</p>'


# ── Footer ─────────────────────────────────────────────────────────────────────

def _format_footer() -> str:
    return f"""
        <tr>
          <td style="padding: 8px 0 0 0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%"
                   style="background-color:{CARD_BG}; border:1px solid {CARD_BORDER}; border-radius:12px; overflow:hidden;">
              <tr>
                <td style="padding:20px 24px; text-align:center;">
                  <a href="https://www.costcotravel.com/Rental-Cars" target="_blank"
                     style="display:inline-block; background-color:{COLOR_GREEN}; color:{BODY_BG}; font-size:13px; font-weight:700; text-decoration:none; padding:10px 24px; border-radius:8px; letter-spacing:0.3px; font-family:{FONT};">
                    View Current Prices at Costco Travel &#8594;
                  </a>
                  <div style="margin-top:14px; font-size:11px; color:{TEXT_MUTED}; font-family:{FONT};">
                    All prices include taxes and fees &middot; Historical trends shown when available
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
    """


# ── Email body ─────────────────────────────────────────────────────────────────

def format_email_body_html(bookings_data: List[Dict]) -> str:
    """Format the complete dark-themed email body (single-column, 640px)."""
    try:
        print(f"\nFormatting email HTML for {len(bookings_data)} bookings:")
        for bd in bookings_data:
            booking = bd["booking"]
            has_drop = bd.get("has_significant_drop", False)
            print(f"- {booking['location']}: {booking['pickup_date']} to {booking['dropoff_date']}")
            if has_drop:
                print("  * Has significant price drop!")

        stats         = _calculate_summary_stats(bookings_data)
        header_rows   = _format_header(bookings_data)
        summary_rows  = _format_summary_bar(stats)
        footer_rows   = _format_footer()

        cards_html = "\n".join(format_booking_card(bd) for bd in bookings_data)

        return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Costco Travel Car Rental Update</title>
  <style type="text/css">
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    body {{ margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: {BODY_BG} !important; }}
    img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }}
  </style>
</head>
<body style="margin: 0; padding: 0; background-color: {BODY_BG}; font-family: {FONT};">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%"
       style="background-color:{BODY_BG};">
  <tr>
    <td align="center" style="padding:24px 16px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640"
             style="max-width:640px; width:100%;">
        {header_rows}
        {summary_rows}
        <tr>
          <td>
            {cards_html}
          </td>
        </tr>
        {footer_rows}
      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
    except Exception as e:
        print(f"Error in format_email_body_html: {str(e)}")
        traceback.print_exc()
        return f'<div style="color:{COLOR_RED}; padding:20px; font-family:{FONT};">An error occurred while generating the email: {str(e)}</div>'
