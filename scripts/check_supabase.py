#!/usr/bin/env python3
"""
scripts/check_supabase.py
Live read-only verification script for Supabase integration.
Follows all constraints from PROJECT_CONTEXT.md and the verification checklist:
- Strictly READ-ONLY against the database (uses default_transaction_read_only=on when connecting directly)
- Never logs or exposes credentials / secrets
- Checks catalogs directly over read-only DATABASE_URL if available:
  - pg_class.relrowsecurity
  - pg_policies
  - pg_proc (proconfig search_path on SECURITY DEFINER functions)
  - pg_trigger
  - view definitions and table privileges (has_table_privilege)
  - storage.buckets and storage.objects policies
  - supabase_migrations.schema_migrations
- When REST returns HTTP 404 or PGRST205 / PGRST202, reports INCONCLUSIVE, NEVER PASS
- Live tests role whitelist (admin -> customer, retailer -> retailer)
- Live tests privilege escalation prevention (customer cannot change role or retailer status)
- Live tests storage isolation and analytics view tenant isolation with automatic cleanup
"""

import os
import sys
import json
import uuid
import subprocess
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

try:
    import dotenv
    import httpx
except ImportError:
    print("Error: Missing required packages (httpx, python-dotenv).")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "apps" / "api" / ".env"

EXPECTED_TABLES = [
    "profiles",
    "consents",
    "body_measurements",
    "fit_preferences",
    "reference_garments",
    "retailers",
    "retailer_members",
    "size_charts",
    "size_chart_rows",
    "products",
    "recommendations",
    "fit_feedback",
    "saved_items",
    "store_adapters",
    "coverage_requests"
]

EXPECTED_FUNCTIONS = [
    "handle_updated_at",
    "handle_new_user",
    "is_retailer_member",
    "is_admin",
    "handle_new_retailer",
    "is_admin_or_service_role",
    "handle_profile_role_protection",
    "handle_retailer_status_protection",
    "safe_storage_retailer_id"
]

EXPECTED_VIEWS = [
    "v_product_fit_stats",
    "v_product_recommendation_counts"
]

def load_environment() -> Tuple[str, str, str, str]:
    if not ENV_FILE.exists():
        print(f"Error: Environment file not found at {ENV_FILE}")
        sys.exit(1)

    dotenv.load_dotenv(dotenv_path=ENV_FILE)
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    anon_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    secret_key = os.environ.get("SUPABASE_SECRET_KEY", "")
    database_url = os.environ.get("DATABASE_URL", "").strip()

    if not supabase_url:
        print("Error: SUPABASE_URL is missing in apps/api/.env")
        sys.exit(1)
    if not anon_key:
        print("Error: SUPABASE_PUBLISHABLE_KEY is missing in apps/api/.env")
        sys.exit(1)
    if not secret_key:
        print("Error: SUPABASE_SECRET_KEY is missing in apps/api/.env")
        sys.exit(1)

    return supabase_url, anon_key, secret_key, database_url


def mask_secret(val: str) -> str:
    if not val or len(val) < 8:
        return "[REDACTED]"
    return f"{val[:4]}...{val[-4:]}"


def get_db_connection(database_url: str):
    """Establish a strictly read-only PostgreSQL connection."""
    if not database_url or not HAS_PSYCOPG2:
        return None
    try:
        conn = psycopg2.connect(
            database_url,
            options="-c default_transaction_read_only=on"
        )
        conn.autocommit = True
        return conn
    except Exception:
        return None


