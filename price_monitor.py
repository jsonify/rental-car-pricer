from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from datetime import datetime
import random
import time
import traceback

def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/Users/jsonify/Downloads/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
    
    # Add stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Add more human-like settings
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

    service = Service("/Users/jsonify/Downloads/chromedriver-mac-x64/chromedriver", service_log_path="selenium.log")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Remove webdriver property
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def human_like_typing(element, text):
    """Simulate human-like typing with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def random_mouse_movement(driver):
    """Simulate random mouse movements"""
    driver.execute_script("""
        var event = new MouseEvent('mousemove', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'clientX': arguments[0],
            'clientY': arguments[1]
        });
        document.dispatchEvent(event);
    """, random.randint(100, 700), random.randint(100, 500))

def enter_date(driver, field_id, date_value):
    """Enhanced date entry function"""
    date_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    
    # Clear the field using different methods
    date_field.click()
    time.sleep(random.uniform(0.3, 0.7))
    
    # Clear using JavaScript
    driver.execute_script("arguments[0].value = '';", date_field)
    
    # Also try regular clear
    date_field.clear()
    time.sleep(random.uniform(0.3, 0.7))
    
    # Enter date using JavaScript first
    driver.execute_script(f"arguments[0].value = '{date_value}';", date_field)
    
    # Then also type it manually to trigger any necessary events
    date_field.click()
    human_like_typing(date_field, date_value)
    
    # Send Tab key to trigger any blur events
    date_field.send_keys(Keys.TAB)
    
    # Add a small delay to let any date picker close
    time.sleep(random.uniform(1, 1.5))
    
    # Verify the date was entered correctly
    entered_value = driver.execute_script("return arguments[0].value;", date_field)
    print(f"Entered date for {field_id}: {entered_value}")
    
    return entered_value == date_value

def extract_lowest_prices(driver):
    """Extract lowest prices for each car category and save to file"""
    print("\nExtracting lowest prices...")
    
    # Dictionary to store category and price pairs
    lowest_prices = {}
    
    # Find all rows (each car category)
    category_rows = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
    
    for row in category_rows:
        try:
            # Get category name from the first div in the row
            category_name = row.find_element(By.CSS_SELECTOR, 'div.inner.text-center.h3-tag-style').text.strip()
            
            # Find the element with lowest price indicator
            lowest_price_element = row.find_element(By.CSS_SELECTOR, 'a.card.car-result-card.lowest-price')
            
            # Extract the price from the data-price attribute
            price = lowest_price_element.get_attribute('data-price')
            
            lowest_prices[category_name] = float(price)
            print(f"Found {category_name}: ${price}")
            
        except Exception as e:
            continue  # Skip if any element is not found in this row
    
    # Save to file
    with open('rental_prices.txt', 'a') as f:
        f.write(f"\nPrices as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for category, price in lowest_prices.items():
            f.write(f"{category}: ${price:.2f}\n")
    
    print(f"Prices saved to rental_prices.txt")
    return lowest_prices

def check_costco_prices():
    driver = setup_driver()
    try:
        print("Navigating to Costco Travel...")
        driver.get("https://www.costcotravel.com/Rental-Cars")
        time.sleep(random.uniform(2, 4))
        
        # Simulate some random mouse movements
        for _ in range(3):
            random_mouse_movement(driver)
            time.sleep(random.uniform(0.5, 1.5))
        
        # Location input with human-like behavior
        pickup_location_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "pickupLocationTextWidget"))
        )
        pickup_location_element.click()
        time.sleep(random.uniform(0.5, 1))
        human_like_typing(pickup_location_element, "KOA")
        time.sleep(random.uniform(1.5, 2.5))
        
        # Select from dropdown
        dropdown_item = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(text(), 'KOA') and contains(text(), 'Kailua')]"))
        )
        time.sleep(random.uniform(0.5, 1))
        dropdown_item.click()
        time.sleep(random.uniform(1, 2))
        
        # Enhanced date entry
        pickup_date = "04/03/2025"
        dropoff_date = "04/10/2025"
        
        # Try entering dates with verification and retry
        max_retries = 3
        for _ in range(max_retries):
            pickup_success = enter_date(driver, "pickUpDateWidget", pickup_date)
            dropoff_success = enter_date(driver, "dropOffDateWidget", dropoff_date)
            
            if pickup_success and dropoff_success:
                print("Dates entered successfully!")
                break
            else:
                print("Date entry failed, retrying...")
                time.sleep(1)
        
        # Times input with human-like delays
        pickup_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickupTimeWidget"))
        )
        Select(pickup_time).select_by_value("12:00 PM")
        time.sleep(random.uniform(0.5, 1))
        
        dropoff_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropoffTimeWidget"))
        )
        Select(dropoff_time).select_by_value("12:00 PM")
        time.sleep(random.uniform(0.5, 1))
        
        # Age checkbox
        age_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "driversAgeWidget"))
        )
        if not age_checkbox.is_selected():
            time.sleep(random.uniform(0.5, 1))
            driver.execute_script("arguments[0].click();", age_checkbox)
            time.sleep(random.uniform(0.5, 1))
        
        # More random mouse movements before search
        for _ in range(2):
            random_mouse_movement(driver)
            time.sleep(random.uniform(0.3, 0.7))
        
        # Verify all fields before search
        print("\nVerifying fields before search:")
        pickup_date_value = driver.execute_script("return document.getElementById('pickUpDateWidget').value;")
        dropoff_date_value = driver.execute_script("return document.getElementById('dropOffDateWidget').value;")
        print(f"Pickup Date: {pickup_date_value}")
        print(f"Dropoff Date: {dropoff_date_value}")
        print(f"Pickup Time: {Select(pickup_time).first_selected_option.text}")
        print(f"Dropoff Time: {Select(dropoff_time).first_selected_option.text}")
        
        # Search button click
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "findMyCarButton"))
        )
        
        # Scroll into view and move to element
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
        time.sleep(random.uniform(0.5, 1))
        
        # Click the search button
        search_button.click()
        print("Search button clicked")
        
        # Wait for results with check for different possible states
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
        
        # Wait for results with a longer timeout
        WebDriverWait(driver, 60).until(check_search_progress)
        
        print("Results page reached")
        time.sleep(5)  # Wait for results to fully load
        driver.save_screenshot("final_results.png")
        
        # Extract and save prices
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