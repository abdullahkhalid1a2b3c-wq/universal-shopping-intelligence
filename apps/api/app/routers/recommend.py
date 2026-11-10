"""Recommendation router connecting user measurements to the pure fit engine."""

from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.auth import get_optional_user
from app.fit.engine import compute_fit_recommendation
from app.fit.explain import generate_explanation
from app.fit.models import (
    BodyMeasurementsInput,
    FitRecommendationOutput,
    ProductAttributesInput,
    SizeChartRowInput,
)
from app.limiter import limiter
from app.supabase_client import get_supabase_client
from app.utils.url import normalize_product_url

router = APIRouter(prefix="/v1", tags=["recommendations"])


class RecommendRequest(BaseModel):
    """Payload to request a fit recommendation."""

    product_id: Optional[str] = None
    product_url: Optional[str] = None
    fit_preference: Optional[Literal["fitted", "regular", "loose"]] = None
    measurements: Optional[BodyMeasurementsInput] = None


class RecommendResponse(BaseModel):
    """API response containing recommendation and localized explanation."""

    recommendation: FitRecommendationOutput
    explanation: str


async def _execute_recommendation_computation(
    client: Any,
    product: Dict[str, Any],
    category: str,
    size_chart: Dict[str, Any],
    chart_rows: List[SizeChartRowInput],
    payload: RecommendRequest,
    lang: str,
    user: Optional[Dict[str, Any]],
) -> RecommendResponse:
    """Execute deterministic fit calculation and consent-safe record persistence."""
    body_input = payload.measurements
    fit_pref = payload.fit_preference
    has_store_consent = False

    if user and client:
        user_id = user["id"]
        # Check consent for storing measurements
        try:
            consent_res = (
                client.table("consents")
                .select("granted")
                .eq("user_id", user_id)
                .eq("consent_type", "store_measurements")
                .limit(1)
                .execute()
            )
            if consent_res.data and consent_res.data[0].get("granted"):
                has_store_consent = True
        except Exception:
            pass

        # Load measurements if not provided in payload
        if body_input is None:
            try:
                bm_res = (
                    client.table("body_measurements")
                    .select("*")
                    .eq("user_id", user_id)
                    .limit(1)
                    .execute()
                )
                if bm_res.data:
                    bm = bm_res.data[0]
                    body_input = BodyMeasurementsInput(
                        chest_cm=bm.get("chest_cm"),
                        waist_cm=bm.get("waist_cm"),
                        hip_cm=bm.get("hip_cm"),
                        shoulder_cm=bm.get("shoulder_cm"),
                        sleeve_cm=bm.get("sleeve_cm"),
                        inseam_cm=bm.get("inseam_cm"),
                        thigh_cm=bm.get("thigh_cm"),
                        torso_length_cm=bm.get("torso_length_cm"),
                        kameez_length_cm=bm.get("kameez_length_cm"),
                    )
            except Exception:
                pass

        # Load fit preference if not provided
        if fit_pref is None:
            try:
                pref_res = (
                    client.table("fit_preferences")
                    .select("fit")
                    .eq("user_id", user_id)
                    .eq("category", category)
                    .limit(1)
                    .execute()
                )
                if pref_res.data:
                    fit_pref = pref_res.data[0].get("fit")
            except Exception:
                pass

    if body_input is None:
        body_input = BodyMeasurementsInput()

    if fit_pref is None:
        fit_pref = "regular"

    # Compute deterministic fit recommendation
    prod_attrs = ProductAttributesInput(
        stretch_pct=float(product.get("stretch_pct", 0) or 0),
        thickness=product.get("thickness"),
        fit_cut=product.get("fit_cut"),
        fabric=product.get("fabric"),
    )

    rec_result = compute_fit_recommendation(
        category=category,
        body=body_input,
        chart_rows=chart_rows,
        fit_preference=fit_pref,
        product=prod_attrs,
        measured_as=size_chart.get("measured_as", "circumference"),
        chart_verified=bool(size_chart.get("verified_at")),
        is_demo=bool(size_chart.get("is_demo", False)),
    )

    explanation = generate_explanation(rec_result.explanation_keys, lang=lang)

    # Persist recommendation history if signed in
    if user and client:
        inputs_snapshot: Dict[str, Any] = {
            "category": category,
            "fit_preference": fit_pref,
            "has_measurements": body_input.chest_cm is not None or body_input.waist_cm is not None,
        }
        if has_store_consent:
            inputs_snapshot["measurements"] = body_input.model_dump(exclude_none=True)

        try:
            client.table("recommendations").insert(
                {
                    "user_id": user["id"],
                    "product_id": product.get("id"),
                    "recommended_size": rec_result.recommended_size,
                    "confidence_score": rec_result.confidence_score,
                    "confidence_label": rec_result.confidence_label,
                    "inputs_snapshot": inputs_snapshot,
                }
            ).execute()
        except Exception:
            pass

    return RecommendResponse(recommendation=rec_result, explanation=explanation)


