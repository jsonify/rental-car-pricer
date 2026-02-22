# Plan: Docs Cleanup & README Refresh

## Phase 1: File Organization

- [ ] Task 1: Delete stale docs
  Remove from root:
  - BROWSER_AUTOMATION_COMPARISON.md
  - CHROMEDRIVER_SETUP_COMPLETE.md
  - MIGRATION_SUMMARY.md
  - SETUP_COMPLETE.md

- [ ] Task 2: Create docs/ and relocate surviving guides
  - Create docs/ directory
  - Move: QUICK_START.md, DEPLOYMENT.md, GMAIL_APP_PASSWORD_SETUP.md,
    GMAIL_SETUP_QUICKSTART.md, PLAYWRIGHT_QUICKSTART.md,
    SETUP_GITHUB_INTEGRATION.md, SETUP_MASTER_CHECKLIST.md,
    SUPABASE_SETUP_CHECKLIST.md
  - Scan moved files for cross-references to other docs and update paths

- [ ] Task 3: Conductor - User Manual Verification 'File Organization' (Protocol in workflow.md)

## Phase 2: README Rewrite

- [ ] Task 1: Rewrite README.md
  Sections:
  1. Title + one-line description
  2. Stack (React/Vite → GitHub Pages, Python/Playwright scraper, Supabase)
  3. Dashboard features (summary strip, booking cards, detail page, inline hold edit)
  4. Local development (Prerequisites, npm run dev, python3 main.py -i, .env vars)
  5. GitHub Actions / CI (price-checker schedule, deploy-dashboard trigger, Secrets list)
  6. Docs (link to docs/ folder)

- [ ] Task 2: Conductor - User Manual Verification 'README Rewrite' (Protocol in workflow.md)

## Phase 3: Validation

- [ ] Task 1: Verify no broken references and build still passes
  - Check docs/ files for references to deleted docs
  - Run npm run build — must pass with 0 errors

- [ ] Task 2: Conductor - User Manual Verification 'Validation' (Protocol in workflow.md)
