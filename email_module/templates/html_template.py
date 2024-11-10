# email_module/templates/html_template.py
from typing import Dict, List, Optional
import traceback
from datetime import datetime
from ..styles.css_styles import EMAIL_CSS
from .formatters import format_price_change_html

def get_html_template() -> str:
    """Return base HTML template with CSS"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style type="text/css">
{EMAIL_CSS}
    </style>
</head>
<body>%s</body>
</html>'''

def format_booking_section_html(booking: Dict, prices: Dict[str, float], trends: Dict) -> str:
    """Format a single booking section in HTML"""
    try:
        focus_category = booking['focus_category']
        holding_price = booking.get('holding_price')
        focus_trends = trends.get('focus_category', {})
        
        html = [
            '<div class="booking-card">',
            '<div class="location-header">',
            f'<h2 class="location-name">{booking["location"]} - {booking.get("location_full_name", "Airport")}</h2>',
            '<div class="dates">',
            f'🗓️ {booking["pickup_date"]} to {booking["dropoff_date"]} • 🕐 {booking["pickup_time"]} - {booking["dropoff_time"]}',
            '</div>'
        ]

        if holding_price:
            html.append(f'<div class="dates">💰 Holding Price: ${holding_price:.2f}</div>')
        html.append('</div>')  # Close location-header

        if focus_category in prices:
            focus_price = prices[focus_category]
            
            # Focus category section
            html.extend([
                '<div class="focus-category">',
                '<div class="focus-label">Tracked Category</div>',
                f'<div class="focus-name">{focus_category}</div>',
                '<div class="price-display">',
                format_price_change_html(focus_price, focus_trends.get('previous_price'), holding_price),
                '</div>'
            ])

            # Price statistics
            if focus_trends:
                html.append('<div class="price-stats">')
                if 'lowest' in focus_trends:
                    html.extend([
                        '<div class="stat-box">',
                        '<div class="stat-label">Lowest Price</div>',
                        f'<div class="stat-value">${focus_trends["lowest"]:.2f}</div>',
                        '</div>'
                    ])
                if 'highest' in focus_trends:
                    html.extend([
                        '<div class="stat-box">',
                        '<div class="stat-label">Highest Price</div>',
                        f'<div class="stat-value">${focus_trends["highest"]:.2f}</div>',
                        '</div>'
                    ])
                if 'average' in focus_trends:
                    html.extend([
                        '<div class="stat-box">',
                        '<div class="stat-label">Average Price</div>',
                        f'<div class="stat-value">${focus_trends["average"]:.2f}</div>',
                        '</div>'
                    ])
                html.append('</div>')  # Close price-stats
            html.append('</div>')  # Close focus-category

            # Better deals section
            better_options = []
            for category, price in prices.items():
                if price < focus_price and category != focus_category:
                    savings = focus_price - price
                    savings_pct = (savings / focus_price) * 100
                    better_options.append(
                        f'<div class="deal-option">{category}: ${price:.2f} '
                        f'<span style="color: #059669">Save ${savings:.2f} ({savings_pct:.1f}%)</span></div>'
                    )

            if better_options:
                html.extend([
                    '<div class="better-deals">',
                    '<div class="better-deals-header">',
                    '💰 Better Deals Available',
                    '</div>',
                    *better_options,
                    '</div>'
                ])

        # All prices section
        html.append('<div class="price-list">')
        for category, price in sorted(prices.items(), key=lambda x: x[1]):
            is_focus = category == focus_category
            row_class = 'price-row' + (' focus-row' if is_focus else '')
            price_display = format_price_change_html(
                price,
                None,
                holding_price if is_focus else None
            )
            html.extend([
                f'<div class="{row_class}">',
                f'<span class="category-name">{"🎯 " if is_focus else ""}{category}</span>',
                f'<span class="price-info">{price_display}</span>',
                '</div>'
            ])
        html.append('</div>')  # Close price-list
        html.append('</div>')  # Close booking-card
        
        return '\n'.join(html)
        
    except Exception as e:
        print(f"Error in format_booking_section_html: {str(e)}")
        traceback.print_exc()
        raise

def format_email_body_html(bookings_data: List[Dict]) -> str:
    """Format the complete email body in HTML"""
    try:
        print("Starting HTML email formatting...")
        
        # Build HTML string
        html = []
        
        # Header
        html.extend([
            '<div class="header">',
            '<h1>Costco Travel Car Rental Update</h1>',
            '<div class="metadata">',
            f'Last checked: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '<br>',
            f'Tracking {len(bookings_data)} booking{"s" if len(bookings_data) != 1 else ""}',
            '</div>',
            '</div>'
        ])
        
        print("Header generated successfully")
        
        # Process each booking
        for booking_data in bookings_data:
            print(f"Processing booking for {booking_data['booking']['location']}")
            try:
                booking = booking_data['booking']
                prices = booking_data['prices']
                trends = booking_data['trends']
                html.append(format_booking_section_html(booking, prices, trends))
                print(f"Booking section generated for {booking['location']}")
            except Exception as e:
                print(f"Error processing booking {booking_data['booking']['location']}: {str(e)}")
                traceback.print_exc()
        
        # Footer
        html.extend([
            '<div class="footer">',
            '<p>All prices include taxes and fees • Historical trends shown when available</p>',
            '</div>'
        ])
        
        print("All bookings processed")
        
        # Get complete HTML using template
        try:
            template = get_html_template()
            complete_html = template % '\n'.join(html)
            print("Template applied successfully")
            return complete_html
        except Exception as e:
            print(f"Error applying template: {str(e)}")
            traceback.print_exc()
            raise
        
    except Exception as e:
        print(f"Error in format_email_body_html: {str(e)}")
        traceback.print_exc()
        raise