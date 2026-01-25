"""
Field-Level Encryption for Sensitive Data

Provides AES encryption for sensitive database columns like Plaid access tokens.
Uses Fernet (AES-128-CBC with HMAC) for authenticated encryption.

Generate a key with:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
import os
from cryptography.fernet import Fernet
from sqlalchemy import String, TypeDecorator


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column type that encrypts/decrypts data transparently.
    
    Usage:
        from app.utils.encryption import EncryptedString
        
        class MyModel(db.Model):
            sensitive_data = db.Column(EncryptedString(500), nullable=False)
    """
    impl = String
    cache_ok = True
    
    def __init__(self, length=255, *args, **kwargs):
        super().__init__(length, *args, **kwargs)
        self._key = None
    
    @property
    def key(self):
        """Lazy-load encryption key from environment"""
        if self._key is None:
            key = os.getenv('DATABASE_ENCRYPTION_KEY')
            if key:
                self._key = key.encode() if isinstance(key, str) else key
        return self._key
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is None:
            return None
        
        if not self.key:
            # No encryption key set - store as plaintext (dev mode)
            # In production, DATABASE_ENCRYPTION_KEY should always be set
            return value
        
        try:
            fernet = Fernet(self.key)
            encrypted = fernet.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"⚠️ Encryption failed: {e}")
            return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value when reading from database"""
        if value is None:
            return None
        
        if not self.key:
            # No encryption key - return as-is
            return value
        
        try:
            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(value.encode())
            return decrypted.decode()
        except Exception:
            # Value might not be encrypted (legacy data or dev mode)
            return value


def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()


# Convenience function to check if encryption is enabled
def is_encryption_enabled():
    """Check if database encryption is configured"""
    return os.getenv('DATABASE_ENCRYPTION_KEY') is not None
