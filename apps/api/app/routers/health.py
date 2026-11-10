"""Health-check router."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return API health status and version."""
    return {"status": "ok", "version": settings.app_version}

