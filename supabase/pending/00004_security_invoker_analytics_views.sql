-- Migration 00004: Ensure Analytics Views Use Security Invoker Mode
-- Explicitly configures security_invoker = true on aggregated analytics views per Check 6 requirements.
-- NOTE: Do not apply automatically; this is a proposed forward-fix migration to be pushed after 00001-00003.

-- 1. Recreate v_product_fit_stats with security_invoker = true
CREATE OR REPLACE VIEW public.v_product_fit_stats
WITH (security_invoker = true)
AS
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

-- 2. Recreate v_product_recommendation_counts with security_invoker = true
CREATE OR REPLACE VIEW public.v_product_recommendation_counts
WITH (security_invoker = true)
AS
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

