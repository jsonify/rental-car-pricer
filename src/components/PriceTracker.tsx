import { useState, useEffect } from 'react';
import { supabase, type Booking, type PriceHistory } from '../lib/supabase';
import { createSupabaseClient } from '@/lib/supabase'
import { DataGrid } from './DataGrid';
import { Chart } from './Chart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import { TestControls } from './TestControls';
import { isDevelopment } from '@/lib/environment';
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { githubActions } from '@/lib/github-actions'

const formatPrice = (price: number) => `$${price.toFixed(2)}`;

interface BookingWithHistory extends Booking {
  price_history: PriceHistory[];
  latestPrice: number;
  previousPrice: number;
  potentialSavings: number;
  priceChange: number;
  percentChange: number;
}

export const PriceTracker = () => {
  const [bookings, setBookings] = useState<BookingWithHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const { isTestEnvironment } = useEnvironment()
  const supabase = createSupabaseClient(isTestEnvironment)
  

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (isTestEnvironment) {
          // Get data from mock store
          const mockStore = githubActions.getMockStore()
          const bookingsWithHistory = mockStore.bookings.map(booking => {
            const priceHistories = mockStore.priceHistories.filter(
              history => history.booking_id === booking.id
            )
            
            const latestHistory = priceHistories[priceHistories.length - 1]
            const previousHistory = priceHistories[priceHistories.length - 2]
    
            const latestPrice = latestHistory?.prices?.[booking.focus_category] || 0
            const previousPrice = previousHistory?.prices?.[booking.focus_category] || 0
            const holdingPrice = booking.holding_price || 0
            const potentialSavings = Math.max(0, holdingPrice - latestPrice)
            const priceChange = latestPrice - previousPrice
            const percentChange = previousPrice ? (priceChange / previousPrice) * 100 : 0
    
            return {
              ...booking,
              price_history: priceHistories,
              latestPrice,
              previousPrice,
              potentialSavings,
              priceChange,
              percentChange
            }
          })
    
          setBookings(bookingsWithHistory)
          setLastUpdated(new Date().toISOString())
        } else {
          // Fetch bookings with holding price history
          const { data: bookingsData, error: bookingsError } = await supabase
            .from('bookings')
            .select('*')
            .eq('active', true)
            .order('pickup_date', { ascending: true });
    
          if (bookingsError) throw bookingsError;
    
          // Fetch data for each booking
          const bookingsWithHistory = await Promise.all(
            bookingsData.map(async (booking) => {
              // Fetch price histories
              const { data: priceHistories, error: historiesError } = await supabase
                .from('price_histories')
                .select('*')
                .eq('booking_id', booking.id)
                .order('created_at', { ascending: true });
    
              if (historiesError) throw historiesError;
    
              // Fetch holding price histories
              const { data: holdingPriceHistory, error: holdingError } = await supabase
                .from('holding_price_histories')
                .select('*')
                .eq('booking_id', booking.id)
                .order('effective_from', { ascending: true });
    
              if (holdingError) throw holdingError;
    
              const latestHistory = priceHistories[priceHistories.length - 1];
              const previousHistory = priceHistories[priceHistories.length - 2];
    
              const latestPrice = latestHistory?.prices?.[booking.focus_category] || 0;
              const previousPrice = previousHistory?.prices?.[booking.focus_category] || 0;
              const holdingPrice = booking.holding_price || 0;
              const potentialSavings = Math.max(0, holdingPrice - latestPrice);
              const priceChange = latestPrice - previousPrice;
              const percentChange = previousPrice ? (priceChange / previousPrice) * 100 : 0;
    
              return {
                ...booking,
                price_history: priceHistories,
                holding_price_history: holdingPriceHistory,
                latestPrice,
                previousPrice,
                potentialSavings,
                priceChange,
                percentChange
              };
            })
          );
    
          setBookings(bookingsWithHistory);
          setLastUpdated(new Date().toISOString());
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };
  
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [isTestEnvironment])

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
          {bookings.map(booking => (
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
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
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
                </div>

                <div className="grid gap-8 md:grid-cols-2">
                  <Chart booking={booking} />
                  <DataGrid booking={booking} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PriceTracker;