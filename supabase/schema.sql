-- Supabase Schema for Rental Car Price Tracker
-- Run this in the SQL Editor at https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Price histories table
CREATE TABLE IF NOT EXISTS price_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    prices JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Holding price histories table (tracks when holding prices were changed)
CREATE TABLE IF NOT EXISTS holding_price_histories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bookings_active ON bookings(active);
CREATE INDEX IF NOT EXISTS idx_bookings_pickup_date ON bookings(pickup_date);
CREATE INDEX IF NOT EXISTS idx_price_histories_booking_id ON price_histories(booking_id);
CREATE INDEX IF NOT EXISTS idx_price_histories_created_at ON price_histories(created_at);
CREATE INDEX IF NOT EXISTS idx_holding_price_histories_booking_id ON holding_price_histories(booking_id);
CREATE INDEX IF NOT EXISTS idx_holding_price_histories_effective_from ON holding_price_histories(effective_from);

-- Enable Row Level Security (RLS)
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_histories ENABLE ROW LEVEL SECURITY;
ALTER TABLE holding_price_histories ENABLE ROW LEVEL SECURITY;

-- Policies for bookings (allow all operations for now - adjust based on your auth setup)
CREATE POLICY "Allow all operations on bookings" ON bookings
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies for price_histories
CREATE POLICY "Allow all operations on price_histories" ON price_histories
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Policies for holding_price_histories
CREATE POLICY "Allow all operations on holding_price_histories" ON holding_price_histories
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Optional: Trigger to automatically set effective_to when a new holding price is added
CREATE OR REPLACE FUNCTION update_previous_holding_price_effective_to()
RETURNS TRIGGER AS $$
BEGIN
    -- Set effective_to for the previous holding price record
    UPDATE holding_price_histories
    SET effective_to = NEW.effective_from
    WHERE booking_id = NEW.booking_id
      AND effective_to IS NULL
      AND id != NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_holding_price_effective_to
    AFTER INSERT ON holding_price_histories
    FOR EACH ROW
    EXECUTE FUNCTION update_previous_holding_price_effective_to();

-- Insert sample data (optional - remove if you want to start completely fresh)
DO $$
DECLARE
    koa_booking_id UUID;
    hnl_booking_id UUID;
BEGIN
    -- Insert sample bookings
    INSERT INTO bookings (id, location, location_full_name, pickup_date, dropoff_date, focus_category, holding_price)
    VALUES
        (uuid_generate_v4(), 'KOA', 'Kailua-Kona International Airport', '04/01/2025', '04/08/2025', 'Economy Car', 299.99)
    RETURNING id INTO koa_booking_id;

    INSERT INTO bookings (id, location, location_full_name, pickup_date, dropoff_date, focus_category, holding_price)
    VALUES
        (uuid_generate_v4(), 'HNL', 'Daniel K. Inouye International Airport', '05/15/2025', '05/22/2025', 'Standard SUV', 499.99)
    RETURNING id INTO hnl_booking_id;

    -- Insert sample price history for KOA
    INSERT INTO price_histories (booking_id, timestamp, prices)
    VALUES
        (koa_booking_id, NOW() - INTERVAL '1 day',
         '{"Economy Car": 305.50, "Compact Car": 310.25, "Intermediate Car": 315.75, "Standard Car": 320.00, "Full-size Car": 335.50, "Premium Car": 390.00, "Compact SUV": 420.00, "Standard SUV": 450.00, "Full-size SUV": 540.00, "Premium SUV": 660.00, "Minivan": 480.00}'::jsonb),
        (koa_booking_id, NOW(),
         '{"Economy Car": 299.99, "Compact Car": 305.00, "Intermediate Car": 310.50, "Standard Car": 315.00, "Full-size Car": 330.00, "Premium Car": 385.00, "Compact SUV": 415.00, "Standard SUV": 445.00, "Full-size SUV": 535.00, "Premium SUV": 655.00, "Minivan": 475.00}'::jsonb);

    -- Insert sample price history for HNL
    INSERT INTO price_histories (booking_id, timestamp, prices)
    VALUES
        (hnl_booking_id, NOW() - INTERVAL '1 day',
         '{"Economy Car": 275.00, "Compact Car": 280.50, "Intermediate Car": 285.75, "Standard Car": 290.00, "Full-size Car": 305.50, "Premium Car": 360.00, "Compact SUV": 390.00, "Standard SUV": 510.00, "Full-size SUV": 590.00, "Premium SUV": 720.00, "Minivan": 520.00}'::jsonb),
        (hnl_booking_id, NOW(),
         '{"Economy Car": 270.00, "Compact Car": 275.25, "Intermediate Car": 280.50, "Standard Car": 285.00, "Full-size Car": 300.00, "Premium Car": 355.00, "Compact SUV": 385.00, "Standard SUV": 499.99, "Full-size SUV": 580.00, "Premium SUV": 710.00, "Minivan": 510.00}'::jsonb);

    -- Insert holding price histories
    INSERT INTO holding_price_histories (booking_id, price, effective_from)
    VALUES
        (koa_booking_id, 299.99, NOW() - INTERVAL '7 days'),
        (hnl_booking_id, 499.99, NOW() - INTERVAL '7 days');
END $$;
