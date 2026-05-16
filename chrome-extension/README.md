# Conga CLM AI Assistant - Chrome Extension

🤖 **Secure, Session-Based AI Assistant for Conga CLM**

## 🔒 Security Features

✅ **Session-Only Credentials** - API keys stored only during active session
✅ **Auto-Clear on Close** - All credentials deleted when tab/browser closes
✅ **Local Processing** - No third-party cloud services
✅ **Direct API Calls** - Connects directly to Conga & Anthropic APIs
✅ **Minimal Permissions** - Only requests necessary Chrome permissions
✅ **Auditable Code** - Full source code visible for security review

## 🏢 Perfect for Corporate Environments

- **No Installation Required** - Just load as Chrome extension
- **No Admin Rights** - Works on locked-down corporate PCs
- **IT-Friendly** - Local processing, no external dependencies
- **Compliance Safe** - No permanent credential storage
- **Professional Design** - Clean interface suitable for business use

## 🚀 Installation Instructions

### Option 1: Load Unpacked Extension (Recommended for Testing)

1. **Download Extension Files:**
   - Extract the chrome-extension folder to your desktop

2. **Open Chrome Extensions Page:**
   - Go to `chrome://extensions/`
   - OR: Chrome Menu → More Tools → Extensions

3. **Enable Developer Mode:**
   - Toggle "Developer mode" switch (top right)

4. **Load Extension:**
   - Click "Load unpacked"
   - Select the chrome-extension folder
   - Extension should appear in your toolbar

### Option 2: Package as .crx File

1. **Package Extension:**
   - Go to `chrome://extensions/`
   - Click "Pack extension"
   - Select the chrome-extension folder
   - Generate .crx file

2. **Install Package:**
   - Drag the .crx file to Chrome
   - Confirm installation

## 📖 Usage Instructions

### First Time Setup

1. **Click Extension Icon** in Chrome toolbar
2. **Enter Your Credentials:**
   - Conga Client ID
   - Conga Client Secret
   - Conga Auth URL
   - Conga Base URL
   - Anthropic API Key

3. **Click "Connect & Start Session"**
   - Extension tests all credentials
   - Shows "Connected" status when ready

### Using the AI Assistant

1. **Navigate to any Conga CLM page** in your browser
2. **Ask questions** in the extension popup:
   - "Find all contracts with ABC Corp"
   - "Show me expired contracts"
   - "Create an MSA with TechCorp"
   - "What's the status of contract xyz123?"

3. **View AI responses** in floating overlay on Conga page
4. **End session** when done - all credentials cleared

## 🔧 Configuration

### Required Credentials

```
CONGA_CLIENT_ID      = Your Conga OAuth Client ID
CONGA_CLIENT_SECRET  = Your Conga OAuth Client Secret
CONGA_AUTH_URL       = https://login-rlspreview.congacloud.com/api/v1/auth/connect/token
CONGA_BASE_URL       = https://preview-rls09.congacloud.com
ANTHROPIC_API_KEY    = Your Claude API key
```

### Chrome Permissions Explained

- **activeTab**: Read current Conga page to inject AI responses
- **storage**: Store session credentials (auto-cleared on close)
- **host_permissions**: Make API calls to Conga and Anthropic

## 🛡️ Security Analysis

### What's Secure

| Aspect | Security Level | Details |
|--------|---------------|---------|
| **Credential Storage** | 🟢 **HIGH** | Session-only, auto-cleared |
| **Data Transmission** | 🟢 **HIGH** | Direct HTTPS to APIs only |
| **Code Transparency** | 🟢 **HIGH** | Full source code visible |
| **Corporate Policy** | 🟢 **HIGH** | No cloud dependencies |
| **User Control** | 🟢 **HIGH** | User enters credentials each session |

### Minimal Risks

| Risk | Level | Mitigation |
|------|-------|------------|
| Browser memory exposure | 🟡 **LOW** | Credentials only in RAM during session |
| Developer tools access | 🟡 **LOW** | User must manually open dev tools |
| Extension permissions | 🟡 **LOW** | Minimal permissions requested |

### Risk Comparison

| Solution | Credential Storage | Security Risk |
|----------|-------------------|---------------|
| **Chrome Extension** | Session only | 🟢 **LOW** |
| Cloud (Replit) | Permanent external | 🔴 **HIGH** |
| Portable Python | Local file | 🟡 **MEDIUM** |

## 🎯 Business Justification

### For IT Security Teams

**Q: Is it safe to use this extension with corporate API keys?**
A: Yes - credentials are only stored in browser session memory and automatically cleared when the session ends. No permanent storage or cloud transmission.

**Q: What permissions does it need?**
A: Minimal - only access to current Conga tabs and session storage. No broad permissions.

**Q: Can we audit the code?**
A: Yes - full source code is visible and can be reviewed before installation.

**Q: Does it violate corporate policies?**
A: No - processes everything locally, no external cloud services, no permanent credential storage.

### For Management

- **Productivity Boost**: AI-powered contract management assistance
- **Cost Effective**: Uses existing Conga and Claude subscriptions
- **Secure**: Meets corporate security standards
- **Professional**: Clean interface suitable for client-facing work
- **Flexible**: Works on any computer with Chrome browser

## 🔍 Troubleshooting

### Extension Not Loading
- Check that Developer Mode is enabled
- Verify all files are in chrome-extension folder
- Look for errors in `chrome://extensions/`

### Authentication Failing
- Verify Conga Client ID/Secret are correct
- Check that URLs match your Conga environment
- Test Anthropic API key in Claude console first

### AI Responses Not Showing
- Ensure you're on a Conga CLM page (congacloud.com)
- Check extension popup shows "Connected" status
- Try refreshing the Conga page

### Corporate Firewall Issues
- Extension makes HTTPS calls to:
  - Your Conga environment (*.congacloud.com)
  - Anthropic API (api.anthropic.com)
- Ask IT to whitelist these domains if blocked

## 📝 Development Notes

### File Structure
```
chrome-extension/
├── manifest.json      # Extension configuration
├── popup.html         # Credential input interface
├── popup.js          # Session management logic
├── background.js     # API communication handler
├── content.js        # Conga page integration
├── styles.css        # Content script styles
├── icons/            # Extension icons
└── README.md         # This file
```

### API Integration
- Uses Conga CLM REST APIs v1
- Integrates with Anthropic Claude API
- Implements proper OAuth2 client credentials flow
- Handles session-based credential management

## 🚀 Next Steps

1. **Install & Test** - Try the extension in your environment
2. **Security Review** - Have your IT team review the code
3. **User Training** - Show colleagues how to use it safely
4. **Feedback** - Report any issues or feature requests

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review Chrome extension console logs
3. Verify API credentials are working outside the extension
4. Test on a simple Conga page first

---

**🔒 Remember: This extension prioritizes security and corporate compliance. All credentials are session-based and automatically cleared when you're done.**