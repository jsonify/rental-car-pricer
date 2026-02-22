# Implementation Plan: Dashboard Card Insights Enhancements

## Phase 1: TrackedRentals Component
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Create TrackedRentals component
  <!-- files: src/components/TrackedRentals.tsx -->
  - Create `src/components/TrackedRentals.tsx`
  - Time filter state: 'month' (default) | 'today' | 'year'
  - Compute bar data from all bookings' price_history:
    - Today → group records by booking, avg latest price for today
    - This Month → one bar per calendar day of current month, avg across all bookings per day
    - This Year → one bar per month (Jan–Dec), avg across all bookings per month
  - Avg hold price across all bookings for color threshold
  - Bar colors: green (#10b981, ≤ hold avg), amber (#f59e0b, ≤ hold avg × 1.15), red (#f87171, > hold avg × 1.15)
  - Use Recharts BarChart with Cell for per-bar coloring
  - Large avg price for selected period displayed above chart
  - Tooltip: date label + `$X.XX avg`
  - Subtitle: "avg. across N tracked bookings"
  - Accepts `bookings: BookingWithHistory[]` prop

- [x] Task 2: Conductor - User Manual Verification 'TrackedRentals Component' (Protocol in workflow.md)

## Phase 2: Enhance StatCards
<!-- execution: sequential -->
<!-- depends: -->

- [x] Task 1: Add week-over-week signals to Best Deal + Biggest Surge cards
  <!-- files: src/components/StatCards.tsx -->
  - Modify `src/components/StatCards.tsx`
  - Helper: `getLastWeekPrice(booking, priceHistory[])` → scan price_history for most recent record with created_at between 7–14 days ago; return price or null
  - Best Deal card: if lastWeekPrice found → compute dollar delta + % change → render `▼ $X.XX from last week` + `X.X% drop` (or `▲` variants if price rose)
  - Biggest Surge card: same pattern
  - If no record in 7–14 day window: omit delta lines entirely
  - Triangle: `▼` (text-emerald-400) for price drop (good), `▲` (text-red-400) for price rise (bad)

- [x] Task 2: Conductor - User Manual Verification 'StatCards Enhancement' (Protocol in workflow.md)

## Phase 3: Integration & Build Validation
<!-- depends: phase1, phase2 -->

- [x] Task 1: Wire TrackedRentals into PriceTracker
  - Update `src/components/PriceTracker.tsx`:
    - Add `import { TrackedRentals } from './TrackedRentals'`
    - Add `<TrackedRentals bookings={bookings} />` above `<StatCards />`

- [x] Task 2: Run build + lint
  - Run `npm run build` — must exit 0
  - Run `npm run lint` — must exit 0
  - Fix any type errors or lint violations

- [x] Task 3: Conductor - User Manual Verification 'Integration & Build Validation' (Protocol in workflow.md)
