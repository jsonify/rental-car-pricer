# DriveTrack Dashboard
## Product Requirements Document (PRD)
**Version:** 1.0  
**Status:** Draft  
**Author:** Product Team  
**Last Updated:** February 2026

---

## 1. Overview

### 1.1 Product Summary
DriveTrack is a car rental price tracking and monitoring dashboard that enables users to watch, compare, and act on rental pricing across vehicle classes, airports, and time periods. The dashboard surfaces real-time and historical pricing intelligence to help individual travelers, corporate travel managers, and fleet operators make informed booking decisions and avoid overpaying.

### 1.2 Problem Statement
Car rental prices are highly dynamic, fluctuating by time of day, demand, season, and location. Travelers currently have no consolidated tool to:
- Track prices against a personal target or budget
- Monitor price surges across vehicle classes in real time
- Identify the optimal booking window based on historical trends
- Receive alerts when a target price is hit or a surge is detected

### 1.3 Goals & Success Metrics

| Goal | Metric | Target |
|---|---|---|
| Reduce avg. booking overpay | % of bookings within target price | ≥ 75% |
| Increase user engagement | Weekly active users | +40% MoM |
| Drive alert-to-booking conversion | Alerts → booking rate | ≥ 30% |
| Improve data confidence | Price data freshness | ≤ 15 min staleness |

---

## 2. Users & Personas

### 2.1 Primary Personas

**Persona 1 — The Frequent Traveler (Jason)**
- Books 4–8 rentals per year, primarily for work trips
- Wants to know when prices drop so he can book at the right time
- Monitors specific airports and vehicle classes (mid-size, SUV)
- Values a clean, at-a-glance summary — not a spreadsheet

**Persona 2 — Corporate Travel Manager**
- Manages travel budgets for a team of 20–100 employees
- Needs visibility into average spend by vehicle class vs. policy limits
- Wants exportable reports and configurable alert thresholds
- Cares deeply about the Price Watch table and surge alerts

**Persona 3 — Bargain Hunter / Leisure Traveler**
- Flexible travel dates, looking for the lowest possible daily rate
- Monitors economy and mid-size classes at major airports
- Engages primarily with the Lowest Price Found card and trend wave

### 2.2 Out of Scope Users
- Rental agencies / fleet operators (supply side)
- Users seeking long-term (30+ day) rental tracking (v2 consideration)

---

## 3. Feature Requirements

### 3.1 Navigation Bar
**Priority:** P0

The top navigation must be persistent across all views and include:

- **Brand identity:** Logo icon + "DriveTrack" wordmark
- **Primary nav tabs:** Dashboard, Vehicles, Alerts, Bookings, More (dropdown)
- **Active state:** Highlighted tab with distinct background (e.g., green pill)
- **Utility icons:** Notifications bell (with unread badge), Bookmarks, Settings, User avatar with profile dropdown
- **Responsive behavior:** On mobile, collapse nav tabs into a hamburger menu

**Acceptance Criteria:**
- Active page tab is visually distinct at all times
- Notification badge reflects unread alert count in real time
- User avatar opens a dropdown with Profile, Preferences, Sign Out

---

### 3.2 Tracked Rentals Card
**Priority:** P0

The primary summary card at the top left provides an aggregate view of monitored rental pricing activity for the selected time period.

**Displayed Data:**
- Total average price across all tracked vehicles/searches for the period
- Subtitle showing count of actively tracked vehicles (e.g., "avg. across 14 tracked vehicles")
- Mini bar chart visualizing daily price variance across the selected period (colorized by volatility level — green = stable, red = volatile)
- Time filter selector: Today / This Month / This Year

**Behavior:**
- Bars update dynamically based on selected time filter
- Clicking a bar narrows the date range to that specific day's detail view
- Color coding of bars reflects price deviation from user's target price (green = at/below target, yellow = within 15%, red = above target)

**Acceptance Criteria:**
- Default view loads "This Month" on page load
- Bar chart renders within 500ms of data load
- Tooltip on hover shows date + avg price for that day

---

### 3.3 Lowest Price Found Card
**Priority:** P0

Highlights the best deal currently available across all user-tracked searches.

**Displayed Data:**
- Lowest daily rate found ($/day)
- Delta vs. same metric last week (e.g., "↓ $12.00 from last week")
- % change indicator (green, downward arrow)
- Vehicle class and pickup location context (e.g., "Economy · Seattle-Tacoma Airport")
- Calendar icon to trigger date picker for filtering

