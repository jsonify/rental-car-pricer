# email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECIPIENT_EMAIL,
    PICKUP_LOCATION,
    PICKUP_DATE,
    DROPOFF_DATE,
    FOCUS_CATEGORY
)

def format_price_change(current_price, previous_price=None):
    """Format price change with arrows and percentage"""
    if previous_price is None:
        return f"${current_price:.2f}"
        
    change = current_price - previous_price
    pct_change = (change / previous_price) * 100
    
    if change > 0:
        return f"${current_price:.2f} 🔺 +${change:.2f} (+{pct_change:.1f}%)"
    elif change < 0:
        return f"${current_price:.2f} 🔽 -${abs(change):.2f} ({pct_change:.1f}%)"
    return f"${current_price:.2f} ◾️ No change"

def format_email_body(prices):
    """Format the price data into a clean email body with focus category highlighted"""
    body = []
    body.append("Costco Travel Car Rental Price Update")
    body.append("=" * 50)
    body.append(f"\nPrices as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    body.append(f"Location: {PICKUP_LOCATION} (Kailua-Kona International Airport)")
    body.append(f"Dates: {PICKUP_DATE} - {DROPOFF_DATE}")
    body.append(f"Focus Category: {FOCUS_CATEGORY}")
    body.append("-" * 50)
    
    # Add focus category first with highlight
    if FOCUS_CATEGORY in prices:
        focus_price = prices[FOCUS_CATEGORY]
        body.append(f"\n🎯 TRACKED CATEGORY:")
        body.append(f"{FOCUS_CATEGORY}: ${focus_price:.2f}")
        
        # Find cheaper alternatives
        cheaper_options = []
        for category, price in prices.items():
            if price < focus_price and category != FOCUS_CATEGORY:
                savings = focus_price - price
                cheaper_options.append(f"- {category}: ${price:.2f} (Save ${savings:.2f})")
        
        if cheaper_options:
            body.append("\n💰 CHEAPER ALTERNATIVES:")
            body.extend(cheaper_options)
        
        body.append("\n" + "-" * 50)
    
    # Calculate the longest category name for alignment
    max_length = max(len(category) for category in prices.keys())
    
    # Add all prices
    body.append("\nALL CATEGORIES:")
    for category, price in sorted(prices.items(), key=lambda x: x[1]):  # Sort by price
        prefix = "➡️ " if category == FOCUS_CATEGORY else "  "
        body.append(f"{prefix}{category:<{max_length}}: ${price:>8.2f}")
    
    body.append("=" * 50)
    body.append("\n📊 Price trends and alerts will be shown once more data is collected.")
    return "\n".join(body)

def send_price_alert(prices):
    """Send an email with the current rental car prices"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Costco Car Rental Price Alert - {FOCUS_CATEGORY} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Add body
        body = format_email_body(prices)
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print("✅ Price alert email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email alert: {str(e)}")
        return False