# Costco Travel Car Rental Price Tracker
A modular Python application that automates checking car rental prices on Costco Travel, using Selenium WebDriver with anti-detection measures.

## Project Structure
The application is split into five Python files:

```
rental-car-pricer/
│
├── config.py           # Configuration settings
├── driver_setup.py     # Selenium WebDriver configuration
├── human_simulation.py # Human-like behavior simulation
├── price_extractor.py  # Price extraction and saving
├── main.py            # Main script orchestration
└── screenshots/        # Directory for saved screenshots
```

## Configuration (config.py)
Contains all configurable parameters and constants:

- Chrome paths
- Search parameters (dates, location, times)
- File paths
- Timeout settings

Key settings to modify:
```python
PICKUP_LOCATION = "KOA"
PICKUP_DATE = "04/03/2025"
DROPOFF_DATE = "04/10/2025"
PICKUP_TIME = "12:00 PM"
DROPOFF_TIME = "12:00 PM"
```

## Components

### Driver Setup (driver_setup.py)
Handles Chrome WebDriver initialization with anti-bot detection measures:
- Stealth settings
- Browser configurations
- User agent spoofing
- WebDriver property removal

### Human Simulation (human_simulation.py)
Provides functions that mimic human behavior:
- Random typing delays
- Mouse movements
- Natural form filling
- Randomized waiting periods

### Price Extractor (price_extractor.py)
Manages price data collection and storage:
- Extracts lowest prices for each car category
- Saves formatted results with timestamps
- Includes location and date information
- Generates aligned, readable output

### Main Script (main.py)
Orchestrates the entire process:
1. Initializes WebDriver
2. Navigates to Costco Travel
3. Fills search form
4. Handles search execution
5. Extracts prices
6. Saves results

## Output Format
Results are saved in 'rental_prices.txt' with the following format:

```
==================================================
Prices as of 2024-11-09 10:30:15
Location: KOA (Kailua-Kona International Airport)
Dates: 04/03/2025 - 04/10/2025
--------------------------------------------------
Economy Car         : $  472.06
Compact Car        : $  485.32
Full-size Car      : $  523.45
Compact SUV        : $  567.89
==================================================
```

## Requirements
- Python 3.x
- Selenium WebDriver
- Google Chrome for Testing
- ChromeDriver matching Chrome version

## Setup Instructions

1. Install Python dependencies:
```bash
pip install selenium
```

2. Download required Chrome components:
- Google Chrome for Testing
- ChromeDriver matching your Chrome version

3. Update paths in config.py:
```python
CHROME_BINARY_PATH = "/path/to/chrome"
CHROMEDRIVER_PATH = "/path/to/chromedriver"
```

4. Create screenshots directory:
```bash
mkdir screenshots
```

## Usage

1. Update search parameters in config.py as needed

2. Run the script:
```bash
python main.py
```

## Features
- Anti-bot detection measures
- Human-like behavior simulation
- Modular, maintainable code structure
- Detailed logging and error handling
- Screenshot capture for debugging
- Formatted price output
- Configurable parameters
- Automatic retries for reliability

## Error Handling
The script includes comprehensive error handling:
- Screenshots on errors
- Detailed error logging
- Retry mechanisms for common failures
- Graceful browser cleanup

## Debugging
- Check selenium.log for WebDriver logs
- Review screenshots in screenshots/ directory
- Monitor console output for progress
- Verify rental_prices.txt for results

## Limitations
- Subject to website changes
- Dependent on network conditions
- May require ChromeDriver updates
- Could be detected as automated

## Best Practices
1. Don't run too frequently to avoid detection
2. Regularly update Chrome and ChromeDriver
3. Monitor for website changes
4. Back up price history regularly
5. Review screenshots for any issues
6. Keep components updated independently

## Maintenance
Regular maintenance tasks:
1. Update Chrome components
2. Check for website changes
3. Verify selector validity
4. Monitor anti-bot measures
5. Review error logs
6. Update configuration as needed

