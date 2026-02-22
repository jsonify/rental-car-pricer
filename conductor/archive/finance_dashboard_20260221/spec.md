# Spec: Finance-Style Portfolio Dashboard

## Overview

Rebuild the React dashboard into a finance/trading-style portfolio view. Each
rental car booking is treated as a "tracked asset" — inspired by DeFi market
dashboards and finance apps (dark background, teal/emerald accents, prominent
area charts with reference lines). The goal is maximum analytical value at a
glance, not just a price number.

## Functional Requirements

### 1. Portfolio Summary Strip

A compact horizontal strip of stat cards rendered above all booking cards.

**Stats to display:**
- **Savings Available** — sum of `max(0, holdingPrice - latestPrice)` across
  all bookings. Shows $0 if no savings currently available. Accent: emerald.
- **Price Trend** — count of bookings where latest price < previous price, vs
  total. e.g. "2 / 2 trending ↓" or "1 / 2 trending ↓". Emerald if all down,
  amber if mixed, red if all up.

Each stat: small card with label, large value, and direction icon.

### 2. Booking Cards (Rebuilt)

#### 2a. Card Header
- Location code (monospace, large) + location full name (muted)
- Date range (pickup → dropoff) + "N days away" chip
- Status badge: "Under Hold" (emerald) / "Above Hold" (amber) / "No Hold" (slate)

#### 2b. Price Hero Row (two-column)
**Left column:**
- Current price: 4xl+ monospace, white
- vs last check: ↓$18 (-5.2%) emerald, or ↑$22 (+6.1%) red, with arrow

**Right column (if holding price set):**
- Label: "Your Hold"
- Holding price in amber
- Savings or overage delta below it
- Small ✎ edit icon — clicking reveals inline edit input + confirm/cancel buttons

#### 2c. Price History Area Chart (primary new feature)
- Full-width, ~200px tall, Recharts `AreaChart`, always visible (not collapsible)
- Line: `#34d399` (emerald-400), 2px stroke
- Fill: gradient from `rgba(52,211,153,0.25)` → `rgba(52,211,153,0)` bottom
- X axis: abbreviated dates (Feb 1, Feb 7…), gridlines in slate-800
- Y axis: dollar labels, minimal, width=55
- Hover tooltip: dark card (`bg-slate-800 border-slate-700`) showing date + price
- **Reference Lines** (Recharts `ReferenceLine`):
  - Hold price → amber dashed, labeled "Hold $N", insideTopRight
  - All-time low → emerald dashed, labeled "Low $N", insideBottomRight
  - Only shown when the relevant value exists

#### 2d. Stats Footer (below chart)
3-column grid: **All-time Low** | **Your Hold** (or "—" if unset) | **All-time High**
Each: label in slate-500 text-xs, value in font-mono text-slate-200 text-sm.
Separated by vertical dividers; top border separates from chart.

#### 2e. Top-border Accent
- "Under Hold" card → `border-t-2 border-t-emerald-500/40`
- "Above Hold" card → `border-t-2 border-t-amber-500/40`
- "No Hold" card → no top accent

#### 2f. Collapsible Sections (retained, restyled)
- "Better Deals Available" (hidden when no cheaper alternatives exist)
- "All Categories" table (ascending price, focus row highlighted)

### 3. Inline Hold Price Editing

The hold price on each card is directly editable without leaving the page:
- Default view: hold price + small `✎` icon button
- Edit view: number input (pre-filled) + `✓` confirm (emerald) + `✕` cancel (slate)
- On confirm: update Supabase directly (test mode) or trigger GitHub Actions
  workflow `update-holding-prices` (production mode), then refetch bookings
- Edit icon hidden if no `onUpdateHold` handler is provided

### 4. Admin Panel (Restyled, Reduced)

The admin panel retains three actions (hold price updates now handled inline):
- **Check Prices Now** (production mode only) — emerald button, triggers scraper workflow
- **Add New Booking** — dark slate button, opens existing dialog (restyled)
- **Delete Booking** — dark red button, opens existing dialog (restyled)

Panel visual updates:
- Remove light Card wrapper → use `bg-slate-900 border border-slate-800 rounded-xl`
- All dialog interiors use dark `bg-slate-900 / border-slate-700` styles
- Admin toggle button in `App.tsx` → small Settings icon, `fixed top-4 right-4`

### 5. Visual Palette (consistent with previous track)

| Token | Color |
|---|---|
| Page background | slate-950 |
| Card background | slate-900 |
| Card border | slate-700 / slate-800 |
| Price drop / savings | emerald-400 (#34d399) |
| Price rise | red-400 (#f87171) |
| Hold reference | amber-400 (#fbbf24) |
| Text primary | slate-100 |
| Text muted | slate-400 / slate-500 |

## Non-Functional Requirements

- Use Recharts `AreaChart`, `Area`, `ReferenceLine`, `Tooltip` — already in stack
- TypeScript: 0 errors; ESLint: 0 warnings after implementation
- Renders correctly in both test (mock localStorage) and production (Supabase) modes
- No changes to Supabase schema or Python scraper

## Acceptance Criteria

- [ ] Portfolio summary strip shows correct total savings and trend count
- [ ] Each booking card shows a full-width area chart with teal line + gradient fill
- [ ] Reference lines appear at correct Y positions for hold price and all-time low
- [ ] Chart hover tooltip shows date and dollar price
- [ ] Clicking the ✎ icon on a card's hold price reveals an inline edit field
- [ ] Saving the inline edit updates the hold price (test: direct DB; prod: workflow trigger)
- [ ] Admin panel no longer shows "Update Holding Prices" button
- [ ] Admin panel and dialogs styled to match dark theme
- [ ] `npm run build` passes with 0 TypeScript errors and 0 lint warnings
- [ ] Test environment (mock data) renders correctly with all chart features

## Out of Scope

- Time range toggle (1H/4H/1D) — no intraday data available
- Sidebar navigation — single-page layout retained
- New Supabase tables or schema changes
- Python scraper changes
