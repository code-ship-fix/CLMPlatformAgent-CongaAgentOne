@echo off
REM Conga CLM AI Agent - Windows Launcher

title Conga CLM AI Agent

echo.
echo ========================================
echo    Conga CLM AI Agent - Web Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Run the launcher
python run.py

pause