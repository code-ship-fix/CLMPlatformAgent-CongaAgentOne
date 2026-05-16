# 🚀 Conga CLM AI Agent - Deployment Guide

## Quick Start (Any Computer)

### Option 1: One-Click Launch (Recommended)

#### Windows:
1. Double-click `start.bat`
2. The script will automatically install dependencies and start the server

#### macOS/Linux:
1. Double-click `start.sh` or run in terminal: `./start.sh`
2. The script will automatically install dependencies and start the server

#### Manual Method:
```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python run.py
```

### Option 2: Development Mode
```bash
# Start with Flask development server
python web_app.py
```

## 🌐 Access the Application

Once started, you'll see output like this:
```
🚀 Starting Conga CLM AI Agent Web Server...
🏠 Local access: http://localhost:5000
🌐 Network access: http://192.168.1.100:5000
📱 Mobile access: http://192.168.1.100:5000 (same network)
```

### Access Options:
- **Local only**: `http://localhost:5000`
- **Same WiFi network**: Use the network IP shown
- **Mobile/tablet**: Use the network IP on same WiFi

## 📋 Prerequisites

### Required:
- Python 3.8 or higher
- Internet connection (for AI and Conga APIs)
- Web browser (Chrome, Firefox, Safari, Edge)

### API Credentials:
Edit `.env` file with your actual credentials:
```
CONGA_CLIENT_ID=your-actual-client-id
CONGA_CLIENT_SECRET=your-actual-client-secret
ANTHROPIC_API_KEY=your-actual-anthropic-key
```

## 📱 Portable Installation

### For Home/Work Computers:

#### Method 1: Copy Entire Folder
1. Copy the entire project folder to target computer
2. Run `start.bat` (Windows) or `start.sh` (Mac/Linux)
3. Done! No additional setup needed.

#### Method 2: USB Stick Installation
1. Copy project folder to USB stick
2. On target computer, copy folder to local drive
3. Run the launcher script
4. Dependencies will auto-install on first run

#### Method 3: Cloud Sync
1. Put project folder in Dropbox/Google Drive/OneDrive
2. Sync to target computer
3. Run launcher script

### Network Deployment (Advanced)

#### Home Server Setup:
1. Install on a computer that stays on (home server/NUC/Raspberry Pi)
2. Configure your router to port forward 5000 → server IP
3. Access from anywhere: `http://your-public-ip:5000`

#### Local Network Only:
- Perfect for office/home network use
- All devices on same WiFi can access
- More secure (no internet exposure)

## 🔧 Configuration

### Environment Variables (.env):
```bash
# Required - Conga CLM credentials
CONGA_CLIENT_ID=your-client-id
CONGA_CLIENT_SECRET=your-client-secret
CONGA_AUTH_URL=https://login-rlspreview.congacloud.com/api/v1/auth/connect/token
CONGA_BASE_URL=https://preview-rls09.congacloud.com

# Required - Anthropic API key
ANTHROPIC_API_KEY=your-anthropic-key

# Optional - Flask settings
FLASK_SECRET_KEY=your-secret-key-for-sessions
```

### System Prompt Customization:
Edit `prompts/system_prompt.txt` to customize:
- Business rules
- Response style
- Available contract types
- Validation requirements

### Port Configuration:
Change port in `web_app.py` if 5000 is in use:
```python
port = 8080  # Change this line
```

## 🐛 Troubleshooting

### Common Issues:

#### "Port 5000 already in use"
```bash
# Find what's using port 5000
netstat -an | grep 5000

# Kill the process or change port in web_app.py
```

#### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or use the launcher script which auto-installs
python run.py
```

#### "Connection failed" errors
1. Check internet connection
2. Verify API credentials in `.env`
3. Check firewall settings

#### Can't access from other devices
1. Ensure server shows network IP
2. Check if firewall is blocking port 5000
3. Confirm devices are on same WiFi network

### Firewall Configuration:

#### Windows:
1. Windows Defender → Allow an app
2. Allow Python through firewall for port 5000

#### macOS:
1. System Preferences → Security & Privacy → Firewall
2. Allow incoming connections for Python

#### Linux:
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --add-port=5000/tcp --permanent
```

## 📊 Performance & Scaling

### Resource Usage:
- **RAM**: ~100-200MB per active session
- **CPU**: Low (spikes during AI processing)
- **Network**: Depends on API usage

### Concurrent Users:
- **Small team (1-5 users)**: Any modern computer
- **Medium team (5-20 users)**: Dedicated server recommended
- **Large team (20+ users)**: Consider cloud deployment

### Production Deployment:

#### Using Gunicorn (Linux/macOS):
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 web_app:app
```

#### Using Docker:
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "web_app.py"]
```

## 🔒 Security Considerations

### For Local Network Use:
- Default configuration is secure for local network
- Credentials stored in `.env` (not committed to git)
- Sessions are isolated per user

### For Internet Exposure:
- Add HTTPS (SSL certificate)
- Implement authentication
- Use environment variables for secrets
- Regular security updates

### Best Practices:
1. Keep `.env` file secure and private
2. Don't share API credentials
3. Regular backup of conversation data
4. Monitor API usage/costs

## 📦 Packaging for Distribution

### Create Portable Package:
1. Copy entire project folder
2. Include `start.bat` and `start.sh`
3. Include `requirements.txt`
4. Create README with setup instructions
5. Zip and share

### What Recipients Need:
1. Python 3.8+ installed
2. Internet connection
3. Their own API credentials
4. Basic computer skills to edit `.env` file

## 🔄 Updates & Maintenance

### Updating the Agent:
1. Replace project files (keep your `.env`)
2. Run `pip install -r requirements.txt` if new deps
3. Restart server

### Backup Important Files:
- `.env` (your credentials)
- `prompts/system_prompt.txt` (customizations)
- Any custom modifications

### Monitoring:
- Check `/health` endpoint for system status
- Monitor API usage in respective dashboards
- Check server logs for errors

---

## 🎉 You're Ready!

Your Conga CLM AI Agent is now portable and ready to run anywhere. The web interface provides a professional, mobile-friendly chat experience for contract management.

**Happy contracting! 🚀**