**Behavior:**
- Updates in real time as prices change (polling interval: ≤ 15 min)
- Tapping/clicking the card opens the full deal detail view
- If price drops more than 20% from user's set target, triggers a push/email notification

**Acceptance Criteria:**
- Card always reflects the single lowest price across all active tracked searches
- % change color: green for drop, red for increase
- Null state ("No active searches") shown if user has no tracked vehicles

---

### 3.4 Highest Price Surge Card
**Priority:** P0

Mirrors the Lowest Price card but surfaces the worst-performing (most expensive) tracked search to warn users of surges.

**Displayed Data:**
- Highest current daily rate ($/day)
- Delta vs. last week (e.g., "+$44.00 from last week")
- % change in red (upward arrow)
- Vehicle class and location context
- Calendar icon for date filtering

**Behavior:**
- If surge exceeds user's configured threshold (default: +25%), badge glows red and sends alert
- Card links to the specific search detail page for that vehicle/location

**Acceptance Criteria:**
- Surge threshold is user-configurable in Settings
- Card never shows the same vehicle/location as the Lowest Price card
- Color coding is always red/orange for this card regardless of direction

---

### 3.5 Price Range & Booking Flow Chart
**Priority:** P0

The central, full-width visualization showing monthly average rental rates alongside booking volume across the full year.

**Chart Type:** Grouped bar chart (2 bars per month)

**Data Series:**
- **Bar 1 (solid teal):** Average daily rental rate for that month
- **Bar 2 (hatched/textured):** Number of bookings made by the user or tracked pool in that month

**Displayed Data:**
- X-axis: Jan – Dec
- Y-axis (left): Price scale ($0 – $200+)
- Y-axis (right, optional v2): Booking volume scale
- Active month highlighted in neon green/cyan
- Tooltip on hover: Month label, Avg Rate ($/day), Bookings count

**Behavior:**
- Time filter (Today / This Month / This Year) changes granularity:
  - Today → hourly bars
  - This Month → daily bars
  - This Year → monthly bars (default)
- Clicking a bar drills down into that period's detail
- Legend is displayed below or inline with the chart

**Acceptance Criteria:**
- Chart renders with all 12 months on initial load
- Tooltip appears within 100ms of hover
- Highlighted (active) month is visually distinct from all others
- Chart is responsive and scrollable horizontally on mobile

---

### 3.6 Price Trend Flow Card
**Priority:** P1

A visual-first card showing the 30-day rolling average price trend as an animated wave/line chart, rendered on a gradient background for quick emotional signal (rising vs. falling market).

**Displayed Data:**
- Line chart: 30-day rolling average price across all tracked searches
- Gradient background: shifts from green (prices falling) to yellow/red tones (prices rising) based on trend direction
- Label: "30-day rolling average"

**Behavior:**
- Wave animates on page load (draw-in animation left to right)
- Gradient updates daily based on 7-day trend direction
- No interactivity required in v1 (tooltip hover is a v2 enhancement)

**Acceptance Criteria:**
- Gradient is green-dominant when 7-day trend is downward
- Gradient shifts to orange/red when 7-day trend is upward ≥ 10%
- Line chart uses smoothed cubic bezier curves (not jagged polyline)

---

### 3.7 Vehicle Class Pricing Gauge
**Priority:** P1

A semi-circular donut/gauge chart showing the distribution of average pricing across vehicle classes, with a needle indicating the currently selected or most-watched class.

**Vehicle Classes (segments):**
- Economy (green)
- Mid-size (cyan)
- Full-size SUV (indigo/purple)
- Luxury (violet)

**Displayed Data:**
- Gauge with colored arc segments proportional to class volume tracked
- Needle pointing to the most-watched / highest activity class
- Center label: avg daily rate for needle-pointed class
- Subtitle: vehicle class name + "avg daily rate"
- Legend below the gauge

**Behavior:**
- Clicking a segment filters the Price Watch table (3.8) to that class
- Needle animates to new position when class selection changes
- Segment sizes reflect the proportion of user's active searches per class

**Acceptance Criteria:**
- All 4 segments always visible (minimum arc size enforced)
- Selected segment is visually emphasized (brighter stroke or glow)
- Center value updates dynamically on segment click

---

### 3.8 Price Watch Table
**Priority:** P0

A data table providing a structured, scannable breakdown of pricing performance by vehicle type against the user's configured target prices.

**Columns:**
| Column | Description |
|---|---|
| Vehicle Type | Category name (Economy, Mid-size, Full-size SUV, Luxury) |
| Target Price | User-configured max acceptable daily rate |
| Current Avg | Live average daily rate from tracked searches |
| Alert Status | Color-coded indicator + % of target consumed |

