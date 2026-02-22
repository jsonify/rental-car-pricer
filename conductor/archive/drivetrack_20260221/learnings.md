# Track Learnings: drivetrack_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components
- Use `holding_price != null` guard (not `!holdingPrice`) when holding price could theoretically be `0`
- Price **drops** → `text-green-400` + `↓`; Price **rises** → `text-red-400` + `↑`
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- `bg-emerald-950/30` is a valid Tailwind opacity modifier for subtle highlight backgrounds
- `EnvironmentContext` defaults to test mode when `VITE_SUPABASE_URL` is absent
- react-router-dom v6 with HashRouter (GitHub Pages compatible) is already installed
- Per-booking SVG gradient IDs should be unique: `priceGradient-${booking.id}`

---

<!-- Learnings from implementation will be appended below -->

## [2026-02-21] - Phase 1 Task 1: Navbar
- **Implemented:** Navbar.tsx with DriveTrack wordmark, route-aware tabs via useLocation, EnvironmentSwitcher on right
- **Files changed:** src/components/Navbar.tsx (created)
- **Commit:** 592bdf6
- **Learnings:**
  - Patterns: Place `<Navbar />` outside `<Routes>` but inside `<EnvironmentProvider>` — it needs environment context but should render on all routes
  - Gotchas: Bookings tab is non-linked in v1 (dimmed span, no href) — keeps it clean without needing useBookings in Navbar

---

## [2026-02-21] - Phase 2 Task 1: StatCards
- **Implemented:** StatCards.tsx replacing PortfolioSummary with 3-card grid
- **Files changed:** src/components/StatCards.tsx (created)
- **Commit:** 592bdf6
- **Learnings:**
  - Patterns: `reduce<Type | null>` with null initial value for finding max/min booking across array
  - Context: Best Deal and Biggest Surge cards are clickable → useNavigate to detail page

---

## [2026-02-21] - Phase 2 Task 2: PriceTrendWave
- **Implemented:** PriceTrendWave.tsx with 30-day rolling avg across all bookings
- **Files changed:** src/components/PriceTrendWave.tsx (created)
- **Commit:** 592bdf6
- **Learnings:**
  - Patterns: Build date range with `subDays(today, i)` loop, then for each date find most recent price_history record with `created_at <= endOfDate`
  - Gotchas: Filter cutoff uses `isAfter(parsed, cutoff)` — records older than 30 days are excluded even if they're the most recent available
  - Context: Direction uses 7-point window average comparison (first window vs last window), not raw first/last values

---

## [2026-02-21] - Phase 2 Task 3: PriceWatchTable
- **Implemented:** PriceWatchTable.tsx compact table with status badges and row navigation
- **Files changed:** src/components/PriceWatchTable.tsx (created)
- **Commit:** 592bdf6
- **Learnings:**
  - Patterns: `getStatus()` helper function returns typed StatusKey enum-like union; `STATUS_ORDER` lookup for sort order
  - Patterns: `holding_price == null` (not `!= 0`) correctly handles the no-hold case

---

## [2026-02-21] - Phase 3 Task 1+2: Integration
- **Implemented:** Wired Navbar into App, updated PriceTracker layout, deleted PortfolioSummary
- **Files changed:** src/App.tsx, src/components/PriceTracker.tsx, src/components/PortfolioSummary.tsx (deleted)
- **Commit:** d211cfd
- **Learnings:**
  - Patterns: Navbar placed between `<EnvironmentProvider>` and `<Routes>` — renders on all routes, has access to environment context and route hooks
  - Gotchas: Removing PortfolioSummary requires checking all imports — it was only used in PriceTracker.tsx

---
