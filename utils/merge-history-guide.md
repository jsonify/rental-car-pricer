# Price History Merge Utility Guide

## Purpose
The merge utility (`merge_history.py`) combines two price history files, allowing you to merge historical price data with current data while maintaining data integrity and avoiding duplicates.

## Usage
```bash
python3 merge_history.py
```

The script expects:
- Current data in `price_history.json`
- Historical data in `price_history_cleaned.json`

## Features

### Automatic Backup
- Creates timestamped backup of current data before merging
- Format: `price_history.backup.YYYYMMDD_HHMMSS.json`

### Smart Merging
- Combines active bookings lists
- Merges price histories chronologically
- Preserves all booking metadata
- Updates last_updated timestamp
- Handles both new and existing bookings

## Process Flow

1. **Load Files**
   ```
   Loading current price history...
   ✅ Current price history loaded
   
   Loading historical price history...
   ✅ Historical price history loaded
   ```

2. **Create Backup**
   ```
   Creating backup: price_history.backup.20241119_085103.json
   ✅ Backup created successfully
   ```

3. **Merge and Save**
   ```
   Merging price histories...
   ✅ Successfully merged and saved price histories
   ```

4. **Summary Report**
   ```
   📊 Merge Summary:
   Total bookings: 3
   
   📍 LIH:
      Price history entries: 8
      Date range: 04/03/2025 - 04/10/2025
      Focus category: Full-size Car
   ```

## Data Handling

### For New Bookings:
- Adds complete booking record from historical data
- Includes all associated price history
- Adds booking ID to active bookings list

### For Existing Bookings:
- Combines price histories chronologically
- Preserves most recent metadata
- Maintains focus categories and holding prices
- Removes duplicate entries

## Best Practices

1. Pre-Merge Steps:
   - Clean historical data first (`cleanup_price_history.py`)
   - Verify both files are valid JSON
   - Back up both files manually if needed

2. Post-Merge Verification:
   - Check the merge summary for expected results
   - Verify total number of bookings
   - Confirm price history entries for each booking
   - Test the merged file in your tracking system

3. Error Handling:
   - Keep the backup file until verification is complete
   - Check error messages for specific issues
   - Restore from backup if needed

## Common Issues

1. Invalid JSON format:
   ```
   ❌ Invalid JSON in file: price_history_cleaned.json
   ```
   - Verify JSON syntax in both files
   - Use a JSON validator if needed

2. Missing Files:
   ```
   ❌ File not found: price_history.json
   ```
   - Ensure both required files are in the correct location
   - Check file permissions

3. Merge Conflicts:
   ```
   ❌ Error merging price histories: [error details]
   ```
   - Check for incompatible data structures
   - Verify timestamp formats match
   - Ensure booking IDs are consistent

## Recovery Steps

If errors occur:
1. Check the error message for specific issues
2. Restore from the automatically created backup
3. Fix any identified problems in the source files
4. Try the merge again
