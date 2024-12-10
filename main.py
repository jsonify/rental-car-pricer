#!/usr/bin/env python3

import time
import random
import traceback
import os
import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from booking_tracker import BookingTracker
from driver_setup import setup_driver
from human_simulation import human_like_typing, random_mouse_movement, enter_date
from price_extractor import extract_lowest_prices
from email_module import send_price_alert
from services.price_alert_service import PriceAlertService

def get_available_categories(driver) -> Set[str]:
    """Extract all available vehicle categories from the search results page"""
    try:
        categories = set()
        category_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
        
        for row in category_rows:
            try:
                category_name = row.find_element(
                    By.CSS_SELECTOR, 
                    'div.inner.text-center.h3-tag-style'
                ).text.strip()
                categories.add(category_name)
            except NoSuchElementException:
                continue
                
        return categories
    except Exception as e:
        print(f"Error getting available categories: {str(e)}")
        return set()

def validate_category(driver, category: str, location: str) -> bool:
    """Validate if a category exists for the given location"""
    try:
        # Navigate to the search page and enter location
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        # Enter location
        pickup_location_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "pickupLocationTextWidget"))
        )
        pickup_location_element.click()
        time.sleep(random.uniform(0.5, 1))
        human_like_typing(pickup_location_element, location)
        time.sleep(random.uniform(1.5, 2.5))
        
        # Select location from dropdown
        location_xpath = f"//li[contains(text(), '{location}')]"
        try:
            dropdown_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, location_xpath))
            )
        except TimeoutException:
            location_xpath = f"//li[contains(., '{location}')]"
            dropdown_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, location_xpath))
            )
        
        dropdown_item.click()
        time.sleep(random.uniform(1, 2))
        
        # Fill default dates and search
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d/%Y")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")
        
        enter_date(driver, "pickUpDateWidget", tomorrow)
        enter_date(driver, "dropOffDateWidget", day_after)
        
        # Set times
        pickup_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickupTimeWidget"))
        )
        Select(pickup_time).select_by_value("12:00 PM")
        
        dropoff_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropoffTimeWidget"))
        )
        Select(dropoff_time).select_by_value("12:00 PM")
        
        # Check age checkbox
        age_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "driversAgeWidget"))
        )
        if not age_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", age_checkbox)
        
        # Click search
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "findMyCarButton"))
        )
        search_button.click()
        
        # Wait for results
        WebDriverWait(driver, 60).until(
            lambda d: "results" in d.current_url or "vehicles" in d.current_url
        )
        time.sleep(5)
        
        # Get available categories
        available_categories = get_available_categories(driver)
        
        if category not in available_categories:
            print(f"\n❌ Category '{category}' not available at {location}")
            print("\nAvailable categories:")
            for available_category in sorted(available_categories):
                print(f"- {available_category}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error validating category: {str(e)}")
        return False

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
        except TimeoutException:
            print(f"Warning: Could not find exact location match, trying partial match...")
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
        time.sleep(5)  # Wait for prices to fully load
        return True
    except Exception as e:
        print(f"❌ Error waiting for results: {str(e)}")
        return False

def get_new_booking_info(driver) -> Dict:
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
            datetime.strptime(pickup_date, "%m/%d/%Y")
            datetime.strptime(dropoff_date, "%m/%d/%Y")
            break
        except ValueError:
            print("❌ Invalid date format. Please use MM/DD/YYYY format.")
    
    # Get available categories for location
    print(f"\nFetching available categories for {location}...")
    try:
        # Navigate and search to get categories
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        if not fill_search_form(driver, {
            'location': location,
            'pickup_date': pickup_date,
            'dropoff_date': dropoff_date,
            'pickup_time': "12:00 PM",
            'dropoff_time': "12:00 PM"
        }):
            raise Exception("Failed to fill search form")
        
        # Search
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "findMyCarButton"))
        )
        current_url = driver.current_url
        search_button.click()
        
        if not wait_for_results(driver, current_url):
            raise Exception("Failed to load results")
        
        # Get categories
        available_categories = sorted(get_available_categories(driver))
        
        if not available_categories:
            raise Exception("No categories found")
        
        print("\n📋 Available categories:")
        for i, cat in enumerate(available_categories, 1):
            print(f"{i}. {cat}")
        
        while True:
            try:
                cat_choice = int(input("\nSelect category number: ").strip())
                if 1 <= cat_choice <= len(available_categories):
                    focus_category = available_categories[cat_choice - 1]
                    break
                print(f"❌ Please enter a number between 1 and {len(available_categories)}")
            except ValueError:
                print("❌ Please enter a valid number")
        
    except Exception as e:
        print(f"❌ Error getting categories: {str(e)}")
        print("Using default category list...")
        
        default_categories = [
            "Economy Car", "Compact Car", "Intermediate Car", "Standard Car",
            "Full-size Car", "Premium Car", "Compact SUV", "Standard SUV",
            "Full-size SUV", "Premium SUV", "Minivan"
        ]
        
        print("\n📋 Default categories:")
        for i, cat in enumerate(default_categories, 1):
            print(f"{i}. {cat}")
        
        while True:
            try:
                cat_choice = int(input("\nSelect category number: ").strip())
                if 1 <= cat_choice <= len(default_categories):
                    focus_category = default_categories[cat_choice - 1]
                    break
                print(f"❌ Please enter a number between 1 and {len(default_categories)}")
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

def process_booking(driver, booking: Dict) -> Optional[Dict[str, float]]:
    """Process a single booking and return prices"""
    try:
        print(f"\n📍 Checking prices for {booking['location']}")
        print(f"📅 {booking['pickup_date']} to {booking['dropoff_date']}")
        print(f"🎯 Focus category: {booking['focus_category']}")
        
        # Navigate to Costco Travel
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        # Fill the search form
        if not fill_search_form(driver, booking):
            raise Exception("Failed to fill search form")
        
        # Verify form fields
        print("\n🔍 Verifying form fields:")
        pickup_date_value = driver.execute_script("return document.getElementById('pickUpDateWidget').value;")
        dropoff_date_value = driver.execute_script("return document.getElementById('dropOffDateWidget').value;")
        pickup_time_element = driver.find_element(By.ID, "pickupTimeWidget")
        dropoff_time_element = driver.find_element(By.ID, "dropoffTimeWidget")
        
        print(f"✓ Pickup Date: {pickup_date_value}")
        print(f"✓ Dropoff Date: {dropoff_date_value}")
        print(f"✓ Pickup Time: {Select(pickup_time_element).first_selected_option.text}")
        print(f"✓ Dropoff Time: {Select(dropoff_time_element).first_selected_option.text}")
        
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
        
        # Save screenshot
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_name = f"results_{booking['location']}_{timestamp}.png"
        driver.save_screenshot(f"screenshots/{screenshot_name}")
        print(f"📸 Screenshot saved: {screenshot_name}")
        
        # Extract prices
        prices = extract_lowest_prices(driver)
        
        # Verify focus category exists
        if booking['focus_category'] not in prices:
            print(f"\n⚠️ Warning: Focus category '{booking['focus_category']}' not found in results!")
            print("Available categories:")
            for category in sorted(prices.keys()):
                print(f"- {category}")
            
            # Optionally prompt for category change if in interactive mode
            if not os.environ.get('CI'):
                change = input("\nWould you like to change the focus category? (y/n): ").lower()
                if change == 'y':
                    print("\nAvailable categories:")
                    categories = sorted(prices.keys())
                    for i, category in enumerate(categories, 1):
                        print(f"{i}. {category} (${prices[category]:.2f})")
                    
                    while True:
                        try:
                            choice = int(input("\nSelect new category number: ").strip())
                            if 1 <= choice <= len(categories):
                                booking['focus_category'] = categories[choice - 1]
                                print(f"✅ Focus category updated to: {booking['focus_category']}")
                                break
                            print(f"❌ Please enter a number between 1 and {len(categories)}")
                        except ValueError:
                            print("❌ Please enter a valid number")
        
        return prices
        
    except Exception as e:
        print(f"❌ Error processing booking: {str(e)}")
        traceback.print_exc()
        
        # Save error screenshot
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_name = f"error_{booking['location']}_{timestamp}.png"
        driver.save_screenshot(f"screenshots/{screenshot_name}")
        print(f"📸 Error screenshot saved: {screenshot_name}")
        
        return None

