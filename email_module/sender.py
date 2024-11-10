# email_module/sender.py
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import smtplib
import traceback

from .templates.html_template import format_email_body_html
from .templates.formatters import format_email_body_text
from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL

def send_price_alert(bookings_data: List[Dict]) -> bool:
    """Send an HTML email with current rental car prices"""
    try:
        print("\nStarting email generation process...")
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        locations = [data['booking']['location'] for data in bookings_data]
        subject = f"Costco Car Rental Update - {', '.join(locations)} - {datetime.now().strftime('%Y-%m-%d')}"
        msg['Subject'] = subject
        
        print("Generating email bodies...")
        try:
            text_body = format_email_body_text(bookings_data)
            print("✅ Plain text body generated successfully")
        except Exception as e:
            print(f"❌ Error generating plain text body: {str(e)}")
            traceback.print_exc()
            raise
            
        try:
            html_body = format_email_body_html(bookings_data)
            print("✅ HTML body generated")
            print("\nFirst 500 characters of HTML:")
            print(html_body[:500])
            print("\nLast 500 characters of HTML:")
            print(html_body[-500:])
        except Exception as e:
            print(f"❌ Error generating HTML body: {str(e)}")
            traceback.print_exc()
            raise
        
        print("\nAttaching bodies to email...")
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        print(f"\n📧 Attempting to send email to {RECIPIENT_EMAIL}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            print("✅ Email sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email alert: {str(e)}")
        traceback.print_exc()
        return False