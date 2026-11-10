-- Migration 00002: Row Level Security (RLS) & Access Policies
-- Enables RLS on all 15 tables and configures access controls per FitSense Data & Engineering rules.

-- 1. Helper function: check if current user is an active member of the retailer
CREATE OR REPLACE FUNCTION public.is_retailer_member(lookup_retailer_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.retailer_members
        WHERE retailer_id = lookup_retailer_id
          AND user_id = auth.uid()
    );
$$;

REVOKE ALL ON FUNCTION public.is_retailer_member(UUID) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.is_retailer_member(UUID) TO authenticated, service_role;

-- 2. Helper function: check if current user has admin role
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE user_id = auth.uid()
          AND role = 'admin'
    );
$$;

REVOKE ALL ON FUNCTION public.is_admin() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated, service_role;

-- 3. Trigger: When a signed-in user creates a retailer, automatically make them the 'owner'
CREATE OR REPLACE FUNCTION public.handle_new_retailer()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF auth.uid() IS NOT NULL THEN
        INSERT INTO public.retailer_members (retailer_id, user_id, member_role)
        VALUES (NEW.id, auth.uid(), 'owner')
        ON CONFLICT DO NOTHING;
    END IF;
    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_new_retailer() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_new_retailer() TO authenticated, service_role;

CREATE OR REPLACE TRIGGER trg_retailer_auto_owner
AFTER INSERT ON public.retailers
FOR EACH ROW EXECUTE FUNCTION public.handle_new_retailer();

-- 4. Helper function: verify if execution context is an authorized admin or trusted service role
-- Explicitly distinguishes anonymous, ordinary authenticated, verified admin, service_role, and database owner.
-- NOTE: Does NOT use current_user because inside a SECURITY DEFINER function current_user resolves to function owner.
CREATE OR REPLACE FUNCTION public.is_admin_or_service_role()
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_jwt_role TEXT;
    v_session_user TEXT;
BEGIN
    -- 1. Inspect verified PostgREST JWT claim role
    -- PostgREST cryptographically validates the token and sets this transaction-local GUC.
    -- Client headers cannot spoof this setting.
    BEGIN
        v_jwt_role := current_setting('request.jwt.claim.role', true);
    EXCEPTION
        WHEN OTHERS THEN
            v_jwt_role := NULL;
    END;

    -- If a PostgREST JWT context is active:
    IF v_jwt_role IS NOT NULL AND v_jwt_role <> '' THEN
        -- Service role is trusted internal API authority
        IF v_jwt_role = 'service_role' THEN
            RETURN TRUE;
        END IF;

        -- Authenticated user: verify administrative status via profiles table
        -- NEVER trust client-controlled user_metadata or claims.
        IF v_jwt_role = 'authenticated' AND auth.uid() IS NOT NULL THEN
            RETURN public.is_admin();
        END IF;

        -- Anonymous ('anon') or any other PostgREST role is strictly UNTRUSTED
        RETURN FALSE;
    END IF;

    -- 2. Direct database connection context (No PostgREST JWT active)
    -- When executing via psql or Supabase Dashboard SQL Editor, no JWT claim exists.
    -- We inspect session_user (the connection initiator, NOT current_user).
    v_session_user := session_user;
    IF v_session_user IN ('postgres', 'supabase_admin') THEN
        RETURN TRUE;
    END IF;

    -- Default safe deny for all unrecognized or unauthenticated contexts
    RETURN FALSE;
END;
$$;

REVOKE ALL ON FUNCTION public.is_admin_or_service_role() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.is_admin_or_service_role() TO authenticated, service_role;

-- 5. Trigger: Protect profiles.role against unauthorized privilege escalation (SEC-01)
CREATE OR REPLACE FUNCTION public.handle_profile_role_protection()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NEW.role IS DISTINCT FROM OLD.role THEN
        -- Strictly verify that caller is an authorized admin or service role
        IF NOT public.is_admin_or_service_role() THEN
            RAISE EXCEPTION 'Unauthorized: only platform administrators or service role can modify user roles';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_profile_role_protection() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_profile_role_protection() TO authenticated, service_role;

CREATE OR REPLACE TRIGGER trg_protect_profile_role
BEFORE UPDATE ON public.profiles
FOR EACH ROW EXECUTE FUNCTION public.handle_profile_role_protection();

