# BBA Services - Quick Start Guide

## Setup in 5 Minutes

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required
DATABASE_URL=sqlite:///dev.db
SECRET_KEY=your-random-secret-key-here
BREVO_API_KEY=your_brevo_api_key
SENDER_EMAIL=your-verified-email@example.com
SENDER_NAME=BBA Services
```

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000`

## Testing the Flow

### 1. Sign Up
- Go to http://localhost:5000
- Click "Get Started Free"
- Enter email and password
- Submit the form

### 2. Verify Email
- Check your email for verification code
- Enter the 6-digit code
- Click "Verify Email"

### 3. Complete Assessment
- Answer the 8 financial health questions
- Submit the questionnaire
- View your health score

### 4. Optional: Enable MFA
- From dashboard, click "Enable MFA"
- Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
- Enter the 6-digit code from your app
- MFA is now enabled!

## Getting API Keys

### Brevo (Required for Email)

1. Go to https://www.brevo.com/
2. Sign up for free account
3. Verify your sender email address
4. Navigate to Settings > SMTP & API
5. Create new API key
6. Copy and paste into `.env`

### MFA (Built-in - No Setup Required!)

TOTP-based MFA is built into the application. Users can enable it using any authenticator app:
- Google Authenticator (iOS/Android)
- Microsoft Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- 1Password (iOS/Android/Desktop)

No external API keys needed!

## Quick Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL
railway add

# Set environment variables
railway variables set BREVO_API_KEY=your_key_here
railway variables set SENDER_EMAIL=your_email@example.com
railway variables set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Deploy
railway up
```

## Troubleshooting

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Emails not sending"**
- Verify BREVO_API_KEY is correct
- Check SENDER_EMAIL is verified in Brevo dashboard
- Look for error messages in terminal

**"Database errors"**
- Delete `dev.db` file if it exists
- Restart the application
- Tables will be created automatically

**"MFA code not working"**
- Ensure your device clock is synchronized (TOTP is time-based)
- Try entering the code immediately after it refreshes
- Make sure you're using the correct account in your authenticator app

## Next Steps

1. ✅ Complete the signup flow
2. ✅ Take the financial health assessment
3. ✅ (Optional) Enable TOTP MFA
4. ✅ Deploy to Railway
5. ✅ Customize the questionnaire questions
6. ✅ Add your branding to templates

## Need Help?

- Check the main README.md for detailed documentation
- Review .env.example for all configuration options
- Ensure all required environment variables are set

---

**Happy Building! 🚀**
