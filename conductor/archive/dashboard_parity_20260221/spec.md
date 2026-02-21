# Spec: Dashboard Email Parity

## Overview

Redesign `BookingCard` to visually match the email's blue-tinted dark aesthetic
and information hierarchy. All six email design elements are ported to the
interactive dashboard while preserving the existing sparkline history panel.

## Functional Requirements

### 1. Color Palette (Tailwind built-ins)

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

### 2. Status Badge

Right side of card header. Three states:
- **Under Hold** — emerald-400 pill — when `latestPrice ≤ holding_price`
- **Above Hold** — amber-400 pill — when `latestPrice > holding_price`
- **No Hold** — slate-500 muted pill — when `holding_price` is absent

### 3. Price Hero (two-column)

- **Left column:** focus_category label (uppercase, muted) → current price
  (large monospace) → change vs previous check (↓ emerald / ↑ red / → no change)
- **Right column:** "Your Hold" label → holding price (slightly smaller) →
  delta above/below in amber/emerald. Hidden if no `holding_price`.

### 4. Gradient Range Bar

Full-width bar below the price hero. Gradient fill: emerald-400 → amber-400 →
red-400 left-to-right. Fill width = position of current price between
all-time low (left) and `holding_price` or `allTimeHigh` (right). Labels below.

### 5. Better Deals Section (collapsible, default collapsed)

Only rendered when cheaper categories exist. Header: "⚡ N Better Deals
Available". Each row: category name + price + emerald savings pill
(`-$X.XX (Y%)`). Independent toggle.

### 6. All Categories Table (collapsible, default collapsed)

All categories from latest check sorted by price ascending. Focus row:
emerald left border + subtle highlight. Independent toggle from history
and better deals.

### 7. Preserve Existing

Collapsible sparkline + recent checks panel (Zone 2) unchanged.

## Data Layer Changes

Two new derived fields added to `useBookings.ts` and `BookingWithHistory`:
- `latestPrices: Record<string, number>` — all categories from the most recent
  price check (used by better deals + all categories sections)
- `allTimeHigh: number` — highest focus-category price ever seen (right anchor
  of range bar when no holding_price)

## Non-Functional Requirements

- Zero new npm dependencies
- `npm run typecheck` passes with 0 errors
- `npm run lint` passes with 0 errors
- All existing functionality preserved

## Acceptance Criteria

- [ ] Page and card backgrounds have visible blue-slate tint (not neutral gray)
- [ ] Status badge correct for all three states (under / above / no hold)
- [ ] Price hero is two-column when `holding_price` exists; single-column otherwise
- [ ] Range bar renders with gradient and correctly positioned fill
- [ ] Better deals section hidden when no cheaper categories exist
- [ ] All categories table and better deals toggle independently from history
- [ ] Sparkline history still works
- [ ] 0 TypeScript errors, 0 lint errors

## Out of Scope

- Changes to `PriceTracker.tsx` layout, `AdminInterface`, `TestControls`
- Mobile breakpoint changes
- New network requests or data sources
