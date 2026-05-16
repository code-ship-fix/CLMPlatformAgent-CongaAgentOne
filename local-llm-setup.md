# Local LLM Server Setup for Chrome Extension

## Option 1: Ollama (Easiest)

### Windows Installation:
1. **Download Ollama**: https://ollama.com/download/windows
2. **Install** (runs as Windows service)
3. **Download Legal Model**:
   ```cmd
   ollama pull llama2:7b
   # OR for better legal understanding:
   ollama pull codellama:13b
   ```
4. **Start Server**: Runs automatically on http://localhost:11434

### Model Options:
- **llama2:7b** (~4GB) - Good general performance
- **mistral:7b** (~4GB) - Better reasoning
- **codellama:13b** (~7GB) - Better for structured data
- **phi3:mini** (~2GB) - Smallest, still decent

---

## Option 2: GPT4All (Offline)

### Windows Installation:
1. **Download GPT4All**: https://gpt4all.io/
2. **Install desktop app** (includes local server)
3. **Download models** through the app interface
4. **API available** at http://localhost:4891

### Best Models for Legal:
- **Nous Hermes 2 Mistral** - Good legal reasoning
- **Wizard-Vicuna** - Better contract understanding
- **Code Llama** - Structured data handling

---

## Option 3: LM Studio (User-Friendly)

### Windows Installation:
1. **Download LM Studio**: https://lmstudio.ai/
2. **Install and browse models**
3. **One-click download** of legal models
4. **Built-in server** with OpenAI-compatible API

---

## Chrome Extension Integration

### Update Extension to Use Local LLM:

```javascript
// In background.js - replace Anthropic calls
async testLocalLLM() {
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama2:7b',
        prompt: 'Hello, test connection',
        stream: false
      })
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Replace Claude API calls with local LLM
async processWithLocalLLM(query) {
  const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama2:7b',
      prompt: `You are a Conga CLM assistant. Help with: ${query}`,
      stream: false
    })
  });

  const data = await response.json();
  return data.response;
}
```

## Model Size Comparison:

| Model | Size | Quality | Speed | Legal Focus |
|-------|------|---------|-------|-------------|
| **Phi3:mini** | 2GB | Good | Fast | Basic |
| **Llama2:7B** | 4GB | Very Good | Medium | Good |
| **Mistral:7B** | 4GB | Excellent | Medium | Very Good |
| **CodeLlama:13B** | 7GB | Excellent | Slow | Excellent |
| **Legal BERT** | 500MB | Limited | Very Slow | Specialized |

## Recommendation:

**Use Mistral 7B with Ollama:**
- ✅ 4GB size (manageable)
- ✅ Excellent reasoning for legal tasks
- ✅ Fast inference
- ✅ Easy Windows installation
- ✅ OpenAI-compatible API
- ✅ No internet required after download