# Spec: Email Improvements

## Overview

Rewrite email alerts to be concise, actionable, and signal-driven. The primary question
each email must answer is: **"Should I rebook right now, or wait?"** This is determined
by comparing the current price to the holding (target) price for each booking.

Emails continue to be sent every scraper run. The subject line becomes the primary
signal — readable without opening the email.

## Functional Requirements

### Subject Line

Format: one segment per booking, pipe-separated, ordered by booking pickup date.

- If current price ≤ holding price: `✅ {LOCATION} ${current} (under holding)`
- If current price > holding price: `⚠️ {LOCATION} ${current} (over holding +${delta})`
- If no holding price set: `📊 {LOCATION} ${current}`

Example: `✅ SEA $215 (under holding) | ⚠️ LAX $310 (over holding +$20)`

### Email Body — Booking Card (HTML)

Each booking card must prominently display, in order:

1. **Status banner** (top of card):
   - Green/✅: "Rebook opportunity — ${current} is ${delta} below your holding price"
   - Amber/⚠️: "Waiting — ${delta} above your holding price"
   - Neutral: "No holding price set — currently ${current}"

2. **Price hero** (large, centered):
   - Current price (large)
   - Change since last check: `↓ $12 (-5.3%)` in green, `↑ $8 (+3.2%)` in red, `→ No change` in gray
   - All-time low for this booking: `All-time low: $198` (highlight if current == all-time low)

3. **Better deals** (keep, existing): cheaper car categories vs. focus category

4. **All categories** (keep, existing): sorted by price, focus category highlighted

### Removed Content

- ❌ Full price history table (date × price rows) — removed entirely

### Plain Text Version

Apply the same structural changes (subject format, status banner, hero section,
no history table) to the plain text fallback.

## Non-Functional Requirements

- No new dependencies — use existing smtplib, string formatting, datetime
- All-time low computed from existing `focus_trends['lowest']` value already passed in
- No visual regression for the sections being kept (better deals, all categories)

## Acceptance Criteria

- [ ] Subject line follows `✅/⚠️/📊 {LOC} ${price} (...)` format for each booking
- [ ] Status banner is the first thing visible in each card (rebook vs. wait)
- [ ] Current price + last-check delta displayed prominently
- [ ] All-time low displayed; highlighted when current price equals all-time low
- [ ] Price history table is completely absent from HTML and plain text
- [ ] Existing better-deals and all-categories sections unchanged
- [ ] Plain text version updated to match same structure

## Out of Scope

- Changing email send frequency (still sends every run)
- Adding new data sources (all data already available in `bookings_data`)
- Changing SMTP infrastructure
- Dashboard changes
