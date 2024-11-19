#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional

class BookingManager:
    def __init__(self, price_history_file: str = 'price_history.json'):
        self.price_history_file = price_history_file
        self.price_history = self._load_price_history()
        self.booking_map = {}
        self._create_booking_map()

    def _load_price_history(self) -> Dict:
        """Load the price history file"""
        try:
            with open(self.price_history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading price history: {e}")
            sys.exit(1)

    def _save_price_history(self) -> None:
        """Save the price history file"""
        try:
            with open(self.price_history_file, 'w') as f:
                json.dump(self.price_history, f, indent=2)
            print("✅ Price history saved successfully")
        except Exception as e:
            print(f"❌ Error saving price history: {e}")
            sys.exit(1)

    def _create_booking_map(self) -> None:
        """Create mapping between booking numbers and booking IDs"""
        bookings = self.price_history.get('bookings', {})
        for i, (booking_id, _) in enumerate(bookings.items(), 1):
            self.booking_map[f"booking_{i}"] = booking_id

    def display_bookings(self) -> None:
        """Display all current bookings"""
        bookings = self.price_history.get('bookings', {})
        
        print("\n=== Current Bookings Before Deletion ===")
        print("{:<5} {:<15} {:<20} {:<25} {:<15}".format(
            "Num", "Location", "Dates", "Category", "Current Price"
        ))
        print("-" * 80)
        
        for i, (_, booking) in enumerate(bookings.items(), 1):
            print("{:<5} {:<15} {:<20} {:<25} {:<15}".format(
                f"[{i}]",
                booking['location'],
                f"{booking['pickup_date']} to {booking['dropoff_date']}",
                booking['focus_category'],
                f"${booking.get('holding_price', 'N/A')}"
            ))

    def delete_booking(self, booking_number: str) -> bool:
        """Delete a booking by its number"""
        try:
            # Display current bookings
            self.display_bookings()
            
            # Get booking ID from map
            booking_key = f"booking_{booking_number}"
            if booking_key not in self.booking_map:
                print(f"❌ Invalid booking number: {booking_number}")
                print(f"Available booking numbers: {list(range(1, len(self.booking_map) + 1))}")
                return False
            
            booking_id = self.booking_map[booking_key]
            
            # Remove from active bookings
            if 'active_bookings' in self.price_history['metadata']:
                if booking_id in self.price_history['metadata']['active_bookings']:
                    self.price_history['metadata']['active_bookings'].remove(booking_id)
                    print(f"✅ Removed booking {booking_number} from active bookings")
            
            # Remove from bookings
            if booking_id in self.price_history['bookings']:
                booking_info = self.price_history['bookings'][booking_id]
                del self.price_history['bookings'][booking_id]
                print(f"✅ Deleted booking {booking_number}:")
                print(f"   Location: {booking_info['location']}")
                print(f"   Dates: {booking_info['pickup_date']} to {booking_info['dropoff_date']}")
                print(f"   Category: {booking_info['focus_category']}")
            
            # Save updated price history
            self._save_price_history()
            
            # Display remaining bookings
            print("\n=== Remaining Bookings After Deletion ===")
            remaining_bookings = self.price_history.get('bookings', {})
            if remaining_bookings:
                for i, (_, booking) in enumerate(remaining_bookings.items(), 1):
                    print(f"[{i}] {booking['location']}: {booking['pickup_date']} to {booking['dropoff_date']}")
            else:
                print("No bookings remaining")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during booking deletion: {e}")
            return False

def main():
    """CLI entry point for booking deletion"""
    # Check if running in GitHub Actions
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        # Get booking number from environment variable
        booking_number = os.environ.get('BOOKING_TO_DELETE', '').strip()
        
        if not booking_number:
            print("❌ No booking number provided (BOOKING_TO_DELETE environment variable is empty)")
            sys.exit(1)
    else:
        # Interactive mode
        manager = BookingManager()
        manager.display_bookings()
        booking_number = input("\nEnter the booking number to delete (or 'q' to quit): ").strip()
        
        if booking_number.lower() == 'q':
            print("Exiting without deletion")
            sys.exit(0)
    
    try:
        booking_number = int(booking_number)
    except ValueError:
        print(f"❌ Invalid booking number format: {booking_number}")
        sys.exit(1)
    
    # Initialize booking manager and delete booking
    manager = BookingManager()
    if manager.delete_booking(str(booking_number)):
        print("✅ Booking deletion completed successfully")
        sys.exit(0)
    else:
        print("❌ Booking deletion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()