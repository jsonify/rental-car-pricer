# ✅ Master Setup Checklist

Your complete setup guide in one place!

## Prerequisites
- [x] Chrome for Testing (141.0.7390.65) - ✅ Installed
- [x] ChromeDriver (141.0.7390.65) - ✅ Installed
- [x] Python 3.7+ - ✅ Available
- [x] Node.js & npm - ✅ Available (for frontend)

## Part 1: Python Environment (1 minute)

- [x] Virtual environment created
  ```bash
  ./setup-venv.sh
  # Or manually: python3 -m venv venv && source venv/bin/activate && pip install selenium python-dotenv supabase
  ```

- [x] Test Chrome setup
  ```bash
  source venv/bin/activate
  python3 test-chrome.py
  ```
  Expected: ✅ Chrome launches and loads Google

## Part 2: Supabase Database (5 minutes)

📋 **Follow**: [SUPABASE_SETUP_CHECKLIST.md](SUPABASE_SETUP_CHECKLIST.md)

- [ ] Run SQL schema in Supabase
  - Go to https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/sql/new
  - Copy/paste `supabase/schema.sql`
  - Click "Run"

- [ ] Get API keys
  - Go to https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/settings/api
  - Copy `URL`, `anon` key, and `service_role` key

- [ ] Update `.env.local` (Frontend)
  ```bash
  VITE_SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
  VITE_SUPABASE_ANON_KEY=<your-anon-key>
  ```

- [ ] Update `.env` (Python)
  ```bash
  SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
  SUPABASE_SERVICE_KEY=<your-service-role-key>
  ```

- [ ] Test frontend
  ```bash
  npm run dev
  # Visit http://localhost:5173, toggle test mode OFF
  # Should see 2 sample bookings (KOA, HNL)
  ```

## Part 3: Gmail Setup (2 minutes)

📧 **Guide**: [GMAIL_SETUP_QUICKSTART.md](GMAIL_SETUP_QUICKSTART.md)

- [ ] Enable 2-Step Verification (if not already)
  - https://myaccount.google.com/signinoptions/two-step-verification

- [ ] Create App Password
  - https://myaccount.google.com/apppasswords
  - Select "Mail" or "Other (Custom name)"
  - Name it "Rental Car Tracker"
  - Copy 16-character password

- [ ] Update `.env`
  ```bash
  SENDER_EMAIL=your-email@gmail.com
  SENDER_PASSWORD=abcdefghijklmnop  # Remove spaces!
  RECIPIENT_EMAIL=your-email@gmail.com
  ```

- [ ] Test email (optional)
  ```bash
  source venv/bin/activate
  python3 test_email.py
  ```

## Part 4: First Run! (2 minutes)

- [ ] Run the scraper
  ```bash
  source venv/bin/activate
  python3 main.py -i
  ```

- [ ] Choose option 1 or 2
  - Option 1: Track existing bookings (sample KOA/HNL)
  - Option 2: Add your own booking

- [ ] Verify in Supabase
  - Check Table Editor for new price_histories
  - https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor

- [ ] Check email
  - You should receive a price alert email

- [ ] View in dashboard
  ```bash
  npm run dev
  # Visit http://localhost:5173
  # Toggle test mode OFF
  # See your live data!
  ```

## 🎉 You're Done!

### What Works Now

✅ **Python scraper**
- Logs into Costco Travel
- Scrapes rental car prices
- Stores in Supabase
- Sends email alerts

✅ **React dashboard**
- Real-time price monitoring
- Interactive charts
- Price history tracking
- Booking management

✅ **Test environment**
- Mock Supabase for testing
- No real API calls needed for dev

### Next Steps

1. **Delete sample bookings** (if you want)
   - Go to Supabase Table Editor
   - Delete KOA and HNL bookings

2. **Add your real bookings**
   - Run `python3 main.py -i`
   - Choose option 2: Add new booking
   - Or use the dashboard Admin Controls

3. **Set up automation** (optional)
   - GitHub Actions to run scraper daily
   - Or use cron job on your machine

4. **Customize**
   - Adjust email template
   - Add more vehicle categories
   - Change alert thresholds

## Quick Reference

```bash
# Activate Python environment
source venv/bin/activate

# Test Chrome
python3 test-chrome.py

# Run scraper (interactive)
python3 main.py -i

# Run scraper (automated)
python3 main.py

# Frontend dashboard
npm run dev

# Deactivate Python environment
deactivate
```

## Documentation Index

| Guide | Purpose |
|-------|---------|
| **QUICK_START.md** | 3-step quick start |
| **SUPABASE_SETUP_CHECKLIST.md** | Supabase database setup |
| **GMAIL_SETUP_QUICKSTART.md** | Gmail app password (quick) |
| **GMAIL_APP_PASSWORD_SETUP.md** | Gmail setup (detailed) |
| **CHROMEDRIVER_SETUP_COMPLETE.md** | Chrome/ChromeDriver details |
| **CLAUDE.md** | Architecture documentation |
| **README.md** | Project overview |

## Troubleshooting

**Chrome won't launch:**
```bash
python3 test-chrome.py
# Should show clear error messages
```

**Supabase connection fails:**
- Check `.env` has correct SUPABASE_URL and SUPABASE_SERVICE_KEY
- Check `.env.local` has correct VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
- Restart dev server after changing .env files

**Email not sending:**
- Verify App Password (no spaces!)
- Check spam folder
- Run `python3 test_email.py` for detailed error

**Frontend shows "Failed to fetch":**
- Toggle test mode OFF
- Check browser console for errors
- Verify Supabase API keys

Need help? Check the relevant guide above or ask! 🚀
