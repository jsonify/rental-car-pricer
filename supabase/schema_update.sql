-- Update schema to use TEXT IDs instead of UUIDs
-- This matches the format used in price_history.json (e.g., "SAN_04022026_04082026")

-- Drop existing tables (warning: this deletes all data!)
DROP TABLE IF EXISTS holding_price_histories CASCADE;
DROP TABLE IF EXISTS price_histories CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;

-- Recreate bookings table with TEXT id
CREATE TABLE bookings (
    id TEXT PRIMARY KEY,
    location TEXT NOT NULL,
    location_full_name TEXT NOT NULL,
    pickup_date TEXT NOT NULL,
    dropoff_date TEXT NOT NULL,
    pickup_time TEXT NOT NULL DEFAULT '12:00 PM',
    dropoff_time TEXT NOT NULL DEFAULT '12:00 PM',
    focus_category TEXT NOT NULL,
    holding_price DECIMAL(10, 2),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Recreate price_histories table
CREATE TABLE price_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id TEXT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    prices JSONB NOT NULL,
    lowest_price JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Recreate holding_price_histories table
CREATE TABLE holding_price_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id TEXT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Recreate indexes
CREATE INDEX idx_bookings_active ON bookings(active);
CREATE INDEX idx_bookings_pickup_date ON bookings(pickup_date);
CREATE INDEX idx_price_histories_booking_id ON price_histories(booking_id);
CREATE INDEX idx_price_histories_created_at ON price_histories(created_at);
CREATE INDEX idx_holding_price_histories_booking_id ON holding_price_histories(booking_id);
CREATE INDEX idx_holding_price_histories_effective_from ON holding_price_histories(effective_from);

-- Enable RLS
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_histories ENABLE ROW LEVEL SECURITY;
ALTER TABLE holding_price_histories ENABLE ROW LEVEL SECURITY;

-- Recreate policies
CREATE POLICY "Allow all operations on bookings" ON bookings
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on price_histories" ON price_histories
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on holding_price_histories" ON holding_price_histories
    FOR ALL USING (true) WITH CHECK (true);
