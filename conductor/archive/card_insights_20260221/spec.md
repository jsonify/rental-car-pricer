# Spec: Dashboard Card Insights Enhancements

## Overview
Enhance the dashboard top section with richer price intelligence: a full-width Tracked Rentals aggregate chart above the existing 3-card row, and week-over-week context (% change + dollar delta vs last week) on the Best Deal and Biggest Surge cards. All data derived from the existing `useBookings()` hook — no new Supabase queries.

## Functional Requirements

### FR1 — Tracked Rentals Card (new, full-width, above StatCards)
- Full-width card with header "Tracked Rentals" and subtitle "avg. across N tracked bookings"
- Time filter pill: Today / This Month / This Year (default: This Month)
- Bar chart showing aggregate avg daily rate across all bookings for the selected period:
  - Today → one bar per available data point today (or single "current avg" if <2 points)
  - This Month → one bar per day of current month
  - This Year → one bar per month Jan–Dec
- Bar color by price vs average hold price: green (≤ hold avg), amber (≤ hold avg × 1.15), red (> hold avg × 1.15)
- Large current-period avg price displayed prominently above the chart
- Tooltip on hover: date label + avg price

### FR2 — Enhanced StatCards (Best Deal + Biggest Surge)
- **Best Deal card** adds below the price:
  - `▼ $X.XX from last week` in text-emerald-400 (or `▲` in text-red-400 if price rose)
  - `X.X% drop` with downward triangle or `X.X% rise` if up
- **Biggest Surge card** adds below the price:
  - `▲ +$X.XX from last week` in text-red-400
  - `X.X% surge` with upward triangle
- **"Last week" price**: scan that booking's `price_history` for the most recent record between 7–14 days ago; if none found, omit the delta line entirely (show nothing rather than mislead)

### FR3 — Layout
Page order after changes:
1. Tracked Rentals card (new, full-width)
2. StatCards 3-col row (enhanced)
3. PriceTrendWave (unchanged)
4. PriceWatchTable (unchanged)
5. Booking cards (unchanged)

## Non-Functional Requirements
- All data derived from existing `useBookings()` hook — no new Supabase queries
- `npm run build` and `npm run lint` must exit 0

## Acceptance Criteria
- [ ] Tracked Rentals card renders with time filter pills; switching filter updates bars
- [ ] Bars are color-coded against avg hold price across all bookings
- [ ] Tooltip shows date + avg on hover
- [ ] Best Deal and Biggest Surge cards show % change + dollar delta vs last week when history ≥7 days exists
- [ ] Delta lines are omitted (not shown as 0) when no 7–14 day history record exists
- [ ] `npm run build` and `npm run lint` exit 0

## Out of Scope
- Clicking bars to drill into day detail (backlogged as future track)
- Total Savings card enhancements
- Vehicles / Alerts nav tabs
- Any Python scraper or Supabase schema changes
