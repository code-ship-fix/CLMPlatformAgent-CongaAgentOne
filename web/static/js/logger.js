// API Call Logger for debugging

class APILogger {
    constructor() {
        this.logs = [];
        this.maxLogs = 100;
        this.createLogWindow();
    }

    createLogWindow() {
        // Create log window HTML
        const logWindow = document.createElement('div');
        logWindow.id = 'debugLogger';
        logWindow.className = 'debug-logger hidden';

        logWindow.innerHTML = `
            <div class="logger-header">
                <h3><i class="fas fa-bug"></i> Debug Logger</h3>
                <div class="logger-controls">
                    <button id="clearLogs" class="btn-small">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                    <button id="toggleLogger" class="btn-small">
                        <i class="fas fa-eye-slash"></i> Hide
                    </button>
                </div>
            </div>
            <div class="logger-content" id="loggerContent">
                <div class="log-entry info">
                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                    <span class="log-type">INFO</span>
                    <span class="message">Debug logger initialized</span>
                </div>
            </div>
            <div class="logger-footer">
                <small>Real-time API and system logging</small>
            </div>
        `;

        document.body.appendChild(logWindow);

        // Add toggle button to main interface
        const toggleButton = document.createElement('button');
        toggleButton.id = 'showLogger';
        toggleButton.className = 'debug-toggle';
        toggleButton.innerHTML = '<i class="fas fa-bug"></i>';
        toggleButton.title = 'Show Debug Logger';
        document.body.appendChild(toggleButton);

        this.bindLoggerEvents();
    }

    bindLoggerEvents() {
        const logger = document.getElementById('debugLogger');
        const showBtn = document.getElementById('showLogger');
        const hideBtn = document.getElementById('toggleLogger');
        const clearBtn = document.getElementById('clearLogs');

        showBtn.addEventListener('click', () => {
            logger.classList.remove('hidden');
            showBtn.classList.add('hidden');
        });

        hideBtn.addEventListener('click', () => {
            logger.classList.add('hidden');
            showBtn.classList.remove('hidden');
        });

        clearBtn.addEventListener('click', () => {
            this.clearLogs();
        });
    }

    log(type, category, message, data = null) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            timestamp,
            type: type.toUpperCase(),
            category,
            message,
            data
        };

        this.logs.push(logEntry);

        // Keep only last maxLogs entries
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }

        this.displayLog(logEntry);
    }

    displayLog(logEntry) {
        const loggerContent = document.getElementById('loggerContent');
        if (!loggerContent) return;

        const logDiv = document.createElement('div');
        logDiv.className = `log-entry ${logEntry.type.toLowerCase()}`;

        let dataHTML = '';
        if (logEntry.data) {
            try {
                const dataStr = typeof logEntry.data === 'string' ?
                    logEntry.data : JSON.stringify(logEntry.data, null, 2);
                dataHTML = `
                    <div class="log-data">
                        <button class="toggle-data">
                            <i class="fas fa-chevron-right"></i> Show Data
                        </button>
                        <pre class="data-content hidden">${dataStr}</pre>
                    </div>
                `;
            } catch (e) {
                dataHTML = `<div class="log-data">Data: ${logEntry.data}</div>`;
            }
        }

        logDiv.innerHTML = `
            <span class="timestamp">${logEntry.timestamp}</span>
            <span class="log-type">${logEntry.type}</span>
            <span class="log-category">[${logEntry.category}]</span>
            <span class="message">${logEntry.message}</span>
            ${dataHTML}
        `;

        // Add click handler for data toggle
        const toggleBtn = logDiv.querySelector('.toggle-data');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const dataContent = logDiv.querySelector('.data-content');
                const icon = toggleBtn.querySelector('i');

                if (dataContent.classList.contains('hidden')) {
                    dataContent.classList.remove('hidden');
                    icon.className = 'fas fa-chevron-down';
                    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Hide Data';
                } else {
                    dataContent.classList.add('hidden');
                    icon.className = 'fas fa-chevron-right';
                    toggleBtn.innerHTML = '<i class="fas fa-chevron-right"></i> Show Data';
                }
            });
        }

        loggerContent.appendChild(logDiv);
        loggerContent.scrollTop = loggerContent.scrollHeight;
    }

    clearLogs() {
        this.logs = [];
        const loggerContent = document.getElementById('loggerContent');
        if (loggerContent) {
            loggerContent.innerHTML = `
                <div class="log-entry info">
                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                    <span class="log-type">INFO</span>
                    <span class="message">Logs cleared</span>
                </div>
            `;
        }
    }

    // Convenient logging methods
    info(category, message, data) { this.log('info', category, message, data); }
    warn(category, message, data) { this.log('warn', category, message, data); }
    error(category, message, data) { this.log('error', category, message, data); }
    debug(category, message, data) { this.log('debug', category, message, data); }
    api(method, url, payload, response) {
        this.log('api', 'API CALL', `${method} ${url}`, {
            method,
            url,
            payload,
            response
        });
    }
}

// Initialize global logger
window.apiLogger = new APILogger();