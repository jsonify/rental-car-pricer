#!/usr/bin/env python3
"""
Migrate old booking IDs to new format with category slug.

Old format: {LOCATION}_{PICKUP_DATE}_{DROPOFF_DATE}
New format: {LOCATION}_{PICKUP_DATE}_{DROPOFF_DATE}_{CATEGORY_SLUG}
"""

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

def get_category_slug(category: str) -> str:
    """Convert category to slug by removing all non-alphanumeric characters"""
    return re.sub(r'[^a-zA-Z0-9]', '', category)

def migrate_booking_ids():
    """Migrate old booking IDs to new format"""

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Missing Supabase credentials in .env file")
        return False

    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }

    # Get all bookings from Supabase
    print("Fetching bookings from Supabase...")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/bookings?active=eq.true",
        headers=headers
    )

    if response.status_code != 200:
        print(f"❌ Error fetching bookings: {response.status_code} - {response.text}")
        return False

    bookings = response.json()
    print(f"Found {len(bookings)} active bookings")

    for booking in bookings:
        old_id = booking['id']
        category = booking['focus_category']
        location = booking['location']
        pickup = booking['pickup_date']
        dropoff = booking['dropoff_date']

        # Generate new ID
        category_slug = get_category_slug(category)
        new_id = f"{location}_{pickup}_{dropoff}_{category_slug}".replace("/", "")

        # Check if ID needs migration (doesn't already have category)
        if old_id == new_id:
            print(f"✓ Booking already has correct ID: {old_id}")
            continue

        print(f"\n🔄 Migrating booking:")
        print(f"   Old ID: {old_id}")
        print(f"   New ID: {new_id}")
        print(f"   Location: {location}")
        print(f"   Category: {category}")

        # Step 1: Create new booking with new ID
        print("   Creating new booking...")
        new_booking = {**booking, 'id': new_id}
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/bookings",
            headers={**headers, 'Prefer': 'resolution=merge-duplicates,return=minimal'},
            json=new_booking
        )

        if response.status_code not in (200, 201, 204):
            print(f"   ❌ Error creating new booking: {response.status_code} - {response.text}")
            continue

        # Step 2: Migrate price_histories
        print("   Migrating price histories...")
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/price_histories?booking_id=eq.{old_id}",
            headers=headers
        )

        if response.status_code == 200:
            price_histories = response.json()
            for ph in price_histories:
                # Update booking_id
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/price_histories?id=eq.{ph['id']}",
                    headers={**headers, 'Prefer': 'return=minimal'},
                    json={'booking_id': new_id}
                )
                if response.status_code not in (200, 204):
                    print(f"   ⚠️  Warning: Error updating price history {ph['id']}")

        # Step 3: Migrate holding_price_histories
        print("   Migrating holding price histories...")
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/holding_price_histories?booking_id=eq.{old_id}",
            headers=headers
        )

        if response.status_code == 200:
            holding_histories = response.json()
            for hh in holding_histories:
                # Update booking_id
                response = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/holding_price_histories?id=eq.{hh['id']}",
                    headers={**headers, 'Prefer': 'return=minimal'},
                    json={'booking_id': new_id}
                )
                if response.status_code not in (200, 204):
                    print(f"   ⚠️  Warning: Error updating holding price history {hh['id']}")

        # Step 4: Delete old booking
        print("   Deleting old booking...")
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/bookings?id=eq.{old_id}",
            headers={**headers, 'Prefer': 'return=minimal'}
        )

        if response.status_code in (200, 204):
            print(f"   ✅ Successfully migrated {old_id} → {new_id}")
        else:
            print(f"   ⚠️  Warning: Could not delete old booking: {response.status_code}")

    print("\n✅ Migration complete!")
    return True

if __name__ == '__main__':
    migrate_booking_ids()
