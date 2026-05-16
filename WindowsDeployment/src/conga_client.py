import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

class CongaAuthenticationError(Exception):
    """Raised when authentication with Conga fails."""
    pass

class CongaAPIError(Exception):
    """Raised when Conga API calls fail."""
    pass

class CongaClient:
    """Client for interacting with Conga CLM REST APIs."""

    def __init__(self):
        load_dotenv()

        self.client_id = os.getenv('CONGA_CLIENT_ID')
        self.client_secret = os.getenv('CONGA_CLIENT_SECRET')
        self.auth_url = os.getenv('CONGA_AUTH_URL')
        self.base_url = os.getenv('CONGA_BASE_URL')

        if not all([self.client_id, self.client_secret, self.auth_url, self.base_url]):
            raise CongaAuthenticationError(
                "Missing required Conga environment variables. Please check your .env file."
            )

        self.access_token = None
        self.token_expires_at = None
        self.session = requests.Session()

    def authenticate(self) -> None:
        """Authenticate with Conga CLM using OAuth2 client credentials flow."""
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = self.session.post(
                self.auth_url,
                data=auth_data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)

                # Set expiry time with 5 minute buffer
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })

            else:
                raise CongaAuthenticationError(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )

        except requests.RequestException as e:
            raise CongaAuthenticationError(f"Authentication request failed: {str(e)}")

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token, refreshing if necessary."""
        if (not self.access_token or
            not self.token_expires_at or
            datetime.now() >= self.token_expires_at):
            self.authenticate()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the Conga API."""
        self._ensure_authenticated()

        url = f"{self.base_url.rstrip('/')}{endpoint}"

        # Log the API request with masked sensitive data
        print(f"[CONGA API] {method} {url}")

        # Mask authorization header for security
        headers_copy = dict(self.session.headers)
        if 'Authorization' in headers_copy:
            token = headers_copy['Authorization']
            if len(token) > 20:
                headers_copy['Authorization'] = f"{token[:20]}...{token[-10:]}"
        print(f"[CONGA API] Headers: {headers_copy}")

        if 'json' in kwargs:
            print(f"[CONGA API] Payload: {kwargs['json']}")
        if 'params' in kwargs:
            print(f"[CONGA API] Params: {kwargs['params']}")
        if 'data' in kwargs:
            print(f"[CONGA API] Data: {kwargs['data']}")

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)

            print(f"[CONGA API] Response: {response.status_code}")
            print(f"[CONGA API] Response Headers: {dict(response.headers)}")
            if response.text:
                print(f"[CONGA API] Response Body: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")

            # Handle token expiry
            if response.status_code == 401:
                print("[CONGA API] 401 detected, re-authenticating...")
                self.authenticate()
                response = self.session.request(method, url, timeout=30, **kwargs)
                print(f"[CONGA API] Retry Response: {response.status_code}")

            return response

        except requests.RequestException as e:
            print(f"[CONGA API] Request Exception: {str(e)}")
            raise CongaAPIError(f"API request failed: {str(e)}")

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a GET request to the Conga API."""
        return self._make_request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a POST request to the Conga API."""
        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a PUT request to the Conga API."""
        return self._make_request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a DELETE request to the Conga API."""
        return self._make_request('DELETE', endpoint, **kwargs)

    # Contract Operations
    def create_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contract in Conga CLM."""
        response = self.post('/api/clm/v1/contracts', json=contract_data)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to create contract")

    def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """Get contract details by ID."""
        response = self.get(f'/api/clm/v1/contracts/{contract_id}')

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to get contract")

    def update_contract(self, contract_id: str, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contract."""
        response = self.put(f'/api/clm/v1/contracts/{contract_id}', json=contract_data)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to update contract")

    def delete_contract(self, contract_id: str) -> bool:
        """Delete a contract."""
        response = self.delete(f'/api/clm/v1/contracts/{contract_id}')

        if response.status_code in [200, 204]:
            return True
        else:
            self._raise_api_error(response, "Failed to delete contract")

    def query_contracts(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query contracts using the search API."""
        response = self.post('/api/clm/v1/contracts/query', json=query_data)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to query contracts")

    # Contract Lifecycle Operations
    def activate_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Activate a contract."""
        return self._lifecycle_action(contract_id, "activate", data)

    def renew_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Renew a contract."""
        return self._lifecycle_action(contract_id, "renew", data)

    def amend_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Amend a contract."""
        return self._lifecycle_action(contract_id, "amend", data)

    def terminate_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Terminate a contract."""
        return self._lifecycle_action(contract_id, "terminate", data)

    def expire_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Expire a contract."""
        return self._lifecycle_action(contract_id, "expire", data)

    def cancel_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cancel a contract."""
        return self._lifecycle_action(contract_id, "cancel", data)

    def clone_contract(self, contract_id: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Clone a contract."""
        return self._lifecycle_action(contract_id, "clone", data)

    def _lifecycle_action(self, contract_id: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform a lifecycle action on a contract."""
        payload = data or {}
        response = self.post(f'/api/clm/v1/contracts/{contract_id}/{action}', json=payload)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            self._raise_api_error(response, f"Failed to {action} contract")

    # Account Operations
    def search_accounts(self, account_name: str) -> Dict[str, Any]:
        """Search accounts by name - try multiple methods."""
        # Method 1: Try the xauthor endpoint
        try:
            response = self.get(f'/api/xauthor/v1/accounts/name?name={account_name}')
            if response.status_code == 200:
                return {"method": "xauthor", "data": response.json()}
        except Exception as e:
            pass

        # Method 2: Try searching contracts and extract account names
        try:
            query = {
                "pageSize": 20,
                "filters": [
                    {
                        "field": "Account.Name",
                        "operator": "contains",
                        "value": account_name
                    }
                ],
                "sorts": [{"field": "Account.Name", "direction": "ASC"}]
            }

            print(f"[CONGA API] Searching contracts for Account.Name contains '{account_name}'")

            response = self.post('/api/clm/v1/contracts/query', json=query)
            if response.status_code == 200:
                response_data = response.json()
                print(f"[CONGA API] Full response structure: {response_data}")

                # Handle Conga's actual response structure
                contracts = []
                if "Success" in response_data and response_data["Success"]:
                    data_section = response_data.get("Data", {})
                    if isinstance(data_section, dict):
                        contracts = data_section.get("Data", [])
                    else:
                        contracts = data_section if isinstance(data_section, list) else []
                else:
                    # Fallback to standard structure
                    contracts = response_data.get("records", [])

                print(f"[CONGA API] Extracted {len(contracts)} contracts")

                # Extract unique accounts from contracts
                accounts = {}
                for contract in contracts:
                    print(f"[CONGA API] Processing contract: {contract.get('Id', 'Unknown')} - {contract.get('Name', 'Unnamed')}")

                    account = contract.get("Account")
                    if account and account.get("Name"):
                        account_id = account.get("Id")
                        account_name = account.get("Name")
                        print(f"[CONGA API] Found account: {account_name} (ID: {account_id})")

                        if account_id not in accounts:
                            accounts[account_id] = {
                                "Id": account_id,
                                "Name": account_name,
                                "Type": account.get("Type"),
                                "Industry": account.get("Industry")
                            }

                print(f"[CONGA API] Unique accounts found: {len(accounts)}")
                for acc_id, acc in accounts.items():
                    print(f"[CONGA API] - {acc['Name']} (ID: {acc_id})")

                return {
                    "method": "contracts",
                    "data": list(accounts.values())
                }

        except Exception as e:
            pass

        # Method 3: Return empty result with error info
        return {
            "method": "failed",
            "data": [],
            "error": "No available method to search accounts - API access limited"
        }

    # Template Operations
    def search_templates(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search templates."""
        response = self.post('/api/clm/v1/templates/query', json=query_data)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to search templates")

    # Document Operations
    def query_contract_documents(self, contract_id: str, query_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query documents for a contract."""
        payload = query_data or {}
        response = self.post(f'/api/clm/v1/contracts/{contract_id}/documents/query', json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to query contract documents")

    def generate_contract_document(self, contract_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a document for a contract."""
        response = self.post(f'/api/clm/v1/contracts/{contract_id}/generate', json=data)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            self._raise_api_error(response, "Failed to generate contract document")

    def _raise_api_error(self, response: requests.Response, base_message: str) -> None:
        """Helper to raise API errors with detailed messages."""
        error_msg = f"{base_message}: {response.status_code}"
        try:
            error_detail = response.json()
            if 'message' in error_detail:
                error_msg += f" - {error_detail['message']}"
            elif 'error' in error_detail:
                error_msg += f" - {error_detail['error']}"
            elif 'errors' in error_detail:
                error_msg += f" - {error_detail['errors']}"
        except:
            error_msg += f" - {response.text}"

        raise CongaAPIError(error_msg)