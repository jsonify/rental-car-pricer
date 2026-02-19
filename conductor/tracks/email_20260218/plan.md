# Plan: Email Improvements

## Phase 1: Subject Line
<!-- execution: sequential -->
<!-- depends: -->

- [ ] Task 1: Write tests for `format_subject(bookings_data)` in `test_email_sender.py`
  <!-- files: test_email_sender.py -->
  - One booking, price below holding → `✅ SEA $215 (under holding)`
  - One booking, price above holding → `⚠️ SEA $243 (over holding +$28)`
  - One booking, no holding price → `📊 SEA $215`
  - Multiple bookings → pipe-separated, ordered by pickup date
  - Booking with no price change still formats correctly

- [ ] Task 2: Implement `format_subject(bookings_data)` in `email_module/sender.py`
  <!-- files: email_module/sender.py -->
  <!-- depends: task1 -->
  - Extract per-booking signal: compare `current_price` vs `holding_price`
  - Format each segment; join with ` | `
  - Replace generic subject in `send_price_alert()`
  - Commit: `feat(email): add signal-driven subject line per booking`

- [ ] Task: Conductor - User Manual Verification 'Subject Line' (Protocol in workflow.md)

## Phase 2: HTML Card Redesign
<!-- execution: sequential -->
<!-- depends: -->

- [ ] Task 1: Write tests for updated `format_booking_card()` in `test_email_html.py`
  <!-- files: test_email_html.py -->
  - Status banner present when holding price set (green vs amber)
  - Status banner neutral when no holding price
  - Price hero shows current price, last-check delta (↑/↓/→), all-time low
  - All-time low highlighted when current price equals all-time low
  - No `<table>` price history rows in output
  - Better deals and all-categories sections still present

- [ ] Task 2: Add status banner to top of card in `html_template.py`
  <!-- files: email_module/templates/html_template.py -->
  <!-- depends: task1 -->
  - ✅ green banner: "Rebook opportunity — ${current} is ${delta} below your holding price"
  - ⚠️ amber banner: "Waiting — ${delta} above your holding price"
  - 📊 neutral: "No holding price set — currently ${current}"
  - Commit: `feat(email): add act-now/wait status banner to HTML card`

- [ ] Task 3: Restructure price hero section in `html_template.py`
  <!-- files: email_module/templates/html_template.py -->
  <!-- depends: task2 -->
  - Current price: large, prominent
  - Last-check delta: `↓ $12 (-5.3%)` green / `↑ $8 (+3.2%)` red / `→ No change` gray
  - All-time low row: `All-time low: $198` — gold highlight when current == all-time low
  - Source `all_time_low` from `focus_trends['lowest']` (already in `bookings_data`)
  - Commit: `feat(email): restructure price hero with delta and all-time low`

- [ ] Task 4: Remove price history table from `html_template.py`
  <!-- files: email_module/templates/html_template.py -->
  <!-- depends: task3 -->
  - Delete call to `format_price_history_table()` in `format_booking_card()`
  - Keep `format_price_history_table()` function (don't delete) — just stop calling it
  - Commit: `refactor(email): remove price history table from HTML card`

- [ ] Task: Conductor - User Manual Verification 'HTML Card Redesign' (Protocol in workflow.md)

## Phase 3: Plain Text Update
<!-- execution: sequential -->
<!-- depends: -->

- [ ] Task 1: Write tests for updated `format_email_body_text()` in `test_email_text.py`
  <!-- files: test_email_text.py -->
  - Status line present for each booking (rebook vs. wait vs. neutral)
  - All-time low present in output
  - No date×price history rows in output

- [ ] Task 2: Update `format_email_body_text()` in `formatters.py`
  <!-- files: email_module/templates/formatters.py -->
  <!-- depends: task1 -->
  - Add status line: "✅ REBOOK NOW — $X below holding" or "⚠️ WAITING — $X above holding"
  - Add all-time low from `focus_trends['lowest']`
  - Remove price history rows (no longer iterated)
  - Commit: `feat(email): update plain text email with status line and all-time low`

- [ ] Task: Conductor - User Manual Verification 'Plain Text Update' (Protocol in workflow.md)

## Phase 4: Validation
<!-- execution: sequential -->
<!-- depends: phase1, phase2, phase3 -->

- [ ] Task 1: Run full test suite — all email tests green
  <!-- files: test_email_sender.py, test_email_html.py, test_email_text.py -->

- [ ] Task 2: Send a live test email and verify layout in email client
  <!-- files: email_module/sender.py -->
  <!-- depends: task1 -->
  - Subject shows per-booking signals
  - Status banner is first visible element in each card
  - No price history table visible
  - Better deals and all-categories sections intact

- [ ] Task: Conductor - User Manual Verification 'Validation' (Protocol in workflow.md)
