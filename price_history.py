# price_history.py

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class PriceHistory:
    def __init__(self, history_file: str = "price_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    # ... (previous methods remain the same) ...

    def update_prices(self, booking_id: str, prices: Dict[str, float]):
        """Update prices for a specific booking"""
        try:
            if booking_id not in self.history:
                raise ValueError(f"Booking {booking_id} not found")
            
            booking = self.history[booking_id]
            focus_category = booking['focus_category']
            timestamp = datetime.now().strftime("%m/%d %H:%M")
            
            print(f"\nUpdating prices for booking {booking_id}")
            print(f"Focus category: {focus_category}")
            print(f"Current prices: {prices}")
            
            # Add to price records
            price_record = {
                'timestamp': timestamp,
                'prices': prices.copy()  # Make a copy to avoid reference issues
            }
            if 'price_records' not in booking:
                booking['price_records'] = []
            booking['price_records'].append(price_record)
            
            # Add to price history with the focus category price
            if focus_category in prices:
                focus_price = prices[focus_category]
                print(f"Adding price history record - Time: {timestamp}, Price: {focus_price}")
                
                price_history_record = {
                    'timestamp': timestamp,
                    'focus_category_price': focus_price,  # Keeping consistent naming
                    'price': focus_price  # Adding both keys for compatibility
                }
                if 'price_history' not in booking:
                    booking['price_history'] = []
                booking['price_history'].append(price_history_record)
            else:
                print(f"Warning: Focus category {focus_category} not found in prices")
            
            self._save_history()
            print("Price history updated successfully")
            
            # Debug: Print final structure
            print("\nCurrent price history structure:")
            print(json.dumps(booking['price_history'][-1], indent=2))
            
        except Exception as e:
            print(f"Error updating prices: {str(e)}")
            raise

    def get_price_trends(self, booking_id: str) -> Dict:
        """Get price trends for a specific booking"""
        try:
            if booking_id not in self.history:
                raise ValueError(f"Booking {booking_id} not found")
            
            booking = self.history[booking_id]
            records = booking.get('price_records', [])
            price_history = booking.get('price_history', [])
            
            print(f"\nGetting price trends for booking {booking_id}")
            print(f"Number of price records: {len(records)}")
            print(f"Number of price history records: {len(price_history)}")
            
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
            
            print("\nGenerated trends:")
            print(json.dumps(trends, indent=2))
            
            return trends
            
        except Exception as e:
            print(f"Error getting price trends: {str(e)}")
            raise