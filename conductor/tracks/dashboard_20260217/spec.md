# Spec: Dashboard Redesign

**Track ID:** `dashboard_20260217`
**Status:** new

---

## Problem Statement

The current dashboard is visually cluttered and doesn't communicate what matters:
- Charts show 10+ overlapping car category lines — confusing for a single-user tool
- The focus category price (the one the user actually cares about) is not prominent
- "Price change" shows delta vs previous check, not vs baseline (when tracking started)
- The category filter UI adds complexity without value in a solo-use tool
- The layout doesn't immediately answer: *"Should I rebook right now?"*

---

## Goals

1. Answer "should I rebook right now?" within 5 seconds of opening the dashboard
2. Make price signals (up/down) immediately scannable via color and delta amounts
3. Remove all UI that doesn't serve the core question
4. Dark, minimal aesthetic — no decorative elements

---

## Out of Scope

- AdminInterface component (booking management) — unchanged
- EnvironmentSwitcher — unchanged
- Backend / data fetching logic in `useBookings.ts` (data additions are in scope, UI replacement is the focus)
- Mobile-specific layout optimization (responsive basics are fine)

---

## New Data Requirements

`useBookings.ts` must compute and expose additional derived values per booking:

| Field | Definition |
|-------|-----------|
| `firstTrackedPrice` | Price at the earliest `price_history` record for `focus_category` |
| `changeFromBaseline` | `latestPrice - firstTrackedPrice` (positive = more expensive, negative = cheaper) |
| `lowestPriceSeen` | Minimum `focus_category` price across all `price_history` records |
| `daysUntilPickup` | Calendar days from today to `pickup_date` |

---

## New Dashboard Layout

### Overall Page

- Dark background (`bg-gray-950` or similar)
- Single column of booking cards, max-width constrained, centered
- Page header: app name + "Last updated: X minutes ago"
- No category filter controls on the main view

### Booking Card

Each booking gets one card with two zones:

#### Zone 1 — Primary (always visible)

```
┌─────────────────────────────────────────────────────┐
│  Las Vegas McCarran           Jun 12–19  · 18 days  │
│  Economy Car                                         │
│                                                      │
│  $289.00          ↓ $34  vs what you booked         │
│  (current)        ↑ $12  since tracking began        │
│                                                      │
│  All-time low: $267.00    Holding: $323.00           │
└─────────────────────────────────────────────────────┘
```

- **Location name** — prominent, top-left
- **Dates + days until pickup** — top-right, muted
- **Focus category** — below location, small label
- **Current price** — very large, dominant
- **vs holding price delta** — immediately below current price
  - Green + ↓ if current < holding (you can save money by rebooking)
  - Red + ↑ if current > holding (prices have gone up, hold your booking)
  - Neutral if no holding price set
- **vs baseline delta** — secondary line
  - "since tracking began" label
- **All-time low** + **Holding price** — bottom row, muted

#### Zone 2 — Detail Panel (expandable, collapsed by default)

A "Show history" toggle reveals:
- Simple sparkline (single line) for `focus_category` price over time
- Last 5 price check timestamps with prices (a simple list, not a table)

---

## Removed Components

The following components are replaced entirely and can be deleted:

| Component | Replacement |
|-----------|------------|
| `DataGrid.tsx` | Inline bottom-row stats in booking card |
| `Chart.tsx` | Simple single-line sparkline in collapsed detail panel |
| `CategoryFilter.tsx` | Removed entirely — not needed |

---

## Preserved Components

| Component | Notes |
|-----------|-------|
| `AdminInterface.tsx` | Unchanged |
| `EnvironmentSwitcher.tsx` | Unchanged |
| `TestControls.tsx` | Unchanged (dev-only) |
| `WorkflowStatusBanner.tsx` | Unchanged |
| `HoldingPriceHistory.tsx` | Unchanged |
| `HoldingPricesDialog.tsx` | Unchanged |
| `useBookings.ts` | Extended (new derived fields) |
| `src/lib/types.ts` | Extended (`BookingWithHistory`) |

---

## Acceptance Criteria

- [ ] Opening the dashboard shows the current focus-category price prominently for each booking
- [ ] Price delta vs holding price is colored green (save money) or red (prices up)
- [ ] "Since tracking began" delta is visible without expanding any panels
- [ ] All-time lowest price seen is visible on each card
- [ ] Days until pickup is visible on each card
- [ ] No category filter UI exists on the main view
- [ ] Historical chart is hidden by default behind a toggle
- [ ] Dark background theme applied
- [ ] No TypeScript errors, no lint errors
