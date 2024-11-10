# price_extractor.py

from datetime import datetime
from selenium.webdriver.common.by import By
from config import PRICES_FILE, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE

def extract_lowest_prices(driver):
    """Extract and save lowest prices for each car category"""
    print("\nExtracting lowest prices...")
    
    lowest_prices = {}
    category_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
    
    for row in category_rows:
        try:
            category_name = row.find_element(
                By.CSS_SELECTOR, 
                'div.inner.text-center.h3-tag-style'
            ).text.strip()
            
            lowest_price_element = row.find_element(
                By.CSS_SELECTOR, 
                'a.card.car-result-card.lowest-price'
            )
            
            price = lowest_price_element.get_attribute('data-price')
            lowest_prices[category_name] = float(price)
            print(f"Found {category_name}: ${price}")
            
        except Exception as e:
            continue
    
    save_prices_to_file(lowest_prices)
    return lowest_prices  # Return dictionary instead of tuple

def save_prices_to_file(prices):
    """Save prices to file with timestamp, location, and dates"""
    with open(PRICES_FILE, 'a') as f:
        f.write(f"\n{'='*50}")
        f.write(f"\nPrices as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        f.write(f"\nLocation: {PICKUP_LOCATION} (Kailua-Kona International Airport)")
        f.write(f"\nDates: {PICKUP_DATE} - {DROPOFF_DATE}")
        f.write(f"\n{'-'*50}\n")
        
        # Calculate the longest category name for alignment
        max_length = max(len(category) for category in prices.keys())
        
        for category, price in prices.items():
            # Right-align prices while left-aligning categories
            f.write(f"{category:<{max_length}}: ${price:>8.2f}\n")
            
        f.write(f"{'='*50}\n")
    
    print(f"Prices saved to {PRICES_FILE}")