# Track Learnings: finance_dashboard_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components
- Dark mode toggled via `class="dark"` on `<html>` — all shadcn/ui components pick up dark CSS vars automatically
- Use `holding_price != null` guard (not `!holdingPrice`) when holding price could theoretically be `0`
- Gradient fills use inline `style={{ background: 'linear-gradient(to right, ...)' }}` — no Tailwind utility needed for multi-stop gradients
- `bg-emerald-950/30` is a valid Tailwind opacity modifier for subtle highlight backgrounds
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}`
- `useMemo` for Supabase client creation — prevents multiple GoTrueClient instances

## Color Palette Reference

| Role | Tailwind | Hex |
|------|----------|-----|
| Price drop / emerald line | emerald-400 | #34d399 |
| Hold reference | amber-400 | #fbbf24 |
| Price rise | red-400 | #f87171 |
| Card bg | slate-900 | #0f172a |
| Page bg | slate-950 | #020617 |
| Border | slate-800 | #1e293b |
| Text muted | slate-400/500 | #94a3b8 / #64748b |

## Similar Archived Tracks

- `dashboard_parity_20260221` — previous slate redesign with BookingCard overhaul (reference for card structure, StatusBadge, price hero layout)

---

<!-- Learnings from implementation will be appended below -->
