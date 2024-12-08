// src/lib/types.ts
export interface Booking {
    id: string
    location: string
    location_full_name: string
    pickup_date: string
    dropoff_date: string
    pickup_time: string
    dropoff_time: string
    focus_category: string
    holding_price?: number
    active: boolean
    created_at: string
  }
  
  export interface PriceHistory {
    id: string
    booking_id: string
    timestamp: string
    prices: Record<string, number>
    created_at: string
  }

  export interface HoldingPriceHistory {
    id: string;
    booking_id: string;
    price: number;
    effective_from: string;
    effective_to: string | null;
    created_at: string;
  }
  
  // Enhanced Booking type
  export interface BookingWithHistory extends Booking {
    price_history: PriceHistory[];
    holding_price_history: HoldingPriceHistory[];
    latestPrice: number;
    previousPrice: number;
    potentialSavings: number;
    priceChange: number;
    percentChange: number;
  }

  