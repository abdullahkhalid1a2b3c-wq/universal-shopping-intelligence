"""Products router for lookup and catalogue inspection."""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.limiter import limiter
from app.supabase_client import get_supabase_client
from app.utils.url import normalize_product_url

router = APIRouter(prefix="/v1/products", tags=["products"])


@router.get("/lookup")
@limiter.limit("60/minute")
async def lookup_product_by_url(
    request: Request,
    url: str = Query(..., description="E-commerce product page URL"),
) -> Dict[str, Any]:
    """Look up a product in the FitSense catalogue by its URL."""
    canonical = normalize_product_url(url)
    client = get_supabase_client()

    if not client:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"covered": False, "detail": "Catalogue unavailable"},
        )

    response = (
        client.table("products")
        .select(
            "id, name, category, gender_category, product_url, canonical_url, external_id, size_chart_id, fabric, stretch_pct, thickness, fit_cut, is_active, is_demo, retailers(id, name, slug, status), size_charts(id, name, verified_at, is_demo, measured_as)"
        )
        .or_(f"canonical_url.eq.{canonical},product_url.eq.{url}")
        .limit(1)
        .execute()
    )

    if not response.data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"covered": False},
        )

    item = response.data[0]
    return {
        "covered": True,
        "product": {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "gender_category": item.get("gender_category"),
            "product_url": item["product_url"],
            "canonical_url": item["canonical_url"],
            "fabric": item.get("fabric"),
            "stretch_pct": float(item.get("stretch_pct", 0)),
            "thickness": item.get("thickness"),
            "fit_cut": item.get("fit_cut"),
            "is_demo": item.get("is_demo", False),
        },
        "retailer": item.get("retailers"),
        "size_chart": item.get("size_charts"),
    }

