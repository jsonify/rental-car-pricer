import { useMemo } from "react";
import { format, parseISO } from "date-fns";
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

interface PriceCheck {
  id: string;
  location: string;
  checked_at: string;
  current_price: number;
  holding_price: number;
  focus_category: string;
}

interface ChartProps {
  data: PriceCheck[];
}

export function Chart({ data }: ChartProps) {
  const chartData = useMemo(() => {
    return data
      .sort((a, b) => parseISO(a.checked_at).getTime() - parseISO(b.checked_at).getTime())
      .map(check => ({
        date: format(parseISO(check.checked_at), "MMM d, h:mm a"),
        currentPrice: check.current_price,
        holdingPrice: check.holding_price,
        savings: check.holding_price - check.current_price
      }));
  }, [data]);

  const minPrice = Math.min(...data.map(d => d.current_price));
  const maxPrice = Math.max(...data.map(d => d.holding_price));
  const yDomain = [
    Math.floor(minPrice * 0.95), // 5% padding below min
    Math.ceil(maxPrice * 1.05)   // 5% padding above max
  ];

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-4">
        Price Trends - {data[0]?.location} ({data[0]?.focus_category})
      </h3>
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis 
              dataKey="date" 
              style={{ fontSize: '12px' }}
              tick={{ fill: '#666' }}
            />
            <YAxis 
              domain={yDomain}
              tickFormatter={(value) => `$${value}`}
              style={{ fontSize: '12px' }}
              tick={{ fill: '#666' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: 'white', borderRadius: '8px' }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="currentPrice"
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
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="text-center p-2 bg-blue-50 rounded">
          <p className="text-sm text-gray-600">Latest Price</p>
          <p className="text-xl font-semibold text-blue-600">
            ${chartData[chartData.length - 1]?.currentPrice.toFixed(2)}
          </p>
        </div>
        <div className="text-center p-2 bg-green-50 rounded">
          <p className="text-sm text-gray-600">Potential Savings</p>
          <p className={`text-xl font-semibold ${chartData[chartData.length - 1]?.savings > 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${Math.abs(chartData[chartData.length - 1]?.savings).toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}