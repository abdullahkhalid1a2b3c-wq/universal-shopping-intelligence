"""Customer fit feedback router for post-purchase fit reporting."""

from typing import Any, Dict, List, Literal, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.auth import get_current_user, get_optional_user
from app.fit.feedback_rules import evaluate_size_chart_review_need
from app.limiter import limiter
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


class FitFeedbackPayload(BaseModel):
    """Payload to submit fit feedback on a purchased item."""

    product_id: UUID
    size_bought: str = Field(..., min_length=1, max_length=16)
    fit_result: Literal["too_tight", "slightly_tight", "perfect", "slightly_loose", "too_loose"]
    problem_area: Optional[Literal["chest", "waist", "hip", "shoulder", "sleeve", "length", "none"]] = "none"
    was_returned: bool = False
    note: Optional[str] = Field(None, max_length=500)


class FeedbackSummaryResponse(BaseModel):
    """Privacy-preserving k-anonymized peer feedback summary."""

    has_summary: bool
    summary_text: Optional[str] = None
    sample_size: int = 0


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_fit_feedback(
    payload: FitFeedbackPayload,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Submit post-purchase fit feedback with one-per-user-per-product-per-size enforcement."""
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        )

    user_id = user["id"]
    product_id_str = str(payload.product_id)
    size_bought_clean = payload.size_bought.strip().upper()

    # 1. Enforce one-per-user-per-product-per-size rule
    existing = (
        client.table("fit_feedback")
        .select("id")
        .eq("user_id", user_id)
        .eq("product_id", product_id_str)
        .eq("size_bought", size_bought_clean)
        .execute()
    )
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have already submitted feedback for size {size_bought_clean} of this product.",
        )

    # 2. Privacy & Consent check: only store body_snapshot if store_measurements consent is granted
    body_snapshot: Optional[Dict[str, Any]] = None
    consent_res = (
        client.table("consents")
        .select("granted")
        .eq("user_id", user_id)
        .eq("consent_type", "store_measurements")
        .limit(1)
        .execute()
    )

    has_consent = bool(consent_res.data and consent_res.data[0].get("granted"))
    if has_consent:
        bm_res = (
            client.table("body_measurements")
            .select("chest_cm, waist_cm, hip_cm, shoulder_cm, sleeve_cm, inseam_cm")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if bm_res.data and len(bm_res.data) > 0:
            raw_bm = bm_res.data[0]
            measurement_keys = ("chest_cm", "waist_cm", "hip_cm", "shoulder_cm", "sleeve_cm", "inseam_cm")
            parsed_snap = {}
            for k in measurement_keys:
                val = raw_bm.get(k)
                if val is not None:
                    try:
                        parsed_snap[k] = float(val)
                    except (ValueError, TypeError):
                        pass
            if parsed_snap:
                body_snapshot = parsed_snap

    # 3. Insert feedback row
    insert_data = {
        "user_id": user_id,
        "product_id": product_id_str,
        "size_bought": size_bought_clean,
        "fit_result": payload.fit_result,
        "problem_area": payload.problem_area,
        "was_returned": payload.was_returned,
        "note": payload.note.strip() if payload.note else None,
        "body_snapshot": body_snapshot,
    }

    insert_res = client.table("fit_feedback").insert(insert_data).execute()
    new_feedback_id = insert_res.data[0]["id"] if insert_res.data else None

    # 4. Trigger feedback-driven quality check on product's size chart
    size_chart_flagged = False
    try:
        # Fetch all feedback for this product & size
        all_size_fb = (
            client.table("fit_feedback")
            .select("fit_result")
            .eq("product_id", product_id_str)
            .eq("size_bought", size_bought_clean)
            .execute()
        )
        if all_size_fb.data:
            eval_result = evaluate_size_chart_review_need(all_size_fb.data)
            if eval_result["needs_review"]:
                # Fetch product to locate size_chart_id
                prod_res = (
                    client.table("products")
                    .select("size_chart_id")
                    .eq("id", product_id_str)
                    .limit(1)
                    .execute()
                )
                if prod_res.data and prod_res.data[0].get("size_chart_id"):
                    sc_id = prod_res.data[0]["size_chart_id"]
                    client.table("size_charts").update({"needs_review": True}).eq("id", sc_id).execute()
                    size_chart_flagged = True
    except Exception:
        # Audit flagging failure must not break customer feedback submission
        pass

    return {
        "status": "submitted",
        "feedback_id": new_feedback_id,
        "size_chart_flagged": size_chart_flagged,
    }


@router.get("/summary", response_model=FeedbackSummaryResponse)
async def get_peer_feedback_summary(
    product_id: UUID,
    recommended_size: str = Query(..., description="Recommended size label"),
    chest_cm: Optional[float] = Query(None, description="Shopper chest measurement in cm"),
    lang: str = Query("en", description="Language for summary (en, ur, ur-roman)"),
) -> FeedbackSummaryResponse:
    """Privacy-preserving k-anonymized peer feedback summary.

    Rules:
    - Minimum 5 similar shoppers within 6 cm chest range.
    - Never exposes individual identities or measurement values.
    """
    client = get_supabase_client()
    if not client or chest_cm is None:
        return FeedbackSummaryResponse(has_summary=False)

    product_id_str = str(product_id)
    size_clean = recommended_size.strip().upper()

    try:
        # Fetch all feedback for this product & size with body_snapshot
        fb_res = (
            client.table("fit_feedback")
            .select("fit_result, body_snapshot")
            .eq("product_id", product_id_str)
            .eq("size_bought", size_clean)
            .execute()
        )
        if not fb_res.data:
            return FeedbackSummaryResponse(has_summary=False)

        similar_count = 0
        well_fit_count = 0

        for row in fb_res.data:
            snapshot = row.get("body_snapshot") or {}
            peer_chest = snapshot.get("chest_cm")
            if peer_chest is not None:
                try:
                    diff = abs(float(peer_chest) - float(chest_cm))
                    if diff <= 6.0:  # within 6 cm
                        similar_count += 1
                        if row.get("fit_result") in ("perfect", "slightly_tight", "slightly_loose"):
                            well_fit_count += 1
                except (ValueError, TypeError):
                    continue

        # k-anonymity check: require at least 5 similar respondents
        if similar_count >= 5:
            if lang == "ur":
                summary_text = f"ملتے جلتے سینے کے سائز والے {well_fit_count} خریداروں نے بتایا کہ {size_clean} سائز بہترین آیا۔"
            elif lang == "ur-roman":
                summary_text = f"Miltay jultay chest size walay {well_fit_count} buyers ne bataya k {size_clean} size fit aya."
            else:
                summary_text = f"{well_fit_count} people with a similar chest size said {size_clean} fit well."

            return FeedbackSummaryResponse(
                has_summary=True,
                summary_text=summary_text,
                sample_size=similar_count,
            )

        return FeedbackSummaryResponse(has_summary=False, sample_size=similar_count)
    except Exception:
        return FeedbackSummaryResponse(has_summary=False)
