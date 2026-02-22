# Costco Travel Car Rental Price Tracker

Automated rental car price monitoring for Costco Travel. Tracks prices across multiple bookings, alerts you to drops, and surfaces better deals — all from a live React dashboard.

## Stack

| Layer | Technology |
|---|---|
| Dashboard | React + Vite, deployed to GitHub Pages |
| Scraper | Python + Playwright (headless Chrome) |
| Database | Supabase (bookings, price history, hold prices) |
| CI | GitHub Actions (scheduled scraper + dashboard deploy) |

## Dashboard Features

- **Portfolio summary** — total savings available across all bookings, price trend direction
- **Booking cards** — current price, vs-last-check delta, inline hold price editing, better deals, all-category breakdown, area chart
- **Detail page** — click any card to open a full-page view with a large price chart, $/day velocity indicator, and complete scrollable price history table
- **Test mode** — toggle between live Supabase data and local mock data for development

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.9+
- A Supabase project (see [docs/SUPABASE_SETUP_CHECKLIST.md](docs/SUPABASE_SETUP_CHECKLIST.md))

### Frontend

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production build
```

### Python Scraper

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
python3 main.py -i     # interactive mode — add/delete bookings, update holds
python3 main.py        # automated mode — run price checks (used by CI)
```

### Required `.env` variables

```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
NOTIFICATION_EMAIL=
```

## GitHub Actions / CI

### Price checker (`price-checker.yaml`)
- Runs every **Monday and Thursday at 6 AM PST**
- Can be triggered manually from the Actions tab
- Inputs: `add-booking`, `update-holding-prices`, `delete-booking`

### Dashboard deploy (`deploy-dashboard.yaml`)
- Triggers on every push to `main` that touches frontend files
- Bakes Vite environment variables from GitHub Secrets into the production bundle

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous (publishable) key |
| `VITE_GITHUB_TOKEN` | Personal access token with `repo` + `workflow` scopes |
| `VITE_GITHUB_OWNER` | GitHub username |
| `VITE_GITHUB_REPO` | Repository name |
| `SUPABASE_SERVICE_KEY` | Supabase service role (secret) key |
| `SUPABASE_URL` | Supabase project URL (for scraper) |
| `GMAIL_ADDRESS` | Gmail account for notifications |
| `GMAIL_APP_PASSWORD` | Gmail App Password |
| `NOTIFICATION_EMAIL` | Where to send price alert emails |

## Docs

Setup guides are in [`docs/`](docs/):

- [QUICK_START.md](docs/QUICK_START.md) — get running in 3 steps
- [SUPABASE_SETUP_CHECKLIST.md](docs/SUPABASE_SETUP_CHECKLIST.md) — database setup
- [SETUP_GITHUB_INTEGRATION.md](docs/SETUP_GITHUB_INTEGRATION.md) — GitHub Actions + Secrets
- [GMAIL_APP_PASSWORD_SETUP.md](docs/GMAIL_APP_PASSWORD_SETUP.md) — email notifications
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) — GitHub Pages deployment details
- [PLAYWRIGHT_QUICKSTART.md](docs/PLAYWRIGHT_QUICKSTART.md) — scraper / Playwright setup
