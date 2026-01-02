"""SMS sending utility using Vonage Verify API for 2FA."""
import random
from flask import current_app

try:
    import vonage
    VONAGE_AVAILABLE = True
except ImportError:
    VONAGE_AVAILABLE = False
    print("⚠️  Vonage not installed - SMS MFA will be disabled")


def send_sms_code(phone_number, code=None):
    """
    Send SMS verification code using Vonage Verify API.
    
    Args:
        phone_number: E.164 format phone number (e.g., +14155551234)
        code: Not used - Vonage generates the code
    
    Returns:
        request_id: Vonage request ID for verification, or None if failed
    """
    if not VONAGE_AVAILABLE:
        print("❌ Vonage not available - cannot send SMS")
        return None
    
    try:
        api_key = current_app.config.get('VONAGE_API_KEY')
        api_secret = current_app.config.get('VONAGE_API_SECRET')
        brand_name = current_app.config.get('VONAGE_BRAND_NAME', 'BBA Services')
        
        if not api_key or not api_secret:
            print("❌ Missing Vonage credentials in config")
            return None
        
        client = vonage.Client(key=api_key, secret=api_secret)
        
        # Start verification request - Vonage manages the OTP code
        response = client.verify.start_verification(
            number=phone_number,
            brand=brand_name,
            code_length=6
        )
        
        if response.get('status') == '0':  # Success
            request_id = response.get('request_id')
            print(f"✅ SMS sent via Vonage to {phone_number}, request_id={request_id}")
            return request_id
        else:
            error = response.get('error_text', 'Unknown error')
            print(f"❌ Vonage error: {error}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to send SMS: {str(e)}")
        return None




def verify_sms_code(request_id, code):
    """
    Verify SMS code using Vonage Verify API.
    
    Args:
        request_id: Vonage request ID from send_sms_code()
        code: 6-digit code entered by user
    
    Returns:
        bool: True if code is valid, False otherwise
    """
    if not VONAGE_AVAILABLE:
        print("❌ Vonage not available - cannot verify SMS")
        return False
    
    try:
        api_key = current_app.config.get('VONAGE_API_KEY')
        api_secret = current_app.config.get('VONAGE_API_SECRET')
        
        if not api_key or not api_secret:
            print("❌ Missing Vonage credentials in config")
            return False
        
        client = vonage.Client(key=api_key, secret=api_secret)
        
        response = client.verify.check(request_id, code=code)
        
        if response.get('status') == '0':  # Success
            print(f"✅ Verification successful for request_id={request_id}")
            return True
        else:
            error = response.get('error_text', 'Invalid code')
            print(f"❌ Verification failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to verify code: {str(e)}")
        return False



def generate_code():
    """
    Generate a 6-digit verification code.
    
    Note: When using Vonage Verify API, code generation is handled by Vonage.
    This function is kept for backwards compatibility with email verification.
    """
    return str(random.randint(100000, 999999))
