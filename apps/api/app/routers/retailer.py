"""Retailer portal router for catalogue management, size charts, validation, and analytics."""

from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.auth import get_current_user, require_retailer_user, verify_retailer_access
from app.limiter import limiter
from app.supabase_client import get_supabase_client
from app.validation.csv_parser import (
    ParsedSizeChartCSV,
    generate_size_chart_csv_template,
    parse_size_chart_csv,
)
from app.validation.product_csv import (
    ParsedProductsCSV,
    generate_product_csv_template,
    parse_products_csv,
)
from app.validation.size_chart import SanityCheckResult, run_size_chart_sanity_checks

router = APIRouter(prefix="/v1/retailer", tags=["retailer"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ValidateSizeChartPayload(BaseModel):
    """Payload to validate size chart measurements."""

    rows: List[Dict[str, Any]]
    measured_as: Literal["flat", "circumference"] = "circumference"
    category: Optional[str] = None
    gender_category: Optional[str] = None


class ParseSizeChartCSVPayload(BaseModel):
    """Payload to parse and validate CSV size chart."""

    csv_content: str
    unit_source: Literal["cm", "in"] = "cm"
    measured_as: Literal["flat", "circumference"] = "circumference"
    category: Optional[str] = None
    gender_category: Optional[str] = None


class ParseProductsCSVPayload(BaseModel):
    """Payload to parse and validate product bulk import CSV."""

    csv_content: str


class AddMemberPayload(BaseModel):
    """Payload to add a team member to a retailer."""

    retailer_id: str
    email: str
    member_role: Literal["owner", "editor"] = "editor"


# ---------------------------------------------------------------------------
# Size Chart Endpoints
# ---------------------------------------------------------------------------


@router.post("/size-charts/validate", response_model=SanityCheckResult)
@limiter.limit("60/minute")
async def validate_size_chart(
    request: Request,
    payload: ValidateSizeChartPayload,
    user: Dict[str, Any] = Depends(require_retailer_user),
) -> SanityCheckResult:
    """Run automated sanity checks on size chart rows."""
    return run_size_chart_sanity_checks(
        rows=payload.rows,
        measured_as=payload.measured_as,
        category=payload.category,
        gender_category=payload.gender_category,
    )


@router.post("/size-charts/parse-csv", response_model=ParsedSizeChartCSV)
@limiter.limit("30/minute")
async def parse_and_validate_size_chart_csv(
    request: Request,
    payload: ParseSizeChartCSVPayload,
    user: Dict[str, Any] = Depends(require_retailer_user),
) -> ParsedSizeChartCSV:
    """Parse size chart CSV, convert units if necessary, and execute sanity checks."""
    return parse_size_chart_csv(
        csv_content=payload.csv_content,
        unit_source=payload.unit_source,
        measured_as=payload.measured_as,
        category=payload.category,
        gender_category=payload.gender_category,
    )


@router.get("/size-charts/template", response_class=PlainTextResponse)
def get_size_chart_template(
    category: Optional[str] = Query(None, description="Optional clothing category (e.g. shirt, trouser)"),
) -> str:
    """Download a CSV template for size chart data entry."""
    return generate_size_chart_csv_template(category=category)


# ---------------------------------------------------------------------------
# Product Bulk Import Endpoints
# ---------------------------------------------------------------------------


@router.post("/products/import-csv", response_model=ParsedProductsCSV)
@limiter.limit("30/minute")
async def validate_product_import_csv(
    request: Request,
    payload: ParseProductsCSVPayload,
    user: Dict[str, Any] = Depends(require_retailer_user),
) -> ParsedProductsCSV:
    """Parse and validate bulk product import CSV row-by-row."""
    return parse_products_csv(csv_content=payload.csv_content)


@router.get("/products/template", response_class=PlainTextResponse)
def get_products_template() -> str:
    """Download a CSV template for product bulk upload."""
    return generate_product_csv_template()


# ---------------------------------------------------------------------------
# Team Members Management
# ---------------------------------------------------------------------------


@router.post("/members")
@limiter.limit("20/minute")
async def add_retailer_member(
    request: Request,
    payload: AddMemberPayload,
    user: Dict[str, Any] = Depends(require_retailer_user),
) -> Dict[str, Any]:
    """Add an existing user by email as a member (editor or owner) of a retailer."""
    if not verify_retailer_access(payload.retailer_id, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage members for this retailer.",
        )

    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable.",
        )

    # 1. Lookup user in profiles / auth by email
    # Query profiles table or auth admin
    target_user_id = None
    email_clean = payload.email.strip().lower()

    try:
        # Check profiles where display_name or metadata matches, or auth users
        res = client.table("profiles").select("user_id, display_name").ilike("display_name", f"%{email_clean}%").limit(1).execute()
        if res.data:
            target_user_id = res.data[0]["user_id"]
    except Exception:
        pass

    if not target_user_id:
        try:
            admin_users = client.auth.admin.list_users()
            for u in admin_users:
                if u.email and u.email.lower() == email_clean:
                    target_user_id = u.id
                    break
        except Exception:
            pass

    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email '{payload.email}'. The user must register an account first.",
        )

    # Insert into retailer_members
    try:
        insert_res = (
            client.table("retailer_members")
            .upsert(
                {
                    "retailer_id": payload.retailer_id,
                    "user_id": target_user_id,
                    "member_role": payload.member_role,
                },
                on_conflict="retailer_id,user_id",
            )
            .execute()
        )
        return {"status": "success", "data": insert_res.data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add retailer member: {e}",
        )


