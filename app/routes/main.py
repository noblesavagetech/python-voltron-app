"""Main application routes"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import db, BankAccount, Transaction
from app.utils.sms import send_sms_code
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
    """Enable SMS-based MFA."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if current_user.mfa_enabled:
        flash('MFA already enabled.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        sms_code = request.form.get('sms_code', '').strip()
        
        if sms_code:
            # Step 2: Verify code and enable MFA
            phone = request.form.get('phone_hidden')
            
            from app.utils.sms import verify_sms_code
            
            if current_user.vonage_request_id and verify_sms_code(current_user.vonage_request_id, sms_code):
                current_user.enable_mfa(phone)
                current_user.vonage_request_id = None
                db.session.commit()
                
                # Send confirmation email
                send_mfa_enabled_notification(current_user.email, phone)
                
                flash('SMS MFA enabled successfully!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid verification code.', 'danger')
                return render_template('enable_mfa.html', phone=phone, step=2)
        else:
            # Step 1: Send verification code
            phone = request.form.get('phone', '').strip()
            if not phone:
                flash('Phone number required.', 'danger')
                return render_template('enable_mfa.html')
            
            # Send SMS code via Vonage
            request_id = send_sms_code(phone, None)
            if request_id:
                current_user.vonage_request_id = request_id
                db.session.commit()
                flash('Verification code sent to your phone.', 'success')
                return render_template('enable_mfa.html', phone=phone, step=2)
            else:
                flash('Failed to send SMS.', 'danger')
                return render_template('enable_mfa.html')
    
    return render_template('enable_mfa.html')


@main_bp.route('/disable-mfa', methods=['POST'])
@login_required
def disable_mfa():
    """Disable MFA."""
    current_user.disable_mfa()
    db.session.commit()
    flash('MFA disabled.', 'info')
    return redirect(url_for('main.dashboard'))
