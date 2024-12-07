import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from supabase_client import get_supabase_client

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

        # Initialize Supabase client only if credentials are available
        supabase = None
        if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_KEY'):
            try:
                supabase = get_supabase_client()
            except Exception as e:
                print(f"Warning: Could not initialize Supabase client: {str(e)}")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Car Rental Price Update ({datetime.now().strftime("%Y-%m-%d %H:%M")})'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Generate email content (your existing email generation code here)
        text_content = "Price update notification..."  # Your text content
        html_content = "<html><body>Price update notification...</body></html>"  # Your HTML content

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

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
                except Exception as e:
                    print(f"Warning: Failed to update Supabase for booking {booking_id}: {str(e)}")

        return True

    except Exception as e:
        print(f"Error sending price alert: {str(e)}")
        # print("Full traceback:")
        # traceback.print_exc()
        return False