"""TOTP (Time-based One-Time Password) MFA utility.

Supports Google Authenticator, Microsoft Authenticator, Authy, and 1Password.
Implements RFC 6238 standard for maximum compatibility.
"""
import pyotp
import qrcode
import io
from base64 import b64encode


def generate_totp_secret():
    """
    Generate a random base32 secret for TOTP.
    
    Returns:
        str: A 32-character base32 encoded secret
    """
    return pyotp.random_base32()


def get_totp_uri(secret, email, issuer='BBA Services'):
    """
    Generate the provisioning URI for authenticator apps.
    
    Args:
        secret: The TOTP secret key
        email: User's email (shown in authenticator app)
        issuer: Name of the service (shown in authenticator app)
    
    Returns:
        str: otpauth:// URI that authenticator apps understand
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code(provisioning_uri):
    """
    Generate a QR code image as base64 string.
    
    Args:
        provisioning_uri: The otpauth:// URI
    
    Returns:
        str: Base64 encoded PNG image
    """
    img = qrcode.make(provisioning_uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return b64encode(buffered.getvalue()).decode('utf-8')


def verify_totp_code(secret, code):
    """
    Verify a TOTP code against a secret.
    
    Args:
        secret: The user's TOTP secret
        code: The 6-digit code from the authenticator app
    
    Returns:
        bool: True if the code is valid, False otherwise
    """
    if not secret or not code:
        return False
    
    # Clean up the code (remove spaces)
    code = code.replace(' ', '').replace('-', '')
    
    try:
        totp = pyotp.TOTP(secret)
        # valid_window=1 allows for 30 seconds of clock skew
        return totp.verify(code, valid_window=1)
    except Exception as e:
        print(f"❌ TOTP verification error: {str(e)}")
        return False


def get_current_totp(secret):
    """
    Get the current TOTP code (for debugging/testing only).
    
    Args:
        secret: The TOTP secret
    
    Returns:
        str: Current 6-digit code
    """
    totp = pyotp.TOTP(secret)
    return totp.now()
