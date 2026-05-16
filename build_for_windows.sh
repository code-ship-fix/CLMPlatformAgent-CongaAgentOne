#!/bin/bash

echo "=========================================="
echo "  Building Conga Agent for Windows"
echo "=========================================="
echo

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   It's recommended to run this in a virtual environment"
    echo
fi

# Install PyInstaller if not already installed
echo "📦 Installing PyInstaller..."
pip install pyinstaller>=6.0.0

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/
rm -rf src/__pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Build the executable
echo "🔨 Building Windows executable..."
pyinstaller --clean build_windows.spec

# Check if build was successful
if [ -d "dist/CongaAgent" ]; then
    echo "✅ Build successful!"
    echo

    # Copy additional files to the distribution
    echo "📋 Copying additional files..."
    cp .env.example dist/CongaAgent/
    cp start_windows.bat dist/CongaAgent/
    cp README.md dist/CongaAgent/ 2>/dev/null || echo "README.md not found, skipping..."

    # Create a deployment package
    echo "📦 Creating deployment package..."
    cd dist

    # Create deployment instructions
    cat > CongaAgent/DEPLOYMENT_INSTRUCTIONS.txt << 'EOF'
CONGA CLM AI AGENT - WINDOWS DEPLOYMENT INSTRUCTIONS
===================================================

📁 WHAT'S IN THIS PACKAGE:
  • CongaAgent.exe        - Main application executable
  • start_windows.bat     - Easy startup script (RECOMMENDED)
  • .env.example          - Environment variables template
  • web/                  - Web interface files
  • _internal/            - Application dependencies (DO NOT MODIFY)

🚀 QUICK START:
  1. Copy this entire CongaAgent folder to your Windows PC
  2. Create a .env file with your credentials (see step 3)
  3. Double-click start_windows.bat to run the application
  4. Open http://localhost:8080 in your browser

⚙️  CONFIGURATION (.env file):
  Copy .env.example to .env and fill in your values:

  CONGA_CLIENT_ID=your-conga-client-id
  CONGA_CLIENT_SECRET=your-conga-client-secret
  CONGA_AUTH_URL=https://your-org.congacloud.com/oauth/token
  CONGA_BASE_URL=https://your-org.congacloud.com
  ANTHROPIC_API_KEY=your-anthropic-api-key
  FLASK_SECRET_KEY=your-random-secret-key

💡 USAGE TIPS:
  • Use start_windows.bat for easy launching
  • The application runs on http://localhost:8080
  • Press Ctrl+C in the command window to stop
  • All files in this folder are needed - don't delete anything

🔧 TROUBLESHOOTING:
  • If .env file is missing, the app will show an error
  • If port 8080 is busy, the app will try other ports
  • Check Windows Firewall if you can't access the web interface
  • Antivirus might flag the .exe - add it to exclusions if needed

📧 SUPPORT:
  If you encounter issues, check the console output for error messages.
EOF

    # Create a ZIP file for easy distribution
    if command -v zip &> /dev/null; then
        echo "🗜️  Creating ZIP package..."
        zip -r CongaAgent_Windows_Portable.zip CongaAgent/
        echo "✅ Created: dist/CongaAgent_Windows_Portable.zip"
    else
        echo "ℹ️  ZIP not available - you can manually compress the CongaAgent folder"
    fi

    cd ..

    echo
    echo "🎉 Windows deployment package ready!"
    echo
    echo "📁 Location: dist/CongaAgent/"
    echo "📋 Instructions: dist/CongaAgent/DEPLOYMENT_INSTRUCTIONS.txt"
    echo
    echo "TO DEPLOY ON WINDOWS:"
    echo "1. Copy the entire 'dist/CongaAgent' folder to your Windows PC"
    echo "2. Create .env file with your credentials"
    echo "3. Double-click start_windows.bat"
    echo "4. Open http://localhost:8080 in browser"
    echo

else
    echo "❌ Build failed! Check the errors above."
    exit 1
fi