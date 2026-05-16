@echo off
echo ==========================================
echo   Conga CLM AI Agent - Windows Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
python --version

echo.
echo Checking if pip is available...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

echo ✓ pip found

echo.
echo Installing required packages...
pip install requests python-dotenv anthropic flask flask-socketio

if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages!
    echo.
    echo Try running this command manually:
    echo pip install requests python-dotenv anthropic flask flask-socketio
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo.
echo Starting Conga CLM AI Agent...
echo 🌐 Web Interface: http://localhost:8080
echo 💡 Press Ctrl+C to stop the server
echo.

python web_app.py

echo.
echo Application stopped.
pause