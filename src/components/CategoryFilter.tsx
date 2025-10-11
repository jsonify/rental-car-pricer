import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface CategoryFilterProps {
  categories: string[];
  excludedCategories: string[];
  onToggleCategory: (category: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  focusCategory?: string;
}

export const CategoryFilter = ({
  categories,
  excludedCategories,
  onToggleCategory,
  onSelectAll,
  onDeselectAll,
  focusCategory
}: CategoryFilterProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const visibleCount = categories.length - excludedCategories.length;
  const totalCount = categories.length;

  return (
    <div className="bg-gray-50 border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-gray-700">Filter Categories</h3>
          <Badge variant="secondary" className="text-xs">
            {visibleCount} of {totalCount} shown
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSelectAll}
            className="text-xs h-7"
          >
            Show All
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onDeselectAll}
            className="text-xs h-7"
          >
            Hide All
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs h-7"
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </Button>
        </div>
      </div>

      {isExpanded && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          {categories.map((category) => {
            const isExcluded = excludedCategories.includes(category);
            const isFocus = category === focusCategory;

            return (
              <button
                key={category}
                onClick={() => onToggleCategory(category)}
                className={`
                  px-4 py-3 rounded-lg text-sm text-left transition-all
                  ${isExcluded
                    ? 'bg-gray-200 text-gray-400 line-through'
                    : 'bg-white text-gray-900 border-2 border-gray-300 hover:border-blue-500 hover:shadow-sm'
                  }
                  ${isFocus && !isExcluded ? 'font-bold border-blue-500 bg-blue-50 shadow-sm' : ''}
                `}
                title={`Click to ${isExcluded ? 'show' : 'hide'} ${category}`}
              >
                {category}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
