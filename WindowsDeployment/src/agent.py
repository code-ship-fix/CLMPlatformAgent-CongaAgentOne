"""Main LLM-powered agent for Conga CLM interactions."""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from .tools import CongaTools
from .utils import load_system_prompt

class CongaAgent:
    """LLM-powered agent for intelligent Conga CLM interactions."""

    def __init__(self):
        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.anthropic = Anthropic(api_key=api_key)
        self.tools = CongaTools()
        self.system_prompt = load_system_prompt()
        self.conversation_history: List[Dict[str, Any]] = []
        self.model = "claude-sonnet-4-20250514"

    def chat(self, user_message: str) -> str:
        """Process user message and return agent response."""
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Log the LLM request
            self._log_llm_request(user_message)

            # Create message with tool definitions
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                tools=self.tools.get_tool_definitions()
            )

            # Log the LLM response
            self._log_llm_response(response)

            # Process response
            assistant_message = {"role": "assistant", "content": []}
            response_text = ""

            for content_block in response.content:
                if content_block.type == "text":
                    response_text += content_block.text
                    assistant_message["content"].append({
                        "type": "text",
                        "text": content_block.text
                    })
                elif content_block.type == "tool_use":
                    # Execute the tool
                    tool_result = self.tools.execute_tool(
                        content_block.name,
                        content_block.input
                    )

                    # Log tool execution
                    self._log_tool_execution(content_block.name, content_block.input, tool_result)

                    # Add tool use to conversation
                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input
                    })

                    # Add tool result to conversation
                    tool_result_message = {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": json.dumps(tool_result)
                            }
                        ]
                    }

                    # Add assistant message and tool result to history
                    self.conversation_history.append(assistant_message)
                    self.conversation_history.append(tool_result_message)

                    # Get follow-up response from Claude
                    follow_up_response = self.anthropic.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        system=self.system_prompt,
                        messages=self.conversation_history,
                        tools=self.tools.get_tool_definitions()
                    )

                    # Process follow-up response
                    return self._process_follow_up_response(follow_up_response)

            # Add assistant response to history if no tools were used
            if assistant_message["content"]:
                self.conversation_history.append(assistant_message)

            return response_text.strip() if response_text else "I'm sorry, I couldn't process that request."

        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            # Add error to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            return error_msg

    def _process_follow_up_response(self, response) -> str:
        """Process follow-up response that may contain more tool calls."""
        response_text = ""
        assistant_message = {"role": "assistant", "content": []}

        for content_block in response.content:
            if content_block.type == "text":
                response_text += content_block.text
                assistant_message["content"].append({
                    "type": "text",
                    "text": content_block.text
                })
            elif content_block.type == "tool_use":
                # Handle additional tool calls recursively
                tool_result = self.tools.execute_tool(
                    content_block.name,
                    content_block.input
                )

                assistant_message["content"].append({
                    "type": "tool_use",
                    "id": content_block.id,
                    "name": content_block.name,
                    "input": content_block.input
                })

                tool_result_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": json.dumps(tool_result)
                        }
                    ]
                }

                self.conversation_history.append(assistant_message)
                self.conversation_history.append(tool_result_message)

                # Get final response
                final_response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    messages=self.conversation_history,
                    tools=self.tools.get_tool_definitions()
                )

                # Extract text from final response
                final_text = ""
                final_assistant_message = {"role": "assistant", "content": []}

                for final_block in final_response.content:
                    if final_block.type == "text":
                        final_text += final_block.text
                        final_assistant_message["content"].append({
                            "type": "text",
                            "text": final_block.text
                        })

                if final_assistant_message["content"]:
                    self.conversation_history.append(final_assistant_message)

                return final_text.strip()

        # Add to history if no additional tool calls
        if assistant_message["content"]:
            self.conversation_history.append(assistant_message)

        return response_text.strip()

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation history."

        summary_parts = []
        for i, message in enumerate(self.conversation_history, 1):
            role = message["role"].title()

            if isinstance(message["content"], str):
                content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
            elif isinstance(message["content"], list):
                text_parts = []
                for part in message["content"]:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, dict) and part.get("type") == "tool_use":
                        text_parts.append(f"[Tool: {part.get('name', 'unknown')}]")
                content = " ".join(text_parts)
                content = content[:100] + "..." if len(content) > 100 else content
            else:
                content = str(message["content"])[:100]

            summary_parts.append(f"{i}. {role}: {content}")

        return "\n".join(summary_parts)

    def update_system_prompt(self, new_prompt: str):
        """Update the system prompt."""
        self.system_prompt = new_prompt

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool["name"] for tool in self.tools.get_tool_definitions()]

    def _log_llm_request(self, user_message: str):
        """Log the LLM request details."""
        print(f"\n[LLM REQUEST] ================")
        print(f"Model: {self.model}")
        print(f"User Message: {user_message}")
        print(f"System Prompt (first 200 chars): {self.system_prompt[:200]}...")
        print(f"Conversation Length: {len(self.conversation_history)}")
        print(f"Available Tools: {len(self.tools.get_tool_definitions())}")
        tool_names = [tool['name'] for tool in self.tools.get_tool_definitions()]
        print(f"Tool Names: {tool_names}")
        print(f"[LLM REQUEST] ================\n")

    def _log_llm_response(self, response):
        """Log the LLM response details."""
        print(f"\n[LLM RESPONSE] ================")
        print(f"Response ID: {getattr(response, 'id', 'N/A')}")
        print(f"Model Used: {getattr(response, 'model', 'N/A')}")
        print(f"Usage: {getattr(response, 'usage', 'N/A')}")

        if hasattr(response, 'content'):
            for i, content_block in enumerate(response.content):
                print(f"Content Block {i}: {content_block.type}")
                if content_block.type == "text":
                    print(f"Text Content: {content_block.text[:200]}...")
                elif content_block.type == "tool_use":
                    print(f"Tool: {content_block.name}")
                    print(f"Tool Input: {content_block.input}")
        print(f"[LLM RESPONSE] ================\n")

    def _log_tool_execution(self, tool_name: str, parameters: dict, result: dict):
        """Log tool execution details."""
        print(f"\n[TOOL EXECUTION] ================")
        print(f"Tool: {tool_name}")
        print(f"Parameters: {parameters}")
        print(f"Result Success: {result.get('success', 'Unknown')}")
        print(f"Result Message: {result.get('message', 'No message')}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        if 'raw_response' in result:
            print(f"Raw API Response: {result['raw_response']}")
        print(f"[TOOL EXECUTION] ================\n")

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent components."""
        try:
            # Test Anthropic connection
            anthropic_ok = True
            anthropic_error = None
            try:
                test_response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                if not test_response:
                    anthropic_ok = False
                    anthropic_error = "No response from Anthropic API"
            except Exception as e:
                anthropic_ok = False
                anthropic_error = str(e)

            # Test Conga connection
            conga_ok = True
            conga_error = None
            try:
                self.tools.client.authenticate()
            except Exception as e:
                conga_ok = False
                conga_error = str(e)

            return {
                "status": "healthy" if anthropic_ok and conga_ok else "unhealthy",
                "anthropic": {
                    "status": "ok" if anthropic_ok else "error",
                    "model": self.model,
                    "error": anthropic_error
                },
                "conga": {
                    "status": "ok" if conga_ok else "error",
                    "error": conga_error
                },
                "tools_count": len(self.get_available_tools()),
                "conversation_length": len(self.conversation_history)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }