import json
import os
from datetime import datetime
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

def connect_to_db():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        print("✅ Connected to database successfully")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        sys.exit(1)

def load_price_history() -> Dict:
    """Load the price history JSON file"""
    try:
        with open('price_history.json', 'r') as f:
            data = json.load(f)
        print("✅ Loaded price_history.json successfully")
        return data
    except Exception as e:
        print(f"❌ Error loading price_history.json: {str(e)}")
        sys.exit(1)

def migrate_holding_prices(conn, data: Dict):
    """Migrate holding price history data"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get current holding price histories
        cur.execute("""
            SELECT booking_id, effective_from, effective_to, price, category
            FROM holding_price_histories
            ORDER BY booking_id, effective_from
        """)
        existing_histories = cur.fetchall()
        print(f"\nFound {len(existing_histories)} existing history records")
        
        # Process each booking
        for booking_id, booking in data['bookings'].items():
            print(f"\nProcessing booking: {booking_id}")
            
            # Get existing records for this booking
            booking_history = [h for h in existing_histories if h['booking_id'] == booking_id]
            print(f"Found {len(booking_history)} existing records for this booking")
            
            # Extract history from price records
            price_history = booking.get('price_history', [])
            
            if not price_history:
                print("No price history found, skipping...")
                continue
            
            # Sort by timestamp to process chronologically
            sorted_history = sorted(price_history, key=lambda x: x['timestamp'])
            
            current_category = None
            current_price = None
            
            for record in sorted_history:
                timestamp = record['timestamp']
                focus_category = record.get('focus_category', booking['focus_category'])
                prices = record.get('prices', {})
                
                # Only process if we have a category price
                if focus_category in prices:
                    category_price = prices[focus_category]
                    
                    # Check if this represents a change
                    if (focus_category != current_category or 
                        category_price != current_price):
                        
                        # Close previous record if exists
                        if current_category:
                            cur.execute("""
                                UPDATE holding_price_histories
                                SET effective_to = %s
                                WHERE booking_id = %s
                                AND effective_to IS NULL
                            """, (timestamp, booking_id))
                        
                        # Insert new record
                        cur.execute("""
                            INSERT INTO holding_price_histories
                            (booking_id, price, category, effective_from, created_at)
                            VALUES (%s, %s, %s, %s, NOW())
                        """, (booking_id, category_price, focus_category, timestamp))
                        
                        print(f"Added history entry: {timestamp} - {focus_category} ${category_price}")
                        
                        current_category = focus_category
                        current_price = category_price
            
            # Commit after each booking
            conn.commit()
            print(f"✅ Committed changes for booking {booking_id}")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {str(e)}")
        raise
    finally:
        cur.close()

def verify_migration(conn):
    """Verify the migration results"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get counts by booking
        cur.execute("""
            SELECT booking_id, 
                   COUNT(*) as record_count,
                   MIN(effective_from) as earliest_record,
                   MAX(effective_from) as latest_record,
                   COUNT(DISTINCT category) as category_count
            FROM holding_price_histories
            GROUP BY booking_id
            ORDER BY booking_id
        """)
        
        results = cur.fetchall()
        print("\n📊 Migration Results:")
        print("=" * 50)
        
        for result in results:
            print(f"\nBooking: {result['booking_id']}")
            print(f"Total Records: {result['record_count']}")
            print(f"Date Range: {result['earliest_record']} to {result['latest_record']}")
            print(f"Unique Categories: {result['category_count']}")
            
    except Exception as e:
        print(f"❌ Error verifying migration: {str(e)}")
    finally:
        cur.close()

def main():
    """Main migration function"""
    print("\n🚀 Starting holding price history migration...")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to database
    conn = connect_to_db()
    
    try:
        # Load price history data
        data = load_price_history()
        
        # Perform migration
        migrate_holding_prices(conn, data)
        
        # Verify results
        verify_migration(conn)
        
        print("\n✨ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()