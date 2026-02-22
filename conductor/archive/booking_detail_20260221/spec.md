# Booking Detail Page

## Overview
Add a full-page detail route (`#/booking/:id`) reachable by clicking any booking card.
The page provides deeper analytics than the card summary: a large area chart, a price
velocity panel ($/day rate + days-to-pickup urgency), and a complete scrollable price
history table. Uses react-router-dom with HashRouter for GitHub Pages compatibility.

## Functional Requirements

### FR1: Routing
- Install `react-router-dom` (+ types included in package)
- Wrap the app in `<HashRouter>` in `src/main.tsx`
- Routes: `#/` → existing dashboard layout; `#/booking/:id` → BookingDetail page
- Clicking a booking card navigates to its detail page
- Interactive elements on the card (hold edit ✎, ✓, ✕, Better Deals toggle, All
  Categories toggle) must NOT trigger card navigation (`e.stopPropagation()`)
- Detail page has a `← Back` button (`useNavigate(-1)`)

### FR2: Detail Page Layout
1. **Header**: `← Back` link | location name (large) | pickup–dropoff dates |
   days-away label | StatusBadge (Under Hold / Above Hold / No Hold)
2. **Large chart**: 320px AreaChart, same emerald gradient + reference lines as card
3. **Velocity strip**: 2-stat card row — $/day rate + days-to-pickup urgency context
4. **Price history table**: scrollable, all price check records, most recent first

### FR3: Large Area Chart
- Reuse the same Recharts AreaChart pattern from BookingCard (emerald gradient, amber
  hold reference line, emerald low reference line)
- Height: 320px (vs 200px on card)
- Add a vertical `ReferenceLine` at today's date on the X-axis (stroke="#475569",
  strokeDasharray="4 3", label "Today") if today falls within the data range
- Tooltip shows date + price formatted as `$XX.XX`

### FR4: Price Velocity
- **$/day rate**: linear slope across all available non-zero price history points for
  the focus category. Formula: `(lastPrice - firstPrice) / daysBetweenFirstAndLast`.
  If fewer than 2 data points, show "—" (not enough data).
  Display: `+$X.XX/day` (red, ↑) or `-$X.XX/day` (emerald, ↓)
- **Days-to-pickup urgency**: display days remaining with a context badge:
  - velocity > 0 && daysUntilPickup ≤ 14 → amber "⚠ Rising with pickup near"
  - velocity < 0 → emerald "Good time to rebook"
  - else → slate "Monitoring"
- Render as a 2-card strip matching PortfolioSummary style (`flex gap-4`,
  `bg-slate-900 border border-slate-800 rounded-xl px-5 py-4`)

### FR5: Price History Table
- Columns: **Date/Time** | **Price** | **Change**
- Change column: emerald `↓ -$X.XX` for drops, red `↑ +$X.XX` for rises,
  slate `→ —` for first record or no change
- Most recent row first (sort by `created_at` descending)
- Scrollable container: `max-h-96 overflow-y-auto rounded-lg border border-slate-800`
- Alternating row shading: `bg-slate-900` / `bg-slate-800/30`
- Sticky header row: `sticky top-0 bg-slate-950`
- Shows the focus_category price for each price check record

## Non-Functional Requirements
- Consistent dark theme (bg-slate-950, slate-900 cards, emerald/amber/red accents)
- No additional Supabase round-trips — filter the existing `useBookings()` result by ID
- TypeScript strict — no `any` except where Recharts label props require it (cast as `any`)

## Acceptance Criteria
- [ ] Clicking a booking card navigates to `#/booking/:id`
- [ ] Clicking hold edit ✎ or better deals/all-categories toggles does NOT navigate
- [ ] `← Back` returns to dashboard
- [ ] Large chart renders with correct data, reference lines, and today marker
- [ ] Velocity strip shows $/day with correct sign/color and urgency badge
- [ ] Price history table shows all records, most recent first, color-coded changes
- [ ] `npm run build` passes with 0 TypeScript errors

## Out of Scope
- Date range filtering / zooming the chart
- Editing booking fields from the detail page (admin panel handles this)
- Per-category price breakdown chart on the detail page
