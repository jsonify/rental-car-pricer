# Track Learnings: dashboard_parity_20260221

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- `useBookings.ts` is the single place to compute all derived price values — add new fields there, not in components
- `isDevelopment` flag exported from `src/lib/environment.ts` — use it to gate dev-only UI
- Dark mode via `class="dark"` on `<html>` — shadcn/ui components pick up dark CSS vars automatically
- **Date formats are mixed**: `pickup_date`/`dropoff_date` use `MM/DD/YYYY`; `created_at` uses ISO
- Price **drops** → `text-green-400` + `↓`; Price **rises** → `text-red-400` + `↑`
- Recharts `Tooltip` needs explicit dark styling: `contentStyle={{ background: '#111827', border: '1px solid #1f2937' }}`
- `emerald-950/30` is a valid Tailwind opacity modifier for subtle highlight backgrounds

## Email → Tailwind Color Map

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

---

<!-- Learnings from implementation will be appended below -->
