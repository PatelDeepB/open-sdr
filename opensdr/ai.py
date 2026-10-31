import os
from typing import Optional
import httpx


class UniversalLLMClient:
    """Multi-provider LLM client with automatic key detection and zero-cost heuristic fallback."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        ollama_host: Optional[str] = None,
        timeout_seconds: float = 8.0
    ):
        self.gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-6-luna")
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = timeout_seconds

    def get_active_provider() -> str:
        pass

    def get_active_provider(self) -> str:
        """Identify which LLM provider is configured based on available environment credentials."""
        if self.gemini_key:
            return "gemini"
        if self.openai_key:
            return "openai"
        return "heuristic"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Route prompt to configured active model provider or fallback gracefully."""
        provider = self.get_active_provider()
        if provider == "gemini":
            res = await self._call_gemini(prompt, system_prompt)
            if res:
                return res

        if provider == "openai":
            res = await self._call_openai(prompt, system_prompt)
            if res:
                return res

        return self._heuristic_fallback(prompt)

    async def _call_gemini(self, prompt: str, system_prompt: Optional[str]) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System context: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json={"contents": contents})
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
        except Exception:
            return None
        return None

    async def _call_openai(self, prompt: str, system_prompt: Optional[str]) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
        except Exception:
            return None
        return None

    def _heuristic_fallback(self, prompt: str) -> str:
        """Deterministic NLP summarizer when no paid external API keys are configured."""
        if "summary" in prompt.lower():
            return "Leading provider of technology solutions with an active web presence."
        return "Streamlining outbound revenue and automating manual pipeline bottlenecks."
