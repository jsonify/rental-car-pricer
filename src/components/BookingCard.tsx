import { useState } from 'react'
import { format } from 'date-fns'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  booking: BookingWithHistory
}

const fmt = (price: number) => `$${price.toFixed(2)}`

const DeltaBadge = ({
  delta,
  label,
  size = 'md',
}: {
  delta: number
  label: string
  size?: 'sm' | 'md'
}) => {
  if (delta === 0) return null
  const down = delta < 0
  const color = down ? 'text-green-400' : 'text-red-400'
  const arrow = down ? '↓' : '↑'
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm'
  return (
    <div className={`${textSize} ${color} font-medium`}>
      {arrow} {fmt(Math.abs(delta))} <span className="text-gray-500 font-normal">{label}</span>
    </div>
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
    changeFromBaseline,
    firstTrackedPrice,
    lowestPriceSeen,
    daysUntilPickup,
    price_history,
  } = booking

  const holdingDelta = holding_price ? latestPrice - holding_price : null

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
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      {/* Header row */}
      <div className="flex justify-between items-start mb-5">
        <div>
          <h2 className="text-lg font-semibold text-white leading-tight">{location_full_name}</h2>
          <p className="text-sm text-gray-400 mt-0.5">{focus_category}</p>
        </div>
        <div className="text-right shrink-0 ml-4">
          <p className="text-sm text-gray-300">
            {pickupLabel} – {dropoffLabel}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">{daysLabel}</p>
        </div>
      </div>

      {/* Price + deltas */}
      <div className="flex items-end gap-6 mb-5">
        <div>
          <p className="text-xs text-gray-500 mb-1 uppercase tracking-wide">Current price</p>
          <p className="text-5xl font-bold text-white tabular-nums">{fmt(latestPrice)}</p>
        </div>
        <div className="pb-1 space-y-1.5">
          {holdingDelta !== null && (
            <DeltaBadge delta={holdingDelta} label="vs what you booked" />
          )}
          {firstTrackedPrice > 0 && (
            <DeltaBadge delta={changeFromBaseline} label="since tracking began" size="sm" />
          )}
        </div>
      </div>

      {/* Stats footer */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-500 border-t border-gray-800 pt-4">
        {lowestPriceSeen > 0 && (
          <span>
            All-time low:{' '}
            <span className={lowestPriceSeen === latestPrice ? 'text-green-400 font-medium' : 'text-gray-300'}>
              {fmt(lowestPriceSeen)}
            </span>
          </span>
        )}
        {holding_price && (
          <span>
            Holding: <span className="text-gray-300">{fmt(holding_price)}</span>
          </span>
        )}
      </div>

      {/* Zone 2 toggle */}
      {chartData.length > 1 && (
        <button
          onClick={() => setShowHistory(v => !v)}
          className="mt-4 text-xs text-gray-600 hover:text-gray-400 transition-colors"
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
              <div key={r.id} className="flex justify-between text-xs text-gray-500">
                <span>{format(new Date(r.created_at), 'MMM d, h:mm a')}</span>
                <span className="text-gray-300 tabular-nums">
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
