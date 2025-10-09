# 📧 Gmail App Password - Super Quick Guide

## TL;DR - 3 Minutes

### 1. Enable 2-Step Verification (if needed)
👉 **https://myaccount.google.com/signinoptions/two-step-verification**
- Click "Get Started"
- Add your phone number
- Done!

### 2. Create App Password
👉 **https://myaccount.google.com/apppasswords**
- Select app: **Mail** (or Other)
- Device: **Other (Custom name)** → type "Rental Car Tracker"
- Click **Generate**
- **Copy the 16-character password** (you won't see it again!)

### 3. Add to `.env`
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop  # No spaces!
RECIPIENT_EMAIL=your-email@gmail.com  # Can be same or different
```

**Remove spaces from the password!**
- Given: `abcd efgh ijkl mnop`
- Use: `abcdefghijklmnop`

## Test It

```bash
source venv/bin/activate
python3 test_email.py
```

Check your inbox!

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't find "App passwords" | Enable 2-Step Verification first |
| "Authentication failed" | Remove spaces from password |
| No email received | Check spam folder, verify email addresses |

## Full Guide

See **[GMAIL_APP_PASSWORD_SETUP.md](GMAIL_APP_PASSWORD_SETUP.md)** for detailed instructions with screenshots and troubleshooting.

---

**That's it!** Once your `.env` has the Gmail credentials, price alerts will be sent to your email automatically. 📬
