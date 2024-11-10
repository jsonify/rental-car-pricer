# price_extractor.py

from datetime import datetime
from selenium.webdriver.common.by import By
from typing import Dict, Tuple
from price_history import PriceHistory
from config import (
    PRICES_FILE,
    PICKUP_LOCATION,
    PICKUP_DATE,
    DROPOFF_DATE,
    FOCUS_CATEGORY
)

def format_price_change(change: float, percentage: float) -> str:
    """Format price change with symbols and colors"""
    if change > 0:
        return f"🔺 +${change:.2f} (+{percentage:.1f}%)"
    elif change < 0:
        return f"🔽 -${abs(change):.2f} ({percentage:.1f}%)"
    return "◾️ No change"

def format_price_comparison(comparison: dict) -> str:
    """Format price comparison for output"""
    output = []
    focus_category = comparison['focus_category']
    
    output.append(f"\n{'='*60}")
    output.append(f"Price Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Location: {PICKUP_LOCATION}")
    output.append(f"Dates: {PICKUP_DATE} - {DROPOFF_DATE}")
    output.append(f"Focus Category: {focus_category}")
    output.append('-' * 60)
    
    if comparison['is_first_record']:
        output.append("\nInitial price check (no previous data for comparison):")
        for category, price in comparison['current_prices'].items():
            prefix = "➡️ " if category == focus_category else "  "
            output.append(f"{prefix}{category:<15}: ${price:>8.2f}")
    else:
        output.append("\nPrice Changes:")
        for category, price in comparison['current_prices'].items():
            prefix = "➡️ " if category == focus_category else "  "
            change_info = comparison['changes'].get(category, None)
            
            if change_info:
                change_str = format_price_change(
                    change_info['price_change'],
                    change_info['percentage_change']
                )
                output.append(f"{prefix}{category:<15}: ${price:>8.2f} {change_str}")
            else:
                output.append(f"{prefix}{category:<15}: ${price:>8.2f} (New category)")
    
    output.append('=' * 60)
    return '\n'.join(output)

def extract_lowest_prices(driver) -> Tuple[Dict[str, float], str]:
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
    
    # Create price history record
    price_history = PriceHistory()
    comparison = price_history.add_price_record(
        location=PICKUP_LOCATION,
        pickup_date=PICKUP_DATE,
        dropoff_date=DROPOFF_DATE,
        prices=lowest_prices,
        focus_category=FOCUS_CATEGORY
    )
    
    # Format and save the output
    output = format_price_comparison(comparison)
    with open(PRICES_FILE, 'a') as f:
        f.write(output)
    
    print(f"\nPrices saved to {PRICES_FILE}")
    return lowest_prices, output

def get_tracking_summary(prices: Dict[str, float], focus_category: str) -> str:
    """Generate a summary focusing on the tracked category"""
    summary = []
    current_price = prices.get(focus_category)
    
    if current_price:
        summary.append(f"\nTracking Summary for {focus_category}")
        summary.append(f"Current Price: ${current_price:.2f}")
        
        # Add comparison with other categories
        cheaper_options = []
        for category, price in prices.items():
            if price < current_price and category != focus_category:
                savings = current_price - price
                cheaper_options.append(
                    f"- {category}: ${price:.2f} (Save ${savings:.2f})"
                )
        
        if cheaper_options:
            summary.append("\nCheaper alternatives available:")
            summary.extend(cheaper_options)
    
    return '\n'.join(summary)