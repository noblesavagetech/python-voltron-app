"""Email sending utility using Brevo (SendinBlue) for transactional emails."""
import sib_api_v3_sdk
from flask import current_app


def send_verification_email(user_email, verification_code):
    """
    Send email verification code using Brevo.
    
    Args:
        user_email (str): Recipient email address
        verification_code (str): 6-digit verification code
        
    Returns:
        bool: Success status
    """
    subject = "Verify Your Email - BBA Services"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">Welcome to BBA Services!</h2>
            <p>Thank you for signing up. Please verify your email address to complete your registration.</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 14px; color: #666;">Your verification code is:</p>
                <p style="font-size: 32px; font-weight: bold; color: #667eea; margin: 10px 0; letter-spacing: 5px;">{verification_code}</p>
            </p>
            <p style="color: #666; font-size: 14px;">This code will expire in 24 hours.</p>
            <p>After verifying your email, you'll complete a brief financial health assessment.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
                If you didn't sign up for BBA Services, please ignore this email.
            </p>
        </body>
    </html>
    """
    
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        sender = {
            "name": current_app.config['SENDER_NAME'],
            "email": current_app.config['SENDER_EMAIL']
        }
        
        to = [{"email": user_email}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ Verification email sent via Brevo to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email via Brevo: {str(e)}")
        return False


def send_mfa_enabled_notification(user_email, phone_number):
    """
    Notify user that MFA has been enabled.
    
    Args:
        user_email (str): Recipient email address
        phone_number (str): Phone number MFA was enabled for
        
    Returns:
        bool: Success status
    """
    subject = "SMS MFA Enabled - BBA Services"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">🔒 SMS MFA Enabled</h2>
            <p>Two-factor authentication has been successfully enabled for your account.</p>
            <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0; color: #155724;">
                    <strong>Protected Phone:</strong> {phone_number[-4:].rjust(len(phone_number), '*')}
                </p>
            </div>
            <p>From now on, you'll need to enter a code sent to your phone when logging in.</p>
            <p style="color: #666; font-size: 14px;">If you didn't enable MFA, please contact support immediately.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">BBA Services Security Team</p>
        </body>
    </html>
    """
    
    try:
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = current_app.config['BREVO_API_KEY']
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        sender = {
            "name": current_app.config['SENDER_NAME'],
            "email": current_app.config['SENDER_EMAIL']
        }
        
        to = [{"email": user_email}]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            html_content=html_content,
            sender=sender,
            subject=subject
        )
        
        api_instance.send_transac_email(send_smtp_email)
        print(f"✅ MFA notification email sent to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send MFA notification: {str(e)}")
        return False
