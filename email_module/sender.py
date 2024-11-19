# email_module/sender.py
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List
import smtplib
import traceback
import ssl
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

def send_price_alert(bookings_data: List[Dict]) -> bool:
    """Send an HTML email with current rental car prices"""
    try:
        print("\nStarting email generation process...")
        print(f"SMTP Server: {SMTP_SERVER}")
        print(f"SMTP Port: {SMTP_PORT}")
        print(f"Sender: {SENDER_EMAIL}")
        print(f"Recipient: {RECIPIENT_EMAIL}")
        
        if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
            raise ValueError("Missing required email configuration. Check environment variables.")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        locations = [data['booking']['location'] for data in bookings_data]
        subject = f"Costco Car Rental Update - {', '.join(locations)} - {datetime.now().strftime('%Y-%m-%d')}"
        msg['Subject'] = subject
        
        print("\nGenerating email content...")
        text_body = format_email_body_text(bookings_data)
        html_body = format_email_body_html(bookings_data)
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        print("\nConnecting to SMTP server...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("Starting TLS...")
            server.starttls(context=context)
            print("Logging in...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("Sending email...")
            server.send_message(msg)
            print("✅ Email sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email alert: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False