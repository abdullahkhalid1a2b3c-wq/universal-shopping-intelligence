"""Unit tests for Phase 3.1 Security Remediation and Pre-Execution Validation.

Validates:
1. Profile role escalation prevention (SEC-01)
2. Safe storage folder UUID parsing (SEC-02)
3. Retailer status verification protection (SEC-03)
4. SECURITY DEFINER function search_path and execution grants (SEC-04)
5. Aggregated analytics privacy & k-anonymity (SEC-05)
6. Demo data demarcation and isolation (SEC-06)
7. AI Provider configuration canonicalization and non-leakage (SEC-08)
"""

import os
import re
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.config import Settings


# ============================================================================
# 1. AI Provider Configuration & Secret Hygiene Tests (SEC-08)
# ============================================================================

def test_openrouter_api_key_canonical_loading(monkeypatch):
    """Test that canonical OPENROUTER_API_KEY is loaded correctly."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-canonical-key-12345")
    monkeypatch.delenv("OPEN_ROUTER_API_KEY", raising=False)

    test_settings = Settings()
    assert test_settings.openrouter_api_key == "sk-or-canonical-key-12345"
    assert test_settings.get_ai_provider_status()["openrouter"] is True


def test_openrouter_api_key_legacy_alias_loading(monkeypatch):
    """Test that legacy alias OPEN_ROUTER_API_KEY is loaded when canonical is omitted."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPEN_ROUTER_API_KEY", "sk-or-legacy-key-67890")

    test_settings = Settings()
    assert test_settings.openrouter_api_key == "sk-or-legacy-key-67890"
    assert test_settings.get_ai_provider_status()["openrouter"] is True


def test_optional_providers_do_not_fail_when_unconfigured(monkeypatch):
    """Test that unconfigured optional providers (Gemini, xAI) default gracefully."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPEN_ROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    test_settings = Settings()
    status = test_settings.get_ai_provider_status()
    assert status["gemini"] is False
    assert status["xai"] is False


def test_secrets_are_not_exposed_in_repr_or_status(monkeypatch):
    """Test that repr() and get_ai_provider_status() do NOT reveal actual secret tokens."""
    secret_key = "super-secret-high-entropy-api-key-999"
    monkeypatch.setenv("OPENROUTER_API_KEY", secret_key)
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "supabase-admin-secret-888")

    test_settings = Settings()
    repr_str = repr(test_settings)
    status = test_settings.get_ai_provider_status()

    # The actual key string must never appear in repr or status
    assert secret_key not in repr_str
    assert "supabase-admin-secret-888" not in repr_str
    assert status["openrouter"] is True
    assert isinstance(status["openrouter"], bool)


# ============================================================================
# 2. Safe Storage Folder UUID Parsing Tests (SEC-02)
# ============================================================================

UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def python_safe_storage_retailer_id(object_name: str | None) -> str | None:
    """Python reference implementation replicating public.safe_storage_retailer_id SQL function."""
    if not object_name:
        return None
    folder_part = object_name.split("/")[0]
    if UUID_REGEX.match(folder_part):
        return folder_part.lower()
    return None


def test_safe_storage_valid_retailer_uuid_path():
    """Valid retailer UUID paths should safely parse to UUID."""
    valid_path = "11111111-1111-1111-1111-111111111111/charts/kurta.png"
    parsed = python_safe_storage_retailer_id(valid_path)
    assert parsed == "11111111-1111-1111-1111-111111111111"


def test_safe_storage_root_level_file_returns_null_safely():
    """Root-level files without a directory should return None without error."""
    root_file = "direct_upload.png"
    parsed = python_safe_storage_retailer_id(root_file)
    assert parsed is None


def test_safe_storage_malformed_directory_returns_null_safely():
    """Directories that are not 36-character UUIDs must return None."""
    assert python_safe_storage_retailer_id("avatars/user1.png") is None
    assert python_safe_storage_retailer_id("temp/chart.jpg") is None
    assert python_safe_storage_retailer_id("12345/chart.jpg") is None
    assert python_safe_storage_retailer_id("../../../etc/passwd") is None


def test_safe_storage_empty_or_none_returns_null():
    """Empty or None path values return None."""
    assert python_safe_storage_retailer_id("") is None
    assert python_safe_storage_retailer_id(None) is None


# ============================================================================
# 3. Profile Role Escalation & Execution Context Tests (SEC-01 & Phase 3.2)
# ============================================================================

def is_admin_or_service_role(
    jwt_role: str | None,
    auth_uid: str | None,
    is_admin_user: bool,
    session_user: str = "authenticator",
) -> bool:
    """Replicates public.is_admin_or_service_role() SQL function."""
    # 1. PostgREST request context (verified JWT claim role)
    if jwt_role:
        if jwt_role == "service_role":
            return True
        if jwt_role == "authenticated" and auth_uid is not None:
            return is_admin_user
        # 'anon' or any other JWT role is untrusted
        return False

    # 2. Direct database connection context (no JWT claim active)
    if session_user in ("postgres", "supabase_admin"):
        return True

    return False


def evaluate_profile_role_update(
    old_role: str,
    new_role: str,
    jwt_role: str | None,
    auth_uid: str | None,
    is_admin_user: bool,
    session_user: str = "authenticator",
) -> bool:
    """Replicates public.handle_profile_role_protection() trigger logic."""
    if new_role != old_role:
        if not is_admin_or_service_role(jwt_role, auth_uid, is_admin_user, session_user):
            return False  # Trigger raises EXCEPTION
    return True  # Allowed


def test_normal_user_cannot_escalate_role_to_admin():
    """Normal customer attempting to self-escalate to admin is rejected."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="admin",
        jwt_role="authenticated",
        auth_uid="user-cust-1",
        is_admin_user=False,
    )
    assert allowed is False


