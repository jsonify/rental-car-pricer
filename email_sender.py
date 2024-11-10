import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    RECIPIENT_EMAIL
)

def format_price_change(current_price: float, previous_price: Optional[float] = None) -> str:
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

def format_booking_section(booking: Dict, prices: Dict[str, float], trends: Dict) -> str:
    """Format a single booking section with prices and trends"""
    lines = []
    focus_category = booking['focus_category']
    
    # Location and dates section
    lines.append(f"\n📍 {booking['location']} - {booking.get('location_full_name', 'Airport')}")
    lines.append(f"📅 {booking['pickup_date']} to {booking['dropoff_date']}")
    lines.append(f"⏰ {booking['pickup_time']} - {booking['dropoff_time']}")
    lines.append("-" * 50)
    
    # Focus category section
    if focus_category in prices:
        focus_price = prices[focus_category]
        focus_trends = trends.get('focus_category', {})
        
        lines.append(f"\n🎯 TRACKED: {focus_category}")
        
        # Current price with trends
        if focus_trends:
            current_price = format_price_change(focus_price, focus_trends.get('previous_price'))
            lines.append(f"Current Price: {current_price}")
            
            if 'lowest' in focus_trends and 'highest' in focus_trends:
                lines.append(f"Historical Range: ${focus_trends['lowest']:.2f} - ${focus_trends['highest']:.2f}")
            if 'average' in focus_trends:
                lines.append(f"Average Price: ${focus_trends['average']:.2f}")
        else:
            lines.append(f"Current Price: ${focus_price:.2f}")
        
        # Find cheaper alternatives
        cheaper_options = []
        for category, price in prices.items():
            if price < focus_price and category != focus_category:
                savings = focus_price - price
                cheaper_options.append(f"- {category}: ${price:.2f} (Save ${savings:.2f})")
        
        if cheaper_options:
            lines.append("\n💰 CHEAPER ALTERNATIVES:")
            lines.extend(cheaper_options)
    
    # All prices section
    max_category_length = max(len(category) for category in prices.keys())
    
    lines.append("\n📊 ALL CATEGORIES:")
    for category, price in sorted(prices.items(), key=lambda x: x[1]):
        prefix = "➡️ " if category == focus_category else "  "
        lines.append(f"{prefix}{category:<{max_category_length}}: ${price:>8.2f}")
    
    return "\n".join(lines)

def format_email_body(bookings_data: List[Dict]) -> str:
    """Format the complete email body for multiple bookings"""
    lines = []
    
    # Email header
    lines.append("🚗 Costco Travel Car Rental Price Update")
    lines.append("=" * 50)
    lines.append(f"\nLast checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total bookings tracked: {len(bookings_data)}")
    lines.append("=" * 50)
    
    # Process each booking
    for booking_data in bookings_data:
        booking = booking_data['booking']
        prices = booking_data['prices']
        trends = booking_data['trends']
        
        section = format_booking_section(booking, prices, trends)
        lines.append(section)
        lines.append("\n" + "=" * 50)
    
    # Footer
    lines.append("\n📝 Notes:")
    lines.append("- Prices include taxes and fees")
    lines.append("- Historical trends shown when available")
    lines.append("- Cheaper alternatives suggested when found")
    
    return "\n".join(lines)

def send_price_alert(bookings_data: List[Dict]) -> bool:
    """Send an email with current rental car prices for multiple bookings"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        # Set subject with summary
        locations = [data['booking']['location'] for data in bookings_data]
        subject = f"Costco Car Rental Update - {', '.join(locations)} - {datetime.now().strftime('%Y-%m-%d')}"
        msg['Subject'] = subject
        
        # Add body
        body = format_email_body(bookings_data)
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