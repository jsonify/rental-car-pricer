# price_history.py

import json
import os
from datetime import datetime
from typing import Dict, Optional

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
        return f"{location}_{pickup_date}_{dropoff_date}"
    
    def add_price_record(self, 
                        location: str,
                        pickup_date: str,
                        dropoff_date: str,
                        prices: Dict[str, float],
                        focus_category: str):
        """Add a new price record and return comparison with previous prices"""
        config_key = self.get_config_key(location, pickup_date, dropoff_date)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if config_key not in self.history:
            self.history[config_key] = {
                'location': location,
                'pickup_date': pickup_date,
                'dropoff_date': dropoff_date,
                'focus_category': focus_category,
                'price_records': []
            }
        
        # Add new record
        self.history[config_key]['price_records'].append({
            'timestamp': timestamp,
            'prices': prices
        })
        
        # Generate price comparison
        comparison = self._compare_prices(config_key)
        
        # Save updated history
        self._save_history()
        
        return comparison
    
    def _compare_prices(self, config_key: str) -> dict:
        """Compare current prices with previous record"""
        records = self.history[config_key]['price_records']
        focus_category = self.history[config_key]['focus_category']
        
        if len(records) < 2:
            return {
                'is_first_record': True,
                'focus_category': focus_category,
                'current_prices': records[-1]['prices'],
                'changes': None,
                'focus_category_change': None
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
        
        return {
            'is_first_record': False,
            'focus_category': focus_category,
            'current_prices': current,
            'previous_prices': previous,
            'changes': changes,
            'focus_category_change': focus_change
        }
    
    def get_price_history(self, 
                         location: str,
                         pickup_date: str,
                         dropoff_date: str) -> Optional[dict]:
        """Get complete price history for a configuration"""
        config_key = self.get_config_key(location, pickup_date, dropoff_date)
        return self.history.get(config_key)