-- 6. Trigger: Protect retailers.status and retailers.is_demo against unauthorized modification (SEC-03)
CREATE OR REPLACE FUNCTION public.handle_retailer_status_protection()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    -- Prevent non-admins/non-service from changing status or is_demo
    IF (NEW.status IS DISTINCT FROM OLD.status) OR (NEW.is_demo IS DISTINCT FROM OLD.is_demo) THEN
        IF NOT public.is_admin_or_service_role() THEN
            RAISE EXCEPTION 'Unauthorized: only platform administrators or service role can modify retailer status or demo status';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

REVOKE ALL ON FUNCTION public.handle_retailer_status_protection() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_retailer_status_protection() TO authenticated, service_role;

CREATE OR REPLACE TRIGGER trg_protect_retailer_status
BEFORE UPDATE ON public.retailers
FOR EACH ROW EXECUTE FUNCTION public.handle_retailer_status_protection();

-- ==========================================
-- Enable RLS on every table
-- ==========================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.body_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fit_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reference_garments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retailers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.retailer_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.size_charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.size_chart_rows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fit_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.store_adapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.coverage_requests ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- Customer Data Policies (user_id = auth.uid())
-- ==========================================

-- profiles
CREATE POLICY "Users can select own profile" ON public.profiles
    FOR SELECT TO authenticated USING (auth.uid() = user_id OR is_admin());
CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE TO authenticated USING (auth.uid() = user_id OR is_admin()) WITH CHECK (auth.uid() = user_id OR is_admin());
CREATE POLICY "Users can delete own profile" ON public.profiles
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- consents
CREATE POLICY "Users can select own consents" ON public.consents
    FOR SELECT TO authenticated USING (auth.uid() = user_id OR is_admin());
CREATE POLICY "Users can insert own consents" ON public.consents
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own consents" ON public.consents
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own consents" ON public.consents
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- body_measurements
CREATE POLICY "Users can select own measurements" ON public.body_measurements
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own measurements" ON public.body_measurements
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own measurements" ON public.body_measurements
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own measurements" ON public.body_measurements
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- fit_preferences
CREATE POLICY "Users can select own fit preferences" ON public.fit_preferences
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own fit preferences" ON public.fit_preferences
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own fit preferences" ON public.fit_preferences
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own fit preferences" ON public.fit_preferences
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- reference_garments
CREATE POLICY "Users can select own reference garments" ON public.reference_garments
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reference garments" ON public.reference_garments
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reference garments" ON public.reference_garments
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own reference garments" ON public.reference_garments
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- saved_items
CREATE POLICY "Users can select own saved items" ON public.saved_items
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own saved items" ON public.saved_items
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own saved items" ON public.saved_items
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own saved items" ON public.saved_items
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- recommendations
CREATE POLICY "Users can select own recommendations" ON public.recommendations
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own recommendations" ON public.recommendations
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own recommendations" ON public.recommendations
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- fit_feedback
CREATE POLICY "Users can select own fit feedback" ON public.fit_feedback
    FOR SELECT TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own fit feedback" ON public.fit_feedback
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own fit feedback" ON public.fit_feedback
    FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own fit feedback" ON public.fit_feedback
    FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- ==========================================
-- Retailer & Catalogue Policies
-- ==========================================

-- retailers:
-- Anyone can select verified retailers or demo retailers; members can select their own; admins can select all.
CREATE POLICY "Select retailers policy" ON public.retailers
    FOR SELECT USING (
        status = 'verified'
        OR is_demo = true
        OR is_retailer_member(id)
        OR is_admin()
    );

-- Any authenticated user can insert a retailer (starts with status pending)
CREATE POLICY "Authenticated users can create pending retailer" ON public.retailers
    FOR INSERT TO authenticated
    WITH CHECK (status = 'pending' OR is_admin());

-- Members can update their own retailer
CREATE POLICY "Members can update own retailer" ON public.retailers
    FOR UPDATE TO authenticated
    USING (is_retailer_member(id) OR is_admin())
    WITH CHECK (is_retailer_member(id) OR is_admin());

-- retailer_members:
CREATE POLICY "Select retailer members" ON public.retailer_members
    FOR SELECT TO authenticated
    USING (user_id = auth.uid() OR is_retailer_member(retailer_id) OR is_admin());

