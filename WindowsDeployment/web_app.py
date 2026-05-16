#!/usr/bin/env python3
"""
Conga CLM AI Agent - Web Application
A web-based conversational AI agent for managing contracts in Conga CLM.
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

from src.agent import CongaAgent

# Load environment variables
load_dotenv()

# Initialize Flask app with correct template and static folders
app = Flask(__name__,
           template_folder='web/templates',
           static_folder='web/static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'conga-clm-ai-agent-secret-key-change-in-production')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active agents per session
active_agents: Dict[str, CongaAgent] = {}

def get_or_create_agent(session_id: str) -> CongaAgent:
    """Get or create an agent for the given session."""
    if session_id not in active_agents:
        try:
            active_agents[session_id] = CongaAgent()
        except Exception as e:
            raise Exception(f"Failed to initialize agent: {str(e)}")
    return active_agents[session_id]

def cleanup_agent(session_id: str):
    """Clean up agent for the given session."""
    if session_id in active_agents:
        del active_agents[session_id]

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chat.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Create a temporary agent to test connections
        temp_agent = CongaAgent()
        health_status = temp_agent.health_check()
        return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """REST API endpoint for chat (fallback if WebSocket fails)."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        agent = get_or_create_agent(session_id)
        response = agent.chat(data['message'])

        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset conversation history."""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in active_agents:
            active_agents[session_id].reset_conversation()
            return jsonify({'message': 'Conversation reset successfully'})
        return jsonify({'message': 'No active conversation to reset'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """Get agent status."""
    try:
        session_id = session.get('session_id')
        if session_id and session_id in active_agents:
            status = active_agents[session_id].health_check()
            return jsonify(status)
        return jsonify({'message': 'No active agent session'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-auth')
def test_auth():
    """Test Conga authentication and API access."""
    try:
        from src.conga_client import CongaClient

        client = CongaClient()

        # Test authentication
        client.authenticate()

        # Test a simple API call
        try:
            result = client.search_accounts("test")
            return jsonify({
                'auth_status': 'success',
                'api_test': 'success',
                'account_search_result': result,
                'message': 'Authentication and API access working'
            })
        except Exception as api_error:
            return jsonify({
                'auth_status': 'success',
                'api_test': 'failed',
                'api_error': str(api_error),
                'message': 'Authentication works but API call failed'
            })

    except Exception as auth_error:
        return jsonify({
            'auth_status': 'failed',
            'auth_error': str(auth_error),
            'message': 'Authentication failed'
        }), 401

# WebSocket Events
@socketio.on('connect')
def on_connect():
    """Handle client connection."""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    join_room(session_id)

    emit('connected', {
        'session_id': session_id,
        'message': 'Connected to Conga CLM AI Agent',
        'timestamp': datetime.now().isoformat()
    })

    # Send welcome message
    welcome_message = """🤖 **Welcome to Conga CLM AI Agent!**

I'm your intelligent assistant for managing contracts in Conga CLM. I can help you:

• **Create contracts**: "Create an MSA with Acme Corp for $50k"
• **Search contracts**: "Find all active contracts with TechCorp"
• **Lifecycle management**: "Activate contract abc123"
• **Get contract details**: "Show me contract abc123"
• **Search accounts**: "Find accounts matching Microsoft"

Just type your request in natural language and I'll help you out!

