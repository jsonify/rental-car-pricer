// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for our data
export interface Booking {
  id: string
  location: string
  location_full_name: string
  pickup_date: string
  dropoff_date: string
  focus_category: string
  pickup_time: string
  dropoff_time: string
  holding_price?: number
  created_at: string
  active: boolean
}

export interface PriceHistory {
  id: string
  booking_id: string
  timestamp: string
  prices: Record<string, number>
  lowest_price?: {
    category: string
    price: number
  }
  created_at: string
}