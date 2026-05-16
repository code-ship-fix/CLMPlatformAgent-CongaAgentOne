// Chrome Extension Background Script - OpenAI Version
// Replace Anthropic calls with OpenAI GPT-4

async testOpenAIAuthentication(apiKey) {
  try {
    console.log('Testing OpenAI authentication...');

    const response = await fetch('https://api.openai.com/v1/models', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`OpenAI auth failed: ${response.status} - ${response.statusText}`);
    }

    console.log('✅ OpenAI authentication successful');
    return { success: true, message: 'OpenAI authentication successful' };

  } catch (error) {
    console.error('❌ OpenAI authentication failed:', error);
    return { success: false, error: error.message };
  }
}

async processQueryWithOpenAI(query, credentials) {
  try {
    // Send query to OpenAI GPT-4
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${credentials.openaiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4-turbo',
        messages: [
          {
            role: 'system',
            content: `You are a helpful AI assistant for managing contracts in Conga CLM.
            You can search contracts, get contract details, and search accounts.
            Always be helpful and provide clear, actionable responses.`
          },
          {
            role: 'user',
            content: query
          }
        ],
        max_tokens: 2000,
        tools: [
          {
            type: "function",
            function: {
              name: "search_contracts",
              description: "Search for contracts in Conga CLM",
              parameters: {
                type: "object",
                properties: {
                  account_name: { type: "string", description: "Account name to search for" },
                  contract_type: { type: "string", description: "Contract type (MSA, NDA, etc.)" },
                  status: { type: "string", description: "Contract status" }
                }
              }
            }
          }
        ]
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();

    // Process tool calls if any
    if (data.choices[0].message.tool_calls) {
      // Handle tool calls similar to Claude implementation
      return await this.handleOpenAIToolCalls(data.choices[0].message.tool_calls, credentials);
    }

    return data.choices[0].message.content;

  } catch (error) {
    throw new Error(`OpenAI processing failed: ${error.message}`);
  }
}