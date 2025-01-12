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
    print(f"\nGenerating email content for {len(bookings_data)} bookings:")
    for booking in bookings_data:
        print(f"- {booking['booking']['location']}: {booking['booking']['pickup_date']} to {booking['booking']['dropoff_date']}")
        if booking.get('has_significant_drop'):
            print("  * Has significant price drop!")
        
    text_content = format_email_body_text(bookings_data)
    html_content = format_email_body_html(bookings_data)
    return text_content, html_content

def send_price_alert(bookings_data: List[Dict]) -> bool:
    """Send price alert email and update Supabase"""
    try:
        # Print debug info
        print(f"\nProcessing {len(bookings_data)} bookings for email:")
        for booking in bookings_data:
            print(f"- {booking['booking']['location']}: {booking['booking']['pickup_date']} to {booking['booking']['dropoff_date']}")

        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL')

        if not all([smtp_server, smtp_port, sender_email, sender_password, recipient_email]):
            print("Missing email configuration")
            return False

        # Filter out expired bookings
        current_date = datetime.now().date()
        active_bookings = []
        for booking_data in bookings_data:
            try:
                booking = booking_data['booking']
                dropoff_date = datetime.strptime(booking['dropoff_date'], "%m/%d/%Y").date()
                if dropoff_date >= current_date:
                    active_bookings.append(booking_data)
                else:
                    print(f"Skipping expired booking in email: {booking['location']} ({booking['dropoff_date']})")
            except Exception as e:
                print(f"Error processing booking for email: {str(e)}")
                continue

        if not active_bookings:
            print("No active bookings to include in email")
            return True

        # Generate email content
        try:
            text_content, html_content = generate_email_content(active_bookings)
            print("✅ Email content generated successfully")
        except Exception as e:
            print(f"Error generating email content: {str(e)}")
            raise

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
            print(f"✅ Price alert email sent successfully for {len(active_bookings)} bookings")

        return True

    except Exception as e:
        print(f"❌ Error sending price alert: {str(e)}")
        traceback.print_exc()
        return False