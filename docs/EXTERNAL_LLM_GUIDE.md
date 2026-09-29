# External LLM Integration Guide
### Insurance Automated Risk Profile Summarizer

This guide explains how to connect and configure external **Large Language Models (LLMs)** with the **Insurance Automated Risk Profile Summarizer**.

The system features a **Dual-Mode AI Architecture**:
1. **Built-in Local Deterministic Engine (Default):** Zero API key required, 100% offline, zero hallucination, sub-millisecond speed (\(< 0.001\)s).
2. **External LLM Adapter:** Connects seamlessly to state-of-the-art commercial and open-source models for rich, expressive natural language dialogue and reasoning.

---

## 🌟 Supported External LLM Providers

| Provider | Supported Models | Config Keys | Best For |
| :--- | :--- | :--- | :--- |
| **Google Gemini** | `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash` | `GEMINI_API_KEY`<br>`GEMINI_MODEL` | Fast generation, high token context, cost-effective |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | `OPENAI_API_KEY`<br>`OPENAI_MODEL` | High reasoning accuracy, standard enterprise LLM |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307` | `ANTHROPIC_API_KEY`<br>`ANTHROPIC_MODEL` | Deep analytical underwriting narratives |
| **Ollama (Local)** | `llama3`, `mistral`, `qwen2.5`, `deepseek-r1`, `phi3` | `OLLAMA_BASE_URL`<br>`OLLAMA_MODEL` | 100% offline, zero data transmission, free |
| **OpenAI-Compatible** | Groq (`llama-3.3-70b-versatile`), vLLM, LM Studio, DeepSeek | `LLM_BASE_URL`<br>`LLM_API_KEY`<br>`LLM_MODEL` | Custom corporate gateways, self-hosted GPU clusters |

---

## 🚀 3 Ways to Configure an External LLM

### Method 1: Interactive Web Dashboard (Recommended — No Restart Needed)
1. Start the server:
   ```bash
   python3 app.py
   ```
2. Open `http://localhost:8080` in your browser.
3. Click the **"External LLM Settings"** tab in the top navigation bar.
4. Select your provider (e.g. **Google Gemini** or **OpenAI**).
5. Paste your API Key and choose a model.
6. Click **"Test Connection"** to verify live connectivity.
7. Click **"Save & Activate Provider"**.
8. Go back to the **Underwriter Workspace** tab and click **"Generate AI Risk Profile Summary"** — your summaries will now be generated live using your external LLM!

---

### Method 2: Via `.env` File (Persistent Local Config)
1. Copy the provided `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in any text editor and fill in your desired provider and API key:

#### Example A: Google Gemini
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyYourGeminiAPIKeyHere
GEMINI_MODEL=gemini-1.5-flash
```

#### Example B: OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YourOpenAIKeyHere
OPENAI_MODEL=gpt-4o-mini
```

#### Example C: Anthropic Claude
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-YourAnthropicKeyHere
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

#### Example D: Ollama (Local Open-Source LLMs)
Make sure Ollama is running (`ollama run llama3`), then set:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

#### Example E: Groq (Ultra-Fast Cloud Inference)
```bash
LLM_PROVIDER=custom
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_YourGroqAPIKeyHere
LLM_MODEL=llama-3.3-70b-versatile
```

3. Start or restart the server:
   ```bash
   python3 app.py
   ```
   *The system automatically detects `.env` on startup.*

---

### Method 3: Via Terminal Environment Variables (Production & Containers)
You can inject environment variables directly when launching the application:

```bash
# Using Google Gemini
export GEMINI_API_KEY="AIzaSyYourKeyHere"
export GEMINI_MODEL="gemini-1.5-flash"
python3 app.py

# Or inline:
OPENAI_API_KEY="sk-..." python3 app.py
```

---

## 📡 REST API: Dynamic LLM Configuration & Testing

You can also inspect, update, and test LLM settings programmatically via REST API:

### 1. Check Active LLM Status
```bash
curl -s http://localhost:8080/api/llm/config
```
**Response:**
```json
{
  "provider": "gemini",
  "active_provider_name": "Google Gemini (gemini-1.5-flash)",
  "use_external": true,
  "gemini_configured": true,
  "gemini_model": "gemini-1.5-flash"
}
```

### 2. Update Provider Dynamically at Runtime
```bash
curl -X POST http://localhost:8080/api/llm/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "openai_key": "sk-proj-...",
    "openai_model": "gpt-4o-mini"
  }'
```

### 3. Test Connection
```bash
curl -X POST http://localhost:8080/api/llm/test
```
**Response:**
```json
{
  "success": true,
  "message": "Successfully connected to Google Gemini (gemini-1.5-flash)! Response: 'Hello there friend!'",
  "provider": "Google Gemini (gemini-1.5-flash)"
}
```

---

## 🛡️ Reliability & Automatic Fallback Guardrail

What happens if the external API experiences network issues, quota limits, or rate limits?

- **Automatic Failover:** The Single-Agent orchestrator catches any network or API timeout exceptions from external LLMs and **immediately falls back to the deterministic local engine**.
- **Zero Downtime:** Underwriters will **never** receive a 500 error or broken screen due to an external LLM failure.
- **Traceable Attribution:** The returned output explicitly declares `generation_mode` (e.g. `"External LLM (Google Gemini (gemini-1.5-flash))"` vs. `"Deterministic Local Engine"`).
- **Speed Guarantee:** If an external LLM takes longer than 18 seconds, the agent terminates the remote call to preserve the Problem Statement's \(< 20.0\)s Speed SLA requirement.
