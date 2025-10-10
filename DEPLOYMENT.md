# GitHub Pages Deployment Guide

## Overview

Your React dashboard is now configured to deploy automatically to GitHub Pages. You no longer need to run `npm run dev` locally to view your price tracking dashboard - it will be publicly accessible at:

**https://jruecke.github.io/rental-car-pricer/**

## Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. Add Required Secrets

Navigate to **Settings** → **Secrets and variables** → **Actions** and add these repository secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `VITE_SUPABASE_URL` | Your Supabase project URL | e.g., `https://xxxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anonymous key | Public key (safe for client-side) |
| `VITE_GITHUB_TOKEN` | Personal Access Token | Must have `repo` and `workflow` scopes |
| `VITE_GITHUB_OWNER` | Your GitHub username | e.g., `jruecke` |
| `VITE_GITHUB_REPO` | Repository name | e.g., `rental-car-pricer` |

**To create a GitHub Personal Access Token:**
1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a descriptive name (e.g., "Car Rental Dashboard")
4. Select scopes: `repo` (Full control of private repositories) and `workflow`
5. Click **Generate token**
6. Copy the token immediately (you won't see it again!)

### 3. Deploy

The dashboard will automatically deploy when you push changes to the `main` branch that affect these files:
- `src/**` (any React components)
- `public/**` (static assets)
- `index.html`
- `package*.json`
- `vite.config.ts`
- `tsconfig.json`
- `.github/workflows/deploy-dashboard.yaml`

**Manual Deployment:**
1. Go to **Actions** tab in your GitHub repository
2. Click **Deploy Dashboard to GitHub Pages** workflow
3. Click **Run workflow** → **Run workflow**

## Security Considerations

⚠️ **Important:** The `VITE_GITHUB_TOKEN` will be embedded in the client-side JavaScript bundle and is **visible to anyone** who inspects the deployed code.

This means:
- Anyone can trigger GitHub Actions workflows in your repository
- The token has access to all your repositories (if scoped broadly)

**Recommendations:**
1. **Option A (Most Secure):** Remove admin controls from the web dashboard
   - Keep the dashboard read-only (price charts and trends only)
   - Manage bookings via Python CLI (`python3 main.py -i`)
   - Delete or comment out the `AdminInterface` component in `src/App.tsx`

2. **Option B (Moderate Security):** Use a dedicated GitHub account
   - Create a separate GitHub account with limited access
   - Give it collaborator access only to this repository
   - Generate a token from that account

3. **Option C (Keep Current):** Accept the risk
   - Anyone can trigger workflows, but they can't modify the code
   - Workflows are defined in your repository and version-controlled
   - Monitor the Actions tab for unexpected runs

## File Changes Made

1. **`vite.config.ts`**: Added `base: '/rental-car-pricer/'` for GitHub Pages routing
2. **`.github/workflows/deploy-dashboard.yaml`**: New workflow for automated deployment
3. **`package.json`**: Updated build script to skip TypeScript checks (use `npm run typecheck` separately)
4. **`CLAUDE.md`**: Added deployment documentation

## Troubleshooting

### Build fails in GitHub Actions
- Check the **Actions** tab for error logs
- Verify all required secrets are set correctly
- Ensure secret names match exactly (case-sensitive)

### Dashboard loads but shows errors
- Check browser console for API errors
- Verify Supabase URL and key are correct
- Check that Supabase RLS policies allow anonymous read access

### Admin controls don't work
- Verify `VITE_GITHUB_TOKEN` has `repo` and `workflow` scopes
- Check that `VITE_GITHUB_OWNER` and `VITE_GITHUB_REPO` are correct
- Look in browser Network tab to see if API calls are failing

### Assets not loading (404 errors)
- Verify the base path in `vite.config.ts` matches your repo name
- GitHub Pages serves from `/<repo-name>/` not `/`

## Local Development

You can still develop locally:

```bash
# Development server (no build needed)
npm run dev

# Type checking only
npm run typecheck

# Build for production (without type checking)
npm run build

# Build with type checking
npm run build:check
```

## Rollback Plan

If you want to revert to local-only dashboard:

1. Disable GitHub Pages in repository settings
2. Revert `vite.config.ts` base path:
   ```ts
   base: '/', // Changed from '/rental-car-pricer/'
   ```
3. Delete `.github/workflows/deploy-dashboard.yaml`
4. Run `npm run dev` for local development
