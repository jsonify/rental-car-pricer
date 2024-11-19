# driver_setup.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config import (
    CHROME_BINARY_PATH,
    CHROMEDRIVER_PATH,
    USER_AGENT,
    LOG_FILE
)

def setup_driver(headless=False):
    """Configure and return a Chrome WebDriver with stealth settings"""
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_PATH
    
    # Check if running in CI environment
    is_ci = os.environ.get('CI') == 'true'
    
    # Stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Headless mode for CI or when requested
    if is_ci or headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
    
    # Common settings
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument(f'user-agent={USER_AGENT}')

    service = Service(CHROMEDRIVER_PATH, service_log_path=LOG_FILE)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Additional stealth measures
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": USER_AGENT})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver