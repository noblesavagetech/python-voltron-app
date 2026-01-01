"""Plaid integration routes for bank linking and transaction management"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.models import db, BankAccount
from app.utils.plaid_service import plaid_service

plaid_bp = Blueprint('plaid', __name__)


@plaid_bp.route('/link')
@login_required
def link():
    """Plaid Link page - initiate bank account connection"""
    # Create link token
    result = plaid_service.create_link_token(current_user)
    
    if not result['success']:
        flash('Unable to connect to Plaid. Please try again later.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('plaid/link.html', link_token=result['link_token'])


@plaid_bp.route('/callback', methods=['POST'])
@login_required
def callback():
    """Handle Plaid Link callback after successful connection"""
    data = request.get_json()
    public_token = data.get('public_token')
    metadata = data.get('metadata', {})
    
    if not public_token:
        return jsonify({'success': False, 'error': 'No public token provided'}), 400
    
    # Exchange public token for access token
    exchange_result = plaid_service.exchange_public_token(public_token)
    
    if not exchange_result['success']:
        return jsonify({'success': False, 'error': 'Failed to exchange token'}), 500
    
    access_token = exchange_result['access_token']
    item_id = exchange_result['item_id']
    
    # Get accounts
    accounts_result = plaid_service.get_accounts(access_token)
    
    if not accounts_result['success']:
        return jsonify({'success': False, 'error': 'Failed to retrieve accounts'}), 500
    
    # Save accounts to database
    institution_name = metadata.get('institution', {}).get('name', 'Unknown Bank')
    saved_accounts = plaid_service.save_accounts_for_user(
        current_user.id,
        access_token,
        item_id,
        accounts_result['accounts'],
        institution_name
    )
    
    # Sync initial transactions for each account
    for account in saved_accounts:
        plaid_service.sync_and_save_transactions(account)
    
    return jsonify({
        'success': True,
        'accounts_linked': len(saved_accounts)
    })


@plaid_bp.route('/accounts')
@login_required
def accounts():
    """View all linked bank accounts"""
    accounts = BankAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    return render_template('plaid/accounts.html', accounts=accounts)


@plaid_bp.route('/sync/<int:account_id>', methods=['POST'])
@login_required
def sync_account(account_id):
    """Manually sync transactions for a specific account"""
    account = BankAccount.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first()
    
    if not account:
        flash('Account not found.', 'danger')
        return redirect(url_for('plaid.accounts'))
    
    result = plaid_service.sync_and_save_transactions(account)
    
    if result['success']:
        flash(f"Synced {result['added']} new transactions.", 'success')
    else:
        flash('Failed to sync transactions.', 'danger')
    
    return redirect(url_for('plaid.accounts'))


@plaid_bp.route('/sync-all', methods=['POST'])
@login_required
def sync_all():
    """Sync all active accounts"""
    accounts = BankAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    total_added = 0
    for account in accounts:
        result = plaid_service.sync_and_save_transactions(account)
        if result['success']:
            total_added += result['added']
    
    flash(f"Synced {total_added} new transactions across all accounts.", 'success')
    return redirect(url_for('main.dashboard'))


@plaid_bp.route('/remove/<int:account_id>', methods=['POST'])
@login_required
def remove_account(account_id):
    """Remove/deactivate a bank account"""
    account = BankAccount.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first()
    
    if not account:
        flash('Account not found.', 'danger')
        return redirect(url_for('plaid.accounts'))
    
    account.is_active = False
    db.session.commit()
    
    flash('Account removed successfully.', 'success')
    return redirect(url_for('plaid.accounts'))
