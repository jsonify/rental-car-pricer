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

// Color palette for different categories
const CATEGORY_COLORS = [
  "#2563eb", // blue
  "#059669", // green
  "#dc2626", // red
  "#7c3aed", // purple
  "#ea580c", // orange
  "#0891b2", // cyan
  "#be185d", // pink
  "#4f46e5", // indigo
  "#65a30d", // lime
  "#0284c7", // sky
];

export const Chart = ({ booking, excludedCategories = [] }: { booking: any; excludedCategories?: string[] }) => {
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

    // Map the price history with all categories
    return booking.price_history.map(record => {
      const dataPoint: any = {
        timestamp: record.timestamp,
        holdingPrice: holdingPrices.get(record.timestamp) || booking.holding_price || 0
      };

      // Add all category prices to the data point
      if (record.prices) {
        Object.entries(record.prices).forEach(([category, price]) => {
          dataPoint[category] = price;
        });
      }

      return dataPoint;
    });
  }, [booking]);

  // Get all unique categories from the price history, excluding filtered categories
  const categories = useMemo(() => {
    if (!booking?.price_history || booking.price_history.length === 0) return [];

    const categorySet = new Set<string>();
    booking.price_history.forEach(record => {
      if (record.prices) {
        Object.keys(record.prices).forEach(category => {
          // Exclude categories based on user filter
          if (!excludedCategories.includes(category)) {
            categorySet.add(category);
          }
        });
      }
    });

    // Sort categories with focus category first
    return Array.from(categorySet).sort((a, b) => {
      if (a === booking.focus_category) return -1;
      if (b === booking.focus_category) return 1;
      return a.localeCompare(b);
    });
  }, [booking, excludedCategories]);

  // Calculate dynamic Y-axis domain based on visible categories and holding price
  const yAxisDomain = useMemo(() => {
    if (chartData.length === 0 || categories.length === 0) {
      return ['auto', 'auto'];
    }

    let minPrice = Infinity;
    let maxPrice = -Infinity;

    // Check all visible category prices and holding price
    chartData.forEach(dataPoint => {
      // Check visible category prices
      categories.forEach(category => {
        const price = dataPoint[category];
        if (typeof price === 'number' && !isNaN(price)) {
          minPrice = Math.min(minPrice, price);
          maxPrice = Math.max(maxPrice, price);
        }
      });

      // Include holding price in the range
      const holdingPrice = dataPoint.holdingPrice;
      if (typeof holdingPrice === 'number' && !isNaN(holdingPrice) && holdingPrice > 0) {
        minPrice = Math.min(minPrice, holdingPrice);
        maxPrice = Math.max(maxPrice, holdingPrice);
      }
    });

    // If we found valid prices, add padding (10% on each side)
    if (minPrice !== Infinity && maxPrice !== -Infinity) {
      const padding = (maxPrice - minPrice) * 0.1;
      return [
        Math.floor(Math.max(0, minPrice - padding)),
        Math.ceil(maxPrice + padding)
      ];
    }

    return ['auto', 'auto'];
  }, [chartData, categories]);

  if (chartData.length === 0) {
    return (
      <div className="h-[500px] flex items-center justify-center text-gray-500">
        No price history available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Custom Legend Grid */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
          {categories.map((category, index) => {
            const isFocusCategory = category === booking.focus_category;
            const color = CATEGORY_COLORS[index % CATEGORY_COLORS.length];

            return (
              <div
                key={category}
                className={`flex items-center gap-2 text-xs ${
                  isFocusCategory ? 'font-bold' : 'font-normal'
                }`}
              >
                <div
                  className="w-4 h-0.5 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="truncate" title={category}>
                  {category}
                </span>
              </div>
            );
          })}
          {/* Holding Price Legend */}
          <div className="flex items-center gap-2 text-xs font-normal">
            <div
              className="w-4 h-0.5 rounded"
              style={{
                backgroundColor: '#dc2626',
                backgroundImage: 'repeating-linear-gradient(90deg, #dc2626 0, #dc2626 3px, transparent 3px, transparent 6px)'
              }}
            />
            <span className="truncate">Holding Price</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
            <XAxis
              dataKey="timestamp"
              tick={{ fill: '#666' }}
              fontSize={12}
            />
            <YAxis
              domain={yAxisDomain}
              tickFormatter={(value) => `$${value}`}
              tick={{ fill: '#666' }}
              fontSize={12}
              width={80}
            />
            <Tooltip
              formatter={(value) => [`$${typeof value === 'number' ? value.toFixed(2) : value}`, '']}
              contentStyle={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '8px',
                border: '1px solid #e5e7eb'
              }}
            />

            {/* Render a line for each category */}
            {categories.map((category, index) => {
              const isFocusCategory = category === booking.focus_category;
              const color = CATEGORY_COLORS[index % CATEGORY_COLORS.length];

              return (
                <Line
                  key={category}
                  type="monotone"
                  dataKey={category}
                  name={category}
                  stroke={color}
                  strokeWidth={isFocusCategory ? 3 : 2}
                  dot={{ r: isFocusCategory ? 4 : 2 }}
                  activeDot={{ r: isFocusCategory ? 6 : 4 }}
                  opacity={isFocusCategory ? 1 : 0.7}
                />
              );
            })}

            {/* Holding Price line */}
            <Line
              type="step"
              dataKey="holdingPrice"
              name="Holding Price"
              stroke="#dc2626"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Chart;