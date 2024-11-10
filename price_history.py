# price_history.py

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class PriceHistory:
    def __init__(self, history_file: str = "price_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> dict:
        """Load price history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.history_file}. Starting fresh.")
                return {}
        return {}
    
    def _save_history(self):
        """Save price history to JSON file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_config_key(self, location: str, pickup_date: str, dropoff_date: str) -> str:
        """Generate a unique key for this search configuration"""
        return f"{location}_{pickup_date}_{dropoff_date}".replace("/", "")
    
    def add_price_record(self, 
                        location: str,
                        pickup_date: str,
                        dropoff_date: str,
                        prices: Dict[str, float],
                        focus_category: str):
        """Add a new price record and return comparison with previous prices"""
        config_key = self.get_config_key(location, pickup_date, dropoff_date)
        timestamp = datetime.now().strftime("%m/%d %H:%M")
        
        if config_key not in self.history:
            self.history[config_key] = {
                'location': location,
                'pickup_date': pickup_date,
                'dropoff_date': dropoff_date,
                'focus_category': focus_category,
                'price_records': [],
                'price_history': []  # New price history list for trend visualization
            }
        
        # Add new record to price_records
        self.history[config_key]['price_records'].append({
            'timestamp': timestamp,
            'prices': prices
        })
        
        # Add to price history for trend visualization
        focus_price = prices.get(focus_category)
        if focus_price is not None:
            self.history[config_key]['price_history'].append({
                'timestamp': timestamp,
                'focus_category_price': focus_price
            })
        
        # Generate price comparison
        comparison = self._compare_prices(config_key)
        
        # Save updated history
        self._save_history()
        
        return comparison
    
    def update_holding_price(self, booking_id: str, holding_price: float):
        """Update the holding price for a booking"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
        
        self.history[booking_id]['holding_price'] = holding_price
        self._save_history()

    def get_active_bookings(self) -> List[Dict]:
        """Get all active bookings with their complete history"""
        active_bookings = []
        for booking_id, booking_data in self.history.items():
            if not booking_data.get('is_archived', False):  # Skip archived bookings
                # Include all booking data including price history
                booking_info = {
                    'booking_id': booking_id,
                    **booking_data,
                    'price_history': booking_data.get('price_history', [])
                }
                active_bookings.append(booking_info)
        return active_bookings

    def update_prices(self, booking_id: str, prices: Dict[str, float]):
        """Update prices for a specific booking"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
            
        booking = self.history[booking_id]
        focus_category = booking['focus_category']
        timestamp = datetime.now().strftime("%m/%d %H:%M")
        
        # Add to price records
        price_record = {
            'timestamp': timestamp,
            'prices': prices
        }
        booking['price_records'].append(price_record)
        
        # Add to price history with the focus category price
        if focus_category in prices:
            price_history_record = {
                'timestamp': timestamp,
                'price': prices[focus_category]  # Changed from focus_category_price to price
            }
            if 'price_history' not in booking:
                booking['price_history'] = []
            booking['price_history'].append(price_history_record)
        
        self._save_history()

    def _compare_prices(self, config_key: str) -> dict:
        """Compare current prices with previous record"""
        booking = self.history[config_key]
        records = booking['price_records']
        focus_category = booking['focus_category']
        price_history = booking.get('price_history', [])
        
        if len(records) < 2:
            return {
                'is_first_record': True,
                'focus_category': focus_category,
                'current_prices': records[-1]['prices'],
                'changes': None,
                'focus_category_change': None,
                'price_history': price_history
            }
        
        current = records[-1]['prices']
        previous = records[-2]['prices']
        
        # Calculate changes for all categories
        changes = {}
        for category in current:
            if category in previous:
                change = current[category] - previous[category]
                pct_change = (change / previous[category]) * 100
                changes[category] = {
                    'price_change': change,
                    'percentage_change': pct_change
                }
        
        # Get focus category change
        focus_change = changes.get(focus_category, None)
        
        # Calculate statistics for focus category
        focus_prices = [record['prices'].get(focus_category) for record in records 
                       if focus_category in record['prices']]
        
        stats = {
            'lowest': min(focus_prices) if focus_prices else None,
            'highest': max(focus_prices) if focus_prices else None,
            'average': sum(focus_prices) / len(focus_prices) if focus_prices else None
        }
        
        return {
            'is_first_record': False,
            'focus_category': focus_category,
            'current_prices': current,
            'previous_prices': previous,
            'changes': changes,
            'focus_category_change': focus_change,
            'price_history': price_history,
            'stats': stats
        }
    
    def get_price_trends(self, booking_id: str) -> Dict:
        """Get comprehensive price trends for a specific booking"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
            
        booking = self.history[booking_id]
        records = booking['price_records']
        price_history = booking.get('price_history', [])
        
        if not records:
            return {}
            
        focus_category = booking['focus_category']
        latest_prices = records[-1]['prices']
        holding_price = booking.get('holding_price')
        
        # Get previous price if available
        previous_price = None
        if len(records) > 1:
            previous_prices = records[-2]['prices']
            previous_price = previous_prices.get(focus_category)
        
        # Calculate statistics for focus category
        focus_prices = [record['prices'].get(focus_category) for record in records 
                       if focus_category in record['prices']]
        
        trends = {
            "focus_category": {
                "current": latest_prices.get(focus_category),
                "previous_price": previous_price,
                "holding_price": holding_price,
                "lowest": min(focus_prices) if focus_prices else None,
                "highest": max(focus_prices) if focus_prices else None,
                "average": sum(focus_prices) / len(focus_prices) if focus_prices else None,
                "total_checks": len(focus_prices),
                "price_history": price_history
            }
        }
        
        return trends

    def get_price_history(self, 
                         location: str,
                         pickup_date: str,
                         dropoff_date: str) -> Optional[dict]:
        """Get complete price history for a configuration"""
        config_key = self.get_config_key(location, pickup_date, dropoff_date)
        return self.history.get(config_key)

    def archive_booking(self, booking_id: str):
        """Archive a booking to keep it in history but remove from active bookings"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
        
        self.history[booking_id]['is_archived'] = True
        self._save_history()

    def restore_booking(self, booking_id: str):
        """Restore an archived booking to active status"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
        
        self.history[booking_id]['is_archived'] = False
        self._save_history()

    def get_booking_stats(self, booking_id: str) -> Dict:
        """Get comprehensive statistics for a booking"""
        if booking_id not in self.history:
            raise ValueError(f"Booking {booking_id} not found")
            
        booking = self.history[booking_id]
        focus_category = booking['focus_category']
        records = booking['price_records']
        
        if not records:
            return {}
        
        focus_prices = [record['prices'].get(focus_category) for record in records 
                       if focus_category in record['prices']]
        
        total_checks = len(focus_prices)
        if total_checks == 0:
            return {}
        
        current_price = focus_prices[-1] if focus_prices else None
        lowest_price = min(focus_prices) if focus_prices else None
        highest_price = max(focus_prices) if focus_prices else None
        avg_price = sum(focus_prices) / total_checks if focus_prices else None
        
        # Calculate price changes
        price_changes = []
        for i in range(1, len(focus_prices)):
            change = focus_prices[i] - focus_prices[i-1]
            pct_change = (change / focus_prices[i-1]) * 100
            price_changes.append({
                'amount': change,
                'percentage': pct_change
            })
        
        return {
            'current_price': current_price,
            'lowest_price': lowest_price,
            'highest_price': highest_price,
            'average_price': avg_price,
            'total_checks': total_checks,
            'price_changes': price_changes,
            'total_price_changes': len(price_changes),
            'price_decreases': len([c for c in price_changes if c['amount'] < 0]),
            'price_increases': len([c for c in price_changes if c['amount'] > 0]),
            'biggest_decrease': min([c['amount'] for c in price_changes], default=0),
            'biggest_increase': max([c['amount'] for c in price_changes], default=0),
            'price_history': booking.get('price_history', [])
        }