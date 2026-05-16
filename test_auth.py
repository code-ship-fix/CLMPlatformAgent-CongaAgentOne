#!/usr/bin/env python3
"""Test Conga authentication and API access."""

import os
import sys
import requests
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_authentication():
    """Test Conga CLM authentication."""
    load_dotenv()

    client_id = os.getenv('CONGA_CLIENT_ID')
    client_secret = os.getenv('CONGA_CLIENT_SECRET')
    auth_url = os.getenv('CONGA_AUTH_URL')
    base_url = os.getenv('CONGA_BASE_URL')

    print("🔍 Testing Conga CLM Authentication")
    print("=" * 50)

    # Check if credentials are set
    print(f"Client ID: {client_id[:10]}...{client_id[-4:] if client_id else 'NOT SET'}")
    print(f"Client Secret: {'SET' if client_secret else 'NOT SET'}")
    print(f"Auth URL: {auth_url}")
    print(f"Base URL: {base_url}")
    print()

    if not all([client_id, client_secret, auth_url, base_url]):
        print("❌ Missing credentials!")
        return False

    # Test authentication
    print("🔐 Testing OAuth2 authentication...")
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(auth_url, data=auth_data, headers=headers, timeout=30)

        print(f"Auth Response Status: {response.status_code}")
        print(f"Auth Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in')

            print(f"✅ Authentication successful!")
            print(f"Access Token: {access_token[:20]}...{access_token[-10:] if access_token else 'None'}")
            print(f"Expires In: {expires_in} seconds")

            # Test API call with token
            print("\n🧪 Testing API access...")
            api_headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Try account search endpoint
            test_url = f"{base_url}/api/xauthor/v1/accounts/name?name=test"
            api_response = requests.get(test_url, headers=api_headers, timeout=30)

            print(f"Account API Status: {api_response.status_code}")
            print(f"Account API Response: {api_response.text[:200]}...")

            if api_response.status_code == 200:
                print("✅ Account API access successful!")
                return True
            elif api_response.status_code == 401:
                print("❌ Account API returned 401 - Authentication failed")
            elif api_response.status_code == 403:
                print("❌ Account API returned 403 - Access denied (check permissions)")
            elif api_response.status_code == 404:
                print("❌ Account API returned 404 - Endpoint not found")
            else:
                print(f"❌ Account API returned {api_response.status_code}")

        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.RequestException as e:
        print(f"❌ Request failed: {str(e)}")

    return False

if __name__ == "__main__":
    test_authentication()