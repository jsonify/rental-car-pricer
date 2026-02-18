# Product Guide: Rental Car Pricer

## Vision

A personal, automated rental car price tracker for Costco Travel that saves money by
catching price drops — without requiring manual checking.

## Core Value Proposition

- **Save money**: Book at the lowest price by being alerted when prices drop
- **Eliminate manual work**: Automated scraping runs on a schedule, no babysitting required
- **Clarity over complexity**: The dashboard and emails should make prices instantly
  understandable at a glance

## Target Users

Solo use — the developer is the only user. Optimized for a single person who wants
low-friction, high-signal information about their upcoming rental car bookings.

## Current Focus Areas

### 1. Scraper Efficiency
The Selenium-based automation works but may be slow or fragile. Investigate whether
the current approach is optimal or if an alternative (e.g., API-based, lighter-weight
headless approach) would be more reliable and faster.

### 2. Dashboard Redesign
The existing React dashboard is being completely replaced. Current charts are
confusing and don't communicate useful information intuitively. The new design
should prioritize:
- Immediate clarity: what's the price right now vs. when I first tracked it?
- Simple trend communication: is this getting cheaper or more expensive?
- Clean, opinionated layout over feature density

### 3. Email Improvements
Email alerts are sent but currently lack useful context. Emails should clearly answer:
- Did the price go up or down since the last check?
- What's the best price seen so far for this booking?
- Should I act now, or wait?

## Success Criteria

- The scraper runs reliably on schedule without manual intervention
- Looking at the dashboard for 5 seconds tells me everything I need to know
- An email alert makes me immediately understand whether I should rebook
