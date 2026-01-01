"""
BBA Services - Flask App with Email Verification, MFA, and Health Assessment
Main application entry point
"""
from app import create_app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
