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

interface PriceRecord {
  timestamp: string;
  prices: {
    [key: string]: number;
  };
}

interface Booking {
  id: string;
  location: string;
  location_full_name: string;
  pickup_date: string;
  dropoff_date: string;
  focus_category: string;
  price_history: PriceRecord[];
  holding_price?: number;
}

interface ChartProps {
  booking: Booking;
}

export const Chart = ({ booking }: ChartProps) => {
  const chartData = useMemo(() => {
    if (!booking?.price_history) return [];

    return booking.price_history.map((record) => ({
      timestamp: record.timestamp,
      price: record.prices?.[booking.focus_category] || 0,
      holdingPrice: booking.holding_price || 0
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
            formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
            contentStyle={{ backgroundColor: 'white', borderRadius: '8px' }}
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
            type="monotone"
            dataKey="holdingPrice"
            name="Holding Price"
            stroke="#dc2626"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};