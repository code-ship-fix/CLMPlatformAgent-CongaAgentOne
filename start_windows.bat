@echo off
echo ==========================================
echo   Conga CLM AI Agent - Windows Launcher
echo ==========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please create a .env file with your credentials:
    echo   CONGA_CLIENT_ID=your-client-id
    echo   CONGA_CLIENT_SECRET=your-client-secret
    echo   CONGA_AUTH_URL=your-auth-url
    echo   CONGA_BASE_URL=your-base-url
    echo   ANTHROPIC_API_KEY=your-anthropic-key
    echo   FLASK_SECRET_KEY=your-secret-key
    echo.
    echo You can copy .env.example to .env and fill in your values.
    echo.
    pause
    exit /b 1
)

echo Checking environment file...
echo ✓ Found .env file

echo.
echo Starting Conga CLM AI Agent...
echo 🌐 Web Interface: http://localhost:8080
echo 💡 Press Ctrl+C to stop the server
echo.

REM Start the application
CongaAgent.exe

echo.
echo Application stopped.
pause