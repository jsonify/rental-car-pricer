# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Search parameters (defaults used when running standalone)
PICKUP_LOCATION = os.getenv('PICKUP_LOCATION', 'KOA')
PICKUP_DATE = os.getenv('PICKUP_DATE', '04/03/2025')
DROPOFF_DATE = os.getenv('DROPOFF_DATE', '04/10/2025')
PICKUP_TIME = os.getenv('PICKUP_TIME', '12:00 PM')
DROPOFF_TIME = os.getenv('DROPOFF_TIME', '12:00 PM')
FOCUS_CATEGORY = os.getenv('FOCUS_CATEGORY', 'Economy Car')

# File paths
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
