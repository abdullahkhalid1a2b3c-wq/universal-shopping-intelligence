-- Migration 00001: Initial Schema for FitSense
-- Creates all core tables, constraints, enums/checks, and user profile trigger.

-- 1. Helper trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 2. profiles table
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    preferred_language TEXT NOT NULL DEFAULT 'en' CHECK (preferred_language IN ('en', 'ur', 'ur-roman')),
    preferred_unit TEXT NOT NULL DEFAULT 'cm' CHECK (preferred_unit IN ('cm', 'in')),
    gender_category TEXT CHECK (gender_category IN ('womens', 'mens', 'unisex')),
    height_cm NUMERIC(5,2) CHECK (height_cm IS NULL OR (height_cm >= 50 AND height_cm <= 260)),
    weight_kg NUMERIC(5,2) CHECK (weight_kg IS NULL OR (weight_kg >= 20 AND weight_kg <= 300)),
    role TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'retailer', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_profiles_user_id UNIQUE (user_id)
);

CREATE TRIGGER trg_profiles_updated_at
BEFORE UPDATE ON public.profiles
FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- Auto-create profile row when a new user signs up in auth.users
-- Admin role can NEVER be granted via raw_user_meta_data during self-signup.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    INSERT INTO public.profiles (user_id, display_name, preferred_language, preferred_unit, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_user_meta_data->>'preferred_language', 'en'),
        COALESCE(NEW.raw_user_meta_data->>'preferred_unit', 'cm'),
        CASE 
            WHEN NEW.raw_user_meta_data->>'role' = 'retailer' THEN 'retailer'
            ELSE 'customer'
        END
    )
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

-- Restrict direct execution of internal trigger function
REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role, postgres;

CREATE OR REPLACE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 3. consents table
CREATE TABLE public.consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    consent_type TEXT NOT NULL CHECK (consent_type IN ('store_measurements', 'use_feedback_for_analytics')),
    granted BOOLEAN NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    policy_version TEXT NOT NULL DEFAULT 'v1.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. body_measurements table
CREATE TABLE public.body_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    chest_cm NUMERIC(5,2) CHECK (chest_cm IS NULL OR (chest_cm >= 50 AND chest_cm <= 200)),
    waist_cm NUMERIC(5,2) CHECK (waist_cm IS NULL OR (waist_cm >= 40 AND waist_cm <= 180)),
    hip_cm NUMERIC(5,2) CHECK (hip_cm IS NULL OR (hip_cm >= 50 AND hip_cm <= 200)),
    shoulder_cm NUMERIC(5,2) CHECK (shoulder_cm IS NULL OR (shoulder_cm >= 25 AND shoulder_cm <= 70)),
    sleeve_cm NUMERIC(5,2) CHECK (sleeve_cm IS NULL OR (sleeve_cm >= 20 AND sleeve_cm <= 100)),
    inseam_cm NUMERIC(5,2) CHECK (inseam_cm IS NULL OR (inseam_cm >= 30 AND inseam_cm <= 120)),
    thigh_cm NUMERIC(5,2) CHECK (thigh_cm IS NULL OR (thigh_cm >= 25 AND thigh_cm <= 100)),
    torso_length_cm NUMERIC(5,2) CHECK (torso_length_cm IS NULL OR (torso_length_cm >= 30 AND torso_length_cm <= 100)),
    kameez_length_cm NUMERIC(5,2) CHECK (kameez_length_cm IS NULL OR (kameez_length_cm >= 50 AND kameez_length_cm <= 160)),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_body_measurements_user_id UNIQUE (user_id)
);

CREATE TRIGGER trg_body_measurements_updated_at
BEFORE UPDATE ON public.body_measurements
FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- 5. fit_preferences table
CREATE TABLE public.fit_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN ('tshirt_top', 'shirt', 'trouser', 'jeans', 'kurta', 'dress')),
    fit TEXT NOT NULL CHECK (fit IN ('fitted', 'regular', 'loose')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fit_preferences_user_category UNIQUE (user_id, category)
);

-- 6. reference_garments table
CREATE TABLE public.reference_garments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN ('tshirt_top', 'shirt', 'trouser', 'jeans', 'kurta', 'dress')),
    label TEXT NOT NULL,
    measurements JSONB NOT NULL DEFAULT '{}'::jsonb,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. retailers table
