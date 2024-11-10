# setup.py

import os
import sys
import shutil
import platform
import subprocess
import json
from pathlib import Path
import webbrowser
from datetime import datetime, timedelta

def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"{text:^60}")
    print('=' * 60)

def print_step(text):
    print(f"\n➜ {text}")

def check_python_version():
    print_step("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Using Python {version.major}.{version.minor}.{version.micro}")

def check_pip_packages():
    print_step("Checking required Python packages...")
    required_packages = [
        'selenium',
        'python-dotenv'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} has been installed")

def find_chrome_and_driver():
    print_step("Locating Chrome for Testing and ChromeDriver...")
    system = platform.system()
    chrome_path = None
    chromedriver_path = None
    
    if system == 'Darwin':  # macOS
        default_paths = [
            '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
            str(Path.home() / 'Downloads/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
            str(Path.home() / 'Downloads/chromedriver-mac-x64/chromedriver')
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                if 'chromedriver' in path:
                    chromedriver_path = path
                else:
                    chrome_path = path
    
    return chrome_path, chromedriver_path

def check_chrome_installation():
    print_step("Checking Chrome for Testing installation...")
    chrome_path, chromedriver_path = find_chrome_and_driver()
    
    if not chrome_path or not chromedriver_path:
        print("❌ Chrome for Testing and/or ChromeDriver not found in default locations")
        print("\nPlease download them from:")
        print("Chrome for Testing: https://googlechromelabs.github.io/chrome-for-testing/")
        print("ChromeDriver: https://chromedriver.chromium.org/downloads")
        
        open_download = input("\nWould you like to open the download page? (y/n): ")
        if open_download.lower() == 'y':
            webbrowser.open('https://googlechromelabs.github.io/chrome-for-testing/')
        
        chrome_path = input("\nEnter the path to Chrome for Testing binary: ").strip()
        chromedriver_path = input("Enter the path to ChromeDriver: ").strip()
        
        if not os.path.exists(chrome_path) or not os.path.exists(chromedriver_path):
            print("❌ Invalid paths provided")
            sys.exit(1)
    
    print("✅ Chrome for Testing found")
    print("✅ ChromeDriver found")
    return chrome_path, chromedriver_path

def check_existing_files():
    """Check for existing configuration files and return their status"""
    return {
        "env": os.path.exists(".env"),
        "price_history": os.path.exists("price_history.json"),
        "price_template": os.path.exists("price_history.template.json"),
        "screenshots_dir": os.path.exists("screenshots")
    }

def check_first_run():
    """Check if this is the first time running the project"""
    existing_files = check_existing_files()
    
    print_step("Checking existing configuration...")
    print("\nFound these configuration items:")
    print(f"- .env file: {'✅' if existing_files['env'] else '❌'}")
    print(f"- price_history.json: {'✅' if existing_files['price_history'] else '❌'}")
    print(f"- price_history.template.json: {'✅' if existing_files['price_template'] else '❌'}")
    print(f"- screenshots directory: {'✅' if existing_files['screenshots_dir'] else '❌'}")
    
    if any(existing_files.values()):
        print("\nSome configuration files already exist.")
        choice = input("\nWould you like to:\n"
                      "1. Start fresh (backup existing files)\n"
                      "2. Keep existing files and only create missing ones\n"
                      "Choose (1/2): ").strip()
        
        if choice == "1":
            # Create backups directory if it doesn't exist
            backup_dir = "setup_backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Backup existing files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if existing_files['env']:
                shutil.copy2(".env", f"{backup_dir}/.env.backup.{timestamp}")
            if existing_files['price_history']:
                shutil.copy2("price_history.json", f"{backup_dir}/price_history.json.backup.{timestamp}")
            if existing_files['price_template']:
                shutil.copy2("price_history.template.json", f"{backup_dir}/price_history.template.json.backup.{timestamp}")
            
            print(f"\nExisting files backed up to {backup_dir}/")
            return "true"
        else:
            return "partial"
    
    return "true"

def get_valid_date(prompt, default_date=None):
    while True:
        if default_date:
            date_input = input(f"{prompt} (default: {default_date.strftime('%m/%d/%Y')}): ").strip()
            if not date_input:
                return default_date.strftime("%m/%d/%Y")
        else:
            date_input = input(prompt).strip()
        
        try:
            # Try to parse the date to validate it
            datetime.strptime(date_input, "%m/%d/%Y")
            return date_input
        except ValueError:
            print("❌ Invalid date format. Please use MM/DD/YYYY format.")

def get_airport_code():
    print_step("Configuring airport location...")
    
    while True:
        airport_code = input("\nEnter the three-letter airport code (e.g., KOA for Kona): ").strip().upper()
        if len(airport_code) == 3 and airport_code.isalpha():
            confirmation = input(f"Is {airport_code} the correct airport code? (y/n): ")
            if confirmation.lower() == 'y':
                return airport_code
        else:
            print("❌ Invalid airport code. Please enter a three-letter code.")

def get_focus_category():
    print_step("Selecting focus category for price tracking")
    
    categories = [
        "Economy Car",
        "Compact Car",
        "Mid-size Car",
        "Full-size Car",
        "Premium Car",
        "Luxury Car",
        "Compact SUV",
        "Standard SUV",
        "Full-size SUV",
        "Premium SUV",
        "Minivan"
    ]
    
    print("\nAvailable car categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of your preferred category: "))
            if 1 <= choice <= len(categories):
                category = categories[choice-1]
                confirmation = input(f"\nConfirm tracking {category}? (y/n): ")
                if confirmation.lower() == 'y':
                    return category
        except ValueError:
            pass
        print("Please enter a valid category number.")

def configure_search_parameters():
    print_step("Configuring search parameters...")
    
    # Get airport code
    airport_code = get_airport_code()
    
    # Calculate default dates (3 months from now)
    default_pickup = datetime.now() + timedelta(days=90)
    default_dropoff = default_pickup + timedelta(days=7)
    
    print("\nEnter search dates (MM/DD/YYYY format)")
    print("Default is 3 months from today + 7 days rental period")
    
    # Get pickup and dropoff dates
    pickup_date = get_valid_date("\nPickup date", default_pickup)
    dropoff_date = get_valid_date("Dropoff date", default_dropoff)
    
    # Get focus category
    focus_category = get_focus_category()
    
    return airport_code, pickup_date, dropoff_date, focus_category

def setup_gmail_instructions():
    print_step("Gmail App Password Setup Instructions")
    print("""
To use Gmail for sending alerts, you'll need to:
1. Enable 2-Step Verification on your Google Account
2. Generate an App Password:
   a. Go to your Google Account settings
   b. Search for "App Passwords"
   c. Select "Mail" and your device
   d. Copy the generated password
   
Would you like to open the Google App Passwords page?""")
    
    open_google = input("Open Google App Passwords page? (y/n): ")
    if open_google.lower() == 'y':
        webbrowser.open('https://myaccount.google.com/apppasswords')

def configure_email_settings():
    print_step("Configuring email settings...")
    
    sender_email = input("\nEnter Gmail address for sending alerts: ").strip()
    setup_gmail_instructions()
    app_password = input("\nEnter the generated App Password: ").strip()
    recipient_email = input("Enter recipient email address: ").strip()
    
    return sender_email, app_password, recipient_email

class PriceHistoryInitializer:
    def __init__(self, airport_code, pickup_date, dropoff_date, pickup_time="12:00 PM", dropoff_time="12:00 PM"):
        self.airport_code = airport_code
        self.pickup_date = pickup_date
        self.dropoff_date = dropoff_date
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        self.template_path = "price_history.template.json"
        self.history_path = "price_history.json"

    def create_initial_structure(self):
        """Create the initial price history structure."""
        current_time = datetime.now().isoformat(timespec='seconds')
        
        # Calculate duration
        pickup = datetime.strptime(self.pickup_date, "%m/%d/%Y")
        dropoff = datetime.strptime(self.dropoff_date, "%m/%d/%Y")
        duration = (dropoff - pickup).days
        
        return {
            "metadata": {
                "last_updated": current_time,
                "location": self.airport_code,
                "location_full_name": f"{self.airport_code} (Kailua-Kona International Airport)",
                "search_parameters": {
                    "pickup_time": self.pickup_time,
                    "dropoff_time": self.dropoff_time,
                    "duration_days": duration
                }
            },
            "price_records": [],
            "category_stats": {
                category: {
                    "min_price": None,
                    "max_price": None,
                    "avg_price": None,
                    "last_price": None,
                    "price_changes": []
                } for category in [
                    "Economy Car",
                    "Compact Car",
                    "Mid-size Car",
                    "Full-size Car",
                    "Premium Car",
                    "Luxury Car",
                    "Compact SUV",
                    "Standard SUV",
                    "Full-size SUV",
                    "Premium SUV",
                    "Minivan"
                ]
            }
        }

    def initialize(self):
        """Initialize both template and working files."""
        print_step("Setting up price history tracking...")
        
        initial_data = self.create_initial_structure()
        
        # Save template file
        with open(self.template_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
        print("✅ Created price history template file")
        
        # Create working file
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
        print("✅ Created price history working file")

def setup_env_file(chrome_path, chromedriver_path, airport_code, pickup_date, dropoff_date, 
                  is_first_run, focus_category, sender_email, app_password, recipient_email):
    print_step("Setting up .env file...")
    
    env_content = f"""# Project Configuration
IS_FIRST_RUN={is_first_run}

# Browser Configuration
CHROME_BINARY_PATH={chrome_path}
CHROMEDRIVER_PATH={chromedriver_path}
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={app_password}
RECIPIENT_EMAIL={recipient_email}

# Search Parameters
PICKUP_LOCATION={airport_code}
PICKUP_DATE={pickup_date}
DROPOFF_DATE={dropoff_date}
PICKUP_TIME=12:00 PM
DROPOFF_TIME=12:00 PM
FOCUS_CATEGORY={focus_category}

# File Paths
LOG_FILE=selenium.log
PRICES_FILE=rental_prices.txt
SCREENSHOT_PATH=screenshots/

# Timeouts (in seconds)
PAGE_LOAD_TIMEOUT=60
ELEMENT_TIMEOUT=10
SEARCH_TIMEOUT=60
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file")

def create_directories():
    print_step("Creating required directories...")
    
    directories = ['screenshots', 'setup_backups']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/ directory")
        else:
            print(f"✅ {directory}/ directory already exists")

def main():
    print_header("Costco Travel Car Rental Price Tracker Setup")
    
    # Check Python version
    check_python_version()
    
    # Check and install required packages
    check_pip_packages()
    
    # Check first run status
    setup_mode = check_first_run()
    
    # Check Chrome installation
    chrome_path, chromedriver_path = check_chrome_installation()
    
    # Configure search parameters
    airport_code, pickup_date, dropoff_date, focus_category = configure_search_parameters()
    
    # Configure email settings
    sender_email, app_password, recipient_email = configure_email_settings()
    
    # Initialize price history based on setup mode
    try:
        initializer = PriceHistoryInitializer(
            airport_code=airport_code,
            pickup_date=pickup_date,
            dropoff_date=dropoff_date
        )
        
        if setup_mode == "true":
            # Full initialization
            initializer.initialize()
        elif setup_mode == "partial":
            # Only create files that don't exist
            if not os.path.exists("price_history.template.json"):
                with open("price_history.template.json", 'w', encoding='utf-8') as f:
                    json.dump(initializer.create_initial_structure(), f, indent=2)
                print("✅ Created price history template file")
            
            if not os.path.exists("price_history.json"):
                with open("price_history.json", 'w', encoding='utf-8') as f:
                    json.dump(initializer.create_initial_structure(), f, indent=2)
                print("✅ Created price history working file")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not initialize price history: {str(e)}")
        print("You may need to manually set up price history tracking later.")
    
    # Create .env file
    setup_env_file(
        chrome_path, chromedriver_path, 
        airport_code, pickup_date, dropoff_date,
        setup_mode, focus_category,
        sender_email, app_password, recipient_email
    )
    
    # Create required directories
    create_directories()
    
    print_header("Setup Complete!")
    print(f"""
Configuration Summary:
- Airport: {airport_code}
- Pickup Date: {pickup_date}
- Dropoff Date: {dropoff_date}
- Focus Category: {focus_category}
- Pickup/Dropoff Time: 12:00 PM
- Price History Tracking: {"Initialized" if setup_mode == "true" else "Skipped"}

Files Created:
- .env with your configuration
- price_history.template.json (template file)
- price_history.json (working file)
- screenshots/ directory

Next steps:
1. Review the .env file and adjust any settings if needed
2. Run the email test script:
   python test_email.py
3. If the test is successful, you can run the main script:
   python main.py

Note: The price history files have been initialized with your current search
parameters. The script will automatically update the history as it runs.
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred during setup: {str(e)}")
        sys.exit(1)