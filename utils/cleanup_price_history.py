#!/usr/bin/env python3

import json
from datetime import datetime
import os
from typing import Dict, List

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string in either ISO or MM/DD HH:MM format"""
    try:
        # Try ISO format first (e.g. "2024-11-10T00:10:18.345155")
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try MM/DD HH:MM format
            return datetime.strptime(f"2024 {timestamp_str}", '%Y %m/%d %H:%M')
        except ValueError:
            # Try YYYY-MM-DD HH:MM:SS format
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

def clean_price_history(filename: str = 'price_history.json') -> None:
    """
    Clean up price history by keeping only one entry from 11/10/2024 
    and all subsequent entries.
    """
    try:
        # Create backup of original file
        backup_filename = f'price_history.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        os.replace(filename, backup_filename)
        print(f"✅ Created backup: {backup_filename}")
        
        # Read the backup file
        with open(backup_filename, 'r') as f:
            data = json.load(f)
        
        target_date = datetime(2024, 11, 10)
        entries_kept = 0
        entries_removed = 0
        
        # Process each booking
        for booking_id in data['bookings']:
            booking = data['bookings'][booking_id]
            print(f"\nProcessing booking: {booking_id}")
            
            if 'price_records' in booking:
                # Filter price records
                filtered_records = []
                found_target_date = False
                original_count = len(booking['price_records'])
                
                for record in sorted(booking['price_records'], 
                                  key=lambda x: parse_timestamp(x['timestamp'])):
                    record_date = parse_timestamp(record['timestamp'])
                    
                    # Keep record if it's after target date or it's the first one from target date
                    if record_date.date() > target_date.date():
                        filtered_records.append(record)
                        entries_kept += 1
                    elif record_date.date() == target_date.date() and not found_target_date:
                        filtered_records.append(record)
                        found_target_date = True
                        entries_kept += 1
                    else:
                        entries_removed += 1
                
                booking['price_records'] = filtered_records
                print(f"Price records: {original_count} → {len(filtered_records)}")
            
            if 'price_history' in booking:
                # Filter price history
                filtered_history = []
                found_target_date = False
                original_count = len(booking['price_history'])
                
                for record in sorted(booking['price_history'], 
                                  key=lambda x: parse_timestamp(x['timestamp'])):
                    record_date = parse_timestamp(record['timestamp'])
                    
                    # Keep record if it's after target date or it's the first one from target date
                    if record_date.date() > target_date.date():
                        filtered_history.append(record)
                        entries_kept += 1
                    elif record_date.date() == target_date.date() and not found_target_date:
                        filtered_history.append(record)
                        found_target_date = True
                        entries_kept += 1
                    else:
                        entries_removed += 1
                
                booking['price_history'] = filtered_history
                print(f"Price history: {original_count} → {len(filtered_history)}")
        
        # Update last_updated in metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save cleaned data
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nCleanup Summary:")
        print(f"✅ Entries kept: {entries_kept}")
        print(f"🗑️ Entries removed: {entries_removed}")
        print(f"📁 Original file backed up to: {backup_filename}")
        print(f"✨ Cleaned file saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error cleaning price history: {str(e)}")
        # Restore original file if there was an error
        if os.path.exists(backup_filename):
            os.replace(backup_filename, filename)
            print(f"⚠️ Restored original file from backup")
        raise

if __name__ == "__main__":
    clean_price_history()