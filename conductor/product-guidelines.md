# Product Guidelines: Rental Car Pricer

## Visual Identity

**Style:** Clean and minimal. Low noise, high signal. Every element on screen should
earn its place. When in doubt, remove it.

**Inspiration:** Linear, Vercel dashboard — functional aesthetics over decoration.

**Color usage:**
- Use color purposefully, not decoratively
- Dark background preferred for a focused, distraction-free feel
- Neutral grays for supporting information
- Reserve color for signals (price changes, status indicators)

## Price Communication

**Green/red delta display** — price changes should be immediately scannable:
- Price dropped → green, downward arrow, dollar amount (e.g., `↓ $23`)
- Price increased → red, upward arrow, dollar amount (e.g., `↑ $14`)
- No change → neutral gray

Deltas should be prominent — the change *is* the story, not just the current number.

## Information Hierarchy

Each booking card should lead with what matters most:

1. **Current price** for the tracked car category — large, prominent
2. **Price change since tracking began** — immediately below, colored delta
3. Supporting context (pickup date, days remaining, etc.) in smaller type

Avoid burying the lead with charts, tables, or secondary categories on the primary view.

## Dashboard Philosophy

- Answer "should I rebook right now?" within 5 seconds of looking at the screen
- Prefer big numbers and clear labels over small charts
- Historical trends are secondary — surface them on demand, not by default
- No unnecessary UI chrome: minimize headers, borders, padding, and decorative elements

## Email Guidelines

Emails should read like a useful text message, not a report:
- Lead with the most actionable fact (e.g., "Price dropped $23 on your Vegas booking")
- Include the current price, the previous price, and the all-time low
- End with a clear recommendation: "Consider rebooking" or "Prices are rising, hold"
- No walls of text, no tables with 10 columns
