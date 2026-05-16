# Windows Deployment Instructions

## Quick Fix for Your Current Issue

The `CongaAgent.exe` file was built for Mac and won't work on Windows. Here's the solution:

### Option 1: Python Source Code (RECOMMENDED - EASIEST)

1. **Copy these files to your Windows laptop:**
   ```
   CongaAgentOne/
   ├── web_app.py
   ├── src/ (entire folder)
   ├── web/ (entire folder)
   ├── prompts/ (entire folder)
   ├── .env.example
   ├── deploy_windows.bat  (NEW FILE)
   └── requirements.txt
   ```

2. **Install Python on Windows:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.8 or higher
   - **IMPORTANT**: Check "Add Python to PATH" during installation

3. **Setup and Run:**
   - Copy `.env.example` to `.env` and fill in your credentials
   - Double-click `deploy_windows.bat`
   - Open http://localhost:8080 in browser

### Option 2: Manual Python Setup

If the batch file doesn't work:

1. **Install Python** (same as above)

2. **Open Command Prompt in your project folder:**
   - Hold Shift + Right-click in the folder
   - Choose "Open PowerShell window here" or "Open command window here"

3. **Install packages:**
   ```cmd
   pip install requests python-dotenv anthropic flask flask-socketio
   ```

4. **Run the application:**
   ```cmd
   python web_app.py
   ```

5. **Open browser:** http://localhost:8080

## Files You Need on Windows

Copy these exact files/folders from your Mac:

### Required Files:
- `web_app.py` - Main application
- `src/` - All Python source code
- `web/` - Web interface (HTML, CSS, JS)
- `prompts/` - AI prompts
- `.env.example` - Configuration template
- `deploy_windows.bat` - Windows setup script
- `requirements.txt` - Python dependencies

### Configuration:
1. Copy `.env.example` to `.env`
2. Edit `.env` with your actual credentials:
   ```
   CONGA_CLIENT_ID=your-real-client-id
   CONGA_CLIENT_SECRET=your-real-client-secret
   CONGA_AUTH_URL=https://login-rlspreview.congacloud.com/api/v1/auth/connect/token
   CONGA_BASE_URL=https://preview-rls09.congacloud.com
   ANTHROPIC_API_KEY=your-real-anthropic-key
   FLASK_SECRET_KEY=any-random-string-here
   ```

## Troubleshooting

### "Python is not recognized"
- Reinstall Python with "Add to PATH" checked
- Or manually add Python to PATH in Windows

### "pip is not recognized"
- Python installation issue - reinstall Python
- Or use: `python -m pip install ...`

### Port 8080 busy
- The app will automatically try 8081, 8082, etc.
- Or manually specify: `python web_app.py --port 8081`

### Firewall/Antivirus
- Allow Python and the application through Windows Firewall
- Add project folder to antivirus exclusions

## Why This Happened

PyInstaller created a Mac executable (.exe format but ARM64 architecture) that doesn't work on Windows. The Python source code approach is actually better because:

- ✅ Works on any operating system
- ✅ Easier to update and maintain
- ✅ No compatibility issues
- ✅ Smaller file size
- ✅ More transparent (you can see the code)

This is the standard way to deploy Python web applications!