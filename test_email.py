# test_email.py

import os
from email_sender import send_price_alert
from config import RECIPIENT_EMAIL
from dotenv import load_dotenv

def verify_env_setup():
    """Verify that all required environment variables are set"""
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    return True

def test_email_sending():
    """Test the email sending functionality"""
    if not verify_env_setup():
        return
    
    print("\n🔍 Testing email functionality...")
    print(f"📧 Will send test email to: {RECIPIENT_EMAIL}")
    
    # Sample test data
    test_prices = {
        "Economy Car": 472.06,
        "Compact Car": 485.32,
        "Full-size Car": 523.45,
        "Compact SUV": 567.89
    }
    
    # Attempt to send email
    success = send_price_alert(test_prices)
    
    if success:
        print("\n✅ Test email sent successfully!")
        print(f"📬 Please check {RECIPIENT_EMAIL} for the test email.")
    else:
        print("\n❌ Failed to send test email.")
        print("Please verify your email configuration in .env file")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    test_email_sending()