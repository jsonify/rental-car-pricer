import { useNavigate, useParams } from 'react-router-dom'
import { format, parseISO, differenceInDays } from 'date-fns'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { useBookings } from '@/hooks/useBookings'

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

export function BookingDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { bookings, loading } = useBookings()

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Loading…</p>
      </div>
    )
  }

  const booking = bookings.find(b => b.id === id)

  if (!booking) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Booking not found.</p>
      </div>
    )
  }

  const {
    location_full_name,
    pickup_date,
    dropoff_date,
    focus_category,
    holding_price,
    latestPrice,
    lowestPriceSeen,
    daysUntilPickup,
    price_history,
  } = booking

  const holdingPrice = holding_price ?? 0

  const pickupLabel = format(new Date(pickup_date), 'MMM d')
  const dropoffLabel = format(new Date(dropoff_date), 'MMM d')

  const daysLabel =
    daysUntilPickup > 0
      ? `${daysUntilPickup} days away`
      : daysUntilPickup === 0
        ? 'Today'
        : `${Math.abs(daysUntilPickup)} days ago`

  // Chart data
  const chartData = price_history
    .map(h => ({
      date: format(parseISO(h.created_at), 'MMM d'),
      price: h.prices?.[focus_category] ?? 0,
    }))
    .filter(d => d.price > 0)

  const todayLabel = format(new Date(), 'MMM d')
  const todayInRange = chartData.some(d => d.date === todayLabel)

  // Price velocity
  const velocityPoints = price_history
    .filter(h => (h.prices?.[focus_category] ?? 0) > 0)
    .sort((a, b) => a.created_at.localeCompare(b.created_at))

  let velocity: number | null = null
  if (velocityPoints.length >= 2) {
    const first = velocityPoints[0]
    const last = velocityPoints[velocityPoints.length - 1]
    const firstPrice = first.prices[focus_category]
    const lastPrice = last.prices[focus_category]
    const daysDiff = differenceInDays(parseISO(last.created_at), parseISO(first.created_at))
    if (daysDiff > 0) {
      velocity = (lastPrice - firstPrice) / daysDiff
    }
  }

  const velocityLabel = velocity === null
    ? '—'
    : velocity > 0
      ? `+${fmt(velocity)}/day`
      : `-${fmt(Math.abs(velocity))}/day`

  const velocityColor = velocity === null
    ? 'text-slate-400'
    : velocity > 0 ? 'text-red-400' : 'text-emerald-400'

  const urgencyBadge = velocity === null || velocity === 0
    ? { label: 'Monitoring', color: 'text-slate-400 bg-slate-800 border-slate-700' }
    : velocity > 0 && daysUntilPickup <= 14
      ? { label: '⚠ Rising with pickup near', color: 'text-amber-400 bg-amber-950 border-amber-800' }
      : velocity < 0
        ? { label: 'Good time to rebook', color: 'text-emerald-400 bg-emerald-950 border-emerald-800' }
        : { label: 'Monitoring', color: 'text-slate-400 bg-slate-800 border-slate-700' }

  // Price history table — sorted most recent first
  const sortedHistory = [...price_history]
    .filter(h => (h.prices?.[focus_category] ?? 0) > 0)
    .sort((a, b) => b.created_at.localeCompare(a.created_at))

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-3xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="text-slate-500 hover:text-slate-300 text-sm mb-4 flex items-center gap-1 transition-colors"
          >
            ← Back
          </button>
          <div className="flex items-start justify-between gap-3">
            <h1 className="text-2xl font-bold text-slate-100 leading-tight">{location_full_name}</h1>
            <StatusBadge latestPrice={latestPrice} holdingPrice={holding_price} />
          </div>
          <p className="text-sm text-slate-400 mt-1">
            {focus_category}
            <span className="text-slate-600 mx-1.5">·</span>
            {pickupLabel} – {dropoffLabel}
            <span className="text-slate-600 mx-1.5">·</span>
            {daysLabel}
          </p>
          <p className="text-3xl font-mono font-bold text-slate-100 mt-3">{fmt(latestPrice)}</p>
        </div>

        {/* Large area chart */}
        {chartData.length > 1 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-6">
            <p className="text-xs text-slate-500 uppercase tracking-widest mb-4">Price History</p>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="priceGradient-detail" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  domain={['auto', 'auto']}
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => `$${v}`}
                  width={55}
                />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: 8,
                    color: '#f1f5f9',
                    fontSize: 12,
                  }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                />
                {holdingPrice > 0 && (
                  <ReferenceLine
                    y={holdingPrice}
                    stroke="#fbbf24"
                    strokeDasharray="4 3"
                    label={{ value: `Hold $${holdingPrice.toFixed(0)}`, fill: '#fbbf24', fontSize: 11, position: 'insideTopRight' } as object}
                  />
                )}
                {lowestPriceSeen > 0 && lowestPriceSeen !== holdingPrice && (
                  <ReferenceLine
                    y={lowestPriceSeen}
                    stroke="#34d399"
                    strokeDasharray="4 3"
                    label={{ value: `Low $${lowestPriceSeen.toFixed(0)}`, fill: '#34d399', fontSize: 11, position: 'insideBottomRight' } as object}
                  />
                )}
                {todayInRange && (
                  <ReferenceLine
                    x={todayLabel}
                    stroke="#475569"
                    strokeDasharray="4 3"
                    label={{ value: 'Today', fill: '#475569', fontSize: 11, position: 'insideTopLeft' } as object}
                  />
                )}
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#34d399"
                  strokeWidth={2}
                  fill="url(#priceGradient-detail)"
                  dot={false}
                  activeDot={{ r: 4, fill: '#34d399' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Velocity strip */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
            <p className="text-slate-400 text-xs uppercase tracking-widest">Price Velocity</p>
            <p className={`text-2xl font-mono mt-1 ${velocityColor}`}>{velocityLabel}</p>
          </div>
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-5 py-4">
            <p className="text-slate-400 text-xs uppercase tracking-widest">Until Pickup</p>
            <p className="text-2xl font-mono text-slate-100 mt-1">{daysLabel}</p>
            <span className={`text-xs font-medium mt-1.5 inline-block px-2 py-0.5 rounded-full border ${urgencyBadge.color}`}>
              {urgencyBadge.label}
            </span>
          </div>
        </div>

        {/* Price history table */}
        {sortedHistory.length > 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <p className="text-xs text-slate-500 uppercase tracking-widest px-5 pt-4 pb-3">All Price Checks</p>
            <div className="max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-950">
                  <tr className="text-xs text-slate-500 uppercase">
                    <th className="text-left px-5 py-2 font-medium">Date</th>
                    <th className="text-right px-5 py-2 font-medium">Price</th>
                    <th className="text-right px-5 py-2 font-medium">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedHistory.map((record, i) => {
                    const price = record.prices[focus_category]
                    const prevRecord = sortedHistory[i + 1]
                    const prevPrice = prevRecord?.prices?.[focus_category]
                    const delta = prevPrice != null ? price - prevPrice : null

                    return (
                      <tr
                        key={record.id}
                        className={`border-t border-slate-800 ${i % 2 === 0 ? 'bg-slate-900' : 'bg-slate-800/30'}`}
                      >
                        <td className="px-5 py-2.5 text-slate-400 tabular-nums">
                          {format(parseISO(record.created_at), 'MMM d, h:mm a')}
                        </td>
                        <td className="px-5 py-2.5 text-right font-mono text-slate-200 tabular-nums">
                          {fmt(price)}
                        </td>
                        <td className="px-5 py-2.5 text-right font-mono tabular-nums">
                          {delta === null ? (
                            <span className="text-slate-600">—</span>
                          ) : delta < 0 ? (
                            <span className="text-emerald-400">↓ {fmt(Math.abs(delta))}</span>
                          ) : delta > 0 ? (
                            <span className="text-red-400">↑ {fmt(delta)}</span>
                          ) : (
                            <span className="text-slate-600">→ —</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
