import { format } from "date-fns";

interface PriceCheck {
  id: string;
  location: string;
  pickup_date: string;
  dropoff_date: string;
  focus_category: string;
  current_price: number;
  holding_price: number;
  checked_at: string;
}

interface DataGridProps {
  data: PriceCheck[];
}

export function DataGrid({ data }: DataGridProps) {
  return (
    <div className="rounded-md border">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="p-2 text-left font-medium">Location</th>
              <th className="p-2 text-left font-medium">Dates</th>
              <th className="p-2 text-left font-medium">Category</th>
              <th className="p-2 text-right font-medium">Price</th>
              <th className="p-2 text-right font-medium">Holding</th>
              <th className="p-2 text-right font-medium">Savings</th>
            </tr>
          </thead>
          <tbody>
            {data.map((check) => {
              const savings = check.holding_price - check.current_price;
              return (
                <tr key={check.id} className="border-t">
                  <td className="p-2">{check.location}</td>
                  <td className="p-2">
                    {format(new Date(check.pickup_date), "MMM d")} -{" "}
                    {format(new Date(check.dropoff_date), "MMM d, yyyy")}
                  </td>
                  <td className="p-2">{check.focus_category}</td>
                  <td className="p-2 text-right">${check.current_price.toFixed(2)}</td>
                  <td className="p-2 text-right">${check.holding_price.toFixed(2)}</td>
                  <td className={`p-2 text-right font-medium ${savings > 0 ? "text-green-600" : "text-red-600"}`}>
                    {savings > 0 ? "+" : ""}${savings.toFixed(2)}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}