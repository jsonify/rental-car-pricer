from supabase import create_client
import os
from typing import Dict, List
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    def store_price_check(self, bookings_data: List[Dict]) -> bool:
        """Store price check results in Supabase"""
        try:
            for booking_data in bookings_data:
                booking = booking_data['booking']
                prices = booking_data['prices']
                trends = booking_data.get('trends', {})

                # Format data for Supabase
                price_record = {
                    'location': booking['location'],
                    'pickup_date': booking['pickup_date'],
                    'dropoff_date': booking['dropoff_date'],
                    'focus_category': booking['focus_category'],
                    'current_price': prices.get(booking['focus_category']),
                    'holding_price': booking.get('holding_price'),
                    'all_prices': prices,
                    'trends': trends,
                    'checked_at': datetime.now().isoformat()
                }

                # Insert into Supabase
                self.supabase.table('price_checks').insert(price_record).execute()

            return True
        except Exception as e:
            print(f"Error storing in Supabase: {str(e)}")
            return False