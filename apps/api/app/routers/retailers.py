"""Retailers router for public directory and product catalogue listing.

Supports Pakistan-wide brand exploration, A-Z filtering, and product lookups.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Request, status

from app.data.pakistan_brands import (
    PAKISTAN_BRANDS,
    get_all_brands,
    get_brand_by_slug,
    get_brand_products,
)
from app.limiter import limiter
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/v1/retailers", tags=["retailers"])


@router.get("/directory")
@limiter.limit("60/minute")
async def get_brand_directory(
    request: Request,
    category: Optional[str] = Query(None, description="Category filter (e.g. eastern, western, unstitched)"),
    audience: Optional[str] = Query(None, description="Audience filter (women, men, kids)"),
    letter: Optional[str] = Query(None, description="A-Z initial letter filter"),
    q: Optional[str] = Query(None, description="Search keyword for name or domain"),
) -> Dict[str, Any]:
    """Retrieve the Pakistan-wide fashion brand directory with multi-faceted filtering."""
    brands = get_all_brands(
        category=category,
        audience=audience,
        letter=letter,
        query=q,
    )
    return {
        "count": len(brands),
        "brands": brands,
        "filters": {
            "category": category,
            "audience": audience,
            "letter": letter,
            "q": q,
        },
    }


@router.get("")
@limiter.limit("60/minute")
async def list_verified_retailers(
    request: Request,
    include_demo: bool = False,
) -> List[Dict[str, Any]]:
    """List all fashion retailers available in FitSense.
    
    Returns database-registered retailers merged with the verified Pakistani brand directory.
    """
    client = get_supabase_client()
    db_retailers: List[Dict[str, Any]] = []

    if client:
        try:
            query = client.table("retailers").select(
                "id, name, slug, website_domain, logo_url, supports_cod, return_policy_url, status, is_demo"
            )
            if include_demo:
                query = query.or_("status.eq.verified,is_demo.eq.true")
            else:
                query = query.eq("status", "verified")

            res = query.order("name").execute()
            db_retailers = res.data or []
        except Exception:
            db_retailers = []

    if db_retailers:
        return db_retailers

    # Fallback to curated catalog if DB table is unpopulated
    return [
        {
            "id": b["id"],
            "name": b["name"],
            "slug": b["slug"],
            "website_domain": b["website_domain"],
            "logo_url": b["logo_url"],
            "supports_cod": b["supports_cod"],
            "return_policy_url": b["return_policy_url"],
            "status": "verified",
            "is_demo": False,
            "categories": b.get("categories", []),
            "target_audience": b.get("target_audience", []),
            "official_size_chart_url": b.get("official_size_chart_url"),
            "description": b.get("description"),
        }
        for b in PAKISTAN_BRANDS
    ]


@router.get("/{slug}")
@limiter.limit("60/minute")
async def get_brand_details(request: Request, slug: str) -> Dict[str, Any]:
    """Retrieve detailed information and size guide availability for a specific brand."""
    # Check directory catalog first
    brand = get_brand_by_slug(slug)
    if brand:
        return brand

    # Fallback to Supabase database lookup
    client = get_supabase_client()
    if client:
        try:
            res = (
                client.table("retailers")
                .select("id, name, slug, website_domain, logo_url, supports_cod, return_policy_url, status, is_demo")
                .eq("slug", slug.lower().strip())
                .limit(1)
                .execute()
            )
            if res.data:
                return res.data[0]
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Brand '{slug}' not found in directory",
    )


@router.get("/{slug}/products")
@limiter.limit("60/minute")
async def list_retailer_products(request: Request, slug: str) -> List[Dict[str, Any]]:
    """List active products for a specific retailer by their slug."""
    clean_slug = slug.lower().strip()
    client = get_supabase_client()

    # 1. Try database lookup if client is configured
    if client:
        try:
            ret_res = (
                client.table("retailers")
                .select("id, name, status")
                .eq("slug", clean_slug)
                .limit(1)
                .execute()
            )
            if ret_res.data:
                retailer_id = ret_res.data[0]["id"]
                prod_res = (
                    client.table("products")
                    .select(
                        "id, name, category, gender_category, product_url, canonical_url, external_id, fabric, stretch_pct, thickness, season, is_demo, fit_cut"
                    )
                    .eq("retailer_id", retailer_id)
                    .eq("is_active", True)
                    .order("name")
                    .execute()
                )
                if prod_res.data:
                    return prod_res.data
        except Exception:
            pass

    # 2. Check catalog products for verified Pakistani brand directory
    catalog_prods = get_brand_products(clean_slug)
    if catalog_prods:
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "gender_category": p["gender_category"],
                "product_url": p["product_url"],
                "canonical_url": p["canonical_url"],
                "external_id": p["external_id"],
                "fabric": p["fabric"],
                "stretch_pct": p["stretch_pct"],
                "thickness": p["thickness"],
                "season": p["season"],
                "fit_cut": p["fit_cut"],
                "is_demo": p["is_demo"],
            }
            for p in catalog_prods
        ]

    # 3. Not found in either DB or catalog
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Retailer '{clean_slug}' not found",
    )
