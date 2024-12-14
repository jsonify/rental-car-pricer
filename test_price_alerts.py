#!/usr/bin/env python3

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from services.price_alert_service import PriceAlertService
from email_module import send_price_alert

def generate_mock_price_history(base_price: float, 
                              days: int = 14, 
                              volatility: float = 0.03,
                              trend: float = 0.0) -> List[Dict]:
    """Generate realistic price history with trends"""
    import random
    import math
    
    price_history = []
    
    for i in range(days):
        # Calculate trend component
        trend_component = base_price * trend * i
        
        # Add some daily pattern (prices often higher during peak hours)
        for hour in [9, 12, 15, 18]:  # 4 checks per day
            time_of_day = hour / 24.0
            daily_pattern = math.sin(time_of_day * 2 * math.pi) * base_price * 0.01
            
            # Add random noise
            noise = random.gauss(0, base_price * volatility)
            
            # Calculate final price
            price = base_price + trend_component + daily_pattern + noise
            
            # Ensure price doesn't go below minimum threshold
            price = max(price, base_price * 0.5)
            
            timestamp = datetime.now() - timedelta(days=days-i, hours=24-hour)
            
            price_history.append({
                'timestamp': timestamp.strftime('%m/%d %H:%M'),
                'price': round(price, 2)
            })
    
    return price_history

def generate_test_data(scenario: str = 'normal') -> List[Dict]:
    """Generate test data for different scenarios"""
    
    if scenario == 'significant_drop':
        # First booking with significant price drop
        booking1 = {
            'booking': {
                'location': 'LIH',
                'location_full_name': 'Lihue Airport',
                'pickup_date': '04/03/2025',
                'dropoff_date': '04/10/2025',
                'focus_category': 'Full-size Car',
                'holding_price': 299.99
            },
            'prices': {
                'Economy Car': 282.16,
                'Compact Car': 285.42,
                'Full-size Car': 285.42,  # $14.57 drop from holding price
                'Premium Car': 323.12
            }
        }
        
        # Second booking with smaller drop
        booking2 = {
            'booking': {
                'location': 'KOA',
                'location_full_name': 'Kailua-Kona International Airport',
                'pickup_date': '05/15/2025',
                'dropoff_date': '05/22/2025',
                'focus_category': 'Standard SUV',
                'holding_price': 499.99
            },
            'prices': {
                'Economy Car': 325.42,
                'Standard SUV': 495.42,  # Only $4.57 drop - shouldn't trigger alert
                'Premium SUV': 556.54
            }
        }
        
        return [booking1, booking2]
        
    elif scenario == 'no_drops':
        # All prices above holding prices
        booking1 = {
            'booking': {
                'location': 'LIH',
                'location_full_name': 'Lihue Airport',
                'pickup_date': '04/03/2025',
                'dropoff_date': '04/10/2025',
                'focus_category': 'Full-size Car',
                'holding_price': 285.42
            },
            'prices': {
                'Economy Car': 282.16,
                'Compact Car': 285.42,
                'Full-size Car': 299.99,  # Above holding price
                'Premium Car': 323.12
            }
        }
        
        return [booking1]
        
    elif scenario == 'expired_booking':
        # Include an expired booking
        booking1 = {
            'booking': {
                'location': 'LIH',
                'location_full_name': 'Lihue Airport',
                'pickup_date': '11/01/2023',
                'dropoff_date': '11/08/2023',  # Expired
                'focus_category': 'Full-size Car',
                'holding_price': 299.99
            },
            'prices': {
                'Full-size Car': 285.42
            }
        }
        
        # And an active booking with drop
        booking2 = {
            'booking': {
                'location': 'KOA',
                'pickup_date': '04/03/2025',
                'dropoff_date': '04/10/2025',
                'focus_category': 'Economy Car',
                'holding_price': 299.99
            },
            'prices': {
                'Economy Car': 282.16
            }
        }
        
        return [booking1, booking2]
    
    return []

def test_price_alerts():
    """Run tests for price alert functionality"""
    # Initialize service
    alert_service = PriceAlertService(price_threshold=10.0)
    
    test_scenarios = [
        ('significant_drop', 'Significant price drop scenario'),
        ('no_drops', 'No price drops scenario'),
        ('expired_booking', 'Expired booking scenario')
    ]
    
    print("\n🧪 Running price alert tests...")
    
    for scenario, description in test_scenarios:
        print(f"\n📋 Testing {description}")
        
        # Generate test data
        test_data = generate_test_data(scenario)
        
        # Filter active bookings
        active_bookings = alert_service.filter_active_bookings(test_data)
        print(f"Active bookings: {len(active_bookings)}")
        
        # Check for price drops
        drops = alert_service.check_price_drops(active_bookings)
        print(f"Found price drops: {len(drops)}")
        
        if drops:
            print("\nSignificant price drops found:")
            for booking_data in drops:
                booking = booking_data['booking']
                prices = booking_data['prices']
                current_price = prices[booking['focus_category']]
                price_drop = booking['holding_price'] - current_price
                
                print(f"""
Location: {booking['location']}
Category: {booking['focus_category']}
Current Price: ${current_price:.2f}
Holding Price: ${booking['holding_price']:.2f}
Price Drop: ${price_drop:.2f}
""")

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify email configuration
    required_vars = ['SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 
                    'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file")
        return
    
    # Run tests
    test_price_alerts()

if __name__ == "__main__":
    main()