import { parseISO, subDays } from 'date-fns'
import { useNavigate } from 'react-router-dom'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  bookings: BookingWithHistory[]
}

function getLastWeekPrice(booking: BookingWithHistory): number | null {
  const now = new Date()
  const sevenDaysAgo = subDays(now, 7)
  const fourteenDaysAgo = subDays(now, 14)

  // Find the most recent price_history record between 7 and 14 days ago
  const candidates = booking.price_history
    .filter(h => {
      const d = parseISO(h.created_at)
      return d >= fourteenDaysAgo && d <= sevenDaysAgo
    })
    .sort((a, b) => parseISO(b.created_at).getTime() - parseISO(a.created_at).getTime())

  if (candidates.length === 0) return null
  return candidates[0].prices[booking.focus_category] ?? null
}

export function StatCards({ bookings }: Props) {
  const navigate = useNavigate()

  if (bookings.length === 0) return null

  // Card 1 — Total Savings
  const totalSavings = bookings.reduce((sum, b) => {
    return sum + Math.max(0, (b.holding_price ?? 0) - b.latestPrice)
  }, 0)

  // Card 2 — Best Deal (lowest latestPrice)
  const bestDeal = bookings.reduce<BookingWithHistory | null>((best, b) => {
    if (!best) return b
    return b.latestPrice < best.latestPrice ? b : best
  }, null)

  // Card 3 — Biggest Surge (highest latestPrice - holding_price, must be > 0)
  let surgeBooking: BookingWithHistory | null = null
  let maxSurge = 0
  for (const b of bookings) {
    const surge = b.latestPrice - (b.holding_price ?? 0)
    if (surge > maxSurge) {
      maxSurge = surge
      surgeBooking = b
    }
  }

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {/* Card 1 — Total Savings */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
        <p className="text-slate-400 text-xs uppercase tracking-widest mb-1">
          Total Savings Available
        </p>
        <p className={`text-2xl font-semibold ${totalSavings > 0 ? 'text-emerald-400' : 'text-slate-500'}`}>
          ${totalSavings.toFixed(2)}
        </p>
        <p className="text-slate-600 text-xs mt-1">
          across {bookings.length} booking{bookings.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Card 2 — Best Deal */}
      <div
        className={`bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 cursor-pointer hover:border-slate-700 transition-colors`}
        onClick={() => bestDeal && navigate(`/booking/${bestDeal.id}`)}
      >
        <p className="text-slate-400 text-xs uppercase tracking-widest mb-1">
          Best Deal
        </p>
        {bestDeal ? (
          <>
            <p className="text-2xl font-semibold text-emerald-400">
              ${bestDeal.latestPrice.toFixed(2)}/day
            </p>
            <p className="text-slate-500 text-xs mt-1">
              {bestDeal.location} · {bestDeal.focus_category}
            </p>
            {(() => {
              const lwp = getLastWeekPrice(bestDeal)
              if (lwp === null) return null
              const delta = bestDeal.latestPrice - lwp
              const pct = lwp > 0 ? Math.abs(delta / lwp * 100) : 0
              const dropped = delta < 0
              return (
                <div className="mt-2 space-y-0.5">
                  <p className={`text-xs font-medium ${dropped ? 'text-emerald-400' : 'text-red-400'}`}>
                    {dropped ? '▼' : '▲'} ${Math.abs(delta).toFixed(2)} from last week
                  </p>
                  <p className={`text-xs ${dropped ? 'text-emerald-500' : 'text-red-500'}`}>
                    {pct.toFixed(1)}% {dropped ? 'drop' : 'rise'}
                  </p>
                </div>
              )
            })()}
          </>
        ) : (
          <p className="text-2xl font-semibold text-slate-500">—</p>
        )}
      </div>

      {/* Card 3 — Biggest Surge */}
      <div
        className={`bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 ${surgeBooking ? 'cursor-pointer hover:border-slate-700 transition-colors' : ''}`}
        onClick={() => surgeBooking && navigate(`/booking/${surgeBooking.id}`)}
      >
        <p className="text-slate-400 text-xs uppercase tracking-widest mb-1">
          Biggest Surge
        </p>
        {surgeBooking ? (
          <>
            <p className="text-2xl font-semibold text-red-400">
              +${maxSurge.toFixed(2)} over hold
            </p>
            <p className="text-slate-500 text-xs mt-1">
              {surgeBooking.location} · {surgeBooking.focus_category}
            </p>
            {(() => {
              const lwp = getLastWeekPrice(surgeBooking)
              if (lwp === null) return null
              const delta = surgeBooking.latestPrice - lwp
              const pct = lwp > 0 ? Math.abs(delta / lwp * 100) : 0
              const dropped = delta < 0
              return (
                <div className="mt-2 space-y-0.5">
                  <p className={`text-xs font-medium ${dropped ? 'text-emerald-400' : 'text-red-400'}`}>
                    {dropped ? '▼' : '▲'} ${Math.abs(delta).toFixed(2)} from last week
                  </p>
                  <p className={`text-xs ${dropped ? 'text-emerald-500' : 'text-red-500'}`}>
                    {pct.toFixed(1)}% {dropped ? 'drop' : 'rise'}
                  </p>
                </div>
              )
            })()}
          </>
        ) : (
          <p className="text-2xl font-semibold text-slate-500">None</p>
        )}
      </div>
    </div>
  )
}
