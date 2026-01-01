# BBA Services - Financial Health Assessment Platform

A Flask web application featuring secure email verification, optional SMS-based MFA, financial health questionnaire, and bank account integration via Plaid.

## ✨ Features

- 🔐 **Secure Authentication**: Email verification via Brevo + optional SMS MFA via Vonage
- 📊 **Health Assessment**: Complete financial health questionnaire during signup
- 🏦 **Bank Integration**: Connect bank accounts via Plaid for transaction tracking
- 💰 **Financial Dashboard**: View balances, transactions, and spending analytics
- 📧 **Email Integration**: Brevo SMTP API for reliable email delivery  
- 📱 **SMS MFA**: Vonage Verify API for two-factor authentication
- 🏛️ **Production Ready**: PostgreSQL database with SQLite fallback
- 🚀 **Railway Deployment**: Optimized for cloud deployment
- 🔒 **Security First**: Password hashing, secure sessions, CSRF protection

## 🔄 User Flow

1. **Sign Up** → Enter email & password
2. **Email Verification** → Receive 6-digit code via Brevo email  
3. **Financial Health Assessment** → Complete 8-question questionnaire
4. **Dashboard** → View health score and insights
5. **Link Bank Account** → Connect accounts via Plaid Link
6. **Track Finances** → View transactions and spending analytics
7. **Optional MFA** → Enable SMS 2FA for enhanced security

## 🚀 Quick Start

### Local Development

```bash
# Clone and install
git clone https://github.com/noblesavagetech/python-voltron-app.git
cd python-voltron-app
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your configuration

# Run development server
python app.py
```

Visit `http://localhost:5000` in your browser!

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Configure environment variables in Railway dashboard:
# DATABASE_URL (auto-configured with Railway PostgreSQL)
# SECRET_KEY (generate secure key)
# BREVO_API_KEY (from Brevo account)
# SENDER_EMAIL (verified sender email)
# SENDER_NAME (display name for emails)
# PLAID_CLIENT_ID (from Plaid dashboard)
# PLAID_SECRET (from Plaid dashboard)
# PLAID_ENV (sandbox/development/production)
# VONAGE_API_KEY (optional, for MFA)
# VONAGE_API_SECRET (optional, for MFA)

# Deploy
railway up
```

## 🔧 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key-here
BREVO_API_KEY=your-brevo-api-key
SENDER_EMAIL=noreply@yourdomain.com

# Plaid (for bank integration)
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox
PLAID_PRODUCTS=transactions,auth,identity
PLAID_COUNTRY_CODES=US

# Optional  
SENDER_NAME="BBA Services"
VONAGE_API_KEY=your-vonage-key
VONAGE_API_SECRET=your-vonage-secret
VONAGE_BRAND_NAME="BBA Services"
FLASK_ENV=production
```

## 📁 Project Structure

```
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway deployment config
├── Dockerfile                # Docker container config
├── app/├── questionnaire.py # Health assessment routes
│   │   └── plaid.py         # Plaid bank linking routes
│   ├── utils/
│   │   ├── email.py         # Brevo email utilities
│   │   ├── sms.py           # Vonage SMS utilities
│   │   └── plaid_service.py # Plaid API integration
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── verify_email.html
│   │   ├── questionnaire.html
│   │   ├── dashboard.html
│   │   ├── enable_mfa.html
│   │   └── plaid/
│   │       ├── link.html
│   │       └── accounts
│   │   ├── index.html
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── verify_email.html
│   │   ├── questionnaire.html
│   │   ├── dashboard.html
│   │   └── enable_mfa.html
│   └── static/
│       └── css/
│           └── styles.css   # Application styles
```

## 🛡️ Security Features

- **Password Security**: Werkzeug password hashing with salt
- **Session Security**: HTTPOnly, Secure, SameSite cookies  
- **Email Verification**: 6-digit codes via Brevo
- **Optional SMS MFA**: Vonage Verify API with automatic voice fallback
- **CSRF Protection**: Built-in Flask-Login protection
- **Input Validation**: Email validation & sanitization


### Bank Accounts Table
- id, user_id
- plaid_item_id, plaid_account_id, plaid_access_token
- institution_name, account_name, account_type, mask
- current_balance, available_balance, credit_limit
- is_active, last_synced_at

### Transactions Table
- id, account_id
- plaid_transaction_id
- name, merchant_name, amount, currency_code
- category, primary_category, detailed_category
- date, pending, payment_channel
## 📋 Database Schema

### Users Table
- id, email, password_hash
- is_verified, verification_code, verified_at
- mfa_enabled, phone, vonage_request_id
- created_at, updated_at

### Questionnaire Responses Table
- id, user_id
- answers (JSON), score, tier
- created_at

## 📊 Financial Health Assessment

The questionnaire includes 8 questions covering:
- Monthly revenue
- Cash reserves
- Invoice payment timing
- Budget planning
- Financial review frequency
- Debt-to-income ratio
- Accounting software usage
- Profit margins

**Scoring Tiers:**
- **Developing** (0-33): Building foundation
- **Stable** (34-66): Solid foundation
- **Optimized** (67-100): Excellent health

## 🔍 API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page |
| `/auth/signup` | GET/POST | User registration |
| `/auth/login` | GET/POST | User login |
| `/auth/verify-email` | GET/POST | Email verification |
| `/auth/resend-verification` | GET | Resend verification code |
| `/auth/logout` | GET | User logout |
| `/questionnaire/take` | GET/POST | Take health assessment |
| `/dashboard` | GET | Protected dashboard |
| `/enable-mfa` | GET/POST | Enable SMS MFA |
| `/disable-mfa` | POST | Disable MFA |

## 🧪 Testing Emails

### Brevo Setup

1. Sign up at https://www.brevo.com/
2. Verify your sender email address
3. Get your API key from Settings > SMTP & API
4. Add to `.env`:
   ```
   BREVO_API_KEY=your_api_key_here
   SENDER_EMAIL=your_verified_email@example.com
   ```

### Vonage Setup (Optional)

1. Sign up at https://dashboard.nexmo.com/
2. Get API Key and API Secret from dashboard
3. Add to `.env`:
   ```
   VONAGE_API_KEY=your_api_key
   VONAGE_API_SECRET=your_api_secret
   ```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## 🚨 Production Checklist

- ✅ Set strong `SECRET_KEY`
- ✅ Configure PostgreSQL database via `DATABASE_URL`
- ✅ Set up Brevo account with verified sender email
- ✅ Enable HTTPS/SSL (automatic on Railway)
- ✅ Test email delivery in production environment
- ✅ Set up automated backups for database
- ✅ Monitor application logs and performance
- ✅ (Optional) Configure Vonage for SMS MFA

## 🐛 Troubleshooting

**App won't start:**
- Check that all required environment variables are set
- Verify database connection string format
- Ensure Python dependencies are installed

**Emails not sending:**
- Verify `BREVO_API_KEY` is correct
- Check `SENDER_EMAIL` is verified in Brevo
- Review application logs for API errors

**Database errors:**  
- Ensure PostgreSQL is running and accessible
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`

**MFA issues:**
- Verify Vonage API credentials
- Check phone number format (E.164: +1234567890)
- Ensure sufficient Vonage account balance

## 📄 Key Differences from Reference Apps

This application combines features from both reference repositories:

1. **From python-webapp-plaid-mfa:**
   - ✅ Email verification via Brevo
   - ✅ Optional SMS MFA via Vonage
   - ✅ Session-based authentication
   - ✅ PostgreSQL/SQLite support

2. **From python-webapp:**
   - ✅ Financial health questionnaire
   - ✅ Questionnaire scoring algorithm
   - ✅ Dashboard with health score display
   - ✅ User assessment tracking

3. **New Integration:**
   - ✅ Questionnaire integrated into signup flow
   - ✅ Email verification before assessment
   - ✅ Optional MFA enabled after assessment
   - ✅ Comprehensive dashboard showing all metrics

## 📚 Technologies Used

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Login
- **Database**: PostgreSQL (production), SQLite (development)
- **Email**: Brevo (SendinBlue) SMTP API
- **SMS**: Vonage Verify API
- **Deployment**: Railway, Docker, Gunicorn
- **Frontend**: Jinja2 templates, custom CSS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE for details.

---

**Built with ❤️ for secure, scalable financial health assessment**