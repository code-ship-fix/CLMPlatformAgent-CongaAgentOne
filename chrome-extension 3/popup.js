/**
 * Conga CLM AI Assistant - Popup Script
 * Session-based credential management for security
 */

class CongaAIPopup {
  constructor() {
    this.initializeUI();
    this.bindEvents();
    this.checkSessionState();
  }

  initializeUI() {
    this.elements = {
      // Forms
      credentialsForm: document.getElementById('credentialsForm'),
      connectedState: document.getElementById('connectedState'),

      // Inputs
      clientId: document.getElementById('clientId'),
      clientSecret: document.getElementById('clientSecret'),
      authUrl: document.getElementById('authUrl'),
      baseUrl: document.getElementById('baseUrl'),
      anthropicKey: document.getElementById('anthropicKey'),
      userQuery: document.getElementById('userQuery'),

      // Buttons
      connectBtn: document.getElementById('connectBtn'),
      clearBtn: document.getElementById('clearBtn'),
      sendBtn: document.getElementById('sendBtn'),
      disconnectBtn: document.getElementById('disconnectBtn'),

      // Status
      status: document.getElementById('status')
    };
  }

  bindEvents() {
    this.elements.connectBtn.addEventListener('click', () => this.connect());
    this.elements.clearBtn.addEventListener('click', () => this.clearForm());
    this.elements.sendBtn.addEventListener('click', () => this.sendQuery());
    this.elements.disconnectBtn.addEventListener('click', () => this.disconnect());

    // Enter key handling
    this.elements.userQuery.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.ctrlKey) {
        this.sendQuery();
      }
    });

    // Auto-clear on window unload (security measure)
    window.addEventListener('beforeunload', () => {
      this.clearSession();
    });
  }

  async checkSessionState() {
    try {
      const session = await this.getSessionData();
      if (session && session.isConnected) {
        this.showConnectedState();
      }
    } catch (error) {
      console.log('No active session found');
    }
  }

  async connect() {
    const credentials = this.getCredentialsFromForm();

    if (!this.validateCredentials(credentials)) {
      this.showStatus('Please fill in all required fields', 'error');
      return;
    }

    this.showStatus('🔄 Connecting and testing credentials...', 'info');
    this.elements.connectBtn.disabled = true;

    try {
      // Test Conga connection
      const congaValid = await this.testCongaConnection(credentials);
      if (!congaValid) {
        throw new Error('Failed to authenticate with Conga CLM');
      }

      // Test Anthropic connection
      const anthropicValid = await this.testAnthropicConnection(credentials.anthropicKey);
      if (!anthropicValid) {
        throw new Error('Failed to authenticate with Anthropic API');
      }

      // Store in session storage (automatically cleared on tab close)
      await this.storeSessionData({
        ...credentials,
        isConnected: true,
        connectedAt: new Date().toISOString()
      });

      this.showConnectedState();
      this.showStatus('✅ Connected successfully - Session active', 'connected');

    } catch (error) {
      this.showStatus(`❌ Connection failed: ${error.message}`, 'error');
      console.error('Connection error:', error);
    } finally {
      this.elements.connectBtn.disabled = false;
    }
  }

  async testCongaConnection(credentials) {
    try {
      // Send message to background script to test Conga auth
      const response = await this.sendToBackground('testCongaAuth', credentials);
      return response.success;
    } catch (error) {
      console.error('Conga test failed:', error);
      return false;
    }
  }

  async testAnthropicConnection(apiKey) {
    try {
      // Test Anthropic API with a minimal request
      const response = await this.sendToBackground('testAnthropicAuth', { apiKey });
      return response.success;
    } catch (error) {
      console.error('Anthropic test failed:', error);
      return false;
    }
  }

  async sendQuery() {
    const query = this.elements.userQuery.value.trim();
    if (!query) {
      this.showStatus('Please enter a query', 'error');
      return;
    }

    this.elements.sendBtn.disabled = true;
    this.showStatus('🤖 Processing your query...', 'info');

    try {
      const session = await this.getSessionData();
      if (!session || !session.isConnected) {
        throw new Error('Session expired - please reconnect');
      }

      // Send query to background script for processing
      const response = await this.sendToBackground('processQuery', {
        query: query,
        credentials: session
      });

      if (response.success) {
        // Inject response into current Conga page
        await this.injectResponseIntoPage(query, response.result);
        this.elements.userQuery.value = '';
        this.showStatus('✅ Query processed successfully', 'connected');
      } else {
        throw new Error(response.error || 'Query processing failed');
      }

    } catch (error) {
      this.showStatus(`❌ Query failed: ${error.message}`, 'error');
      console.error('Query error:', error);
    } finally {
      this.elements.sendBtn.disabled = false;
    }
  }

  async injectResponseIntoPage(query, response) {
    // Send message to content script to show response on Conga page
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0] && tabs[0].url.includes('congacloud.com')) {
      await chrome.tabs.sendMessage(tabs[0].id, {
        action: 'showAIResponse',
        query: query,
        response: response
      });
    }
  }

  disconnect() {
    this.clearSession();
    this.showCredentialsForm();
    this.showStatus('🔒 Session ended - all credentials cleared', 'info');
  }

  clearForm() {
    this.elements.clientId.value = '';
    this.elements.clientSecret.value = '';
    this.elements.anthropicKey.value = '';
    this.elements.userQuery.value = '';
  }

  showConnectedState() {
    this.elements.credentialsForm.classList.add('hidden');
    this.elements.connectedState.classList.remove('hidden');
  }

  showCredentialsForm() {
    this.elements.connectedState.classList.add('hidden');
    this.elements.credentialsForm.classList.remove('hidden');
  }

  showStatus(message, type = 'info') {
    this.elements.status.textContent = message;
    this.elements.status.className = `status ${type}`;
    this.elements.status.classList.remove('hidden');

    // Auto-hide after 5 seconds for non-error messages
    if (type !== 'error' && type !== 'connected') {
      setTimeout(() => {
        this.elements.status.classList.add('hidden');
      }, 5000);
    }
  }

  getCredentialsFromForm() {
    return {
      clientId: this.elements.clientId.value.trim(),
      clientSecret: this.elements.clientSecret.value.trim(),
      authUrl: this.elements.authUrl.value.trim(),
      baseUrl: this.elements.baseUrl.value.trim(),
      anthropicKey: this.elements.anthropicKey.value.trim()
    };
  }

  validateCredentials(creds) {
    return creds.clientId &&
           creds.clientSecret &&
           creds.authUrl &&
           creds.baseUrl &&
           creds.anthropicKey;
  }

  async storeSessionData(data) {
    // Use sessionStorage for security - automatically cleared on tab close
    return new Promise((resolve) => {
      chrome.storage.session.set({ congaAISession: data }, resolve);
    });
  }

  async getSessionData() {
    return new Promise((resolve) => {
      chrome.storage.session.get(['congaAISession'], (result) => {
        resolve(result.congaAISession || null);
      });
    });
  }

  async clearSession() {
    // Explicitly clear session data and sensitive variables
    await new Promise((resolve) => {
      chrome.storage.session.clear(resolve);
    });

    // Clear form fields for extra security
    this.clearForm();
  }

  async sendToBackground(action, data) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage({ action, data }, (response) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(response);
        }
      });
    });
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new CongaAIPopup();
});

// Security: Clear session on extension disable/reload
chrome.runtime.onSuspend.addListener(() => {
  chrome.storage.session.clear();
});