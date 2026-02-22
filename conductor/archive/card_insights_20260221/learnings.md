# Track Learnings: card_insights_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components
- `holding_price != null` guard (not `!holdingPrice`) when holding price could be `0`
- Price drops → `text-emerald-400` + `▼`; Price rises → `text-red-400` + `▲`
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- For per-bar coloring in Recharts BarChart: use `<Cell>` inside `<Bar>` with a fill computed per datum
- Status badge pattern: helper returns typed union, STATUS_ORDER for sort, sub-component for rendering
- Place `<Navbar />` between `<EnvironmentProvider>` and `<Routes>` — renders on all routes

---

<!-- Learnings from implementation will be appended below -->
