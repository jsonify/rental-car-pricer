import { useState, useMemo } from 'react'
import {
  BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts'
import {
  format, startOfDay, startOfMonth, endOfMonth,
  eachDayOfInterval, startOfYear, endOfYear, eachMonthOfInterval,
  parseISO, isSameMonth
} from 'date-fns'
import { BookingWithHistory } from '@/lib/types'

type TimeFilter = 'today' | 'month' | 'year'

interface ChartBucket {
  label: string
  avg: number
}

interface Props {
  bookings: BookingWithHistory[]
}

function getBarColor(avg: number, avgHold: number): string {
  if (avgHold === 0) return '#10b981'
  if (avg <= avgHold) return '#10b981'
  if (avg <= avgHold * 1.15) return '#f59e0b'
  return '#f87171'
}

export function TrackedRentals({ bookings }: Props) {
  const [filter, setFilter] = useState<TimeFilter>('month')

  const avgHold = useMemo(() => {
    const holds = bookings
      .filter(b => b.holding_price != null && b.holding_price > 0)
      .map(b => b.holding_price as number)
    if (holds.length === 0) return 0
    return holds.reduce((sum, p) => sum + p, 0) / holds.length
  }, [bookings])

  const chartData = useMemo((): ChartBucket[] => {
    if (bookings.length === 0) return []
    const now = new Date()

    if (filter === 'today') {
      const todayStart = startOfDay(now)

      // Collect all records from today across all bookings
      const hourMap = new Map<string, number[]>()

      for (const booking of bookings) {
        for (const record of booking.price_history) {
          const ts = parseISO(record.created_at)
          if (ts >= todayStart) {
            const hourLabel = format(ts, 'HH:mm')
            const price = record.prices[booking.focus_category]
            if (price != null) {
              if (!hourMap.has(hourLabel)) hourMap.set(hourLabel, [])
              hourMap.get(hourLabel)!.push(price)
            }
          }
        }
      }

      const sortedHours = Array.from(hourMap.keys()).sort()

      if (sortedHours.length < 2) {
        // Show a single "Current Avg" bar using latestPrice
        const prices = bookings.map(b => b.latestPrice).filter(p => p > 0)
        if (prices.length === 0) return []
        const avg = prices.reduce((sum, p) => sum + p, 0) / prices.length
        return [{ label: 'Current Avg', avg }]
      }

      return sortedHours.map(label => {
        const vals = hourMap.get(label)!
        const avg = vals.reduce((sum, p) => sum + p, 0) / vals.length
        return { label, avg }
      })
    }

    if (filter === 'month') {
      const monthStart = startOfMonth(now)
      const monthEnd = endOfMonth(now)
      const days = eachDayOfInterval({ start: monthStart, end: monthEnd })

      const buckets: ChartBucket[] = []

      for (const day of days) {
        const dayEnd = new Date(day)
        dayEnd.setHours(23, 59, 59, 999)

        const dayPrices: number[] = []

        for (const booking of bookings) {
          // Find most recent record for this booking where created_at <= end of day and >= start of month
          const candidates = booking.price_history.filter(record => {
            const ts = parseISO(record.created_at)
            return ts >= monthStart && ts <= dayEnd
          })

          if (candidates.length === 0) continue

          // Sort by created_at descending, take most recent
          candidates.sort((a, b) =>
            parseISO(b.created_at).getTime() - parseISO(a.created_at).getTime()
          )
          const mostRecent = candidates[0]
          const price = mostRecent.prices[booking.focus_category]
          if (price != null) {
            dayPrices.push(price)
          }
        }

        if (dayPrices.length === 0) continue

        const avg = dayPrices.reduce((sum, p) => sum + p, 0) / dayPrices.length
        buckets.push({ label: format(day, 'MMM d'), avg })
      }

      return buckets
    }

    if (filter === 'year') {
      const yearStart = startOfYear(now)
      const yearEnd = endOfYear(now)
      const months = eachMonthOfInterval({ start: yearStart, end: yearEnd })

      const buckets: ChartBucket[] = []

      for (const month of months) {
        const monthPrices: number[] = []

        for (const booking of bookings) {
          const records = booking.price_history.filter(record => {
            const ts = parseISO(record.created_at)
            return isSameMonth(ts, month)
          })

          for (const record of records) {
            const price = record.prices[booking.focus_category]
            if (price != null) {
              monthPrices.push(price)
            }
          }
        }

        if (monthPrices.length === 0) continue

        const avg = monthPrices.reduce((sum, p) => sum + p, 0) / monthPrices.length
        buckets.push({ label: format(month, 'MMM'), avg })
      }

      return buckets
    }

    return []
  }, [bookings, filter])

  const periodAvg = useMemo(() => {
    if (chartData.length === 0) return 0
    return chartData.reduce((sum, b) => sum + b.avg, 0) / chartData.length
  }, [chartData])

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 mb-6">
      <div className="flex items-start justify-between mb-1">
        <div>
          <p className="text-slate-400 text-xs uppercase tracking-widest">Tracked Rentals</p>
          <p className="text-2xl font-semibold text-slate-100 mt-1">${periodAvg.toFixed(2)}</p>
          <p className="text-slate-500 text-xs mt-0.5">
            avg. across {bookings.length} tracked booking{bookings.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex gap-1">
          {(['today', 'month', 'year'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={
                filter === f
                  ? 'px-3 py-1 rounded-full text-xs font-medium bg-slate-700 text-white'
                  : 'px-3 py-1 rounded-full text-xs font-medium text-slate-500 hover:text-slate-300'
              }
            >
              {f === 'today' ? 'Today' : f === 'month' ? 'This Month' : 'This Year'}
            </button>
          ))}
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={120}>
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
            <XAxis
              dataKey="label"
              tick={{ fill: '#475569', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis hide />
            <Tooltip
              contentStyle={{
                background: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '6px',
                fontSize: '11px'
              }}
              labelStyle={{ color: '#94a3b8' }}
              formatter={(v: number) => [`$${v.toFixed(2)}`, 'Avg']}
            />
            <Bar dataKey="avg" radius={[2, 2, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={getBarColor(entry.avg, avgHold)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-slate-600 text-sm text-center py-8">No price history available</p>
      )}
    </div>
  )
}
