# setup.py

import os
import sys
import shutil
import platform
import subprocess
import traceback
import json
from pathlib import Path
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, Optional

def print_header(text: str):
    print(f"\n{'=' * 60}")
    print(f"{text:^60}")
    print('=' * 60)

def print_step(text: str):
    print(f"\n➜ {text}")

def get_airport_code() -> str:
    """Get and validate airport code from user"""
    print_step("Configuring airport location...")
    
    while True:
        airport_code = input("\nEnter the three-letter airport code (e.g., KOA for Kona): ").strip().upper()
        if len(airport_code) == 3 and airport_code.isalpha():
            confirmation = input(f"Is {airport_code} the correct airport code? (y/n): ")
            if confirmation.lower() == 'y':
                return airport_code
        else:
            print("❌ Invalid airport code. Please enter a three-letter code.")

def get_rental_dates() -> tuple:
    """Get and validate rental dates from user"""
    print_step("Setting rental dates...")
    
    # Calculate default dates (3 months from now)
    default_pickup = datetime.now() + timedelta(days=90)
    default_dropoff = default_pickup + timedelta(days=7)
    
    print("\nEnter dates in MM/DD/YYYY format")
    print(f"Default pickup: {default_pickup.strftime('%m/%d/%Y')}")
    print(f"Default dropoff: {default_dropoff.strftime('%m/%d/%Y')}")
    
    while True:
        try:
            pickup = input("\nPickup date (press Enter for default): ").strip()
            pickup_date = default_pickup.strftime("%m/%d/%Y") if not pickup else pickup
            
            dropoff = input("Dropoff date (press Enter for default): ").strip()
            dropoff_date = default_dropoff.strftime("%m/%d/%Y") if not dropoff else dropoff
            
            # Validate dates
            datetime.strptime(pickup_date, "%m/%d/%Y")
            datetime.strptime(dropoff_date, "%m/%d/%Y")
            
            return pickup_date, dropoff_date
        except ValueError:
            print("❌ Invalid date format. Please use MM/DD/YYYY.")

def get_focus_category() -> str:
    """Get user's preferred vehicle category"""
    print_step("Selecting vehicle category to track")
    
    categories = [
        "Economy Car",
        "Compact Car",
        "Mid-size Car",
        "Full-size Car",
        "Premium Car",
        "Luxury Car",
        "Compact SUV",
        "Standard SUV",
        "Full-size SUV",
        "Premium SUV",
        "Minivan"
    ]
    
    print("\nAvailable car categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    
    while True:
        try:
            choice = int(input("\nSelect your preferred category (1-11): "))
            if 1 <= choice <= len(categories):
                return categories[choice-1]
        except ValueError:
            pass
        print("❌ Please enter a valid number between 1 and 11.")

def setup_first_booking() -> Dict:
    """Guide user through setting up their first booking"""
    print_header("First Booking Setup")
    
    print("""
Let's set up your first car rental booking to track.
This will help you start monitoring prices right away.
    """)
    
    # Get booking details
    airport = get_airport_code()
    pickup_date, dropoff_date = get_rental_dates()
    focus_category = get_focus_category()
    
    # Create booking dictionary
    booking = {
        "location": airport,
        "pickup_date": pickup_date,
        "dropoff_date": dropoff_date,
        "focus_category": focus_category,
        "pickup_time": "12:00 PM",
        "dropoff_time": "12:00 PM"
    }
    
    # Initialize price history file with the booking
    history_file = 'price_history.json'
    booking_id = f"{airport}_{pickup_date}_{dropoff_date}".replace("/", "")
    
    initial_history = {
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "active_bookings": [booking_id]
        },
        "bookings": {
            booking_id: {
                **booking,
                "location_full_name": f"{airport} Airport",
                "price_history": [],
                "created_at": datetime.now().isoformat()
            }
        }
    }
    
    with open(history_file, 'w') as f:
        json.dump(initial_history, f, indent=2)
    
    print(f"\n✅ First booking created successfully!")
    print(f"📍 Location: {airport}")
    print(f"📅 Dates: {pickup_date} to {dropoff_date}")
    print(f"🚗 Category: {focus_category}")
    
    return booking

def main():
    print_header("Costco Travel Car Rental Price Tracker Setup")
    
    # Previous setup steps...
    # [Keep your existing setup logic here]
    
    # Add first booking setup
    first_booking = setup_first_booking()
    
    print_header("Setup Complete!")
    print(f"""
Configuration Summary:
- First booking configured for:
  📍 Airport: {first_booking['location']}
  📅 Pickup: {first_booking['pickup_date']}
  📅 Dropoff: {first_booking['dropoff_date']}
  🚗 Category: {first_booking['focus_category']}

Next steps:
1. Run the price checker:
   python3 main.py

2. To add more bookings, select option 2 when running main.py
   
3. To check prices for existing bookings, select option 1
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred during setup: {str(e)}")
        traceback.print_exc()
        sys.exit(1)