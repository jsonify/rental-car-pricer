import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from supabase_client import get_supabase_client

def format_price(price: float) -> str:
    """Format price with 2 decimal places"""
    return f"${price:.2f}"

def calculate_price_change(current: float, previous: float) -> tuple:
    """Calculate price change and percentage"""
    if not previous:
        return 0, 0
    change = current - previous
    percent = (change / previous) * 100
    return change, percent

def generate_email_content(bookings_data: List[Dict]) -> tuple:
    """Generate both plain text and HTML email content"""
    
    # Plain text version
    text_content = [
        "🚗 Costco Travel Car Rental Price Update",
        "=" * 50,
        f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total bookings tracked: {len(bookings_data)}",
        "=" * 50,
        ""
    ]

    # HTML version
    html_content = [
        """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                .booking { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .price-change.increase { color: #dc2626; }
                .price-change.decrease { color: #059669; }
                .savings { color: #059669; }
                .divider { border-top: 1px solid #e5e7eb; margin: 15px 0; }
                .category-prices { margin-top: 15px; }
                .category-row { display: flex; justify-content: space-between; padding: 8px 0; }
                .category-row:nth-child(odd) { background: #f8f9fa; }
            </style>
        </head>
        <body>
        """
    ]

    # Add header to HTML
    html_content.append(f"""
        <div class="header">
            <h1>🚗 Costco Travel Car Rental Price Update</h1>
            <p>Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total bookings tracked: {len(bookings_data)}</p>
        </div>
    """)

    # Process each booking
    for data in bookings_data:
        booking = data['booking']
        prices = data['prices']
        trends = data.get('trends', {}).get('focus_category', {})
        
        current_price = prices.get(booking['focus_category'], 0)
        previous_price = trends.get('previous_price')
        holding_price = booking.get('holding_price')
        
        price_change, percent_change = calculate_price_change(current_price, previous_price)
        potential_savings = holding_price - current_price if holding_price else 0
        
        # Add to text content
        text_content.extend([
            f"📍 {booking['location']} - {booking['location_full_name']}",
            f"📅 {booking['pickup_date']} to {booking['dropoff_date']}",
            f"⏰ {booking['pickup_time']} - {booking['dropoff_time']}",
            "-" * 50,
            f"\n🎯 TRACKED: {booking['focus_category']}",
            f"Current Price: {format_price(current_price)}"
        ])

        if price_change:
            change_text = f"{format_price(abs(price_change))} ({percent_change:.1f}%)"
            text_content.append(f"Price Change: {'↑' if price_change > 0 else '↓'} {change_text}")

        if holding_price and potential_savings > 0:
            text_content.append(f"Potential Savings: {format_price(potential_savings)}")

        # Add to HTML content
        html_content.append(f"""
            <div class="booking">
                <h2>📍 {booking['location']} - {booking['location_full_name']}</h2>
                <p>📅 {booking['pickup_date']} to {booking['dropoff_date']}</p>
                <p>⏰ {booking['pickup_time']} - {booking['dropoff_time']}</p>
                
                <div class="divider"></div>
                
                <h3>🎯 {booking['focus_category']}</h3>
                <p><strong>Current Price:</strong> {format_price(current_price)}</p>
        """)

        if price_change:
            change_class = "increase" if price_change > 0 else "decrease"
            change_arrow = "↑" if price_change > 0 else "↓"
            html_content.append(f"""
                <p class="price-change {change_class}">
                    {change_arrow} {format_price(abs(price_change))} ({percent_change:.1f}%)
                </p>
            """)

        if holding_price and potential_savings > 0:
            html_content.append(f"""
                <p class="savings">Potential Savings: {format_price(potential_savings)}</p>
            """)

        # Add all category prices
        html_content.append("""
            <div class="category-prices">
                <h4>All Category Prices:</h4>
        """)

        for category, price in sorted(prices.items()):
            diff = price - current_price if category != booking['focus_category'] else 0
            diff_class = "increase" if diff > 0 else "decrease" if diff < 0 else ""
            diff_text = f"({format_price(abs(diff))} {'more' if diff > 0 else 'less'})" if diff else ""
            
            html_content.append(f"""
                <div class="category-row">
                    <span>{category}</span>
                    <span class="{diff_class}">{format_price(price)} {diff_text}</span>
                </div>
            """)

        html_content.append("</div></div>")
        text_content.extend(["-" * 50, ""])

    # Close HTML
    html_content.append("</body></html>")

    return "\n".join(text_content), "\n".join(html_content)

def send_price_alert(bookings_data: List[Dict]) -> bool:
    """Send price alert email and update Supabase"""
    try:
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL')

        if not all([smtp_server, smtp_port, sender_email, sender_password, recipient_email]):
            print("Missing email configuration")
            return False

        # Initialize Supabase client
        supabase = None
        if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_KEY'):
            try:
                supabase = get_supabase_client()
            except Exception as e:
                print(f"Warning: Could not initialize Supabase client: {str(e)}")

        # Generate email content
        text_content, html_content = generate_email_content(bookings_data)

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Car Rental Price Update ({datetime.now().strftime("%Y-%m-%d %H:%M")})'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("✅ Price alert email sent successfully")

        # Update Supabase if client is available
        if supabase:
            for booking_data in bookings_data:
                try:
                    booking_id = booking_data['booking']['id']
                    price_data = {
                        'booking_id': booking_id,
                        'timestamp': datetime.now().isoformat(),
                        'prices': booking_data['prices'],
                        'lowest_price': min(booking_data['prices'].values()) if booking_data['prices'] else None
                    }
                    supabase.update_price_history(booking_id, price_data)
                    print(f"✅ Updated price history for booking {booking_id}")
                except Exception as e:
                    print(f"⚠️ Failed to update Supabase for booking {booking_id}: {str(e)}")

        return True

    except Exception as e:
        print(f"❌ Error sending price alert: {str(e)}")
        return False