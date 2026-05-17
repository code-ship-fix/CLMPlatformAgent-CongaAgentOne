#!/usr/bin/env python3
"""Quick test script for Anthropic API key."""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

anthropic_key = os.getenv('ANTHROPIC_API_KEY')

print(f"🔍 Testing Anthropic API Key")
print("=" * 30)
print(f"API Key: {anthropic_key[:20]}...{anthropic_key[-10:] if anthropic_key else 'NOT SET'}")

if not anthropic_key:
    print("❌ No Anthropic API key found")
    exit(1)

# Test the API key with a simple request
try:
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': anthropic_key,
            'anthropic-version': '2023-06-01'
        },
        json={
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 10,
            'messages': [{'role': 'user', 'content': 'Hello'}]
        },
        timeout=10
    )

    if response.status_code == 200:
        print("✅ Anthropic API key is valid")
    else:
        print(f"❌ Anthropic API failed: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error testing Anthropic API: {str(e)}")