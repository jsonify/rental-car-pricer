#!/usr/bin/env python3

import sys
import re
from datetime import datetime
import json

def parse_car_categories(text_block):
    """Parse car categories and prices from a section of text"""
    prices = {}
    in_category_section = False
    current_category = None
    
    for line in text_block.split('\n'):
        line = line.strip()
        
        # Start capturing after "All Categories"
        if "All Categories" in line:
            in_category_section = True
            continue
        
        # Skip if not in category section or empty line
        if not in_category_section or not line:
            continue
            
        # Stop if we hit the next section
        if line.startswith(('LIH -', 'KOA -', 'OGG -')):
            break
            
        # Remove focus marker if present
        line = line.replace('🎯 ', '')
        
        # If line has a dollar sign, it's a price for the previous category
        if line.startswith('$'):
            if current_category:
                try:
                    price = float(line.replace('$', '').strip())
                    prices[current_category] = price
                    print(f"Added: {current_category} = ${price}")
                except ValueError as e:
                    print(f"Error parsing price: {line}, Error: {e}")
            current_category = None
        else:
            # If no dollar sign, this is a category name
            current_category = line
            print(f"Found category: {current_category}")
    
    if prices:
        print(f"\nSuccessfully parsed {len(prices)} categories")
        print("Sample of parsed prices:")
        for i, (cat, price) in enumerate(sorted(prices.items())):
            if i >= 3:
                break
            print(f"  {cat}: ${price}")
    else:
        print("\nWarning: No prices were parsed from the section")
    
    return prices

def parse_text_to_json(text_content):
    """Convert price check text content to JSON format"""
    result = {
        "metadata": {
            "last_updated": "",
            "active_bookings": []
        },
        "bookings": {}
    }
    
    # Extract timestamp
    timestamp_match = re.search(r"Last checked: (.*)", text_content)
    if timestamp_match:
        last_checked = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S")
        result["metadata"]["last_updated"] = last_checked.isoformat()
        print(f"Found timestamp: {last_checked}")
    
    # Split into booking sections
    sections = text_content.split('\n')
    current_section = []
    all_sections = []
    
    for line in sections:
        if re.match(r'^[A-Z]{3} -', line):
            if current_section:
                all_sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    if current_section:
        all_sections.append('\n'.join(current_section))
    
    # Process each section
    for section in all_sections:
        try:
            # Parse basic booking info
            location_match = re.search(r'([A-Z]{3}) - (.+)', section)
            date_match = re.search(r'📅 (\d{2}/\d{2}/\d{4}) to (\d{2}/\d{2}/\d{4})', section)
            
            if not location_match or not date_match:
                continue
            
            location = location_match.group(1)
            location_full_name = location_match.group(2).strip()
            pickup_date = date_match.group(1)
            dropoff_date = date_match.group(2)
            
            print(f"\nProcessing booking for {location}")
            print(f"Dates: {pickup_date} to {dropoff_date}")
            
            # Extract focus category
            focus_match = re.search(r'Tracked Category\n(.*?)(?=\n)', section)
            focus_category = focus_match.group(1).strip() if focus_match else None
            print(f"Focus category: {focus_category}")
            
            # Extract holding price
            holding_match = re.search(r'💰 Holding Price: \$(\d+\.\d+)', section)
            holding_price = float(holding_match.group(1)) if holding_match else None
            print(f"Holding price: ${holding_price}")
            
            # Parse car categories and prices
            prices = parse_car_categories(section)
            
            if not prices:
                print(f"Warning: No prices found for {location}")
                continue
            
            # Create booking ID
            booking_id = f"{location}_{pickup_date}_{dropoff_date}".replace("/", "")
            
            # Create price history entry
            lowest_price = min(prices.items(), key=lambda x: x[1])
            price_history_entry = {
                "timestamp": result["metadata"]["last_updated"],
                "prices": prices,
                "lowest_price": {
                    "category": lowest_price[0],
                    "price": lowest_price[1]
                }
            }
            
            # Create booking entry
            booking_data = {
                "location": location,
                "location_full_name": location_full_name,
                "pickup_date": pickup_date,
                "dropoff_date": dropoff_date,
                "pickup_time": "12:00 PM",
                "dropoff_time": "12:00 PM",
                "focus_category": focus_category,
                "price_history": [price_history_entry],
                "created_at": result["metadata"]["last_updated"],
                "holding_price": holding_price
            }
            
            # Add to result
            result["bookings"][booking_id] = booking_data
            if booking_id not in result["metadata"]["active_bookings"]:
                result["metadata"]["active_bookings"].append(booking_id)
            
        except Exception as e:
            print(f"Error processing section: {str(e)}")
            continue
    
    return result

def main():
    """Main function to process the text file"""
    if len(sys.argv) != 2:
        print("Usage: python3 text_to_json_converter.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.rsplit('.', 1)[0] + '.json'
    
    print(f"Processing {input_file}...")
    
    try:
        with open(input_file, 'r') as f:
            text_content = f.read()
        
        json_data = parse_text_to_json(text_content)
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\nConversion complete. Output saved to {output_file}")
        print("\nBooking summary:")
        for booking_id, booking in json_data["bookings"].items():
            prices = booking["price_history"][0]["prices"] if booking["price_history"] else {}
            print(f"\n{booking['location']} - {booking['pickup_date']} to {booking['dropoff_date']}")
            print(f"Categories found: {len(prices)}")
            if prices:
                print("Sample categories:")
                for i, (category, price) in enumerate(sorted(prices.items())):
                    if i >= 3:
                        break
                    print(f"  {category}: ${price}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()