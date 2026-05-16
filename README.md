# 🤖 Conga CLM AI Agent - Web Edition

An intelligent, LLM-powered AI agent for managing contracts in Conga CLM platform. Features a modern web interface accessible from any browser, mobile-friendly design, and portable deployment for home/office use.

## 🌟 Features

- **🌐 Web-Based Chat Interface**: Modern, responsive chat UI accessible from any browser
- **📱 Mobile Friendly**: Works perfectly on phones, tablets, and desktops
- **🚀 One-Click Launch**: Simple startup scripts for Windows, Mac, and Linux
- **🏠 Portable**: Copy folder to any computer and run - no complex setup
- **🔄 Real-Time Communication**: WebSocket-powered instant messaging
- **🧠 Natural Language**: Talk to the agent in plain English
- **🔒 Secure**: OAuth2 authentication with automatic token refresh
- **⚡ Fast**: Optimized for quick responses and smooth experience

## 🏗️ Architecture

### Web Application Stack
- **Backend**: Flask + SocketIO for real-time communication
- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design
- **AI Engine**: Claude API (claude-sonnet-4-20250514) for natural language understanding
- **APIs**: Comprehensive Conga CLM REST API integration

### Agent Capabilities
- **CREATE CONTRACT**: "Create an MSA with Acme Corp for $50k starting March 1st"
- **SEARCH CONTRACTS**: "Find all active contracts with TechCorp"
- **CONTRACT LIFECYCLE**: "Activate contract abc123", "Renew the Acme MSA"
- **CONTRACT DETAILS**: "Show me details of contract abc123"
- **ACCOUNT SEARCH**: "Find accounts matching Microsoft"
- **GENERAL QUERIES**: "How many contracts are expiring this month?"

## 🚀 Quick Start (Web Interface)

### Option 1: One-Click Launch ⚡

#### Windows:
```bash
# Double-click start.bat or run:
start.bat
```

#### macOS/Linux:
```bash
# Double-click start.sh or run:
./start.sh
```

### Option 2: Manual Launch
```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start web server
python run.py
```

## 🌐 Access the Application

Once started, open your browser to:
- **Local**: `http://localhost:5000`
- **Network**: `http://your-ip:5000` (shown in console)
- **Mobile**: Use network URL on same WiFi

### Multi-Device Access:
- **Desktop**: Full-featured interface with all capabilities
- **Tablet**: Optimized touch interface
- **Phone**: Mobile-responsive chat interface
- **Multiple Users**: Each gets their own conversation session

## 📋 Environment Variables

Create a `.env` file with these variables:

```bash
# Conga CLM API Configuration
CONGA_CLIENT_ID=your-client-id-here
CONGA_CLIENT_SECRET=your-client-secret-here
CONGA_AUTH_URL=https://login-rlspreview.congacloud.com/api/v1/auth/connect/token
CONGA_BASE_URL=https://preview-rls09.congacloud.com

# Anthropic API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

## 🔧 Usage Examples

### Creating Contracts
```
You: Create an MSA with Acme Corp for $50,000 starting March 1st
Agent: I found 2 existing contracts with Acme Corp:
• MSA - Active - Created Jan 2024 (ID: contract123)
• NDA - Expired - Created June 2023 (ID: contract456)

Do you still want to create a new MSA contract? (yes/no)

You: yes
Agent: Created MSA contract "Acme Corp Master Service Agreement" (ID: abc123) starting March 1, 2024
```

### Searching Contracts
```
You: Find all contracts with TechCorp
Agent: Found 3 contracts with TechCorp:
• MSA - TechCorp Master Service Agreement (Active) - ID: xyz789
• NDA - TechCorp NDA (Active) - ID: def456
• SOW - Q1 Services Agreement (Completed) - ID: ghi123
```

### Contract Lifecycle Management
```
You: Activate contract abc123
Agent: Contract abc123 has been successfully activated. Status is now Active.
```

## 🛠️ Project Structure

```
conga-agent/
├── .env                      # Credentials (git-ignored)
├── .env.example              # Example configuration
├── .gitignore
├── requirements.txt
├── prompts/
│   └── system_prompt.txt     # Editable system prompt with business rules
├── src/
│   ├── __init__.py
│   ├── conga_client.py       # Conga API client with OAuth
│   ├── tools.py              # Tool definitions for Claude
│   ├── agent.py              # Main agent logic with Claude
│   └── utils.py              # Helper functions
├── main.py                   # Entry point - interactive chat
└── README.md
```

## 🤖 Available Commands

In the interactive CLI:

- `help` - Show help and examples
- `quit` or `exit` - Exit the application
- `clear` - Clear conversation history
- `status` - Check agent health status
- `history` - Show conversation summary

## 🔨 Available Contract Types

- **MSA** - Master Service Agreement
- **NDA** - Non-Disclosure Agreement
- **SOW** - Statement of Work
- **ORDER** - Order Form
- **AMENDMENT** - Contract Amendment

## 📡 Conga CLM APIs Used

### Contract Operations
- `POST /api/clm/v1/contracts` - Create contract
- `GET /api/clm/v1/contracts/{id}` - Get contract details
- `PUT /api/clm/v1/contracts/{id}` - Update contract
- `POST /api/clm/v1/contracts/query` - Search contracts

### Lifecycle Operations
- `POST /api/clm/v1/contracts/{id}/activate` - Activate
- `POST /api/clm/v1/contracts/{id}/renew` - Renew
- `POST /api/clm/v1/contracts/{id}/terminate` - Terminate
- `POST /api/clm/v1/contracts/{id}/amend` - Amend
- `POST /api/clm/v1/contracts/{id}/clone` - Clone

### Data Operations
- `POST /api/data/v1/account/query` - Search accounts
- `POST /api/clm/v1/templates/query` - Search templates

## ⚙️ Configuration

### Business Rules
Edit `prompts/system_prompt.txt` to customize:
- Business logic rules
- Validation requirements
- Response style
- Available contract types

### Tool Definitions
The agent uses these tools to interact with Conga:
- `search_contracts` - Find existing contracts
- `get_contract` - Get contract details
- `create_contract` - Create new contracts
- `update_contract` - Update contracts
- `lifecycle_action` - Perform lifecycle actions
- `search_accounts` - Find accounts
- `search_templates` - Find templates

## 🔍 Health Check

The agent includes a health check system:

```bash
python main.py
# In CLI, type: status
```

This checks:
- Anthropic API connectivity
- Conga API authentication
- Available tools count
- Conversation state

## 🐛 Debugging

Run with debug flag for detailed error information:

```bash
python main.py --debug
```

## 📝 Requirements

- Python 3.8+
- Anthropic API key
- Conga CLM client credentials
- Required Python packages (see requirements.txt)

## 🔐 Security

- Credentials stored in `.env` file (git-ignored)
- OAuth2 client credentials flow for Conga
- Automatic token refresh
- No hardcoded secrets

## 📚 Dependencies

- `anthropic` - Claude AI API client
- `requests` - HTTP client for Conga APIs
- `python-dotenv` - Environment variable management
- `colorama` - Cross-platform colored terminal text
- `pyyaml` - YAML configuration support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the health status: `status` command
2. Review error messages for API connectivity
3. Verify environment variables are set correctly
4. Check Conga CLM API documentation for endpoint changes

---

**Happy contract managing! 🎉**