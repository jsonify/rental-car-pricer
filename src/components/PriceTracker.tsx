import { useMemo } from 'react'
import { formatDistanceToNow, parseISO } from 'date-fns'
import { BookingCard } from './BookingCard'
import { StatCards } from './StatCards'
import { PriceTrendWave } from './PriceTrendWave'
import { PriceWatchTable } from './PriceWatchTable'
import { TestControls } from './TestControls'
import { isDevelopment } from '@/lib/environment'
import { useBookings } from '@/hooks/useBookings'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { createSupabaseClient } from '@/lib/supabase'
import { triggerWorkflow } from '@/lib/github'

export const PriceTracker = () => {
  const { bookings, loading, error, lastUpdated, refetch } = useBookings()
  const { isTestEnvironment } = useEnvironment()
  const supabase = useMemo(() => createSupabaseClient(isTestEnvironment), [isTestEnvironment])

  const handleUpdateHoldPrice = async (bookingId: string, bookingIndex: number, newPrice: number) => {
    if (isTestEnvironment) {
      // Test mode: update directly in the mock Supabase store
      await supabase
        .from('bookings')
        .update({ holding_price: newPrice })
        .eq('id', bookingId)
        .select()

      await supabase
        .from('holding_price_histories')
        .insert({
          booking_id: bookingId,
          price: newPrice,
          effective_from: new Date().toISOString(),
          effective_to: null
        })
        .select()

      await refetch()
    } else {
      // Production mode: trigger GitHub Actions workflow
      await triggerWorkflow({
        action: 'update-holding-prices',
        booking_updates_json: JSON.stringify([bookingIndex + 1, newPrice])
      })
      setTimeout(refetch, 5000)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <p className="text-slate-500 text-sm">Loading price data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <p className="text-red-400 text-sm">Error: {error}</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {isDevelopment && <TestControls />}

      <StatCards bookings={bookings} />

      <PriceTrendWave bookings={bookings} />

      <PriceWatchTable bookings={bookings} />

      {lastUpdated && (
        <p className="text-xs text-slate-600 -mt-4">
          Updated {formatDistanceToNow(parseISO(lastUpdated), { addSuffix: true })}
        </p>
      )}

      {bookings.length === 0 ? (
        <p className="text-slate-600 text-sm text-center py-12">No active bookings.</p>
      ) : (
        bookings.map((booking, index) => (
          <BookingCard
            key={booking.id}
            booking={booking}
            onUpdateHold={(newPrice) => handleUpdateHoldPrice(booking.id, index, newPrice)}
          />
        ))
      )}
    </div>
  )
}

export default PriceTracker
