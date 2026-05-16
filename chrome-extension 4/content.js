/**
 * Conga CLM AI Assistant - Content Script
 * Injects AI responses into Conga web pages
 */

class CongaAIContent {
  constructor() {
    this.initializeMessageListener();
    this.createAIContainer();
  }

  initializeMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === 'showAIResponse') {
        this.showAIResponse(message.query, message.response);
        sendResponse({ success: true });
      }
    });
  }

  createAIContainer() {
    // Create a floating AI assistant container
    if (!document.getElementById('conga-ai-container')) {
      const container = document.createElement('div');
      container.id = 'conga-ai-container';
      container.innerHTML = `
        <div class="conga-ai-header">
          <span>🤖 AI Assistant</span>
          <button class="conga-ai-close">×</button>
        </div>
        <div class="conga-ai-content">
          <div class="conga-ai-messages"></div>
        </div>
      `;

      document.body.appendChild(container);

      // Add close button functionality
      container.querySelector('.conga-ai-close').addEventListener('click', () => {
        container.style.display = 'none';
      });

      // Make draggable
      this.makeDraggable(container);
    }
  }

  showAIResponse(query, response) {
    const container = document.getElementById('conga-ai-container');
    const messagesContainer = container.querySelector('.conga-ai-messages');

    // Clear previous messages or add to history
    const timestamp = new Date().toLocaleTimeString();

    const messageHtml = `
      <div class="conga-ai-message">
        <div class="conga-ai-query">
          <strong>You:</strong> ${this.escapeHtml(query)}
          <span class="conga-ai-timestamp">${timestamp}</span>
        </div>
        <div class="conga-ai-response">
          <strong>AI:</strong> ${this.formatResponse(response)}
        </div>
      </div>
    `;

    messagesContainer.innerHTML = messageHtml;
    container.style.display = 'block';

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  formatResponse(response) {
    // Convert markdown-like formatting to HTML
    return this.escapeHtml(response)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>')
      .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  makeDraggable(element) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    const header = element.querySelector('.conga-ai-header');

    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
      initialX = e.clientX - xOffset;
      initialY = e.clientY - yOffset;

      if (e.target === header || header.contains(e.target)) {
        isDragging = true;
      }
    }

    function drag(e) {
      if (isDragging) {
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        xOffset = currentX;
        yOffset = currentY;

        element.style.transform = `translate(${currentX}px, ${currentY}px)`;
      }
    }

    function dragEnd() {
      initialX = currentX;
      initialY = currentY;
      isDragging = false;
    }
  }
}

// Initialize content script
if (window.location.hostname.includes('congacloud.com')) {
  new CongaAIContent();
}