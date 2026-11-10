"""Supabase client wrapper using service role key for backend operations."""

from typing import Optional
from supabase import Client, create_client
from app.config import settings

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Return a cached Supabase client or None if unconfigured."""
    global _supabase_client
    if _supabase_client is None:
        if settings.supabase_url and settings.supabase_service_key:
            _supabase_client = create_client(
                settings.supabase_url, settings.supabase_service_key
            )
    return _supabase_client


def set_supabase_client(client: Optional[Client]) -> None:
    """Override Supabase client (useful for unit tests and mocks)."""
    global _supabase_client
    _supabase_client = client