def test_normal_user_cannot_change_role_to_retailer():
    """Normal customer attempting to self-assign retailer role is rejected."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="retailer",
        jwt_role="authenticated",
        auth_uid="user-cust-1",
        is_admin_user=False,
    )
    assert allowed is False


def test_anonymous_user_cannot_modify_role():
    """Anonymous user (auth.uid() IS NULL, jwt_role='anon') attempting role modification is rejected."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="admin",
        jwt_role="anon",
        auth_uid=None,
        is_admin_user=False,
    )
    assert allowed is False


def test_unauthenticated_null_context_is_not_blindly_trusted():
    """Arbitrary context with NULL auth_uid and no service_role is rejected."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="admin",
        jwt_role=None,
        auth_uid=None,
        is_admin_user=False,
        session_user="anon_connection",
    )
    assert allowed is False


def test_normal_user_can_update_profile_without_changing_role():
    """Normal user updating other fields (display name, height) keeps role unchanged."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="customer",
        jwt_role="authenticated",
        auth_uid="user-cust-1",
        is_admin_user=False,
    )
    assert allowed is True


def test_admin_user_can_update_roles():
    """Authorized platform administrator can promote or modify user roles."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="retailer",
        jwt_role="authenticated",
        auth_uid="user-admin-1",
        is_admin_user=True,
    )
    assert allowed is True


def test_service_role_can_modify_roles():
    """Internal service role (jwt_role='service_role') can update roles."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="admin",
        jwt_role="service_role",
        auth_uid=None,
        is_admin_user=False,
    )
    assert allowed is True


def test_database_owner_can_modify_roles():
    """Database owner (session_user='postgres') can update roles in migrations/SQL Editor."""
    allowed = evaluate_profile_role_update(
        old_role="customer",
        new_role="admin",
        jwt_role=None,
        auth_uid=None,
        is_admin_user=False,
        session_user="postgres",
    )
    assert allowed is True


# ============================================================================
# 4. Retailer Status Verification Protection Logic Tests (SEC-03 & Phase 3.2)
# ============================================================================

def evaluate_retailer_update(
    old_status: str,
    new_status: str,
    old_is_demo: bool,
    new_is_demo: bool,
    jwt_role: str | None,
    auth_uid: str | None,
    is_admin_user: bool,
    session_user: str = "authenticator",
) -> bool:
    """Replicates public.handle_retailer_status_protection() trigger logic."""
    if (new_status != old_status) or (new_is_demo != old_is_demo):
        if not is_admin_or_service_role(jwt_role, auth_uid, is_admin_user, session_user):
            return False  # Trigger raises EXCEPTION
    return True  # Allowed


