"""
LLM Client Adapter for Generative AI Synthesis.
Supports:
1. Built-in Deterministic Generative Synthesis Engine (Zero-API Key, ultra-fast, 100% private)
2. External OpenAI / Gemini API (if environment variable OPENAI_API_KEY or GEMINI_API_KEY is configured)
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class LLMClient:
    """Connects to external GenAI endpoints or fallbacks to the high-accuracy local generative synthesizer."""

    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.use_external = bool(self.openai_key or self.gemini_key)

    def generate(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Attempts generation with external LLM if configured; returns None if external fails or unconfigured."""
        if not self.use_external:
            return None

        if self.gemini_key:
            return self._call_gemini(prompt, system_prompt)
        elif self.openai_key:
            return self._call_openai(prompt, system_prompt)
        return None

    def _call_gemini(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
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
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return None

    def _call_openai(self, prompt: str, system_prompt: str) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None
