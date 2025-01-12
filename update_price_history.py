#!/usr/bin/env python3

"""
Script to add a historical price record to the price history.
This adds the missing price point from December 13th, 2024.
"""

import json
from datetime import datetime
import traceback

def add_historical_price(filename: str, booking_id: str, timestamp: str, prices: dict, lowest_price_category: str = None):
    """Add a historical price record to a booking's price history"""
    try:
        # Load current price history
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Verify booking exists
        if booking_id not in data['bookings']:
            print(f"❌ Booking {booking_id} not found")
            return False
        
        # Create price record
        price_record = {
            "timestamp": timestamp,
            "prices": prices,
            "lowest_price": {
                "category": lowest_price_category or min(prices.items(), key=lambda x: x[1])[0],
                "price": min(prices.values())
            }
        }
        
        # Insert price record chronologically
        booking = data['bookings'][booking_id]
        if 'price_history' not in booking:
            booking['price_history'] = []
        
        # Convert timestamp to datetime for comparison
        record_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        
        # Find insertion point
        insert_index = 0
        for i, record in enumerate(booking['price_history']):
            try:
                curr_dt = datetime.strptime(record['timestamp'], "%Y-%m-%dT%H:%M:%S")
                if record_dt < curr_dt:
                    insert_index = i
                    break
            except ValueError:
                # Handle any non-standard timestamp formats
                continue
            insert_index = i + 1
        
        # Insert the record
        booking['price_history'].insert(insert_index, price_record)
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        print("✅ Historical price record added successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error adding historical price: {str(e)}")
        traceback.print_exc()
        return False

def main():
    # Historical price data from December 13th, 2024
    booking_id = "KOA_04102025_04142025"
    timestamp = "2024-12-13T08:00:00"
    prices = {
        "Economy Car": 225.42,
        "Compact Car": 220.15,
        "Intermediate Car": 215.38,  # Key historical price we're adding
        "Standard Car": 225.50,
        "Full-size Car": 226.70,
        "Premium Car": 289.69,
        "Compact SUV": 275.49,
        "Intermediate SUV": 287.33,
        "Standard SUV": 335.73,
        "Standard Elite SUV": 393.49,
        "Full-size SUV": 474.46,
        "Mini Van": 367.76,
        "Jeep Wrangler 2 door": 394.00,
        "Jeep Wrangler 4 door": 423.17,
        "Standard Convertible": 337.91,
        "Standard Sporty Car": 357.19,
        "Premium SUV": 569.38,
        "Luxury SUV": 549.12,
        "Large Luxury SUV": 552.81,
        "Luxury Car": 1181.75,
        "Midsize Pickup": 339.25,
        "Full-size Pickup": 350.00
    }
    
    print(f"\n🕒 Adding historical price record:")
    print(f"📅 Date: {timestamp}")
    print(f"📍 Booking: {booking_id}")
    print(f"🎯 Focus Category (Intermediate Car): ${prices['Intermediate Car']:.2f}")
    
    success = add_historical_price('price_history.json', booking_id, timestamp, prices)
    
    if success:
        print("\n✅ Price history updated successfully")
        print("To verify the update, check the following:")
        print("1. Look for the new record in price_history.json")
        print("2. Run the price checker to see the updated trends")
        print("3. Verify the holding price comparison now works correctly")
    else:
        print("\n❌ Failed to update price history")

if __name__ == "__main__":
    main()