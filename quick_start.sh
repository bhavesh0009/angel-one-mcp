#!/bin/bash

# Angel One MCP Trading Assistant - Quick Start Script
# This script helps you set up everything needed to run the trading assistant

echo "🚀 Angel One MCP Trading Assistant - Quick Start"
echo "=================================================="

# Check if Python is installed (try python3 first, then python)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo "❌ Python 3 is required, but found: $PYTHON_VERSION"
        echo "Please install Python 3.10+ and try again."
        exit 1
    fi
else
    echo "❌ Python is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check if pip is installed
if ! command -v $PIP_CMD &> /dev/null; then
    echo "❌ $PIP_CMD is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ $PIP_CMD found"

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "📂 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies in virtual environment..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo "✅ Dependencies installed successfully!"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from example template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example!"
    elif [ -f "config_template.txt" ]; then
        cp config_template.txt .env
        echo "✅ .env file created from config_template.txt!"
    else
        echo "❌ Template files not found. Creating basic .env file..."
        cat > .env << 'EOF'
# Angel One API Configuration
ANGEL_ONE_API_KEY=your_api_key_here
ANGEL_ONE_CLIENT_CODE=your_client_code_here
ANGEL_ONE_PASSWORD=your_4_digit_pin_here
ANGEL_ONE_TOTP_SECRET=your_totp_secret_here

# Google Gemini API Configuration  
GEMINI_API_KEY=your_gemini_api_key_here
EOF
        echo "✅ Basic .env file created!"
    fi
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your actual credentials:"
    echo "   1. Angel One API key, client code, 4-digit PIN, and TOTP secret"
    echo "   2. Google Gemini API key"
    echo ""
    echo "📋 To get your credentials:"
    echo "   • Angel One API: https://smartapi.angelone.in/"
    echo "   • Google Gemini API: https://aistudio.google.com/app/apikey"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🧪 Running setup test..."
$PYTHON_CMD test_setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Edit the .env file with your actual SECRET credentials"
echo "   2. Optionally edit config.yaml for model settings and trading limits"
echo "   3. Run the test again: $PYTHON_CMD test_setup.py"
echo "   4. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "   5. Start the trading assistant: $PYTHON_CMD angel_one_mcp_client.py angel_one_mcp_server.py"
echo ""
echo "📚 For detailed instructions, see README.md"
echo ""
echo "⚠️  Safety reminder: Always start with DRY_RUN_MODE=true for testing!" 