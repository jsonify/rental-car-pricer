import { useMemo } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { format, subDays, parseISO, startOfDay, isAfter } from 'date-fns'
import type { BookingWithHistory } from '@/lib/types'

interface Props {
  bookings: BookingWithHistory[]
}

export function PriceTrendWave({ bookings }: Props) {
  const chartData = useMemo(() => {
    const today = startOfDay(new Date())
    const cutoff = subDays(today, 30)

    // Build list of all calendar dates from today-30 to today
    const dates: Date[] = []
    for (let i = 30; i >= 0; i--) {
      dates.push(subDays(today, i))
    }

    const result = dates.map((date) => {
      const dateStr = format(date, 'MMM d')
      const prices: number[] = []

      for (const booking of bookings) {
        const { focus_category, price_history } = booking
        if (!price_history || price_history.length === 0) continue

        // Find most recent history record with created_at <= date (end of that day)
        const endOfDate = new Date(date)
        endOfDate.setHours(23, 59, 59, 999)

        const eligible = price_history
          .filter((h) => {
            const parsed = parseISO(h.created_at)
            return parsed <= endOfDate && isAfter(parsed, cutoff)
          })
          .sort((a, b) =>
            parseISO(b.created_at).getTime() - parseISO(a.created_at).getTime()
          )

        if (eligible.length > 0) {
          const price = eligible[0].prices[focus_category]
          if (price && price > 0) {
            prices.push(price)
          }
        }
      }

      const avg = prices.length > 0
        ? prices.reduce((sum, p) => sum + p, 0) / prices.length
        : 0

      return { date: dateStr, avg }
    })

    // Filter out dates with no data
    return result.filter((d) => d.avg > 0)
  }, [bookings])

  const { directionLabel, directionColor } = useMemo(() => {
    if (chartData.length === 0) {
      return { directionLabel: '→ Stable', directionColor: 'text-slate-400' }
    }

    const windowSize = Math.min(7, Math.floor(chartData.length / 2))

    if (windowSize === 0) {
      return { directionLabel: '→ Stable', directionColor: 'text-slate-400' }
    }

    const firstWindow = chartData.slice(0, windowSize)
    const lastWindow = chartData.slice(chartData.length - windowSize)

    const firstAvg = firstWindow.reduce((sum, d) => sum + d.avg, 0) / firstWindow.length
    const lastAvg = lastWindow.reduce((sum, d) => sum + d.avg, 0) / lastWindow.length

    const slope = lastAvg - firstAvg

    if (slope < -0.01) {
      return { directionLabel: '↓ Trending down', directionColor: 'text-emerald-400' }
    } else if (slope > 0.01) {
      return { directionLabel: '↑ Trending up', directionColor: 'text-amber-400' }
    } else {
      return { directionLabel: '→ Stable', directionColor: 'text-slate-400' }
    }
  }, [chartData])

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl px-5 py-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <p className="text-slate-400 text-xs uppercase tracking-widest">30-Day Price Trend</p>
        <span className={`text-xs font-medium ${directionColor}`}>{directionLabel}</span>
      </div>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={120}>
          <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
            <defs>
              <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="avg"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#waveGradient)"
              dot={false}
            />
            <XAxis
              dataKey="date"
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
                fontSize: '11px',
              }}
              labelStyle={{ color: '#94a3b8' }}
              itemStyle={{ color: '#10b981' }}
              formatter={(v: number) => [`$${v.toFixed(2)}`, 'Avg']}
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-slate-600 text-sm text-center py-8">No price history available</p>
      )}
    </div>
  )
}
