// src/hooks/usePriceChecker.ts
import { useState, useCallback } from 'react'
import { faker } from '@faker-js/faker'

interface PriceCheck {
  isChecking: boolean
  lastChecked: string | null
  checkPrices: () => Promise<void>
  error: string | null
}

export const usePriceChecker = (): PriceCheck => {
  const [isChecking, setIsChecking] = useState(false)
  const [lastChecked, setLastChecked] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const checkPrices = useCallback(async () => {
    setIsChecking(true)
    setError(null)

    try {
      const response = await fetch('/api/check-prices', {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to check prices')
      }

      const data = await response.json()
      setLastChecked(data.timestamp)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsChecking(false)
    }
  }, [])

  return {
    isChecking,
    lastChecked,
    checkPrices,
    error
  }
}

// src/hooks/useBookings.ts
import { useState, useEffect } from 'react'
import { faker } from '@faker-js/faker'

interface Booking {
  id: string
  location: string
  location_full_name: string
  pickup_date: string
  dropoff_date: string
  focus_category: string
  price_history: any[]
  holding_price: number
}

export const useBookings = () => {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBookings = async () => {
      try {
        const response = await fetch('/api/bookings')
        if (!response.ok) throw new Error('Failed to fetch bookings')
        const data = await response.json()
        setBookings(data.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchBookings()
  }, [])

  return { bookings, loading, error }
}