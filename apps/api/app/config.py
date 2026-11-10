"""Application configuration loaded from environment variables."""

from typing import Any, Dict, Optional
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    Values are read from environment variables or a .env file.
    Secret values are never logged or displayed in repr.
    """

    # Supabase Configuration
    supabase_url: str = ""
    supabase_project_id: str = "zoxobxpjgottuhrezgie"
    supabase_service_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SECRET_KEY"),
    )
    supabase_publishable_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"),
    )
    supabase_jwt_secret: str = ""
    supabase_jwks_url: Optional[str] = "https://zoxobxpjgottuhrezgie.supabase.co/auth/v1/.well-known/jwks.json"
    allowed_origins: str = "http://localhost:3000"
    app_version: str = "0.1.0"
    sentry_dsn: Optional[str] = None

    # AI Provider API Keys (Canonical with legacy aliases)
    openrouter_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("OPENROUTER_API_KEY", "OPEN_ROUTER_API_KEY"),
    )
    mistral_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("MISTRAL_API_KEY"),
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY"),
    )
    xai_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("XAI_API_KEY", "GROK_API_KEY"),
    )

    # AI Models (Optimized for active provider availability)
    openrouter_model: str = "google/gemini-2.5-flash"
    mistral_model: str = "open-mistral-7b"
    gemini_model: str = "gemini-flash-latest"
    xai_model: str = "grok-2"

    @model_validator(mode="after")
    def inspect_gemini_key_in_model(self) -> "Settings":
        """Handle cases where Gemini API key was saved in GEMINI_MODEL."""
        raw_model = self.gemini_model
        if raw_model and (raw_model.startswith("AQ.") or raw_model.startswith("AIzaSy") or len(raw_model) > 30):
            if not self.gemini_api_key:
                self.gemini_api_key = raw_model
            self.gemini_model = "gemini-flash-latest"
        return self

    model_config = {"env_file": [".env", "apps/api/.env"], "extra": "ignore"}

    def get_ai_provider_status(self) -> Dict[str, bool]:
        """Safely report provider configuration status without revealing credentials."""
        return {
            "openrouter": bool(self.openrouter_api_key and self.openrouter_api_key.strip()),
            "mistral": bool(self.mistral_api_key and self.mistral_api_key.strip()),
            "gemini": bool(self.gemini_api_key and self.gemini_api_key.strip()),
            "xai": bool(self.xai_api_key and self.xai_api_key.strip()),
        }

    def safe_repr(self) -> Dict[str, Any]:
        """Return a representation of settings with all secrets redacted."""
        return {
            "supabase_url": self.supabase_url,
            "supabase_jwks_url": self.supabase_jwks_url,
            "allowed_origins": self.allowed_origins,
            "app_version": self.app_version,
            "ai_providers": self.get_ai_provider_status(),
            "models": {
                "openrouter": self.openrouter_model,
                "mistral": self.mistral_model,
                "gemini": self.gemini_model,
                "xai": self.xai_model,
            },
        }

    def __repr__(self) -> str:
        return f"Settings({self.safe_repr()})"


settings = Settings()
