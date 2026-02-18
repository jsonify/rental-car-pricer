# Track Learnings: dashboard_20260217

Patterns, gotchas, and context discovered during implementation.

---

## [2026-02-17] - Phase 1: Data Layer Enhancements

- **Implemented:** Added `firstTrackedPrice`, `changeFromBaseline`, `lowestPriceSeen`, `daysUntilPickup` to `BookingWithHistory` and `useBookings.ts`
- **Files changed:** `src/lib/types.ts`, `src/hooks/useBookings.ts`
- **Commit:** `a44286d`
- **Learnings:**
  - Gotcha: `node_modules` was not installed — run `npm install` first in any fresh clone
  - Gotcha: `npm run typecheck` fails with "tsc: command not found" unless using `./node_modules/.bin/tsc --noEmit` directly, or installing deps first
  - Pattern: `useBookings.ts` computes all derived price values — add new derived fields here, not in components

---

## [2026-02-17] - Phase 2: New BookingCard Component

- **Implemented:** Created `BookingCard.tsx` with dark minimal design, Zone 1 (always visible) and Zone 2 (collapsible history)
- **Files changed:** `src/components/BookingCard.tsx`
- **Commit:** `b32601b`
- **Learnings:**
  - Pattern: Price delta coloring — green (`text-green-400`) when price DROPS (good news), red (`text-red-400`) when price RISES (bad news). Down is good.
  - Pattern: Recharts `ResponsiveContainer` + `LineChart` works cleanly in a dark card with `contentStyle={{ background: '#111827' }}` on Tooltip
  - Gotcha: `supabaseUrl is required` crash on first load — `EnvironmentContext` defaults to production mode; fixed by defaulting to test mode when env vars absent

---

## [2026-02-17] - Phase 3: Replace PriceTracker

- **Implemented:** Rewrote `PriceTracker.tsx` to render `BookingCard` list; deleted `DataGrid.tsx`, `CategoryFilter.tsx`, `Chart.tsx`
- **Files changed:** `src/components/PriceTracker.tsx` (rewritten), 3 files deleted
- **Commit:** `edbb5d1`
- **Learnings:**
  - Pattern: `isDevelopment` flag is exported from `src/lib/environment.ts` — use it to gate dev-only UI
  - `formatDistanceToNow` from `date-fns` is the right call for "Updated X minutes ago" display

---

## [2026-02-17] - Phase 4: Dark Theme

- **Implemented:** `<html class="dark">` in `index.html` activates shadcn CSS variable dark mode; `App.tsx` updated to `bg-gray-950`
- **Files changed:** `index.html`, `src/App.tsx`, `src/components/EnvironmentSwitcher.tsx`
- **Commit:** `cb54533`, `d57b0b9`
- **Learnings:**
  - Pattern: Dark mode is toggled via `class="dark"` on `<html>` — all shadcn components pick up dark CSS vars automatically
  - Gotcha: `tsconfig.json` was missing `"types": ["vite/client"]` — caused `import.meta.env` errors everywhere. Always include this for Vite projects.
  - Gotcha: The mock date format is `MM/DD/YYYY` (e.g. `04/01/2025`), NOT ISO. `parseISO()` crashes on it. Use `new Date()` for all date fields that originate from bookings. `created_at` fields are always `.toISOString()` so `parseISO()` is fine there.
  - Pattern: Admin/utility UI should be collapsed by default — bookings are the primary content

---

## [2026-02-17] - Phase 5: Final Polish

- **Implemented:** Added `.eslintrc.cjs`, fixed `useCallback` in `useBookings`, suppressed pre-existing issues via `.eslintignore`
- **Files changed:** `.eslintrc.cjs`, `.eslintignore`, `src/hooks/useBookings.ts`, `src/contexts/EnvironmentContext.tsx`
- **Commit:** `a9cf17d`
- **Learnings:**
  - Gotcha: `.eslintrc.cjs` was missing entirely from the repo — ESLint config must be committed
  - Pattern: When adding ESLint to an existing codebase, use `.eslintignore` to scope lint to new/owned files first, then tackle legacy debt as a separate track
  - Pattern: `fetchBookings` in `useBookings.ts` must be wrapped in `useCallback` with `[isTestEnvironment]` deps to satisfy `react-hooks/exhaustive-deps`