*Type 'help' for more commands or examples.*"""

    emit('bot_message', {
        'message': welcome_message,
        'timestamp': datetime.now().isoformat(),
        'type': 'welcome'
    })

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection."""
    session_id = session.get('session_id')
    if session_id:
        leave_room(session_id)
        # Don't immediately cleanup - keep session for potential reconnection
        # cleanup_agent(session_id)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle incoming chat messages."""
    try:
        session_id = session.get('session_id')
        if not session_id:
            emit('error', {'message': 'No active session'})
            return

        message = data.get('message', '').strip()
        if not message:
            emit('error', {'message': 'Empty message'})
            return

        # Emit debug info to client
        emit('debug_log', {
            'type': 'info',
            'category': 'SERVER',
            'message': f'Processing message: "{message}"',
            'data': {'session_id': session_id, 'timestamp': datetime.now().isoformat()}
        })

        # Handle special commands
        if message.lower() in ['help', '/help']:
            help_message = """**Available Commands:**

🔹 **help** - Show this help message
🔹 **clear** - Clear conversation history
🔹 **status** - Check agent health status

**Natural Language Examples:**

• "Create an MSA contract with Acme Corp starting March 1st for $100,000"
• "Search for all NDA contracts with TechCorp"
• "Find expiring contracts"
• "Activate contract ID abc123"
• "Show me details of contract xyz456"
• "Renew the Acme MSA"
• "What accounts are available for Microsoft?"

**Contract Types:**
• MSA (Master Service Agreement)
• NDA (Non-Disclosure Agreement)
• SOW (Statement of Work)
• ORDER (Order Form)
• AMENDMENT (Contract Amendment)

Just describe what you want to do in plain English!"""

            emit('bot_message', {
                'message': help_message,
                'timestamp': datetime.now().isoformat(),
                'type': 'help'
            })
            return

        elif message.lower() in ['clear', '/clear']:
            if session_id in active_agents:
                active_agents[session_id].reset_conversation()
            emit('conversation_cleared', {
                'message': 'Conversation history cleared.',
                'timestamp': datetime.now().isoformat()
            })
            return

        elif message.lower() in ['status', '/status']:
            if session_id in active_agents:
                status = active_agents[session_id].health_check()
                status_message = f"""**Agent Status:**

• Overall: {status['status'].title()}
• Anthropic API: {status['anthropic']['status'].upper()}
• Conga API: {status['conga']['status'].upper()}
• Available Tools: {status['tools_count']}
• Conversation Messages: {status['conversation_length']}"""

                emit('bot_message', {
                    'message': status_message,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'status'
                })
            else:
                emit('bot_message', {
                    'message': 'No active agent session.',
                    'timestamp': datetime.now().isoformat(),
                    'type': 'status'
                })
            return

        # Process with AI agent
        emit('typing', {'typing': True})

        try:
            agent = get_or_create_agent(session_id)

            # Log before LLM call
            emit('debug_log', {
                'type': 'info',
                'category': 'LLM_START',
                'message': f'Starting LLM processing for: "{message}"',
                'data': {'agent_id': id(agent), 'conversation_length': len(agent.conversation_history)}
            })

            response = agent.chat(message)

            # Log after LLM call
            emit('debug_log', {
                'type': 'info',
                'category': 'LLM_COMPLETE',
                'message': f'LLM processing complete',
                'data': {'response_length': len(response), 'conversation_length': len(agent.conversation_history)}
            })

            emit('typing', {'typing': False})
            emit('bot_message', {
                'message': response,
                'timestamp': datetime.now().isoformat(),
                'type': 'response'
            })

        except Exception as e:
            emit('debug_log', {
                'type': 'error',
                'category': 'LLM_ERROR',
                'message': f'LLM processing failed: {str(e)}',
                'data': {'error': str(e), 'type': type(e).__name__}
            })

            emit('typing', {'typing': False})
            emit('error', {
                'message': f'Error processing request: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        emit('error', {
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection keep-alive."""
    emit('pong')

if __name__ == '__main__':
    # Check environment
    required_vars = ['CONGA_CLIENT_ID', 'CONGA_CLIENT_SECRET', 'ANTHROPIC_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f'your-{var.lower().replace("_", "-")}-here':
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\nPlease update your .env file with actual credentials.")
        sys.exit(1)

    print("🚀 Starting Conga CLM AI Agent Web Server...")
    print("🌐 Access the application at: http://localhost:8080")
    print("💡 Use Ctrl+C to stop the server")

    # Run with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',  # Allow external connections
        port=8080,
        debug=False,
        allow_unsafe_werkzeug=True
    )