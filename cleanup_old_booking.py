#!/usr/bin/env python3
"""
Clean up old booking with incorrect ID format and recreate with new format
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json'
}

# Delete old booking
old_id = "SAN_04022026_04082026"
print(f"Deleting old booking: {old_id}")
response = requests.delete(
    f"{supabase_url}/rest/v1/bookings?id=eq.{old_id}",
    headers=headers
)

if response.status_code == 204:
    print(f"✅ Deleted old booking")
else:
    print(f"⚠️  Status {response.status_code}: {response.text}")

# Delete old price histories
print(f"Deleting old price histories...")
response = requests.delete(
    f"{supabase_url}/rest/v1/price_histories?booking_id=eq.{old_id}",
    headers=headers
)

if response.status_code == 204:
    print(f"✅ Deleted old price histories")
else:
    print(f"⚠️  Status {response.status_code}: {response.text}")

# Delete old holding price histories
print(f"Deleting old holding price histories...")
response = requests.delete(
    f"{supabase_url}/rest/v1/holding_price_histories?booking_id=eq.{old_id}",
    headers=headers
)

if response.status_code == 204:
    print(f"✅ Deleted old holding price histories")
else:
    print(f"⚠️  Status {response.status_code}: {response.text}")

print("\n✅ Cleanup complete! Now update price_history.json and re-add the booking with the new format.")
