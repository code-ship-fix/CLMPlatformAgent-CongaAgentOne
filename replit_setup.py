#!/usr/bin/env python3
"""
Conga CLM AI Agent - Cloud Setup Script
This script prepares the application for cloud deployment (Replit, etc.)
"""

import os
import shutil
from pathlib import Path

def create_cloud_package():
    """Create a package ready for cloud deployment."""

    print("Creating cloud deployment package...")

    # Create cloud deployment directory
    cloud_dir = Path("CloudDeployment")
    if cloud_dir.exists():
        shutil.rmtree(cloud_dir)
    cloud_dir.mkdir()

    # Files to include
    files_to_copy = [
        "web_app.py",
        ".env.example",
        "requirements.txt",
        "src/",
        "web/",
        "prompts/"
    ]

    # Copy files
    for item in files_to_copy:
        src_path = Path(item)
        if src_path.exists():
            if src_path.is_dir():
                shutil.copytree(src_path, cloud_dir / item)
            else:
                shutil.copy2(src_path, cloud_dir / item)
            print(f"✓ Copied {item}")

    # Create cloud-specific files

    # Replit configuration
    with open(cloud_dir / ".replit", "w") as f:
        f.write("""language = "python3"
run = "python web_app.py"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "python web_app.py"]
""")

    # Create main.py (alternative entry point)
    with open(cloud_dir / "main.py", "w") as f:
        f.write("""#!/usr/bin/env python3
# Alternative entry point for cloud platforms
import web_app

if __name__ == "__main__":
    # Run the Flask app
    web_app.socketio.run(
        web_app.app,
        host='0.0.0.0',
        port=8080,
        debug=False,
        allow_unsafe_werkzeug=True
    )
""")

    # Create README for cloud deployment
    with open(cloud_dir / "README_CLOUD.md", "w") as f:
        f.write("""# Conga CLM AI Agent - Cloud Deployment

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
""")

    print(f"\n✅ Cloud deployment package created in: {cloud_dir}")
    print("\nOptions for your office PC:")
    print("1. Upload to Replit.com (free, runs in browser)")
    print("2. Use portable Python (no installation needed)")
    print("3. Ask IT for Python installation approval")

if __name__ == "__main__":
    create_cloud_package()