-- Migration 00003: Analytics Views & Storage Bucket Configuration
-- Creates privacy-preserving, tenant-isolated aggregated analytics views with k-anonymity protection
-- and sets up the private 'size-chart-images' storage bucket with safe, regex-validated UUID folder policies.

-- ==========================================
-- 1. Analytics Views (Aggregated, Privacy-Preserving, No PII)
-- ==========================================

-- View: v_product_fit_stats
-- Calculates customer feedback count, fit distribution percentages, and return count per product and size.
-- Applies strict k-anonymity (HAVING COUNT >= 5) with full row suppression for small groups.
-- NOTE: Each count represents a distinct customer review (governed by uq_fit_feedback_user_product_size).
-- Groups with < 5 customer reviews are completely suppressed to prevent re-identification and before/after delta attacks.
CREATE OR REPLACE VIEW public.v_product_fit_stats AS
SELECT
    p.id AS product_id,
    p.retailer_id,
    p.name AS product_name,
    p.is_demo,
    fb.size_bought,
    COUNT(fb.id) AS total_feedback,
    ROUND(COUNT(CASE WHEN fb.fit_result IN ('too_tight', 'slightly_tight') THEN 1 END)::numeric / COUNT(fb.id) * 100, 2) AS pct_too_tight,
    ROUND(COUNT(CASE WHEN fb.fit_result = 'perfect' THEN 1 END)::numeric / COUNT(fb.id) * 100, 2) AS pct_perfect,
    ROUND(COUNT(CASE WHEN fb.fit_result IN ('too_loose', 'slightly_loose') THEN 1 END)::numeric / COUNT(fb.id) * 100, 2) AS pct_too_loose,
    COUNT(CASE WHEN fb.was_returned = true THEN 1 END) AS return_count
FROM public.products p
JOIN public.fit_feedback fb ON fb.product_id = p.id
WHERE (public.is_retailer_member(p.retailer_id) OR public.is_admin())
GROUP BY p.id, p.retailer_id, p.name, p.is_demo, fb.size_bought
HAVING COUNT(fb.id) >= 5;

REVOKE ALL ON public.v_product_fit_stats FROM PUBLIC;
GRANT SELECT ON public.v_product_fit_stats TO authenticated, service_role;

-- View: v_product_recommendation_counts
-- Aggregates recommendation count per product per calendar week with strict tenant scoping.
CREATE OR REPLACE VIEW public.v_product_recommendation_counts AS
SELECT
    p.id AS product_id,
    p.retailer_id,
    p.name AS product_name,
    p.is_demo,
    date_trunc('week', r.created_at) AS week_start,
    COUNT(r.id) AS recommendation_count
FROM public.products p
JOIN public.recommendations r ON r.product_id = p.id
WHERE (public.is_retailer_member(p.retailer_id) OR public.is_admin())
GROUP BY p.id, p.retailer_id, p.name, p.is_demo, date_trunc('week', r.created_at);

REVOKE ALL ON public.v_product_recommendation_counts FROM PUBLIC;
GRANT SELECT ON public.v_product_recommendation_counts TO authenticated, service_role;

-- ==========================================
-- 2. Safe Storage Folder Parsing Function (SEC-02)
-- ==========================================

-- Robust parser that extracts the retailer UUID from the object path (<retailer_id>/<filename>)
-- Safely rejects root files, malformed paths, and non-UUID folder names without throwing SQL exceptions.
CREATE OR REPLACE FUNCTION public.safe_storage_retailer_id(object_name TEXT)
RETURNS UUID
LANGUAGE plpgsql
IMMUTABLE
SET search_path = public, pg_temp
AS $$
DECLARE
    folder_part TEXT;
BEGIN
    IF object_name IS NULL THEN
        RETURN NULL;
    END IF;

    -- Extract root folder component before first slash
    folder_part := split_part(object_name, '/', 1);

    -- Validate that folder_part matches standard 36-char hyphenated UUID format
    IF folder_part ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' THEN
        RETURN folder_part::uuid;
    END IF;

    RETURN NULL;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$;

REVOKE ALL ON FUNCTION public.safe_storage_retailer_id(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.safe_storage_retailer_id(TEXT) TO authenticated, service_role;

-- ==========================================
-- 3. Storage Bucket: size-chart-images
-- ==========================================

-- Insert the private bucket if it doesn't already exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'size-chart-images',
    'size-chart-images',
    false,
    10485760, -- 10MB limit
    ARRAY['image/png', 'image/jpeg', 'image/webp', 'image/gif']
)
ON CONFLICT (id) DO UPDATE SET
    public = false;

-- Storage RLS Policies
-- Files are stored under path: <retailer_id>/<filename>
-- Access is strictly restricted to active members of <retailer_id> or platform admins.

CREATE POLICY "Retailer members can read size chart images"
ON storage.objects FOR SELECT TO authenticated
USING (
    bucket_id = 'size-chart-images'
    AND (
        (public.safe_storage_retailer_id(name) IS NOT NULL 
         AND public.is_retailer_member(public.safe_storage_retailer_id(name)))
        OR public.is_admin()
    )
);

CREATE POLICY "Retailer members can upload size chart images"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
    bucket_id = 'size-chart-images'
    AND (
        (public.safe_storage_retailer_id(name) IS NOT NULL 
         AND public.is_retailer_member(public.safe_storage_retailer_id(name)))
        OR public.is_admin()
    )
);

CREATE POLICY "Retailer members can update size chart images"
ON storage.objects FOR UPDATE TO authenticated
USING (
    bucket_id = 'size-chart-images'
    AND (
        (public.safe_storage_retailer_id(name) IS NOT NULL 
         AND public.is_retailer_member(public.safe_storage_retailer_id(name)))
        OR public.is_admin()
    )
)
WITH CHECK (
    bucket_id = 'size-chart-images'
    AND (
        (public.safe_storage_retailer_id(name) IS NOT NULL 
         AND public.is_retailer_member(public.safe_storage_retailer_id(name)))
        OR public.is_admin()
    )
);

CREATE POLICY "Retailer members can delete size chart images"
ON storage.objects FOR DELETE TO authenticated
USING (
    bucket_id = 'size-chart-images'
    AND (
        (public.safe_storage_retailer_id(name) IS NOT NULL 
         AND public.is_retailer_member(public.safe_storage_retailer_id(name)))
        OR public.is_admin()
    )
);

