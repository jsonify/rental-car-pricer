import { format } from "date-fns";

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

interface DataGridProps {
  booking: Booking;
}

export const DataGrid = ({ booking }: DataGridProps) => {
  const priceHistory = booking.price_history || [];
  const latestPrices = priceHistory[priceHistory.length - 1]?.prices || {};
  const categories = Object.keys(latestPrices).sort();

  return (
    <div className="rounded-md border">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="p-2 text-left font-medium">Category</th>
              <th className="p-2 text-right font-medium">Price</th>
              <th className="p-2 text-right font-medium">vs Focus</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => {
              const price = latestPrices[category];
              const priceDiff = price - (latestPrices[booking.focus_category] || 0);
              
              return (
                <tr 
                  key={category} 
                  className={`border-t ${category === booking.focus_category ? 'bg-blue-50' : ''}`}
                >
                  <td className="p-2">{category}</td>
                  <td className="p-2 text-right">${price.toFixed(2)}</td>
                  <td className={`p-2 text-right ${
                    priceDiff === 0 ? 'text-gray-500' :
                    priceDiff > 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {priceDiff === 0 ? '-' : 
                     `${priceDiff > 0 ? '+' : ''}$${Math.abs(priceDiff).toFixed(2)}`}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};