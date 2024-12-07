#!/usr/bin/env python3

import json
from datetime import datetime
import sys
from typing import Dict, List

def load_json_file(filename: str) -> Dict:
    """Load and parse a JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {filename}")
        sys.exit(1)

def merge_price_histories(current_data: Dict, historical_data: Dict) -> Dict:
    """Merge historical price data into current data structure"""
    merged_data = current_data.copy()
    
    # Update metadata
    merged_data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'active_bookings': list(set(
            current_data.get('metadata', {}).get('active_bookings', []) +
            historical_data.get('metadata', {}).get('active_bookings', [])
        ))
    }
    
    # Merge bookings
    for booking_id, historical_booking in historical_data.get('bookings', {}).items():
        if booking_id not in merged_data.get('bookings', {}):
            # New booking from historical data
            merged_data.setdefault('bookings', {})[booking_id] = historical_booking
        else:
            # Merge price histories for existing booking
            current_booking = merged_data['bookings'][booking_id]
            historical_prices = historical_booking.get('price_history', [])
            current_prices = current_booking.get('price_history', [])
            
            # Combine and sort price histories
            all_prices = historical_prices + current_prices
            all_prices.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
            
            # Update booking with merged price history
            current_booking['price_history'] = all_prices
    
    return merged_data

def main():
    """Main function to merge price histories"""
    print("\n🔄 Price History Merge Tool")
    print("=" * 50)
    
    # Load current price history
    print("\nLoading current price history...")
    try:
        current_data = load_json_file('price_history.json')
        print("✅ Current price history loaded")
    except Exception as e:
        print(f"❌ Error loading current price history: {e}")
        return
    
    # Load historical price history
    print("\nLoading historical price history...")
    try:
        historical_data = load_json_file('price_history_cleaned.json')
        print("✅ Historical price history loaded")
    except Exception as e:
        print(f"❌ Error loading historical price history: {e}")
        return
    
    # Create backup of current price history
    backup_filename = f'price_history.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    print(f"\nCreating backup: {backup_filename}")
    try:
        with open(backup_filename, 'w') as f:
            json.dump(current_data, f, indent=2)
        print("✅ Backup created successfully")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return
    
    # Merge price histories
    print("\nMerging price histories...")
    try:
        merged_data = merge_price_histories(current_data, historical_data)
        
        # Save merged data
        with open('price_history.json', 'w') as f:
            json.dump(merged_data, f, indent=2)
        print("✅ Successfully merged and saved price histories")
        
        # Print summary
        print("\n📊 Merge Summary:")
        print(f"Total bookings: {len(merged_data['bookings'])}")
        for booking_id, booking in merged_data['bookings'].items():
            print(f"\n📍 {booking['location']}:")
            print(f"   Price history entries: {len(booking['price_history'])}")
            print(f"   Date range: {booking['pickup_date']} - {booking['dropoff_date']}")
            print(f"   Focus category: {booking['focus_category']}")
        
    except Exception as e:
        print(f"❌ Error merging price histories: {e}")
        return

if __name__ == "__main__":
    main()