"""xAI (Grok) provider adapter."""

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ProviderType


class XAIAdapter(BaseAIProvider):
    """xAI (Grok) provider adapter."""

    API_BASE = "https://api.x.ai/v1"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.XAI

    def _build_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    async def generate_text(self, request: AIRequest) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("xAI API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.default_model,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        start = time.time()
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(f"{self.API_BASE}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        duration_ms = round((time.time() - start) * 1000, 2)
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        tokens = data.get("usage", {}).get("total_tokens")

        return AIResponse(
            content=content,
            provider=self.provider_type,
            model=data.get("model", self.default_model),
            tokens_used=tokens,
            duration_ms=duration_ms,
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def generate_json(self, request: AIRequest) -> AIResponse:
        request.json_mode = True
        return await self.generate_text(request)

    async def stream_text(self, request: AIRequest) -> AsyncIterator[str]:
        res = await self.generate_text(request)
        yield res.content

