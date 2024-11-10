# main.py

import time
import random
import traceback
import argparse
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List, Optional

from booking_tracker import BookingTracker
from headless_driver import setup_headless_driver, setup_visible_driver
from human_simulation import human_like_typing, random_mouse_movement, enter_date
from price_extractor import extract_lowest_prices
from email_module import send_price_alert

def fill_search_form(driver, booking: Dict) -> bool:
    """Fill in the search form for a specific booking"""
    try:
        print(f"\nFilling form for {booking['location']}...")
        
        # Location input
        pickup_location_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "pickupLocationTextWidget"))
        )
        pickup_location_element.click()
        time.sleep(random.uniform(0.5, 1))
        human_like_typing(pickup_location_element, booking['location'])
        time.sleep(random.uniform(1.5, 2.5))
        
        # Select location from dropdown
        location_xpath = f"//li[contains(text(), '{booking['location']}')]"
        try:
            dropdown_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, location_xpath))
            )
            time.sleep(random.uniform(0.5, 1))
            dropdown_item.click()
        except Exception as e:
            print(f"Warning: Could not find exact location match, trying partial match...")
            # Try a more general location match
            location_xpath = f"//li[contains(., '{booking['location']}')]"
            dropdown_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, location_xpath))
            )
            time.sleep(random.uniform(0.5, 1))
            dropdown_item.click()
        
        time.sleep(random.uniform(1, 2))
        
        # Enter dates
        max_retries = 3
        for attempt in range(max_retries):
            pickup_success = enter_date(driver, "pickUpDateWidget", booking['pickup_date'])
            dropoff_success = enter_date(driver, "dropOffDateWidget", booking['dropoff_date'])
            
            if pickup_success and dropoff_success:
                print("✅ Dates entered successfully!")
                break
            else:
                print(f"⚠️ Date entry failed, attempt {attempt + 1}/{max_retries}")
                time.sleep(1)
                if attempt == max_retries - 1:
                    return False
        
        # Set times
        pickup_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickupTimeWidget"))
        )
        Select(pickup_time).select_by_value(booking['pickup_time'])
        time.sleep(random.uniform(0.5, 1))
        
        dropoff_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropoffTimeWidget"))
        )
        Select(dropoff_time).select_by_value(booking['dropoff_time'])
        time.sleep(random.uniform(0.5, 1))
        
        # Age checkbox
        age_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "driversAgeWidget"))
        )
        if not age_checkbox.is_selected():
            time.sleep(random.uniform(0.5, 1))
            driver.execute_script("arguments[0].click();", age_checkbox)
            time.sleep(random.uniform(0.5, 1))
        
        return True
        
    except Exception as e:
        print(f"❌ Error filling form: {str(e)}")
        traceback.print_exc()
        return False

def wait_for_results(driver, current_url: str, timeout: int = 60) -> bool:
    """Wait for search results to load"""
    def check_search_progress(driver):
        try:
            new_url = driver.current_url
            page_source = driver.page_source.lower()
            
            status_updates = []
            if new_url != current_url:
                status_updates.append(f"URL changed to: {new_url}")
            if "searching" in page_source:
                status_updates.append("Searching for vehicles...")
            if "loading" in page_source:
                status_updates.append("Loading results...")
            
            if status_updates:
                print(" | ".join(status_updates))
            
            return (
                "results" in new_url.lower() or
                "vehicles" in new_url.lower() or
                new_url != current_url
            )
        except:
            return False
    
    try:
        WebDriverWait(driver, timeout).until(check_search_progress)
        # Wait for prices to fully load after URL change
        time.sleep(5)
        return True
    except Exception as e:
        print(f"❌ Error waiting for results: {str(e)}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Costco Travel Car Rental Price Monitor')
    parser.add_argument('--headless', action='store_true', 
                      help='Run in headless mode (no visible browser)')
    return parser.parse_args()

def get_new_booking_info() -> Dict:
    """Get information for a new booking from user input"""
    print("\n📝 Enter new booking information:")
    
    # Get location
    while True:
        location = input("\nEnter airport code (e.g., KOA): ").strip().upper()
        if len(location) == 3 and location.isalpha():
            break
        print("❌ Invalid airport code. Please enter a three-letter code.")
    
    # Get dates
    while True:
        try:
            pickup_date = input("Enter pickup date (MM/DD/YYYY): ").strip()
            dropoff_date = input("Enter dropoff date (MM/DD/YYYY): ").strip()
            # Validate dates by parsing them
            datetime.strptime(pickup_date, "%m/%d/%Y")
            datetime.strptime(dropoff_date, "%m/%d/%Y")
            break
        except ValueError:
            print("❌ Invalid date format. Please use MM/DD/YYYY format.")
    
    # Select category
    categories = [
        "Economy Car", "Compact Car", "Mid-size Car", "Full-size Car",
        "Premium Car", "Luxury Car", "Compact SUV", "Standard SUV",
        "Full-size SUV", "Premium SUV", "Minivan"
    ]
    
    print("\n📋 Available categories:")
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat}")
    
    while True:
        try:
            cat_choice = int(input("\nSelect category number: ").strip())
            if 1 <= cat_choice <= len(categories):
                focus_category = categories[cat_choice - 1]
                break
            print(f"❌ Please enter a number between 1 and {len(categories)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return {
        "location": location,
        "pickup_date": pickup_date,
        "dropoff_date": dropoff_date,
        "focus_category": focus_category,
        "pickup_time": "12:00 PM",
        "dropoff_time": "12:00 PM"
    }

