import { useState } from 'react'
import { format } from 'date-fns'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  booking: BookingWithHistory
}

const fmt = (price: number) => `$${price.toFixed(2)}`

const StatusBadge = ({ latestPrice, holdingPrice }: { latestPrice: number; holdingPrice?: number }) => {
  if (!holdingPrice) {
    return (
      <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-800 text-slate-500 border border-slate-700">
        No Hold
      </span>
    )
  }
  if (latestPrice <= holdingPrice) {
    return (
      <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
        Under Hold
      </span>
    )
  }
  return (
    <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-950 text-amber-400 border border-amber-800">
      Above Hold
    </span>
  )
}


export function BookingCard({ booking }: Props) {
  const [showHistory, setShowHistory] = useState(false)

  const {
    location_full_name,
    pickup_date,
    dropoff_date,
    focus_category,
    holding_price,
    latestPrice,
    priceChange,
    lowestPriceSeen,
    daysUntilPickup,
    price_history,
  } = booking

  const holdingDelta = holding_price != null ? latestPrice - holding_price : null

  const pickupLabel = format(new Date(pickup_date), 'MMM d')
  const dropoffLabel = format(new Date(dropoff_date), 'MMM d')

  const daysLabel =
    daysUntilPickup > 0
      ? `${daysUntilPickup} days away`
      : daysUntilPickup === 0
        ? 'Today'
        : `${Math.abs(daysUntilPickup)} days ago`

  const chartData = price_history
    .map(r => ({
      date: format(new Date(r.created_at), 'MMM d'),
      price: r.prices?.[focus_category],
    }))
    .filter((d): d is { date: string; price: number } => typeof d.price === 'number')

  const recentChecks = [...price_history]
    .reverse()
    .slice(0, 5)
    .filter(r => typeof r.prices?.[focus_category] === 'number')

  return (
    <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
      {/* Header row */}
      <div className="mb-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-100 leading-tight">{location_full_name}</h2>
          <StatusBadge latestPrice={latestPrice} holdingPrice={holding_price} />
        </div>
        <p className="text-sm text-slate-400 mt-1">
          {focus_category}
          <span className="text-slate-600 mx-1.5">·</span>
          {pickupLabel} – {dropoffLabel}
          <span className="text-slate-600 mx-1.5">·</span>
          {daysLabel}
        </p>
      </div>

      {/* Price hero — two-column */}
      <div className="flex items-start gap-6 mb-5">
        {/* Left: current price */}
        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wide">{focus_category}</p>
          <p className="text-4xl font-mono font-bold text-slate-100 tabular-nums">{fmt(latestPrice)}</p>
          <div className="mt-1 text-sm font-medium">
            {priceChange < 0 ? (
              <span className="text-emerald-400">↓ {fmt(Math.abs(priceChange))} vs last check</span>
            ) : priceChange > 0 ? (
              <span className="text-red-400">↑ {fmt(priceChange)} vs last check</span>
            ) : (
              <span className="text-slate-500">→ no change</span>
            )}
          </div>
        </div>

        {/* Right: holding price (hidden if no hold) */}
        {holding_price != null && holdingDelta !== null && (
          <div className="shrink-0 text-right">
            <p className="text-xs text-slate-500 mb-1 uppercase tracking-wide">Your Hold</p>
            <p className="text-2xl font-mono font-semibold text-slate-300 tabular-nums">{fmt(holding_price)}</p>
            <div className="mt-1 text-sm font-medium">
              {holdingDelta > 0 ? (
                <span className="text-amber-400">↑ {fmt(holdingDelta)} above</span>
              ) : holdingDelta < 0 ? (
                <span className="text-emerald-400">↓ {fmt(Math.abs(holdingDelta))} below</span>
              ) : (
                <span className="text-slate-500">at hold price</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Stats footer */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-slate-500 border-t border-slate-700 pt-4">
        {lowestPriceSeen > 0 && (
          <span>
            All-time low:{' '}
            <span className={lowestPriceSeen === latestPrice ? 'text-green-400 font-medium' : 'text-slate-300'}>
              {fmt(lowestPriceSeen)}
            </span>
          </span>
        )}
        {holding_price && (
          <span>
            Holding: <span className="text-slate-300">{fmt(holding_price)}</span>
          </span>
        )}
      </div>

      {/* Zone 2 toggle */}
      {chartData.length > 1 && (
        <button
          onClick={() => setShowHistory(v => !v)}
          className="mt-4 text-xs text-slate-600 hover:text-slate-400 transition-colors"
        >
          {showHistory ? 'Hide history ↑' : 'Show history ↓'}
        </button>
      )}

      {/* Zone 2 — detail panel */}
      {showHistory && (
        <div className="mt-4 space-y-4">
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: '#6b7280' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 11, fill: '#6b7280' }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => `$${v}`}
                width={52}
              />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 6 }}
                labelStyle={{ color: '#9ca3af', fontSize: 11 }}
                itemStyle={{ color: '#e5e7eb', fontSize: 12 }}
                formatter={(v: number) => [fmt(v), focus_category]}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#60a5fa"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#60a5fa' }}
              />
            </LineChart>
          </ResponsiveContainer>

          <div className="space-y-1">
            {recentChecks.map(r => (
              <div key={r.id} className="flex justify-between text-xs text-slate-500">
                <span>{format(new Date(r.created_at), 'MMM d, h:mm a')}</span>
                <span className="text-slate-300 tabular-nums">
                  {fmt(r.prices[focus_category])}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
