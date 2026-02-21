# Track Learnings: dashboard_parity_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components
- `isDevelopment` flag exported from `src/lib/environment.ts` — use it to gate dev-only UI
- Dark mode via `class="dark"` on `<html>` — shadcn/ui components pick up dark CSS vars automatically
- **Date formats are mixed**: `pickup_date`/`dropoff_date` use `MM/DD/YYYY`; `created_at` uses ISO
- Price **drops** → `text-green-400` + `↓`; Price **rises** → `text-red-400` + `↑`
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- `emerald-950/30` is a valid Tailwind opacity modifier for subtle highlight backgrounds

## Email → Tailwind Color Map

| Role            | Email hex | Tailwind token |
|-----------------|-----------|----------------|
| Page background | `#141521` | `slate-950`    |
| Card background | `#1c1d2e` | `slate-900`    |
| Card border     | `#2a2b3d` | `slate-700`    |
| Primary text    | `#e8e8ed` | `slate-100`    |
| Secondary text  | `#8b8ca0` | `slate-400`    |
| Muted text      | `#6b6c80` | `slate-500`    |
| Green accent    | `#34d399` | `emerald-400`  |
| Amber accent    | `#fbbf24` | `amber-400`    |
| Red accent      | `#f87171` | `red-400`      |

---

<!-- Learnings from implementation will be appended below -->

## [2026-02-21] - Phase 3: Card Header + Status Badge
- **Commit:** 8d32bf1
- **Learnings:**
  - StatusBadge uses `holding_price != null` guard (not `!holdingPrice`) to avoid falsy-zero edge cases
  - Subtitle row (`category · dates · days`) keeps header clean without a second column

## [2026-02-21] - Phase 4: Price Hero
- **Commit:** 831a7a6
- **Learnings:**
  - `DeltaBadge` became fully unused after price hero refactor — remove it to avoid lint errors
  - Holding delta direction: positive = above hold = amber (bad); negative = below hold = emerald (good)

## [2026-02-21] - Phase 5: Range Bar
- **Commit:** 93f7cc2
- **Learnings:**
  - RangeBar uses `clamp(2, fill%, 98)` so indicator is always visible even at extremes
  - Inline `background: linear-gradient(to right, #34d399, #fbbf24, #f87171)` — no Tailwind class needed
  - `holding_price ?? allTimeHigh` cleanly picks the right anchor

## [2026-02-21] - Phase 6: Better Deals + All Categories
- **Commit:** 5eed4fc
- **Learnings:**
  - `bg-emerald-950/30` is valid Tailwind opacity modifier for the focus row highlight
  - Filter: `cat !== focus_category && price < latestPrice` — exclude focus cat from better deals

## [2026-02-21] - Phase 7: Validation (pre-existing error fixes)
- **Commit:** c23ae7f
- **Learnings:**
  - Two files (`usePriceChecker.ts`, `mocks/handlers.ts`) had multiple complete modules concatenated — likely copy-paste scaffolding artifacts
  - `HoldingPricesDialog.tsx` had no TypeScript types at all — adding `Booking` prop type fixed 12 errors at once
  - Unused variable errors: prefix with `_` (e.g. `_columns`) or remove assignment entirely

## [2026-02-21] - Phase 1 Tasks 1+2: Data Layer
- **Implemented:** Added `allTimeHigh` and `latestPrices` to `BookingWithHistory`; computed in `useBookings.ts`
- **Files changed:** `src/lib/types.ts`, `src/hooks/useBookings.ts`
- **Commit:** 5adc0bb
- **Learnings:**
  - Patterns: `focusPrices` array already existed for `lowestPriceSeen` — adding `allTimeHigh` was just adding `Math.max(...focusPrices)` alongside it
  - `latestPrices` uses nullish coalescing `latestHistory?.prices ?? {}` — safe when no history exists
  - Pre-existing typecheck errors exist in unrelated files (AdminInterface, HoldingPricesDialog, mocks) — not introduced by this change
---

## [2026-02-21] - Phase 2 Tasks 1+2: Palette & Shell
- **Implemented:** `bg-gray-950 → bg-slate-950` in App.tsx; full `gray-*` → `slate-*` sweep in BookingCard.tsx
- **Files changed:** `src/App.tsx`, `src/components/BookingCard.tsx`
- **Commit:** 5adc0bb
- **Learnings:**
  - `DeltaBadge` inner `<span>` also used `text-gray-500` — easy to miss when doing a sweep
  - Recharts Tooltip `contentStyle`/`labelStyle`/`itemStyle` use hardcoded hex (`#111827` etc) — leaving those as-is is fine, they're already dark-themed
---
