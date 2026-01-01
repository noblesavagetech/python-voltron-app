#!/bin/bash

echo "========================================="
echo "  BBA Services - Setup Script"
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys:"
    echo "   - BREVO_API_KEY (required for email)"
    echo "   - SENDER_EMAIL (required for email)"
    echo "   - VONAGE_API_KEY (optional for MFA)"
    echo "   - VONAGE_API_SECRET (optional for MFA)"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "========================================="
echo "  ✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Run: python app.py"
echo "  3. Visit: http://localhost:5000"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""
