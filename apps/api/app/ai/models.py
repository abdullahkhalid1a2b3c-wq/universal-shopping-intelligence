"""Data models for Multi-Provider AI Infrastructure."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskCategory(str, Enum):
    """Categorized AI tasks with dedicated model priorities and prompt optimizations."""
    FIT_ASSISTANT = "fit_assistant"
    SIZE_CHART_INTELLIGENCE = "size_chart_intelligence"
    PRODUCT_INTELLIGENCE = "product_intelligence"
    SHOPPING_ASSISTANCE = "shopping_assistance"
    RETAILER_ASSISTANCE = "retailer_assistance"


class ProviderType(str, Enum):
    """Supported AI providers."""
    MISTRAL = "mistral"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    XAI = "xai"
    OPENAI = "openai"


class ChatMessage(BaseModel):
    """Individual message in a conversation context."""
    role: str = Field(..., description="Role of the author ('system', 'user', or 'assistant')")
    content: str = Field(..., description="Message text content")


class AIRequest(BaseModel):
    """Normalized request passed to AI orchestration service."""
    task_category: TaskCategory = TaskCategory.FIT_ASSISTANT
    messages: List[ChatMessage] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    json_mode: bool = False
    json_schema: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None


class AIResponse(BaseModel):
    """Standardized response returned by any AI provider adapter."""
    content: str
    provider: ProviderType
    model: str
    tokens_used: Optional[int] = None
    duration_ms: float
    finish_reason: Optional[str] = "stop"
    fallback_used: bool = False
    structured_data: Optional[Dict[str, Any]] = None

