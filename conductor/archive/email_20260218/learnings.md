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

## [2026-02-19] - Phase 1 Task 2 (resumed): Wire format_subject into send_price_alert

- **Implemented:** Wired `format_subject(active_bookings)` into `send_price_alert()` replacing the hardcoded generic subject
- **Files changed:** `email_module/sender.py`, `test_email_sender.py`
- **Commit:** e561048
- **Learnings:**
  - Gotcha: `test_email_sender.py` was stubbing `email_module.templates.html_template` as an empty `types.ModuleType`. When pytest ran sender tests first, subsequent tests importing the real module got the empty stub → `ImportError: cannot import name 'format_booking_card' (unknown location)`. Fix: only stub the modules that actually import supabase (i.e., `supabase` and `supabase_client`). Template submodules (`html_template.py`, `formatters.py`, `css_styles.py`) have no supabase dependency and load fine without stubs.
  - Pattern: `sys.modules.setdefault()` prevents overwriting real modules but does NOT prevent replacing real modules with stubs when the stub is registered first.
---