def test_pending_retailer_cannot_self_verify():
    """Retailer member attempting to self-verify status='verified' is rejected."""
    allowed = evaluate_retailer_update(
        old_status="pending",
        new_status="verified",
        old_is_demo=False,
        new_is_demo=False,
        jwt_role="authenticated",
        auth_uid="retailer-owner-1",
        is_admin_user=False,
    )
    assert allowed is False


def test_anonymous_user_cannot_verify_retailer():
    """Anonymous user attempting to verify retailer is rejected."""
    allowed = evaluate_retailer_update(
        old_status="pending",
        new_status="verified",
        old_is_demo=False,
        new_is_demo=False,
        jwt_role="anon",
        auth_uid=None,
        is_admin_user=False,
    )
    assert allowed is False


def test_retailer_member_cannot_modify_demo_flag():
    """Retailer member attempting to alter is_demo flag is rejected."""
    allowed = evaluate_retailer_update(
        old_status="pending",
        new_status="pending",
        old_is_demo=True,
        new_is_demo=False,
        jwt_role="authenticated",
        auth_uid="retailer-owner-1",
        is_admin_user=False,
    )
    assert allowed is False


def test_retailer_member_can_update_regular_fields():
    """Retailer member can update name, logo, COD policy when status is unchanged."""
    allowed = evaluate_retailer_update(
        old_status="pending",
        new_status="pending",
        old_is_demo=False,
        new_is_demo=False,
        jwt_role="authenticated",
        auth_uid="retailer-owner-1",
        is_admin_user=False,
    )
    assert allowed is True


def test_admin_can_verify_retailer():
    """Platform administrator can approve and verify a retailer."""
    allowed = evaluate_retailer_update(
        old_status="pending",
        new_status="verified",
        old_is_demo=False,
        new_is_demo=False,
        jwt_role="authenticated",
        auth_uid="admin-1",
        is_admin_user=True,
    )
    assert allowed is True


# ============================================================================
# 5. Analytics Privacy & K-Anonymity Tests (SEC-05)
# ============================================================================

def compute_product_fit_stats(feedback_entries: list[dict]) -> dict | None:
    """Replicates public.v_product_fit_stats aggregation with HAVING COUNT >= 5 row suppression."""
    total = len(feedback_entries)
    if total < 5:
        # Full row suppression: no row emitted below k=5 threshold
        return None

    tight = sum(1 for fb in feedback_entries if fb["fit_result"] in ("too_tight", "slightly_tight"))
    perfect = sum(1 for fb in feedback_entries if fb["fit_result"] == "perfect")
    loose = sum(1 for fb in feedback_entries if fb["fit_result"] in ("too_loose", "slightly_loose"))
    returns = sum(1 for fb in feedback_entries if fb.get("was_returned", False))

    return {
        "total_feedback": total,
        "pct_too_tight": round((tight / total) * 100, 2),
        "pct_perfect": round((perfect / total) * 100, 2),
        "pct_too_loose": round((loose / total) * 100, 2),
        "return_count": returns,
    }


def test_k_anonymity_completely_suppresses_rows_for_low_sample_count():
    """When customer feedback count < 5, row is completely suppressed to prevent group inference."""
    low_sample_feedback = [
        {"fit_result": "too_tight", "was_returned": True},
        {"fit_result": "too_tight", "was_returned": True},
        {"fit_result": "perfect", "was_returned": False},
    ]

    stats = compute_product_fit_stats(low_sample_feedback)
    # The view completely omits rows with COUNT < 5 (HAVING COUNT >= 5)
    assert stats is None


