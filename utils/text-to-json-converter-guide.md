# Text to JSON Converter Utility Guide

## Purpose
This utility converts a formatted text file containing car rental price checks into a structured JSON format that's compatible with the Car Rental Price Tracker system. It's particularly useful when you need to manually import price check data or convert historical price records.

## Usage
```bash
python3 text_to_json_converter.py <input_file>
```

The script will automatically create an output JSON file with the same name as your input file (e.g., `prices.txt` → `prices.json`).

## Input Format Requirements
The input text file must follow this specific format:

```text
Last checked: 2024-11-19 08:51:03

LIH - Lihue Airport
📅 04/03/2025 to 04/10/2025
⏰ 12:00 PM - 12:00 PM

Tracked Category
Full-size Car

💰 Holding Price: $469.70

All Categories:
Economy Car
$517.19
Compact Car
$491.40
Intermediate Car
$489.79
Full-size Car
$512.07
Premium Car
$589.54

KOA - Kailua-Kona International Airport
📅 04/10/2025 to 04/14/2025
...
```

### Key Format Requirements:
1. Must start with "Last checked:" timestamp
2. Each booking section must start with airport code (e.g., "LIH - ", "KOA - ")
3. Dates must use the format: 📅 MM/DD/YYYY to MM/DD/YYYY
4. Categories and prices must be listed under "All Categories:"
5. Prices must start with $ and be on their own line
6. Optional holding price can be specified with "💰 Holding Price: $XXX.XX"

## Output Format
The script generates a JSON file structured like this:

```json
{
  "metadata": {
    "last_updated": "2024-11-19T08:51:03",
    "active_bookings": ["LIH_04032025_04102025", "KOA_04102025_04142025"]
  },
  "bookings": {
    "LIH_04032025_04102025": {
      "location": "LIH",
      "location_full_name": "Lihue Airport",
      "pickup_date": "04/03/2025",
      "dropoff_date": "04/10/2025",
      "pickup_time": "12:00 PM",
      "dropoff_time": "12:00 PM",
      "focus_category": "Full-size Car",
      "holding_price": 469.70,
      "price_history": [
        {
          "timestamp": "2024-11-19T08:51:03",
          "prices": {
            "Economy Car": 517.19,
            "Compact Car": 491.40
          },
          "lowest_price": {
            "category": "Intermediate Car",
            "price": 489.79
          }
        }
      ],
      "created_at": "2024-11-19T08:51:03"
    }
  }
}
```

## Example Usage

1. Create a text file `prices.txt`:
```text
Last checked: 2024-11-19 08:51:03

LIH - Lihue Airport
📅 04/03/2025 to 04/10/2025
⏰ 12:00 PM - 12:00 PM

Tracked Category
Full-size Car

💰 Holding Price: $469.70

All Categories:
Economy Car
$517.19
Compact Car
$491.40
Full-size Car
$512.07
```

2. Run the converter:
```bash
python3 text_to_json_converter.py prices.txt
```

3. The script will create `prices.json` with the structured data.

## Features and Error Handling

### Debugging Features
- Provides detailed progress output during conversion
- Shows parsed categories and sample prices for verification
- Reports any errors encountered during parsing
- Provides a summary of converted bookings at the end

### Error Handling
- Validates required fields and format
- Skips invalid sections while continuing to process others
- Reports specific parsing errors for troubleshooting
- Creates backup of existing files before overwriting

## Best Practices and Tips

1. Format Verification
   - Double-check input format matches requirements exactly
   - Ensure all required sections are present
   - Verify timestamps and dates use correct format

2. Data Management
   - Keep backup copies of important price history files
   - Verify the generated JSON in a text editor after conversion
   - Use the script's verbose output to identify parsing issues

3. Common Use Cases
   - Importing historical price data into the tracking system
   - Converting manually collected price information
   - Restoring price history from text backups
   - Merging multiple price check records

## Troubleshooting

If you encounter issues:

1. Check the timestamp format matches exactly: "YYYY-MM-DD HH:MM:SS"
2. Verify each booking section starts with a location line
3. Ensure prices are on separate lines and start with $
4. Check for any missing or extra blank lines
5. Verify emoji usage matches the template exactly

## Additional Notes

- The script maintains the original timestamp from the input file
- Automatically calculates booking IDs from location and dates
- Preserves any existing holding prices
- Identifies and tracks the focus category for each booking
- Calculates lowest price information automatically
