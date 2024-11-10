from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config import (
    CHROME_BINARY_PATH,
    CHROMEDRIVER_PATH,
    USER_AGENT,
    LOG_FILE
)

def setup_headless_driver():
    """Configure and return a headless Chrome WebDriver with stealth settings"""
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_PATH
    
    # Headless settings
    chrome_options.add_argument('--headless=new')  # New headless mode for Chrome
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Window size is still important in headless mode for proper rendering
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument(f'user-agent={USER_AGENT}')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Additional headless optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-setuid-sandbox')
    
    service = Service(CHROMEDRIVER_PATH, service_log_path=LOG_FILE)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Additional stealth measures
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": USER_AGENT})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def setup_visible_driver():
    """Configure and return a visible Chrome WebDriver with stealth settings"""
    chrome_options = Options()
    chrome_options.binary_location = CHROME_BINARY_PATH
    
    # Stealth settings
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Browser settings
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={USER_AGENT}')

    service = Service(CHROMEDRIVER_PATH, service_log_path=LOG_FILE)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Additional stealth measures
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": USER_AGENT})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver