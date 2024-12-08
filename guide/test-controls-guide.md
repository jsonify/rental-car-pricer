# Car Rental Price Monitor - Testing Guide

## Admin Controls

### Check Current Prices
- Simulates the price checking functionality
- Takes ~2 seconds to complete (simulated network delay)
- Updates all bookings with new randomly generated prices
- Updates the "Last updated" timestamp
- Use this to test how your UI handles price changes and updates

### Add New Booking
- Opens a dialog to add a new test booking
- Allows you to specify:
  - Airport code (KOA, HNL, OGG, LIH)
  - Pickup/Dropoff dates
  - Vehicle category
  - Optional holding price
- New booking appears immediately in the dashboard
- Generates random price history for the new booking

### Update Holding Prices
- Opens a dialog to modify holding prices for existing bookings
- Useful for testing:
  - Price comparison features
  - Savings calculations
  - UI updates when holding prices change
- Changes are reflected immediately in the dashboard

### Delete Booking
- Removes a selected booking from the test data
- Useful for testing:
  - UI handling of booking removal
  - Empty state displays
  - Grid/layout adjustments with fewer items

## Test Controls

### Add Test Booking
- Quickly adds a new booking with randomized data:
  - Random airport location
  - Random future dates
  - Random vehicle category
  - Random holding price
  - Generated price history (last 30 days)
- Helpful for testing UI with different numbers of bookings
- Each booking has realistic, but random price variations

### Reset Test Data
- Resets all test data to initial state
- Creates 3 fresh bookings with new random data
- Clears any custom bookings or modifications
- Use this when you want to start fresh or test with consistent number of items

## Development Tips

1. Use "Add Test Booking" to quickly populate your UI with varied data
2. Test edge cases by adding many bookings
3. Use "Reset Test Data" when you want to ensure a consistent starting point
4. Test loading states by checking prices (2-second delay)
5. Test error handling by triggering multiple actions simultaneously

## Data Generation Details

The test environment generates:
- Realistic price variations (±20% from base price)
- 30 days of price history per booking
- Proper price relationships between vehicle categories
- Timestamps that match your current timezone
- Consistent data structures matching production

## Limitations

1. Data is reset when you refresh the page
2. Prices are random but maintain reasonable relationships
3. Dates are always in the future
4. Limited to 4 test airport locations
5. Price check delay is fixed at 2 seconds

## Adding New Test Scenarios

To add new test scenarios, you can modify the mock data generation in:
- `src/lib/mock-supabase.ts`
- Adjust price ranges, locations, categories, or timing
- Add new failure scenarios or edge cases