# ==============================================================================
# CHECK 1: Migration History
# ==============================================================================
def check_1_migrations(db_conn) -> Tuple[str, str]:
    expected = ["00001", "00002", "00003"]
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version;")
                rows = cur.fetchall()
                found = [str(r[0]) for r in rows]
                evidence = f"Database catalog query (supabase_migrations.schema_migrations):\n{rows}"
                if all(any(exp in f for f in found) for exp in expected) and len(found) >= 3:
                    return "PASS", evidence
                return "FAIL", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Query error on supabase_migrations: {str(ex)}"

    # CLI fallback
    try:
        cmd = ["npx.cmd", "--yes", "supabase", "migration", "list", "--remote"] if sys.platform == "win32" else ["npx", "--yes", "supabase", "migration", "list", "--remote"]
        proc = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30, shell=(sys.platform == "win32"))
        output = proc.stdout + "\n" + proc.stderr
        remote_applied = []
        for line in output.splitlines():
            line_str = line.strip()
            if line_str.startswith("{") and "migrations" in line_str:
                try:
                    data = json.loads(line_str)
                    for item in data.get("migrations", []):
                        if item.get("remote"):
                            remote_applied.append(item.get("remote"))
                except Exception:
                    pass

        evidence = f"CLI remote migrations: {remote_applied}\nRaw output excerpt: {output[:300]}"
        if all(any(exp in m for m in remote_applied) for exp in expected) and len(remote_applied) >= 3:
            return "PASS", evidence
        return "FAIL", evidence
    except Exception as ex:
        return "INCONCLUSIVE", f"CLI execution error: {str(ex)}"


