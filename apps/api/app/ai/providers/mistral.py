"""Mistral AI provider adapter using official REST API."""

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ProviderType


class MistralAdapter(BaseAIProvider):
    """Mistral AI provider adapter for text, JSON, and streaming."""

    API_BASE = "https://api.mistral.ai/v1"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MISTRAL

    def _build_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    async def generate_text(self, request: AIRequest) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("Mistral API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        candidate_models = [self.default_model]
        for fallback_m in ["open-mistral-7b", "codestral-latest"]:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        last_exc: Optional[Exception] = None
        for model in candidate_models:
            payload: Dict[str, Any] = {
                "model": model,
                "messages": self._build_messages(request),
                "temperature": request.temperature,
                "max_tokens": min(request.max_tokens or 500, 600),
            }
            if request.json_mode:
                payload["response_format"] = {"type": "json_object"}

            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
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

        raise last_exc or RuntimeError("All Mistral candidate models failed")

    async def generate_json(self, request: AIRequest) -> AIResponse:
        request.json_mode = True
        return await self.generate_text(request)

    async def stream_text(self, request: AIRequest) -> AsyncIterator[str]:
        if not self.is_available():
            raise RuntimeError("Mistral API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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

