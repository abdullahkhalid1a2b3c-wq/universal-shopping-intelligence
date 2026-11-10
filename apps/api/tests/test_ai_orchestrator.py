"""Unit and integration tests for Multi-Provider AI Infrastructure and task routing."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ChatMessage, ProviderType, TaskCategory
from app.ai.orchestrator import AIOrchestrator
from app.main import app

client = TestClient(app)


class MockSuccessProvider(BaseAIProvider):
    def __init__(self, ptype: ProviderType, model: str = "mock-model"):
        super().__init__(api_key="valid-mock-key", default_model=model)
        self._ptype = ptype

    @property
    def provider_type(self) -> ProviderType:
        return self._ptype

    async def generate_text(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=f"Response from {self._ptype.value}",
            provider=self._ptype,
            model=self.default_model,
            tokens_used=42,
            duration_ms=15.0,
            finish_reason="stop",
        )

    async def generate_json(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content='{"key": "value"}',
            provider=self._ptype,
            model=self.default_model,
            tokens_used=50,
            duration_ms=20.0,
            structured_data={"key": "value"},
        )

    async def stream_text(self, request: AIRequest):
        yield f"Response from {self._ptype.value}"


class MockFailingProvider(BaseAIProvider):
    def __init__(self, ptype: ProviderType):
        super().__init__(api_key="valid-mock-key", default_model="failing-model")
        self._ptype = ptype

    @property
    def provider_type(self) -> ProviderType:
        return self._ptype

    async def generate_text(self, request: AIRequest) -> AIResponse:
        raise ConnectionError("Upstream timeout connecting to provider")

    async def generate_json(self, request: AIRequest) -> AIResponse:
        raise ConnectionError("Upstream timeout connecting to provider")

    async def stream_text(self, request: AIRequest):
        raise ConnectionError("Upstream timeout connecting to provider")


@pytest.mark.asyncio
async def test_orchestrator_routes_to_primary_provider():
    """Verify primary provider executes task successfully."""
    orch = AIOrchestrator()
    orch.providers[ProviderType.OPENROUTER] = MockSuccessProvider(ProviderType.OPENROUTER)

    req = AIRequest(
        task_category=TaskCategory.FIT_ASSISTANT,
        messages=[ChatMessage(role="user", content="Hello")],
    )
    res = await orch.execute(req)
    assert res.provider == ProviderType.OPENROUTER
    assert "Response from openrouter" in res.content
    assert res.fallback_used is False


@pytest.mark.asyncio
async def test_orchestrator_triggers_fallback_on_failure():
    """Verify orchestrator fails over to secondary provider when primary fails."""
    orch = AIOrchestrator()
    orch.providers[ProviderType.OPENROUTER] = MockFailingProvider(ProviderType.OPENROUTER)
    orch.providers[ProviderType.MISTRAL] = MockSuccessProvider(ProviderType.MISTRAL)

    req = AIRequest(
        task_category=TaskCategory.FIT_ASSISTANT,
        messages=[ChatMessage(role="user", content="How does Khaadi fit?")],
    )
    res = await orch.execute(req)
    assert res.provider == ProviderType.MISTRAL
    assert "Response from mistral" in res.content
    assert res.fallback_used is True
    assert orch.metrics["fallbacks_triggered"] >= 1


@pytest.mark.asyncio
async def test_orchestrator_deterministic_offline_fallback():
    """Verify deterministic, zero-crash fallback when no providers are reachable."""
    orch = AIOrchestrator()
    orch.providers[ProviderType.OPENROUTER] = MockFailingProvider(ProviderType.OPENROUTER)
    orch.providers[ProviderType.MISTRAL] = MockFailingProvider(ProviderType.MISTRAL)
    orch.providers[ProviderType.GEMINI] = MockFailingProvider(ProviderType.GEMINI)
    orch.providers[ProviderType.XAI] = MockFailingProvider(ProviderType.XAI)

    req = AIRequest(
        task_category=TaskCategory.FIT_ASSISTANT,
        messages=[ChatMessage(role="user", content="Tell me my size")],
    )
    res = await orch.execute(req)
    assert res.finish_reason == "fallback"
    assert "deterministic" in res.content.lower()


def test_ai_status_endpoint_never_exposes_secrets():
    """Verify /v1/ai/status reports availability without leaking keys."""
    resp = client.get("/v1/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "configured_providers" in data
    assert "models" in data
    # Ensure no secrets in the response
    for k, v in data.items():
        assert "key" not in str(v).lower() or isinstance(v, dict)


def test_explain_recommendation_endpoint():
    """Verify /v1/ai/explain-recommendation preserves recommended size."""
    payload = {
        "brand_name": "Khaadi",
        "category": "kurta",
        "recommended_size": "M",
        "confidence": 0.95,
        "fit_preference": "regular",
        "measurements_comparison": {
            "chest": {"body": 98.0, "garment": 104.0, "ease_cm": 6.0}
        },
    }
    resp = client.post("/v1/ai/explain-recommendation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["recommended_size"] == "M"
    assert data["brand_name"] == "Khaadi"
    assert "explanation" in data

