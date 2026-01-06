"""Financial dashboard API routes - Data endpoints"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta, date
from app.models import db, BankAccount, Transaction

financials_api_bp = Blueprint('financials_api', __name__, url_prefix='/api/financials')


@financials_api_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """Get complete financial overview data"""
    # Get accounts
    bank_accounts = BankAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Calculate totals
    total_balance = sum(acc.current_balance or 0 for acc in bank_accounts)
    total_available = sum(acc.available_balance or 0 for acc in bank_accounts)
    
    # Get transactions for last 30 days
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    recent_transactions = Transaction.query.join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).order_by(Transaction.date.desc()).limit(10).all()
    
    # Calculate income and expenses
    cash_flow = db.session.query(
        func.sum(func.case(
            (Transaction.amount < 0, func.abs(Transaction.amount)),
            else_=0
        )).label('income'),
        func.sum(func.case(
            (Transaction.amount > 0, Transaction.amount),
            else_=0
        )).label('expenses')
    ).join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).first()
    
    income = float(cash_flow.income or 0)
    expenses = float(cash_flow.expenses or 0)
    
    # Spending by category
    spending_by_category = db.session.query(
        Transaction.primary_category,
        func.sum(Transaction.amount).label('total')
    ).join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= thirty_days_ago,
        Transaction.amount > 0
    ).group_by(Transaction.primary_category).all()
    
    return jsonify({
        'net_worth': {
            'net_worth': total_balance,
            'total_assets': total_available,
            'total_liabilities': 0,
            'changes': {
                'monthly': {'amount': 0, 'percentage': 0}
            }
        },
        'cash_flow': {
            'total_income': income,
            'total_expenses': expenses,
            'net_cash_flow': income - expenses,
            'savings_rate': (income - expenses) / income * 100 if income > 0 else 0,
            'insights': {
                'recommendations': [
                    f"You've spent ${expenses:.2f} in the last 30 days",
                    f"Your savings rate is {((income - expenses) / income * 100 if income > 0 else 0):.1f}%"
                ]
            }
        },
        'portfolio': {
            'total_value': 0,
            'total_gain': 0
        },
        'recent_transactions': [{
            'id': tx.id,
            'name': tx.name,
            'merchant_name': tx.merchant_name,
            'amount': float(tx.amount),
            'date': tx.date.isoformat(),
            'category': tx.primary_category
        } for tx in recent_transactions],
        'spending_by_category': [{
            'category': cat or 'Uncategorized',
            'amount': float(total)
        } for cat, total in spending_by_category]
    }), 200


@financials_api_bp.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get all accounts with balances"""
    accounts = BankAccount.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    accounts_data = [{
        'id': acc.id,
        'name': acc.account_name,
        'institution': acc.institution_name,
        'type': acc.account_type,
        'subtype': acc.account_subtype,
        'mask': acc.mask,
        'balance': float(acc.current_balance or 0),
        'available': float(acc.available_balance or 0)
    } for acc in accounts]
    
    total_assets = sum(acc.current_balance or 0 for acc in accounts)
    
    return jsonify({
        'accounts': accounts_data,
        'totals': {
            'total_assets': total_assets,
            'total_liabilities': 0,
            'net_worth': total_assets,
            'checking': sum(acc.current_balance or 0 for acc in accounts if acc.account_subtype == 'checking'),
            'savings': sum(acc.current_balance or 0 for acc in accounts if acc.account_subtype == 'savings'),
            'credit': 0,
            'investment': 0
        }
    }), 200


@financials_api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get transactions with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Filters
    account_id = request.args.get('account_id')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    query = Transaction.query.join(BankAccount).filter(
        BankAccount.user_id == current_user.id
    )
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    
    if category:
        query = query.filter(Transaction.primary_category == category)
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(Transaction.date >= start)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Transaction.date <= end)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Transaction.name.ilike(search_term),
                Transaction.merchant_name.ilike(search_term)
            )
        )
    
    query = query.order_by(Transaction.date.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'transactions': [{
            'id': tx.id,
            'name': tx.name,
            'merchant_name': tx.merchant_name,
            'amount': float(tx.amount),
            'date': tx.date.isoformat(),
            'category': tx.primary_category,
            'detailed_category': tx.detailed_category,
            'account_id': tx.account_id
        } for tx in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@financials_api_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """Get list of transaction categories with spending totals"""
    today = date.today()
    month_start = today.replace(day=1)
    
    categories = db.session.query(
        Transaction.primary_category,
        func.sum(Transaction.amount).label('total')
    ).join(BankAccount).filter(
        BankAccount.user_id == current_user.id,
        Transaction.date >= month_start,
        Transaction.amount > 0
    ).group_by(
        Transaction.primary_category
    ).order_by(
        db.desc('total')
    ).all()
    
    return jsonify({
        'categories': [
            {'name': c[0] or 'UNCATEGORIZED', 'total': float(c[1] or 0)}
            for c in categories
        ]
    }), 200
