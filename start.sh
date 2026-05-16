#!/bin/bash
# Conga CLM AI Agent - Unix/Linux/macOS Launcher

echo "========================================"
echo "   Conga CLM AI Agent - Web Launcher"
echo "========================================"
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Error: Python is not installed or not in PATH"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try running manually:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        echo "   python web_app.py"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if packages are installed
if ! python -c "import flask, flask_socketio, anthropic" &> /dev/null; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install packages"
        echo "💡 Try running manually:"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Environment ready!"
echo "🚀 Starting Conga CLM AI Agent Web Server..."

# Run the web application
python web_app.py