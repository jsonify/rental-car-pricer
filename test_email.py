# test_email.py

import os
import smtplib
import ssl
import json
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our actual email formatters
from email_module.templates.html_template import format_email_body_html
from email_module.templates.formatters import format_email_body_text

def print_debug(msg: str, obj: Any = None) -> None:
    """Debug print function with clear separators"""
    print("\n" + "="*50)
    print(msg)
    if obj is not None:
        if isinstance(obj, (dict, list)):
            print(json.dumps(obj, indent=2))
        else:
            print(obj)
    print("="*50)

def generate_test_data() -> List[Dict]:
    """Generate sample booking data that matches Supabase database format"""
    test_data = [{
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
        ]
    }]
    
    print_debug("Generated Test Data", test_data)
    return test_data

def test_smtp_connection():
    """Test SMTP connection and send a test email with sample booking data"""
    try:
        # Get configuration from environment
        smtp_server = os.environ['SMTP_SERVER']
        smtp_port = int(os.environ['SMTP_PORT'])
        sender_email = os.environ['SENDER_EMAIL']
        sender_password = os.environ['SENDER_PASSWORD']
        recipient_email = os.environ.get('RECIPIENT_OVERRIDE') or os.environ['RECIPIENT_EMAIL']

        print_debug("Email Configuration", {
            'server': smtp_server,
            'port': smtp_port,
            'sender': sender_email,
            'recipient': recipient_email
        })

        # Generate test data
        bookings_data = generate_test_data()
        
        print_debug("Generating email content...")
        
        # Generate email content
        text_content = format_email_body_text(bookings_data)
        print_debug("Text content generated successfully", text_content[:500] + "...")
        
        html_content = format_email_body_html(bookings_data)
        print_debug("HTML content generated successfully", html_content[:500] + "...")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Car Rental Price Tracker - Test Email ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        print_debug("Connecting to SMTP server...")
        
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            print_debug("TLS connection started")
            
            server.login(sender_email, sender_password)
            print_debug("Login successful")
            
            server.send_message(msg)
            print_debug("Test email sent successfully!")
            return True

    except Exception as e:
        print_debug(f"Error sending email", {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        })
        raise

if __name__ == "__main__":
    test_smtp_connection()