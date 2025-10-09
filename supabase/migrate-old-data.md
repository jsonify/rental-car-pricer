# Migrating Data from Old Supabase Project

If you have the SQL dump from your old Supabase project and want to restore it:

## Option 1: Direct SQL Import (Recommended)

1. Get your old database dump file (should be named something like `backup_YYYY-MM-DD.sql`)

2. Go to the SQL Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/sql/new

3. Open your dump file and copy relevant `INSERT` statements

4. Paste and run them in the SQL editor

**Important**: Skip any `CREATE TABLE` statements since we already created the schema.

## Option 2: CSV Import via Table Editor

If you have CSV exports:

1. Go to Table Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor
2. Select a table (bookings, price_histories, etc.)
3. Click "Insert" → "Import from CSV"
4. Upload your CSV file

## Option 3: Python Script Migration

If you have the old database credentials, you can migrate programmatically:

```python
# migrate_from_old_db.py
from supabase import create_client
import os

# Old database
OLD_URL = "https://your-old-project.supabase.co"
OLD_KEY = "your-old-service-key"

# New database
NEW_URL = "https://wjhrxogbluuxbcbxruqu.supabase.co"
NEW_KEY = os.getenv('SUPABASE_SERVICE_KEY')

old_db = create_client(OLD_URL, OLD_KEY)
new_db = create_client(NEW_URL, NEW_KEY)

# Migrate bookings
print("Migrating bookings...")
bookings = old_db.table('bookings').select('*').execute()
for booking in bookings.data:
    # Remove 'id' to let Supabase generate new UUIDs
    booking_id = booking.pop('id')
    new_booking = new_db.table('bookings').insert(booking).execute()
    print(f"Migrated booking: {booking['location']}")

# Migrate price histories
print("Migrating price histories...")
histories = old_db.table('price_histories').select('*').execute()
for history in histories.data:
    history.pop('id')
    new_db.table('price_histories').insert(history).execute()

print("✅ Migration complete!")
```

## What to Migrate

Consider what you actually need:

### Essential:
- **Bookings** - Your current tracked rental searches
- **Latest price_histories** - Maybe just the last 30 days

### Optional:
- Old historical data - Nice to have but not critical
- Holding price histories - Can recreate with current values

### Skip:
- Any test/development data
- Expired bookings (where dropoff_date has passed)

## Starting Fresh (Recommended)

Since this is a price tracker, starting fresh might be simpler:

1. Add your current bookings via the Admin UI
2. Run the Python scraper to get current prices
3. Build new price history going forward

Benefits:
- Clean slate with new architecture
- No migration bugs or data inconsistencies
- Faster setup (5 minutes vs hours of migration)

You can always keep the old database dump as a backup if you need to reference historical data later.