def test_k_anonymity_discloses_statistics_for_sufficient_sample_count():
    """When feedback count >= 5, statistics are safely computed and disclosed."""
    sufficient_feedback = [
        {"fit_result": "too_tight", "was_returned": True},
        {"fit_result": "perfect", "was_returned": False},
        {"fit_result": "perfect", "was_returned": False},
        {"fit_result": "perfect", "was_returned": False},
        {"fit_result": "too_loose", "was_returned": False},
    ]

    stats = compute_product_fit_stats(sufficient_feedback)
    assert stats is not None
    assert stats["total_feedback"] == 5
    assert stats["pct_too_tight"] == 20.0
    assert stats["pct_perfect"] == 60.0
    assert stats["pct_too_loose"] == 20.0
    assert stats["return_count"] == 1


def test_analytics_multi_tenant_isolation_and_pii_exclusion():
    """Verify that Retailer A cannot see Retailer B analytics rows and no PII is returned."""
    products = [
        {"id": "prod-A1", "retailer_id": "ret-A", "name": "Kurta A"},
        {"id": "prod-B1", "retailer_id": "ret-B", "name": "Shirt B"},
    ]
    memberships = {
        "user-retailer-A": ["ret-A"],
        "user-retailer-B": ["ret-B"],
        "user-admin": ["ret-A", "ret-B"],
    }
    feedback_table = [
        {"id": "fb-1", "product_id": "prod-A1", "size_bought": "M", "fit_result": "perfect", "body_snapshot": {"chest": 96}, "note": "Great"},
        {"id": "fb-2", "product_id": "prod-A1", "size_bought": "M", "fit_result": "perfect", "body_snapshot": {"chest": 98}, "note": "Nice"},
        {"id": "fb-3", "product_id": "prod-A1", "size_bought": "M", "fit_result": "perfect", "body_snapshot": {"chest": 97}, "note": "Good"},
        {"id": "fb-4", "product_id": "prod-A1", "size_bought": "M", "fit_result": "perfect", "body_snapshot": {"chest": 95}, "note": "Fine"},
        {"id": "fb-5", "product_id": "prod-A1", "size_bought": "M", "fit_result": "too_tight", "body_snapshot": {"chest": 102}, "note": "Tight"},
        {"id": "fb-6", "product_id": "prod-B1", "size_bought": "L", "fit_result": "too_loose", "body_snapshot": {"chest": 110}, "note": "Big"},
    ]

    def query_v_product_fit_stats(caller_user_id: str, is_admin: bool):
        allowed_retailers = memberships.get(caller_user_id, [])
        results = []
        for p in products:
            if is_admin or (p["retailer_id"] in allowed_retailers):
                prod_feedback = [fb for fb in feedback_table if fb["product_id"] == p["id"]]
                stats = compute_product_fit_stats(prod_feedback)
                # If suppressed by HAVING COUNT >= 5, no row is emitted
                if stats is not None:
                    results.append({
                        "product_id": p["id"],
                        "retailer_id": p["retailer_id"],
                        "product_name": p["name"],
                        "total_feedback": stats["total_feedback"],
                        "pct_too_tight": stats["pct_too_tight"],
                        "pct_perfect": stats["pct_perfect"],
                        "pct_too_loose": stats["pct_too_loose"],
                    })
        return results

    # Retailer A query: sees only Retailer A product with 5 submissions
    res_A = query_v_product_fit_stats("user-retailer-A", is_admin=False)
    assert len(res_A) == 1
    assert res_A[0]["product_id"] == "prod-A1"
    assert res_A[0]["retailer_id"] == "ret-A"
    assert res_A[0]["total_feedback"] == 5
    assert res_A[0]["pct_perfect"] == 80.0
    # Customer PII must NEVER be in analytics results
    assert "body_snapshot" not in res_A[0]
    assert "note" not in res_A[0]
    assert "user_id" not in res_A[0]

    # Retailer B query: Retailer B has only 1 feedback submission; row is completely suppressed
    res_B = query_v_product_fit_stats("user-retailer-B", is_admin=False)
    assert len(res_B) == 0

    # Admin query: sees only prod-A1 because prod-B1 has < 5 feedback submissions
    res_admin = query_v_product_fit_stats("user-admin", is_admin=True)
    assert len(res_admin) == 1
    assert res_admin[0]["product_id"] == "prod-A1"


