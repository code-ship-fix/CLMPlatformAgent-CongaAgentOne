"""Tool definitions for Claude function calling to interact with Salesforce-based Conga CLM."""

from typing import Dict, Any, List
import json
import re
from datetime import datetime, timedelta
from .sf_client import SFClient, SalesforceAPIError, SalesforceAuthenticationError


class SalesforceTools:
    """Tools for Claude to interact with Salesforce Conga CLM APIs."""

    def __init__(self):
        self.client = SFClient()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return all tool definitions for Claude."""
        return [
            {
                "name": "search_agreements",
                "description": "Search for agreements in Salesforce Conga CLM. Use this to find agreements by status, account, dates, or value ranges.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Filter criteria for agreements",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "description": "Agreement status (e.g., 'In Effect', 'Expired', 'In Authoring')"
                                },
                                "status_category": {
                                    "type": "string",
                                    "description": "Status category (In Authoring, In Signatures, In Effect, Expired, Terminated, Request)"
                                },
                                "account_name": {
                                    "type": "string",
                                    "description": "Account/company name to filter by"
                                },
                                "start_date_from": {
                                    "type": "string",
                                    "description": "Start date range from (YYYY-MM-DD format)"
                                },
                                "start_date_to": {
                                    "type": "string",
                                    "description": "Start date range to (YYYY-MM-DD format)"
                                },
                                "end_date_from": {
                                    "type": "string",
                                    "description": "End date range from (YYYY-MM-DD format)"
                                },
                                "end_date_to": {
                                    "type": "string",
                                    "description": "End date range to (YYYY-MM-DD format)"
                                },
                                "total_value_min": {
                                    "type": "number",
                                    "description": "Minimum total contract value"
                                },
                                "total_value_max": {
                                    "type": "number",
                                    "description": "Maximum total contract value"
                                },
                                "agreement_name": {
                                    "type": "string",
                                    "description": "Agreement name to search for"
                                }
                            },
                            "additionalProperties": False
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 50, max: 200)"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_agreement_details",
                "description": "Get detailed information about a specific agreement by ID, including related clauses.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agreement_id": {
                            "type": "string",
                            "description": "The Salesforce ID of the agreement to retrieve"
                        }
                    },
                    "required": ["agreement_id"],
                    "additionalProperties": False
                }
            },
            {
                "name": "run_soql",
                "description": "Execute a SOQL query directly. Use for complex queries not covered by other tools. Only SELECT queries are allowed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "soql": {
                            "type": "string",
                            "description": "SOQL SELECT query to execute"
                        }
                    },
                    "required": ["soql"],
                    "additionalProperties": False
                }
            },
            {
                "name": "list_agreement_fields",
                "description": "List all available fields for the agreement object to help build queries.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "create_agreement",
                "description": "Create a new agreement in Salesforce.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Agreement name/number"
                        },
                        "account_id": {
                            "type": "string",
                            "description": "Salesforce Account ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "Agreement status"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Contract start date (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Contract end date (YYYY-MM-DD)"
                        },
                        "total_value": {
                            "type": "number",
                            "description": "Total contract value"
                        },
                        "additional_fields": {
                            "type": "object",
                            "description": "Additional fields to set on the agreement"
                        }
                    },
                    "required": ["name"],
                    "additionalProperties": False
                }
            },
            {
                "name": "update_agreement",
                "description": "Update an existing agreement.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "agreement_id": {
                            "type": "string",
                            "description": "Salesforce ID of the agreement to update"
                        },
                        "fields": {
                            "type": "object",
                            "description": "Fields to update on the agreement"
                        }
                    },
                    "required": ["agreement_id", "fields"],
                    "additionalProperties": False
                }
            }
        ]

    def search_agreements(self, filters: Dict[str, Any] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for agreements based on filter criteria."""
        try:
            filters = filters or {}
            limit = min(limit or 50, 200)  # Cap at 200

            # Build SOQL WHERE clause
            where_conditions = []

            if filters.get('status'):
                where_conditions.append(f"Apttus__Status__c = '{self._escape_soql_string(filters['status'])}'")

            if filters.get('status_category'):
                where_conditions.append(f"Apttus__Status_Category__c = '{self._escape_soql_string(filters['status_category'])}'")

            if filters.get('account_name'):
                where_conditions.append(f"Apttus__Account__r.Name LIKE '%{self._escape_soql_string(filters['account_name'])}%'")

            if filters.get('agreement_name'):
                where_conditions.append(f"Name LIKE '%{self._escape_soql_string(filters['agreement_name'])}%'")

            if filters.get('start_date_from'):
                where_conditions.append(f"Apttus__Contract_Start_Date__c >= {filters['start_date_from']}")

            if filters.get('start_date_to'):
                where_conditions.append(f"Apttus__Contract_Start_Date__c <= {filters['start_date_to']}")

            if filters.get('end_date_from'):
                where_conditions.append(f"Apttus__Contract_End_Date__c >= {filters['end_date_from']}")

            if filters.get('end_date_to'):
                where_conditions.append(f"Apttus__Contract_End_Date__c <= {filters['end_date_to']}")

            if filters.get('total_value_min'):
                where_conditions.append(f"Apttus__Total_Contract_Value__c >= {filters['total_value_min']}")

            if filters.get('total_value_max'):
                where_conditions.append(f"Apttus__Total_Contract_Value__c <= {filters['total_value_max']}")

            # Build complete SOQL query
            select_fields = [
                "Id",
                "Name",
                "Apttus__Status__c",
                "Apttus__Status_Category__c",
                "Apttus__Account__r.Name",
                "Apttus__Account__r.Id",
                "Apttus__Contract_Start_Date__c",
                "Apttus__Contract_End_Date__c",
                "Apttus__Total_Contract_Value__c",
                "CreatedDate",
                "LastModifiedDate"
            ]

            # Try to include currency if multi-currency is enabled
            try:
                describe_result = self.client.describe_agreement()
                fields = describe_result.get('fields', [])
                currency_field_exists = any(field.get('name') == 'CurrencyIsoCode' for field in fields)
                if currency_field_exists:
                    select_fields.append("CurrencyIsoCode")
            except:
                pass  # Ignore if describe fails

            soql = f"SELECT {', '.join(select_fields)} FROM {self.client.agreement_object}"

            if where_conditions:
                soql += f" WHERE {' AND '.join(where_conditions)}"

            soql += f" ORDER BY LastModifiedDate DESC LIMIT {limit}"

            print(f"[TOOLS] Executing SOQL: {soql}")

            records = self.client.query(soql)

            return {
                "success": True,
                "count": len(records),
                "records": records,
                "soql_used": soql
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e),
                "records": []
            }

    def get_agreement_details(self, agreement_id: str) -> Dict[str, Any]:
        """Get detailed agreement information including related clauses."""
        try:
            # First get the main agreement record
            agreement = self.client.get_agreement(agreement_id)

            # Try to get related clauses via SOQL subquery
            try:
                clause_soql = f"""
                SELECT Id, Name, Apttus__Status__c, Apttus__Status_Category__c,
                       Apttus__Account__r.Name, Apttus__Account__r.Id,
                       Apttus__Contract_Start_Date__c, Apttus__Contract_End_Date__c,
                       Apttus__Total_Contract_Value__c, CreatedDate, LastModifiedDate,
                       (SELECT Id, Name, Apttus__Clause_Text__c, Apttus__Position__c
                        FROM Apttus__Agreement_Clauses__r
                        ORDER BY Apttus__Position__c)
                FROM {self.client.agreement_object}
                WHERE Id = '{agreement_id}'
                """

                records = self.client.query(clause_soql)
                if records:
                    agreement = records[0]

            except Exception as e:
                print(f"[TOOLS] Could not fetch clauses: {str(e)}")
                # Continue with just the main agreement record

            return {
                "success": True,
                "agreement": agreement
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e)
            }

    def run_soql(self, soql: str) -> Dict[str, Any]:
        """Execute a custom SOQL query (SELECT only)."""
        try:
            # Security check: only allow SELECT queries
            soql_trimmed = soql.strip().upper()
            if not soql_trimmed.startswith('SELECT'):
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed"
                }

            # Additional security checks
            dangerous_keywords = ['DELETE', 'UPDATE', 'INSERT', 'UPSERT', 'MERGE', 'DROP', 'CREATE', 'ALTER']
            if any(keyword in soql_trimmed for keyword in dangerous_keywords):
                return {
                    "success": False,
                    "error": "Query contains forbidden keywords"
                }

            print(f"[TOOLS] Executing custom SOQL: {soql}")

            records = self.client.query(soql)

            return {
                "success": True,
                "count": len(records),
                "records": records,
                "soql_used": soql
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_agreement_fields(self) -> Dict[str, Any]:
        """List all available fields for the agreement object."""
        try:
            describe_result = self.client.describe_agreement()
            fields = describe_result.get('fields', [])

            field_list = []
            for field in fields:
                field_info = {
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "length": field.get("length"),
                    "picklistValues": [v.get("value") for v in field.get("picklistValues", [])],
                    "referenceTo": field.get("referenceTo"),
                    "relationshipName": field.get("relationshipName"),
                    "custom": field.get("custom", False),
                    "createable": field.get("createable", False),
                    "updateable": field.get("updateable", False)
                }
                field_list.append(field_info)

            return {
                "success": True,
                "objectName": self.client.agreement_object,
                "totalFields": len(field_list),
                "fields": field_list
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_agreement(self, name: str, account_id: str = None, status: str = None,
                        start_date: str = None, end_date: str = None, total_value: float = None,
                        additional_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new agreement."""
        try:
            fields = {"Name": name}

            if account_id:
                fields["Apttus__Account__c"] = account_id
            if status:
                fields["Apttus__Status__c"] = status
            if start_date:
                fields["Apttus__Contract_Start_Date__c"] = start_date
            if end_date:
                fields["Apttus__Contract_End_Date__c"] = end_date
            if total_value is not None:
                fields["Apttus__Total_Contract_Value__c"] = total_value

            # Add any additional fields
            if additional_fields:
                fields.update(additional_fields)

            result = self.client.create_agreement(fields)

            return {
                "success": True,
                "id": result.get("id"),
                "created": True
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_agreement(self, agreement_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agreement."""
        try:
            self.client.update_agreement(agreement_id, fields)

            return {
                "success": True,
                "updated": True
            }

        except (SalesforceAPIError, SalesforceAuthenticationError) as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _escape_soql_string(self, value: str) -> str:
        """Escape single quotes in SOQL string values."""
        if value:
            return value.replace("'", "\\'")
        return value

    # Tool execution dispatcher
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with the provided arguments."""
        try:
            if tool_name == "search_agreements":
                return self.search_agreements(
                    filters=kwargs.get("filters"),
                    limit=kwargs.get("limit")
                )
            elif tool_name == "get_agreement_details":
                return self.get_agreement_details(kwargs["agreement_id"])
            elif tool_name == "run_soql":
                return self.run_soql(kwargs["soql"])
            elif tool_name == "list_agreement_fields":
                return self.list_agreement_fields()
            elif tool_name == "create_agreement":
                return self.create_agreement(
                    name=kwargs["name"],
                    account_id=kwargs.get("account_id"),
                    status=kwargs.get("status"),
                    start_date=kwargs.get("start_date"),
                    end_date=kwargs.get("end_date"),
                    total_value=kwargs.get("total_value"),
                    additional_fields=kwargs.get("additional_fields")
                )
            elif tool_name == "update_agreement":
                return self.update_agreement(
                    agreement_id=kwargs["agreement_id"],
                    fields=kwargs["fields"]
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }