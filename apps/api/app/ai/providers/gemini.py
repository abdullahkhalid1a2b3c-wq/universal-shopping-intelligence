"""Google Gemini AI Studio direct provider adapter."""

import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ProviderType


class GeminiAdapter(BaseAIProvider):
    """Google Gemini AI Studio adapter via official REST endpoints."""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GEMINI

    def _convert_contents(self, request: AIRequest) -> List[Dict[str, Any]]:
        contents: List[Dict[str, Any]] = []
        for msg in request.messages:
            role = "model" if msg.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": msg.content}]})
        return contents

    async def generate_text(self, request: AIRequest) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured")

        url = f"{self.API_BASE}/{self.default_model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        generation_config: Dict[str, Any] = {
            "temperature": request.temperature,
            "maxOutputTokens": request.max_tokens,
        }
        if request.json_mode:
            generation_config["responseMimeType"] = "application/json"

        payload: Dict[str, Any] = {
            "contents": self._convert_contents(request),
            "generationConfig": generation_config,
        }
        if request.system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": request.system_prompt}]
            }

        start = time.time()
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        duration_ms = round((time.time() - start) * 1000, 2)
        candidates = data.get("candidates", [{}])
        first_candidate = candidates[0] if candidates else {}
        parts = first_candidate.get("content", {}).get("parts", [])
        content = parts[0].get("text", "") if parts else ""
        tokens = data.get("usageMetadata", {}).get("totalTokenCount")

        structured_data = None
        if request.json_mode:
            try:
                structured_data = json.loads(content)
            except Exception:
                structured_data = None

        return AIResponse(
            content=content,
            provider=self.provider_type,
            model=self.default_model,
            tokens_used=tokens,
            duration_ms=duration_ms,
            finish_reason=first_candidate.get("finishReason", "STOP"),
            structured_data=structured_data,
        )

    async def generate_json(self, request: AIRequest) -> AIResponse:
        request.json_mode = True
        return await self.generate_text(request)

    async def stream_text(self, request: AIRequest) -> AsyncIterator[str]:
        # For simplicity and robust fallback, stream via generate_text
        res = await self.generate_text(request)
        yield res.content

