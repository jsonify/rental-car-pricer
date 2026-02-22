# Plan: Finance-Style Portfolio Dashboard

## Phase 1: PortfolioSummary Component
<!-- depends: -->

- [x] Task 1: Create `PortfolioSummary` component
  <!-- files: src/components/PortfolioSummary.tsx -->
  New component. Props: `bookings: BookingWithHistory[]`.
  Renders two stat cards in a horizontal strip:
  - **Savings Available**: `sum of max(0, holding_price - latestPrice)`. Emerald if >0, slate-500 if 0.
  - **Price Trend**: count where `priceChange < 0` vs total. e.g. "2 / 2 ↓". Emerald if all down, amber if mixed, red if all up.
  Style: `flex gap-4 mb-6`. Each card: `bg-slate-900 border border-slate-800 rounded-xl px-5 py-4`.
  Label: `text-slate-400 text-xs uppercase tracking-widest`. Value: `text-2xl font-mono text-slate-100 mt-1`.

- [~] Task 2: Conductor - User Manual Verification 'Portfolio Summary Strip'

## Phase 2: BookingCard — Area Chart + Inline Hold Edit
<!-- depends: -->

- [x] Task 1: Replace LineChart with AreaChart + gradient fill + reference lines
  <!-- files: src/components/BookingCard.tsx -->
  Import `AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine` from recharts.
  Build chart data from `booking.price_history` filtering out zero prices; format dates as "MMM d".
  Render a 200px tall AreaChart (always visible, not behind a toggle):
  - Define SVG `<defs><linearGradient>` id="priceGradient" — stop 0%: rgba(52,211,153,0.25), stop 100%: rgba(52,211,153,0)
  - `<Area>` type="monotone" dataKey="price" stroke="#34d399" strokeWidth={2} fill="url(#priceGradient)" dot={false}
  - `<XAxis>` dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false}
  - `<YAxis>` domain={['auto','auto']} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} width={55}
  - `<Tooltip>` contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} formatter={(v: number) => [`$${v.toFixed(2)}`, 'Price']}
  - `<ReferenceLine>` for holdingPrice (if >0): y={holdingPrice} stroke="#fbbf24" strokeDasharray="4 3" label={{ value: `Hold $${holdingPrice.toFixed(0)}`, fill: '#fbbf24', fontSize: 11, position: 'insideTopRight' }}
  - `<ReferenceLine>` for lowestPriceSeen (if >0): y={lowestPriceSeen} stroke="#34d399" strokeDasharray="4 3" label={{ value: `Low $${lowestPriceSeen.toFixed(0)}`, fill: '#34d399', fontSize: 11, position: 'insideBottomRight' }}
  Remove `showHistory` state and the old LineChart entirely.

- [x] Task 2: Add inline hold price edit to the card
  <!-- files: src/components/BookingCard.tsx -->
  Add prop: `onUpdateHold?: (newPrice: number) => Promise<void>`.
  Add local state: `isEditingHold: boolean`, `holdEditValue: string`.
  In the price hero's "Your Hold" column:
  - Default: hold price + a small `✎` icon button (text-slate-500 hover:text-amber-400), only visible if `onUpdateHold` is defined.
  - Edit mode: number `<input>` pre-filled with current hold price (bg-slate-800 border-slate-700 rounded px-2 py-1 text-sm font-mono w-24) + `✓` confirm (text-emerald-400) + `✕` cancel (text-slate-500).
  - On confirm: call `onUpdateHold(parseFloat(holdEditValue))`, set `isEditingHold` false.
  - Disable confirm if value is empty or NaN.

- [~] Task 3: Conductor - User Manual Verification 'Area Chart + Inline Edit'

## Phase 3: PriceTracker Integration
<!-- depends: phase1, phase2 -->

