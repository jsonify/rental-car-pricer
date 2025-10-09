# 🚀 Quick Start Guide

Get your rental car price tracker running in 3 steps!

## ✅ Step 1: Python Setup (1 minute)

Run the setup script:

```bash
./setup-venv.sh
```

This creates a virtual environment and installs all Python dependencies.

**Manual alternative:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install selenium python-dotenv supabase
```

## ✅ Step 2: Supabase Setup (5 minutes)

Follow the checklist: **[SUPABASE_SETUP_CHECKLIST.md](SUPABASE_SETUP_CHECKLIST.md)**

Quick version:
1. Run SQL schema in Supabase dashboard
2. Copy API keys to `.env.local` (frontend) and `.env` (Python)
3. Test connection

## ✅ Step 3: Email Setup (2 minutes)

👉 **Quick Guide**: [GMAIL_SETUP_QUICKSTART.md](GMAIL_SETUP_QUICKSTART.md)
👉 **Full Guide**: [GMAIL_APP_PASSWORD_SETUP.md](GMAIL_APP_PASSWORD_SETUP.md)

**Super Quick:**
1. Go to https://myaccount.google.com/apppasswords
2. Create app password for "Rental Car Tracker"
3. Copy the 16-character password (remove spaces!)
4. Update `.env`:

```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop  # App password (no spaces!)
RECIPIENT_EMAIL=your-email@gmail.com
```

## 🎉 You're Ready!

### Test the Scraper

```bash
source venv/bin/activate  # If not already activated
python3 main.py -i
```

Options:
1. Track current bookings
2. Add a new booking
3. Delete a booking
4. Update holding prices

### Run the Dashboard

```bash
npm run dev
```

Visit http://localhost:5173

Toggle "Test Mode" OFF to see your real Supabase data.

## 📁 Your Configuration Files

### `.env` (Python - Backend)
```bash
# Supabase
SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Chrome (Already configured!)
CHROME_BINARY_PATH="/Applications/chrome/..."
CHROMEDRIVER_PATH=/Applications/chrome/.../chromedriver

# Email
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com
```

### `.env.local` (Frontend)
```bash
VITE_SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## 🔧 What's Already Done

✅ Chrome for Testing installed (141.0.7390.65)
✅ ChromeDriver downloaded and configured
✅ `.env` created with Chrome paths
✅ Supabase schema ready to run
✅ Frontend architecture improved

## 📚 Full Documentation

- **Chrome/ChromeDriver**: [CHROMEDRIVER_SETUP_COMPLETE.md](CHROMEDRIVER_SETUP_COMPLETE.md)
- **Supabase**: [SUPABASE_SETUP_CHECKLIST.md](SUPABASE_SETUP_CHECKLIST.md)
- **Architecture**: [CLAUDE.md](CLAUDE.md)
- **Migration**: [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)

## 🆘 Troubleshooting

### "No module named 'selenium'"
```bash
source venv/bin/activate  # Activate virtual environment first
```

### "ChromeDriver version mismatch"
Already solved! Chrome and ChromeDriver are both version 141.0.7390.65

### "Failed to connect to Supabase"
Check your `.env` and `.env.local` have the correct API keys from Supabase dashboard.

### "Email not sending"
Make sure you're using a Gmail App Password, not your regular password.

## 🎯 Next Steps

1. Run Supabase schema (see SUPABASE_SETUP_CHECKLIST.md)
2. Add your Gmail credentials to `.env`
3. Test: `python3 main.py -i`
4. Add your first booking
5. Let it run!

The scraper will automatically:
- Check prices for all active bookings
- Store results in Supabase
- Send consolidated email alerts
- Update the dashboard in real-time

You're all set! 🚗💨
