# 📧 Gmail App Password Setup Guide

## What is a Gmail App Password?

An **App Password** is a 16-character code that lets apps (like your price tracker) access your Gmail account without using your actual password. It's more secure than using your regular password.

⚠️ **Important**: You CANNOT use your regular Gmail password. You must create an App Password.

## Prerequisites

✅ Your Gmail account must have **2-Step Verification** enabled.

## Step-by-Step Guide

### Step 1: Enable 2-Step Verification (if not already enabled)

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google," click **2-Step Verification**
4. Click **Get Started** and follow the prompts
5. Set up your phone number for verification codes

### Step 2: Create an App Password

1. **Go to App Passwords page**: https://myaccount.google.com/apppasswords

   Or navigate manually:
   - Google Account → Security → 2-Step Verification
   - Scroll down to **App passwords**
   - Click **App passwords**

2. **You may need to sign in again** for security

3. **Select the app and device**:
   - App: Select **Mail** (or "Other")
   - Device: Select **Other (Custom name)**
   - Type a name like: `Rental Car Price Tracker`

4. **Click Generate**

5. **Copy the 16-character password**
   - It will look like: `abcd efgh ijkl mnop`
   - **Important**: You won't be able to see this again, so copy it now!

6. **Click Done**

### Step 3: Add to Your `.env` File

Update your `.env` file:

```bash
# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com        # Your Gmail address
SENDER_PASSWORD=abcdefghijklmnop         # 16-char app password (no spaces!)
RECIPIENT_EMAIL=recipient@gmail.com       # Where to send alerts
```

**Important**: Remove spaces from the app password!
- ✅ Correct: `SENDER_PASSWORD=abcdefghijklmnop`
- ❌ Wrong: `SENDER_PASSWORD=abcd efgh ijkl mnop`

## Quick Access Links

- **Enable 2-Step Verification**: https://myaccount.google.com/signinoptions/two-step-verification
- **Create App Password**: https://myaccount.google.com/apppasswords
- **Security Settings**: https://myaccount.google.com/security

## Troubleshooting

### "App passwords" option not showing

**Cause**: 2-Step Verification is not enabled.

**Solution**:
1. Go to https://myaccount.google.com/signinoptions/two-step-verification
2. Enable 2-Step Verification
3. Wait a few minutes
4. Try accessing App Passwords again

### "Less secure app access" message

**Cause**: You're trying to use your regular password instead of an App Password.

**Solution**: Follow the steps above to create an App Password and use that instead.

### Email not sending

**Cause**: App password might have spaces or be incorrect.

**Solution**:
1. Remove all spaces from the 16-character password
2. Make sure you copied it correctly
3. If it still doesn't work, generate a new App Password

### "Authentication failed"

**Causes**:
- Wrong email address
- Wrong app password
- Spaces in the app password
- Account security settings blocking access

**Solution**:
1. Double-check `SENDER_EMAIL` matches your Gmail
2. Regenerate the App Password
3. Copy without spaces
4. Try again

## Test Your Email Setup

Once configured, test it:

```bash
source venv/bin/activate
python3 test_email.py
```

You should receive a test email at your `RECIPIENT_EMAIL` address.

## Example `.env` Configuration

Here's what a complete email section looks like:

```bash
# Email Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=john.doe@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
RECIPIENT_EMAIL=john.doe@gmail.com
```

**Notes**:
- `SENDER_EMAIL` and `RECIPIENT_EMAIL` can be the same
- Remove all spaces from `SENDER_PASSWORD`
- The app password is case-insensitive

## Security Best Practices

✅ **Do**:
- Keep your App Password secret
- Store it only in `.env` (which is in .gitignore)
- Revoke App Passwords you're not using

❌ **Don't**:
- Share your App Password
- Commit `.env` to git
- Use your regular Gmail password
- Reuse App Passwords across projects

## Revoking App Passwords

If you need to revoke an App Password:

1. Go to https://myaccount.google.com/apppasswords
2. Find the app password (e.g., "Rental Car Price Tracker")
3. Click **Remove**
4. Generate a new one if needed

## Alternative: Using Gmail OAuth2 (Advanced)

If you want more security, you can use OAuth2 instead of App Passwords. This is more complex but more secure. Let me know if you want help setting this up!

---

**Once you have your App Password, update `.env` and you're ready to receive price alerts!** 📧
