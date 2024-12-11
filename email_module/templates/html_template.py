# email_module/templates/html_template.py
from typing import Dict, List, Optional
import json
import traceback
from datetime import datetime
from ..styles.css_styles import EMAIL_CSS
from .formatters import format_price_change_html
from ..charts import generate_price_trend_chart


def get_holding_price_details(holding_price_histories: List[Dict]) -> Dict:
    """
    Get details about holding prices from history
    
    Returns:
        Dict containing:
        - initial_price: First holding price
        - current_price: Most recent holding price
        - days_since_update: Days since last update
        - total_changes: Number of price changes
    """
    if not holding_price_histories:
        return None
        
    # Sort by effective_from date
    sorted_history = sorted(holding_price_histories, key=lambda x: x['effective_from'])
    
    initial_price = sorted_history[0]['price']
    current_price = sorted_history[-1]['price']
    last_update = datetime.fromisoformat(sorted_history[-1]['effective_from'])
    days_since_update = (datetime.now() - last_update).days
    
    return {
        'initial_price': initial_price,
        'current_price': current_price,
        'days_since_update': days_since_update,
        'total_changes': len(sorted_history)
    }
    
def calculate_holding_price_age(booking: Dict) -> Optional[int]:
    """Calculate days since holding price was last updated"""
    try:
        if not booking.get('holding_price_updated_at'):
            return None
        
        last_update = datetime.fromisoformat(booking['holding_price_updated_at'])
        days_since = (datetime.now() - last_update).days
        return days_since
    except:
        return None

def generate_mini_sparkline(price_history: List[Dict], holding_price_histories: List[Dict], 
                          width: int = 100, height: int = 30) -> str:
    """Generate a simple SVG sparkline comparing actual prices vs holding prices"""
    try:
        if not price_history:
            return ""
        
        # Get all prices for y-axis scaling
        actual_prices = [float(record['price']) for record in price_history]
        
        # Get holding prices at each date point
        holding_prices = []
        sorted_holdings = sorted(holding_price_histories, key=lambda x: x['effective_from'])
        
        for record in price_history:
            price_date = datetime.fromisoformat(record['timestamp'])
            # Find applicable holding price
            applicable_price = None
            for holding in sorted_holdings:
                holding_date = datetime.fromisoformat(holding['effective_from'])
                if holding_date <= price_date:
                    applicable_price = holding['price']
                else:
                    break
            holding_prices.append(applicable_price if applicable_price is not None else sorted_holdings[0]['price'])
        
        # Calculate y-axis scale
        all_prices = actual_prices + holding_prices
        min_price = min(all_prices)
        max_price = max(all_prices)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Calculate points for both lines
        actual_points = []
        holding_points = []
        step = width / (len(price_history) - 1) if len(price_history) > 1 else 0
        
        for i, (actual, holding) in enumerate(zip(actual_prices, holding_prices)):
            x = i * step
            # Normalize prices to height, inverting Y since SVG coords go top-down
            actual_y = height - ((actual - min_price) / price_range * height)
            holding_y = height - ((holding - min_price) / price_range * height)
            actual_points.append(f"{x},{actual_y}")
            holding_points.append(f"{x},{holding_y}")
        
        # Create SVG paths
        actual_path = f"M{' L'.join(actual_points)}"
        holding_path = f"M{' L'.join(holding_points)}"
        
        return f'''
            <svg width="{width}" height="{height}" style="margin-left: 10px;">
                <!-- Holding price line -->
                <path 
                    d="{holding_path}" 
                    fill="none" 
                    stroke="#dc2626" 
                    stroke-width="1.5"
                    stroke-dasharray="3,3"
                    opacity="0.6"
                />
                <!-- Actual price line -->
                <path 
                    d="{actual_path}" 
                    fill="none" 
                    stroke="#2563eb" 
                    stroke-width="2"
                    stroke-linecap="round"
                />
            </svg>
        '''
    except Exception as e:
        print(f"Error generating sparkline: {str(e)}")
        return ""

def format_price_comparison(current_price: float, holding_price_details: Dict, 
                          price_history: List[Dict], holding_price_histories: List[Dict]) -> str:
    """Format the price comparison section with PNG chart and holding price details"""
    if not holding_price_details:
        return ""
    
    current_holding = holding_price_details['current_price']
    price_diff = current_price - current_holding
    pct_change = (price_diff / current_holding) * 100
    
    days_text = f"(last updated {holding_price_details['days_since_update']} days ago)"
    changes_text = f"Changed {holding_price_details['total_changes']} times since initial ${holding_price_details['initial_price']:.2f}"
    
    # Generate price trend chart
    chart_image = generate_price_trend_chart(price_history, holding_price_histories)
    chart_html = f'<img src="{chart_image}" style="width: 100%; max-width: 300px; height: auto;" />' if chart_image else ''
    
    return f"""
        <div style="margin-top: 10px;">
            <div style="font-size: 0.875rem; color: #64748b;">
                vs Holding Price {days_text}
            </div>
            <div style="font-size: 1rem; margin-top: 2px; color: {price_diff > 0 and '#dc2626' or '#16a34a'}">
                {price_diff > 0 and '↑' or '↓'} ${abs(price_diff):.2f}
                ({abs(pct_change):.1f}%)
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">
                {changes_text}
            </div>
            <div style="margin-top: 10px;">
                {chart_html}
            </div>
        </div>
    """
                          
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
        holding_price_histories = booking.get('holding_price_histories', [])
        focus_trends = trends.get('focus_category', {})
        price_history = focus_trends.get('price_history', [])
        
        # Get holding price details
        holding_price_details = get_holding_price_details(holding_price_histories)
        
        # Calculate better deals
        better_deals = calculate_better_deals(prices, focus_category)
        better_deals_html = format_better_deals_section(better_deals)
        
        # Calculate current price and price comparison
        current_price = prices.get(focus_category, 0)
        
        price_comparison_html = ""
        if holding_price_details:
            price_comparison_html = format_price_comparison(
                current_price,
                holding_price_details,
                price_history,
                holding_price_histories
            )

        return f"""
            <td style="width: 50%; padding: 20px; vertical-align: top;">
                <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0 0 10px 0; color: #1a1a1a;">
                        {booking['location']} - {booking.get('location_full_name', 'Airport')}
                    </h2>
                    
                    <div style="background: #f3f4f6; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                        <div style="margin-bottom: 5px;">📅 {booking['pickup_date']} to {booking['dropoff_date']}</div>
                        <div>⏰ {booking['pickup_time']} - {booking['dropoff_time']}</div>
                        {holding_price_details and f'<div style="margin-top: 5px;">💰 Holding Price: ${holding_price_details["current_price"]:.2f}</div>' or ''}
                    </div>
                    
                    <div style="background: #f8fafc; border-radius: 8px; padding: 15px; border: 2px solid #e2e8f0;">
                        <div style="text-transform: uppercase; color: #64748b; font-size: 0.75rem; letter-spacing: 0.05em;">
                            Tracked Category
                        </div>
                        <div style="font-size: 1.25rem; font-weight: bold; margin: 8px 0;">
                            {focus_category}
                        </div>
                        <div style="font-size: 2rem; font-weight: bold;">
                            ${current_price:.2f}
                        </div>
                        
                        {price_comparison_html}
                        
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
                    Costco Travel Car Rental Update
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
            
            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
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