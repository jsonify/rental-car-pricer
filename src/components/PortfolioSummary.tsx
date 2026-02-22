// src/components/PortfolioSummary.tsx
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  bookings: BookingWithHistory[]
}

export const PortfolioSummary = ({ bookings }: Props) => {
  // Total savings: sum of max(0, holdingPrice - latestPrice) across all bookings
  const totalSavings = bookings.reduce((sum, b) => {
    const hp = b.holding_price ?? 0
    return sum + Math.max(0, hp - b.latestPrice)
  }, 0)

  // Trend: count bookings where latest < previous (price dropped)
  const trendingDown = bookings.filter(b => b.priceChange < 0).length
  const total = bookings.length

  // Trend color: emerald if all down, amber if mixed, red if all up
  const allDown = trendingDown === total && total > 0
  const allUp = trendingDown === 0 && total > 0
  const trendColor = allDown ? 'text-emerald-400' : allUp ? 'text-red-400' : 'text-amber-400'
  const trendArrow = allDown ? '↓' : allUp ? '↑' : '↕'

  const savingsColor = totalSavings > 0 ? 'text-emerald-400' : 'text-slate-500'

  if (bookings.length === 0) return null

  return (
    <div className="flex gap-4 mb-6">
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
        <p className="text-slate-400 text-xs uppercase tracking-widest">Savings Available</p>
        <p className={`text-2xl font-mono mt-1 ${savingsColor}`}>
          ${totalSavings.toFixed(2)}
        </p>
      </div>
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
        <p className="text-slate-400 text-xs uppercase tracking-widest">Price Trend</p>
        <p className={`text-2xl font-mono mt-1 ${trendColor}`}>
          {trendingDown} / {total} {trendArrow}
        </p>
      </div>
    </div>
  )
}
