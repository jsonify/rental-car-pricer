# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Browser Configuration
CHROME_BINARY_PATH = os.getenv('CHROME_BINARY_PATH')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
USER_AGENT = os.getenv('USER_AGENT')

# Search parameters
PICKUP_LOCATION = os.getenv('PICKUP_LOCATION', 'KOA')
PICKUP_DATE = os.getenv('PICKUP_DATE', '04/03/2025')
DROPOFF_DATE = os.getenv('DROPOFF_DATE', '04/10/2025')
PICKUP_TIME = os.getenv('PICKUP_TIME', '12:00 PM')
DROPOFF_TIME = os.getenv('DROPOFF_TIME', '12:00 PM')
FOCUS_CATEGORY = os.getenv('FOCUS_CATEGORY', 'Economy Car')  # Added this line

# File paths
LOG_FILE = os.getenv('LOG_FILE', 'selenium.log')
PRICES_FILE = os.getenv('PRICES_FILE', 'rental_prices.txt')
SCREENSHOT_PATH = os.getenv('SCREENSHOT_PATH', 'screenshots/')

# Timeouts
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '60'))
ELEMENT_TIMEOUT = int(os.getenv('ELEMENT_TIMEOUT', '10'))
SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', '60'))

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Project Configuration
IS_FIRST_RUN = os.getenv('IS_FIRST_RUN', 'true').lower() == 'true'

# Validate required environment variables
required_env_vars = [
    'CHROME_BINARY_PATH',
    'CHROMEDRIVER_PATH',
    'SENDER_EMAIL',
    'SENDER_PASSWORD',
    'RECIPIENT_EMAIL',
    'FOCUS_CATEGORY'  # Added this line
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}\n"
        "Please check your .env file or environment settings."
    )

# Validate file paths
def validate_file_paths():
    # Validate Chrome binary
    if not os.path.exists(CHROME_BINARY_PATH):
        raise FileNotFoundError(f"Chrome binary not found at: {CHROME_BINARY_PATH}")
    
    # Validate ChromeDriver
    if not os.path.exists(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")
    
    # Ensure screenshot directory exists
    if not os.path.exists(SCREENSHOT_PATH):
        os.makedirs(SCREENSHOT_PATH)
        print(f"Created screenshot directory at: {SCREENSHOT_PATH}")

# Run validation on import
validate_file_paths()