def run_price_checks(tracker, active_bookings):
    """Run price checks for all active bookings"""
    driver = setup_driver(headless=True)
    alert_service = PriceAlertService(price_threshold=10.0)  # $10 minimum price drop
    
    # Clean up expired bookings
    deleted_bookings = tracker.cleanup_expired_bookings()
    if deleted_bookings:
        print("\n🧹 Cleaned up expired bookings:")
        for booking_id in deleted_bookings:
            print(f"  - {booking_id}")
    
    try:
        bookings_data = []
        
        # Process each booking
        for booking in active_bookings:
            # Skip expired bookings
            try:
                dropoff_date = datetime.strptime(booking['dropoff_date'], "%m/%d/%Y").date()
                if dropoff_date < datetime.now().date():
                    print(f"Skipping expired booking: {booking['location']} - {booking['dropoff_date']}")
                    continue
            except ValueError:
                print(f"Error parsing date for booking: {booking['location']}")
                continue
                
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
        
        # Send alerts only if there are significant price drops
        if bookings_data:
            if alert_service.send_alerts(bookings_data):
                print("\n📧 Price alert email sent successfully!")
            else:
                print("\n❌ Failed to send price alert email")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        print("\n🔄 Closing browser...")
        driver.quit()

def interactive_mode():
    """Run the price checker in interactive mode with user input"""
    print("\n🚗 Costco Travel Car Rental Price Tracker")
    print("=" * 50)
    
    # Initialize booking tracker
    tracker = BookingTracker()
    active_bookings = tracker.get_active_bookings()
    
    # Display current bookings
    if not active_bookings:
        print("📢 No active bookings found.")
    else:
        print("\n📋 Current active bookings:")
        for i, booking in enumerate(active_bookings, 1):
            print(f"\n{i}. 📍 {booking['location']}")
            print(f"   📅 {booking['pickup_date']} - {booking['dropoff_date']}")
            print(f"   🎯 Focus: {booking['focus_category']}")
    
    # Get user choice
    print("\n🔄 Choose an action:")
    print("1. Track current bookings")
    print("2. Add a new booking")
    print("3. Delete a booking")
    print("4. Update holding prices")
    print("5. Exit")
    
    choice = input("\nChoice (default: 1): ").strip() or "1"
    
    if choice == "2":
        driver = setup_driver(headless=True)
        try:
            new_booking = get_new_booking_info(driver)
            if validate_category(driver, new_booking['focus_category'], new_booking['location']):
                booking_id = tracker.add_booking(**new_booking)
                print(f"\n✅ Added new booking: {new_booking['location']}")
                active_bookings = tracker.get_active_bookings()
            else:
                print("\n❌ Failed to add booking: Invalid category for location")
        finally:
            driver.quit()
    elif choice == "3":
        try:
            booking_id = tracker.get_booking_choice()
            if tracker.delete_booking(booking_id):
                print(f"\n✅ Booking deleted successfully")
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
        return
    elif choice == "4":
        tracker.prompt_for_holding_prices()
        return
    elif choice == "5":
        print("\n👋 Goodbye!")
        return
    
    # Process bookings if there are any
    if active_bookings:
        run_price_checks(tracker, active_bookings)

def automated_mode():
    """Run the price checker in automated mode without user interaction"""
    print("\n🤖 Running in automated mode")
    print("=" * 50)
    
    # Initialize booking tracker
    tracker = BookingTracker()
    active_bookings = tracker.get_active_bookings()
    
    if not active_bookings:
        print("📢 No active bookings found.")
        return
    
    print(f"📋 Found {len(active_bookings)} active bookings")
    run_price_checks(tracker, active_bookings)

def main():
    """Main function that handles command line arguments and execution mode"""
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Costco Travel Car Rental Price Tracker')
        parser.add_argument('-i', '--interactive', 
                          action='store_true',
                          help='Run in interactive mode')
        args = parser.parse_args()

        # Check execution mode
        is_ci = os.environ.get('CI') == 'true'
        
        if args.interactive:
            print("\n🔄 Running in interactive mode...")
            interactive_mode()
        elif is_ci:
            print("\n🤖 Running in CI automated mode...")
            automated_mode()
        else:
            print("\n🤖 Running in automated mode...")
            print("Tip: Use -i or --interactive flag for interactive mode")
            automated_mode()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()