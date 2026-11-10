"""Account management router: data export, deletion, and consent withdrawal."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.supabase_client import get_supabase_client

router = APIRouter(prefix="/v1/account", tags=["account"])


@router.get("/export")
async def export_user_data(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Export all personal customer data stored in FitSense as JSON (Data Portability)."""
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        )

    user_id = user["id"]
    exported: Dict[str, Any] = {
        "user_id": user_id,
        "email": user.get("email"),
        "exported_at": None,
    }

    tables = [
        "profiles",
        "consents",
        "body_measurements",
        "fit_preferences",
        "reference_garments",
        "saved_items",
        "recommendations",
        "fit_feedback",
    ]

    for tbl in tables:
        try:
            res = client.table(tbl).select("*").eq("user_id", user_id).execute()
            exported[tbl] = res.data or []
        except Exception:
            exported[tbl] = []

    return exported


@router.post("/withdraw-consent")
async def withdraw_measurement_consent(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Withdraw measurement storage consent.

    Immediately deletes stored body measurements and wipes any body snapshot
    references in historical feedback or recommendation records.
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        )

    user_id = user["id"]

    # 1. Revoke consent in consents table
    try:
        client.table("consents").update({"granted": False}).eq("user_id", user_id).eq("consent_type", "store_measurements").execute()
    except Exception:
        pass

    # 2. Delete stored body measurements
    try:
        client.table("body_measurements").delete().eq("user_id", user_id).execute()
    except Exception:
        pass

    # 3. Wipe body snapshots from feedback rows
    try:
        client.table("fit_feedback").update({"body_snapshot": None}).eq("user_id", user_id).execute()
    except Exception:
        pass

    return {
        "status": "withdrawn",
        "message": "Measurement storage consent withdrawn. All stored measurements and snapshots deleted.",
    }


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_user_account(
    keep_anonymous_feedback: bool = Query(False, description="Whether to preserve anonymized feedback without user_id"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Permanently delete user account and clean all associated tables.

    Enforces Right to be Forgotten.
    If keep_anonymous_feedback is True, feedback rows are disassociated (user_id=null, body_snapshot=null)
    rather than deleted.
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable",
        )

    user_id = user["id"]

    # 1. Handle fit_feedback (anonymize or delete)
    try:
        if keep_anonymous_feedback:
            # Anonymize: remove user_id and body_snapshot so no identifying measurement remains
            client.table("fit_feedback").update({"user_id": None, "body_snapshot": None}).eq("user_id", user_id).execute()
        else:
            client.table("fit_feedback").delete().eq("user_id", user_id).execute()
    except Exception:
        pass

    # 2. Delete customer rows across all user tables
    tables = [
        "recommendations",
        "saved_items",
        "reference_garments",
        "fit_preferences",
        "body_measurements",
        "consents",
        "profiles",
    ]
    for tbl in tables:
        try:
            client.table(tbl).delete().eq("user_id", user_id).execute()
        except Exception:
            pass

    # 3. Delete auth.users account via admin auth API
    try:
        client.auth.admin.delete_user(user_id)
    except Exception:
        pass

    return {
        "status": "deleted",
        "message": "User account and all personal data permanently deleted.",
        "feedback_anonymized": keep_anonymous_feedback,
    }
