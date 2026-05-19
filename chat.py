#!/usr/bin/env python3
"""Interactive CLI for Salesforce Conga CLM AI Agent."""

import os
import sys
import signal
import readline
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import SalesforceAgent


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n👋 Goodbye!")
    sys.exit(0)


def print_banner():
    """Print the welcome banner."""
    print("🤖 Salesforce Conga CLM AI Agent")
    print("=" * 40)
    print("Ask me anything about your agreements!")
    print("Type 'quit', 'exit', or Ctrl+C to exit")
    print("Type 'help' for sample queries")
    print("Type 'clear' to clear conversation history")
    print("Type 'health' to check system status")
    print("-" * 40)


def print_help():
    """Print help message with sample queries."""
    print("\n💡 Sample Questions You Can Ask:")
    print("=" * 40)
    print("📊 Search & Discovery:")
    print("  • List my 5 most recent agreements")
    print("  • Show me agreements expiring in the next 30 days")
    print("  • Find all agreements with Microsoft")
    print("  • What agreements are in 'In Effect' status?")
    print("")
    print("💰 Value & Analysis:")
    print("  • Show me agreements over $100,000")
    print("  • What's the total value of all active agreements?")
    print("  • Which agreements have the highest contract value?")
    print("")
    print("📋 Details & Information:")
    print("  • Get details for agreement [paste agreement ID here]")
    print("  • What fields are available for agreements?")
    print("  • Show me agreement clauses for [agreement ID]")
    print("")
    print("🔍 Custom Queries:")
    print("  • Run this SOQL: SELECT Name, Apttus__Status__c FROM Apttus__APTS_Agreement__c LIMIT 5")
    print("  • Find agreements that started this year")
    print("  • Show expired agreements from last quarter")
    print("-" * 40)


def main():
    """Main CLI loop."""
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Load environment variables
    load_dotenv()

    # Print banner
    print_banner()

    # Initialize agent
    try:
        print("🔧 Initializing agent...")
        agent = SalesforceAgent()
        print("✅ Agent ready!")
        print()

    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\nPlease check:")
        print("1. Your .env file has valid credentials")
        print("2. Run 'python test_sf_auth.py' first to test connectivity")
        sys.exit(1)

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye!")
                break

            elif user_input.lower() == 'help':
                print_help()
                continue

            elif user_input.lower() == 'clear':
                agent.clear_history()
                print("🧹 Conversation history cleared!")
                continue

            elif user_input.lower() == 'health':
                print("\n🏥 Running health check...")
                health = agent.health_check()

                print(f"Agent Status: {health['agent_status']}")
                print(f"Anthropic API: {health['anthropic_api']}")
                print(f"Salesforce API: {health['salesforce_api']}")
                print(f"Available Tools: {health['tools_count']}")
                print(f"Conversation Length: {health['conversation_length']} messages")

                if health['errors']:
                    print("\n❌ Errors detected:")
                    for error in health['errors']:
                        print(f"  • {error}")
                else:
                    print("✅ All systems healthy!")
                continue

            # Process user message with the agent
            print("🤔 Thinking...")

            response = agent.chat(user_input)

            # Print the response
            print("\n🤖 Agent:")
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

        except EOFError:
            print("\n\n👋 Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Try asking again or type 'help' for sample queries.")


if __name__ == "__main__":
    main()