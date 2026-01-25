"""Main application routes"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import db, BankAccount, Transaction
from app.utils.totp import generate_totp_secret, get_totp_uri, generate_qr_code, verify_totp_code
from app.utils.email import send_mfa_enabled_notification

main_bp = Blueprint('main', __name__)


@main_bp.route('/health')
def health():
    """Health check endpoint for Railway."""
    return {'status': 'ok'}, 200


@main_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with bank accounts and transactions."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    # Get user's questionnaire responses
    from app.models import QuestionnaireResponse
    latest_response = QuestionnaireResponse.query.filter_by(
        user_id=current_user.id
    ).order_by(QuestionnaireResponse.created_at.desc()).first()
    
    # Get bank accounts
    bank_accounts = BankAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Get recent transactions (last 30 days)
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    recent_transactions = Transaction.query.join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).order_by(Transaction.date.desc()).limit(10).all()
    
    # Calculate total balance across all accounts
    total_balance = sum(acc.current_balance or 0 for acc in bank_accounts)
    
    # Calculate spending by category (last 30 days)
    spending_by_category = db.session.query(
        Transaction.primary_category,
        func.sum(Transaction.amount).label('total')
    ).join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= thirty_days_ago,
        Transaction.amount > 0  # Only expenses (positive amounts in Plaid)
    ).group_by(Transaction.primary_category).all()
    
    return render_template(
        'dashboard.html',
        assessment=latest_response,
        bank_accounts=bank_accounts,
        recent_transactions=recent_transactions,
        total_balance=total_balance,
        spending_by_category=spending_by_category
    )


@main_bp.route('/enable-mfa', methods=['GET', 'POST'])
@login_required
def enable_mfa():
    """Enable TOTP-based MFA (Google Authenticator, Microsoft Authenticator, Authy, 1Password)."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if current_user.mfa_enabled:
        flash('MFA already enabled.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        totp_code = request.form.get('totp_code', '').strip()
        pending_secret = session.get('mfa_secret_pending')
        
        if not pending_secret:
            flash('Session expired. Please try again.', 'danger')
            return redirect(url_for('main.enable_mfa'))
        
        # Verify the TOTP code
        if verify_totp_code(pending_secret, totp_code):
            # SUCCESS: Save to database
            current_user.enable_mfa(pending_secret)
            db.session.commit()
            
            # Clean up session
            session.pop('mfa_secret_pending', None)
            
            # Send confirmation email
            send_mfa_enabled_notification(current_user.email, 'Authenticator App')
            
            flash('MFA enabled successfully! Your account is now more secure.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
            # Re-render with the same QR code
            provisioning_uri = get_totp_uri(pending_secret, current_user.email)
            qr_code = generate_qr_code(provisioning_uri)
            return render_template('enable_mfa.html', qr_code=qr_code, secret=pending_secret, step=2)
    
    # GET request: Generate new secret and QR code
    secret = generate_totp_secret()
    session['mfa_secret_pending'] = secret
    
    provisioning_uri = get_totp_uri(secret, current_user.email)
    qr_code = generate_qr_code(provisioning_uri)
    
    return render_template('enable_mfa.html', qr_code=qr_code, secret=secret, step=2)


@main_bp.route('/disable-mfa', methods=['POST'])
@login_required
def disable_mfa():
    """Disable MFA."""
    current_user.disable_mfa()
    db.session.commit()
    flash('MFA disabled.', 'info')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page."""
    return render_template('privacy_policy.html')
