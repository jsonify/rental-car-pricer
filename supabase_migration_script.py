import requests
import json
from datetime import datetime
import os
from typing import Dict, List
from dotenv import load_dotenv

class SupabaseRestMigration:
    def __init__(self, supabase_url: str, service_key: str):
        """Initialize Supabase REST client"""
        self.base_url = supabase_url
        self.headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'  # Don't return the response body for faster inserts
        }

    def migrate_data(self, price_history_file: str = 'price_history.json') -> None:
        """Migrate data from JSON file to Supabase using REST API"""
        try:
            # Load JSON data
            print("Loading price history data...")
            with open(price_history_file, 'r') as f:
                data = json.load(f)

            # Process each booking
            total_bookings = len(data['bookings'])
            print(f"\nFound {total_bookings} bookings to migrate")

            for i, (booking_id, booking) in enumerate(data['bookings'].items(), 1):
                print(f"\nProcessing booking {i}/{total_bookings}: {booking_id}")
                
                # Prepare booking data
                booking_data = {
                    'id': booking_id,
                    'location': booking['location'],
                    'location_full_name': booking['location_full_name'],
                    'pickup_date': booking['pickup_date'],
                    'dropoff_date': booking['dropoff_date'],
                    'pickup_time': booking['pickup_time'],
                    'dropoff_time': booking['dropoff_time'],
                    'focus_category': booking['focus_category'],
                    'holding_price': booking.get('holding_price'),
                    'created_at': booking['created_at'],
                    'active': booking_id in data['metadata']['active_bookings']
                }

                # Insert booking using upsert (update if exists)
                response = requests.post(
                    f"{self.base_url}/rest/v1/bookings",
                    headers={**self.headers, 'Prefer': 'resolution=merge-duplicates'},
                    json=booking_data
                )
                
                if response.status_code not in (200, 201):
                    print(f"Error inserting booking {booking_id}: {response.text}")
                    continue
                
                print(f"✓ Booking data migrated")

                # Insert price histories
                price_histories = booking.get('price_history', [])
                if price_histories:
                    print(f"Migrating {len(price_histories)} price records...")
                    
                    for price_record in price_histories:
                        price_history_data = {
                            'booking_id': booking_id,
                            'timestamp': price_record['timestamp'],
                            'prices': price_record['prices'],
                            'lowest_price': price_record.get('lowest_price'),
                            'created_at': datetime.now().isoformat()
                        }

                        response = requests.post(
                            f"{self.base_url}/rest/v1/price_histories",
                            headers=self.headers,
                            json=price_history_data
                        )
                        
                        if response.status_code not in (200, 201):
                            print(f"Error inserting price history: {response.text}")
                            continue
                    
                    print(f"✓ Price history migrated")

            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            raise

    def verify_migration(self) -> None:
        """Verify the migrated data"""
        try:
            print("\nVerifying migration...")
            
            # Get all bookings
            response = requests.get(
                f"{self.base_url}/rest/v1/bookings?select=id",
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Error fetching bookings: {response.text}")
            
            bookings = response.json()
            print(f"\nTotal bookings migrated: {len(bookings)}")
            
            # Get price histories for each booking
            for booking in bookings:
                response = requests.get(
                    f"{self.base_url}/rest/v1/price_histories?booking_id=eq.{booking['id']}&select=id",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"Error fetching price histories for {booking['id']}: {response.text}")
                    continue
                
                histories = response.json()
                print(f"Booking {booking['id']}: {len(histories)} price records")

        except Exception as e:
            print(f"\n❌ Error during verification: {str(e)}")
            raise

def main():
    # Load environment variables
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use the service key for full access
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase credentials. Please check your .env file.")
    
    # Run migration
    migration = SupabaseRestMigration(SUPABASE_URL, SUPABASE_KEY)
    migration.migrate_data()
    migration.verify_migration()

if __name__ == "__main__":
    main()