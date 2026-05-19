#!/usr/bin/env python3
"""Salesforce authentication and basic functionality test script."""

import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.sf_client import SFClient, SalesforceAuthenticationError, SalesforceAPIError


def test_sf_authentication():
    """Test Salesforce authentication and basic API functionality."""

    print("🔍 Testing Salesforce Authentication and API")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Show configuration
    client_id = os.getenv('SF_CLIENT_ID')
    client_secret = os.getenv('SF_CLIENT_SECRET')
    instance_url = os.getenv('SF_INSTANCE_URL')
    api_version = os.getenv('SF_API_VERSION', 'v62.0')
    agreement_object = os.getenv('SF_AGREEMENT_OBJECT', 'Apttus__APTS_Agreement__c')

    print(f"Client ID: {client_id[:20]}...{client_id[-10:] if client_id else 'NOT SET'}")
    print(f"Client Secret: {'SET' if client_secret else 'NOT SET'}")
    print(f"Instance URL: {instance_url}")
    print(f"API Version: {api_version}")
    print(f"Agreement Object: {agreement_object}")
    print()

    if not all([client_id, client_secret, instance_url]):
        print("❌ Missing required Salesforce credentials")
        print("Required: SF_CLIENT_ID, SF_CLIENT_SECRET, SF_INSTANCE_URL")
        return False

    try:
        # Initialize client
        print("🔐 Initializing Salesforce client...")
        sf_client = SFClient()

        # Test authentication
        print("🔐 Testing OAuth2 authentication...")
        sf_client.authenticate()

        # Show masked token info
        if sf_client.access_token:
            token_preview = f"{sf_client.access_token[:20]}...{sf_client.access_token[-10:]}"
            print(f"✅ Authentication successful")
            print(f"Access Token: {token_preview}")
            print(f"Instance URL: {sf_client.instance_url}")
        else:
            print("❌ Authentication failed - no access token received")
            return False

        print()

        # Test basic SOQL query
        print("📊 Testing basic SOQL query...")
        test_soql = f"SELECT Id, Name, Apttus__Status__c FROM {agreement_object} LIMIT 3"
        print(f"Query: {test_soql}")

        try:
            records = sf_client.query(test_soql)
            print(f"✅ Query successful - Found {len(records)} records")

            if records:
                print("\nSample records:")
                for i, record in enumerate(records, 1):
                    record_id = record.get('Id', 'Unknown')
                    name = record.get('Name', 'Unnamed')
                    status = record.get('Apttus__Status__c', 'No Status')
                    print(f"  {i}. {name} (ID: {record_id}) - Status: {status}")
            else:
                print("  No agreements found in the system")

        except SalesforceAPIError as e:
            print(f"❌ SOQL query failed: {str(e)}")
            print("\nThis might indicate:")
            print("  - The agreement object doesn't exist")
            print("  - Insufficient permissions")
            print("  - Wrong object API name")
            return False

        print()

        # Test describe operation
        print("🔍 Testing object describe operation...")
        try:
            describe_result = sf_client.describe_agreement()
            field_count = len(describe_result.get('fields', []))
            object_label = describe_result.get('label', 'Unknown')

            print(f"✅ Describe successful")
            print(f"Object Label: {object_label}")
            print(f"Field Count: {field_count}")

            # Show some key fields
            fields = describe_result.get('fields', [])
            key_fields = []
            for field in fields:
                name = field.get('name', '')
                if any(keyword in name.lower() for keyword in ['status', 'account', 'contract', 'value', 'date']):
                    label = field.get('label', name)
                    field_type = field.get('type', 'unknown')
                    key_fields.append(f"{name} ({label}) - {field_type}")

            if key_fields:
                print(f"\nKey fields found:")
                for field in key_fields[:10]:  # Show first 10
                    print(f"  - {field}")
                if len(key_fields) > 10:
                    print(f"  ... and {len(key_fields) - 10} more")

        except SalesforceAPIError as e:
            print(f"❌ Describe operation failed: {str(e)}")
            return False

        print("\n" + "=" * 50)
        print("✅ All tests passed! Salesforce integration is working correctly.")
        print("\nNext steps:")
        print("1. Run: python chat.py")
        print("2. Try sample queries like:")
        print("   - 'List my recent agreements'")
        print("   - 'Show me agreements expiring soon'")
        print("   - 'What are the available fields for agreements?'")

        return True

    except SalesforceAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("\nThis might indicate:")
        print("  - Invalid Client ID or Client Secret")
        print("  - Connected App not configured correctly")
        print("  - Instance URL is wrong")
        print("  - Client Credentials flow not enabled")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_sf_authentication()
    sys.exit(0 if success else 1)