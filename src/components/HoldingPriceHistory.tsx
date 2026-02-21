// src/components/HoldingPriceHistory.tsx - New component to display history
import { format } from 'date-fns';
import type { HoldingPriceHistory as HoldingPriceHistoryType } from '@/lib/types';

interface HoldingPriceHistoryProps {
  history: HoldingPriceHistoryType[];
}

export const HoldingPriceHistory = ({ history }: HoldingPriceHistoryProps) => {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-medium mb-2">Holding Price History</h4>
      <div className="space-y-2">
        {history.map((entry) => (
          <div key={entry.id} className="flex justify-between text-sm">
            <span>
              {format(new Date(entry.effective_from), 'MMM d, yyyy')} -
              {entry.effective_to 
                ? format(new Date(entry.effective_to), 'MMM d, yyyy')
                : 'Present'}
            </span>
            <span className="font-medium">${entry.price.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};