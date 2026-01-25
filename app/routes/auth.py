"""Authentication routes"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from app.models import db, User
from app.utils.email import send_verification_email
from app.utils.totp import verify_totp_code
import random

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Simple signup with email verification."""
    if current_user.is_authenticated:
        if not current_user.is_verified:
            return redirect(url_for('auth.verify_email'))
        return redirect(url_for('questionnaire.take_assessment'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Basic validation
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('signup.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address.', 'danger')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        
        # Create user
        verification_code = str(random.randint(100000, 999999))
        user = User(email=email)
        user.set_password(password)
        user.verification_code = verification_code
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if send_verification_email(email, verification_code):
            flash('Account created! Check your email for verification code.', 'success')
            login_user(user)
            return redirect(url_for('auth.verify_email'))
        else:
            flash('Account created but email failed to send. Please contact support.', 'warning')
            return redirect(url_for('auth.login'))
    
    return render_template('signup.html')


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    """Verify email with code."""
    if current_user.is_verified:
        return redirect(url_for('questionnaire.take_assessment'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()
        
        if current_user.verification_code == code:
            current_user.verify_email()
            db.session.commit()
            flash('Email verified! Please complete the financial health assessment.', 'success')
            return redirect(url_for('questionnaire.take_assessment'))
        else:
            flash('Invalid verification code.', 'danger')
    
    return render_template('verify_email.html')


@auth_bp.route('/resend-verification')
@login_required
def resend_verification():
    """Resend email verification code."""
    if current_user.is_verified:
        flash('Email already verified.', 'info')
        return redirect(url_for('main.dashboard'))
    
    verification_code = str(random.randint(100000, 999999))
    current_user.verification_code = verification_code
    db.session.commit()
    
    if send_verification_email(current_user.email, verification_code):
        flash('Verification code resent.', 'success')
    else:
        flash('Failed to send email.', 'danger')
    
    return redirect(url_for('auth.verify_email'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login with optional TOTP MFA."""
    if current_user.is_authenticated:
        if not current_user.is_verified:
            return redirect(url_for('auth.verify_email'))
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        totp_code = request.form.get('totp_code', '').strip()
        
        if not email or not password:
            flash('Email and password required.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
        
        # Check MFA if enabled
        if user.mfa_enabled:
            if not totp_code:
                # Show TOTP input field
                flash('Please enter the code from your authenticator app.', 'info')
                return render_template('login.html', require_mfa=True, email=email)
            
            # Verify TOTP code
            if not verify_totp_code(user.mfa_secret, totp_code):
                flash('Invalid authentication code. Please try again.', 'danger')
                return render_template('login.html', require_mfa=True, email=email)
        
        login_user(user)
        
        if not user.is_verified:
            return redirect(url_for('auth.verify_email'))
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.index'))
