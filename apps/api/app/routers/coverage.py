"""Coverage requests router for submitting unsupported brand URLs."""

from urllib.parse import urlparse
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, HttpUrl

from app.auth import get_optional_user
from app.limiter import limiter
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/v1/coverage-requests", tags=["coverage"])


class CoverageRequestPayload(BaseModel):
    """Payload to request support for a fashion page or domain."""

    page_url: str
    domain: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_coverage_request(
    request: Request,
    payload: CoverageRequestPayload,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> Dict[str, Any]:
    """Submit a URL for a retailer or product page not yet supported by FitSense."""
    url = payload.page_url.strip()
    domain = payload.domain
    if not domain:
        domain = urlparse(url).netloc.lower()

    client = get_supabase_client()
    user_id = user.get("id") if user else None

    if client:
        res = (
            client.table("coverage_requests")
            .insert(
                {
                    "user_id": user_id,
                    "page_url": url,
                    "domain": domain,
                }
            )
            .execute()
        )
        return {"status": "received", "data": res.data}

    return {"status": "received", "domain": domain, "page_url": url}

