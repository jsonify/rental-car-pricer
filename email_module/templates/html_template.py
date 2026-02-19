# email_module/templates/html_template.py
from typing import Dict, List, Optional
import json
import traceback
from datetime import datetime
from ..styles.css_styles import EMAIL_CSS
from .formatters import format_price_change_html


def calculate_better_deals(prices: Dict[str, float], focus_category: str) -> List[Dict]:
    """Calculate better deals compared to focus category"""
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


def format_better_deals_section(better_deals: List[Dict]) -> str:
    """Format the better deals section of the email"""
    if not better_deals:
        return ""

    deals_html = []
    for deal in better_deals:
        deals_html.append(f"""
            <div style="background: white; padding: 8px; margin: 4px 0; border-radius: 4px;">
                {deal["category"]}: ${deal["price"]:.2f}
                <span style="color: #059669">
                    (Save ${deal["savings"]:.2f}, {deal["savings_pct"]:.1f}%)
                </span>
            </div>
        """)

    return f"""
        <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bae6fd;">
            <div style="font-weight: bold; color: #0369a1; margin-bottom: 10px;">
                💰 Better Deals Available
            </div>
            {"".join(deals_html)}
        </div>
    """


def format_price_history_table(price_history: List[Dict], focus_category: str) -> str:
    """Format price history table for a booking"""
    if not price_history:
        return ""

    history_rows = []
    # Sort history by timestamp in descending order (newest first)
    sorted_history = sorted(price_history, key=lambda x: x["timestamp"], reverse=True)

    for record in sorted_history:
        timestamp = record.get("timestamp", "")
        record_prices = record.get("prices", {})
        if focus_category in record_prices:
            category_price = record_prices[focus_category]
            history_rows.append(f"""
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px; text-align: left;">{timestamp}</td>
                    <td style="padding: 8px; text-align: right;">${category_price:.2f}</td>
                </tr>
            """)

    if history_rows:  # Only show if we have history data
        return f"""
            <div style="margin: 15px 0; background: #f8fafc; border-radius: 8px; padding: 15px;">
                <div style="font-weight: bold; margin-bottom: 8px;">📋 Price History for {focus_category}</div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem;">
                        <thead>
                            <tr style="border-bottom: 2px solid #e2e8f0; font-weight: bold;">
                                <th style="padding: 8px; text-align: left;">Date</th>
                                <th style="padding: 8px; text-align: right;">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(history_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        """
    return ""


def create_price_rows(prices: Dict[str, float], focus_category: str) -> str:
    """Create HTML rows for all price categories with enhanced focus highlighting"""
    rows = []
    for category, price in sorted(prices.items(), key=lambda x: x[1]):
        is_focus = category == focus_category
        row_style = """
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            border-bottom: 1px solid #e2e8f0;
            {}
        """.format("background: #e0f2fe;" if is_focus else "")

        rows.append(f"""
            <div style="{row_style}">
                <span>
                    {is_focus and "🎯 " or ""}{category}
                </span>
                <span>${price:.2f}</span>
            </div>
        """)
    return "".join(rows)


def _format_status_banner(current_price: float, holding_price: Optional[float]) -> str:
    """Format the status banner based on holding price comparison."""
    if holding_price is None:
        return f"""
            <div style="background: #f3f4f6; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #6b7280;">
                <span style="color: #6b7280; font-weight: 600;">📊 No holding price set — currently ${current_price:.2f}</span>
            </div>
        """

    delta = abs(current_price - holding_price)

    if current_price <= holding_price:
        return f"""
            <div style="background: #dcfce7; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #16a34a;">
                <span style="color: #16a34a; font-weight: 600;">✅ Rebook opportunity — ${current_price:.2f} is ${delta:.2f} below your holding price</span>
            </div>
        """
    else:
        return f"""
            <div style="background: #fef3c7; padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #d97706;">
                <span style="color: #92400e; font-weight: 600;">⚠️ Waiting — ${delta:.2f} above your holding price</span>
            </div>
        """


def _format_price_change_display(
    current_price: float, previous_price: Optional[float]
) -> str:
    """Format the price change since last check."""
    if previous_price is None:
        return '<div style="font-size: 0.875rem; color: #6b7280; margin-top: 8px;">→ No change</div>'

    price_change = current_price - previous_price

    if price_change == 0:
        return '<div style="font-size: 0.875rem; color: #6b7280; margin-top: 8px;">→ No change</div>'

    pct_change = abs((price_change / previous_price) * 100)

    if price_change < 0:
        return f'<div style="font-size: 0.875rem; color: #16a34a; margin-top: 8px;">↓ ${abs(price_change):.2f} (-{pct_change:.1f}%)</div>'
    else:
        return f'<div style="font-size: 0.875rem; color: #dc2626; margin-top: 8px;">↑ ${price_change:.2f} (+{pct_change:.1f}%)</div>'


def _format_all_time_low(current_price: float, all_time_low: Optional[float]) -> str:
    """Format the all-time low display with optional highlighting."""
    if all_time_low is None:
        return ""

    is_at_low = abs(current_price - all_time_low) < 0.01

    if is_at_low:
        return f"""
            <div style="margin-top: 12px; padding: 8px 12px; background: #fef3c7; border-radius: 6px; border: 1px solid #fbbf24;">
                <span style="color: #92400e; font-weight: 600;">🏆 All-time low: ${all_time_low:.2f}</span>
            </div>
        """
    else:
        return f"""
            <div style="margin-top: 12px; padding: 8px 12px; background: #f8fafc; border-radius: 6px;">
                <span style="color: #64748b;">All-time low: ${all_time_low:.2f}</span>
            </div>
        """


