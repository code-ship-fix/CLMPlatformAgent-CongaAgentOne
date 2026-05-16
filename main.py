#!/usr/bin/env python3
"""
Conga CLM AI Agent - Interactive CLI Interface
A conversational AI agent for managing contracts in Conga CLM.
"""

import os
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import CongaAgent

# Initialize colorama for cross-platform colored output
init(autoreset=True)

def print_banner():
    """Print the application banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    🤖 Conga CLM AI Agent                    ║
║              Intelligent Contract Management                 ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}Welcome! I'm your AI assistant for managing contracts in Conga CLM.
I can help you create, search, and manage contracts using natural language.

Examples of what you can ask:
• "Create an MSA with Acme Corp for $50k starting next month"
• "Find all active contracts with TechCorp"
• "Activate contract abc123"
• "Show me contracts expiring this month"

Type 'help' for more commands or 'quit' to exit.{Style.RESET_ALL}
"""
    print(banner)

def print_help():
    """Print help information."""
    help_text = f"""
{Fore.YELLOW}Available Commands:{Style.RESET_ALL}
• {Fore.CYAN}help{Style.RESET_ALL} - Show this help message
• {Fore.CYAN}quit, exit{Style.RESET_ALL} - Exit the application
• {Fore.CYAN}clear{Style.RESET_ALL} - Clear conversation history
• {Fore.CYAN}status{Style.RESET_ALL} - Check agent health status
• {Fore.CYAN}history{Style.RESET_ALL} - Show conversation summary

{Fore.YELLOW}Natural Language Examples:{Style.RESET_ALL}
• "Create an MSA contract with Acme Corp starting March 1st for $100,000"
• "Search for all NDA contracts with TechCorp"
• "Find expiring contracts"
• "Activate contract ID abc123"
• "Show me details of contract xyz456"
• "Renew the Acme MSA"
• "What accounts are available for Microsoft?"

{Fore.YELLOW}Contract Types Available:{Style.RESET_ALL}
• MSA (Master Service Agreement)
• NDA (Non-Disclosure Agreement)
• SOW (Statement of Work)
• ORDER (Order Form)
• AMENDMENT (Contract Amendment)

{Fore.GREEN}Just type your request in natural language - I'll understand and help!{Style.RESET_ALL}
"""
    print(help_text)

def print_error(message: str):
    """Print error message in red."""
    print(f"{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")

def print_success(message: str):
    """Print success message in green."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Print info message in blue."""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")

def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def check_environment() -> bool:
    """Check if all required environment variables are set."""
    load_dotenv()

    required_vars = ['CONGA_CLIENT_ID', 'CONGA_CLIENT_SECRET', 'ANTHROPIC_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'your-{var.lower().replace("_", "-")}-here':
            missing_vars.append(var)

    if missing_vars:
        print_error("Missing or placeholder values for required environment variables:")
        for var in missing_vars:
            print(f"  • {var}")
        print("\nPlease update your .env file with actual credentials.")
        print("See .env.example for required format.")
        return False

    return True

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='Conga CLM AI Agent')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-banner', action='store_true', help='Skip banner display')
    args = parser.parse_args()

    # Check environment variables
    if not check_environment():
        sys.exit(1)

    # Show banner
    if not args.no_banner:
        print_banner()

    try:
        # Initialize agent
        print_info("Initializing AI agent...")
        agent = CongaAgent()

        # Perform health check
        health = agent.health_check()
        if health["status"] != "healthy":
            print_warning("Health check shows some issues:")
            if health.get("anthropic", {}).get("status") != "ok":
                print_error(f"Anthropic API: {health['anthropic'].get('error', 'Unknown error')}")
            if health.get("conga", {}).get("status") != "ok":
                print_error(f"Conga API: {health['conga'].get('error', 'Unknown error')}")

            response = input(f"{Fore.YELLOW}Continue anyway? (y/N): {Style.RESET_ALL}")
            if response.lower() != 'y':
                sys.exit(1)
        else:
            print_success("AI agent initialized successfully!")

        # Main interaction loop
        print(f"\n{Fore.GREEN}Ready to help! What would you like to do?{Style.RESET_ALL}")

        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.CYAN}You: {Style.RESET_ALL}").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Fore.GREEN}Thank you for using Conga CLM AI Agent. Goodbye!{Style.RESET_ALL}")
                    break

                elif user_input.lower() == 'help':
                    print_help()
                    continue

                elif user_input.lower() == 'clear':
                    agent.reset_conversation()
                    print_success("Conversation history cleared.")
                    continue

                elif user_input.lower() == 'status':
                    health = agent.health_check()
                    print(f"\n{Fore.BLUE}Agent Status:{Style.RESET_ALL}")
                    print(f"Overall: {health['status']}")
                    print(f"Anthropic API: {health['anthropic']['status']}")
                    print(f"Conga API: {health['conga']['status']}")
                    print(f"Available tools: {health['tools_count']}")
                    print(f"Conversation messages: {health['conversation_length']}")
                    continue

                elif user_input.lower() == 'history':
                    summary = agent.get_conversation_summary()
                    print(f"\n{Fore.BLUE}Conversation History:{Style.RESET_ALL}")
                    print(summary)
                    continue

                # Process user message with agent
                print(f"{Fore.MAGENTA}🤖 Agent: {Style.RESET_ALL}", end="", flush=True)
                response = agent.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted by user. Type 'quit' to exit gracefully.{Style.RESET_ALL}")
                continue

            except Exception as e:
                if args.debug:
                    import traceback
                    traceback.print_exc()
                print_error(f"Unexpected error: {str(e)}")
                continue

    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Thank you for using Conga CLM AI Agent. Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        print_error(f"Failed to start agent: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()