# Conga CLM AI Agent - Cloud Deployment

## Quick Setup on Replit:

1. **Upload Files:**
   - Drag all files from this folder to Replit

2. **Set Environment Variables:**
   - Click "Tools" → "Environment Variables"
   - Add your credentials:
     ```
     CONGA_CLIENT_ID=your-client-id
     CONGA_CLIENT_SECRET=your-client-secret
     CONGA_AUTH_URL=https://login-rlspreview.congacloud.com/api/v1/auth/connect/token
     CONGA_BASE_URL=https://preview-rls09.congacloud.com
     ANTHROPIC_API_KEY=your-anthropic-key
     FLASK_SECRET_KEY=mysecretkey123
     ```

3. **Install Dependencies:**
   - Replit will auto-install from requirements.txt
   - Or click "Packages" and search for: flask, flask-socketio, requests, python-dotenv, anthropic

4. **Run:**
   - Click the "Run" button
   - Your app will be available at the provided URL

## Other Cloud Platforms:

### Heroku:
- Add `Procfile`: `web: python web_app.py`
- Set environment variables in dashboard
- Deploy via Git

### PythonAnywhere:
- Upload files via file browser
- Set environment variables
- Create web app pointing to web_app.py

### Glitch:
- Import from GitHub
- Set environment variables in .env
- App runs automatically

## Security Note:
Never commit .env file with real credentials to public repositories!
