"""Admin router for system administration, retailer approval, adapter management, and data quality auditing."""

from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from app.auth import require_admin_user
from app.limiter import limiter
from app.supabase_client import get_supabase_client
from app.validation.size_chart import run_size_chart_sanity_checks

router = APIRouter(prefix="/v1/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class UpdateRetailerStatusPayload(BaseModel):
    """Payload to update retailer status."""

    status: Literal["pending", "verified", "suspended"]


class StoreAdapterPayload(BaseModel):
    """Payload to create or update a store DOM scraping adapter."""

    platform: Literal["shopify", "woocommerce", "custom"] = "custom"
    selectors: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True


# ---------------------------------------------------------------------------
# Retailer Approval & Management
# ---------------------------------------------------------------------------


@router.get("/retailers")
@limiter.limit("60/minute")
async def list_all_retailers(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> List[Dict[str, Any]]:
    """List all retailers with member count and product count."""
    client = get_supabase_client()
    if not client:
        return []

    res = (
        client.table("retailers")
        .select("id, name, slug, website_domain, logo_url, supports_cod, return_policy_url, status, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    retailers = res.data or []

    # Enrich with product and member counts
    for ret in retailers:
        ret_id = ret["id"]
        try:
            prod_cnt = client.table("products").select("id", count="exact").eq("retailer_id", ret_id).execute()
            ret["product_count"] = prod_cnt.count or 0
        except Exception:
            ret["product_count"] = 0

        try:
            mem_cnt = client.table("retailer_members").select("id", count="exact").eq("retailer_id", ret_id).execute()
            ret["member_count"] = mem_cnt.count or 0
        except Exception:
            ret["member_count"] = 0

    return retailers


@router.patch("/retailers/{retailer_id}/status")
@limiter.limit("30/minute")
async def update_retailer_status(
    request: Request,
    retailer_id: str,
    payload: UpdateRetailerStatusPayload,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> Dict[str, Any]:
    """Approve (verify), suspend, or reset a retailer's status."""
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable.",
        )

    res = (
        client.table("retailers")
        .update({"status": payload.status})
        .eq("id", retailer_id)
        .execute()
    )

    if not res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retailer '{retailer_id}' not found.",
        )

    return {"status": "success", "retailer": res.data[0]}


# ---------------------------------------------------------------------------
# Coverage Requests
# ---------------------------------------------------------------------------


@router.get("/coverage")
@limiter.limit("60/minute")
async def list_coverage_summary(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> List[Dict[str, Any]]:
    """List customer coverage requests grouped by domain with count."""
    client = get_supabase_client()
    if not client:
        return []

    res = (
        client.table("coverage_requests")
        .select("domain, page_url, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    # Group by domain
    domain_counts: Dict[str, Dict[str, Any]] = {}
    for r in res.data or []:
        dom = r.get("domain", "").lower()
        if not dom:
            continue
        if dom not in domain_counts:
            domain_counts[dom] = {
                "domain": dom,
                "request_count": 0,
                "sample_urls": [],
                "latest_request": r.get("created_at"),
            }
        domain_counts[dom]["request_count"] += 1
        if len(domain_counts[dom]["sample_urls"]) < 3 and r.get("page_url"):
            domain_counts[dom]["sample_urls"].append(r["page_url"])

    sorted_domains = sorted(
        domain_counts.values(), key=lambda x: x["request_count"], reverse=True
    )
    return sorted_domains


# ---------------------------------------------------------------------------
# Store Adapters
# ---------------------------------------------------------------------------


@router.get("/adapters")
@limiter.limit("60/minute")
async def list_store_adapters(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> List[Dict[str, Any]]:
    """List all store adapters for DOM scraping."""
    client = get_supabase_client()
    if not client:
        return []

    res = client.table("store_adapters").select("*").order("domain").execute()
    return res.data or []


@router.put("/adapters/{domain}")
@limiter.limit("30/minute")
async def upsert_store_adapter(
    request: Request,
    domain: str,
    payload: StoreAdapterPayload,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> Dict[str, Any]:
    """Create or update a store adapter configuration."""
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable.",
        )

    clean_domain = domain.strip().lower()
    res = (
        client.table("store_adapters")
        .upsert(
            {
                "domain": clean_domain,
                "platform": payload.platform,
                "selectors": payload.selectors,
                "is_enabled": payload.is_enabled,
            },
            on_conflict="domain",
        )
        .execute()
    )
    return {"status": "success", "adapter": res.data[0] if res.data else None}


# ---------------------------------------------------------------------------
# Data Quality Audit
# ---------------------------------------------------------------------------


@router.get("/data-quality")
@limiter.limit("30/minute")
async def audit_data_quality(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_user),
) -> Dict[str, Any]:
    """Audit size charts to surface unverified, demo, or warned charts."""
    client = get_supabase_client()
    if not client:
        return {
            "unverified_charts": [],
            "demo_charts": [],
            "charts_with_warnings": [],
            "total_charts": 0,
        }

    # Fetch all size charts with retailer info
    charts_res = (
        client.table("size_charts")
        .select("id, name, category, gender_category, measured_as, unit_source, verified_at, is_demo, needs_review, retailer_id, retailers(id, name, slug)")
        .order("created_at", desc=True)
        .execute()
    )

    all_charts = charts_res.data or []
    unverified_charts: List[Dict[str, Any]] = []
    demo_charts: List[Dict[str, Any]] = []
    charts_with_warnings: List[Dict[str, Any]] = []
    needs_review_charts: List[Dict[str, Any]] = []

    for chart in all_charts:
        chart_id = chart["id"]
        is_verified = bool(chart.get("verified_at"))
        is_demo = bool(chart.get("is_demo"))
        needs_review = bool(chart.get("needs_review", False))

        ret_info = chart.get("retailers") or {}
        retailer_name = ret_info.get("name", "Unknown Retailer")

        entry = {
            "id": chart_id,
            "name": chart["name"],
            "category": chart.get("category"),
            "gender_category": chart.get("gender_category"),
            "measured_as": chart.get("measured_as"),
            "unit_source": chart.get("unit_source"),
            "retailer_name": retailer_name,
            "retailer_id": chart.get("retailer_id"),
            "is_demo": is_demo,
            "needs_review": needs_review,
            "verified_at": chart.get("verified_at"),
        }

        if not is_verified:
            unverified_charts.append(entry)

        if is_demo:
            demo_charts.append(entry)

        if needs_review:
            needs_review_charts.append(entry)

        # Check rows for sanity check warnings
        rows_res = (
            client.table("size_chart_rows")
            .select("size_label, measurement_key, value_cm")
            .eq("size_chart_id", chart_id)
            .execute()
        )
        rows_data = rows_res.data or []
        if rows_data:
            sanity = run_size_chart_sanity_checks(
                rows=rows_data,
                measured_as=chart.get("measured_as", "circumference"),
                category=chart.get("category"),
                gender_category=chart.get("gender_category"),
            )
            if sanity.warnings or sanity.errors:
                entry_warn = dict(entry)
                entry_warn["warnings"] = sanity.warnings
                entry_warn["errors"] = sanity.errors
                charts_with_warnings.append(entry_warn)

    # Compute Recommendation Accuracy Metric
    # Share of feedback marked perfect or slightly tight/loose (acceptable) where user followed recommended size
    accuracy_metric = {"followed_recommendation_count": 0, "acceptable_fit_count": 0, "accuracy_pct": 0.0}
    try:
        fb_all = client.table("fit_feedback").select("user_id, product_id, size_bought, fit_result").execute().data or []
        rec_all = client.table("recommendations").select("user_id, product_id, recommended_size").execute().data or []
        rec_map = {(r["user_id"], r["product_id"]): r["recommended_size"].strip().upper() for r in rec_all if r.get("user_id") and r.get("product_id")}

        followed_count = 0
        acceptable_count = 0
        for fb in fb_all:
            u_id = fb.get("user_id")
            p_id = fb.get("product_id")
            if not u_id or not p_id:
                continue
            rec_size = rec_map.get((u_id, p_id))
            if rec_size and rec_size == fb.get("size_bought", "").strip().upper():
                followed_count += 1
                if fb.get("fit_result") in ("perfect", "slightly_tight", "slightly_loose"):
                    acceptable_count += 1

        accuracy_pct = round((acceptable_count / followed_count) * 100, 1) if followed_count > 0 else 0.0
        accuracy_metric = {
            "followed_recommendation_count": followed_count,
            "acceptable_fit_count": acceptable_count,
            "accuracy_pct": accuracy_pct,
        }
    except Exception:
        pass

    return {
        "unverified_charts": unverified_charts,
        "demo_charts": demo_charts,
        "charts_with_warnings": charts_with_warnings,
        "needs_review_charts": needs_review_charts,
        "total_charts": len(all_charts),
        "unverified_count": len(unverified_charts),
        "demo_count": len(demo_charts),
        "warnings_count": len(charts_with_warnings),
        "needs_review_count": len(needs_review_charts),
        "accuracy": accuracy_metric,
    }
