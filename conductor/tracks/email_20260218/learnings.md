# Track Learnings: email_20260218

Patterns, gotchas, and context discovered during implementation.

## Codebase Patterns (Inherited)

- Price **drops** → green + ↓ (good news — rebook opportunity); price **rises** → red + ↑ (bad news — hold) (from: dashboard_20260217)
- `bookings_data` list items carry: `booking` dict, `prices` dict, `trends` dict (with `focus_category.lowest`, `focus_category.previous_price`), `has_significant_drop` bool (from: email_module code review)
- All-time low is in `focus_trends['lowest']`; previous price is in `focus_trends['previous_price']` — both already passed into templates
- `holding_price` may be `None` — always guard with `is not None` before comparing
- Email files: `sender.py` (orchestration, subject), `html_template.py` (HTML card), `formatters.py` (plain text)
- Date formats: `pickup_date`/`dropoff_date` use `MM/DD/YYYY` (from: dashboard_20260217)

---

<!-- Learnings from implementation will be appended below -->
