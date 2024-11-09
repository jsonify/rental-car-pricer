# main.py

import time
import random
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from config import (
    PICKUP_LOCATION,
    PICKUP_DATE,
    DROPOFF_DATE,
    PICKUP_TIME,
    DROPOFF_TIME,
    ELEMENT_TIMEOUT,
    SEARCH_TIMEOUT
)
from driver_setup import setup_driver
from human_simulation import human_like_typing, random_mouse_movement, enter_date
from price_extractor import extract_lowest_prices

def check_costco_prices():
    driver = setup_driver()
    try:
        print("Navigating to Costco Travel...")
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        # Random mouse movements
        for _ in range(3):
            random_mouse_movement(driver)
            time.sleep(random.uniform(0.5, 1.5))
        
        # Location input
        pickup_location_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "pickupLocationTextWidget"))
        )
        pickup_location_element.click()
        time.sleep(random.uniform(0.5, 1))
        human_like_typing(pickup_location_element, PICKUP_LOCATION)
        time.sleep(random.uniform(1.5, 2.5))
        
        # Select location from dropdown
        dropdown_item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'KOA') and contains(text(), 'Kailua')]"))
        )
        time.sleep(random.uniform(0.5, 1))
        dropdown_item.click()
        time.sleep(random.uniform(1, 2))
        
        # Enter dates
        max_retries = 3
        for _ in range(max_retries):
            pickup_success = enter_date(driver, "pickUpDateWidget", PICKUP_DATE)
            dropoff_success = enter_date(driver, "dropOffDateWidget", DROPOFF_DATE)
            
            if pickup_success and dropoff_success:
                print("Dates entered successfully!")
                break
            else:
                print("Date entry failed, retrying...")
                time.sleep(1)
        
        # Set times
        pickup_time = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "pickupTimeWidget"))
        )
        Select(pickup_time).select_by_value(PICKUP_TIME)
        time.sleep(random.uniform(0.5, 1))
        
        dropoff_time = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "dropoffTimeWidget"))
        )
        Select(dropoff_time).select_by_value(DROPOFF_TIME)
        time.sleep(random.uniform(0.5, 1))
        
        # Age checkbox
        age_checkbox = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "driversAgeWidget"))
        )
        if not age_checkbox.is_selected():
            time.sleep(random.uniform(0.5, 1))
            driver.execute_script("arguments[0].click();", age_checkbox)
            time.sleep(random.uniform(0.5, 1))
        
        # Final mouse movements
        for _ in range(2):
            random_mouse_movement(driver)
            time.sleep(random.uniform(0.3, 0.7))
        
        # Verify fields
        print("\nVerifying fields before search:")
        pickup_date_value = driver.execute_script("return document.getElementById('pickUpDateWidget').value;")
        dropoff_date_value = driver.execute_script("return document.getElementById('dropOffDateWidget').value;")
        print(f"Pickup Date: {pickup_date_value}")
        print(f"Dropoff Date: {dropoff_date_value}")
        print(f"Pickup Time: {Select(pickup_time).first_selected_option.text}")
        print(f"Dropoff Time: {Select(dropoff_time).first_selected_option.text}")
        
        # Click search
        search_button = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "findMyCarButton"))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
        time.sleep(random.uniform(0.5, 1))
        
        search_button.click()
        print("Search button clicked")
        
        # Wait for results
        current_url = driver.current_url
        print(f"Current URL before search: {current_url}")
        
        def check_search_progress(driver):
            try:
                new_url = driver.current_url
                page_source = driver.page_source.lower()
                
                if new_url != current_url:
                    print(f"URL changed to: {new_url}")
                if "searching" in page_source:
                    print("Found 'searching' in page")
                if "loading" in page_source:
                    print("Found 'loading' in page")
                
                return (
                    "results" in new_url.lower() or
                    "vehicles" in new_url.lower() or
                    new_url != current_url
                )
            except:
                return False
        
        WebDriverWait(driver, SEARCH_TIMEOUT).until(check_search_progress)
        
        print("Results page reached")
        time.sleep(5)
        driver.save_screenshot("final_results.png")
        
        # Extract prices
        prices = extract_lowest_prices(driver)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()
        driver.save_screenshot("error.png")
    finally:
        print("\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    check_costco_prices()