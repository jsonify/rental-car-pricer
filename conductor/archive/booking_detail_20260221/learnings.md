# Track Learnings: booking_detail_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute derived price values — find booking by ID here, don't add new fetch logic
- Date formats are mixed: booking `pickup_date`/`dropoff_date` use `MM/DD/YYYY`; `created_at` fields use ISO — use `parseISO()` for price_history timestamps
- Dark theme: `bg-slate-950` page, `bg-slate-900` cards, `border-slate-800`, emerald/amber/red accents
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}`
- Per-booking gradient IDs must be unique — use a static id like `priceGradient-detail` for the detail page (only one chart on the page)
- `holding_price != null` guard (not `!holdingPrice`) to avoid falsy-zero edge cases
- `isDevelopment` flag from `src/lib/environment.ts` for dev-only UI gating
- HashRouter required for GitHub Pages (no server-side routing support)

---

<!-- Learnings from implementation will be appended below -->
