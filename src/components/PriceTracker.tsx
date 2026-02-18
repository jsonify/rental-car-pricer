import { formatDistanceToNow, parseISO } from 'date-fns'
import { BookingCard } from './BookingCard'
import { TestControls } from './TestControls'
import { isDevelopment } from '@/lib/environment'
import { useBookings } from '@/hooks/useBookings'

export const PriceTracker = () => {
  const { bookings, loading, error, lastUpdated } = useBookings()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <p className="text-gray-500 text-sm">Loading price data...</p>
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

      <div className="flex justify-between items-baseline">
        <h1 className="text-sm font-medium text-gray-400 uppercase tracking-widest">
          Rentals
        </h1>
        {lastUpdated && (
          <p className="text-xs text-gray-600">
            Updated {formatDistanceToNow(parseISO(lastUpdated), { addSuffix: true })}
          </p>
        )}
      </div>

      {bookings.length === 0 ? (
        <p className="text-gray-600 text-sm text-center py-12">No active bookings.</p>
      ) : (
        bookings.map(booking => (
          <BookingCard key={booking.id} booking={booking} />
        ))
      )}
    </div>
  )
}

export default PriceTracker
