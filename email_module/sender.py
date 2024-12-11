import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from supabase_client import get_supabase_client
from email_module.templates.html_template import format_email_body_html
from email_module.templates.formatters import format_email_body_text

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
    text_content = format_email_body_text(bookings_data)
    html_content = format_email_body_html(bookings_data)
    return text_content, html_content

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