# ---------------------------------------------------------------------------
# Retailer Analytics
# ---------------------------------------------------------------------------


@router.get("/analytics")
@limiter.limit("60/minute")
async def get_retailer_analytics(
    request: Request,
    retailer_id: str = Query(..., description="UUID of the retailer"),
    user: Dict[str, Any] = Depends(require_retailer_user),
) -> Dict[str, Any]:
    """Get aggregated analytics for a retailer's products.

    Returns:
    - recommendations_per_week: line chart data
    - fit_feedback_distribution: stacked bar breakdown per product and size
    - problem_products: products where >25% of feedback in a size is too tight or too loose (>= 10 responses)
    - total_returns: return count
    - plain_language_hints: actionable recommendations
    """
    if not verify_retailer_access(retailer_id, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view analytics for this retailer.",
        )

    client = get_supabase_client()
    if not client:
        return {
            "recommendations_per_week": [],
            "feedback_distribution": [],
            "problem_products": [],
            "total_returns": 0,
            "plain_language_hints": [],
        }

    # 1. Fetch weekly recommendations
    weekly_res = (
        client.table("v_product_recommendation_counts")
        .select("week_start, recommendation_count, product_name")
        .eq("retailer_id", retailer_id)
        .order("week_start")
        .execute()
    )

    # Group recommendations by week
    weeks_map: Dict[str, int] = {}
    for r in weekly_res.data or []:
        ws = str(r.get("week_start", ""))[:10]
        weeks_map[ws] = weeks_map.get(ws, 0) + int(r.get("recommendation_count", 0))

    weekly_series = [{"week": k, "count": v} for k, v in sorted(weeks_map.items())]

    # 2. Fetch feedback statistics
    fb_res = (
        client.table("v_product_fit_stats")
        .select("*")
        .eq("retailer_id", retailer_id)
        .execute()
    )

    feedback_distribution: List[Dict[str, Any]] = []
    problem_products: List[Dict[str, Any]] = []
    plain_language_hints: List[str] = []
    total_returns = 0

    for item in fb_res.data or []:
        total_fb = int(item.get("total_feedback", 0))
        returns = int(item.get("return_count", 0))
        total_returns += returns

        prod_name = item.get("product_name", "Unknown Product")
        size = item.get("size_bought", "Standard")
        pct_tight = float(item.get("pct_too_tight", 0))
        pct_perfect = float(item.get("pct_perfect", 0))
        pct_loose = float(item.get("pct_too_loose", 0))

        dist_entry = {
            "product_id": item.get("product_id"),
            "product_name": prod_name,
            "size_label": size,
            "total_feedback": total_fb,
            "pct_too_tight": pct_tight,
            "pct_perfect": pct_perfect,
            "pct_too_loose": pct_loose,
            "return_count": returns,
        }
        feedback_distribution.append(dist_entry)

        # Check problem threshold (> 25% tight or loose)
        is_too_tight = pct_tight > 25.0
        is_too_loose = pct_loose > 25.0

        if is_too_tight or is_too_loose:
            if total_fb >= 10:
                problem_type = "runs small (too tight)" if is_too_tight else "runs large (too loose)"
                problem_pct = pct_tight if is_too_tight else pct_loose
                dimension_hint = "chest measurement" if "shirt" in prod_name.lower() or "top" in prod_name.lower() or "kurta" in prod_name.lower() else "waist measurement"

                hint = (
                    f"Size {size} of '{prod_name}' runs {problem_type.split()[1]} for {problem_pct:.0f}% of buyers "
                    f"({total_fb} responses). Check the {dimension_hint} in the size chart."
                )
                plain_language_hints.append(hint)

                problem_products.append(
                    {
                        "product_name": prod_name,
                        "size_label": size,
                        "problem_type": problem_type,
                        "percentage": problem_pct,
                        "total_responses": total_fb,
                        "has_sufficient_sample": True,
                        "hint": hint,
                    }
                )
            else:
                problem_products.append(
                    {
                        "product_name": prod_name,
                        "size_label": size,
                        "problem_type": "potential issue",
                        "percentage": max(pct_tight, pct_loose),
                        "total_responses": total_fb,
                        "has_sufficient_sample": False,
                        "note": f"Sample size too small ({total_fb}/10 responses) to flag as confirmed problem.",
                    }
                )

    # Fetch size charts flagged for review
    charts_needing_review: List[Dict[str, Any]] = []
    try:
        cnr_res = (
            client.table("size_charts")
            .select("id, name, category, gender_category, needs_review")
            .eq("retailer_id", retailer_id)
            .eq("needs_review", True)
            .execute()
        )
        charts_needing_review = cnr_res.data or []
    except Exception:
        charts_needing_review = []

    return {
        "retailer_id": retailer_id,
        "recommendations_per_week": weekly_series,
        "feedback_distribution": feedback_distribution,
        "problem_products": problem_products,
        "charts_needing_review": charts_needing_review,
        "charts_needing_review_count": len(charts_needing_review),
        "total_returns": total_returns,
        "plain_language_hints": plain_language_hints,
    }
