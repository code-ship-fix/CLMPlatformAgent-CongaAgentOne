/**
 * Conga CLM AI Assistant - Background Service Worker
 * Handles secure API communications
 */

class CongaAIBackground {
  constructor() {
    this.initializeMessageHandler();
  }

  initializeMessageHandler() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep message channel open for async response
    });
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'testCongaAuth':
          const congaResult = await this.testCongaAuthentication(message.data);
          sendResponse(congaResult);
          break;

        case 'testAnthropicAuth':
          const anthropicResult = await this.testAnthropicAuthentication(message.data.apiKey);
          sendResponse(anthropicResult);
          break;

        case 'processQuery':
          const queryResult = await this.processUserQuery(message.data);
          sendResponse(queryResult);
          break;

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Background script error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async testCongaAuthentication(credentials) {
    try {
      console.log('Testing Conga authentication...');

      // Authenticate with Conga OAuth2
      const authResponse = await fetch(credentials.authUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: credentials.clientId,
          client_secret: credentials.clientSecret
        })
      });

      if (!authResponse.ok) {
        throw new Error(`Conga auth failed: ${authResponse.status} - ${authResponse.statusText}`);
      }

      const authData = await authResponse.json();
      if (!authData.access_token) {
        throw new Error('No access token received from Conga');
      }

      console.log('✅ Conga authentication successful');
      return { success: true, message: 'Conga authentication successful' };

    } catch (error) {
      console.error('❌ Conga authentication failed:', error);
      return { success: false, error: error.message };
    }
  }

  async testAnthropicAuthentication(apiKey) {
    try {
      console.log('Testing Anthropic authentication...');

      // Test with a minimal request
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-3-sonnet-20240229',
          max_tokens: 10,
          messages: [{ role: 'user', content: 'Hi' }]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Anthropic auth failed: ${response.status} - ${errorData.error?.message || response.statusText}`);
      }

      console.log('✅ Anthropic authentication successful');
      return { success: true, message: 'Anthropic authentication successful' };

    } catch (error) {
      console.error('❌ Anthropic authentication failed:', error);
      return { success: false, error: error.message };
    }
  }

  async processUserQuery(data) {
    try {
      const { query, credentials } = data;
      console.log('Processing user query:', query);

      // First, get Conga access token
      const accessToken = await this.getCongaAccessToken(credentials);

      // Initialize the AI tools with credentials
      const aiTools = new CongaAITools(credentials, accessToken);

      // Process the query with Claude
      const result = await aiTools.processQuery(query);

      return { success: true, result };

    } catch (error) {
      console.error('Query processing error:', error);
      return { success: false, error: error.message };
    }
  }

  async getCongaAccessToken(credentials) {
    const authResponse = await fetch(credentials.authUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: credentials.clientId,
        client_secret: credentials.clientSecret
      })
    });

    if (!authResponse.ok) {
      throw new Error(`Failed to get access token: ${authResponse.status}`);
    }

    const authData = await authResponse.json();
    return authData.access_token;
  }
}

/**
 * AI Tools for Conga CLM Integration
 */
class CongaAITools {
  constructor(credentials, accessToken) {
    this.credentials = credentials;
    this.accessToken = accessToken;
    this.baseUrl = credentials.baseUrl;
  }

  async processQuery(query) {
    // Define available tools for Claude
    const tools = [
      {
        name: "search_contracts",
        description: "Search for contracts in Conga CLM",
        input_schema: {
          type: "object",
          properties: {
            account_name: { type: "string", description: "Account name to search for" },
            contract_type: { type: "string", description: "Contract type (MSA, NDA, etc.)" },
            status: { type: "string", description: "Contract status" }
          }
        }
      },
      {
        name: "get_contract",
        description: "Get details of a specific contract by ID",
        input_schema: {
          type: "object",
          properties: {
            contract_id: { type: "string", description: "Contract ID" }
          },
          required: ["contract_id"]
        }
      },
      {
        name: "search_accounts",
        description: "Search for accounts in Conga CLM",
        input_schema: {
          type: "object",
          properties: {
            name: { type: "string", description: "Account name to search for" }
          },
          required: ["name"]
        }
      }
    ];

    // Send query to Claude with tools
    const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.credentials.anthropicKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 2000,
        system: `You are a helpful AI assistant for managing contracts in Conga CLM.
        You can search contracts, get contract details, and search accounts.
        Always be helpful and provide clear, actionable responses.`,
        messages: [{ role: 'user', content: query }],
        tools: tools
      })
    });

    if (!claudeResponse.ok) {
      throw new Error(`Claude API error: ${claudeResponse.status}`);
    }

    const claudeData = await claudeResponse.json();

    // Process any tool calls
    let response = '';
    for (const content of claudeData.content) {
      if (content.type === 'text') {
        response += content.text;
      } else if (content.type === 'tool_use') {
        const toolResult = await this.executeTool(content.name, content.input);

        // Send tool result back to Claude for final response
        const followUpResponse = await this.getFollowUpResponse(claudeData.content, toolResult, content.id);
        response += followUpResponse;
      }
    }

    return response || "I processed your request, but didn't generate a text response.";
  }

  async executeTool(toolName, parameters) {
    try {
      switch (toolName) {
        case 'search_contracts':
          return await this.searchContracts(parameters);
        case 'get_contract':
          return await this.getContract(parameters);
        case 'search_accounts':
          return await this.searchAccounts(parameters);
        default:
          return { error: `Unknown tool: ${toolName}` };
      }
    } catch (error) {
      return { error: error.message };
    }
  }

  async searchContracts(params) {
    const query = {
      pageSize: 10,
      filters: []
    };

    if (params.account_name) {
      query.filters.push({
        field: "Account.Name",
        operator: "equals",
        value: params.account_name
      });
    }

    if (params.contract_type) {
      query.filters.push({
        field: "ContractType",
        operator: "equals",
        value: params.contract_type
      });
    }

    if (params.status) {
      query.filters.push({
        field: "Status",
        operator: "equals",
        value: params.status
      });
    }

    const response = await this.makeApiCall('/api/clm/v1/contracts/query', 'POST', query);
    return this.formatContractResults(response);
  }

  async getContract(params) {
    const response = await this.makeApiCall(`/api/clm/v1/contracts/${params.contract_id}`, 'GET');
    return { success: true, contract: response };
  }

  async searchAccounts(params) {
    // Use contract search to find accounts (same as the original implementation)
    const query = {
      pageSize: 20,
      filters: [{
        field: "Account.Name",
        operator: "contains",
        value: params.name
      }]
    };

    const response = await this.makeApiCall('/api/clm/v1/contracts/query', 'POST', query);

    // Extract unique accounts from contracts
    const accounts = {};
    const contracts = this.extractContractsFromResponse(response);

    for (const contract of contracts) {
      const account = contract.Account;
      if (account && account.Name) {
        if (!accounts[account.Id]) {
          accounts[account.Id] = {
            id: account.Id,
            name: account.Name,
            type: account.Type,
            industry: account.Industry
          };
        }
      }
    }

    return {
      success: true,
      accounts: Object.values(accounts),
      message: `Found ${Object.keys(accounts).length} accounts matching '${params.name}'`
    };
  }

  formatContractResults(response) {
    const contracts = this.extractContractsFromResponse(response);

    const formatted = contracts.map(contract => ({
      id: contract.Id,
      name: contract.Name,
      type: contract.ContractType,
      status: contract.Status,
      account_name: contract.Account?.Name || null,
      created_date: contract.CreatedDate
    }));

    return {
      success: true,
      contracts: formatted,
      total_count: formatted.length,
      message: `Found ${formatted.length} contracts`
    };
  }

  extractContractsFromResponse(response) {
    // Handle Conga's response structure
    if (response.Success && response.Data) {
      const dataSection = response.Data;
      return Array.isArray(dataSection.Data) ? dataSection.Data : [];
    }
    return response.records || [];
  }

  async makeApiCall(endpoint, method = 'GET', body = null) {
    const url = `${this.baseUrl}${endpoint}`;

    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      }
    };

    if (body && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} - ${response.statusText}`);
    }

    return await response.json();
  }

  async getFollowUpResponse(originalContent, toolResult, toolUseId) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.credentials.anthropicKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 1500,
        messages: [
          {
            role: 'assistant',
            content: originalContent
          },
          {
            role: 'user',
            content: [
              {
                type: 'tool_result',
                tool_use_id: toolUseId,
                content: JSON.stringify(toolResult)
              }
            ]
          }
        ]
      })
    });

    if (!response.ok) {
      return `Tool executed but couldn't generate follow-up response: ${response.status}`;
    }

    const data = await response.json();
    return data.content.map(c => c.text).join('');
  }
}

// Initialize background script
new CongaAIBackground();