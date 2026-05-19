# 🤖 Salesforce Conga CLM AI Agent

An intelligent AI agent for managing Conga CLM agreements in Salesforce. Chat with your agreements using natural language through Claude AI.

## 🌟 Features

- **🧠 Natural Language Interface**: Ask questions in plain English about your agreements
- **🔍 Smart Search**: Find agreements by status, account, dates, value ranges, and more
- **📊 Analytics & Insights**: Get summaries, totals, and trend analysis
- **🔗 Salesforce Integration**: Works directly with your Salesforce org and Conga CLM data
- **⚡ Fast SOQL Queries**: Optimized queries with automatic pagination
- **🛡️ Secure Authentication**: OAuth2 Client Credentials flow with no stored passwords

## 🏗️ Architecture

### Authentication Model
- **OAuth2 Client Credentials Flow** via Salesforce External Client App
- No username/password required - just Client ID and Secret
- Direct API connections to your Salesforce org

### Data Integration
- **Salesforce Objects**: `Apttus__APTS_Agreement__c` (agreements) and related objects
- **SOQL Queries**: Intelligent query generation from natural language
- **Real-time Access**: Live data from your Salesforce org

### AI Engine
- **Claude 3.5 Sonnet**: Advanced language model for understanding and generating responses
- **Function Calling**: Seamless integration between AI and Salesforce APIs
- **Context Awareness**: Maintains conversation context for follow-up questions

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- Salesforce org with Conga CLM
- External Client App configured in Salesforce
- Anthropic API key

### 2. Setup Environment Variables

Create a `.env` file:

```bash
# Salesforce Configuration
SF_CLIENT_ID=your_connected_app_client_id
SF_CLIENT_SECRET=your_connected_app_client_secret
SF_INSTANCE_URL=https://yourorg.my.salesforce.com
SF_API_VERSION=v62.0
SF_AGREEMENT_OBJECT=Apttus__APTS_Agreement__c

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Authentication

```bash
python test_sf_auth.py
```

This will verify your Salesforce credentials and show sample agreements.

### 5. Start Chatting

```bash
python chat.py
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SF_CLIENT_ID` | External Client App Consumer Key | `3MVG9t8TL3jEkA4i...` |
| `SF_CLIENT_SECRET` | External Client App Consumer Secret | `6C29530195F51B59...` |
| `SF_INSTANCE_URL` | Your Salesforce instance URL | `https://yourorg.my.salesforce.com` |
| `SF_API_VERSION` | Salesforce API version (optional) | `v62.0` |
| `SF_AGREEMENT_OBJECT` | Agreement object API name (optional) | `Apttus__APTS_Agreement__c` |
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-api03-...` |

### Salesforce Setup

1. **Create External Client App**:
   - Setup → App Manager → New Connected App
   - Enable OAuth settings
   - Grant `api` and `refresh_token` scopes
   - Enable Client Credentials Flow

2. **Grant Permissions**:
   - Assign API access to the integration user
   - Ensure Conga CLM object permissions
   - Test with Workbench or similar tool

## 💬 Sample Queries

### Search & Discovery
```
• List my 5 most recent agreements
• Show me agreements expiring in the next 30 days
• Find all agreements with Microsoft
• What agreements are in 'In Effect' status?
```

### Value & Analysis
```
• Show me agreements over $100,000
• What's the total value of all active agreements?
• Which agreements have the highest contract value?
• Find agreements that started this year
```

### Details & Information
```
• Get details for agreement [agreement ID]
• What fields are available for agreements?
• Show me agreement clauses for [agreement ID]
• What's the status of agreement ABC-123?
```

### Custom Queries
```
• Run this SOQL: SELECT Name, Apttus__Status__c FROM Apttus__APTS_Agreement__c LIMIT 5
• Find expired agreements from last quarter
• Show me all amendments created this month
```

## 🛠️ Available Tools

The agent has access to these specialized tools:

- **`search_agreements`** - Find agreements by filters (status, account, dates, value)
- **`get_agreement_details`** - Get full details for a specific agreement ID
- **`run_soql`** - Execute custom SOQL SELECT queries
- **`list_agreement_fields`** - Discover available fields and their types
- **`create_agreement`** - Create new agreements
- **`update_agreement`** - Update existing agreements

## 📋 CLI Commands

In the chat interface:

- `help` - Show sample queries and usage tips
- `health` - Check system status and API connectivity
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the application

## 🎯 Field Mappings

Common Conga CLM field mappings:

| Display Name | API Name | Description |
|--------------|----------|-------------|
| Agreement Number | `Name` | Unique agreement identifier |
| Status | `Apttus__Status__c` | Current agreement status |
| Status Category | `Apttus__Status_Category__c` | Lifecycle stage |
| Account | `Apttus__Account__c` | Related account (lookup) |
| Start Date | `Apttus__Contract_Start_Date__c` | Agreement start date |
| End Date | `Apttus__Contract_End_Date__c` | Agreement end date |
| Total Value | `Apttus__Total_Contract_Value__c` | Total contract value |
| Currency | `CurrencyIsoCode` | Currency code (if multi-currency) |

## 🔍 Troubleshooting

### Authentication Issues
1. Run `python test_sf_auth.py` first
2. Verify External Client App configuration
3. Check API permissions for the integration user
4. Ensure Client Credentials Flow is enabled

### Query Issues
1. Use `list_agreement_fields` to discover available fields
2. Check object permissions in Salesforce
3. Verify SOQL syntax with Workbench

### API Errors
- **401 Unauthorized**: Invalid Client ID/Secret
- **403 Forbidden**: Insufficient permissions
- **INVALID_SESSION_ID**: Token expired (auto-handled)

## 🏥 Health Check

```bash
python chat.py
> health
```

This checks:
- Anthropic API connectivity
- Salesforce API authentication
- Available tools count
- Conversation state

## 📝 Development

### Project Structure
```
├── src/
│   ├── sf_client.py       # Salesforce REST API client
│   ├── tools.py           # AI tool definitions
│   └── agent.py           # Claude AI agent
├── test_sf_auth.py        # Authentication test script
├── chat.py                # Interactive CLI
├── .env                   # Configuration (git-ignored)
└── requirements.txt       # Python dependencies
```

### Adding Custom Tools
1. Add tool definition to `src/tools.py`
2. Implement the tool method
3. Update the `execute_tool` dispatcher
4. The agent will automatically discover and use new tools

## 🔐 Security

- **No Persistent Credentials**: Uses OAuth2 client credentials flow
- **Session-based Authentication**: Tokens auto-refresh as needed
- **SOQL Injection Protection**: Query validation and sanitization
- **Read-only by Default**: Custom tools prevent destructive operations

## 🤝 Support

For issues or questions:
1. Check the health status: run `health` command
2. Verify authentication with `python test_sf_auth.py`
3. Review Salesforce API permissions
4. Check logs for detailed error messages

---

**Happy agreement management! 🎉**