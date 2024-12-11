# test_email.py

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List

# Import our actual email formatters
from email_module.templates.html_template import format_email_body_html
from email_module.templates.formatters import format_email_body_text

def generate_test_data() -> List[Dict]:
    """Generate sample booking data that matches Supabase database format"""
    return [{
        'booking': {
            'location': 'LIH',
            'location_full_name': 'Lihue Airport',
            'pickup_date': '04/03/2025',
            'dropoff_date': '04/10/2025',
            'pickup_time': '12:00 PM',
            'dropoff_time': '12:00 PM',
            'focus_category': 'Full-size Car',
            'holding_price_histories': [
                {
                    'price': 560.50,
                    'effective_from': '2024-09-27T00:00:00+00:00',
                    'effective_to': '2024-10-09T00:00:00+00:00'
                },
                {
                    'price': 469.68,
                    'effective_from': '2024-11-18T00:00:00+00:00',
                    'effective_to': None
                }
            ]
        },
        'prices': {
            'Economy Car': 620.40,
            'Compact Car': 558.65,
            'Intermediate Car': 462.88,
            'Standard Car': 465.73,
            'Full-size Car': 469.68,
            'Premium Car': 988.53,
        },
        'price_history': [
            {
                'timestamp': '2024-11-10T00:10:18+00:00',
                'prices': json.dumps({
                    'Full-size Car': 512.07,
                    'Economy Car': 517.19,
                    'Compact Car': 491.40
                }),
                'lowest_price': json.dumps({
                    'price': 491.40,
                    'category': 'Compact Car'
                })
            },
            {
                'timestamp': '2024-11-19T08:39:59+00:00',
                'prices': json.dumps({
                    'Full-size Car': 469.68,
                    'Economy Car': 620.40,
                    'Compact Car': 558.65
                }),
                'lowest_price': json.dumps({
                    'price': 469.68,
                    'category': 'Full-size Car'
                })
            }
        ],
        'trends': {
            'focus_category': {
                'current': 469.68,
                'previous_price': 512.07,
                'lowest': 469.68,
                'highest': 512.07,
                'average': 478.16
            }
        }
    }]

def test_smtp_connection():
    """Test SMTP connection and send a test email with sample booking data"""
    # Get configuration from environment
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = int(os.environ['SMTP_PORT'])
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']
    recipient_email = os.environ.get('RECIPIENT_OVERRIDE') or os.environ['RECIPIENT_EMAIL']

    print("\n📧 Email Configuration:")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Sender: {sender_email}")
    print(f"Recipient: {recipient_email}")

    try:
        # Generate test data
        bookings_data = generate_test_data()
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Car Rental Price Tracker - Test Email ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Generate email content using our actual templates
        text_content = format_email_body_text(bookings_data)
        html_content = format_email_body_html(bookings_data)

        # Attach both versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        print("\n🔄 Connecting to SMTP server...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            print("🔒 Starting TLS connection...")
            
            server.login(sender_email, sender_password)
            print("✅ Login successful")
            
            server.send_message(msg)
            print("📨 Test email sent successfully!")
            return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    test_smtp_connection()