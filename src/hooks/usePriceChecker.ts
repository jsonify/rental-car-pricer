// src/hooks/usePriceChecker.ts
import { useState, useCallback } from 'react'

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