**Alert Status Logic:**
- 🟢 Green (≤ 90% of target): "Good deal — book now"
- 🟡 Yellow (91–110% of target): "Approaching limit"
- 🔴 Red (> 110% of target): "Over budget target"

**Behavior:**
- Rows are clickable and open a detail drawer for that vehicle class
- Target Price is editable inline (click to edit, enter to save)
- Table supports sorting by any column header
- Alert column triggers push/email notification when status changes to 🔴

**Acceptance Criteria:**
- Table always shows all 4 vehicle classes (no pagination in v1)
- Inline edit saves target price to user profile within 2 seconds
- Color coding updates in real time as prices change
- A legend explaining color codes is shown below the table

---

## 4. Data Requirements

### 4.1 Data Sources
- **Primary pricing data:** Aggregated from rental provider APIs (Enterprise, Hertz, Avis, Budget, SIXT) or a third-party aggregator (e.g., CarRentals.com API, Kayak API)
- **Booking data:** User-connected booking accounts or manual entry
- **Airport/location data:** IATA airport codes + display name lookup table

### 4.2 Data Freshness
- Price data: refreshed every 15 minutes
- Historical chart data: refreshed every 24 hours
- Booking count data: refreshed on user session load

### 4.3 Data Storage
- User-defined target prices stored in user profile DB
- Price history retained for 12 months per tracked search
- Alert event log retained for 90 days

---

## 5. Design Requirements

### 5.1 Visual Design
- **Theme:** Dark mode primary (light mode as v2 enhancement)
- **Primary accent:** Neon green (#00F5A0) for positive indicators and active states
- **Secondary accent:** Cyan (#00D9F5) for data series and highlights
- **Alert red:** #F87171 for surges and over-budget states
- **Warning yellow:** #FBBF24 for approaching-limit states
- **Background:** #111827 (cards), #1A1A2E (page)
- **Typography:** System sans-serif (Segoe UI / Inter fallback)

### 5.2 Responsive Breakpoints
| Breakpoint | Layout |
|---|---|
| Desktop (≥ 1280px) | Full 3-column grid as designed |
| Tablet (768–1279px) | 2-column grid; chart full width |
| Mobile (< 768px) | Single column stack; chart scrollable |

### 5.3 Accessibility
- All color indicators must have a text/icon fallback (not color alone)
- Minimum contrast ratio: 4.5:1 for all text
- Keyboard navigable tabs and table rows
- Screen reader labels on all chart elements

---

## 6. Alerts & Notifications

### 6.1 Alert Types
| Alert | Trigger | Channel |
|---|---|---|
| Price Drop Alert | Tracked price drops ≥ configured % below target | Push + Email |
| Surge Warning | Tracked price rises ≥ 25% above target | Push + Email |
| Best Time to Book | Historical model predicts price will rise in 48h | Email |
| Weekly Digest | Summary of price movements for all tracked searches | Email |

### 6.2 User Controls
- Users can enable/disable each alert type individually
- Surge threshold is configurable (default 25%, range 5–50%)
- Drop threshold is configurable (default 15%, range 5–40%)
- Quiet hours configurable for push notifications

---

## 7. Out of Scope (v1)

- Supply-side / rental agency portal
- Multi-user / team sharing of tracked searches
- Flight + rental bundle tracking
- Mobile native app (web responsive only in v1)
- Light mode theme
- International currency support (USD only in v1)
- AI-powered "best time to book" prediction engine (v2)

---

## 8. Open Questions

1. Should users be able to track prices without creating an account (guest mode with local storage)?
2. What is the maximum number of concurrent tracked searches per user (free vs. paid tier)?
3. Will we build our own scraping/API layer or rely entirely on a third-party aggregator?
4. How do we handle rental providers that don't expose public APIs?
5. What is the retention and deletion policy for user search history?

---

## 9. Timeline (Proposed)

| Milestone | Target Date |
|---|---|
| PRD finalized & approved | Week 1 |
| Design mockups (Figma) | Week 3 |
| Design review & sign-off | Week 4 |
| Frontend scaffolding + nav | Week 5 |
| Core cards (P0 components) | Week 7 |
| Chart & table components | Week 9 |
| Data integration (API layer) | Week 10 |
| Alert system implementation | Week 11 |
| QA & bug bash | Week 12 |
| Beta launch | Week 13 |
| v1.0 GA release | Week 15 |
