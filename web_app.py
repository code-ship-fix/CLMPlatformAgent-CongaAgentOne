#!/usr/bin/env python3
"""
Salesforce Conga CLM AI Agent - Web Application
A real-time web-based conversational AI agent for managing Conga CLM agreements in Salesforce.
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import SalesforceAgent

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'salesforce-conga-clm-ai-agent-secret-key-change-in-production')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active agents per session
active_agents: Dict[str, SalesforceAgent] = {}

def get_or_create_agent(session_id: str) -> SalesforceAgent:
    """Get or create an agent for the given session."""
    if session_id not in active_agents:
        try:
            active_agents[session_id] = SalesforceAgent()
            print(f"[WEB] Created new agent for session: {session_id}")
        except Exception as e:
            raise Exception(f"Failed to initialize Salesforce agent: {str(e)}")
    return active_agents[session_id]

def cleanup_agent(session_id: str):
    """Clean up agent for the given session."""
    if session_id in active_agents:
        del active_agents[session_id]
        print(f"[WEB] Cleaned up agent for session: {session_id}")

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Try to create a test agent to verify everything works
        test_agent = SalesforceAgent()
        health_status = test_agent.health_check()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'active_sessions': len(active_agents),
            'agent_health': health_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    join_room(session_id)
    print(f"[WEB] Client connected: {session_id}")

    # Send welcome message
    emit('message', {
        'type': 'system',
        'content': 'Connected to Salesforce Conga CLM AI Agent. Ask me anything about your agreements!',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = session.get('session_id')
    if session_id:
        leave_room(session_id)
        print(f"[WEB] Client disconnected: {session_id}")

@socketio.on('user_message')
def handle_user_message(data):
    """Handle user message and get AI response."""
    session_id = session.get('session_id')
    if not session_id:
        emit('error', {'message': 'No session ID found'})
        return

    user_message = data.get('message', '').strip()
    if not user_message:
        emit('error', {'message': 'Empty message'})
        return

    try:
        # Echo user message back
        emit('message', {
            'type': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })

        # Show typing indicator
        emit('typing', {'is_typing': True})

        print(f"[WEB] Processing message for session {session_id}: {user_message}")

        # Get or create agent for this session
        agent = get_or_create_agent(session_id)

        # Handle special commands
        if user_message.lower() == 'clear':
            agent.clear_history()
            emit('typing', {'is_typing': False})
            emit('message', {
                'type': 'system',
                'content': '🧹 Conversation history cleared!',
                'timestamp': datetime.now().isoformat()
            })
            return

        elif user_message.lower() == 'health':
            health_status = agent.health_check()
            emit('typing', {'is_typing': False})

            status_msg = f"""🏥 **System Health Check**

**Agent Status:** {health_status['agent_status']}
**Anthropic API:** {health_status['anthropic_api']}
**Salesforce API:** {health_status['salesforce_api']}
**Available Tools:** {health_status['tools_count']}
**Conversation Length:** {health_status['conversation_length']} messages

{('⚠️ **Errors:**\\n' + '\\n'.join(f'• {error}' for error in health_status['errors'])) if health_status['errors'] else '✅ All systems operational!'}"""

            emit('message', {
                'type': 'assistant',
                'content': status_msg,
                'timestamp': datetime.now().isoformat()
            })
            return

        elif user_message.lower() == 'help':
            help_msg = """💡 **Sample Questions You Can Ask:**

**🔍 Search & Discovery:**
• List my 5 most recent agreements
• Show me agreements expiring in the next 30 days
• Find all agreements with Microsoft
• What agreements are in 'In Effect' status?

**💰 Value & Analysis:**
• Show me agreements over $100,000
• What's the total value of all active agreements?
• Which agreements have the highest contract value?

**📋 Details & Information:**
• Get details for agreement [agreement ID]
• What fields are available for agreements?
• Show me agreement clauses for [agreement ID]

**🔧 Utility Commands:**
• `clear` - Clear conversation history
• `health` - Check system status
• `help` - Show this help message

Just ask in natural language - I'll figure out what you need!"""

            emit('typing', {'is_typing': False})
            emit('message', {
                'type': 'assistant',
                'content': help_msg,
                'timestamp': datetime.now().isoformat()
            })
            return

        # Process message with AI agent
        response = agent.chat(user_message)

        # Send AI response
        emit('typing', {'is_typing': False})
        emit('message', {
            'type': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })

        print(f"[WEB] Response sent for session {session_id}")

    except Exception as e:
        print(f"[WEB] Error processing message: {str(e)}")
        emit('typing', {'is_typing': False})
        emit('message', {
            'type': 'error',
            'content': f'Sorry, I encountered an error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('clear_history')
def handle_clear_history():
    """Clear conversation history for the current session."""
    session_id = session.get('session_id')
    if session_id and session_id in active_agents:
        active_agents[session_id].clear_history()
        emit('message', {
            'type': 'system',
            'content': '🧹 Conversation history cleared!',
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🚀 Starting Salesforce Conga CLM AI Agent Web Server...")
    print("🌐 Access the application at: http://localhost:8080")
    print("💡 Use Ctrl+C to stop the server")

    # Verify environment setup
    required_vars = ['SF_CLIENT_ID', 'SF_CLIENT_SECRET', 'SF_INSTANCE_URL', 'ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and run test_sf_auth.py first")
        sys.exit(1)

    try:
        # Test basic connectivity
        test_agent = SalesforceAgent()
        print("✅ Salesforce agent initialized successfully")

        # Start the web server
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)

    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        print("Please run test_sf_auth.py to diagnose the issue")
        sys.exit(1)