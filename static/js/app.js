// Salesforce Conga CLM AI Agent - Web Interface JavaScript

class CongaAIAgent {
    constructor() {
        this.socket = io();
        this.isConnected = false;
        this.isTyping = false;

        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketHandlers();
        this.autoResizeTextarea();
    }

    initializeElements() {
        // Get DOM elements
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.healthBtn = document.getElementById('healthBtn');
        this.helpBtn = document.getElementById('helpBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.connectionText = document.getElementById('connectionText');
        this.toastContainer = document.getElementById('toastContainer');
        this.quickActionBtns = document.querySelectorAll('.quick-action-btn');
    }

    setupEventListeners() {
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());

        // Quick action buttons
        this.quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.messageInput.value = message;
                this.sendMessage();
            });
        });

        // Utility buttons
        this.clearBtn.addEventListener('click', () => this.clearConversation());
        this.healthBtn.addEventListener('click', () => this.checkHealth());
        this.helpBtn.addEventListener('click', () => this.showHelp());

        // Focus input on load
        this.messageInput.focus();
    }

    setupSocketHandlers() {
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected', 'connected');
            this.showToast('Connected to Salesforce Conga CLM AI Agent', 'success');
        });

        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'disconnected');
            this.showToast('Disconnected from server', 'error');
        });

        this.socket.on('message', (data) => {
            this.addMessage(data.content, data.type, data.timestamp);
        });

        this.socket.on('typing', (data) => {
            this.showTypingIndicator(data.is_typing);
        });

        this.socket.on('error', (data) => {
            this.showToast(data.message || 'An error occurred', 'error');
        });
    }

    updateConnectionStatus(text, status) {
        this.connectionText.textContent = text;
        this.connectionStatus.className = 'status-dot ' + status;
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;

        // Clear input
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Disable send button temporarily
        this.sendBtn.disabled = true;

        // Send to server
        this.socket.emit('user_message', { message: message });

        // Re-enable send button after a delay
        setTimeout(() => {
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }, 1000);
    }

    addMessage(content, type, timestamp) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Handle markdown rendering for assistant messages
        if (type === 'assistant') {
            contentDiv.innerHTML = marked.parse(content);
            // Wrap tables in scrollable containers
            this.wrapTablesInScrollContainers(contentDiv);
        } else {
            contentDiv.textContent = content;
        }

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = this.formatTimestamp(timestamp);

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator(show) {
        this.isTyping = show;
        this.typingIndicator.style.display = show ? 'flex' : 'none';
        if (show) {
            this.scrollToBottom();
        }
    }

    scrollToBottom() {
        // Immediate scroll for better responsiveness
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        // Additional scroll after content is fully rendered
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 50);
    }

    wrapTablesInScrollContainers(container) {
        const tables = container.querySelectorAll('table');
        tables.forEach(table => {
            // Skip if already wrapped
            if (table.parentElement.classList.contains('table-container')) {
                return;
            }

            const wrapper = document.createElement('div');
            wrapper.className = 'table-container';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
    }

    clearConversation() {
        if (confirm('Are you sure you want to clear the conversation?')) {
            this.messagesContainer.innerHTML = '';
            this.socket.emit('clear_history');
            this.showToast('Conversation cleared', 'success');
        }
    }

    checkHealth() {
        this.messageInput.value = 'health';
        this.sendMessage();
    }

    showHelp() {
        this.messageInput.value = 'help';
        this.sendMessage();
    }

    autoResizeTextarea() {
        // Reset height to auto to get accurate scrollHeight
        this.messageInput.style.height = 'auto';

        // Set height based on content, with min/max constraints
        const scrollHeight = this.messageInput.scrollHeight;
        const maxHeight = 120; // Max height in pixels
        const minHeight = 24; // Min height in pixels

        if (scrollHeight > maxHeight) {
            this.messageInput.style.height = maxHeight + 'px';
            this.messageInput.style.overflowY = 'scroll';
        } else if (scrollHeight < minHeight) {
            this.messageInput.style.height = minHeight + 'px';
            this.messageInput.style.overflowY = 'hidden';
        } else {
            this.messageInput.style.height = scrollHeight + 'px';
            this.messageInput.style.overflowY = 'hidden';
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const isToday = date.toDateString() === now.toDateString();

        if (isToday) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }

    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        this.toastContainer.appendChild(toast);

        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);

        // Click to remove
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }

    // Add smooth scrolling to quick actions
    enableSmoothScrolling() {
        const quickActionsContainer = document.querySelector('.quick-actions');
        if (quickActionsContainer) {
            quickActionsContainer.addEventListener('wheel', (e) => {
                e.preventDefault();
                quickActionsContainer.scrollLeft += e.deltaY;
            });
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new CongaAIAgent();

    // Add some initial welcome behavior
    setTimeout(() => {
        app.addMessage(
            '👋 **Welcome to the Salesforce Conga CLM AI Agent!**\n\n' +
            'I can help you manage your agreements using natural language. Try asking me:\n\n' +
            '• "List my recent agreements"\n' +
            '• "Show me expiring contracts"\n' +
            '• "What fields are available for agreements?"\n\n' +
            'Click the quick action buttons below or type your own question!',
            'system',
            new Date().toISOString()
        );
    }, 1000);

    // Add global error handling
    window.addEventListener('error', (e) => {
        console.error('Application error:', e.error);
        app.showToast('An unexpected error occurred', 'error');
    });

    // Add visibility change handler to reconnect if needed
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && !app.isConnected) {
            app.showToast('Attempting to reconnect...', 'warning');
        }
    });
});

// Configure marked.js for better markdown rendering
if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false
    });
}