// src/lib/price-checker.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export interface PriceCheckResult {
  success: boolean
  message: string
  checked_at: string
  notifications: PriceNotification[]
}

export interface PriceNotification {
  booking_id: string
  location: string
  category: string
  new_price: number
  old_price: number
  holding_price: number | null
  price_change: number
}

export interface PriceTrends {
  success: boolean
  booking_id: string
  focus_category: string
  stats: {
    lowest_price: number
    highest_price: number
    average_price: number
    total_checks: number
  }
  current_price: number
  holding_price: number | null
}

export const priceChecker = {
  checkPrices: async (): Promise<PriceCheckResult> => {
    try {
      const { data, error } = await supabase
        .rpc('check_rental_prices')

      if (error) throw error
      return data
    } catch (error) {
      console.error('Error checking prices:', error)
      throw new Error('Failed to check prices')
    }
  },

  getPriceTrends: async (bookingId: string): Promise<PriceTrends> => {
    try {
      const { data, error } = await supabase
        .rpc('get_price_trends', { booking_id_param: bookingId })

      if (error) throw error
      return data
    } catch (error) {
      console.error('Error getting price trends:', error)
      throw new Error('Failed to get price trends')
    }
  }
}