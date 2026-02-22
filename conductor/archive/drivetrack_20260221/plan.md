# Implementation Plan: DriveTrack Dashboard Upgrade

## Phase 1: Navbar Component
<!-- execution: sequential -->

- [x] Task 1: Create Navbar component
  - Create `src/components/Navbar.tsx`
  - Full-width `bg-slate-900 border-b border-slate-800` bar
  - DriveTrack wordmark (car emoji + "DriveTrack" semibold white text)
  - Dashboard / Bookings nav tabs — active tab gets emerald pill via `useLocation()`
  - EnvironmentSwitcher relocated to right side of Navbar
  - No props needed; reads route state internally via react-router-dom

- [x] Task 2: Conductor - User Manual Verification 'Navbar Component' (Protocol in workflow.md)

## Phase 2: New Dashboard Components
<!-- execution: parallel -->
<!-- depends: -->

- [x] Task 1: Create StatCards component
  <!-- files: src/components/StatCards.tsx -->
  - 3-column grid: Total Savings | Best Deal | Biggest Surge
  - Total Savings: Σ (holdingPrice − latestPrice) where holdingPrice > latestPrice
  - Best Deal: booking with lowest latestPrice → click navigates to detail
  - Biggest Surge: booking most over hold → click navigates to detail
  - Null/empty states when no bookings
  - Accepts `bookings: BookingWithHistory[]` prop

- [x] Task 2: Create PriceTrendWave component
  <!-- files: src/components/PriceTrendWave.tsx -->
  - 120px-tall Recharts AreaChart
  - Computes composite 30-day rolling average across all bookings' focusCategory price history
  - Emerald stroke (#10b981) + gradient fill, direction label top-right
  - "↓ Trending down" (text-emerald-400) or "↑ Trending up" (text-amber-400) based on 7-day slope
  - No interactivity in v1
  - Accepts `bookings: BookingWithHistory[]` prop

- [x] Task 3: Create PriceWatchTable component
  <!-- files: src/components/PriceWatchTable.tsx -->
  - Compact table: Location | Category | Current | Hold | Δ | Status
  - Status: Under Hold (emerald) / Within 10% (amber) / Over Hold (red)
  - Rows sorted: red first, then amber, then emerald, then by location name
  - Each row navigates to `/booking/:id` on click
  - Accepts `bookings: BookingWithHistory[]` prop

- [x] Task 4: Conductor - User Manual Verification 'Dashboard Components' (Protocol in workflow.md)

## Phase 3: Integration & Layout
<!-- depends: phase1, phase2 -->

- [x] Task 1: Wire Navbar into App
  - Update `src/App.tsx`: render `<Navbar />` above `<Routes>`
  - Remove standalone `EnvironmentSwitcher` from Dashboard component (now inside Navbar)

- [x] Task 2: Rewire PriceTracker layout
  - Update `src/components/PriceTracker.tsx`:
    - Remove `PortfolioSummary` import and usage
    - Add `<StatCards bookings={bookings} />` at top of main content area
    - Add `<PriceTrendWave bookings={bookings} />` below stat cards
    - Add `<PriceWatchTable bookings={bookings} />` below trend wave
    - Booking cards grid remains below PriceWatchTable
  - Delete `src/components/PortfolioSummary.tsx`

- [x] Task 3: Conductor - User Manual Verification 'Integration & Layout' (Protocol in workflow.md)

## Phase 4: Build Validation
<!-- depends: phase3 -->

- [x] Task 1: Run `npm run build` — must exit 0; fix any TypeScript errors
  - Run `npm run lint` — must exit 0; fix any ESLint violations

- [x] Task 2: Conductor - User Manual Verification 'Build Validation' (Protocol in workflow.md)
