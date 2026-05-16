"""Tool definitions for Claude function calling to interact with Conga CLM."""

from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from .conga_client import CongaClient, CongaAPIError, CongaAuthenticationError

class CongaTools:
    """Tools for Claude to interact with Conga CLM APIs."""

    def __init__(self):
        self.client = CongaClient()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return all tool definitions for Claude."""
        return [
            {
                "name": "search_contracts",
                "description": "Search for contracts in Conga CLM. Use this to find existing contracts by account, type, status, name, or other criteria.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "account_name": {
                            "type": "string",
                            "description": "Name of the account/company to search contracts for"
                        },
                        "contract_type": {
                            "type": "string",
                            "description": "Type of contract (MSA, NDA, SOW, ORDER, AMENDMENT)"
                        },
                        "status": {
                            "type": "string",
                            "description": "Contract status (Active, Draft, Expired, Terminated, etc.)"
                        },
                        "contract_name": {
                            "type": "string",
                            "description": "Contract name to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_contract",
                "description": "Get detailed information about a specific contract by ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {
                            "type": "string",
                            "description": "The ID of the contract to retrieve"
                        }
                    },
                    "required": ["contract_id"],
                    "additionalProperties": False
                }
            },
            {
                "name": "create_contract",
                "description": "Create a new contract in Conga CLM. Always search for existing contracts with the same account first.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "contract_type": {
                            "type": "string",
                            "description": "Type of contract (MSA, NDA, SOW, ORDER, AMENDMENT)"
                        },
                        "contract_name": {
                            "type": "string",
                            "description": "Name for the contract"
                        },
                        "account_id": {
                            "type": "string",
                            "description": "Account ID (must be obtained from search_accounts first)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Contract start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Contract end date in YYYY-MM-DD format"
                        },
                        "term_months": {
                            "type": "integer",
                            "description": "Contract term in months"
                        },
                        "total_contract_value": {
                            "type": "number",
                            "description": "Total contract value amount"
                        }
                    },
                    "required": ["contract_type", "contract_name", "account_id"],
                    "additionalProperties": False
                }
            },
            {
                "name": "update_contract",
                "description": "Update an existing contract with new information.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {
                            "type": "string",
                            "description": "The ID of the contract to update"
                        },
                        "contract_data": {
                            "type": "object",
                            "description": "Fields to update on the contract"
                        }
                    },
                    "required": ["contract_id", "contract_data"],
                    "additionalProperties": False
                }
            },
            {
                "name": "lifecycle_action",
                "description": "Perform lifecycle actions on contracts (activate, renew, terminate, expire, cancel, amend, clone).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {
                            "type": "string",
                            "description": "The ID of the contract"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["activate", "renew", "terminate", "expire", "cancel", "amend", "clone"],
                            "description": "Action to perform: activate, renew, terminate, expire, cancel, amend, clone"
                        },
                        "data": {
                            "type": "object",
                            "description": "Additional data for the action (optional)"
                        }
                    },
                    "required": ["contract_id", "action"],
                    "additionalProperties": False
                }
            },
            {
                "name": "search_accounts",
                "description": "Search for accounts/companies in Conga. Use this to find the correct Account ID when creating contracts.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Account/company name to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": ["name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "search_templates",
                "description": "Search for contract templates in Conga CLM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "template_type": {
                            "type": "string",
                            "description": "Type of template to search for"
                        },
                        "name": {
                            "type": "string",
                            "description": "Template name to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "additionalProperties": False
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given parameters."""
        try:
            if tool_name == "search_contracts":
                return self._search_contracts(parameters)
            elif tool_name == "get_contract":
                return self._get_contract(parameters)
            elif tool_name == "create_contract":
                return self._create_contract(parameters)
            elif tool_name == "update_contract":
                return self._update_contract(parameters)
            elif tool_name == "lifecycle_action":
                return self._lifecycle_action(parameters)
            elif tool_name == "search_accounts":
                return self._search_accounts(parameters)
            elif tool_name == "search_templates":
                return self._search_templates(parameters)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except CongaAuthenticationError as e:
            return {"error": f"Authentication failed: {str(e)}"}
        except CongaAPIError as e:
            return {"error": f"API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def _search_contracts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for contracts with given criteria."""
        query = {
            "pageSize": params.get("limit", 10),
            "filters": []
        }

        # Store search criteria for client-side filtering
        search_account_name = params.get("account_name")

        # Add filters based on parameters
        if "account_name" in params:
            # Try both operators since Conga API filtering seems inconsistent
            query["filters"].append({
                "field": "Account.Name",
                "operator": "equals",  # Changed from "contains" to "equals"
                "value": params["account_name"]
            })

        if "contract_type" in params:
            query["filters"].append({
                "field": "ContractType",
                "operator": "equals",
                "value": params["contract_type"]
            })

        if "status" in params:
            query["filters"].append({
                "field": "Status",
                "operator": "equals",
                "value": params["status"]
            })

        if "contract_name" in params:
            query["filters"].append({
                "field": "Name",
                "operator": "contains",
                "value": params["contract_name"]
            })

        # Add sorting
        query["sorts"] = [{"field": "CreatedDate", "direction": "DESC"}]

        result = self.client.query_contracts(query)
        return self._format_contract_results(result, search_account_name)

    def _get_contract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get contract details by ID."""
        contract_id = params["contract_id"]
        result = self.client.get_contract(contract_id)
        return {"success": True, "contract": result}

    def _create_contract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contract."""
        contract_data = {
            "ContractType": params["contract_type"],
            "Name": params["contract_name"],
            "AccountId": params["account_id"]
        }

        # Add optional fields if provided
        if "start_date" in params:
            contract_data["StartDate"] = params["start_date"]
        if "end_date" in params:
            contract_data["EndDate"] = params["end_date"]
        if "term_months" in params:
            contract_data["TermMonths"] = params["term_months"]
        if "total_contract_value" in params:
            contract_data["TotalContractValue"] = params["total_contract_value"]

        result = self.client.create_contract(contract_data)
        return {
            "success": True,
            "message": f"Contract created successfully",
            "contract_id": result.get("Id"),
            "contract": result
        }

    def _update_contract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contract."""
        contract_id = params["contract_id"]
        contract_data = params["contract_data"]

        result = self.client.update_contract(contract_id, contract_data)
        return {
            "success": True,
            "message": f"Contract {contract_id} updated successfully",
            "contract": result
        }

    def _lifecycle_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform lifecycle action on a contract."""
        contract_id = params["contract_id"]
        action = params["action"]
        data = params.get("data", {})

        action_methods = {
            "activate": self.client.activate_contract,
            "renew": self.client.renew_contract,
            "terminate": self.client.terminate_contract,
            "expire": self.client.expire_contract,
            "cancel": self.client.cancel_contract,
            "amend": self.client.amend_contract,
            "clone": self.client.clone_contract
        }

        if action not in action_methods:
            return {"error": f"Invalid action: {action}"}

        result = action_methods[action](contract_id, data)
        return {
            "success": True,
            "message": f"Contract {contract_id} {action}d successfully",
            "result": result
        }

    def _search_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for accounts by name using available Conga methods."""
        account_name = params["name"]

        try:
            result = self.client.search_accounts(account_name)

            # Handle the new response format with method indication
            method = result.get("method", "unknown")
            accounts_data = result.get("data", [])

            print(f"[TOOL DEBUG] Method: {method}")
            print(f"[TOOL DEBUG] Raw accounts_data: {accounts_data}")
            print(f"[TOOL DEBUG] Raw result: {result}")

            if method == "failed":
                return {
                    "success": False,
                    "message": f"Account search not available: {result.get('error', 'Unknown error')}",
                    "accounts": [],
                    "method": method
                }

            # Ensure accounts_data is a list
            if not isinstance(accounts_data, list):
                print(f"[TOOL DEBUG] Converting non-list data to list: {type(accounts_data)}")
                accounts_data = []

            formatted_accounts = []
            for i, acc in enumerate(accounts_data):
                print(f"[TOOL DEBUG] Processing account {i}: {acc}")
                formatted_account = {
                    "id": acc.get("id") or acc.get("Id"),
                    "name": acc.get("name") or acc.get("Name"),
                    "type": acc.get("type") or acc.get("Type"),
                    "industry": acc.get("industry") or acc.get("Industry")
                }
                print(f"[TOOL DEBUG] Formatted account {i}: {formatted_account}")
                formatted_accounts.append(formatted_account)

            method_message = {
                "xauthor": "Direct account API",
                "contracts": "Extracted from existing contracts",
                "failed": "No method available"
            }.get(method, method)

            print(f"[TOOL DEBUG] Final formatted_accounts count: {len(formatted_accounts)}")

            result_data = {
                "success": True,
                "message": f"Found {len(formatted_accounts)} accounts matching '{account_name}' using {method_message}",
                "accounts": formatted_accounts,
                "method": method,
                "note": "Limited to accounts that have existing contracts" if method == "contracts" else None
            }

            print(f"[TOOL DEBUG] Final result: {result_data}")
            return result_data

        except Exception as e:
            return {
                "error": f"Account search failed: {str(e)}",
                "success": False
            }

    def _search_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for contract templates."""
        query = {
            "pageSize": params.get("limit", 10),
            "filters": []
        }

        if "template_type" in params:
            query["filters"].append({
                "field": "Type",
                "operator": "equals",
                "value": params["template_type"]
            })

        if "name" in params:
            query["filters"].append({
                "field": "Name",
                "operator": "contains",
                "value": params["name"]
            })

        result = self.client.search_templates(query)
        templates = result.get("records", [])

        return {
            "success": True,
            "message": f"Found {len(templates)} templates",
            "templates": [
                {
                    "id": tmp.get("Id"),
                    "name": tmp.get("Name"),
                    "type": tmp.get("Type"),
                    "status": tmp.get("Status")
                }
                for tmp in templates
            ]
        }

    def _format_contract_results(self, result: Dict[str, Any], filter_account_name: str = None) -> Dict[str, Any]:
        """Format contract query results for better readability."""
        print(f"[TOOL DEBUG] Raw contract search result structure: {result}")

        # Handle Conga's actual response structure (same as in search_accounts)
        contracts = []
        if "Success" in result and result["Success"]:
            data_section = result.get("Data", {})
            if isinstance(data_section, dict):
                contracts = data_section.get("Data", [])
            else:
                contracts = data_section if isinstance(data_section, list) else []
        else:
            # Fallback to standard structure
            contracts = result.get("records", [])

        print(f"[TOOL DEBUG] Extracted {len(contracts)} contracts from response")

        formatted_contracts = []
        filtered_count = 0
        for i, contract in enumerate(contracts):
            print(f"[TOOL DEBUG] Processing contract {i}: {contract.get('Id', 'Unknown')} - {contract.get('Name', 'Unnamed')}")

            # Get account name for this contract
            account_name = contract.get("Account", {}).get("Name") if contract.get("Account") else None
            print(f"[TOOL DEBUG] Contract {i} account: '{account_name}'")

            # Apply client-side filtering if account name filter is specified
            if filter_account_name:
                if not account_name:
                    print(f"[TOOL DEBUG] Filtering out contract {i}: no account")
                    filtered_count += 1
                    continue
                elif account_name.lower() != filter_account_name.lower():
                    print(f"[TOOL DEBUG] Filtering out contract {i}: account '{account_name}' doesn't match '{filter_account_name}'")
                    filtered_count += 1
                    continue

            formatted_contract = {
                "id": contract.get("Id"),
                "name": contract.get("Name"),
                "type": contract.get("ContractType"),
                "status": contract.get("Status"),
                "account_name": account_name,
                "start_date": contract.get("StartDate"),
                "end_date": contract.get("EndDate"),
                "total_value": contract.get("TotalContractValue"),
                "created_date": contract.get("CreatedDate")
            }
            print(f"[TOOL DEBUG] Added contract {i}: {formatted_contract}")
            formatted_contracts.append(formatted_contract)

        total_count = result.get("totalSize", len(contracts))
        if "Success" in result and result["Success"]:
            data_section = result.get("Data", {})
            if isinstance(data_section, dict):
                total_count = data_section.get("TotalSize", len(contracts))

        if filter_account_name and filtered_count > 0:
            print(f"[TOOL DEBUG] Client-side filtering: {filtered_count} contracts filtered out for not matching account '{filter_account_name}'")

        print(f"[TOOL DEBUG] Final contract results: {len(formatted_contracts)} contracts matching criteria, total fetched: {len(contracts)}")

        message = f"Found {len(formatted_contracts)} contracts"
        if filter_account_name:
            message += f" for account '{filter_account_name}'"

        return {
            "success": True,
            "message": message,
            "total_count": len(formatted_contracts),  # Return actual filtered count, not API total
            "contracts": formatted_contracts
        }