def process_booking(driver, booking: Dict, save_screenshots: bool = False) -> Optional[Dict[str, float]]:
    """Process a single booking and return prices"""
    try:
        print(f"\n📍 Checking prices for {booking['location']}")
        print(f"📅 {booking['pickup_date']} to {booking['dropoff_date']}")
        print(f"🎯 Focus category: {booking['focus_category']}")
        
        # Navigate to Costco Travel
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        # Random mouse movements for natural behavior
        for _ in range(3):
            random_mouse_movement(driver)
            time.sleep(random.uniform(0.5, 1.5))
        
        # Fill search form
        if not fill_search_form(driver, booking):
            raise Exception("Failed to fill search form")
        
        # Verify form fields before search
        print("\n🔍 Verifying form fields:")
        pickup_date_value = driver.execute_script("return document.getElementById('pickUpDateWidget').value;")
        dropoff_date_value = driver.execute_script("return document.getElementById('dropOffDateWidget').value;")
        print(f"✓ Pickup Date: {pickup_date_value}")
        print(f"✓ Dropoff Date: {dropoff_date_value}")
        
        # Click search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "findMyCarButton"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
        time.sleep(random.uniform(0.5, 1))
        
        current_url = driver.current_url
        print("\n🔄 Initiating search...")
        search_button.click()
        
        # Wait for results
        if not wait_for_results(driver, current_url):
            raise Exception("Failed to load results")
        
        print("✅ Results loaded successfully")
        
        # Extract prices
        prices = extract_lowest_prices(driver)
        return prices
        
    except Exception as e:
        print(f"❌ Error processing booking: {str(e)}")
        traceback.print_exc()
        return None

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    print("\n🚗 Costco Travel Car Rental Price Tracker")
    print("=" * 50)
    print(f"Mode: {'Headless (Automatic)' if args.headless else 'Visible (Interactive)'}")
    
    # Initialize booking tracker
    tracker = BookingTracker()
    active_bookings = tracker.get_active_bookings()
    
    # Only prompt for holding prices in visible mode
    if not args.headless:
        tracker.prompt_for_holding_prices()
    
    # Display current bookings
    if not active_bookings:
        print("📢 No active bookings found.")
    else:
        print("\n📋 Current active bookings:")
        for i, booking in enumerate(active_bookings, 1):
            print(f"\n{i}. 📍 {booking['location']}")
            print(f"   📅 {booking['pickup_date']} - {booking['dropoff_date']}")
            print(f"   🎯 Focus: {booking['focus_category']}")
    
    # Only prompt for new bookings in visible mode
    if not args.headless:
        print("\n🔄 Choose an action:")
        print("1. Track current bookings only")
        print("2. Add a new booking")
        choice = input("\nChoice (default: 1): ").strip() or "1"
        
        if choice == "2":
            new_booking = get_new_booking_info()
            booking_id = tracker.add_booking(**new_booking)
            print(f"\n✅ Added new booking: {new_booking['location']}")
            active_bookings = tracker.get_active_bookings()
    
    # Process all bookings
    if active_bookings:
        # Setup appropriate driver based on mode
        driver = setup_headless_driver() if args.headless else setup_visible_driver()
        
        try:
            bookings_data = []
            
            # Process each booking
            for booking in active_bookings:
                prices = process_booking(driver, booking)
                
                if prices:
                    # Generate booking ID
                    booking_id = f"{booking['location']}_{booking['pickup_date']}_{booking['dropoff_date']}".replace("/", "")
                    
                    # Update price history
                    tracker.update_prices(booking_id, prices)
                    
                    # Get price trends
                    trends = tracker.get_price_trends(booking_id)
                    
                    # Add to bookings data for email
                    bookings_data.append({
                        'booking': booking,
                        'prices': prices,
                        'trends': trends
                    })
                    
                    print(f"\n✅ Prices updated for {booking['location']}")
                else:
                    print(f"\n❌ Failed to get prices for {booking['location']}")
                
                # Wait between bookings
                time.sleep(random.uniform(2, 4))
            
            # Send email with all booking data
            if bookings_data:
                if send_price_alert(bookings_data):
                    print("\n📧 Price alert email sent successfully!")
                else:
                    print("\n❌ Failed to send price alert email")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            traceback.print_exc()
        finally:
            print("\n🔄 Closing browser...")
            driver.quit()
    
    print("\n✨ Done checking prices!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()