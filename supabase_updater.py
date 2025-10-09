import os
import json
from datetime import datetime
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class SupabaseUpdater:
    def __init__(self, supabase_url: str, service_key: str):
        self.base_url = supabase_url
        self.headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }

    def update_price_histories(self, price_history_file: str = 'price_history.json') -> bool:
        """Update Supabase with only the latest price check data"""
        try:
            # Load latest price history data
            with open(price_history_file, 'r') as f:
                data = json.load(f)

            # Process each booking
            for booking_id, booking in data['bookings'].items():
                # Update booking active status
                booking_data = {
                    'active': booking_id in data['metadata']['active_bookings']
                }
                
                response = requests.patch(
                    f"{self.base_url}/rest/v1/bookings?id=eq.{booking_id}",
                    headers=self.headers,
                    json=booking_data
                )

                if response.status_code != 204:
                    print(f"Warning: Failed to update booking status for {booking_id}")

                # Get only the most recent price record
                price_histories = booking.get('price_history', [])
                if not price_histories:
                    print(f"No price history found for booking {booking_id}")
                    continue

                latest_record = price_histories[-1]  # Get only the last record
                
                # Check if this record already exists
                response = requests.get(
                    f"{self.base_url}/rest/v1/price_histories?booking_id=eq.{booking_id}&timestamp=eq.{latest_record['timestamp']}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"Error checking existing price history for {booking_id}")
                    continue

                if response.json():
                    print(f"Latest price record already exists for booking {booking_id}")
                    continue

                # Insert only the latest price record
                price_history_data = {
                    'booking_id': booking_id,
                    'timestamp': latest_record['timestamp'],
                    'prices': latest_record['prices'],
                    'lowest_price': latest_record.get('lowest_price'),
                    'created_at': datetime.now().isoformat()
                }

                response = requests.post(
                    f"{self.base_url}/rest/v1/price_histories",
                    headers=self.headers,
                    json=price_history_data
                )
                
                if response.status_code in (200, 201):
                    print(f"Added new price record for booking {booking_id}")
                else:
                    print(f"Error inserting price history for {booking_id}: {response.text}")

            return True

        except Exception as e:
            print(f"Error updating Supabase: {str(e)}")
            return False

def update_supabase():
    """Main function to update Supabase with new price data"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials")
        return False
    
    updater = SupabaseUpdater(supabase_url, supabase_key)
    return updater.update_price_histories()

if __name__ == "__main__":
    update_supabase()