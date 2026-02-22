# Docs Cleanup & README Refresh

## Overview
Declutter the project root by deleting stale one-off documentation artifacts,
consolidating surviving guides into a `docs/` folder, and rewriting README.md
to accurately reflect the current stack, local dev workflow, and CI setup.

## Functional Requirements

### FR1: Delete stale docs (root level)
Remove files that are outdated or no longer relevant:
- `BROWSER_AUTOMATION_COMPARISON.md` — decision made, Playwright won
- `CHROMEDRIVER_SETUP_COMPLETE.md` — we no longer use ChromeDriver
- `MIGRATION_SUMMARY.md` — one-time Supabase migration artifact
- `SETUP_COMPLETE.md` — references Chrome/ChromeDriver, obsolete

### FR2: Move surviving docs to docs/
Create `docs/` directory and relocate:
- `QUICK_START.md`
- `DEPLOYMENT.md`
- `GMAIL_APP_PASSWORD_SETUP.md`
- `GMAIL_SETUP_QUICKSTART.md`
- `PLAYWRIGHT_QUICKSTART.md`
- `SETUP_GITHUB_INTEGRATION.md`
- `SETUP_MASTER_CHECKLIST.md`
- `SUPABASE_SETUP_CHECKLIST.md`

### FR3: Rewrite README.md
Replace the outdated README with sections covering:
1. **What it is** — brief project description (Costco Travel price tracker)
2. **Stack** — React/Vite dashboard (GitHub Pages) + Python/Playwright scraper + Supabase
3. **Dashboard features** — portfolio summary, booking cards, detail page, inline hold edit
4. **Local development** — `npm run dev`, `python3 main.py -i`, required `.env` vars
5. **GitHub Actions / CI** — scheduled scraper workflow, dashboard deploy workflow,
   required GitHub Secrets list
6. **Docs** — link to `docs/` for setup guides

## Non-Functional Requirements
- README should be concise — a developer should orient in < 2 min
- Minimal emoji use
- Internal links within moved docs updated to reflect new `docs/` relative paths

## Acceptance Criteria
- [ ] 4 stale docs deleted from root
- [ ] `docs/` directory created with 8 surviving guides
- [ ] README.md rewritten to reflect current stack and workflow
- [ ] `npm run build` still passes
- [ ] No broken cross-references between docs

## Out of Scope
- Cleaning up Python migration scripts or other root-level non-doc files
- Updating content within the moved docs (structure only)
