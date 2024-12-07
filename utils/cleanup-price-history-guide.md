# Price History Cleanup Utility Guide

## Purpose
The cleanup utility (`cleanup_price_history.py`) helps maintain your price history database by cleaning up old price records. It keeps only one entry from a specified date (11/10/2024) and all subsequent entries, removing older data to prevent database bloat.

## Usage
```bash
python3 cleanup_price_history.py
```

The script operates on `price_history.json` by default.

## Features

### Automatic Backup
- Creates a timestamped backup before cleaning: `price_history.backup.YYYYMMDD_HHMMSS.json`
- Restores from backup automatically if an error occurs

### Data Cleaning
- Keeps one price entry from 11/10/2024
- Retains all entries after 11/10/2024
- Cleans both `price_records` and `price_history` sections
- Updates the `last_updated` timestamp in metadata

### Smart Timestamp Parsing
Handles multiple timestamp formats:
- ISO format (e.g., "2024-11-10T00:10:18.345155")
- MM/DD HH:MM format
- YYYY-MM-DD HH:MM:SS format

## Output Example
```
✅ Created backup: price_history.backup.20241119_085103.json

Processing booking: LIH_04032025_04102025
Price records: 10 → 4
Price history: 10 → 4

Processing booking: KOA_04102025_04142025
Price records: 8 → 3
Price history: 8 → 3

Cleanup Summary:
✅ Entries kept: 7
🗑️ Entries removed: 11
📁 Original file backed up to: price_history.backup.20241119_085103.json
✨ Cleaned file saved to: price_history.json
```

## Best Practices
1. Always verify your data needs before running the cleanup
2. Keep the generated backup file until you've verified the cleaned data
3. Run the script during off-peak hours if using in production
4. Check the cleanup summary to ensure expected results

## Error Recovery
If an error occurs:
1. The script automatically restores from backup
2. Check the error message for details
3. Verify the original file was restored correctly
4. Address any issues before retrying
