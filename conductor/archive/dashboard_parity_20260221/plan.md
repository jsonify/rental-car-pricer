# Plan: dashboard_parity_20260221

## Phase 1: Data Layer
<!-- depends: -->

- [x] Task 1: Extend `BookingWithHistory` in `src/lib/types.ts` — add
  `allTimeHigh: number` and `latestPrices: Record<string, number>`
- [x] Task 2: Compute both fields in `useBookings.ts` — `allTimeHigh` = max
  focus-category price across all history records; `latestPrices` = latest
  history entry's full `prices` dict (or `{}` if no history)
- [x] Task 3: Conductor - User Manual Verification 'Data Layer'

## Phase 2: Palette & Shell
<!-- depends: -->

- [x] Task 1: Update page background to `bg-slate-950` in `src/App.tsx`
- [x] Task 2: In `BookingCard.tsx` replace card container colors —
  `bg-gray-900 → bg-slate-900`, `border-gray-800 → border-slate-700`; sweep
  all `gray-*` text tokens → `slate-*` equivalents
- [x] Task 3: Conductor - User Manual Verification 'Palette & Shell'

## Phase 3: Card Header + Status Badge
<!-- depends: phase1, phase2 -->

- [x] Task 1: Add inline `StatusBadge` component in `BookingCard.tsx` —
  three states: Under Hold (emerald-400 pill), Above Hold (amber-400 pill),
  No Hold (slate-500 muted pill)
- [x] Task 2: Rework card header — location + category left, status badge
  right; move dates + days-away to subtitle row below location name
- [x] Task 3: Conductor - User Manual Verification 'Card Header + Status Badge'

## Phase 4: Price Hero
<!-- depends: phase3 -->

- [x] Task 1: Refactor price hero to two-column flex layout: left = category
  label (uppercase muted) + current price (4xl monospace) + change vs previous
  (↓ emerald / ↑ red / → slate); right = "Your Hold" label + holding price +
  above/below delta in amber/emerald. Right column hidden if no `holding_price`.
- [x] Task 2: Conductor - User Manual Verification 'Price Hero'

## Phase 5: Range Bar
<!-- depends: phase4 -->

- [x] Task 1: Add inline `RangeBar` component — full-width gradient bar
  (emerald-400 → amber-400 → red-400 via inline style), fill width =
  `clamp(2, (latestPrice - lowestPriceSeen) / (rightAnchor - lowestPriceSeen) * 100, 98)%`.
  Right anchor = `holding_price` if set, else `allTimeHigh`. Labels below
  (left: "All-time low $X", right: "Your hold $X" or "All-time high $X").
- [x] Task 2: Render `RangeBar` below price hero
- [x] Task 3: Conductor - User Manual Verification 'Range Bar'

## Phase 6: Better Deals + All Categories
<!-- depends: phase5 -->

- [x] Task 1: Compute `betterDeals` from `latestPrices` (categories where
  price < `latestPrice`, sorted by savings desc). Add collapsible section:
  "⚡ N Better Deals Available" header, each row shows category + price +
  emerald savings pill `-$X (Y%)`. Hidden entirely when no better deals exist.
- [x] Task 2: Add collapsible all-categories table — `latestPrices` sorted
  ascending; focus row gets `border-l-2 border-emerald-400 bg-emerald-950/30`;
  independent `showAllCats` toggle state.
- [x] Task 3: Conductor - User Manual Verification 'Better Deals + All Categories'

## Phase 7: Validation
<!-- depends: phase6 -->

- [x] Task 1: `npm run typecheck` — resolve all errors
- [x] Task 2: `npm run lint` — resolve all warnings
- [x] Task 3: Conductor - User Manual Verification 'Validation'
