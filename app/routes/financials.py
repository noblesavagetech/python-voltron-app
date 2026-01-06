"""Financial dashboard routes - Advanced analytics views"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

financials_bp = Blueprint('financials', __name__, url_prefix='/financials')


@financials_bp.route('/overview')
@login_required
def overview():
    """Financial Overview Dashboard - Main analytics page"""
    if not current_user.is_verified:
        from flask import redirect, url_for
        return redirect(url_for('auth.verify_email'))
    return render_template('financials/overview.html')


@financials_bp.route('/accounts')
@login_required
def accounts():
    """Accounts Management Dashboard"""
    if not current_user.is_verified:
        from flask import redirect, url_for
        return redirect(url_for('auth.verify_email'))
    return render_template('financials/accounts.html')


@financials_bp.route('/transactions')
@login_required
def transactions():
    """Transactions Dashboard"""
    if not current_user.is_verified:
        from flask import redirect, url_for
        return redirect(url_for('auth.verify_email'))
    return render_template('financials/transactions.html')


@financials_bp.route('/investments')
@login_required
def investments():
    """Investments & Portfolio Dashboard"""
    if not current_user.is_verified:
        from flask import redirect, url_for
        return redirect(url_for('auth.verify_email'))
    return render_template('financials/investments.html')


@financials_bp.route('/analytics')
@login_required
def analytics():
    """Advanced Analytics Dashboard"""
    if not current_user.is_verified:
        from flask import redirect, url_for
        return redirect(url_for('auth.verify_email'))
    return render_template('financials/analytics.html')
