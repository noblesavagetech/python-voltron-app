# Railway Deployment Guide

## 🚀 Deploy to Railway in 3 Steps

### Step 1: Prerequisites

- GitHub account connected to Railway
- Brevo account with API key
- (Optional) Vonage account for SMS MFA
- (Optional) Plaid account for bank integration

### Step 2: Deploy from GitHub

1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `noblesavagetech/python-voltron-app`
5. Railway will auto-detect Flask and start deployment

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database" → "Add PostgreSQL"**
3. Railway automatically sets `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

#### Required Variables

```bash
SECRET_KEY=<generate-random-64-char-string>
BREVO_API_KEY=<your-brevo-api-key>
SENDER_EMAIL=<your-verified-sender-email>
SENDER_NAME=BBA Services
```

#### Optional Variables (for SMS MFA)

```bash
VONAGE_API_KEY=<your-vonage-api-key>
VONAGE_API_SECRET=<your-vonage-api-secret>
VONAGE_BRAND_NAME=BBA Services
```

#### Optional Variables (for Plaid Bank Integration)

```bash
PLAID_CLIENT_ID=<your-plaid-client-id>
PLAID_SECRET=<your-plaid-secret>
PLAID_ENV=sandbox
PLAID_PRODUCTS=transactions,auth,identity
PLAID_COUNTRY_CODES=US
PLAID_REDIRECT_URI=https://<your-app>.railway.app/plaid/callback
```

### Step 5: Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as `SECRET_KEY` in Railway.

---

## 📋 Pre-Deployment Checklist

- [x] `runtime.txt` - Python version specified
- [x] `requirements.txt` - All dependencies listed
- [x] `Procfile` - Gunicorn web server configured
- [x] `railway.json` - Railway deployment settings
- [x] `.railwayignore` - Exclude unnecessary files
- [x] PostgreSQL-compatible database URL handling
- [x] Environment variable configuration

---

## 🔧 Get Your API Keys

### Brevo (Required for Email)

1. Sign up at [Brevo.com](https://www.brevo.com)
2. Go to **SMTP & API** → **API Keys**
3. Create new API key
4. Verify sender email in **Senders** section

### Vonage (Optional for SMS MFA)

1. Sign up at [Vonage.com](https://www.vonage.com)
2. Go to **Dashboard** → **API Settings**
3. Copy API Key and API Secret
4. Add test credits or payment method

### Plaid (Optional for Bank Integration)

1. Sign up at [Plaid.com](https://plaid.com)
2. Go to **Team Settings** → **Keys**
3. Get Sandbox credentials (free for testing)
4. For production, apply for Production access

---

## 🌐 Access Your App

After deployment:

1. Railway provides a public URL: `https://<your-app>.railway.app`
2. Visit the URL to see your live app
3. Create your first account
4. Test email verification (check spam folder)
5. Complete questionnaire
6. (Optional) Link bank account via Plaid

---

## 🐛 Troubleshooting

### Database Connection Issues

Railway auto-configures `DATABASE_URL`. The app handles the legacy `postgres://` → `postgresql://` conversion automatically.

### Email Not Sending

- Check Brevo API key is correct
- Verify sender email is confirmed in Brevo
- Check Railway logs: `railway logs`

### Build Failures

```bash
# Check Railway logs
railway logs

# Redeploy
railway up
```

### SMS MFA Not Working

- Verify Vonage credentials
- Check phone number format (+1234567890)
- Ensure Vonage account has credits

---

## 📊 Monitor Your App

```bash
# View live logs
railway logs

# Check app status
railway status

# Open app in browser
railway open
```

---

## 🔄 Update Deployment

Every push to `main` branch auto-deploys:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway automatically rebuilds and redeploys.

---

## 💰 Cost Estimate

- **Free Tier**: $5/month credit (sufficient for testing)
- **PostgreSQL**: ~$5/month (included in free tier)
- **Web Service**: ~$5/month (included in free tier)
- **Total**: FREE for hobby projects

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Brevo Support: https://help.brevo.com
- Vonage Docs: https://developer.vonage.com
- Plaid Docs: https://plaid.com/docs

---

## ✅ Post-Deployment

Once deployed, your app includes:

- ✅ Email verification system
- ✅ Financial health questionnaire
- ✅ User dashboard with insights
- ✅ Optional SMS MFA
- ✅ Optional bank account linking
- ✅ Transaction tracking
- ✅ Spending analytics

**Your production-ready financial health platform is live!** 🎉
