# email_module/templates/formatters.py
from typing import Dict, List, Optional
from datetime import datetime


def format_price_change_text(
    current_price: float,
    previous_price: Optional[float] = None,
    holding_price: Optional[float] = None,
) -> str:
    """Format price change for plain text emails"""
    try:
        parts = [f"${current_price:.2f}"]

        if previous_price is not None:
            change = current_price - previous_price
            pct_change = (change / previous_price) * 100

            if change > 0:
                parts.append(f"↑ +${change:.2f} (+{pct_change:.1f}%)")
            elif change < 0:
                parts.append(f"↓ -${abs(change):.2f} ({pct_change:.1f}%)")
            else:
                parts.append("= No change")

        if holding_price is not None:
            holding_diff = current_price - holding_price
            if holding_diff != 0:
                parts.append(
                    f"[${abs(holding_diff):.2f} {'above' if holding_diff > 0 else 'below'} holding]"
                )

        return " ".join(parts)
    except Exception as e:
        return f"${current_price:.2f}"


def format_price_change_html(
    current_price: float,
    previous_price: Optional[float] = None,
    holding_price: Optional[float] = None,
) -> str:
    """Format price change for HTML emails"""
    try:
        parts = [f'<span class="price">${current_price:.2f}</span>']

        if previous_price is not None:
            change = current_price - previous_price
            pct_change = (change / previous_price) * 100

            if change > 0:
                parts.append(
                    f'<span class="change increase">+${change:.2f} (+{pct_change:.1f}%)</span>'
                )
            elif change < 0:
                parts.append(
                    f'<span class="change decrease">-${abs(change):.2f} ({pct_change:.1f}%)</span>'
                )

        return " ".join(parts)
    except Exception as e:
        return f"${current_price:.2f}"


def format_email_body_text(bookings_data: List[Dict]) -> str:
    """Format email body for plain text version"""
    lines = []

    # Header
    lines.append("Costco Travel Car Rental Update")
    lines.append("=" * 50)
    lines.append(f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        f"Tracking {len(bookings_data)} booking{'s' if len(bookings_data) != 1 else ''}"
    )
    lines.append("=" * 50)

    # Process each booking
    for booking_data in bookings_data:
        booking = booking_data["booking"]
        prices = booking_data["prices"]
        trends = booking_data.get("trends", {})

        focus_category = booking["focus_category"]
        focus_price = prices.get(focus_category)
        focus_trends = trends.get("focus_category", {})
        holding_price = booking.get("holding_price")
        all_time_low = focus_trends.get("lowest")

        # Location header
        lines.append(
            f"\n📍 {booking['location']} - {booking.get('location_full_name', 'Airport')}"
        )
        lines.append(f"📅 {booking['pickup_date']} to {booking['dropoff_date']}")
        lines.append(f"⏰ {booking['pickup_time']} - {booking['dropoff_time']}")

        # Status line at start of booking section
        if focus_price is not None and holding_price is not None:
            diff = holding_price - focus_price
            if focus_price < holding_price:
                lines.append(f"✅ REBOOK NOW — ${diff:.2f} below holding")
            else:
                lines.append(f"⚠️ WAITING — ${abs(diff):.2f} above holding")
        else:
            lines.append("📊 Tracking")

        lines.append("-" * 50)

        # Focus category
        if focus_category in prices:
            lines.append(f"\n🎯 TRACKED: {focus_category}")
            price_text = format_price_change_text(
                focus_price, focus_trends.get("previous_price"), holding_price
            )
            lines.append(f"Current Price: {price_text}")

            # All-time low
            if all_time_low is not None:
                if focus_price is not None and focus_price == all_time_low:
                    lines.append(
                        f"All-time low: ${all_time_low:.2f} ← CURRENT (lowest ever seen!)"
                    )
                else:
                    lines.append(f"All-time low: ${all_time_low:.2f}")

            # Historical data
            if "highest" in focus_trends:
                lines.append(
                    f"Historical Range: ${focus_trends['lowest']:.2f} - ${focus_trends['highest']:.2f}"
                )
            if "average" in focus_trends:
                lines.append(f"Average Price: ${focus_trends['average']:.2f}")

        # Better deals
        better_options = []
        if focus_category in prices:
            focus_price = prices[focus_category]
            for category, price in prices.items():
                if price < focus_price and category != focus_category:
                    savings = focus_price - price
                    better_options.append(
                        f"- {category}: ${price:.2f} (Save ${savings:.2f})"
                    )

        if better_options:
            lines.append("\n💰 BETTER DEALS AVAILABLE:")
            lines.extend(better_options)

        # All categories
        lines.append("\n📊 ALL CATEGORIES:")
        for category, price in sorted(prices.items(), key=lambda x: x[1]):
            prefix = "➡️ " if category == focus_category else "  "
            price_text = format_price_change_text(
                price,
                None,
                booking.get("holding_price") if category == focus_category else None,
            )
            lines.append(f"{prefix}{category}: {price_text}")

        lines.append("=" * 50)

    # Footer
    lines.append("\n📝 Notes:")
    lines.append("- Prices include taxes and fees")
    lines.append("- Historical trends shown when available")

    return "\n".join(lines)
