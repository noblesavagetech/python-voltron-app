"""Plaid integration service for bank account linking and transaction syncing"""
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from flask import current_app
from datetime import datetime, date
import logging

from app.models import db, BankAccount, Transaction

logger = logging.getLogger(__name__)


class PlaidService:
    """Service for Plaid API interactions"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of Plaid client"""
        if self._client is None:
            configuration = plaid.Configuration(
                host=self._get_plaid_host(),
                api_key={
                    'clientId': current_app.config['PLAID_CLIENT_ID'],
                    'secret': current_app.config['PLAID_SECRET'],
                }
            )
            api_client = plaid.ApiClient(configuration)
            self._client = plaid_api.PlaidApi(api_client)
        return self._client
    
    def _get_plaid_host(self):
        """Get Plaid host URL based on environment"""
        env = current_app.config['PLAID_ENV']
        hosts = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production
        }
        return hosts.get(env, plaid.Environment.Sandbox)
    
    def create_link_token(self, user):
        """
        Create a Link token for initializing Plaid Link
        
        Args:
            user: User object
            
        Returns:
            dict with 'success' and 'link_token' or 'error'
        """
        try:
            request = LinkTokenCreateRequest(
                products=[Products(p) for p in current_app.config['PLAID_PRODUCTS']],
                client_name=current_app.config['SENDER_NAME'],
                country_codes=[CountryCode(c) for c in current_app.config['PLAID_COUNTRY_CODES']],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(user.id)
                ),
                redirect_uri=current_app.config.get('PLAID_REDIRECT_URI')
            )
            
            response = self.client.link_token_create(request)
            return {
                'success': True,
                'link_token': response['link_token'],
                'expiration': response['expiration']
            }
        except plaid.ApiException as e:
            logger.error(f"Error creating link token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def exchange_public_token(self, public_token):
        """
        Exchange public token for access token
        
        Args:
            public_token: Public token from Plaid Link
            
        Returns:
            dict with 'success', 'access_token', 'item_id' or 'error'
        """
        try:
            request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            response = self.client.item_public_token_exchange(request)
            return {
                'success': True,
                'access_token': response['access_token'],
                'item_id': response['item_id']
            }
        except plaid.ApiException as e:
            logger.error(f"Error exchanging public token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_accounts(self, access_token):
        """
        Get account information from Plaid
        
        Args:
            access_token: Plaid access token
            
        Returns:
            dict with 'success' and 'accounts' list or 'error'
        """
        try:
            request = AccountsGetRequest(
                access_token=access_token
            )
            
            response = self.client.accounts_get(request)
            return {
                'success': True,
                'accounts': response['accounts'],
                'item': response['item']
            }
        except plaid.ApiException as e:
            logger.error(f"Error getting accounts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_transactions(self, access_token, cursor=None):
        """
        Sync transactions using Plaid Sync API
        
        Args:
            access_token: Plaid access token
            cursor: Optional cursor for incremental sync
            
        Returns:
            dict with 'success', transaction data, or 'error'
        """
        try:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )
            
            response = self.client.transactions_sync(request)
            return {
                'success': True,
                'added': response.get('added', []),
                'modified': response.get('modified', []),
                'removed': response.get('removed', []),
                'next_cursor': response['next_cursor'],
                'has_more': response['has_more']
            }
        except plaid.ApiException as e:
            logger.error(f"Error syncing transactions: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_accounts_for_user(self, user_id, access_token, item_id, accounts_data, institution_name):
        """
        Save bank accounts to database
        
        Args:
            user_id: User ID
            access_token: Plaid access token
            item_id: Plaid item ID
            accounts_data: List of account dicts from Plaid
            institution_name: Name of financial institution
            
        Returns:
            List of saved BankAccount objects
        """
        saved_accounts = []
        
        for account in accounts_data:
            # Check if account already exists
            existing = BankAccount.query.filter_by(
                plaid_account_id=account['account_id']
            ).first()
            
            if existing:
                # Update existing account
                existing.account_name = account['name']
                existing.account_type = str(account['type']) if account.get('type') else None
                existing.account_subtype = str(account['subtype']) if account.get('subtype') else None
                existing.mask = account['mask']
                existing.is_active = True
                
                # Update balances
                balances = account.get('balances', {})
                existing.current_balance = balances.get('current')
                existing.available_balance = balances.get('available')
                existing.credit_limit = balances.get('limit')
                existing.last_synced_at = datetime.utcnow()
                
                saved_accounts.append(existing)
            else:
                # Create new account
                balances = account.get('balances', {})
                new_account = BankAccount(
                    user_id=user_id,
                    plaid_item_id=item_id,
                    plaid_account_id=account['account_id'],
                    plaid_access_token=access_token,
                    institution_name=institution_name,
                    account_name=account['name'],
                    account_type=str(account['type']) if account.get('type') else None,
                    account_subtype=str(account['subtype']) if account.get('subtype') else None,
                    mask=account['mask'],
                    current_balance=balances.get('current'),
                    available_balance=balances.get('available'),
                    credit_limit=balances.get('limit'),
                    last_synced_at=datetime.utcnow()
                )
                db.session.add(new_account)
                saved_accounts.append(new_account)
        
        db.session.commit()
        return saved_accounts
    
    def sync_and_save_transactions(self, bank_account):
        """
        Sync and save transactions for a bank account
        
        Args:
            bank_account: BankAccount object
            
        Returns:
            dict with sync statistics
        """
        cursor = None  # For full sync; could store cursor for incremental
        has_more = True
        added_count = 0
        modified_count = 0
        removed_count = 0
        
        while has_more:
            result = self.sync_transactions(bank_account.plaid_access_token, cursor)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            # Process added transactions
            for tx in result['added']:
                self._save_transaction(bank_account.id, tx)
                added_count += 1
            
            # Process modified transactions
            for tx in result['modified']:
                self._update_transaction(tx)
                modified_count += 1
            
            # Process removed transactions
            for tx_id in result['removed']:
                self._remove_transaction(tx_id)
                removed_count += 1
            
            cursor = result['next_cursor']
            has_more = result['has_more']
        
        # Update last synced timestamp
        bank_account.last_synced_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'added': added_count,
            'modified': modified_count,
            'removed': removed_count
        }
    
    def _save_transaction(self, account_id, tx_data):
        """Save a new transaction to database"""
        # Check if transaction already exists
        existing = Transaction.query.filter_by(
            plaid_transaction_id=tx_data['transaction_id']
        ).first()
        
        if existing:
            return existing
        
        # Parse categories
        categories = tx_data.get('category', [])
        primary_cat = categories[0] if len(categories) > 0 else None
        detailed_cat = categories[1] if len(categories) > 1 else None
        
        # Parse date
        tx_date = tx_data.get('date')
        if isinstance(tx_date, str):
            tx_date = datetime.strptime(tx_date, '%Y-%m-%d').date()
        
        transaction = Transaction(
            account_id=account_id,
            plaid_transaction_id=tx_data['transaction_id'],
            name=tx_data['name'],
            merchant_name=tx_data.get('merchant_name'),
            amount=tx_data['amount'],
            currency_code=tx_data.get('iso_currency_code', 'USD'),
            category=', '.join(categories) if categories else None,
            primary_category=primary_cat,
            detailed_category=detailed_cat,
            date=tx_date,
            pending=tx_data.get('pending', False),
            payment_channel=tx_data.get('payment_channel')
        )
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def _update_transaction(self, tx_data):
        """Update an existing transaction"""
        transaction = Transaction.query.filter_by(
            plaid_transaction_id=tx_data['transaction_id']
        ).first()
        
        if transaction:
            transaction.name = tx_data['name']
            transaction.merchant_name = tx_data.get('merchant_name')
            transaction.amount = tx_data['amount']
            transaction.pending = tx_data.get('pending', False)
            db.session.commit()
    
    def _remove_transaction(self, transaction_id):
        """Remove a transaction (mark as inactive or delete)"""
        transaction = Transaction.query.filter_by(
            plaid_transaction_id=transaction_id
        ).first()
        
        if transaction:
            db.session.delete(transaction)
            db.session.commit()


# Singleton instance
plaid_service = PlaidService()
