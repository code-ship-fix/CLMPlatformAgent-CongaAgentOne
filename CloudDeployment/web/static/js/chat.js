// Conga CLM AI Agent - Chat Interface JavaScript

class CongaChatApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.sessionId = null;
        this.messageHistory = [];

        this.init();
    }

    init() {
        this.initializeElements();
        this.initializeSocket();
        this.bindEvents();
        this.setupKeyboardShortcuts();
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.typingIndicator = document.getElementById('typingIndicator');

        // Status elements
        this.connectionStatus = document.getElementById('connectionStatus');

        // Toast elements
        this.errorToast = document.getElementById('errorToast');
        this.successToast = document.getElementById('successToast');
        this.errorMessage = document.getElementById('errorMessage');
        this.successMessage = document.getElementById('successMessage');

        // Counter and shortcuts
        this.charCounter = document.getElementById('charCounter');
        this.shortcutBtns = document.querySelectorAll('.shortcut-btn');

        // Quick actions
        this.quickActions = document.getElementById('quickActions');
        this.mobileMenuToggle = document.getElementById('mobileMenuToggle');
        this.closeQuickActions = document.getElementById('closeQuickActions');
        this.actionItems = document.querySelectorAll('.action-item');
    }

    initializeSocket() {
        try {
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 10000,
                forceNew: true
            });

            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.isConnected = true;
                this.updateConnectionStatus('connected', 'Connected');
            });

            this.socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected', 'Disconnected');
                this.hideTyping();
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this.updateConnectionStatus('disconnected', 'Connection Error');
                this.showError('Connection failed. Please check your network connection.');
            });

            this.socket.on('connected', (data) => {
                this.sessionId = data.session_id;
                console.log('Session established:', this.sessionId);
            });

            this.socket.on('bot_message', (data) => {
                this.hideTyping();
                this.addMessage('bot', data.message, data.timestamp, data.type);
            });

            this.socket.on('typing', (data) => {
                if (data.typing) {
                    this.showTyping();
                } else {
                    this.hideTyping();
                }
            });

            this.socket.on('error', (data) => {
                this.hideTyping();
                this.showError(data.message);
                console.error('Server error:', data);
            });

            this.socket.on('conversation_cleared', (data) => {
                this.clearChatMessages();
                this.showSuccess(data.message);
            });

            this.socket.on('pong', () => {
                console.log('Received pong from server');
            });

            this.socket.on('debug_log', (data) => {
                apiLogger.log(data.type, data.category, data.message, data.data);
            });

        } catch (error) {
            console.error('Socket initialization error:', error);
            this.showError('Failed to initialize chat connection');
        }
    }

    bindEvents() {
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearConversation());

        // Message input
        this.messageInput.addEventListener('input', () => {
            this.updateCharCounter();
            this.autoResize();
            this.updateSendButton();
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Shortcut buttons
        this.shortcutBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                if (message) {
                    this.sendPredefinedMessage(message);
                }
            });
        });

        // Mobile menu toggle
        this.mobileMenuToggle.addEventListener('click', () => {
            this.toggleQuickActions();
        });

        // Close quick actions
        this.closeQuickActions.addEventListener('click', () => {
            this.closeQuickActionsPanel();
        });

        // Action items
        this.actionItems.forEach(item => {
            item.addEventListener('click', () => {
                const message = item.dataset.message;
                if (message) {
                    this.messageInput.value = message;
                    this.updateCharCounter();
                    this.messageInput.focus();
                    this.closeQuickActionsPanel();
                }
            });
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.scrollToBottom();
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }

            // Escape to close quick actions
            if (e.key === 'Escape') {
                this.closeQuickActionsPanel();
            }

            // Ctrl/Cmd + K to clear
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.clearConversation();
            }
        });
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;

        // Log user message
        apiLogger.info('CHAT', `User sent: "${message}"`);

        // Add user message to chat
        this.addMessage('user', message, new Date().toISOString());

        // Clear input
        this.messageInput.value = '';
        this.updateCharCounter();
        this.updateSendButton();
        this.autoResize();

        // Send to server
        apiLogger.info('WEBSOCKET', 'Sending chat_message to server', { message });
        this.socket.emit('chat_message', { message });

        // Store in history
        this.messageHistory.push(message);

        // Show typing indicator
        this.showTyping();
    }

    sendPredefinedMessage(message) {
        if (!this.isConnected) {
            this.showError('Not connected to server');
            return;
        }

        // Add user message to chat
        this.addMessage('user', message, new Date().toISOString());

        // Send to server
        this.socket.emit('chat_message', { message });

        // Show typing indicator
        this.showTyping();
    }

    addMessage(sender, content, timestamp, type = 'message') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender} new`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.textContent = sender === 'user' ? 'U' : '🤖';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';

        // Process content with markdown if it's from bot
        if (sender === 'bot') {
            bubbleDiv.innerHTML = marked.parse(content);
        } else {
            bubbleDiv.textContent = content;
        }

        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = this.formatTimestamp(timestamp);

        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timestampDiv);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);

        // Remove animation class after animation completes
        setTimeout(() => {
            messageDiv.classList.remove('new');
        }, 300);

        this.scrollToBottom();
    }

    clearConversation() {
        if (!this.isConnected) {
            this.showError('Not connected to server');
            return;
        }

        this.socket.emit('chat_message', { message: 'clear' });
    }

    clearChatMessages() {
        this.chatMessages.innerHTML = '';
    }

    showTyping() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.style.display = 'none';
    }

    updateConnectionStatus(status, text) {
        this.connectionStatus.className = `connection-status ${status}`;
        this.connectionStatus.querySelector('span').textContent = text;

        // Update send button state
        this.updateSendButton();
    }

    updateSendButton() {
        const hasMessage = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasMessage || !this.isConnected;
    }

    updateCharCounter() {
        const length = this.messageInput.value.length;
        this.charCounter.textContent = `${length}/2000`;

        if (length > 1800) {
            this.charCounter.style.color = 'var(--error-color)';
        } else if (length > 1500) {
            this.charCounter.style.color = 'var(--warning-color)';
        } else {
            this.charCounter.style.color = 'var(--text-secondary)';
        }
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return '';
        }
    }

    toggleQuickActions() {
        this.quickActions.classList.toggle('open');
    }

    closeQuickActionsPanel() {
        this.quickActions.classList.remove('open');
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorToast.classList.add('show');

        setTimeout(() => {
            this.hideToast('errorToast');
        }, 5000);
    }

    showSuccess(message) {
        this.successMessage.textContent = message;
        this.successToast.classList.add('show');

        setTimeout(() => {
            this.hideToast('successToast');
        }, 3000);
    }

    hideToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.remove('show');
        }
    }

    // Ping server periodically to keep connection alive
    startHeartbeat() {
        setInterval(() => {
            if (this.isConnected && this.socket) {
                this.socket.emit('ping');
            }
        }, 30000); // Ping every 30 seconds
    }
}

// Global function for toast close buttons
function hideToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.classList.remove('show');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new CongaChatApp();
    app.startHeartbeat();

    // Focus on input field
    setTimeout(() => {
        app.messageInput.focus();
    }, 500);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page is visible again, check connection
        if (window.chatApp && window.chatApp.socket && !window.chatApp.isConnected) {
            window.chatApp.socket.connect();
        }
    }
});

// Handle online/offline events
window.addEventListener('online', () => {
    console.log('Network connection restored');
    if (window.chatApp && window.chatApp.socket && !window.chatApp.isConnected) {
        window.chatApp.socket.connect();
    }
});

window.addEventListener('offline', () => {
    console.log('Network connection lost');
    if (window.chatApp) {
        window.chatApp.updateConnectionStatus('disconnected', 'Offline');
    }
});

// Make app globally available for debugging
window.chatApp = null;
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new CongaChatApp();
});