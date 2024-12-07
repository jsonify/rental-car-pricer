import { useState, useEffect } from 'react';
import { DataGrid } from './DataGrid';
import { Chart } from './Chart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const formatPrice = (price) => `$${parseFloat(price).toFixed(2)}`;

export const PriceTracker = () => {
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPriceData = async () => {
      try {
        const response = await fetch('/price_history.json');
        if (!response.ok) throw new Error('Failed to load price data');
        const data = await response.json();
        setPriceData(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPriceData();
    const interval = setInterval(fetchPriceData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

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

  const bookings = Object.entries(priceData?.bookings || {}).map(([id, booking]) => {
    const priceHistory = booking.price_history || [];
    const latestPrice = priceHistory[priceHistory.length - 1]?.prices?.[booking.focus_category] || 0;
    const previousPrice = priceHistory[priceHistory.length - 2]?.prices?.[booking.focus_category] || 0;
    const holdingPrice = booking.holding_price || 0;
    const potentialSavings = Math.max(0, holdingPrice - latestPrice);

    return {
      id,
      ...booking,
      latestPrice,
      previousPrice,
      potentialSavings,
      priceChange: latestPrice - previousPrice,
      percentChange: previousPrice ? ((latestPrice - previousPrice) / previousPrice) * 100 : 0
    };
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Car Rental Price Monitor</h1>
          <p className="text-gray-500">
            Last updated: {new Date(priceData?.metadata?.last_updated).toLocaleString()}
          </p>
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