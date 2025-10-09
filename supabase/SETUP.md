# Supabase Setup Guide

## New Project Information
- **Project URL**: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu
- **Project ID**: `wjhrxogbluuxbcbxruqu`

## Step 1: Run the Schema

1. Go to the SQL Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/sql/new
2. Copy the contents of `supabase/schema.sql`
3. Paste into the SQL editor
4. Click "Run" or press `Cmd/Ctrl + Enter`

This will create:
- 3 tables: `bookings`, `price_histories`, `holding_price_histories`
- Indexes for performance
- Row Level Security policies (allow all for now)
- Automatic trigger to manage holding price history
- Sample data (2 bookings with price history)

## Step 2: Get Your API Keys

1. Go to Settings → API: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/settings/api
2. Copy the following values:

### For Frontend (.env.local or Vite config):
```bash
VITE_SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

### For Python Backend (.env):
```bash
SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
SUPABASE_SERVICE_KEY=<your-service-role-key>
```

**Note**: Use the `service_role` key for Python (has full access), and the `anon` key for frontend (respects RLS policies).

## Step 3: Update Your Environment Files

### Frontend Environment
Create or update `.env.local` in the project root:
```bash
VITE_SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...your-actual-key-here
```

### Python Environment
Update your `.env` file (keep your existing Chrome/email config):
```bash
# Supabase (NEW)
SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...your-actual-service-key-here

# Chrome/ChromeDriver (keep existing)
CHROME_BINARY_PATH=/path/to/chrome
CHROMEDRIVER_PATH=/path/to/chromedriver
USER_AGENT=Mozilla/5.0...

# Email (keep existing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com
```

## Step 4: Test the Connection

### Test Frontend:
```bash
npm run dev
```

Then:
1. Open http://localhost:5173
2. Toggle the test environment switch OFF (to use production Supabase)
3. You should see the 2 sample bookings with price data
4. Try adding a booking via Admin Controls

### Test Python:
```bash
python3 -c "from supabase_client import get_supabase_client; client = get_supabase_client(); print('✅ Connected:', client.table('bookings').select('*').execute())"
```

## Step 5: Optional - Remove Sample Data

If you want to start completely fresh without the sample bookings:

1. Go to Table Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor
2. Select the `bookings` table
3. Delete the 2 sample rows (KOA and HNL)
4. The related `price_histories` will be automatically deleted due to `ON DELETE CASCADE`

Or run this SQL:
```sql
DELETE FROM bookings WHERE location IN ('KOA', 'HNL');
```

## Troubleshooting

### "Failed to fetch" errors in frontend:
- Check that `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are set correctly
- Restart the dev server after changing env vars (`npm run dev`)

### Python connection errors:
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`
- Make sure you're using the `service_role` key, not the `anon` key

### RLS Policy Issues:
The policies are currently set to "allow all". If you want to add authentication later:
```sql
-- Example: Only allow authenticated users
DROP POLICY "Allow all operations on bookings" ON bookings;
CREATE POLICY "Authenticated users can manage bookings" ON bookings
    FOR ALL
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated');
```

## Database Schema Reference

### bookings
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| location | TEXT | Airport code (e.g., "KOA") |
| location_full_name | TEXT | Full airport name |
| pickup_date | TEXT | Format: MM/DD/YYYY |
| dropoff_date | TEXT | Format: MM/DD/YYYY |
| pickup_time | TEXT | Format: "12:00 PM" |
| dropoff_time | TEXT | Format: "12:00 PM" |
| focus_category | TEXT | Vehicle category to track |
| holding_price | DECIMAL | Current reserved price |
| active | BOOLEAN | Whether booking is active |
| created_at | TIMESTAMPTZ | When booking was created |

### price_histories
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| booking_id | UUID | Foreign key to bookings |
| timestamp | TIMESTAMPTZ | When prices were checked |
| prices | JSONB | All category prices as JSON object |
| created_at | TIMESTAMPTZ | When record was created |

### holding_price_histories
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| booking_id | UUID | Foreign key to bookings |
| price | DECIMAL | Holding price value |
| effective_from | TIMESTAMPTZ | When this price started |
| effective_to | TIMESTAMPTZ | When this price ended (null = current) |
| created_at | TIMESTAMPTZ | When record was created |

## Next Steps

After setup is complete:
1. Run the Python scraper to get real price data: `python3 main.py`
2. Set up GitHub Actions to run automated price checks
3. Configure email alerts for price drops
