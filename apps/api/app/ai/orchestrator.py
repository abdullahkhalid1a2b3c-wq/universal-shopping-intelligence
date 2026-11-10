"""FitSense Central AI Orchestration Service.

Handles multi-provider model routing, task prioritization, automatic failover,
and token/cost tracking while strictly safeguarding customer privacy.
"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from app.ai.base import BaseAIProvider
from app.ai.models import AIRequest, AIResponse, ProviderType, TaskCategory
from app.ai.providers.gemini import GeminiAdapter
from app.ai.providers.mistral import MistralAdapter
from app.ai.providers.openrouter import OpenRouterAdapter
from app.ai.providers.xai import XAIAdapter
from app.config import settings

logger = logging.getLogger("fitsense.ai.orchestrator")


class AIOrchestrator:
    """Central AI orchestrator with task-based routing and automatic fallback."""

    def __init__(self):
        self.providers: Dict[ProviderType, BaseAIProvider] = {}
        self._init_providers()

        # Task routing priority rules
        self.task_routing: Dict[TaskCategory, List[ProviderType]] = {
            TaskCategory.FIT_ASSISTANT: [
                ProviderType.OPENROUTER,
                ProviderType.MISTRAL,
                ProviderType.GEMINI,
                ProviderType.XAI,
            ],
            TaskCategory.SIZE_CHART_INTELLIGENCE: [
                ProviderType.GEMINI,
                ProviderType.MISTRAL,
                ProviderType.OPENROUTER,
            ],
            TaskCategory.PRODUCT_INTELLIGENCE: [
                ProviderType.MISTRAL,
                ProviderType.OPENROUTER,
                ProviderType.GEMINI,
            ],
            TaskCategory.SHOPPING_ASSISTANCE: [
                ProviderType.OPENROUTER,
                ProviderType.MISTRAL,
                ProviderType.XAI,
            ],
            TaskCategory.RETAILER_ASSISTANCE: [
                ProviderType.MISTRAL,
                ProviderType.OPENROUTER,
                ProviderType.GEMINI,
            ],
        }

        # Usage and performance metrics
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "fallbacks_triggered": 0,
            "errors": 0,
        }

    def _init_providers(self):
        """Initialize provider adapters from environment configuration."""
        self.providers[ProviderType.OPENROUTER] = OpenRouterAdapter(
            api_key=settings.openrouter_api_key,
            default_model=settings.openrouter_model,
        )
        self.providers[ProviderType.MISTRAL] = MistralAdapter(
            api_key=settings.mistral_api_key,
            default_model=settings.mistral_model,
        )
        self.providers[ProviderType.GEMINI] = GeminiAdapter(
            api_key=settings.gemini_api_key,
            default_model=settings.gemini_model,
        )
        self.providers[ProviderType.XAI] = XAIAdapter(
            api_key=settings.xai_api_key,
            default_model=settings.xai_model,
        )

    def get_available_providers(self) -> List[ProviderType]:
        """List provider types with active credentials."""
        return [ptype for ptype, provider in self.providers.items() if provider.is_available()]

    def get_status(self) -> Dict[str, Any]:
        """Return provider configuration status and metrics without secrets."""
        return {
            "configured_providers": {
                ptype.value: provider.is_available() for ptype, provider in self.providers.items()
            },
            "available_count": len(self.get_available_providers()),
            "models": {
                ptype.value: provider.default_model for ptype, provider in self.providers.items()
            },
            "metrics": self.metrics,
        }

    async def execute(self, request: AIRequest) -> AIResponse:
        """Route request through prioritized providers with automatic fallback."""
        priorities = self.task_routing.get(request.task_category, [
            ProviderType.OPENROUTER,
            ProviderType.MISTRAL,
            ProviderType.GEMINI,
        ])

        candidates = [p for p in priorities if self.providers.get(p) and self.providers[p].is_available()]

        if not candidates:
            # Fallback when no external provider is configured
            return self._generate_local_fallback(request)

        last_error: Optional[Exception] = None
        attempt = 0

        for provider_type in candidates:
            attempt += 1
            provider = self.providers[provider_type]
            try:
                logger.info(f"Dispatching task '{request.task_category.value}' to provider '{provider_type.value}'")
                if request.json_mode:
                    res = await provider.generate_json(request)
                else:
                    res = await provider.generate_text(request)

                self.metrics["total_requests"] += 1
                if res.tokens_used:
                    self.metrics["total_tokens"] += res.tokens_used
                if attempt > 1:
                    res.fallback_used = True
                    self.metrics["fallbacks_triggered"] += 1

                return res

            except Exception as exc:
                last_error = exc
                self.metrics["errors"] += 1
                logger.warning(
                    f"Provider '{provider_type.value}' failed on task '{request.task_category.value}': {str(exc)}. "
                    "Initiating fallback."
                )

        # All candidates failed
        logger.error(f"All configured providers failed for task '{request.task_category.value}': {last_error}")
        return self._generate_local_fallback(request, error_context=str(last_error))

    def _generate_local_fallback(self, request: AIRequest, error_context: Optional[str] = None) -> AIResponse:
        """Generate a deterministic, privacy-safe fallback response when AI providers are unavailable."""
        self.metrics["total_requests"] += 1

        if request.task_category == TaskCategory.FIT_ASSISTANT:
            content = (
                "FitSense Assistant is currently operating in offline mode. "
                "Your clothing size recommendations are always calculated deterministically by our zero-ML fit engine "
                "using your exact body measurements and the brand's verified size chart. "
                "For immediate size advice, check the 'Find My Size' screen on any brand or product page."
            )
        elif request.task_category == TaskCategory.SIZE_CHART_INTELLIGENCE:
            content = "{}"
        else:
            content = (
                "FitSense Intelligence is currently operating in offline mode. "
                "Please verify brand details and size tables directly on the official brand page."
            )

        return AIResponse(
            content=content,
            provider=ProviderType.OPENROUTER,
            model="deterministic-fallback",
            tokens_used=0,
            duration_ms=0.0,
            finish_reason="fallback",
            fallback_used=True,
            structured_data={} if request.json_mode else None,
        )


# Global singleton instance
ai_orchestrator = AIOrchestrator()

