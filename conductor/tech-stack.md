# Tech Stack: Rental Car Pricer

## Frontend

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | React | 18 |
| Language | TypeScript | 5.x |
| Build Tool | Vite | 5.x |
| Styling | Tailwind CSS | 3.x |
| UI Components | Radix UI | various |
| Charts | Recharts | 2.x |
| HTTP Client | @supabase/supabase-js | 2.x |
| GitHub API | @octokit/rest | 21.x |

## Backend (Python)

| Layer | Technology | Notes |
|-------|-----------|-------|
| Language | Python | 3.x |
| Browser Automation | **Selenium** (current) | ⚠️ Targeted for replacement — see below |
| HTTP | requests | 2.x |
| HTML Parsing | BeautifulSoup4 | 4.x |
| Env Config | python-dotenv | 1.x |
| DB Client | supabase | 2.x |

### Planned: Migrate Selenium → Playwright

`BROWSER_AUTOMATION_COMPARISON.md` documents the full analysis. Summary:
- **Problem**: Selenium requires manual ChromeDriver version matching, is slower, and is more easily detected
- **Solution**: Playwright auto-manages browsers, has built-in smart waiting, better stealth, and simpler setup
- **Effort**: ~2 hours
- **Status**: Planned (dedicated track)

## Infrastructure

| Layer | Technology |
|-------|-----------|
| Database | Supabase (PostgreSQL) |
| Frontend Hosting | GitHub Pages |
| Automation Scheduling | GitHub Actions (cron) |
| Workflow Dispatch | GitHub Actions + Octokit REST |
| Email | Gmail SMTP (Python smtplib) |

## Architecture Type

Dual-stack monorepo:
- Python scripts in root (scraper, CLI tools, Supabase sync)
- React app in `src/` (dashboard, deployed to GitHub Pages)
- Shared data layer via Supabase

## Environment

| Context | Details |
|---------|---------|
| Python runtime | Local + GitHub Actions |
| Node runtime | Local (dev) + GitHub Actions (build/deploy) |
| Secrets management | `.env` (local) + GitHub Secrets (CI) |
| Test mode | Mock Supabase client with localStorage persistence |