CREATE POLICY "Retailer owners can manage members" ON public.retailer_members
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.retailer_members rm
            WHERE rm.retailer_id = retailer_members.retailer_id
              AND rm.user_id = auth.uid()
              AND rm.member_role = 'owner'
        )
        OR is_admin()
    );

-- size_charts:
-- Public read where retailer is verified or is_demo = true
CREATE POLICY "Read size charts" ON public.size_charts
    FOR SELECT USING (
        is_demo = true
        OR EXISTS (
            SELECT 1 FROM public.retailers r
            WHERE r.id = size_charts.retailer_id AND r.status = 'verified'
        )
        OR is_retailer_member(retailer_id)
        OR is_admin()
    );

CREATE POLICY "Members can insert size charts" ON public.size_charts
    FOR INSERT TO authenticated
    WITH CHECK (is_retailer_member(retailer_id) OR is_admin());

CREATE POLICY "Members can update size charts" ON public.size_charts
    FOR UPDATE TO authenticated
    USING (is_retailer_member(retailer_id) OR is_admin())
    WITH CHECK (is_retailer_member(retailer_id) OR is_admin());

CREATE POLICY "Members can delete size charts" ON public.size_charts
    FOR DELETE TO authenticated
    USING (is_retailer_member(retailer_id) OR is_admin());

-- size_chart_rows:
CREATE POLICY "Read size chart rows" ON public.size_chart_rows
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.size_charts sc
            LEFT JOIN public.retailers r ON r.id = sc.retailer_id
            WHERE sc.id = size_chart_rows.size_chart_id
              AND (sc.is_demo = true OR r.status = 'verified' OR is_retailer_member(sc.retailer_id) OR is_admin())
        )
    );

CREATE POLICY "Members can insert size chart rows" ON public.size_chart_rows
    FOR INSERT TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.size_charts sc
            WHERE sc.id = size_chart_rows.size_chart_id
              AND (is_retailer_member(sc.retailer_id) OR is_admin())
        )
    );

CREATE POLICY "Members can update size chart rows" ON public.size_chart_rows
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.size_charts sc
            WHERE sc.id = size_chart_rows.size_chart_id
              AND (is_retailer_member(sc.retailer_id) OR is_admin())
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.size_charts sc
            WHERE sc.id = size_chart_rows.size_chart_id
              AND (is_retailer_member(sc.retailer_id) OR is_admin())
        )
    );

CREATE POLICY "Members can delete size chart rows" ON public.size_chart_rows
    FOR DELETE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.size_charts sc
            WHERE sc.id = size_chart_rows.size_chart_id
              AND (is_retailer_member(sc.retailer_id) OR is_admin())
        )
    );

-- products:
CREATE POLICY "Read products" ON public.products
    FOR SELECT USING (
        is_demo = true
        OR EXISTS (
            SELECT 1 FROM public.retailers r
            WHERE r.id = products.retailer_id AND r.status = 'verified'
        )
        OR is_retailer_member(retailer_id)
        OR is_admin()
    );

CREATE POLICY "Members can insert products" ON public.products
    FOR INSERT TO authenticated
    WITH CHECK (is_retailer_member(retailer_id) OR is_admin());

CREATE POLICY "Members can update products" ON public.products
    FOR UPDATE TO authenticated
    USING (is_retailer_member(retailer_id) OR is_admin())
    WITH CHECK (is_retailer_member(retailer_id) OR is_admin());

CREATE POLICY "Members can delete products" ON public.products
    FOR DELETE TO authenticated
    USING (is_retailer_member(retailer_id) OR is_admin());

-- store_adapters: public read where is_enabled; no public writes
CREATE POLICY "Read enabled store adapters" ON public.store_adapters
    FOR SELECT USING (is_enabled = true OR is_admin());

CREATE POLICY "Admin write store adapters" ON public.store_adapters
    FOR ALL TO authenticated
    USING (is_admin())
    WITH CHECK (is_admin());

-- coverage_requests: anyone signed in can insert; nobody can read except admins
CREATE POLICY "Signed-in users can insert coverage requests" ON public.coverage_requests
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

CREATE POLICY "Admins can view coverage requests" ON public.coverage_requests
    FOR SELECT TO authenticated
    USING (is_admin());

