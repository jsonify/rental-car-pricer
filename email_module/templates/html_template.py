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
                better_deals.append({
                    'category': category,
                    'price': price,
                    'savings': savings,
                    'savings_pct': savings_pct
                })
    return sorted(better_deals, key=lambda x: x['savings'], reverse=True)

def format_better_deals_section(better_deals: List[Dict]) -> str:
    """Format the better deals section of the email"""
    if not better_deals:
        return ""
        
    deals_html = []
    for deal in better_deals:
        deals_html.append(f"""
            <div style="background: white; padding: 8px; margin: 4px 0; border-radius: 4px;">
                {deal['category']}: ${deal['price']:.2f}
                <span style="color: #059669">
                    (Save ${deal['savings']:.2f}, {deal['savings_pct']:.1f}%)
                </span>
            </div>
        """)
    
    return f"""
        <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bae6fd;">
            <div style="font-weight: bold; color: #0369a1; margin-bottom: 10px;">
                💰 Better Deals Available
            </div>
            {''.join(deals_html)}
        </div>
    """

def format_booking_card(booking: Dict, prices: Dict[str, float], trends: Dict) -> str:
    """Format a single booking card with updated layout"""
    try:
        focus_category = booking['focus_category']
        holding_price = booking.get('holding_price')
        focus_trends = trends.get('focus_category', {})
        price_history = booking.get('price_history', [])  # Get price history directly from booking
        
        # Calculate better deals
        better_deals = calculate_better_deals(prices, focus_category)
        better_deals_html = format_better_deals_section(better_deals)
        
        # Calculate stats
        current_price = prices.get(focus_category, 0)
        previous_price = focus_trends.get('previous_price')
        if previous_price:
            price_change = current_price - previous_price
            price_change_html = f"""
                <div style="font-size: 1rem; margin-top: 5px; color: {price_change > 0 and '#dc2626' or '#16a34a'}">
                    {price_change > 0 and '↑' or '↓'} ${abs(price_change):.2f}
                    ({abs((price_change / previous_price) * 100):.1f}%)
                </div>
            """
        else:
            price_change_html = ""

        # Create price history table
        price_history_html = ""
        if price_history:
            history_rows = []
            # Sort history by timestamp in descending order (newest first)
            sorted_history = sorted(price_history, key=lambda x: x['timestamp'], reverse=True)
            
            for record in sorted_history:
                timestamp = record.get('timestamp', '')
                record_prices = record.get('prices', {})
                if focus_category in record_prices:
                    category_price = record_prices[focus_category]
                    history_rows.append(f"""
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 8px; text-align: left;">{timestamp}</td>
                            <td style="padding: 8px; text-align: right;">${category_price:.2f}</td>
                        </tr>
                    """)
            
            if history_rows:  # Only show if we have history data
                price_history_html = f"""
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
                                    {''.join(history_rows)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                """

        return f"""
            <td style="width: 50%; padding: 20px; vertical-align: top;">
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0 0 10px 0; color: #1a1a1a;">
                        {booking['location']} - {booking.get('location_full_name', 'Airport')}
                    </h2>
                    
                    <div style="background: #f3f4f6; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                        <div style="margin-bottom: 5px;">📅 {booking['pickup_date']} to {booking['dropoff_date']}</div>
                        <div>⏰ {booking['pickup_time']} - {booking['dropoff_time']}</div>
                        {holding_price and f'<div style="margin-top: 5px;">💰 Holding Price: ${holding_price:.2f}</div>' or ''}
                    </div>
                    
                    {price_history_html}
                    
                    <div style="background: #f8fafc; border-radius: 8px; padding: 15px; border: 2px solid #e2e8f0;">
                        <div style="text-transform: uppercase; color: #64748b; font-size: 0.75rem; letter-spacing: 0.05em;">
                            Tracked Category
                        </div>
                        <div style="font-size: 1.25rem; font-weight: bold; margin: 8px 0;">
                            {focus_category}
                        </div>
                        <div style="font-size: 2rem; font-weight: bold;">
                            ${current_price:.2f}
                            {price_change_html}
                        </div>
                        
                        <div style="display: flex; gap: 10px; margin-top: 15px;">
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Lowest</div>
                                <div style="font-weight: bold; margin-top: 2px;">
                                    ${focus_trends.get('lowest', 0):.2f}
                                </div>
                            </div>
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Average</div>
                                <div style="font-weight: bold; margin-top: 2px;">
                                    ${focus_trends.get('average', 0):.2f}
                                </div>
                            </div>
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Highest</div>
                                <div style="font-weight: bold; margin-top: 2px;">
                                    ${focus_trends.get('highest', 0):.2f}
                                </div>
                            </div>
                        </div>
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
        """.format('background: #e0f2fe;' if is_focus else '')
        
        rows.append(f"""
            <div style="{row_style}">
                <span>
                    {is_focus and '🎯 ' or ''}{category}
                </span>
                <span>${price:.2f}</span>
            </div>
        """)
    return ''.join(rows)

def format_email_body_html(bookings_data: List[Dict]) -> str:
    """Format the complete email body in HTML"""
    try:
        # Split bookings into rows of 2
        booking_rows = []
        for i in range(0, len(bookings_data), 2):
            row_bookings = bookings_data[i:i+2]
            row_html = "<tr>"
            for booking_data in row_bookings:
                row_html += format_booking_card(
                    booking_data['booking'],
                    booking_data['prices'],
                    booking_data['trends']
                )
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
                    Tracking {len(bookings_data)} booking{'s' if len(bookings_data) != 1 else ''}
                </div>
            </div>
            
            <table style="width: 100%; border-collapse: separate; border-spacing: 15px;">
                {''.join(booking_rows)}
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