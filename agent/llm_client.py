"""
Enhanced LLM Client Adapter for Generative AI Synthesis.
Supports:
1. Built-in Deterministic Generative Synthesis Engine (Zero-API Key, ultra-fast, 100% private)
2. Google Gemini (Gemini 1.5 Flash / Pro, Gemini 2.0)
3. OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
4. Anthropic Claude (Claude 3.5 Sonnet, Claude 3 Haiku)
5. Local Ollama (e.g. Llama 3, Mistral, Qwen, DeepSeek)
6. Custom OpenAI-Compatible Endpoints (Groq, Together AI, vLLM, LM Studio, Corporate Gateways)
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple


def load_dotenv(filepath: str = ".env"):
    """Lightweight zero-dependency .env loader."""
    if not os.path.exists(filepath):
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


class LLMClient:
    """Connects to external GenAI endpoints or falls back to the local deterministic engine."""

    def __init__(self):
        # Auto-load .env if available
        load_dotenv()
        self.provider = "auto"
        self._load_from_env()

    def _load_from_env(self):
        self.last_error = ""

        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()

        self.openai_key = (
            os.environ.get("OPENAI_API_KEY", "").strip() or
            os.environ.get("api_key", "").strip() or
            os.environ.get("API_KEY", "").strip() or
            os.environ.get("GROQ_API_KEY", "").strip() or
            os.environ.get("LLM_API_KEY", "").strip()
        )
        self.openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.openai_base_url = (
            os.environ.get("OPENAI_BASE_URL", "").strip() or
            os.environ.get("LLM_BASE_URL", "").strip()
        )

        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()

        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "").strip()
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3").strip()

        self.custom_base_url = os.environ.get("LLM_BASE_URL", "").strip() or self.openai_base_url
        self.custom_key = os.environ.get("LLM_API_KEY", "").strip() or self.openai_key
        self.custom_model = os.environ.get("LLM_MODEL", "default").strip()

        # Determine active provider
        env_provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
        if env_provider in ["gemini", "openai", "anthropic", "ollama", "custom", "local"]:
            self.provider = env_provider
        elif self.openai_key or self.openai_base_url:
            self.provider = "openai"
        elif self.gemini_key:
            self.provider = "gemini"
        elif self.anthropic_key:
            self.provider = "anthropic"
        elif self.ollama_base_url:
            self.provider = "ollama"
        elif self.custom_base_url:
            self.provider = "custom"
        else:
            self.provider = "local"

    @property
    def use_external(self) -> bool:
        return self.provider not in ["local", "none", ""]

    @property
    def active_provider(self) -> str:
        if self.provider == "gemini":
            return f"Google Gemini ({self.gemini_model})"
        elif self.provider == "openai":
            return f"OpenAI ({self.openai_model})"
        elif self.provider == "anthropic":
            return f"Anthropic Claude ({self.anthropic_model})"
        elif self.provider == "ollama":
            return f"Ollama Local ({self.ollama_model})"
        elif self.provider == "custom":
            return f"OpenAI-Compatible ({self.custom_model})"
        return "Deterministic Local Engine"

    def get_status(self) -> Dict[str, Any]:
        """Returns safe status report with masked keys for Web UI / API."""
        return {
            "provider": self.provider,
            "active_provider_name": self.active_provider,
            "use_external": self.use_external,
            "gemini_configured": bool(self.gemini_key),
            "gemini_model": self.gemini_model,
            "openai_configured": bool(self.openai_key),
            "openai_model": self.openai_model,
            "anthropic_configured": bool(self.anthropic_key),
            "anthropic_model": self.anthropic_model,
            "ollama_configured": bool(self.ollama_base_url),
            "ollama_base_url": self.ollama_base_url or "http://localhost:11434",
            "ollama_model": self.ollama_model,
            "custom_configured": bool(self.custom_base_url),
            "custom_base_url": self.custom_base_url,
            "custom_model": self.custom_model
        }

    def update_config(self, provider: str, **kwargs) -> Dict[str, Any]:
        """Allows dynamic configuration from UI or REST API."""
        prov = provider.strip().lower()
        if prov not in ["gemini", "openai", "anthropic", "ollama", "custom", "local"]:
            raise ValueError(f"Unsupported provider: '{provider}'. Allowed: gemini, openai, anthropic, ollama, custom, local")

        self.provider = prov

        if "gemini_key" in kwargs and kwargs["gemini_key"]:
            self.gemini_key = kwargs["gemini_key"].strip()
        if "gemini_model" in kwargs and kwargs["gemini_model"]:
            self.gemini_model = kwargs["gemini_model"].strip()

        if "openai_key" in kwargs and kwargs["openai_key"]:
            self.openai_key = kwargs["openai_key"].strip()
        if "openai_model" in kwargs and kwargs["openai_model"]:
            self.openai_model = kwargs["openai_model"].strip()

        if "anthropic_key" in kwargs and kwargs["anthropic_key"]:
            self.anthropic_key = kwargs["anthropic_key"].strip()
        if "anthropic_model" in kwargs and kwargs["anthropic_model"]:
            self.anthropic_model = kwargs["anthropic_model"].strip()

        if "ollama_base_url" in kwargs and kwargs["ollama_base_url"]:
            self.ollama_base_url = kwargs["ollama_base_url"].strip()
        if "ollama_model" in kwargs and kwargs["ollama_model"]:
            self.ollama_model = kwargs["ollama_model"].strip()

        if "custom_base_url" in kwargs and kwargs["custom_base_url"]:
            self.custom_base_url = kwargs["custom_base_url"].strip()
        if "custom_key" in kwargs and kwargs["custom_key"]:
            self.custom_key = kwargs["custom_key"].strip()
        if "custom_model" in kwargs and kwargs["custom_model"]:
            self.custom_model = kwargs["custom_model"].strip()

        return self.get_status()

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Routes generation to the active external provider; returns None on failure or if local."""
        if not self.use_external:
            return None

        try:
            if self.provider == "gemini":
                return self._call_gemini(prompt, system_prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt, system_prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt, system_prompt)
            elif self.provider == "ollama":
                return self._call_ollama(prompt, system_prompt)
            elif self.provider == "custom":
                return self._call_custom(prompt, system_prompt)
        except Exception as e:
            # Silently fallback to deterministic local engine
            return None
        return None

    def test_connection(self) -> Tuple[bool, str]:
        """Tests connectivity with the active provider using a 2-word probe."""
        if not self.use_external:
            return True, "Deterministic Local Engine is active (no external connection required)."

        self.last_error = ""
        test_prompt = "Say hello in 3 words."
        test_sys = "You are a test probe."
        res = self.generate(test_prompt, test_sys)
        if res:
            return True, f"Successfully connected to {self.active_provider}! Response: '{res.strip()[:60]}'"
        err_detail = f" Reason: {self.last_error}" if getattr(self, "last_error", "") else ""
        return False, f"Connection to {self.active_provider} failed.{err_detail}"

    def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        if not self.gemini_key:
            self.last_error = "Gemini API key is missing."
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}
            ],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            try:
                err_msg = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", str(e))
            except Exception:
                err_msg = str(e)
            self.last_error = f"HTTP {e.code}: {err_msg}"
            return None
        except Exception as e:
            self.last_error = str(e)
            return None

    def _call_openai(self, prompt: str, system_prompt: str) -> Optional[str]:
        if not self.openai_key:
            self.last_error = "API key is missing."
            return None

        base = (self.openai_base_url or "https://api.openai.com/v1").rstrip("/")
        if not base.endswith("/chat/completions"):
            url = f"{base}/chat/completions"
        else:
            url = base

        payload = {
            "model": self.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=18) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            try:
                err_msg = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", str(e))
            except Exception:
                err_msg = str(e)
            self.last_error = f"HTTP {e.code}: {err_msg}"
            return None
        except Exception as e:
            self.last_error = str(e)
            return None

    def _call_anthropic(self, prompt: str, system_prompt: str) -> Optional[str]:
        if not self.anthropic_key:
            return None
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": self.anthropic_model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=18) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]

    def _call_ollama(self, prompt: str, system_prompt: str) -> Optional[str]:
        base = self.ollama_base_url or "http://localhost:11434"
        url = f"{base.rstrip('/')}/api/generate"
        payload = {
            "model": self.ollama_model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response")

    def _call_custom(self, prompt: str, system_prompt: str) -> Optional[str]:
        base = self.custom_base_url.rstrip("/")
        if not base.endswith("/chat/completions"):
            url = f"{base}/chat/completions" if "/v1" in base else f"{base}/v1/chat/completions"
        else:
            url = base

        payload = {
            "model": self.custom_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }
        headers = {"Content-Type": "application/json"}
        if self.custom_key:
            headers["Authorization"] = f"Bearer {self.custom_key}"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
