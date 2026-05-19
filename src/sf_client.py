"""Salesforce REST API client for Conga CLM integration."""

import os
import requests
import json
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv


class SalesforceAuthenticationError(Exception):
    """Raised when authentication with Salesforce fails."""
    pass


class SalesforceAPIError(Exception):
    """Raised when Salesforce API calls fail."""
    pass


class SFClient:
    """Client for interacting with Salesforce REST APIs for Conga CLM."""

    def __init__(self):
        load_dotenv()

        self.client_id = os.getenv('SF_CLIENT_ID')
        self.client_secret = os.getenv('SF_CLIENT_SECRET')
        self.instance_url = os.getenv('SF_INSTANCE_URL')
        self.api_version = os.getenv('SF_API_VERSION', 'v62.0')
        self.agreement_object = os.getenv('SF_AGREEMENT_OBJECT', 'Apttus__APTS_Agreement__c')

        if not all([self.client_id, self.client_secret, self.instance_url]):
            raise SalesforceAuthenticationError(
                "Missing required Salesforce environment variables. Please check SF_CLIENT_ID, SF_CLIENT_SECRET, and SF_INSTANCE_URL."
            )

        # Ensure instance URL has proper format
        if not self.instance_url.startswith('https://'):
            self.instance_url = f"https://{self.instance_url}"

        self.access_token = None
        self.token_expires_at = None
        self.session = requests.Session()

    def authenticate(self) -> None:
        """Authenticate with Salesforce using OAuth2 client credentials flow."""
        auth_url = f"{self.instance_url}/services/oauth2/token"

        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"[SF API] Authenticating to: {auth_url}")
            response = self.session.post(
                auth_url,
                data=auth_data,
                headers=headers,
                timeout=30
            )

            print(f"[SF API] Auth response: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.instance_url = token_data.get('instance_url', self.instance_url)

                # Client credentials flow doesn't return expires_in, set 2 hour default
                self.token_expires_at = datetime.now() + timedelta(seconds=7200)

                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })

                print(f"[SF API] Authentication successful")
                print(f"[SF API] Instance URL: {self.instance_url}")

            else:
                error_text = response.text
                try:
                    error_data = response.json()
                    if isinstance(error_data, list) and error_data:
                        error_msg = error_data[0].get('message', 'Unknown error')
                        error_code = error_data[0].get('errorCode', 'UNKNOWN')
                        raise SalesforceAuthenticationError(f"Authentication failed: {error_code} - {error_msg}")
                except json.JSONDecodeError:
                    pass

                raise SalesforceAuthenticationError(
                    f"Authentication failed: {response.status_code} - {error_text}"
                )

        except requests.RequestException as e:
            raise SalesforceAuthenticationError(f"Authentication request failed: {str(e)}")

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token, refreshing if necessary."""
        if (not self.access_token or
            not self.token_expires_at or
            datetime.now() >= self.token_expires_at):
            self.authenticate()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the Salesforce API."""
        self._ensure_authenticated()

        # Build full URL
        if path.startswith('/'):
            url = f"{self.instance_url}{path}"
        else:
            url = f"{self.instance_url}/{path}"

        # Set content type for write methods
        if method.upper() in ['POST', 'PUT', 'PATCH'] and 'headers' not in kwargs:
            kwargs['headers'] = {'Content-Type': 'application/json'}
        elif method.upper() in ['POST', 'PUT', 'PATCH'] and 'Content-Type' not in kwargs.get('headers', {}):
            kwargs.setdefault('headers', {})['Content-Type'] = 'application/json'

        print(f"[SF API] {method.upper()} {url}")
        if 'json' in kwargs:
            print(f"[SF API] Payload: {json.dumps(kwargs['json'], indent=2)}")
        if 'params' in kwargs:
            print(f"[SF API] Params: {kwargs['params']}")

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)

            print(f"[SF API] Response: {response.status_code}")
            if response.text:
                response_preview = response.text[:500] + ('...' if len(response.text) > 500 else '')
                print(f"[SF API] Response Body: {response_preview}")

            # Handle token expiry or invalid session
            if (response.status_code == 401 or
                (response.status_code == 400 and 'INVALID_SESSION_ID' in response.text)):
                print("[SF API] 401 or INVALID_SESSION_ID detected, re-authenticating...")
                self.authenticate()
                # Retry the request once
                response = self.session.request(method, url, timeout=30, **kwargs)
                print(f"[SF API] Retry Response: {response.status_code}")

            return response

        except requests.RequestException as e:
            print(f"[SF API] Request Exception: {str(e)}")
            raise SalesforceAPIError(f"API request failed: {str(e)}")

    def _raise_api_error(self, response: requests.Response, base_message: str) -> None:
        """Helper to raise API errors with detailed Salesforce error messages."""
        error_msg = f"{base_message}: {response.status_code}"

        try:
            error_data = response.json()
            if isinstance(error_data, list) and error_data:
                # Salesforce error format: [{"message":"...","errorCode":"..."}]
                errors = []
                for error in error_data:
                    if isinstance(error, dict):
                        msg = error.get('message', 'Unknown error')
                        code = error.get('errorCode', '')
                        if code:
                            errors.append(f"{code}: {msg}")
                        else:
                            errors.append(msg)
                if errors:
                    error_msg += f" - {'; '.join(errors)}"
            elif isinstance(error_data, dict):
                if 'message' in error_data:
                    error_msg += f" - {error_data['message']}"
                elif 'error' in error_data:
                    error_msg += f" - {error_data['error']}"
        except (json.JSONDecodeError, AttributeError):
            error_msg += f" - {response.text}"

        raise SalesforceAPIError(error_msg)

    def query(self, soql: str) -> List[Dict[str, Any]]:
        """Execute a SOQL query and return all records, handling pagination."""
        encoded_soql = urllib.parse.quote(soql)
        path = f"/services/data/{self.api_version}/query/"
        params = {'q': soql}  # Let requests handle URL encoding

        all_records = []
        next_records_url = None

        while True:
            if next_records_url:
                # Use the full nextRecordsUrl for pagination
                response = self._request('GET', next_records_url)
            else:
                # Initial query
                response = self._request('GET', path, params=params)

            if response.status_code == 200:
                result = response.json()

                # Add records to our collection
                records = result.get('records', [])
                all_records.extend(records)

                print(f"[SF API] Retrieved {len(records)} records (total: {len(all_records)})")

                # Check if there are more records
                if result.get('done', True):
                    break

                next_records_url = result.get('nextRecordsUrl')
                if not next_records_url:
                    break
            else:
                self._raise_api_error(response, "SOQL query failed")

        print(f"[SF API] Query complete: {len(all_records)} total records")
        return all_records

    def get_agreement(self, agreement_id: str) -> Dict[str, Any]:
        """Get a specific agreement record by ID."""
        path = f"/services/data/{self.api_version}/sobjects/{self.agreement_object}/{agreement_id}"
        response = self._request('GET', path)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, f"Failed to get agreement {agreement_id}")

    def create_agreement(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agreement record."""
        path = f"/services/data/{self.api_version}/sobjects/{self.agreement_object}"
        response = self._request('POST', path, json=fields)

        if response.status_code == 201:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to create agreement")

    def update_agreement(self, agreement_id: str, fields: Dict[str, Any]) -> bool:
        """Update an existing agreement record."""
        path = f"/services/data/{self.api_version}/sobjects/{self.agreement_object}/{agreement_id}"
        response = self._request('PATCH', path, json=fields)

        if response.status_code == 204:
            return True
        else:
            self._raise_api_error(response, f"Failed to update agreement {agreement_id}")

    def delete_agreement(self, agreement_id: str) -> bool:
        """Delete an agreement record."""
        path = f"/services/data/{self.api_version}/sobjects/{self.agreement_object}/{agreement_id}"
        response = self._request('DELETE', path)

        if response.status_code == 204:
            return True
        else:
            self._raise_api_error(response, f"Failed to delete agreement {agreement_id}")

    def describe_agreement(self) -> Dict[str, Any]:
        """Get metadata about the agreement object fields."""
        path = f"/services/data/{self.api_version}/sobjects/{self.agreement_object}/describe"
        response = self._request('GET', path)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, f"Failed to describe {self.agreement_object}")