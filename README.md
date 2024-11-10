# Costco Travel Car Rental Price Tracker 🚗

An automated tool that tracks rental car prices on Costco Travel, featuring email notifications, price history tracking, and focus category monitoring. Built with Python and Selenium, this tool helps you monitor price changes and find the best deals for your preferred vehicle type.

## Features ✨

- 🤖 Automated price checking using Selenium WebDriver
- 📧 Email notifications with price updates
- 📊 Price history tracking with JSON storage
- 🎯 Focus category tracking for your preferred vehicle type
- 💰 Cheaper alternatives suggestions
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
- Initializing price history tracking
- Creating necessary directories

## Configuration ⚙️

The setup script will help you configure:

### Search Parameters:

- Airport location (three-letter code)
- Pickup and dropoff dates
- Focus category (vehicle type to track)
- Pickup and dropoff times

### Email Settings:

- SMTP server details (Gmail)
- Sender email
- App password (for Gmail)
- Recipient email

### Browser Settings:

- Chrome binary path
- ChromeDriver path
- Timeout values

## File Structure 📁

```
rental-car-pricer/
│
├── config.py           # Configuration and environment variables
├── driver_setup.py     # Selenium WebDriver configuration
├── email_sender.py     # Email notification handling
├── human_simulation.py # Human-like behavior simulation
├── main.py            # Main script orchestration
├── price_extractor.py # Price extraction and analysis
├── setup.py           # Project setup and configuration
├── test_email.py      # Email configuration testing
│
├── price_history.json        # Working price history file
├── price_history.template.json # Template for price history
│
├── screenshots/        # Directory for debug screenshots
├── setup_backups/      # Directory for configuration backups
└── .env               # Environment variables
```

## Usage 🚀

### Initial Setup 🎯

1. Run the setup script:

```bash
python3 setup.py
```

The setup script guides you through:

- Verifying Python (3.7+) and required packages
- Setting up Chrome and ChromeDriver paths
- Configuring your search parameters
- Setting up email notifications
- Initializing price history tracking
- Creating necessary directories and files

### Setup Options 🔄

When running setup.py, you'll have two main options:

1. **Start Fresh** (Option 1):

   - Backs up all existing configuration files
   - Creates new .env file
   - Reinitializes price history
   - Resets all settings

   ```bash
   # Example backup created:
   setup_backups/
   ├── .env.backup.20241109_161200
   ├── price_history.json.backup.20241109_161200
   └── price_history.template.json.backup.20241109_161200
   ```

2. **Update Existing** (Option 2):
   - Keeps existing configuration
   - Only creates missing files
   - Preserves price history
   - Allows selective updates

### Configuration Examples 📝

1. **Basic Hawaii Setup**:

```
Airport: KOA
Pickup Date: 04/03/2025
Dropoff Date: 04/10/2025
Focus Category: Economy Car
Email: your.email@gmail.com
```

2. **Extended SUV Rental**:

```
Airport: OGG
Pickup Date: 05/15/2025
Dropoff Date: 05/30/2025
Focus Category: Standard SUV
Email: your.email@gmail.com
```

3. **Short-term Premium**:

```
Airport: HNL
Pickup Date: 03/20/2025
Dropoff Date: 03/23/2025
Focus Category: Premium Car
Email: your.email@gmail.com
```

### Setup Troubleshooting 🔧

1. **Chrome/ChromeDriver Issues**:

   ```
   ❌ Chrome for Testing and/or ChromeDriver not found
   ```

   Solution:

   - Download Chrome for Testing from provided link
   - Ensure ChromeDriver matches Chrome version
   - Enter full paths when prompted

   ```bash
   # Example paths:
   /Users/username/Downloads/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing
   /Users/username/Downloads/chromedriver-mac-x64/chromedriver
   ```

2. **Permission Issues**:

   ```
   ❌ Permission denied: '.env'
   ```

   Solution:

   ```bash
   # Check file permissions
   ls -la
   # Fix permissions if needed
   chmod 644 .env
   ```

3. **Python Package Issues**:

   ```
   ❌ selenium is missing
   ```

   Solution:

   ```bash
   pip3 install selenium python-dotenv
   # or
   pip3 install -r requirements.txt
   ```

4. **Price History Initialization Fails**:
   ```
   ⚠️ Warning: Could not initialize price history
   ```
   Solution:
   ```bash
   # Remove existing files and try again
   rm price_history.json price_history.template.json
   python3 setup.py
   ```

### Daily Usage 📅

After setup is complete:

1. Test email configuration:

```bash
python3 test_email.py
```

2. Run price checker:

```bash
python3 main.py
```

### Updating Configuration ⚙️

To modify your setup:

1. **Complete Reset**:

```bash
python3 setup.py
# Choose Option 1: Start fresh
```

2. **Partial Update**:

```bash
python3 setup.py
# Choose Option 2: Keep existing files
```

3. **Manual Updates**:

- Edit .env file directly for minor changes
- Run setup.py for major changes

### Best Practices 🌟

1. **Before First Run**:

   - Download latest Chrome for Testing
   - Set up Gmail App Password
   - Check Python version
   - Clear any old config files

2. **Regular Maintenance**:

   - Keep Chrome and ChromeDriver updated
   - Monitor price_history.json file size
   - Check setup_backups directory periodically
   - Review email notifications settings

3. **Troubleshooting Workflow**:
   - Check selenium.log first
   - Review screenshots directory
   - Verify price_history.json structure
   - Test email configuration separately

## Price History Tracking 📈

The tool maintains a detailed price history in JSON format, tracking:

- Historical prices for all vehicle categories
- Price trends and changes
- Minimum, maximum, and average prices
- Focus category performance

The history file is excluded from version control to keep your price data private. A template file is provided for reference.

## Email Notifications 📬

You'll receive emails containing:

- Current prices for all vehicle categories
- Highlighted focus category with price changes
- Cheaper alternatives to your focus category
- Price trends and historical data
- Potential savings opportunities

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

3. **Price History Issues**:
   - Run setup.py with option 1 to start fresh
   - Check file permissions in the project directory

### Debug Tools:

- Check `selenium.log` for WebDriver logs
- Review screenshots in `screenshots/` directory
- Verify `price_history.json` for tracking data

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Security Notes 🔐

- Never commit your `.env` file
- Keep your Gmail App Password secure
- Don't share your configuration files
- Price history files contain personal search data

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚠️

This tool is for personal use only. Be mindful of Costco Travel's terms of service and use the tool responsibly.
