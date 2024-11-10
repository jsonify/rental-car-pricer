# Costco Travel Car Rental Price Tracker 🚗

An automated tool that tracks rental car prices on Costco Travel, featuring email notifications and focus category tracking. Built with Python and Selenium, this tool helps you monitor price changes and find the best deals for your preferred vehicle type.

## Features ✨

- 🤖 Automated price checking using Selenium WebDriver
- 📧 Email notifications with price updates
- 🎯 Focus category tracking for your preferred vehicle type
- 💰 Cheaper alternatives suggestions
- 📊 Price history tracking
- 🔄 Price change notifications
- 🕒 Configurable search parameters
- 🔒 Secure credential management using environment variables

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
- Configuring search parameters
- Setting up email notifications
- Creating necessary directories

## Configuration ⚙️

The setup script will create a `.env` file with your configuration. You can also manually configure the following:

### Search Parameters:
- Airport location (three-letter code)
- Pickup and dropoff dates
- Focus category (vehicle type to track)
- Pickup and dropoff times

### Email Settings:
- SMTP server details
- Sender email (Gmail)
- App password (for Gmail)
- Recipient email

### Browser Settings:
- Chrome binary path
- ChromeDriver path
- Timeout values

## Usage 🚀

1. Test the email configuration:
```bash
python3 test_email.py
```

2. Run the price checker:
```bash
python3 main.py
```

The script will:
1. Navigate to Costco Travel
2. Enter your search parameters
3. Extract current prices
4. Send an email with:
   - Focus category price and changes
   - Cheaper alternatives
   - Complete price list
   - Price trends (when available)

## Email Notifications 📬

You'll receive emails containing:
- Current prices for all vehicle categories
- Highlighted focus category with price changes
- Cheaper alternatives to your focus category
- Price trends and historical data
- Potential savings opportunities

## Project Structure 📁

```
rental-car-pricer/
│
├── config.py           # Configuration and environment variables
├── driver_setup.py     # Selenium WebDriver configuration
├── email_sender.py     # Email notification handling
├── human_simulation.py # Human-like behavior simulation
├── main.py            # Main script orchestration
├── price_extractor.py # Price extraction and analysis
├── price_history.py   # Historical price tracking
├── setup.py           # Project setup and configuration
├── test_email.py      # Email configuration testing
│
├── screenshots/        # Directory for debug screenshots
└── .env               # Environment variables (created by setup.py)
```

## Price History Setup

To initialize price tracking:
1. Copy `price_history.template.json` to `price_history.json`
2. The script will automatically update the history file with new prices

Note: `price_history.json` is not tracked in the repository to avoid conflicts and keep your price history private.

## Gmail Setup 📨

To use Gmail for notifications:

1. Enable 2-Step Verification on your Google Account
2. Generate an App Password:
   - Go to Google Account settings
   - Search for "App Passwords"
   - Select "Mail" and your device
   - Use the generated password in your configuration

## Troubleshooting 🔍

### Common Issues:

1. **ChromeDriver Version Mismatch**:
   - Ensure ChromeDriver version matches your Chrome version
   - Download the correct version from the official site

2. **Email Authentication Errors**:
   - Verify your Gmail App Password is correct
   - Ensure 2-Step Verification is enabled

3. **Selenium Errors**:
   - Check Chrome and ChromeDriver paths in `.env`
   - Verify the browser is not being controlled by another instance

### Debug Tools:

- Check `selenium.log` for WebDriver logs
- Review screenshots in `screenshots/` directory
- Verify `rental_prices.txt` for price history

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Security Notes 🔐

- Never commit your `.env` file
- Keep your Gmail App Password secure
- Don't share your configuration files

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Selenium WebDriver
- Python community
- Costco Travel

## Disclaimer ⚠️

This tool is for personal use only. Be mindful of Costco Travel's terms of service and use the tool responsibly.