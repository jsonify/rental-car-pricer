# email_module/templates/html_template.py
from typing import Dict, List, Optional
import json
import traceback
from datetime import datetime
from ..styles.css_styles import EMAIL_CSS
from .formatters import format_price_change_html

def create_price_trend_table(price_history: List[Dict]) -> str:
    """Create an HTML table showing price trends"""
    try:
        if not price_history:
            print("No price history available")
            return ""
        
        print("\nCreating price trend table")
        print(f"Number of records: {len(price_history)}")
        print("First record structure:", json.dumps(price_history[0], indent=2))
        
        rows = []
        for record in price_history:
            # Try both possible key names
            price = record.get('price') or record.get('focus_category_price')
            if price is None:
                print(f"Warning: No price found in record: {record}")
                continue
                
            rows.append(f"""
                <tr>
                    <td style="padding: 4px; border-bottom: 1px solid #e5e7eb;">{record['timestamp']}</td>
                    <td style="padding: 4px; border-bottom: 1px solid #e5e7eb; text-align: right;">${price:.2f}</td>
                </tr>
            """)
        
        return f"""
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px;">
                <tr>
                    <th style="padding: 4px; border-bottom: 2px solid #e5e7eb; text-align: left;">Time</th>
                    <th style="padding: 4px; border-bottom: 2px solid #e5e7eb; text-align: right;">Price</th>
                </tr>
                {''.join(rows)}
            </table>
        """
    except Exception as e:
        print(f"Error creating price trend table: {str(e)}")
        traceback.print_exc()
        return f"<div style='color: red;'>Error creating price trend table: {str(e)}</div>"

def create_price_rows(prices: Dict[str, float], focus_category: str) -> str:
    """Create HTML rows for all price categories"""
    rows = []
    for category, price in sorted(prices.items(), key=lambda x: x[1]):
        background = 'background: #e0f2fe;' if category == focus_category else ''
        rows.append(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #e2e8f0; {background}">
                <span>{"🎯 " if category == focus_category else ""}{category}</span>
                <span>${price:.2f}</span>
            </div>
        """)
    return ''.join(rows)

def format_booking_card(booking: Dict, prices: Dict[str, float], trends: Dict) -> str:
    """Format a single booking card"""
    try:
        print(f"\nFormatting booking card for {booking.get('location')}")
        print("Trends structure:", json.dumps(trends, indent=2))
        
        focus_category = booking['focus_category']
        holding_price = booking.get('holding_price')
        focus_trends = trends.get('focus_category', {})
        price_history = focus_trends.get('price_history', [])
        
        print(f"Focus category: {focus_category}")
        print(f"Current prices: {prices}")
        print(f"Number of price history records: {len(price_history)}")
        
        # Better deals section
        better_deals_html = []
        if focus_category in prices:
            focus_price = prices[focus_category]
            for category, price in prices.items():
                if price < focus_price and category != focus_category:
                    savings = focus_price - price
                    savings_pct = (savings / focus_price) * 100
                    better_deals_html.append(f"""
                        <div style="background: #f0f9ff; padding: 8px; margin: 4px 0; border-radius: 4px;">
                            {category}: ${price:.2f} 
                            <span style="color: #059669">(Save ${savings:.2f}, {savings_pct:.1f}%)</span>
                        </div>
                    """)

        better_deals_section = ""
        if better_deals_html:
            better_deals_section = f"""
                <div style="margin: 15px 0;">
                    <div style="font-weight: bold; color: #0369a1; margin-bottom: 8px;">
                        💰 Better Deals Available
                    </div>
                    {''.join(better_deals_html)}
                </div>
            """

        return f"""
            <td style="width: 50%; padding: 20px; vertical-align: top;">
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0 0 10px 0; color: #1a1a1a;">
                        {booking['location']} - {booking.get('location_full_name', 'Airport')}
                    </h2>
                    
                    <div style="background: #f3f4f6; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                        📅 {booking['pickup_date']} to {booking['dropoff_date']}
                        <br>
                        ⏰ {booking['pickup_time']} - {booking['dropoff_time']}
                        {f'<br>💰 Holding Price: ${holding_price:.2f}' if holding_price else ''}
                    </div>
                    
                    <div style="background: #f8fafc; border-radius: 8px; padding: 15px; margin: 15px 0; border: 2px solid #e2e8f0;">
                        <div style="font-size: 0.875rem; color: #64748b; text-transform: uppercase; margin-bottom: 8px;">
                            Tracked Category
                        </div>
                        <div style="font-size: 1.25rem; font-weight: bold; margin-bottom: 10px;">
                            {focus_category}
                        </div>
                        <div style="font-size: 1.5rem; font-weight: bold;">
                            ${prices.get(focus_category, 0):.2f}
                        </div>
                        
                        {create_price_trend_table(price_history)}
                        
                        <div style="display: flex; gap: 10px; margin-top: 15px;">
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Lowest</div>
                                <div style="font-weight: bold;">
                                    ${focus_trends.get('lowest', 0):.2f}
                                </div>
                            </div>
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Average</div>
                                <div style="font-weight: bold;">
                                    ${focus_trends.get('average', 0):.2f}
                                </div>
                            </div>
                            <div style="flex: 1; background: white; padding: 10px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 0.75rem; color: #64748b;">Highest</div>
                                <div style="font-weight: bold;">
                                    ${focus_trends.get('highest', 0):.2f}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {better_deals_section}
                    
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
            # If odd number of bookings, add empty cell
            if len(row_bookings) == 1:
                row_html += "<td style='width: 50%;'></td>"
            row_html += "</tr>"
            booking_rows.append(row_html)

        html = f"""
        <div style="max-width: 1200px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #1a1a1a; margin-bottom: 10px;">Costco Travel Car Rental Update</h1>
                <div style="color: #666;">
                    Last checked: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    <br>
                    Tracking {len(bookings_data)} booking{'s' if len(bookings_data) != 1 else ''}
                </div>
            </div>
            
            <table style="width: 100%; border-collapse: separate; border-spacing: 15px;">
                {''.join(booking_rows)}
            </table>
            
            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                All prices include taxes and fees • Historical trends shown when available
            </div>
        </div>
        """
        
        return html
        
    except Exception as e:
        print(f"Error in format_email_body_html: {str(e)}")
        traceback.print_exc()
        return f"""
        <div style="color: red; padding: 20px;">
            An error occurred while generating the email: {str(e)}
        </div>
        """