#!/usr/bin/env python3
"""
Sync bookings from price_history.json to Supabase database.
This is useful after a schema migration to repopulate the database.
"""

import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def sync_bookings():
    """Sync all bookings from price_history.json to Supabase"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False

    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

    try:
        # Load price history
        with open('price_history.json', 'r') as f:
            data = json.load(f)

        active_bookings = data['metadata']['active_bookings']

        print(f"\n📚 Found {len(data['bookings'])} bookings in price_history.json")
        print(f"📌 {len(active_bookings)} are active\n")

        # Sync each booking
        for booking_id, booking in data['bookings'].items():
            print(f"Processing: {booking_id}")

            # Prepare booking data
            booking_data = {
                'id': booking_id,
                'location': booking['location'],
                'location_full_name': booking.get('location_full_name', f"{booking['location']} Airport"),
                'pickup_date': booking['pickup_date'],
                'dropoff_date': booking['dropoff_date'],
                'pickup_time': booking.get('pickup_time', '12:00 PM'),
                'dropoff_time': booking.get('dropoff_time', '12:00 PM'),
                'focus_category': booking['focus_category'],
                'holding_price': booking.get('holding_price'),
                'active': booking_id in active_bookings
            }

            # Check if booking exists
            check_response = requests.get(
                f"{supabase_url}/rest/v1/bookings?id=eq.{booking_id}",
                headers=headers
            )

            if check_response.status_code == 200 and check_response.json():
                # Update existing booking
                response = requests.patch(
                    f"{supabase_url}/rest/v1/bookings?id=eq.{booking_id}",
                    headers=headers,
                    json=booking_data
                )
                action = "Updated"
            else:
                # Insert new booking
                response = requests.post(
                    f"{supabase_url}/rest/v1/bookings",
                    headers=headers,
                    json=booking_data
                )
                action = "Created"

            if response.status_code in (200, 201, 204):
                print(f"  ✅ {action} booking: {booking['location']} ({booking['pickup_date']} to {booking['dropoff_date']})")

                # Create holding price history if it exists
                if booking.get('holding_price'):
                    # Check if history entry exists
                    history_check = requests.get(
                        f"{supabase_url}/rest/v1/holding_price_histories?booking_id=eq.{booking_id}&effective_to=is.null",
                        headers=headers
                    )

                    if history_check.status_code == 200 and not history_check.json():
                        # Create initial holding price history
                        history_data = {
                            'booking_id': booking_id,
                            'price': booking['holding_price'],
                            'effective_from': booking.get('created_at', datetime.now().isoformat()),
                            'effective_to': None
                        }

                        history_response = requests.post(
                            f"{supabase_url}/rest/v1/holding_price_histories",
                            headers=headers,
                            json=history_data
                        )

                        if history_response.status_code in (200, 201):
                            print(f"  ✅ Created holding price history: ${booking['holding_price']:.2f}")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")

        print("\n✅ Booking sync complete!")
        return True

    except FileNotFoundError:
        print("❌ price_history.json not found")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    sync_bookings()
