# GitHub Integration Setup

The web interface can now trigger GitHub Actions workflows directly! This allows you to manage bookings from the UI instead of manually running workflows in GitHub Actions.

## Required Setup

### 1. Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Give it a descriptive name: `rental-car-pricer-web-ui`
3. Set expiration (recommend 90 days or no expiration)
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### 2. Add Environment Variables

Add these to your `.env` file:

```bash
# Frontend GitHub Integration
VITE_GITHUB_TOKEN=ghp_your_token_here
VITE_GITHUB_OWNER=jsonify
VITE_GITHUB_REPO=rental-car-pricer
```

### 3. Restart Development Server

```bash
npm run dev
```

## How It Works

### Test Mode (Test Environment Toggle ON)
- Updates mock data in localStorage immediately
- No GitHub workflow triggered
- Great for testing UI without affecting production

### Production Mode (Test Environment Toggle OFF)
- Triggers GitHub Actions workflow
- Workflow runs the Python scraper
- Updates `price_history.json` and Supabase
- Commits changes to repo

## Usage

### Adding a Booking
1. Click "Add New Booking"
2. Fill in details (location, dates, category, holding price)
3. Click "Add Booking"
4. In production mode: Workflow triggers, check GitHub Actions for progress
5. In test mode: Booking added to mock data immediately

### Updating Holding Prices
1. Click "Update Holding Prices"
2. Enter new prices for bookings
3. Click "Submit"
4. In production mode: Workflow triggers for each price update
5. In test mode: Prices updated in mock data immediately

### Deleting a Booking
1. Click "Delete Booking"
2. Select booking to delete
3. Click "Delete Booking"
4. In production mode: Workflow triggers
5. In test mode: Booking deactivated in mock data immediately

## Monitoring Workflows

After triggering a workflow, you can monitor progress at:
https://github.com/jsonify/rental-car-pricer/actions

The workflow will:
1. Update `price_history.json`
2. Run the scraper (for add-booking)
3. Sync to Supabase
4. Commit changes

## Troubleshooting

### "GitHub configuration is missing" error
- Check that all three `VITE_GITHUB_*` variables are in `.env`
- Restart the dev server after adding variables

### "Failed to trigger workflow" error
- Verify your GitHub token has `repo` and `workflow` scopes
- Check that the token hasn't expired
- Ensure GITHUB_OWNER and GITHUB_REPO are correct

### Workflow doesn't start
- Check GitHub Actions tab for errors
- Verify the workflow file exists: `.github/workflows/price-checker.yaml`
- Ensure the workflow has `workflow_dispatch` trigger

## Security Notes

- **Never commit your `.env` file** (it's in `.gitignore`)
- The GitHub token gives full access to your repo - keep it secret!
- Revoke old tokens when creating new ones
- Consider using a token with minimal required scopes
