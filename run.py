#!/usr/bin/env python3
"""
Conga CLM AI Agent - Launcher Script
Simplified launcher for the web application with auto-setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_and_install_requirements():
    """Check and install required packages."""
    try:
        # Check if requirements are already installed
        import flask
        import flask_socketio
        import anthropic
        import requests
        from dotenv import load_dotenv
        print("✅ All required packages are already installed")
        return True
    except ImportError as e:
        print(f"📦 Installing missing package: {str(e).split()[-1]}")

    try:
        print("📦 Installing required packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def check_environment():
    """Check environment variables."""
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['CONGA_CLIENT_ID', 'CONGA_CLIENT_SECRET', 'ANTHROPIC_API_KEY']
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your-{var.lower().replace("_", "-")}-here':
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing or placeholder values for required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Please update your .env file with actual credentials.")
        print("   See .env.example for the required format.")
        return False

    print("✅ Environment variables configured")
    return True

def get_local_ip():
    """Get local IP address."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    """Main launcher function."""
    print("🤖 Conga CLM AI Agent - Web Launcher")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        sys.exit(1)

    # Check and install requirements
    if not check_and_install_requirements():
        input("Press Enter to exit...")
        sys.exit(1)

    # Check environment
    if not check_environment():
        input("Press Enter to exit...")
        sys.exit(1)

    # Get network info
    local_ip = get_local_ip()
    port = 5000

    print("\n🚀 Starting Conga CLM AI Agent Web Server...")
    print(f"🏠 Local access: http://localhost:{port}")
    print(f"🌐 Network access: http://{local_ip}:{port}")
    print(f"📱 Mobile access: http://{local_ip}:{port} (same network)")
    print("\n💡 Tips:")
    print("   • Use the local URL for this computer only")
    print("   • Use the network URL to access from other devices on same WiFi")
    print("   • Press Ctrl+C to stop the server")
    print("=" * 50)

    try:
        # Import and run the web application
        from web_app import app, socketio

        # Run with SocketIO
        socketio.run(
            app,
            host='0.0.0.0',  # Allow external connections
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )

    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()