def format_booking_card(booking_data: Dict) -> str:
    """Format a single booking card with updated layout"""
    try:
        booking = booking_data["booking"]
        prices = booking_data["prices"]
        trends = booking_data.get("trends", {})

        focus_category = booking["focus_category"]
        holding_price = booking.get("holding_price")
        has_significant_drop = booking_data.get("has_significant_drop", False)
        price_history = booking.get("price_history", [])

        # Calculate better deals
        better_deals = calculate_better_deals(prices, focus_category)
        better_deals_html = format_better_deals_section(better_deals)

        # Calculate stats and price changes
        current_price = prices.get(focus_category, 0)
        previous_record = price_history[-2] if len(price_history) > 1 else None
        previous_price = (
            previous_record["prices"].get(focus_category) if previous_record else None
        )

        # Get all-time low from trends
        all_time_low = trends.get("focus_category", {}).get("lowest")

        # Format status banner
        status_banner_html = _format_status_banner(current_price, holding_price)

        # Format price change display
        price_change_html = _format_price_change_display(current_price, previous_price)

        # Format all-time low
        all_time_low_html = _format_all_time_low(current_price, all_time_low)

        # Card style with optional highlight for significant drops
        card_style = """
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            {}
        """.format("border: 2px solid #16a34a;" if has_significant_drop else "")

        return f"""
            <td style="width: 50%; padding: 20px; vertical-align: top;">
                <div style="{card_style}">
                    <h2 style="margin: 0 0 10px 0; color: #1a1a1a;">
                        {booking["location"]} - {booking.get("location_full_name", "Airport")}
                    </h2>
                    
                    <div style="background: #f3f4f6; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                        <div style="margin-bottom: 5px;">📅 {booking["pickup_date"]} to {booking["dropoff_date"]}</div>
                        <div>⏰ {booking["pickup_time"]} - {booking["dropoff_time"]}</div>
                    </div>
                    
                    {status_banner_html}
                    
                    <div style="text-align: center; padding: 20px 0; margin-bottom: 15px;">
                        <div style="text-transform: uppercase; color: #64748b; font-size: 0.75rem; letter-spacing: 0.05em; margin-bottom: 8px;">
                            {focus_category}
                        </div>
                        <div style="font-size: 2.5rem; font-weight: bold; color: #1a1a1a;">
                            ${current_price:.2f}
                        </div>
                        {price_change_html}
                        {all_time_low_html}
                    </div>
                    
                    {better_deals_html}
                    
                    <div style="margin-top: 15px;">
                        <div style="font-weight: bold; margin-bottom: 8px;">All Categories</div>
                        <div style="background: #f8fafc; border-radius: 8px; overflow: hidden;">
                            {create_price_rows(prices, focus_category)}
                        </div>
                    </div>
                </div>
            </td>
        """
    except Exception as e:
        print(f"Error formatting booking card: {str(e)}")
        traceback.print_exc()
        return f"""
            <td style="padding: 20px;">
                <div style="color: red;">Error formatting booking card: {str(e)}</div>
            </td>
        """


def format_email_body_html(bookings_data: List[Dict]) -> str:
    """Format the complete email body in HTML"""
    try:
        # Print debug info about bookings being processed
        print(f"\nFormatting email HTML for {len(bookings_data)} bookings:")
        for booking_data in bookings_data:
            booking = booking_data["booking"]
            has_drop = booking_data.get("has_significant_drop", False)
            print(
                f"- {booking['location']}: {booking['pickup_date']} to {booking['dropoff_date']}"
            )
            if has_drop:
                print("  * Has significant price drop!")

        # Split bookings into rows of 2
        booking_rows = []
        for i in range(0, len(bookings_data), 2):
            row_bookings = bookings_data[i : i + 2]
            row_html = "<tr>"

            # Add booking cards
            for booking_data in row_bookings:
                row_html += format_booking_card(booking_data)

            # Add empty cell if odd number of bookings
            if len(row_bookings) == 1:
                row_html += "<td style='width: 50%;'></td>"

            row_html += "</tr>"
            booking_rows.append(row_html)

        return f"""
        <div style="max-width: 1200px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #1a1a1a; margin-bottom: 10px; font-size: 24px; font-weight: bold;">
                    <a href="https://www.costcotravel.com/Rental-Cars" 
                       style="color: #2563eb; text-decoration: none;"
                       target="_blank">
                        🚗 Costco Travel Car Rental Update
                    </a>
                </h1>
                <div style="color: #666; font-size: 14px;">
                    Last checked: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    <br>
                    Tracking {len(bookings_data)} booking{"s" if len(bookings_data) != 1 else ""}
                </div>
            </div>
            
            <table style="width: 100%; border-collapse: separate; border-spacing: 15px;">
                {"".join(booking_rows)}
            </table>
            
            <div style="text-align: center; margin-top: 30px; padding: 20px;">
                <a href="https://www.costcotravel.com/Rental-Cars" 
                   style="color: #2563eb; text-decoration: none; font-weight: 500;"
                   target="_blank">
                    View Current Prices at Costco Travel →
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 10px; color: #666; font-size: 12px;">
                All prices include taxes and fees • Historical trends shown when available
            </div>
        </div>
        """
    except Exception as e:
        print(f"Error in format_email_body_html: {str(e)}")
        traceback.print_exc()
        return f"""
        <div style="color: red; padding: 20px;">
            An error occurred while generating the email: {str(e)}
        </div>
        """
