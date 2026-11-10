"""OpenRouter multi-model gateway adapter."""

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ProviderType


class OpenRouterAdapter(BaseAIProvider):
    """OpenRouter adapter supporting Google Gemini, Claude, OpenAI, Grok, and Llama."""

    API_BASE = "https://openrouter.ai/api/v1"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER

    def _build_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    async def generate_text(self, request: AIRequest) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("OpenRouter API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://fitsense.pk",
            "X-Title": "FitSense Universal Fit Assistant",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        candidate_models = [self.default_model]
        for fallback_m in ["google/gemini-2.5-flash", "meta-llama/llama-3.3-70b-instruct"]:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        # Cap max_tokens to 600 to prevent OpenRouter upfront token credit limits
        safe_max_tokens = min(request.max_tokens or 500, 600)

        last_exc: Optional[Exception] = None
        for model in candidate_models:
            payload: Dict[str, Any] = {
                "model": model,
                "messages": self._build_messages(request),
                "temperature": request.temperature,
                "max_tokens": safe_max_tokens,
            }
            if request.json_mode:
                payload["response_format"] = {"type": "json_object"}

            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=35.0) as client:
                    resp = await client.post(f"{self.API_BASE}/chat/completions", headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()

                duration_ms = round((time.time() - start) * 1000, 2)
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                tokens = data.get("usage", {}).get("total_tokens")

                structured_data = None
                if request.json_mode:
                    try:
                        structured_data = json.loads(content)
                    except Exception:
                        structured_data = None

                return AIResponse(
                    content=content,
                    provider=self.provider_type,
                    model=model,
                    tokens_used=tokens,
                    duration_ms=duration_ms,
                    finish_reason=choice.get("finish_reason", "stop"),
                    structured_data=structured_data,
                )
            except Exception as exc:
                last_exc = exc
                continue

        raise last_exc or RuntimeError("All OpenRouter candidate models failed")

    async def generate_json(self, request: AIRequest) -> AIResponse:
        request.json_mode = True
        return await self.generate_text(request)

    async def stream_text(self, request: AIRequest) -> AsyncIterator[str]:
        if not self.is_available():
            raise RuntimeError("OpenRouter API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://fitsense.pk",
            "X-Title": "FitSense",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.default_model,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            async with client.stream("POST", f"{self.API_BASE}/chat/completions", headers=headers, json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        raw = line[6:].strip()
                        if raw:
                            try:
                                chunk = json.loads(raw)
                                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except json.JSONDecodeError:
                                continue