CREATE TABLE public.retailers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    website_domain TEXT,
    logo_url TEXT,
    supports_cod BOOLEAN NOT NULL DEFAULT false,
    return_policy_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'suspended')),
    is_demo BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. retailer_members table
CREATE TABLE public.retailer_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES public.retailers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    member_role TEXT NOT NULL DEFAULT 'owner' CHECK (member_role IN ('owner', 'editor')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_retailer_members_retailer_user UNIQUE (retailer_id, user_id)
);

-- 9. size_charts table
CREATE TABLE public.size_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES public.retailers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('tshirt_top', 'shirt', 'trouser', 'jeans', 'kurta', 'dress')),
    gender_category TEXT CHECK (gender_category IN ('womens', 'mens', 'unisex')),
    measured_as TEXT NOT NULL DEFAULT 'circumference' CHECK (measured_as IN ('flat', 'circumference')),
    unit_source TEXT NOT NULL DEFAULT 'cm' CHECK (unit_source IN ('cm', 'in')),
    source_note TEXT,
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    is_demo BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. size_chart_rows table
CREATE TABLE public.size_chart_rows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    size_chart_id UUID NOT NULL REFERENCES public.size_charts(id) ON DELETE CASCADE,
    size_label TEXT NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    measurement_key TEXT NOT NULL CHECK (measurement_key IN ('chest', 'waist', 'hip', 'shoulder', 'sleeve', 'length', 'inseam', 'thigh', 'rise', 'hem')),
    value_cm NUMERIC(5,2) NOT NULL CHECK (value_cm > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_size_chart_rows_chart_size_key UNIQUE (size_chart_id, size_label, measurement_key)
);

-- 11. products table
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retailer_id UUID NOT NULL REFERENCES public.retailers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('tshirt_top', 'shirt', 'trouser', 'jeans', 'kurta', 'dress')),
    gender_category TEXT CHECK (gender_category IN ('womens', 'mens', 'unisex')),
    product_url TEXT NOT NULL,
    canonical_url TEXT NOT NULL UNIQUE,
    external_id TEXT,
    size_chart_id UUID REFERENCES public.size_charts(id) ON DELETE SET NULL,
    fabric TEXT,
    stretch_pct NUMERIC(4,2) NOT NULL DEFAULT 0 CHECK (stretch_pct >= 0 AND stretch_pct <= 40),
    thickness TEXT CHECK (thickness IN ('light', 'medium', 'heavy')),
    transparency TEXT CHECK (transparency IN ('opaque', 'slightly_sheer', 'sheer')),
    shrinkage_pct NUMERIC(4,2) DEFAULT 0,
    season TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_demo BOOLEAN NOT NULL DEFAULT false,
    fit_cut TEXT CHECK (fit_cut IN ('slim', 'regular', 'relaxed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. recommendations table
CREATE TABLE public.recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    recommended_size TEXT NOT NULL,
    confidence_score INT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    confidence_label TEXT NOT NULL,
    inputs_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 13. fit_feedback table
CREATE TABLE public.fit_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    size_bought TEXT NOT NULL,
    fit_result TEXT NOT NULL CHECK (fit_result IN ('too_tight', 'slightly_tight', 'perfect', 'slightly_loose', 'too_loose')),
    problem_area TEXT CHECK (problem_area IN ('chest', 'waist', 'hip', 'shoulder', 'sleeve', 'length', 'none')),
    was_returned BOOLEAN NOT NULL DEFAULT false,
    note TEXT,
    body_snapshot JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fit_feedback_user_product_size UNIQUE (user_id, product_id, size_bought)
);

-- 14. saved_items table
CREATE TABLE public.saved_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    size_label TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'saved' CHECK (status IN ('saved', 'bought', 'dismissed')),
    bought_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 15. store_adapters table
CREATE TABLE public.store_adapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT NOT NULL UNIQUE,
    platform TEXT CHECK (platform IN ('shopify', 'woocommerce', 'custom')),
    selectors JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 16. coverage_requests table
CREATE TABLE public.coverage_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    page_url TEXT NOT NULL,
    domain TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes specified in requirements
CREATE INDEX idx_products_canonical_url ON public.products(canonical_url);
CREATE INDEX idx_products_retailer_id ON public.products(retailer_id);
CREATE INDEX idx_size_chart_rows_chart_id ON public.size_chart_rows(size_chart_id);
CREATE INDEX idx_fit_feedback_product_id ON public.fit_feedback(product_id);
CREATE INDEX idx_recommendations_product_created ON public.recommendations(product_id, created_at);

