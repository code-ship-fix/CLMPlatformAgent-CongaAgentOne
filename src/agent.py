"""Anthropic Claude-powered agent for Salesforce Conga CLM interactions."""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from .tools import SalesforceTools


class SalesforceAgent:
    """AI agent for intelligent Salesforce Conga CLM interactions."""

    def __init__(self):
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.anthropic = Anthropic(api_key=api_key)
        self.tools = SalesforceTools()
        self.model = "claude-sonnet-4-5"
        self.conversation_history: List[Dict[str, Any]] = []

        # System prompt for Salesforce Conga CLM
        self.system_prompt = """You are a Conga CLM assistant working with Salesforce-based agreements.

CONTEXT:
- You work with agreements stored in the Apttus__APTS_Agreement__c object in Salesforce
- Agreement fields use the Apttus__ prefix (e.g., Apttus__Status__c, Apttus__Account__c)
- Always show agreement Name + Id in results so users can reference them
- Related clauses are in the Apttus__Agreement_Clause__c object

TOOLS AVAILABLE:
- search_agreements: Find agreements by filters (status, account, dates, value)
- get_agreement_details: Get full details for a specific agreement ID
- run_soql: Execute custom SOQL SELECT queries for complex requirements
- list_agreement_fields: Discover available fields and their types
- create_agreement: Create new agreements
- update_agreement: Update existing agreements

GUIDELINES:
1. Use list_agreement_fields first if unsure what fields exist in the org
2. Always include Id and Name in search results for easy reference
3. Use search_agreements for filtered lists, get_agreement_details for single records
4. For complex queries, use run_soql with proper SOQL syntax
5. Never invent field names - use describe/list_agreement_fields if uncertain
6. Show meaningful date ranges (e.g., "next 30 days", "this quarter")
7. Format monetary values clearly with currency if available
8. Provide actionable insights about agreement status and timelines

COMMON FIELD MAPPINGS:
- Agreement Number: Name
- Status: Apttus__Status__c
- Status Category: Apttus__Status_Category__c
- Account: Apttus__Account__c (lookup to Account)
- Start Date: Apttus__Contract_Start_Date__c
- End Date: Apttus__Contract_End_Date__c
- Total Value: Apttus__Total_Contract_Value__c
- Currency: CurrencyIsoCode (if multi-currency enabled)

Be helpful, concise, and focus on delivering actionable contract insights."""

    def chat(self, user_message: str) -> str:
        """Process user message and return agent response with tool execution."""
        try:
            # Add user message to conversation
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Start conversation loop
            messages = self.conversation_history.copy()

            while True:
                # Call Claude with tools
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=self.system_prompt,
                    messages=messages,
                    tools=self.tools.get_tool_definitions()
                )

                # Add Claude's response to messages
                assistant_message = {
                    "role": "assistant",
                    "content": response.content
                }
                messages.append(assistant_message)

                # Check if Claude wants to use tools
                tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

                if not tool_use_blocks:
                    # No tool use - return the text response
                    text_blocks = [block for block in response.content if block.type == "text"]
                    final_response = "\n".join([block.text for block in text_blocks])

                    # Update conversation history
                    self.conversation_history.append(assistant_message)

                    return final_response

                # Execute tools and collect results
                tool_results = []
                for tool_block in tool_use_blocks:
                    tool_name = tool_block.name
                    tool_input = tool_block.input
                    tool_use_id = tool_block.id

                    print(f"[AGENT] Executing tool: {tool_name}")
                    print(f"[AGENT] Tool input: {json.dumps(tool_input, indent=2)}")

                    try:
                        # Execute the tool
                        result = self.tools.execute_tool(tool_name, **tool_input)

                        print(f"[AGENT] Tool result preview: {str(result)[:200]}...")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result, indent=2, default=str)
                        })

                    except Exception as e:
                        print(f"[AGENT] Tool execution error: {str(e)}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps({
                                "success": False,
                                "error": f"Tool execution failed: {str(e)}"
                            }, indent=2)
                        })

                # Add tool results to conversation
                if tool_results:
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                # Continue the loop to let Claude process the tool results

        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            print(f"[AGENT] {error_msg}")
            return f"I encountered an error: {error_msg}"

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation history."

        summary = f"Conversation with {len(self.conversation_history)} messages:\n"
        for i, msg in enumerate(self.conversation_history[-5:], 1):  # Last 5 messages
            role = msg["role"].title()
            content = str(msg["content"])
            preview = content[:100] + "..." if len(content) > 100 else content
            summary += f"{i}. {role}: {preview}\n"

        return summary

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the agent and its components."""
        health = {
            "agent_status": "healthy",
            "anthropic_api": "unknown",
            "salesforce_api": "unknown",
            "tools_count": len(self.tools.get_tool_definitions()),
            "conversation_length": len(self.conversation_history),
            "errors": []
        }

        # Test Anthropic API
        try:
            test_response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            health["anthropic_api"] = "healthy"
        except Exception as e:
            health["anthropic_api"] = "error"
            health["errors"].append(f"Anthropic API: {str(e)}")

        # Test Salesforce API
        try:
            self.tools.client.authenticate()
            health["salesforce_api"] = "healthy"
        except Exception as e:
            health["salesforce_api"] = "error"
            health["errors"].append(f"Salesforce API: {str(e)}")

        if health["errors"]:
            health["agent_status"] = "degraded"

        return health