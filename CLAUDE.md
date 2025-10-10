# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A dual-stack rental car price tracker for Costco Travel with:
- **Python backend**: Selenium-based web scraper that monitors car rental prices
- **React/TypeScript frontend**: Real-time dashboard for viewing price trends and managing bookings
- **Supabase integration**: Database for storing bookings and price history
- **Test environment**: Mock data support for development without hitting production APIs

## Common Commands

### Frontend (React + Vite)
- **Development server**: `npm run dev` (runs on http://localhost:5173)
- **Build**: `npm run build` (TypeScript compilation + Vite build)
- **Lint**: `npm run lint`
- **Preview production build**: `npm run preview`
- **Live dashboard**: Deployed to GitHub Pages at https://jruecke.github.io/rental-car-pricer/

### Python Backend
- **Interactive mode**: `python3 main.py -i` or `python3 main.py --interactive`
  - Allows adding/deleting bookings, updating holding prices
- **Automated mode**: `python3 main.py` (for CI/GitHub Actions)
- **Setup**: `python3 setup.py` (first-time configuration)
- **Dashboard server**: `python3 dashboard_server.py` (legacy HTTP server on port 8000)

### Python Dependencies
```bash
pip3 install selenium python-dotenv supabase
```

## Architecture

### Data Flow (Unified)
1. **Python scraper** (`main.py`) → Selenium WebDriver → Costco Travel website
2. Extracted prices → `price_history.json` (local) AND Supabase (bookings, price_histories tables)
3. **React dashboard** → Unified Supabase client (real or mock) → displays real-time price trends
4. **Environment switcher**: Toggle between production (Supabase) and test (mock data) modes
   - **Production**: Uses real Supabase client with `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
   - **Test**: Uses mock Supabase client that implements the same API but stores data in localStorage

### Frontend Architecture (Refactored)
- **Single client interface**: `createSupabaseClient(isTestEnvironment)` returns appropriate client
- **Data fetching layer**: Custom hook `useBookings()` handles all data fetching logic
- **Components are pure**: PriceTracker and AdminInterface don't know about test vs production
- **Mock store**: Persists to localStorage (`mockSupabaseStore` key), survives page refreshes
- **Type safety**: All components use shared TypeScript interfaces from `src/lib/types.ts`

### Key Python Modules
- **`booking_tracker.py`**: Manages booking CRUD operations with `price_history.json`
- **`price_monitor.py`**: Core Selenium logic for Costco Travel automation
- **`human_simulation.py`**: Anti-bot techniques (random typing delays, mouse movements)
- **`price_extractor.py`**: Extracts prices from search results DOM
- **`supabase_updater.py`**: Syncs Python data to Supabase database
- **`email_module/`**: Sends consolidated email alerts with price changes

### Key TypeScript/React Files
- **`src/App.tsx`**: Main app layout with EnvironmentProvider, PriceTracker, AdminInterface
- **`src/contexts/EnvironmentContext.tsx`**: Manages test/production mode toggle (persisted in localStorage)
- **`src/lib/supabase.ts`**: Factory function `createSupabaseClient(isTestEnvironment)` that returns real or mock client
- **`src/lib/mock-supabase.ts`**: Mock Supabase client with full API compatibility (select, insert, update, delete)
- **`src/lib/types.ts`**: TypeScript interfaces for Booking, PriceHistory, HoldingPriceHistory, BookingWithHistory
- **`src/hooks/useBookings.ts`**: Custom hook that fetches bookings with price history (works with both environments)
- **`src/components/PriceTracker.tsx`**: Main dashboard view (simplified, uses useBookings hook)
- **`src/components/AdminInterface.tsx`**: Booking management UI (uses Supabase client directly)
- **`src/components/TestControls.tsx`**: Test environment utilities (add/reset/clear mock data)

### Supabase Schema
- **`bookings`**: location, pickup_date, dropoff_date, focus_category, holding_price, active
- **`price_histories`**: booking_id, timestamp, prices (JSONB), created_at
- **`holding_price_histories`**: booking_id, price, effective_from, effective_to

### Test Environment System (Improved)
The app has a unified dual-mode system:
- **Production mode**: Uses real Supabase client connecting to `VITE_SUPABASE_URL`
- **Test mode**: Uses mock Supabase client with faker-generated data stored in localStorage (`mockSupabaseStore`)
- **Unified API**: Both clients implement the same Supabase interface (`.from()`, `.select()`, `.insert()`, `.update()`, `.delete()`)
- **Single code path**: Components call the same methods regardless of environment
- **Persistence**: Mock data persists across page refreshes via localStorage
- **Test utilities**: `testUtils` object provides `addMockBooking()`, `resetMockStore()`, `clearMockStore()`
- Toggle via `EnvironmentSwitcher` component (state in localStorage key `use-test-environment`)

## Configuration Files
- **`.env`**: Required for Python scripts (SUPABASE_URL, SUPABASE_SERVICE_KEY, Gmail credentials)
- **Vite env vars**: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_GITHUB_TOKEN`, `VITE_GITHUB_OWNER`, `VITE_GITHUB_REPO`
- **`price_history.json`**: Local JSON database for bookings (Python-managed)
- **`price_history.template.json`**: Template structure for initializing empty history

### GitHub Pages Deployment
The React dashboard is automatically deployed to GitHub Pages on every push to `main` that modifies frontend files.

**Required GitHub Secrets** (Settings → Secrets and variables → Actions):
- `VITE_SUPABASE_URL`: Supabase project URL
- `VITE_SUPABASE_ANON_KEY`: Supabase anonymous key (public, safe for client-side)
- `VITE_GITHUB_TOKEN`: Personal access token with `repo` and `workflow` scopes
- `VITE_GITHUB_OWNER`: GitHub username (e.g., "jruecke")
- `VITE_GITHUB_REPO`: Repository name (e.g., "rental-car-pricer")

**Deployment workflow**: `.github/workflows/deploy-dashboard.yaml`
- Triggers on pushes to `main` affecting frontend files
- Can be manually triggered via "Actions" tab → "Deploy Dashboard to GitHub Pages" → "Run workflow"
- Requires GitHub Pages to be enabled (Settings → Pages → Source: GitHub Actions)

**Note on security**: The `VITE_GITHUB_TOKEN` will be embedded in the client-side JavaScript bundle and is visible to anyone. Consider the security implications of allowing public workflow triggers. For enhanced security, you could remove admin controls from the dashboard and manage bookings via Python CLI only.

## Important Implementation Details

### Selenium Anti-Bot Measures
The scraper in `price_monitor.py` uses several techniques to avoid detection:
- Custom Chrome binary path (Google Chrome for Testing)
- Disabled automation flags (`--disable-blink-features=AutomationControlled`)
- Random typing delays (0.1-0.3s per character)
- Random mouse movements
- Human-like form interaction with verification retries

### Price History Management
- Each booking generates a unique ID: `{LOCATION}_{PICKUP_DATE}_{DROPOFF_DATE}` (slashes removed)
- Prices stored as dictionary: `{ "Economy Car": 299.99, "Full-size Car": 350.00, ... }`
- Trends calculated from all historical records for the focus_category
- Expired bookings automatically cleaned up (dropoff_date < current_date)

### Email Notifications
- Consolidates all bookings into single email
- Includes focus category price + trend, cheaper alternatives, historical ranges
- Uses HTML templates in `email_module/templates/`
- Sent via Gmail SMTP with App Password authentication

### GitHub Actions Integration (Production)
- Workflow file: `.github/workflows/price-checker.yaml` (if exists)
- Triggered via Octokit REST API
- Actions: `add-booking`, `update-holding-prices`, `delete-booking`
- Inputs passed as workflow dispatch parameters

## Development Workflow

1. **Adding a new booking** (Python):
   - Run `python3 main.py -i` → select option 2
   - Validates category availability for location before saving

2. **Adding a new booking** (React):
   - Use AdminInterface component
   - In test mode: triggers mock workflow
   - In production mode: dispatches GitHub Actions workflow

3. **Testing price scraper**:
   - Screenshots saved to `screenshots/` directory
   - Error screenshots: `error_{LOCATION}_{TIMESTAMP}.png`
   - Success screenshots: `results_{LOCATION}_{TIMESTAMP}.png`
   - Selenium logs: `selenium.log`

4. **Working with test data**:
   - Toggle test environment in UI (top-right switch)
   - Data persists in localStorage (`mockStore` key)
   - Use "Clear Mock Store" button to reset test data

## Path Aliases
- TypeScript uses `@/` alias for `./src/` (configured in vite.config.ts and tsconfig.json)
