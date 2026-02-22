import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import { parseISO } from 'date-fns'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  booking: BookingWithHistory
  onUpdateHold?: (newPrice: number) => Promise<void>
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


export function BookingCard({ booking, onUpdateHold }: Props) {
  const navigate = useNavigate()
  const [showBetterDeals, setShowBetterDeals] = useState(false)
  const [showAllCats, setShowAllCats] = useState(false)
  const [isEditingHold, setIsEditingHold] = useState(false)
  const [holdEditValue, setHoldEditValue] = useState('')

  const {
    location_full_name,
    pickup_date,
    dropoff_date,
    focus_category,
    holding_price,
    latestPrice,
    priceChange,
    lowestPriceSeen,
    allTimeHigh,
    latestPrices,
    daysUntilPickup,
    price_history,
  } = booking

  const holdingPrice = holding_price ?? 0
  const potentialSavings = holdingPrice > 0 ? holdingPrice - latestPrice : 0

  const betterDealsBaseline = holdingPrice > 0 ? holdingPrice : 0
  const betterDeals = betterDealsBaseline > 0
    ? Object.entries(latestPrices)
        .filter(([cat, price]) => cat !== focus_category && price < betterDealsBaseline)
        .map(([cat, price]) => ({ cat, price, savings: betterDealsBaseline - price }))
        .sort((a, b) => b.savings - a.savings)
    : []

  const allCatsSorted = Object.entries(latestPrices).sort(([, a], [, b]) => a - b)

  const pickupLabel = format(new Date(pickup_date), 'MMM d')
  const dropoffLabel = format(new Date(dropoff_date), 'MMM d')

  const daysLabel =
    daysUntilPickup > 0
      ? `${daysUntilPickup} days away`
      : daysUntilPickup === 0
        ? 'Today'
        : `${Math.abs(daysUntilPickup)} days ago`

  const chartData = price_history
    .map(h => ({
      date: format(parseISO(h.created_at), 'MMM d'),
      price: h.prices?.[focus_category] ?? 0,
    }))
    .filter(d => d.price > 0)

  const handleHoldConfirm = async () => {
    const parsed = parseFloat(holdEditValue)
    if (!isNaN(parsed) && onUpdateHold) {
      await onUpdateHold(parsed)
      setIsEditingHold(false)
    }
  }

  const topAccent = holding_price != null
    ? latestPrice <= holding_price
      ? 'border-t-2 border-t-emerald-500/40'
      : 'border-t-2 border-t-amber-500/40'
    : ''

  return (
    <div
      className={`bg-slate-900 rounded-xl p-6 border border-slate-700 ${topAccent} cursor-pointer`}
      onClick={() => navigate(`/booking/${booking.id}`)}
    >
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

        {/* Right column: Hold price */}
        {holdingPrice != null && holdingPrice > 0 && (
          <div className="text-right">
            <p className="text-slate-400 text-xs uppercase tracking-widest mb-1">Your Hold</p>
            {isEditingHold ? (
              <div className="flex items-center gap-1 justify-end">
                <input
                  type="number"
                  className="w-24 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm font-mono text-slate-100 text-right"
                  value={holdEditValue}
                  onChange={e => setHoldEditValue(e.target.value)}
                  autoFocus
                  onKeyDown={e => {
                    if (e.key === 'Enter') handleHoldConfirm()
                    if (e.key === 'Escape') setIsEditingHold(false)
                  }}
                />
                <button
                  className="text-emerald-400 hover:text-emerald-300 text-sm px-1"
                  onClick={e => { e.stopPropagation(); handleHoldConfirm() }}
                  disabled={!holdEditValue || isNaN(parseFloat(holdEditValue))}
                >✓</button>
                <button
                  className="text-slate-500 hover:text-slate-400 text-sm px-1"
                  onClick={e => { e.stopPropagation(); setIsEditingHold(false) }}
                >✕</button>
              </div>
            ) : (
              <div className="flex items-center gap-1 justify-end">
                <span className="text-xl font-mono text-amber-400">{fmt(holdingPrice)}</span>
                {onUpdateHold && (
                  <button
                    className="text-slate-600 hover:text-amber-400 transition-colors ml-1"
                    onClick={e => { e.stopPropagation(); setHoldEditValue(holdingPrice.toFixed(2)); setIsEditingHold(true) }}
                    title="Edit hold price"
                  >✎</button>
                )}
              </div>
            )}
            {/* savings/overage delta below hold price */}
            {potentialSavings > 0 ? (
              <p className="text-xs text-emerald-400 mt-0.5">saving {fmt(potentialSavings)}</p>
            ) : (
              <p className="text-xs text-red-400 mt-0.5">over by {fmt(Math.abs(potentialSavings))}</p>
            )}
          </div>
        )}
      </div>

      {/* Better Deals */}
      {betterDeals.length > 0 && (
        <div className="mb-4">
          <button
            onClick={e => { e.stopPropagation(); setShowBetterDeals(v => !v) }}
            className="w-full flex items-center justify-between text-sm font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
          >
            <span>⚡ {betterDeals.length} Better Deal{betterDeals.length > 1 ? 's' : ''} Available</span>
            <span className="text-slate-600">{showBetterDeals ? '↑' : '↓'}</span>
          </button>
          {showBetterDeals && (
            <div className="mt-2 space-y-1.5">
              {betterDeals.map(({ cat, price, savings }) => (
                <div key={cat} className="flex items-center justify-between text-sm">
                  <span className="text-slate-300">{cat}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-300 tabular-nums font-mono">{fmt(price)}</span>
                    <span className="text-xs font-medium text-emerald-400 bg-emerald-950 px-1.5 py-0.5 rounded">
                      -{fmt(savings)} ({((savings / betterDealsBaseline) * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* All Categories */}
      {allCatsSorted.length > 0 && (
        <div className="mb-4">
          <button
            onClick={e => { e.stopPropagation(); setShowAllCats(v => !v) }}
            className="text-xs text-slate-600 hover:text-slate-400 transition-colors"
          >
            {showAllCats ? 'Hide all categories ↑' : 'All categories ↓'}
          </button>
          {showAllCats && (
            <div className="mt-2 border border-slate-700 rounded-lg overflow-hidden">
              {allCatsSorted.map(([cat, price]) => {
                const isFocus = cat === focus_category
                return (
                  <div
                    key={cat}
                    className={`flex items-center justify-between px-3 py-2 text-sm border-b border-slate-800 last:border-b-0 ${
                      isFocus ? 'border-l-2 border-l-emerald-400 bg-emerald-950/30' : ''
                    }`}
                  >
                    <span className={isFocus ? 'text-emerald-400 font-medium' : 'text-slate-400'}>{cat}</span>
                    <span className={`tabular-nums font-mono ${isFocus ? 'text-slate-100' : 'text-slate-300'}`}>
                      {fmt(price)}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Area Chart — always visible when there is history */}
      {chartData.length > 1 && (
        <div className="px-5 pb-2">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`priceGradient-${booking.id}`} x1="0" y1="0" x2="0" y2="1">
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
              <Area
                type="monotone"
                dataKey="price"
                stroke="#34d399"
                strokeWidth={2}
                fill={`url(#priceGradient-${booking.id})`}
                dot={false}
                activeDot={{ r: 4, fill: '#34d399' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Stats footer */}
      <div className="grid grid-cols-3 divide-x divide-slate-800 text-center mt-4 pt-4 border-t border-slate-800">
        <div>
          <p className="text-slate-500 text-xs">All-time Low</p>
          <p className="font-mono text-slate-200 text-sm mt-0.5">{fmt(lowestPriceSeen)}</p>
        </div>
        <div>
          <p className="text-slate-500 text-xs">Your Hold</p>
          <p className="font-mono text-slate-200 text-sm mt-0.5">{holdingPrice ? fmt(holdingPrice) : '—'}</p>
        </div>
        <div>
          <p className="text-slate-500 text-xs">All-time High</p>
          <p className="font-mono text-slate-200 text-sm mt-0.5">{fmt(allTimeHigh)}</p>
        </div>
      </div>
    </div>
  )
}
