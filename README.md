# Costco Travel Car Rental Price Tracker 🚗

An automated tool that tracks rental car prices on Costco Travel, featuring email notifications, focus category tracking, and support for multiple bookings. Built with Python and Selenium, this tool helps you monitor price changes and find the best deals for your preferred vehicle types across multiple rentals.

## Features ✨

- 🤖 Automated price checking using Selenium WebDriver
- 📧 Consolidated email notifications for all tracked bookings
- 🎯 Focus category tracking for each booking
- 💰 Cheaper alternatives suggestions per booking
- 📊 Price history tracking with JSON storage
- 🔄 Price change notifications with trends
- 🕒 Configurable search parameters
- 🔒 Secure credential management using environment variables
- 📚 Multiple bookings support
- 🖼️ Screenshot capture for verification

## Prerequisites 📋

Before you begin, ensure you have the following installed:

- Python 3.7 or higher
- Google Chrome for Testing
- ChromeDriver (matching your Chrome version)
- pip (Python package installer)

## Installation 🔧

1. Clone the repository:

```bash
git clone https://github.com/yourusername/costco-car-rental-tracker.git
cd costco-car-rental-tracker
```

2. Install required Python packages:

```bash
pip3 install selenium python-dotenv
```

3. Download required Chrome components:

   - [Google Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
   - [ChromeDriver](https://chromedriver.chromium.org/downloads) (make sure it matches your Chrome version)

4. Run the setup script:

```bash
python3 setup.py
```

The setup script will guide you through:

- Validating your Python environment
- Locating Chrome and ChromeDriver
- Configuring your first booking
- Setting up email notifications
- Creating necessary directories

## Usage 🚀

### Initial Setup

When you first run `setup.py`, you'll be guided through creating your first booking:

```bash
python3 setup.py

Costco Travel Car Rental Price Tracker Setup
==============================================
Let's set up your first car rental booking to track...

Enter the three-letter airport code (e.g., KOA for Kona): LIH
Enter pickup date (MM/DD/YYYY): 04/03/2025
Enter dropoff date (MM/DD/YYYY): 04/10/2025
Select your preferred category (1-11): 4

✅ First booking created successfully!
📍 Location: LIH
📅 Dates: 04/03/2025 to 04/10/2025
🚗 Category: Full-size Car
```

### Managing Bookings

Run the main script to check prices or add new bookings:

```bash
python3 main.py

🚗 Costco Travel Car Rental Price Tracker
==================================================
📋 Current active bookings:

1. 📍 LIH
   📅 04/03/2025 - 04/10/2025
   🎯 Focus: Full-size Car

🔄 Choose an action:
1. Track current bookings only
2. Add a new booking
```

### Adding More Bookings

Select option 2 when running main.py to add additional bookings:

```bash
Choice: 2

📝 Enter new booking information:

Enter airport code (e.g., KOA): KOA
Enter pickup date (MM/DD/YYYY): 05/15/2025
Enter dropoff date (MM/DD/YYYY): 05/22/2025
Select category number: 7

✅ Added new booking: KOA
```

### Tracking Multiple Bookings

When you run the script to check prices (option 1):

- Processes all active bookings sequentially
- Takes screenshots of results for each booking
- Updates price history for each booking
- Sends a single consolidated email with all results

### Email Notifications 📬

You'll receive a single email containing:

- Price updates for all tracked bookings
- Focus category prices and trends for each booking
- Cheaper alternatives for each booking
- Historical price data when available
- Price change alerts

Example email format:

```
🚗 Costco Travel Car Rental Price Update
==================================================
Last checked: 2024-11-10 00:15:23
Total bookings tracked: 2
==================================================

📍 LIH - Lihue Airport
📅 04/03/2025 to 04/10/2025
⏰ 12:00 PM - 12:00 PM
--------------------------------------------------

🎯 TRACKED: Full-size Car
Current Price: $282.16 🔽 -$5.83 (-2.1%)
Historical Range: $282.16 - $295.99
Average Price: $289.08

💰 CHEAPER ALTERNATIVES:
- Economy Car: $275.42 (Save $6.74)
- Compact Car: $278.99 (Save $3.17)

📊 ALL CATEGORIES:
[Price list for LIH]
==================================================

📍 KOA - Kailua-Kona International Airport
[Details for second booking...]
==================================================
```

## Price History Tracking 📈

The tool maintains a JSON file (`price_history.json`) containing:

- Historical prices for all bookings
- Price trends per booking
- Focus category performance
- Booking metadata

## Troubleshooting 🔍

### Common Issues:

1. **ChromeDriver Version Mismatch**:

```bash
# Check Chrome version
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Download matching ChromeDriver
```

2. **Location Selection Issues**:

```
❌ Error: Could not find exact location match
⚠️ Trying partial match...
✅ Location selected successfully
```

### Debug Tools:

- Check `selenium.log` for WebDriver logs
- Review screenshots in `screenshots/` directory:
  - `results_[LOCATION]_[TIMESTAMP].png` for successful searches
  - `error_[LOCATION]_[TIMESTAMP].png` for failed attempts
- Verify `price_history.json` for tracking data

## Maintenance 🛠️

Regular maintenance tasks:

1. Keep Chrome and ChromeDriver versions in sync
2. Monitor price_history.json file size
3. Review screenshot directory periodically
4. Update Gmail App Password if needed

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Security Notes 🔐

- Never commit your `.env` file
- Keep your Gmail App Password secure
- Don't share your price history files
- Regularly review app permissions

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚠️

This tool is for personal use only. Be mindful of Costco Travel's terms of service and use the tool responsibly.