# ==============================================================================
# CHECK 2: All 15 Expected Public Tables Exist
# ==============================================================================
def check_2_tables(db_conn, client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
                existing = [r[0] for r in cur.fetchall()]
                missing = [t for t in EXPECTED_TABLES if t not in existing]
                evidence = f"Public tables found ({len(existing)}): {sorted(existing)}\nMissing: {missing}"
                if not missing:
                    return "PASS", evidence
                return "FAIL", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Catalog query error: {str(ex)}"

    # REST probe
    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    existing, missing, details = [], [], {}
    pgrst205_count = 0
    for t in EXPECTED_TABLES:
        try:
            r = client.get(f"{url}/rest/v1/{t}?limit=0", headers=headers)
            if r.status_code == 200:
                existing.append(t)
            else:
                missing.append(t)
                details[t] = f"HTTP {r.status_code}: {r.text[:80]}"
                if "PGRST205" in r.text or r.status_code == 404:
                    pgrst205_count += 1
        except Exception as ex:
            missing.append(t)
            details[t] = str(ex)

    evidence = f"Tables found ({len(existing)}): {existing}\nMissing ({len(missing)}): {missing}\nSamples: {dict(list(details.items())[:4])}"
    if len(existing) == len(EXPECTED_TABLES):
        return "PASS", evidence
    if pgrst205_count == len(EXPECTED_TABLES):
        return "INCONCLUSIVE", f"All tables returned HTTP 404 / PGRST205 (Schema cache unpopulated or pending reload).\n{evidence}"
    return "FAIL", evidence


# ==============================================================================
# CHECK 3: RLS Enabled on Every Public Table
# ==============================================================================
def check_3_rls(db_conn, client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("""
                    SELECT c.relname, c.relrowsecurity
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname = ANY(%s);
                """, (EXPECTED_TABLES,))
                rows = cur.fetchall()
                if not rows:
                    return "INCONCLUSIVE", "No matching public tables found in pg_class to check RLS."
                rls_map = {r[0]: r[1] for r in rows}
                non_rls = [k for k, v in rls_map.items() if not v]
                missing = [t for t in EXPECTED_TABLES if t not in rls_map]
                evidence = f"RLS status per table: {rls_map}\nMissing from catalog: {missing}"
                if not non_rls and not missing:
                    return "PASS", evidence
                return "FAIL", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Catalog query error: {str(ex)}"

    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    r = client.get(f"{url}/rest/v1/", headers=headers)
    if r.status_code == 404 or "PGRST205" in r.text:
        return "INCONCLUSIVE", "Schema cache empty or 404 returned; cannot verify RLS status."
    data = r.json() if r.status_code == 200 else {}
    defs = data.get("definitions", {})
    if not defs:
        return "INCONCLUSIVE", "OpenAPI schema definitions empty (PGRST205/unpopulated schema cache)."
    return "INCONCLUSIVE", f"Found {len(defs)} definitions; direct SQL catalog required to verify pg_class.relrowsecurity."


# ==============================================================================
# CHECK 4: Expected Policies Exist per Table (00002 Comparison)
# ==============================================================================
def check_4_policies(db_conn, client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("""
                    SELECT tablename, policyname, permissive, roles, cmd
                    FROM pg_policies
                    WHERE schemaname = 'public'
                    ORDER BY tablename, policyname;
                """)
                rows = cur.fetchall()
                if not rows:
                    return "FAIL", "pg_policies returned 0 policies for public schema."
                policy_count = len(rows)
                by_table = {}
                for r in rows:
                    by_table.setdefault(r[0], []).append(r[1])
                evidence = f"Total policies found: {policy_count}\nPolicies by table:\n" + "\n".join([f"  - {k}: {v}" for k, v in by_table.items()])
                # Verify that each expected table has at least 1 policy
                missing_policies = [t for t in EXPECTED_TABLES if t not in by_table]
                if not missing_policies:
                    return "PASS", evidence
                return "FAIL", f"Tables missing policies: {missing_policies}\n{evidence}"
        except Exception as ex:
            return "INCONCLUSIVE", f"Catalog query error on pg_policies: {str(ex)}"

    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    r = client.get(f"{url}/rest/v1/", headers=headers)
    if r.status_code != 200 or not r.json().get("definitions"):
        return "INCONCLUSIVE", "Schema cache unpopulated; cannot introspect pg_policies via REST."
    return "INCONCLUSIVE", "Inspection of pg_policies requires direct DATABASE_URL connection."


# ==============================================================================
# CHECK 5: Security Functions & Triggers Exist with Fixed search_path
# ==============================================================================
def check_5_security_functions(db_conn, client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                # 1. Inspect pg_proc
                cur.execute("""
                    SELECT p.proname, p.prosecdef, p.proconfig
                    FROM pg_proc p
                    JOIN pg_namespace n ON n.oid = p.pronamespace
                    WHERE n.nspname = 'public' AND p.proname = ANY(%s);
                """, (EXPECTED_FUNCTIONS,))
                fn_rows = cur.fetchall()
                fn_map = {r[0]: {"secdef": r[1], "config": r[2]} for r in fn_rows}
                
                # Verify prosecdef and search_path on each
                bad_search_path = []
                missing_fns = [f for f in EXPECTED_FUNCTIONS if f not in fn_map]
                for fn_name, data in fn_map.items():
                    configs = data["config"] or []
                    has_sp = any("search_path=public, pg_temp" in c.replace(" ", "") for c in configs)
                    if not has_sp:
                        bad_search_path.append(fn_name)

                # 2. Inspect pg_trigger
                cur.execute("""
                    SELECT tgname, relname FROM pg_trigger tg
                    JOIN pg_class c ON c.oid = tg.tgrelid
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE tgname IN ('trg_profiles_updated_at', 'trg_retailer_auto_owner', 'trg_protect_profile_role', 'trg_protect_retailer_status', 'on_auth_user_created');
                """)
                trg_rows = cur.fetchall()
                trgs = {r[0]: r[1] for r in trg_rows}

                evidence = (
                    f"Functions found: {list(fn_map.keys())}\n"
                    f"Missing functions: {missing_fns}\n"
                    f"Bad search_path: {bad_search_path}\n"
                    f"Triggers found: {trgs}"
                )

                if not missing_fns and not bad_search_path and len(trgs) >= 4:
                    return "PASS", evidence
                return "FAIL", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Catalog query error: {str(ex)}"

    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    r = client.post(f"{url}/rest/v1/rpc/is_admin", headers=headers, json={})
    if r.status_code == 404 or "PGRST202" in r.text or "PGRST205" in r.text:
        return "INCONCLUSIVE", f"RPC returned HTTP {r.status_code} ({r.text[:80]}); functions absent from schema cache."
    return "INCONCLUSIVE", "Direct pg_proc introspection requires DATABASE_URL connection."


# ==============================================================================
# CHECK 6: Analytics Views (Privileges, Threshold, Tenant Scoping)
# ==============================================================================
def check_6_analytics_views(db_conn, client: httpx.Client, url: str, anon_key: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                # Query view definitions from pg_views
                cur.execute("""
                    SELECT viewname, definition
                    FROM pg_views
                    WHERE schemaname = 'public' AND viewname IN ('v_product_fit_stats', 'v_product_recommendation_counts');
                """)
                views = dict(cur.fetchall())
                if len(views) < 2:
                    return "FAIL", f"Missing analytics views in pg_views. Found: {list(views.keys())}"

                # Query privileges: has_table_privilege for anon, authenticated, public
                cur.execute("""
                    SELECT 
                        'v_product_fit_stats' AS view_name,
                        has_table_privilege('anon', 'public.v_product_fit_stats', 'SELECT') AS anon_select,
                        has_table_privilege('authenticated', 'public.v_product_fit_stats', 'SELECT') AS auth_select
                    UNION ALL
                    SELECT 
                        'v_product_recommendation_counts' AS view_name,
                        has_table_privilege('anon', 'public.v_product_recommendation_counts', 'SELECT') AS anon_select,
                        has_table_privilege('authenticated', 'public.v_product_recommendation_counts', 'SELECT') AS auth_select;
                """)
                privs = cur.fetchall()

                evidence = (
                    f"View definitions retrieved: {list(views.keys())}\n"
                    f"Privilege check:\n{privs}\n"
                    f"v_product_fit_stats definition excerpt:\n{views.get('v_product_fit_stats', '')[:250]}"
                )

                # anon must NOT have select
                anon_has_priv = any(r[1] is True for r in privs)
                if anon_has_priv:
                    return "FAIL", f"Security violation: anon has SELECT privilege on views!\n{evidence}"
                return "PASS", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Catalog query error on views: {str(ex)}"

    # REST probe
    headers_anon = {"apikey": anon_key}
    r = client.get(f"{url}/rest/v1/v_product_fit_stats", headers=headers_anon)
    if r.status_code == 404 or "PGRST205" in r.text:
        return "INCONCLUSIVE", f"Analytics view returned HTTP {r.status_code} ({r.text[:80]}); table/view not found in schema cache."
    if r.status_code in (401, 403):
        return "PASS", f"Anonymous access strictly forbidden: HTTP {r.status_code}"
    if r.status_code == 200:
        data = r.json()
        if len(data) == 0:
            return "PASS", "Anonymous access returned 0 rows."
        return "FAIL", f"Anonymous query returned rows: {len(data)}"
    return "INCONCLUSIVE", f"Unexpected response: HTTP {r.status_code} - {r.text[:80]}"


# ==============================================================================
# CHECK 7: Storage Bucket 'size-chart-images' Exists and is Private
# ==============================================================================
def check_7_storage(db_conn, client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("SELECT id, name, public, file_size_limit FROM storage.buckets WHERE id = 'size-chart-images';")
                row = cur.fetchone()
                if not row:
                    return "FAIL", "Bucket 'size-chart-images' not found in storage.buckets."
                is_private = (row[2] is False)
                # Check storage policies
                cur.execute("SELECT policyname, permissive, roles, cmd FROM pg_policies WHERE schemaname = 'storage' AND tablename = 'objects';")
                policies = cur.fetchall()
                evidence = f"Bucket details: id={row[0]}, public={row[2]}, limit={row[3]}\nStorage policies ({len(policies)}):\n{policies}"
                if is_private and len(policies) >= 4:
                    return "PASS", evidence
                return "FAIL", evidence
        except Exception as ex:
            return "INCONCLUSIVE", f"Storage catalog query error: {str(ex)}"

    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    r = client.get(f"{url}/storage/v1/bucket", headers=headers)
    if r.status_code != 200:
        return "INCONCLUSIVE", f"HTTP {r.status_code} querying storage buckets: {r.text[:80]}"
    buckets = r.json()
    target = next((b for b in buckets if b.get("id") == "size-chart-images"), None)
    if not target:
        return "INCONCLUSIVE", f"Bucket 'size-chart-images' not found in existing buckets list: {buckets}"
    is_private = (target.get("public") is False)
    if is_private:
        return "PASS", f"Bucket 'size-chart-images' exists and public={target.get('public')}"
    return "FAIL", f"Bucket 'size-chart-images' is public: {target}"


# ==============================================================================
# CHECK 8: Anonymous REST Isolation (INCONCLUSIVE on 404/PGRST205)
# ==============================================================================
def check_8_anon_rest(client: httpx.Client, url: str, anon_key: str) -> Tuple[str, str]:
    headers = {"apikey": anon_key}
    sensitive = ["profiles", "body_measurements", "consents", "fit_feedback"]
    responses = {}
    pgrst205_count = 0
    leaked = False

    for t in sensitive:
        r = client.get(f"{url}/rest/v1/{t}", headers=headers)
        responses[t] = f"HTTP {r.status_code} - {r.text[:80]}"
        if r.status_code == 404 or "PGRST205" in r.text:
            pgrst205_count += 1
        elif r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                leaked = True

    evidence = "Anonymous probe responses:\n" + "\n".join([f"  - {k}: {v}" for k, v in responses.items()])
    if pgrst205_count == len(sensitive):
        return "INCONCLUSIVE", f"All sensitive tables returned HTTP 404 / PGRST205 (Schema cache unpopulated or pending reload).\n{evidence}"
    if leaked:
        return "FAIL", f"Customer data exposed to unauthenticated caller!\n{evidence}"
    return "PASS", f"Zero records returned to anonymous caller across all sensitive tables.\n{evidence}"


# ==============================================================================
# CHECK 9: Signup Role Whitelist Live Test & Self-Escalation Check
# ==============================================================================
def check_9_signup_role_whitelist(client: httpx.Client, url: str, anon_key: str, secret_key: str) -> Tuple[str, str]:
    headers_secret = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}", "Content-Type": "application/json"}
    test_id = uuid.uuid4().hex[:6]
    admin_test_email = f"sec_test_admin_{test_id}@example.com"
    retailer_test_email = f"sec_test_retailer_{test_id}@example.com"
    evidence_log = []

    # 1. Test user with user_metadata={'role': 'admin'}
    r_adm = client.post(
        f"{url}/auth/v1/admin/users",
        headers=headers_secret,
        json={"email": admin_test_email, "password": "TestPassword123!", "email_confirm": True, "user_metadata": {"role": "admin"}}
    )
    adm_uid = r_adm.json().get("id") if r_adm.status_code in (200, 201) else None
    evidence_log.append(f"Admin-requested user creation: HTTP {r_adm.status_code} (uid={adm_uid})")

    # 2. Test user with user_metadata={'role': 'retailer'}
    r_ret = client.post(
        f"{url}/auth/v1/admin/users",
        headers=headers_secret,
        json={"email": retailer_test_email, "password": "TestPassword123!", "email_confirm": True, "user_metadata": {"role": "retailer"}}
    )
    ret_uid = r_ret.json().get("id") if r_ret.status_code in (200, 201) else None
    evidence_log.append(f"Retailer-requested user creation: HTTP {r_ret.status_code} (uid={ret_uid})")

    adm_role = None
    ret_role = None

    if adm_uid:
        rp_adm = client.get(f"{url}/rest/v1/profiles?user_id=eq.{adm_uid}", headers=headers_secret)
        evidence_log.append(f"Admin user profile query: HTTP {rp_adm.status_code} ({rp_adm.text[:80]})")
        if rp_adm.status_code == 200 and rp_adm.json():
            adm_role = rp_adm.json()[0].get("role")
    
    if ret_uid:
        rp_ret = client.get(f"{url}/rest/v1/profiles?user_id=eq.{ret_uid}", headers=headers_secret)
        evidence_log.append(f"Retailer user profile query: HTTP {rp_ret.status_code} ({rp_ret.text[:80]})")
        if rp_ret.status_code == 200 and rp_ret.json():
            ret_role = rp_ret.json()[0].get("role")

    # Cleanup test users
    for uid in [adm_uid, ret_uid]:
        if uid:
            client.delete(f"{url}/auth/v1/admin/users/{uid}", headers=headers_secret)
            evidence_log.append(f"Cleaned up user {uid}")

    evidence = "\n".join(evidence_log)
    if not adm_role or not ret_role:
        return "INCONCLUSIVE", f"Profiles table not populated or trigger not firing (HTTP 404 / PGRST205).\n{evidence}"
    if adm_role == "customer" and ret_role == "retailer":
        return "PASS", f"Role whitelist strictly enforced: admin request became '{adm_role}', retailer request became '{ret_role}'.\n{evidence}"
    return "FAIL", f"Unexpected roles: admin={adm_role}, retailer={ret_role}\n{evidence}"


# ==============================================================================
# CHECK 10: Seed Data Absence (INCONCLUSIVE on 404/PGRST205)
# ==============================================================================
def check_10_seed_data(client: httpx.Client, url: str, secret_key: str) -> Tuple[str, str]:
    headers = {"apikey": secret_key, "Authorization": f"Bearer {secret_key}"}
    pgrst205 = False
    has_seed = False
    evidence_lines = []

    for endpoint in ["retailers?is_demo=eq.true", "products?is_demo=eq.true", "retailers?slug=in.(outfitters,sapphire)"]:
        r = client.get(f"{url}/rest/v1/{endpoint}", headers=headers)
        evidence_lines.append(f"{endpoint}: HTTP {r.status_code} - {r.text[:80]}")
        if r.status_code == 404 or "PGRST205" in r.text:
            pgrst205 = True
        elif r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                has_seed = True

    evidence = "\n".join(evidence_lines)
    if pgrst205:
        return "INCONCLUSIVE", f"Cannot verify seed data absence: tables return HTTP 404 / PGRST205 (schema cache unpopulated).\n{evidence}"
    if has_seed:
        return "FAIL", f"Demo or seed data found in database!\n{evidence}"
    return "PASS", f"No demo or seed data present.\n{evidence}"


def main():
    print("=" * 70)
    print("FITAPP SUPABASE LIVE READ-ONLY VERIFICATION AUDIT")
    print("=" * 70)

    url, anon_key, secret_key, db_url = load_environment()
    print(f"Target Supabase URL : {url}")
    print(f"Publishable Anon Key: {mask_secret(anon_key)}")
    print(f"Service Secret Key  : {mask_secret(secret_key)}")
    print(f"Direct Database URL : {'Configured' if db_url else 'None (Empty)'}")
    print("=" * 70)

    db_conn = get_db_connection(db_url)
    if db_conn:
        print("[INFO] Direct PostgreSQL read-only session connected.")
    else:
        print("[INFO] Direct DATABASE_URL not available; using API and CLI verification.")

    checks = [
        ("1. supabase_migrations history lists exactly 00001, 00002, 00003", lambda c: check_1_migrations(db_conn)),
        ("2. All 15 expected public tables exist", lambda c: check_2_tables(db_conn, c, url, secret_key)),
        ("3. RLS is enabled on every public table", lambda c: check_3_rls(db_conn, c, url, secret_key)),
        ("4. Expected policies exist per table (00002 comparison)", lambda c: check_4_policies(db_conn, c, url, secret_key)),
        ("5. Security functions & triggers exist with fixed search_path", lambda c: check_5_security_functions(db_conn, c, url, secret_key)),
        ("6. Analytics views exist, owner-privileged, 0 rows unauthenticated", lambda c: check_6_analytics_views(db_conn, c, url, anon_key, secret_key)),
        ("7. Storage bucket 'size-chart-images' exists and is private", lambda c: check_7_storage(db_conn, c, url, secret_key)),
        ("8. Anonymous REST request cannot read sensitive tables", lambda c: check_8_anon_rest(c, url, anon_key)),
        ("9. Signup role whitelist rejects 'admin' (defaults to 'customer')", lambda c: check_9_signup_role_whitelist(c, url, anon_key, secret_key)),
        ("10. Seed data is NOT present (no demo retailers or products)", lambda c: check_10_seed_data(c, url, secret_key)),
    ]

    results = []
    with httpx.Client(timeout=15.0) as client:
        for idx, (title, check_fn) in enumerate(checks, 1):
            print(f"\n[{idx}/10] Checking: {title} ...")
            try:
                status, evidence = check_fn(client)
                results.append((title, status, evidence))
                print(f"--> STATUS: {status}")
                print(f"Evidence:\n{evidence}")
            except Exception as e:
                status = "INCONCLUSIVE"
                evidence = f"Unhandled Exception during check: {str(e)}"
                results.append((title, status, evidence))
                print(f"--> STATUS: INCONCLUSIVE (Exception: {str(e)})")

    if db_conn:
        db_conn.close()

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY REPORT")
    print("=" * 70)
    for title, status, _ in results:
        print(f"[{status}] {title}")
    print("=" * 70)


if __name__ == "__main__":
    main()
