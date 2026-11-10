"""Abstract Base Class for FitSense AI Provider Adapters."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Optional
from app.ai.models import AIRequest, AIResponse, ProviderType


class BaseAIProvider(ABC):
    """Abstract interface that all concrete AI provider adapters must implement."""

    def __init__(self, api_key: Optional[str], default_model: str):
        self.api_key = api_key.strip() if api_key else None
        self.default_model = default_model

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the unique provider type enum."""
        pass

    def is_available(self) -> bool:
        """Check whether the provider has a valid non-empty API key configured."""
        return bool(self.api_key)

    @abstractmethod
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Execute text generation and return a normalized AIResponse."""
        pass

    @abstractmethod
    async def generate_json(self, request: AIRequest) -> AIResponse:
        """Execute structured JSON generation and return parsed dict in response."""
        pass

    @abstractmethod
    async def stream_text(self, request: AIRequest) -> AsyncIterator[str]:
        """Stream response chunks asynchronously."""
        pass

