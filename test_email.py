import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from email_module import send_price_alert
from booking_tracker import BookingTracker
from config import RECIPIENT_EMAIL

def verify_env_setup() -> bool:
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

def generate_price_history(base_price: float, 
                         days: int = 14, 
                         volatility: float = 0.03,
                         trend: float = 0.0,
                         samples_per_day: int = 4) -> List[Dict]:
    """
    Generate realistic price history with trends and patterns.
    
    Args:
        base_price: Starting price point
        days: Number of days of history
        volatility: Price variation (0.03 = 3% standard deviation)
        trend: Price trend direction (-0.02 = 2% downward trend per day)
        samples_per_day: Number of price checks per day
    """
    import random
    import math
    
    price_history = []
    total_samples = days * samples_per_day
    
    # Add some randomness to make it more realistic
    random_seed = random.randint(1, 1000)
    random.seed(random_seed)
    
    for i in range(total_samples):
        # Calculate current day and time
        current_day = i // samples_per_day
        hour = (i % samples_per_day) * (24 // samples_per_day)
        
        # Base timestamp
        timestamp = (datetime.now() - timedelta(days=days-current_day, hours=24-hour))
        
        # Calculate trend component
        trend_component = base_price * trend * current_day
        
        # Add daily pattern (prices often higher during peak hours)
        time_of_day = hour / 24.0
        daily_pattern = math.sin(time_of_day * 2 * math.pi) * base_price * 0.01
        
        # Add random noise
        noise = random.gauss(0, base_price * volatility)
        
        # Calculate final price
        price = base_price + trend_component + daily_pattern + noise
        
        # Ensure price doesn't go below minimum threshold
        price = max(price, base_price * 0.5)
        
        price_history.append({
            'timestamp': timestamp.strftime('%m/%d %H:%M'),
            'price': round(price, 2),
            'day_of_week': timestamp.strftime('%A'),
            'hour': hour
        })
    
    return price_history

def calculate_price_analytics(price_history: List[Dict]) -> Dict:
    """Calculate advanced analytics from price history"""
    if not price_history:
        return {}
    
    prices = [record['price'] for record in price_history]
    
    # Basic statistics
    stats = {
        'current': prices[-1],
        'previous': prices[-2] if len(prices) > 1 else None,
        'lowest': min(prices),
        'highest': max(prices),
        'average': sum(prices) / len(prices),
        'total_checks': len(prices)
    }
    
    # Day of week analysis
    dow_prices = {}
    for record in price_history:
        day = record['day_of_week']
        if day not in dow_prices:
            dow_prices[day] = []
        dow_prices[day].append(record['price'])
    
    stats['day_of_week_avg'] = {
        day: sum(prices) / len(prices)
        for day, prices in dow_prices.items()
    }
    
    # Time of day analysis
    hour_prices = {}
    for record in price_history:
        hour = record['hour']
        if hour not in hour_prices:
            hour_prices[hour] = []
        hour_prices[hour].append(record['price'])
    
    stats['hour_avg'] = {
        hour: sum(prices) / len(prices)
        for hour, prices in hour_prices.items()
    }
    
    # Calculate trends
    if len(prices) > 1:
        # Overall trend
        price_change = prices[-1] - prices[0]
        days_elapsed = len(prices) / 4  # assuming 4 samples per day
        stats['daily_trend'] = price_change / days_elapsed if days_elapsed > 0 else 0
        
        # Volatility (standard deviation)
        mean_price = stats['average']
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        stats['volatility'] = (variance ** 0.5) / mean_price  # as percentage of mean
        
        # Price momentum (recent trend vs overall trend)
        recent_prices = prices[-4:]  # last day
        if len(recent_prices) > 1:
            recent_change = recent_prices[-1] - recent_prices[0]
            stats['momentum'] = recent_change / recent_prices[0]  # as percentage
    
    return stats

def generate_sample_data() -> List[Dict]:
    """Generate sample test data with two bookings and rich trend data"""
    print("\n📝 Generating sample test data with 2 bookings and trend analysis...")
    
    # First booking - LIH with Full-size Car (showing price increase)
    base_price_1 = 285.00
    price_history_1 = generate_price_history(
        base_price=base_price_1,
        days=14,
        volatility=0.02,
        trend=0.01  # 1% upward trend per day
    )
    
    # Second booking - KOA with Standard SUV (showing price decrease)
    base_price_2 = 499.99
    price_history_2 = generate_price_history(
        base_price=base_price_2,
        days=14,
        volatility=0.03,
        trend=-0.015  # 1.5% downward trend per day
    )
    
    # Calculate analytics for both bookings
    analytics_1 = calculate_price_analytics(price_history_1)
    analytics_2 = calculate_price_analytics(price_history_2)
    
    # First booking - LIH with Full-size Car
    booking1 = {
        'booking': {
            'location': 'LIH',
            'location_full_name': 'Lihue Airport',
            'pickup_date': '04/03/2025',
            'dropoff_date': '04/10/2025',
            'pickup_time': '12:00 PM',
            'dropoff_time': '12:00 PM',
            'focus_category': 'Full-size Car',
            'holding_price': 299.99
        },
        'prices': {
            'Economy Car': 282.16,
            'Compact Car': 285.42,
            'Intermediate Car': 289.69,
            'Full-size Car': analytics_1['current'],
            'Premium Car': 323.12,
            'Luxury Car': 1450.81
        },
        'trends': {
            'focus_category': {
                **analytics_1,
                'price_history': price_history_1,
                'prediction': {
                    'next_day': analytics_1['current'] + analytics_1['daily_trend'],
                    'next_week': analytics_1['current'] + (analytics_1['daily_trend'] * 7),
                    'confidence': 0.85 - analytics_1['volatility']  # Lower confidence with higher volatility
                },
                'best_booking_time': {
                    'day_of_week': min(analytics_1['day_of_week_avg'].items(), key=lambda x: x[1])[0],
                    'hour': min(analytics_1['hour_avg'].items(), key=lambda x: x[1])[0]
                }
            }
        }
    }
    
    # Second booking - KOA with Standard SUV
    booking2 = {
        'booking': {
            'location': 'KOA',
            'location_full_name': 'Kailua-Kona International Airport',
            'pickup_date': '05/15/2025',
            'dropoff_date': '05/22/2025',
            'pickup_time': '12:00 PM',
            'dropoff_time': '12:00 PM',
            'focus_category': 'Standard SUV',
            'holding_price': 450.00
        },
        'prices': {
            'Economy Car': 325.42,
            'Compact Car': 332.16,
            'Intermediate Car': 345.89,
            'Standard SUV': analytics_2['current'],
            'Full-size SUV': 489.99,
            'Premium SUV': 556.54,
            'Luxury SUV': 789.99
        },
        'trends': {
            'focus_category': {
                **analytics_2,
                'price_history': price_history_2,
                'prediction': {
                    'next_day': analytics_2['current'] + analytics_2['daily_trend'],
                    'next_week': analytics_2['current'] + (analytics_2['daily_trend'] * 7),
                    'confidence': 0.85 - analytics_2['volatility']
                },
                'best_booking_time': {
                    'day_of_week': min(analytics_2['day_of_week_avg'].items(), key=lambda x: x[1])[0],
                    'hour': min(analytics_2['hour_avg'].items(), key=lambda x: x[1])[0]
                }
            }
        }
    }
    
    return [booking1, booking2]

def load_test_data() -> List[Dict]:
    """Load real price history data for email testing"""
    tracker = BookingTracker()
    bookings = tracker.get_active_bookings()
    
    if not bookings or len(bookings) < 2:
        print("\n⚠️ Need at least 2 bookings for layout testing.")
        print("Using sample test data with 2 bookings instead...")
        return generate_sample_data()
    
    print(f"\n📊 Found {len(bookings)} active bookings in price history")
    
    bookings_data = []
    for booking in bookings:
        # Generate booking ID
        booking_id = f"{booking['location']}_{booking['pickup_date']}_{booking['dropoff_date']}".replace("/", "")
        
        # Get latest prices from history
        price_history = booking.get('price_history', [])
        if not price_history:
            print(f"⚠️ No price history for booking {booking_id}")
            continue
            
        latest_prices = price_history[-1].get('prices', {})
        if not latest_prices:
            print(f"⚠️ No prices in latest record for booking {booking_id}")
            continue
        
        # Get trends
        trends = tracker.get_price_trends(booking_id)
        
        bookings_data.append({
            'booking': booking,
            'prices': latest_prices,
            'trends': trends
        })
        
        print(f"\n✅ Loaded data for {booking['location']}:")
        print(f"   📅 {booking['pickup_date']} - {booking['dropoff_date']}")
        print(f"   🎯 {booking['focus_category']}")
        print(f"   💰 Latest prices: {len(latest_prices)} categories")
    
    # If we don't have at least 2 bookings from real data, use sample data
    if len(bookings_data) < 2:
        print("\n⚠️ Not enough bookings in price history for layout testing")
        print("Using sample test data instead...")
        return generate_sample_data()
    
    return bookings_data

def test_email_sending():
    """Test the email sending functionality with real or sample data"""
    if not verify_env_setup():
        return
    
    print("\n🔍 Testing email functionality...")
    print(f"📧 Will send test email to: {RECIPIENT_EMAIL}")
    
    # Load test data from price history or generate sample data
    bookings_data = load_test_data()
    
    if not bookings_data:
        print("\n❌ No test data available")
        return
    
    if len(bookings_data) < 2:
        print("\n⚠️ Warning: Less than 2 bookings available.")
        print("Two-column layout may not be visible in the test email.")
    
    # Print summary of test data
    print("\n📋 Test Data Summary:")
    for data in bookings_data:
        booking = data['booking']
        prices = data['prices']
        trends = data['trends']
        
        print(f"\n📍 {booking['location']}:")
        print(f"   Categories: {len(prices)}")
        print(f"   Focus: {booking['focus_category']}")
        if 'focus_category' in trends:
            print(f"   Price History Records: {len(trends['focus_category'].get('price_history', []))}")
    
    # Attempt to send email
    success = send_price_alert(bookings_data)
    
    if success:
        print("\n✅ Test email sent successfully!")
        print(f"📬 Please check {RECIPIENT_EMAIL} for the test email")
        print("\nEmail contains:")
        print(f"- {len(bookings_data)} booking{'s' if len(bookings_data) > 1 else ''}")
        print("- Two-column layout" if len(bookings_data) >= 2 else "- Single-column layout")
        print("- Real price history and trends")
        print("- Full HTML formatting")
    else:
        print("\n❌ Failed to send test email")
        print("Please verify your email configuration in .env file")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    test_email_sending()