import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

class PriceHistoryInitializer:
    def __init__(self, config):
        """
        Initialize price history manager with configuration settings.
        
        Args:
            config: Configuration object containing search parameters
        """
        self.config = config
        self.template_path = "price_history.template.json"
        self.history_path = "price_history.json"
    
    def create_initial_structure(self) -> Dict:
        """Create the initial price history structure with current config values."""
        current_time = datetime.now(timezone.utc).isoformat(timespec='seconds')
        
        # Extract dates from config
        pickup_date = datetime.strptime(self.config.PICKUP_DATE, "%m/%d/%Y")
        dropoff_date = datetime.strptime(self.config.DROPOFF_DATE, "%m/%d/%Y")
        duration = (dropoff_date - pickup_date).days
        
        return {
            "metadata": {
                "last_updated": current_time,
                "location": self.config.PICKUP_LOCATION,
                "location_full_name": f"{self.config.PICKUP_LOCATION} (Kailua-Kona International Airport)",
                "search_parameters": {
                    "pickup_time": self.config.PICKUP_TIME,
                    "dropoff_time": self.config.DROPOFF_TIME,
                    "duration_days": duration
                }
            },
            "price_records": [],
            "category_stats": {
                category: {
                    "min_price": None,
                    "max_price": None,
                    "avg_price": None,
                    "last_price": None,
                    "price_changes": []
                } for category in [
                    "Economy Car",
                    "Compact Car",
                    "Full-size Car",
                    "Compact SUV"
                ]
            }
        }

    def initialize_price_history(self, force: bool = False) -> bool:
        """
        Initialize the price history file if it doesn't exist or if force is True.
        
        Args:
            force: If True, overwrites existing price_history.json
        
        Returns:
            bool: True if initialization was performed, False if file already existed
        """
        try:
            # Check if history file already exists
            if os.path.exists(self.history_path) and not force:
                print(f"Price history file already exists at {self.history_path}")
                return False
            
            # Create initial structure
            initial_data = self.create_initial_structure()
            
            # Save template for reference
            with open(self.template_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
                print(f"Created template file at {self.template_path}")
            
            # Create actual price history file if needed
            if force or not os.path.exists(self.history_path):
                with open(self.history_path, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2)
                print(f"Created price history file at {self.history_path}")
            
            return True
            
        except Exception as e:
            print(f"Error initializing price history: {str(e)}")
            raise

    def validate_history_file(self) -> bool:
        """
        Validate the structure of an existing price history file.
        
        Returns:
            bool: True if valid, raises exception if invalid
        """
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required top-level keys
            required_keys = ["metadata", "price_records", "category_stats"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key: {key}")
            
            # Validate metadata structure
            metadata_keys = ["last_updated", "location", "location_full_name", "search_parameters"]
            for key in metadata_keys:
                if key not in data["metadata"]:
                    raise ValueError(f"Missing metadata key: {key}")
            
            return True
            
        except FileNotFoundError:
            print(f"Price history file not found at {self.history_path}")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON in price history file")
            return False
        except Exception as e:
            print(f"Error validating price history: {str(e)}")
            return False

def initialize_price_tracking(config) -> None:
    """
    Main function to set up price tracking.
    
    Args:
        config: Configuration object containing search parameters
    """
    initializer = PriceHistoryInitializer(config)
    
    print("\nInitializing price history tracking...")
    
    # Check for existing file
    if os.path.exists(initializer.history_path):
        print("\nExisting price history file found.")
        if initializer.validate_history_file():
            print("✅ Existing file structure is valid")
        else:
            print("❌ Existing file structure is invalid")
            user_input = input("Would you like to reinitialize the file? (y/n): ")
            if user_input.lower() == 'y':
                initializer.initialize_price_history(force=True)
    else:
        print("\nNo existing price history file found.")
        initializer.initialize_price_history()
    
    print("\nPrice history initialization complete!")

if __name__ == "__main__":
    # Example usage
    import config
    initialize_price_tracking(config)