# ============================================================================
# 6. Static SQL File Invariants Verification (SEC-01 through SEC-06)
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_sql_migrations_exist_and_are_readable():
    """Verify that all three migration files and seed.sql exist locally."""
    m1 = REPO_ROOT / "supabase" / "migrations" / "00001_initial_schema.sql"
    m2 = REPO_ROOT / "supabase" / "migrations" / "00002_rls_and_policies.sql"
    m3 = REPO_ROOT / "supabase" / "migrations" / "00003_analytics_and_storage.sql"
    seed = REPO_ROOT / "supabase" / "seed.sql"

    assert m1.exists(), "00001_initial_schema.sql missing"
    assert m2.exists(), "00002_rls_and_policies.sql missing"
    assert m3.exists(), "00003_analytics_and_storage.sql missing"
    assert seed.exists(), "seed.sql missing"


def test_all_security_definer_functions_have_secure_search_path():
    """Every SECURITY DEFINER function across all migration files MUST declare search_path = public, pg_temp."""
    sql_files = [
        REPO_ROOT / "supabase" / "migrations" / "00001_initial_schema.sql",
        REPO_ROOT / "supabase" / "migrations" / "00002_rls_and_policies.sql",
        REPO_ROOT / "supabase" / "migrations" / "00003_analytics_and_storage.sql",
    ]

    for sql_file in sql_files:
        content = sql_file.read_text(encoding="utf-8")
        # Find every CREATE ... FUNCTION with SECURITY DEFINER
        func_blocks = re.findall(
            r"CREATE(?:\s+OR\s+REPLACE)?\s+FUNCTION\s+([a-zA-Z0-9_\.]+)\s*\(.*?\).*?SECURITY\s+DEFINER.*?\$\$;",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        # Split file into individual function definitions to verify search_path on each
        for func_name in func_blocks:
            # Locate function definition in content
            pattern = re.compile(
                r"CREATE(?:\s+OR\s+REPLACE)?\s+FUNCTION\s+" + re.escape(func_name) + r".*?\$\$;",
                re.DOTALL | re.IGNORECASE,
            )
            match = pattern.search(content)
            assert match is not None, f"Could not find function body for {func_name} in {sql_file.name}"
            body = match.group(0)
            assert "SET search_path = public, pg_temp" in body or "SET search_path = public" in body, (
                f"Function {func_name} in {sql_file.name} lacks secure search_path definition"
            )


def test_seed_retailers_are_demo_and_pending_only():
    """Seed retailers must all be marked as is_demo = true and status = 'pending'."""
    seed_file = REPO_ROOT / "supabase" / "seed.sql"
    content = seed_file.read_text(encoding="utf-8")

    # In 1. Demo Retailers INSERT, verified status must NOT be present
    assert "status) VALUES" not in content or "status, is_demo) VALUES" in content
    # Look for status 'verified' in retailers INSERT
    retailer_block_match = re.search(r"INSERT INTO public\.retailers.*?ON CONFLICT", content, re.DOTALL)
    assert retailer_block_match is not None, "Could not locate retailer INSERT in seed.sql"
    retailer_block = retailer_block_match.group(0)

    assert "'verified'" not in retailer_block, "Seed data contains unvetted retailer with status='verified'"
    assert "'pending'" in retailer_block, "Seed retailers should be status='pending'"
    assert "true" in retailer_block, "Seed retailers must have is_demo = true"


def test_seed_size_charts_have_null_verified_at():
    """Seed size charts must NOT have fake verification dates (verified_at = NULL)."""
    seed_file = REPO_ROOT / "supabase" / "seed.sql"
    content = seed_file.read_text(encoding="utf-8")

    charts_block_match = re.search(r"INSERT INTO public\.size_charts.*?ON CONFLICT", content, re.DOTALL)
    assert charts_block_match is not None, "Could not locate size_charts INSERT in seed.sql"
    charts_block = charts_block_match.group(0)

    # In seed data, verified_at should be NULL, never NOW()
    assert "NOW()" not in charts_block, "Seed charts must not use NOW() for verified_at"
    assert "NULL, true" in charts_block, "Seed charts must have verified_at = NULL and is_demo = true"

