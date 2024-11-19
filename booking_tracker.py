# booking_tracker.py

from datetime import datetime
import json
import os
from typing import Dict, List, Optional

class BookingTracker:
    def __init__(self, history_file: str = 'price_history.json'):
        self.history_file = history_file
        self.bookings = self._load_bookings()

    def _create_empty_structure(self) -> Dict:
        """Create empty booking history structure"""
        return {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "active_bookings": []
            },
            "bookings": {}
        }

    def _load_bookings(self) -> Dict:
        """Load bookings from the price history file"""
        if not os.path.exists(self.history_file):
            empty_structure = self._create_empty_structure()
            self.save_bookings(empty_structure)
            return empty_structure
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                
                # Ensure required structure exists
                if 'metadata' not in data:
                    data['metadata'] = {}
                if 'active_bookings' not in data['metadata']:
                    data['metadata']['active_bookings'] = []
                if 'bookings' not in data:
                    data['bookings'] = {}
                
                return data
        except json.JSONDecodeError:
            print(f"Error reading {self.history_file}. Creating new booking history.")
            empty_structure = self._create_empty_structure()
            self.save_bookings(empty_structure)
            return empty_structure

    def save_bookings(self, bookings=None):
        """Save bookings to the price history file"""
        if bookings is None:
            bookings = self.bookings
        
        bookings["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.history_file) if os.path.dirname(self.history_file) else '.', exist_ok=True)
        
        with open(self.history_file, 'w') as f:
            json.dump(bookings, f, indent=2)

    def add_booking(self, location: str, pickup_date: str, dropoff_date: str, 
                   focus_category: str, pickup_time: str = "12:00 PM", 
                   dropoff_time: str = "12:00 PM", holding_price: float = None) -> str:
        """Add a new booking to track"""
        booking_id = f"{location}_{pickup_date}_{dropoff_date}".replace("/", "")
        
        if booking_id in self.bookings["bookings"]:
            print(f"Booking already exists for {location} from {pickup_date} to {dropoff_date}")
            return booking_id

        self.bookings["bookings"][booking_id] = {
            "location": location,
            "location_full_name": self._get_location_name(location),
            "pickup_date": pickup_date,
            "dropoff_date": dropoff_date,
            "pickup_time": pickup_time,
            "dropoff_time": dropoff_time,
            "focus_category": focus_category,
            "holding_price": holding_price,
            "price_history": [],
            "created_at": datetime.now().isoformat()
        }
        
        if booking_id not in self.bookings["metadata"]["active_bookings"]:
            self.bookings["metadata"]["active_bookings"].append(booking_id)
        
        self.save_bookings()
        return booking_id

    def delete_booking(self, booking_id: str) -> bool:
        """Delete a specific booking by ID"""
        if booking_id not in self.bookings["bookings"]:
            raise ValueError(f"Booking {booking_id} not found")
            
        # Remove from active bookings
        if booking_id in self.bookings["metadata"]["active_bookings"]:
            self.bookings["metadata"]["active_bookings"].remove(booking_id)
        
        # Remove booking data
        del self.bookings["bookings"][booking_id]
        self.save_bookings()
        return True

    def cleanup_expired_bookings(self) -> List[str]:
        """Remove bookings whose dropoff date has passed"""
        current_date = datetime.now()
        deleted_bookings = []
        
        for booking_id, booking in list(self.bookings["bookings"].items()):
            dropoff_date = datetime.strptime(booking["dropoff_date"], "%m/%d/%Y")
            if dropoff_date < current_date:
                self.delete_booking(booking_id)
                deleted_bookings.append(booking_id)
        
        return deleted_bookings

    def get_booking_choice(self) -> str:
        """Interactive prompt for selecting a booking to delete"""
        active_bookings = self.get_active_bookings()
        
        if not active_bookings:
            raise ValueError("No active bookings found")
        
        print("\n📋 Select booking to delete:")
        for i, booking in enumerate(active_bookings, 1):
            print(f"\n{i}. 📍 {booking['location']}")
            print(f"   📅 {booking['pickup_date']} - {booking['dropoff_date']}")
            print(f"   🎯 Focus: {booking['focus_category']}")
        
        while True:
            try:
                choice = int(input("\nEnter booking number: ").strip())
                if 1 <= choice <= len(active_bookings):
                    booking = active_bookings[choice - 1]
                    booking_id = f"{booking['location']}_{booking['pickup_date']}_{booking['dropoff_date']}".replace("/", "")
                    return booking_id
            except ValueError:
                pass
            print(f"❌ Please enter a number between 1 and {len(active_bookings)}")

    def update_holding_price(self, booking_id: str, holding_price: float):
        """Update the holding price for a booking"""
        if booking_id not in self.bookings["bookings"]:
            raise ValueError(f"Booking {booking_id} not found")
        
        self.bookings["bookings"][booking_id]["holding_price"] = holding_price
        self.save_bookings()

    def get_active_bookings(self) -> List[Dict]:
        """Get all active bookings"""
        active_bookings = []
        for booking_id in self.bookings["metadata"]["active_bookings"]:
            if booking_id in self.bookings["bookings"]:
                booking = self.bookings["bookings"][booking_id]
                active_bookings.append(booking)
        return active_bookings

    def update_prices(self, booking_id: str, prices: Dict[str, float]):
        """Update prices for a specific booking"""
        if booking_id not in self.bookings["bookings"]:
            raise ValueError(f"Booking {booking_id} not found")
            
        self.bookings["bookings"][booking_id]["price_history"].append({
            "timestamp": datetime.now().isoformat(),
            "prices": prices,
            "lowest_price": {
                "category": min(prices.items(), key=lambda x: x[1])[0],
                "price": min(prices.values())
            }
        })
        self.save_bookings()

    def get_price_trends(self, booking_id: str) -> Dict:
        """Get price trends for a specific booking"""
        if booking_id not in self.bookings["bookings"]:
            raise ValueError(f"Booking {booking_id} not found")
            
        booking = self.bookings["bookings"][booking_id]
        history = booking["price_history"]
        
        if not history:
            return {}
            
        focus_category = booking["focus_category"]
        latest_prices = history[-1]["prices"]
        holding_price = booking.get("holding_price")
        
        # Get previous price if available
        previous_price = None
        if len(history) > 1:
            previous_prices = history[-2]["prices"]
            previous_price = previous_prices.get(focus_category)
        
        trends = {
            "focus_category": {
                "current": latest_prices.get(focus_category),
                "previous_price": previous_price,
                "holding_price": holding_price,
                "lowest": float('inf'),
                "highest": float('-inf'),
                "average": 0,
                "total_checks": 0
            }
        }
        
        for record in history:
            if focus_category in record["prices"]:
                price = record["prices"][focus_category]
                trends["focus_category"]["lowest"] = min(trends["focus_category"]["lowest"], price)
                trends["focus_category"]["highest"] = max(trends["focus_category"]["highest"], price)
                trends["focus_category"]["average"] += price
                trends["focus_category"]["total_checks"] += 1
        
        if trends["focus_category"]["total_checks"] > 0:
            trends["focus_category"]["average"] /= trends["focus_category"]["total_checks"]
        
        return trends

    def _get_location_name(self, code: str) -> str:
        """Get full name for airport code"""
        locations = {
            "KOA": "Kailua-Kona International Airport",
            "HNL": "Daniel K. Inouye International Airport",
            "OGG": "Kahului Airport",
            "LIH": "Lihue Airport"
        }
        return locations.get(code, f"{code} Airport")

    def prompt_for_holding_prices(self):
        """Prompt user for holding prices for all active bookings"""
        for booking_id in self.bookings["metadata"]["active_bookings"]:
            booking = self.bookings["bookings"][booking_id]
            current_holding = booking.get("holding_price")
            
            print(f"\n📍 {booking['location']} ({booking['pickup_date']} - {booking['dropoff_date']})")
            print(f"🎯 Focus category: {booking['focus_category']}")
            
            if current_holding:
                print(f"Current holding price: ${current_holding:.2f}")
                update = input("Would you like to update the holding price? (y/n): ").lower()
                if update != 'y':
                    continue
            
            while True:
                try:
                    price_input = input(f"Enter holding price for {booking['focus_category']} (or press Enter to skip): ").strip()
                    if not price_input:
                        break
                    price = float(price_input)
                    self.update_holding_price(booking_id, price)
                    print(f"✅ Holding price updated to ${price:.2f}")
                    break
                except ValueError:
                    print("❌ Please enter a valid number")