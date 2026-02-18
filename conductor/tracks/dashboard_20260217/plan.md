# Plan: Dashboard Redesign

**Track ID:** `dashboard_20260217`

---

## Phase 1: Data Layer Enhancements

Extend `useBookings.ts` and `BookingWithHistory` to expose all derived values needed by the new UI. No visual changes in this phase.

- [ ] Task: Add `firstTrackedPrice` to `BookingWithHistory` in `src/lib/types.ts`
  - Earliest `price_history` record's price for `focus_category` (or 0 if no history)
- [ ] Task: Add `changeFromBaseline` to `BookingWithHistory` in `src/lib/types.ts`
  - `latestPrice - firstTrackedPrice`
- [ ] Task: Add `lowestPriceSeen` to `BookingWithHistory` in `src/lib/types.ts`
  - `Math.min(...price_history.map(r => r.prices[focus_category]).filter(Boolean))`
- [ ] Task: Add `daysUntilPickup` to `BookingWithHistory` in `src/lib/types.ts`
  - `differenceInCalendarDays(parseISO(pickup_date), new Date())`
- [ ] Task: Compute the four new fields in `useBookings.ts` and include in returned objects
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Data Layer Enhancements' (Protocol in workflow.md)

---

## Phase 2: New BookingCard Component

Create `src/components/BookingCard.tsx` — the replacement for the per-booking section in `PriceTracker.tsx`.

- [ ] Task: Create `src/components/BookingCard.tsx` with Zone 1 (primary stats, always visible)
  - Location name, dates, focus category label
  - Large current price
  - vs-holding delta with green/red color + arrow
  - vs-baseline delta
  - All-time low and holding price bottom row
  - Days until pickup in header
- [ ] Task: Add Zone 2 (collapsible detail panel) to `BookingCard.tsx`
  - "Show history" toggle button
  - Simple single-line Recharts LineChart for focus_category price over time
  - Last 5 price checks listed as `<date>: $X.XX`
- [ ] Task: Conductor - User Manual Verification 'Phase 2: New BookingCard Component' (Protocol in workflow.md)

---

## Phase 3: Replace PriceTracker

Replace `src/components/PriceTracker.tsx` with a simplified version that uses `BookingCard`.

- [ ] Task: Rewrite `PriceTracker.tsx` to render a list of `BookingCard` components
  - Remove all excluded-category state management
  - Remove category toggle handlers
  - Keep loading/error states
  - Keep `lastUpdated` display in page header
- [ ] Task: Delete `src/components/DataGrid.tsx`
- [ ] Task: Delete `src/components/CategoryFilter.tsx`
- [ ] Task: Delete `src/components/Chart.tsx`
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Replace PriceTracker' (Protocol in workflow.md)

---

## Phase 4: Dark Theme

Apply dark background and color scheme to the overall app.

- [ ] Task: Update `App.tsx` root div to use dark background (`bg-gray-950 text-gray-100`)
- [ ] Task: Update `tailwind.config.js` to set `darkMode: 'class'` if not already set
- [ ] Task: Ensure `BookingCard` uses dark-compatible colors throughout
  - Card background: `bg-gray-900`
  - Muted text: `text-gray-400`
  - Price up: `text-red-400`
  - Price down: `text-green-400`
- [ ] Task: Verify `AdminInterface` and other preserved components don't break with dark background
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Dark Theme' (Protocol in workflow.md)

---

## Phase 5: Final Polish

- [ ] Task: Run `npm run typecheck` and fix all type errors
- [ ] Task: Run `npm run lint` and fix all lint warnings
- [ ] Task: Smoke test in dev server — verify all bookings render, toggle works, no console errors
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final Polish' (Protocol in workflow.md)
