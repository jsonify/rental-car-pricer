import { useState, useEffect, useMemo } from 'react';
import { DataGrid } from './DataGrid';
import { Chart } from './Chart';
import { CategoryFilter } from './CategoryFilter';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import { TestControls } from './TestControls';
import { isDevelopment } from '@/lib/environment';
import { useBookings } from '@/hooks/useBookings'

const formatPrice = (price: number) => `$${price.toFixed(2)}`;

// Default excluded categories
const DEFAULT_EXCLUDED_CATEGORIES = [
  "Luxury Specialty",
  "Large Luxury SUV",
  "Full-size Van"
];

export const PriceTracker = () => {
  const { bookings, loading, error, lastUpdated } = useBookings();

  // Load excluded categories from localStorage or use defaults
  const [excludedCategories, setExcludedCategories] = useState<Record<string, string[]>>(() => {
    const saved = localStorage.getItem('excludedCategories');
    return saved ? JSON.parse(saved) : {};
  });

  // Save to localStorage whenever excluded categories change
  useEffect(() => {
    localStorage.setItem('excludedCategories', JSON.stringify(excludedCategories));
  }, [excludedCategories]);

  // Get all available categories for a booking
  const getBookingCategories = (booking: any) => {
    const categorySet = new Set<string>();
    (booking.price_history || []).forEach((record: any) => {
      if (record.prices) {
        Object.keys(record.prices).forEach(category => categorySet.add(category));
      }
    });
    return Array.from(categorySet).sort();
  };

  // Toggle category visibility for a specific booking
  const toggleCategory = (bookingId: string, category: string) => {
    setExcludedCategories(prev => {
      const bookingExcluded = prev[bookingId] || DEFAULT_EXCLUDED_CATEGORIES;
      const isCurrentlyExcluded = bookingExcluded.includes(category);

      return {
        ...prev,
        [bookingId]: isCurrentlyExcluded
          ? bookingExcluded.filter(c => c !== category)
          : [...bookingExcluded, category]
      };
    });
  };

  // Show all categories for a booking
  const selectAllCategories = (bookingId: string) => {
    setExcludedCategories(prev => ({
      ...prev,
      [bookingId]: []
    }));
  };

  // Hide all categories for a booking
  const deselectAllCategories = (bookingId: string, allCategories: string[]) => {
    setExcludedCategories(prev => ({
      ...prev,
      [bookingId]: allCategories
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Loading price data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
      {isDevelopment && <TestControls />}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Car Rental Price Monitor</h1>
          {lastUpdated && (
            <p className="text-gray-500">
              Last updated: {format(new Date(lastUpdated), 'PPpp')}
            </p>
          )}
        </div>
        
        <div className="space-y-8">
          {bookings.map(booking => {
            const allCategories = getBookingCategories(booking);
            const bookingExcluded = excludedCategories[booking.id] || DEFAULT_EXCLUDED_CATEGORIES;

            return (
              <Card key={booking.id} className="overflow-hidden">
                <CardHeader>
                  <CardTitle className="flex justify-between items-center">
                    <div>
                      <span className="text-xl">{booking.location_full_name}</span>
                      <span className="text-gray-500 text-sm ml-4">
                        {booking.pickup_date} - {booking.dropoff_date}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">Focus Category</div>
                      <div className="font-semibold">{booking.focus_category}</div>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow-sm">
                      <div className="text-sm text-gray-500">Current Price</div>
                      <div className="text-2xl font-semibold">
                        {formatPrice(booking.latestPrice)}
                      </div>
                      {booking.priceChange !== 0 && (
                        <div className={`text-sm ${booking.priceChange > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {booking.priceChange > 0 ? '↑' : '↓'} {formatPrice(Math.abs(booking.priceChange))}
                          ({booking.percentChange.toFixed(1)}%)
                        </div>
                      )}
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow-sm">
                      <div className="text-sm text-gray-500">Holding Price</div>
                      <div className="text-2xl font-semibold">
                        {formatPrice(booking.holding_price || 0)}
                      </div>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow-sm">
                      <div className="text-sm text-gray-500">Potential Savings</div>
                      <div className="text-2xl font-semibold text-green-600">
                        {formatPrice(booking.potentialSavings)}
                      </div>
                    </div>

                    <div className="lg:col-span-1">
                      <DataGrid booking={booking} excludedCategories={bookingExcluded} />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <CategoryFilter
                      categories={allCategories}
                      excludedCategories={bookingExcluded}
                      onToggleCategory={(category) => toggleCategory(booking.id, category)}
                      onSelectAll={() => selectAllCategories(booking.id)}
                      onDeselectAll={() => deselectAllCategories(booking.id, allCategories)}
                      focusCategory={booking.focus_category}
                    />

                    <Chart booking={booking} excludedCategories={bookingExcluded} />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PriceTracker;