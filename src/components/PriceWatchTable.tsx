import { useNavigate } from 'react-router-dom'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  bookings: BookingWithHistory[]
}

type StatusKey = 'over' | 'within' | 'under' | 'none'

function getStatus(booking: BookingWithHistory): StatusKey {
  const { holding_price, latestPrice } = booking
  if (holding_price == null) return 'none'
  if (latestPrice <= holding_price) return 'under'
  if (latestPrice <= holding_price * 1.10) return 'within'
  return 'over'
}

const STATUS_ORDER: Record<StatusKey, number> = {
  over: 0,
  within: 1,
  under: 2,
  none: 3,
}

function StatusBadge({ status }: { status: StatusKey }) {
  switch (status) {
    case 'over':
      return (
        <span className="px-2 py-0.5 rounded-full text-xs bg-red-950/50 text-red-400 border border-red-900/50">
          Over Hold
        </span>
      )
    case 'within':
      return (
        <span className="px-2 py-0.5 rounded-full text-xs bg-amber-950/50 text-amber-400 border border-amber-900/50">
          Within 10%
        </span>
      )
    case 'under':
      return (
        <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-950/50 text-emerald-400 border border-emerald-900/50">
          Under Hold
        </span>
      )
    case 'none':
      return (
        <span className="px-2 py-0.5 rounded-full text-xs bg-slate-800 text-slate-500 border border-slate-700">
          No Hold Set
        </span>
      )
  }
}

export function PriceWatchTable({ bookings }: Props) {
  const navigate = useNavigate()

  const sortedBookings = [...bookings].sort((a, b) => {
    const statusA = getStatus(a)
    const statusB = getStatus(b)
    const orderDiff = STATUS_ORDER[statusA] - STATUS_ORDER[statusB]
    if (orderDiff !== 0) return orderDiff
    return a.location.localeCompare(b.location)
  })

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden mb-6">
      <div className="px-5 py-3 border-b border-slate-800">
        <p className="text-slate-400 text-xs uppercase tracking-widest">Price Watch</p>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 text-xs border-b border-slate-800">
            <th className="text-left px-5 py-2 font-normal">Location</th>
            <th className="text-left px-3 py-2 font-normal">Category</th>
            <th className="text-right px-3 py-2 font-normal">Current</th>
            <th className="text-right px-3 py-2 font-normal">Hold</th>
            <th className="text-right px-3 py-2 font-normal">Δ</th>
            <th className="text-right px-5 py-2 font-normal">Status</th>
          </tr>
        </thead>
        <tbody>
          {sortedBookings.map(booking => {
            const status = getStatus(booking)
            const deltaPrefix = booking.priceChange >= 0 ? '+' : ''
            const deltaColor = booking.priceChange > 0 ? 'text-red-400' : booking.priceChange < 0 ? 'text-emerald-400' : 'text-slate-400'
            return (
              <tr
                key={booking.id}
                onClick={() => navigate('/booking/' + booking.id)}
                className="cursor-pointer hover:bg-slate-800/50 transition-colors border-b border-slate-800/50 last:border-0"
              >
                <td className="px-5 py-3 text-slate-200 font-medium">{booking.location}</td>
                <td className="px-3 py-3 text-slate-400">{booking.focus_category}</td>
                <td className="px-3 py-3 text-right text-slate-200">${booking.latestPrice.toFixed(2)}</td>
                <td className="px-3 py-3 text-right text-slate-400">
                  {booking.holding_price != null ? '$' + booking.holding_price.toFixed(2) : '—'}
                </td>
                <td className={`px-3 py-3 text-right ${deltaColor}`}>
                  {deltaPrefix}{booking.priceChange.toFixed(2)}
                </td>
                <td className="px-5 py-3 text-right">
                  <StatusBadge status={status} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {bookings.length === 0 && (
        <p className="text-slate-600 text-sm text-center py-8">No active bookings.</p>
      )}
    </div>
  )
}
