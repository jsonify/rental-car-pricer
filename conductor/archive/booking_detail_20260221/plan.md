# Plan: Booking Detail Page

## Phase 1: Router + Navigation Foundation

- [x] Task 1: Install react-router-dom and configure routing
  <!-- files: src/main.tsx, src/App.tsx, src/pages/BookingDetail.tsx -->
  1. Run `npm install react-router-dom`
  2. In `src/main.tsx`: wrap `<App />` in `<HashRouter>` (import from 'react-router-dom')
  3. In `src/App.tsx`: import `Routes`, `Route` from 'react-router-dom'; wrap existing
     layout in `<Route path="/" ... />` and add
     `<Route path="/booking/:id" element={<BookingDetail />} />`
  4. Create `src/pages/BookingDetail.tsx` stub (renders "Detail coming soon")
     so routing resolves before the page is fully built

- [x] Task 2: Make BookingCard navigable on click
  <!-- files: src/components/BookingCard.tsx -->
  1. Import `useNavigate` from 'react-router-dom'
  2. Add `cursor-pointer` to card outer div; `onClick={() => navigate(\`/booking/${booking.id}\`)}`
  3. Add `e.stopPropagation()` to hold edit ✎ button, ✓ confirm, ✕ cancel,
     Better Deals toggle button, and All Categories toggle button

- [x] Task 3: Conductor - User Manual Verification 'Router + Navigation Foundation' (Protocol in workflow.md)

## Phase 2: BookingDetail Page

- [x] Task 1: Create BookingDetail shell and large area chart
  <!-- files: src/pages/BookingDetail.tsx -->
  1. `useParams<{ id: string }>()` to get booking ID
  2. `const { bookings, loading } = useBookings()` — find: `bookings.find(b => b.id === id)`
  3. Handle loading state (spinner/placeholder) and not-found (redirect or error message)
  4. Header row: `← Back` button (useNavigate(-1)), location name (text-2xl font-bold),
     pickup–dropoff dates, days label, StatusBadge
  5. Large AreaChart (320px height) with same pattern as BookingCard:
     - chartData from price_history, filtering zero prices, formatted "MMM d"
     - linearGradient id="priceGradient-detail" (emerald, 0.25 → 0)
     - XAxis, YAxis, Tooltip (same dark styling)
     - ReferenceLine for holdingPrice (amber dashed) if > 0
     - ReferenceLine for lowestPriceSeen (emerald dashed) if > 0
     - Vertical ReferenceLine for today: find today's "MMM d" label in chartData;
       if present, add `<ReferenceLine x={todayLabel} stroke="#475569"
       strokeDasharray="4 3" label={{ value: 'Today', fill: '#475569', fontSize: 11 }}`

- [x] Task 2: Add price velocity strip
  <!-- files: src/pages/BookingDetail.tsx -->
  1. Filter price_history to non-zero focus_category prices, sort by created_at asc
  2. If ≥ 2 points: velocity = (lastPrice - firstPrice) / daysDiff(first.created_at, last.created_at)
     If < 2 points: velocity = null (show "—")
  3. Format velocity: `+$X.XX/day` red ↑ / `-$X.XX/day` emerald ↓ / `—` slate
  4. Urgency badge (based on velocity + daysUntilPickup from booking):
     - velocity > 0 && daysUntilPickup ≤ 14 → amber "⚠ Rising with pickup near"
     - velocity !== null && velocity < 0 → emerald "Good time to rebook"
     - else → slate "Monitoring"
  5. 2-card strip (flex gap-4): left card = velocity stat, right card = days-to-pickup + urgency badge

- [x] Task 3: Add full price history table
  <!-- files: src/pages/BookingDetail.tsx -->
  1. Sort price_history by created_at descending (most recent first)
  2. For each row compute delta: current focus_category price − next row's price
     (first row in sorted order has no previous → show "—")
  3. Render table inside `max-h-96 overflow-y-auto rounded-lg border border-slate-800`
  4. Sticky `<thead>` with `sticky top-0 bg-slate-950 text-xs text-slate-500 uppercase`
  5. Columns: Date/Time | Price | Change
     - Date: format(parseISO(created_at), 'MMM d, h:mm a')
     - Price: fmt(price) in font-mono text-slate-200
     - Change: emerald "↓ -$X.XX" / red "↑ +$X.XX" / slate "—"
  6. Row alternating: even rows bg-slate-900, odd rows bg-slate-800/30

- [x] Task 4: Conductor - User Manual Verification 'BookingDetail Page' (Protocol in workflow.md)

## Phase 3: Validation

- [x] Task 1: TypeScript and lint clean-up
  Run `npm run build`. Fix any type errors:
  - `useParams` generic typing (`useParams<{ id: string }>()`)
  - Recharts vertical ReferenceLine label prop (cast as `any` if needed)
  - Any unused imports from router setup
  - Ensure `src/pages/` directory is included in TypeScript path resolution
  Target: 0 TypeScript errors, 0 ESLint warnings.

- [x] Task 2: Conductor - User Manual Verification 'Validation' (Protocol in workflow.md)