@router.post("/recommend", response_model=RecommendResponse)
@limiter.limit("30/minute")
async def get_recommendation(
    request: Request,
    payload: RecommendRequest,
    lang: str = Query("en", description="Preferred explanation language (en, ur, ur-roman)"),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
) -> RecommendResponse:
    """Generate a size recommendation with confidence score and localized explanation."""
    client = get_supabase_client()

    # 1. Check if requesting a standard directory catalog product
    if payload.product_id and payload.product_id.startswith("cat-"):
        from app.data.pakistan_brands import get_catalog_product
        catalog_prod = get_catalog_product(payload.product_id)
        if catalog_prod:
            product = catalog_prod
            category = product["category"]
            size_chart = {"measured_as": "circumference", "verified_at": "2026-01-01T00:00:00Z", "is_demo": False}
            chart_rows = [
                SizeChartRowInput(
                    size_label=r["size_label"],
                    sort_order=r.get("sort_order", 0),
                    measurement_key=r["measurement_key"],
                    value_cm=float(r["value_cm"]),
                )
                for r in product.get("size_chart_rows", [])
            ]
            return await _execute_recommendation_computation(
                client=client,
                product=product,
                category=category,
                size_chart=size_chart,
                chart_rows=chart_rows,
                payload=payload,
                lang=lang,
                user=user,
            )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service not configured",
        )

    # 2. Fetch Product from Supabase DB
    query = client.table("products").select("*, size_charts(*)")
    if payload.product_id:
        query = query.eq("id", payload.product_id)
    elif payload.product_url:
        norm_url = normalize_product_url(payload.product_url)
        query = query.or_(f"canonical_url.eq.{norm_url},product_url.eq.{payload.product_url}")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either product_id or product_url must be provided",
        )

    prod_res = query.limit(1).execute()
    if not prod_res.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product = prod_res.data[0]
    category = product["category"]
    size_chart = product.get("size_charts") or {}
    size_chart_id = product.get("size_chart_id")

    if not size_chart_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Product does not have an associated size chart",
        )

    # 3. Fetch Size Chart Rows
    rows_res = (
        client.table("size_chart_rows")
        .select("size_label, sort_order, measurement_key, value_cm")
        .eq("size_chart_id", size_chart_id)
        .order("sort_order")
        .execute()
    )

    if not rows_res.data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No measurements found for this product's size chart",
        )

    chart_rows = [
        SizeChartRowInput(
            size_label=r["size_label"],
            sort_order=r.get("sort_order", 0),
            measurement_key=r["measurement_key"],
            value_cm=float(r["value_cm"]),
        )
        for r in rows_res.data
    ]

    return await _execute_recommendation_computation(
        client=client,
        product=product,
        category=category,
        size_chart=size_chart,
        chart_rows=chart_rows,
        payload=payload,
        lang=lang,
        user=user,
    )
