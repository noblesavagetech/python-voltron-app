"""Database models"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with email verification and optional SMS MFA."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verified_at = db.Column(db.DateTime)
    
    # SMS MFA
    mfa_enabled = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    vonage_request_id = db.Column(db.String(100))  # Temp storage for Vonage verification
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    bank_accounts = db.relationship('BankAccount', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def verify_email(self):
        """Mark the user's email as verified."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_code = None
    
    def enable_mfa(self, phone_number):
        """Enable SMS-based MFA with phone number."""
        self.phone = phone_number
        self.mfa_enabled = True
    
    def disable_mfa(self):
        """Disable MFA."""
        self.mfa_enabled = False
        self.phone = None


class QuestionnaireResponse(db.Model):
    """Stores user responses to the health assessment questionnaire"""
    __tablename__ = 'questionnaire_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Response data
    answers = db.Column(db.JSON, nullable=False)  # Stores all question answers
    score = db.Column(db.Float)  # Financial health score (0-100)
    tier = db.Column(db.String(50))  # Developing, Stable, Optimized
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuestionnaireResponse user_id={self.user_id} score={self.score}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'answers': self.answers,
            'score': self.score,
            'tier': self.tier,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BankAccount(db.Model):
    """Bank account linked via Plaid"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Plaid identifiers
    plaid_item_id = db.Column(db.String(100), nullable=False)
    plaid_account_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    plaid_access_token = db.Column(db.String(200), nullable=False)
    
    # Account details
    institution_id = db.Column(db.String(50))
    institution_name = db.Column(db.String(100))
    account_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50))  # checking, savings, credit, etc.
    account_subtype = db.Column(db.String(50))
    mask = db.Column(db.String(10))  # Last 4 digits
    
    # Balances
    current_balance = db.Column(db.Float, default=0.0)
    available_balance = db.Column(db.Float, default=0.0)
    credit_limit = db.Column(db.Float)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_synced_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BankAccount {self.institution_name} - {self.mask}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'institution_name': self.institution_name,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'mask': self.mask,
            'current_balance': self.current_balance,
            'available_balance': self.available_balance,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None
        }


class Transaction(db.Model):
    """Financial transaction from Plaid"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    # Plaid identifiers
    plaid_transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Transaction details
    name = db.Column(db.String(200), nullable=False)
    merchant_name = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(10), default='USD')
    
    # Categorization
    category = db.Column(db.String(100))
    primary_category = db.Column(db.String(100))
    detailed_category = db.Column(db.String(100))
    
    # Date/time
    date = db.Column(db.Date, nullable=False, index=True)
    authorized_date = db.Column(db.Date)
    
    # Status
    pending = db.Column(db.Boolean, default=False)
    payment_channel = db.Column(db.String(50))  # online, in store, etc.
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.name} ${self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'merchant_name': self.merchant_name,
            'amount': self.amount,
            'currency_code': self.currency_code,
            'category': self.category,
            'date': self.date.isoformat() if self.date else None,
            'pending': self.pending,
            'payment_channel': self.payment_channel
        }
