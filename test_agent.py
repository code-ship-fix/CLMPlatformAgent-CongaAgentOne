#!/usr/bin/env python3
"""Test end-to-end agent functionality."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import SalesforceAgent

def test_agent():
    print('🧠 Testing end-to-end AI agent...')
    agent = SalesforceAgent()
    print('✅ Agent initialized successfully')

    print('\n🔥 Asking: "List my recent agreements"')
    response = agent.chat('List my recent agreements')

    print('\n✅ Response received:')
    print('=' * 50)
    print(response)
    print('=' * 50)

    return response

if __name__ == '__main__':
    test_agent()