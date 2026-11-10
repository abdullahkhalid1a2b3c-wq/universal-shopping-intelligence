"""Authentication dependencies for Supabase JWT verification and role enforcement."""

from typing import Any, Dict, Optional
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.supabase_client import get_supabase_client

# HTTPBearer with auto_error=False to cleanly support optional auth (guests)
security = HTTPBearer(auto_error=False)

_jwks_client: Optional[PyJWKClient] = None
if settings.supabase_jwks_url:
    _jwks_client = PyJWKClient(settings.supabase_jwks_url)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a Supabase JWT token."""
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "HS256":
            secret = settings.supabase_jwt_secret or "secret"
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        elif _jwks_client and alg in ("RS256", "ES256"):
            signing_key = _jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256", "RS256"],
                options={"verify_aud": False},
            )
        elif settings.supabase_jwt_secret:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            # In testing or unconfigured development environments without secret
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_aud": False},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
            )

        # Check metadata for role override
        raw_app_meta = payload.get("app_metadata", {})
        raw_user_meta = payload.get("user_metadata", {})
        app_role = raw_app_meta.get("role") or raw_user_meta.get("role") or payload.get("app_role")

        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": app_role or payload.get("role", "authenticated"),
            "app_role": app_role,
            "raw": payload,
        }
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {exc}",
        ) from exc


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Dependency that enforces a valid authenticated user."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )
    return decode_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Dependency for optional authentication (supports guest shoppers)."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return decode_token(credentials.credentials)
    except HTTPException:
        return None


def resolve_user_db_role(user: Dict[str, Any]) -> str:
    """Resolve user application role from profile in database or claims."""
    # First check decoded token claims
    claim_role = user.get("app_role") or user.get("role")
    if claim_role in ("admin", "retailer"):
        return claim_role

    client = get_supabase_client()
    if client:
        try:
            res = (
                client.table("profiles")
                .select("role")
                .eq("user_id", user["id"])
                .limit(1)
                .execute()
            )
            if res.data and res.data[0].get("role"):
                return res.data[0]["role"]
        except Exception:
            pass

    return "customer"


async def require_admin_user(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Enforce that the authenticated user possesses the 'admin' role."""
    role = resolve_user_db_role(user)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required. Access denied.",
        )
    user["resolved_role"] = "admin"
    return user


async def require_retailer_user(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Enforce that the authenticated user possesses 'retailer' or 'admin' role."""
    role = resolve_user_db_role(user)
    if role not in ("retailer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Retailer privileges required. Access denied.",
        )
    user["resolved_role"] = role
    return user


def verify_retailer_access(retailer_id: str, user: Dict[str, Any]) -> bool:
    """Verify that the user is an owner or editor of the given retailer, or an admin."""
    if user.get("resolved_role") == "admin":
        return True

    client = get_supabase_client()
    if not client:
        return True

    try:
        res = (
            client.table("retailer_members")
            .select("member_role")
            .eq("retailer_id", retailer_id)
            .eq("user_id", user["id"])
            .limit(1)
            .execute()
        )
        return bool(res.data)
    except Exception:
        return False