- [ ] Task 1: Wire PortfolioSummary and updateHold handler into PriceTracker
  <!-- files: src/components/PriceTracker.tsx -->
  1. Import and render `<PortfolioSummary bookings={bookings} />` above the booking card list.
  2. Remove the old "Rentals" h1 header; move `lastUpdated` timestamp to a subtle `text-xs text-slate-600` line below the summary strip.
  3. Add `useEnvironment` to get `isTestEnvironment`; add `useMemo(() => createSupabaseClient(isTestEnvironment), [isTestEnvironment])` for the supabase client.
  4. Create `handleUpdateHoldPrice(bookingId: string, bookingIndex: number, newPrice: number): Promise<void>`:
     - Test mode: update `bookings` table `holding_price`, close current `holding_price_histories` entry (set `effective_to`), insert new history entry, call `refetch()`.
     - Production mode: call `triggerWorkflow({ action: 'update-holding-prices', booking_updates_json: JSON.stringify([bookingIndex + 1, newPrice]) })`, then `setTimeout(refetch, 5000)`.
  5. Pass `onUpdateHold={(price) => handleUpdateHoldPrice(booking.id, index, price)}` to each `<BookingCard>`.

- [ ] Task 2: Conductor - User Manual Verification 'PriceTracker Integration'

## Phase 4: Admin Panel Restyle
<!-- depends: -->

- [x] Task 1: Remove HoldingPricesDialog; restyle AdminInterface to dark theme
  <!-- files: src/components/AdminInterface.tsx -->
  1. Remove the "Update Holding Prices" button, its `updatePricesOpen` state, the `<HoldingPricesDialog>` usage, and the `handleUpdateHoldingPrices` function. Hold price is now handled inline on each card.
  2. Restyle the panel wrapper: remove `<Card>/<CardContent>` — use `<div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">`.
  3. Button styles:
     - "Check Prices Now" → `bg-emerald-700 hover:bg-emerald-600 text-white border-0`
     - "Add New Booking" → `bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200`
     - "Delete Booking" → `bg-red-950 hover:bg-red-900 border border-red-800 text-red-400`
  4. Restyle all dialog interiors: dialog content bg `bg-slate-900`, inputs `bg-slate-800 border-slate-700`, labels `text-slate-300`.

- [x] Task 2: Update App.tsx admin toggle
  <!-- files: src/App.tsx -->
  Replace the "⚙ Admin" text toggle with a `Settings` lucide icon button:
  `className="fixed top-4 right-4 z-50 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg p-2 text-slate-400 hover:text-slate-200 transition-colors"`
  The admin panel renders below the PortfolioSummary (inside max-w-2xl), not fixed. Only the toggle button is fixed.

- [~] Task 3: Conductor - User Manual Verification 'Admin Panel'

## Phase 5: Card Layout Polish
<!-- depends: phase3 -->

- [ ] Task 1: Remove RangeBar; add 3-column stats footer; add top-border accent
  <!-- files: src/components/BookingCard.tsx -->
  1. Delete the `RangeBar` component and its single usage entirely.
  2. Add a 3-column stats footer below the chart area:
     ```
     <div className="grid grid-cols-3 divide-x divide-slate-800 text-center mt-4 pt-4 border-t border-slate-800">
       <div><p className="text-slate-500 text-xs">All-time Low</p><p className="font-mono text-slate-200 text-sm mt-0.5">{fmt(lowestPriceSeen)}</p></div>
       <div><p className="text-slate-500 text-xs">Your Hold</p><p className="font-mono text-slate-200 text-sm mt-0.5">{holdingPrice ? fmt(holdingPrice) : '—'}</p></div>
       <div><p className="text-slate-500 text-xs">All-time High</p><p className="font-mono text-slate-200 text-sm mt-0.5">{fmt(allTimeHigh)}</p></div>
     </div>
     ```
  3. Add conditional top-border accent to the card wrapper:
     - Under Hold → append `border-t-2 border-t-emerald-500/40`
     - Above Hold → append `border-t-2 border-t-amber-500/40`

- [ ] Task 2: Conductor - User Manual Verification 'Card Polish'

## Phase 6: Validation
<!-- depends: phase5 -->

- [ ] Task 1: TypeScript and lint clean-up
  Run `npm run build`. Fix any type errors:
  - `onUpdateHold` prop on BookingCard
  - Recharts `ReferenceLine` label prop types (use `LabelProps` or cast as needed)
  - Removed HoldingPricesDialog — ensure no orphan imports in AdminInterface.tsx
  - Any unused state after removing old chart toggle
  Target: 0 TypeScript errors, 0 ESLint warnings. Verify test env renders correctly.

- [ ] Task 2: Conductor - User Manual Verification 'Validation'
