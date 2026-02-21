// src/hooks/useBookings.ts
import { useState, useEffect, useCallback, useMemo } from 'react'
import { differenceInCalendarDays } from 'date-fns'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { createSupabaseClient } from '@/lib/supabase'
import type { Booking, BookingWithHistory, PriceHistory } from '@/lib/types'

export const useBookings = () => {
  const [bookings, setBookings] = useState<BookingWithHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const { isTestEnvironment } = useEnvironment()
  const supabase = useMemo(() => createSupabaseClient(isTestEnvironment), [isTestEnvironment])

  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch active bookings
      const { data: bookingsData, error: bookingsError } = await supabase
        .from('bookings')
        .select('*')
        .eq('active', true)
        .order('pickup_date', { ascending: true })

      if (bookingsError) throw bookingsError

      // Fetch related data for each booking
      const bookingsWithHistory = await Promise.all(
        (bookingsData || []).map(async (booking: Booking) => {
          // Fetch price histories
          const { data: priceHistories, error: historiesError } = await supabase
            .from('price_histories')
            .select('*')
            .eq('booking_id', booking.id)
            .order('created_at', { ascending: true })

          if (historiesError) throw historiesError

          // Fetch holding price histories
          const { data: holdingPriceHistory, error: holdingError } = await supabase
            .from('holding_price_histories')
            .select('*')
            .eq('booking_id', booking.id)
            .order('effective_from', { ascending: true })

          if (holdingError) throw holdingError

          // Calculate derived values
          const histories = priceHistories || []
          const latestHistory = histories[histories.length - 1]
          const previousHistory = histories[histories.length - 2]
          const firstHistory = histories[0]

          const latestPrice = latestHistory?.prices?.[booking.focus_category] || 0
          const previousPrice = previousHistory?.prices?.[booking.focus_category] || 0
          const holdingPrice = booking.holding_price || 0
          const potentialSavings = Math.max(0, holdingPrice - latestPrice)
          const priceChange = latestPrice - previousPrice
          const percentChange = previousPrice ? (priceChange / previousPrice) * 100 : 0

          const firstTrackedPrice = firstHistory?.prices?.[booking.focus_category] || 0
          const changeFromBaseline = latestPrice - firstTrackedPrice
          const focusPrices = histories
            .map((r: PriceHistory) => r.prices?.[booking.focus_category])
            .filter((p: number | undefined): p is number => typeof p === 'number' && p > 0)
          const lowestPriceSeen = focusPrices.length > 0 ? Math.min(...focusPrices) : 0
          const allTimeHigh = focusPrices.length > 0 ? Math.max(...focusPrices) : 0
          const latestPrices: Record<string, number> = latestHistory?.prices ?? {}
          const daysUntilPickup = differenceInCalendarDays(new Date(booking.pickup_date), new Date())

          return {
            ...booking,
            price_history: histories,
            holding_price_history: holdingPriceHistory || [],
            latestPrice,
            previousPrice,
            potentialSavings,
            priceChange,
            percentChange,
            firstTrackedPrice,
            changeFromBaseline,
            lowestPriceSeen,
            allTimeHigh,
            latestPrices,
            daysUntilPickup
          }
        })
      )

      setBookings(bookingsWithHistory)
      setLastUpdated(new Date().toISOString())
    } catch (err) {
      console.error('Error fetching bookings:', err)
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }, [supabase])

  useEffect(() => {
    fetchBookings()
  }, [fetchBookings])

  return {
    bookings,
    loading,
    error,
    lastUpdated,
    refetch: fetchBookings
  }
}
