# Spec: DriveTrack Dashboard Upgrade

## Overview

Upgrade the existing React dashboard with DriveTrack-inspired components: a persistent navigation bar, a 3-card stat summary row, a 30-day price trend wave, and a compact Price Watch Table. All new components derive their data exclusively from the existing `useBookings()` hook — no new Supabase queries or schema changes required. The visual palette (emerald/slate) and sticky admin sidebar remain unchanged.

---

## Functional Requirements

### FR1 — Navbar
- Full-width `bg-slate-900 border-b border-slate-800` top bar, persistent across all routes
- **Left**: car emoji icon + "DriveTrack" wordmark (semibold, white)
- **Center**: tab navigation — "Dashboard" (route `/`) and "Bookings" (routes to first booking detail or shows count); active tab renders as an emerald pill
- **Right**: `EnvironmentSwitcher` relocated from its current inline position into the Navbar
- Uses `useLocation()` from react-router-dom for active-state detection
- No props needed; self-contained

### FR2 — 3-Card Stat Row (StatCards)
- Replaces `PortfolioSummary` component
- Three cards side-by-side in a grid:
  1. **Total Savings** — Σ (holdingPrice − latestPrice) for all bookings where hold > latest; shows "$X available" subtitle
  2. **Best Deal** — booking with the lowest `latestPrice`; shows vehicle class + airport code; click navigates to that booking's detail page
  3. **Biggest Surge** — booking whose `latestPrice` exceeds its `holdingPrice` by the most dollars; shows "↑ $X over hold"; click navigates to that booking's detail page
- Null/empty states shown when no bookings are loaded

### FR3 — Price Trend Flow Wave (PriceTrendWave)
- Full-width card, 120px tall Recharts `AreaChart`
- Data: composite 30-day rolling daily average across **all** bookings' `focusCategory` price histories
  - Each calendar day → average of all bookings' price on that day (using their most recent record ≤ that day)
  - Only dates within the past 30 days
- Emerald stroke (`#10b981`) + gradient fill (emerald → transparent)
- Direction label in top-right: "↓ Trending down" (text-emerald-400) when 7-day slope is negative; "↑ Trending up" (text-amber-400) when positive
- No interactivity required in v1

### FR4 — Price Watch Table (PriceWatchTable)
- Compact full-width table below the Trend Wave
- **Columns**: Location | Category | Current ($/day) | Hold ($/day) | Δ | Status
- **Status badge**:
  - 🟢 Under Hold — `latestPrice ≤ holdingPrice` (emerald)
  - 🟡 Within 10% — `latestPrice` within 10% above hold (amber)
  - 🔴 Over Hold — `latestPrice > holdingPrice × 1.10` (red)
- Entire row is clickable → navigates to `/booking/:id`
- Rows sorted by status severity (red first), then by location name

### FR5 — Layout
- Page order (top to bottom):
  1. `<Navbar />` (full-width, outside Routes main container)
  2. `<StatCards />` (replaces PortfolioSummary)
  3. `<PriceTrendWave />`
  4. `<PriceWatchTable />`
  5. Booking cards grid (existing — unchanged)
- Sticky admin sidebar (`w-72`) preserved on the right side of the main content area
- No changes to `BookingCard`, `BookingDetail`, or any Python backend files

---

## Non-Functional Requirements

- All derived values computed in existing `useBookings()` hook pattern — no new hooks or Supabase calls
- `npm run build` and `npm run lint` must exit 0 after implementation
- Emerald/slate dark palette unchanged; no new color tokens introduced
- Responsive: Navbar collapses gracefully on narrow viewports (flex-wrap allowed)

---

## Acceptance Criteria

- [ ] Navbar renders on every route; active tab is visually distinct (emerald pill)
- [ ] EnvironmentSwitcher appears inside Navbar and no longer renders elsewhere
- [ ] StatCards displays correct Total Savings, Best Deal location, and Biggest Surge location
- [ ] Clicking Best Deal or Biggest Surge cards navigates to the correct booking detail page
- [ ] PriceTrendWave renders with at least 1 data point when bookings have price history
- [ ] Direction label updates correctly based on 7-day trend direction
- [ ] PriceWatchTable shows all active bookings with correct Δ and Status badges
- [ ] PriceWatchTable rows navigate to correct detail page on click
- [ ] PortfolioSummary is removed with no orphan imports or references
- [ ] `npm run build` exits 0 (no TypeScript errors)
- [ ] `npm run lint` exits 0 (no ESLint errors)

---

## Out of Scope

- Light mode / theme toggle
- Navbar mobile hamburger menu (flex-wrap is sufficient for v1)
- Notifications bell or bookmark icon (DriveTrack PRD §3.1 — v2 consideration)
- Price drop / surge push notifications (existing email system unchanged)
- "Bookings" tab linking to a dedicated bookings list page (tab present but navigates to first booking detail)
- International currency (USD only)
- Any changes to Python scraper, CI workflows, or Supabase schema
