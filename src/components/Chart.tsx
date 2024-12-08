import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

export const Chart = ({ booking }) => {
  const chartData = useMemo(() => {
    if (!booking?.price_history) return [];

    // Convert holding price history into a lookup map
    const holdingPrices = new Map();
    
    // If we have holding price history in the booking
    if (booking.holding_price_history) {
      booking.holding_price_history.forEach(history => {
        // Get dates as timestamps for comparison
        const startDate = new Date(history.effective_from).getTime();
        const endDate = history.effective_to ? new Date(history.effective_to).getTime() : new Date().getTime();
        
        // For each price history entry
        booking.price_history.forEach(record => {
          const recordDate = new Date(record.timestamp).getTime();
          // If the record falls within this holding price's effective period
          if (recordDate >= startDate && recordDate <= endDate) {
            holdingPrices.set(record.timestamp, history.price);
          }
        });
      });
    }

    // Map the price history with corresponding holding prices
    return booking.price_history.map(record => ({
      timestamp: record.timestamp,
      price: record.prices?.[booking.focus_category] || 0,
      // Use the mapped holding price or fall back to current holding price
      holdingPrice: holdingPrices.get(record.timestamp) || booking.holding_price || 0
    }));
  }, [booking]);

  if (chartData.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center text-gray-500">
        No price history available
      </div>
    );
  }

  return (
    <div className="h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
          <XAxis
            dataKey="timestamp"
            tick={{ fill: '#666' }}
            fontSize={12}
          />
          <YAxis
            tickFormatter={(value) => `$${value}`}
            tick={{ fill: '#666' }}
            fontSize={12}
          />
          <Tooltip
            formatter={(value) => [`$${value.toFixed(2)}`, '']}
            contentStyle={{ 
              backgroundColor: 'white', 
              borderRadius: '8px',
              padding: '8px',
              border: '1px solid #e5e7eb'
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            name="Current Price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="step"
            dataKey="holdingPrice"
            name="Holding Price"
            stroke="#dc2626"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Chart;