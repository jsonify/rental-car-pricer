#!/usr/bin/env python3
"""Apply schema migration to Supabase database"""

# Read the SQL file
with open('supabase/schema_update.sql', 'r') as f:
    sql_content = f.read()

# Supabase doesn't have a direct SQL execution endpoint via REST API
# We need to use the database connection directly
# For now, let's manually execute via the Supabase dashboard

print("=" * 80)
print("MANUAL MIGRATION REQUIRED")
print("=" * 80)
print("\nPlease follow these steps:")
print(f"\n1. Go to: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor/sql")
print("\n2. Copy and paste the following SQL:\n")
print("-" * 80)
print(sql_content)
print("-" * 80)
print("\n3. Click 'Run' to execute the migration")
print("\nWARNING: This will delete all existing data in the bookings, price_histories,")
print("         and holding_price_histories tables!")
print("\n" + "=" * 80)
