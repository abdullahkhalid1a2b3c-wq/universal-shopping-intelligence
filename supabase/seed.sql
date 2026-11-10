-- ====================================================================
-- FitSense Seed Data (SEC-06: Strict Demo Demarcation)
-- CAUTION: Synthetic placeholder data for testing and development only.
-- Real commercial brands are marked as status = 'pending' and is_demo = true.
-- Charts have verified_at = NULL and are marked is_demo = true.
-- To completely purge all seed data:
--     DELETE FROM public.retailers WHERE is_demo = true;
-- (Foreign key cascades will automatically delete associated charts, rows, and products).
-- ====================================================================

-- 1. Demo Retailers (status = 'pending', is_demo = true)
INSERT INTO public.retailers (id, name, slug, website_domain, logo_url, supports_cod, return_policy_url, status, is_demo)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Khaadi (Demo)', 'khaadi', 'pk.khaadi.com', 'https://pk.khaadi.com/logo.svg', true, 'https://pk.khaadi.com/returns', 'pending', true),
    ('22222222-2222-2222-2222-222222222222', 'Sapphire (Demo)', 'sapphire', 'pk.sapphireonline.pk', 'https://pk.sapphireonline.pk/logo.svg', true, 'https://pk.sapphireonline.pk/return-exchange', 'pending', true),
    ('33333333-3333-3333-3333-333333333333', 'Breakout (Demo)', 'breakout', 'breakout.com.pk', 'https://breakout.com.pk/logo.png', true, 'https://breakout.com.pk/pages/returns-exchanges', 'pending', true),
    ('44444444-4444-4444-4444-444444444444', 'Diners (Demo)', 'diners', 'diners.com.pk', 'https://diners.com.pk/logo.png', true, 'https://diners.com.pk/policies/refund-policy', 'pending', true),
    ('55555555-5555-5555-5555-555555555555', 'Outfitters (Demo)', 'outfitters', 'outfitters.com.pk', 'https://outfitters.com.pk/logo.png', true, 'https://outfitters.com.pk/pages/returns-exchanges', 'pending', true)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    is_demo = EXCLUDED.is_demo
WHERE retailers.is_demo = true;

-- 2. Store Adapters (All disabled by default pending verification)
INSERT INTO public.store_adapters (domain, platform, selectors, is_enabled)
VALUES
    ('pk.khaadi.com', 'custom', '{"product_title": "h1.product-name", "size_buttons": ".swatch-size-button", "price": ".sales .value"}'::jsonb, false),
    ('pk.sapphireonline.pk', 'shopify', '{"product_title": ".product__title", "size_buttons": "input[name=\"Size\"] + label", "price": ".price__regular"}'::jsonb, false),
    ('breakout.com.pk', 'shopify', '{"product_title": ".product-title", "size_buttons": ".variant-input label", "price": ".product-price"}'::jsonb, false),
    ('diners.com.pk', 'shopify', '{"product_title": "h1.product_title", "size_buttons": ".size-swatch", "price": ".price-item--regular"}'::jsonb, false),
    ('outfitters.com.pk', 'shopify', '{"product_title": ".product-single__title", "size_buttons": ".variant-input-wrap label", "price": ".product__price"}'::jsonb, false)
ON CONFLICT (domain) DO UPDATE SET
    platform = EXCLUDED.platform,
    selectors = EXCLUDED.selectors;

-- 3. Demo Size Charts (is_demo = true, verified_at = NULL)
INSERT INTO public.size_charts (id, retailer_id, name, category, gender_category, measured_as, unit_source, source_note, verified_at, is_demo)
VALUES
    -- Khaadi Demo Charts
    ('c1111111-0001-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Demo Khaadi Women Kurta Chart', 'kurta', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c1111111-0002-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'Demo Khaadi Women Shirt Chart', 'shirt', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c1111111-0003-0000-0000-000000000003', '11111111-1111-1111-1111-111111111111', 'Demo Khaadi Women Trouser Chart', 'trouser', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),

    -- Sapphire Demo Charts
    ('c2222222-0001-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'Demo Sapphire Women Kurta Chart', 'kurta', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c2222222-0002-0000-0000-000000000002', '22222222-2222-2222-2222-222222222222', 'Demo Sapphire Men Casual Shirt Chart', 'shirt', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c2222222-0003-0000-0000-000000000003', '22222222-2222-2222-2222-222222222222', 'Demo Sapphire Men Chinos Chart', 'trouser', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),

    -- Breakout Demo Charts
    ('c3333333-0001-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 'Demo Breakout Graphic Tee Chart', 'tshirt_top', 'unisex', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c3333333-0002-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 'Demo Breakout Men Slim Jeans Chart', 'jeans', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c3333333-0003-0000-0000-000000000003', '33333333-3333-3333-3333-333333333333', 'Demo Breakout Women Summer Dress Chart', 'dress', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),

    -- Diners Demo Charts
    ('c4444444-0001-0000-0000-000000000001', '44444444-4444-4444-4444-444444444444', 'Demo Diners Executive Shirt Chart', 'shirt', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c4444444-0002-0000-0000-000000000002', '44444444-4444-4444-4444-444444444444', 'Demo Diners Formal Trouser Chart', 'trouser', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c4444444-0003-0000-0000-000000000003', '44444444-4444-4444-4444-444444444444', 'Demo Diners Men Traditional Kurta Chart', 'kurta', 'mens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),

    -- Outfitters Demo Charts
    ('c5555555-0001-0000-0000-000000000001', '55555555-5555-5555-5555-555555555555', 'Demo Outfitters Boxy Tee Chart', 'tshirt_top', 'unisex', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c5555555-0002-0000-0000-000000000002', '55555555-5555-5555-5555-555555555555', 'Demo Outfitters Carpenter Jeans Chart', 'jeans', 'unisex', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true),
    ('c5555555-0003-0000-0000-000000000003', '55555555-5555-5555-5555-555555555555', 'Demo Outfitters Slip Dress Chart', 'dress', 'womens', 'circumference', 'cm', 'Demo / Synthetic placeholder chart for testing only', NULL, true)
ON CONFLICT (id) DO NOTHING;

-- 4. Demo Size Chart Rows (Plausible Values in cm)
INSERT INTO public.size_chart_rows (size_chart_id, size_label, sort_order, measurement_key, value_cm)
VALUES
    -- Breakout Graphic Tee (Tshirt): chest, shoulder, length
    ('c3333333-0001-0000-0000-000000000001', 'S', 1, 'chest', 98.0),
    ('c3333333-0001-0000-0000-000000000001', 'S', 1, 'shoulder', 42.0),
    ('c3333333-0001-0000-0000-000000000001', 'S', 1, 'length', 68.0),
    ('c3333333-0001-0000-0000-000000000001', 'M', 2, 'chest', 104.0),
    ('c3333333-0001-0000-0000-000000000001', 'M', 2, 'shoulder', 44.0),
    ('c3333333-0001-0000-0000-000000000001', 'M', 2, 'length', 70.0),
    ('c3333333-0001-0000-0000-000000000001', 'L', 3, 'chest', 110.0),
    ('c3333333-0001-0000-0000-000000000001', 'L', 3, 'shoulder', 46.0),
    ('c3333333-0001-0000-0000-000000000001', 'L', 3, 'length', 72.0),
    ('c3333333-0001-0000-0000-000000000001', 'XL', 4, 'chest', 116.0),
    ('c3333333-0001-0000-0000-000000000001', 'XL', 4, 'shoulder', 48.0),
    ('c3333333-0001-0000-0000-000000000001', 'XL', 4, 'length', 74.0),

    -- Outfitters Boxy Tee (Tshirt): chest, shoulder, length
    ('c5555555-0001-0000-0000-000000000001', 'S', 1, 'chest', 102.0),
    ('c5555555-0001-0000-0000-000000000001', 'S', 1, 'shoulder', 45.0),
    ('c5555555-0001-0000-0000-000000000001', 'S', 1, 'length', 69.0),
    ('c5555555-0001-0000-0000-000000000001', 'M', 2, 'chest', 108.0),
    ('c5555555-0001-0000-0000-000000000001', 'M', 2, 'shoulder', 47.0),
    ('c5555555-0001-0000-0000-000000000001', 'M', 2, 'length', 71.0),
    ('c5555555-0001-0000-0000-000000000001', 'L', 3, 'chest', 114.0),
    ('c5555555-0001-0000-0000-000000000001', 'L', 3, 'shoulder', 49.0),
    ('c5555555-0001-0000-0000-000000000001', 'L', 3, 'length', 73.0),
    ('c5555555-0001-0000-0000-000000000001', 'XL', 4, 'chest', 120.0),
    ('c5555555-0001-0000-0000-000000000001', 'XL', 4, 'shoulder', 51.0),
    ('c5555555-0001-0000-0000-000000000001', 'XL', 4, 'length', 75.0),

    -- Khaadi Women Kurta: chest, shoulder, hip, length
    ('c1111111-0001-0000-0000-000000000001', 'XS', 1, 'chest', 92.0),
    ('c1111111-0001-0000-0000-000000000001', 'XS', 1, 'shoulder', 36.0),
    ('c1111111-0001-0000-0000-000000000001', 'XS', 1, 'hip', 98.0),
    ('c1111111-0001-0000-0000-000000000001', 'S', 2, 'chest', 98.0),
    ('c1111111-0001-0000-0000-000000000001', 'S', 2, 'shoulder', 37.5),
    ('c1111111-0001-0000-0000-000000000001', 'S', 2, 'hip', 104.0),
    ('c1111111-0001-0000-0000-000000000001', 'M', 3, 'chest', 106.0),
    ('c1111111-0001-0000-0000-000000000001', 'M', 3, 'shoulder', 39.0),
    ('c1111111-0001-0000-0000-000000000001', 'M', 3, 'hip', 112.0),
    ('c1111111-0001-0000-0000-000000000001', 'L', 4, 'chest', 114.0),
    ('c1111111-0001-0000-0000-000000000001', 'L', 4, 'shoulder', 41.0),
    ('c1111111-0001-0000-0000-000000000001', 'L', 4, 'hip', 120.0),

    -- Sapphire Women Kurta
    ('c2222222-0001-0000-0000-000000000001', 'S', 1, 'chest', 96.0),
    ('c2222222-0001-0000-0000-000000000001', 'S', 1, 'shoulder', 37.0),
    ('c2222222-0001-0000-0000-000000000001', 'S', 1, 'hip', 102.0),
    ('c2222222-0001-0000-0000-000000000001', 'M', 2, 'chest', 104.0),
    ('c2222222-0001-0000-0000-000000000001', 'M', 2, 'shoulder', 38.5),
    ('c2222222-0001-0000-0000-000000000001', 'M', 2, 'hip', 110.0),
    ('c2222222-0001-0000-0000-000000000001', 'L', 3, 'chest', 112.0),
    ('c2222222-0001-0000-0000-000000000001', 'L', 3, 'shoulder', 40.0),
    ('c2222222-0001-0000-0000-000000000001', 'L', 3, 'hip', 118.0),

    -- Diners Kurta (Men)
    ('c4444444-0003-0000-0000-000000000003', 'S', 1, 'chest', 102.0),
    ('c4444444-0003-0000-0000-000000000003', 'S', 1, 'shoulder', 43.0),
    ('c4444444-0003-0000-0000-000000000003', 'M', 2, 'chest', 108.0),
    ('c4444444-0003-0000-0000-000000000003', 'M', 2, 'shoulder', 45.0),
    ('c4444444-0003-0000-0000-000000000003', 'L', 3, 'chest', 114.0),
    ('c4444444-0003-0000-0000-000000000003', 'L', 3, 'shoulder', 47.0),

    -- Diners Formal Shirt
    ('c4444444-0001-0000-0000-000000000001', '15', 1, 'chest', 104.0),
    ('c4444444-0001-0000-0000-000000000001', '15', 1, 'waist', 96.0),
    ('c4444444-0001-0000-0000-000000000001', '15', 1, 'shoulder', 44.0),
    ('c4444444-0001-0000-0000-000000000001', '15.5', 2, 'chest', 108.0),
    ('c4444444-0001-0000-0000-000000000001', '15.5', 2, 'waist', 100.0),
    ('c4444444-0001-0000-0000-000000000001', '15.5', 2, 'shoulder', 45.5),
    ('c4444444-0001-0000-0000-000000000001', '16', 3, 'chest', 112.0),
    ('c4444444-0001-0000-0000-000000000001', '16', 3, 'waist', 104.0),
    ('c4444444-0001-0000-0000-000000000001', '16', 3, 'shoulder', 47.0),

    -- Sapphire Men Casual Shirt
    ('c2222222-0002-0000-0000-000000000002', 'S', 1, 'chest', 102.0),
    ('c2222222-0002-0000-0000-000000000002', 'S', 1, 'shoulder', 43.0),
    ('c2222222-0002-0000-0000-000000000002', 'M', 2, 'chest', 108.0),
    ('c2222222-0002-0000-0000-000000000002', 'M', 2, 'shoulder', 45.0),
    ('c2222222-0002-0000-0000-000000000002', 'L', 3, 'chest', 114.0),
    ('c2222222-0002-0000-0000-000000000002', 'L', 3, 'shoulder', 47.0),

    -- Khaadi Women Shirt
    ('c1111111-0002-0000-0000-000000000002', 'S', 1, 'chest', 96.0),
    ('c1111111-0002-0000-0000-000000000002', 'S', 1, 'shoulder', 37.0),
    ('c1111111-0002-0000-0000-000000000002', 'M', 2, 'chest', 102.0),
    ('c1111111-0002-0000-0000-000000000002', 'M', 2, 'shoulder', 38.5),
    ('c1111111-0002-0000-0000-000000000002', 'L', 3, 'chest', 110.0),
    ('c1111111-0002-0000-0000-000000000002', 'L', 3, 'shoulder', 40.5),

    -- Breakout Jeans (Men)
    ('c3333333-0002-0000-0000-000000000002', '30', 1, 'waist', 78.0),
    ('c3333333-0002-0000-0000-000000000002', '30', 1, 'hip', 94.0),
    ('c3333333-0002-0000-0000-000000000002', '30', 1, 'inseam', 79.0),
    ('c3333333-0002-0000-0000-000000000002', '32', 2, 'waist', 83.0),
    ('c3333333-0002-0000-0000-000000000002', '32', 2, 'hip', 99.0),
    ('c3333333-0002-0000-0000-000000000002', '32', 2, 'inseam', 80.0),
    ('c3333333-0002-0000-0000-000000000002', '34', 3, 'waist', 88.0),
    ('c3333333-0002-0000-0000-000000000002', '34', 3, 'hip', 104.0),
    ('c3333333-0002-0000-0000-000000000002', '34', 3, 'inseam', 81.0),

    -- Outfitters Jeans
    ('c5555555-0002-0000-0000-000000000002', '30', 1, 'waist', 80.0),
    ('c5555555-0002-0000-0000-000000000002', '30', 1, 'hip', 98.0),
    ('c5555555-0002-0000-0000-000000000002', '30', 1, 'inseam', 78.0),
    ('c5555555-0002-0000-0000-000000000002', '32', 2, 'waist', 85.0),
    ('c5555555-0002-0000-0000-000000000002', '32', 2, 'hip', 103.0),
    ('c5555555-0002-0000-0000-000000000002', '32', 2, 'inseam', 79.0),
    ('c5555555-0002-0000-0000-000000000002', '34', 3, 'waist', 90.0),
    ('c5555555-0002-0000-0000-000000000002', '34', 3, 'hip', 108.0),
    ('c5555555-0002-0000-0000-000000000002', '34', 3, 'inseam', 80.0),

    -- Diners Trouser
    ('c4444444-0002-0000-0000-000000000002', '32', 1, 'waist', 82.0),
    ('c4444444-0002-0000-0000-000000000002', '32', 1, 'hip', 98.0),
    ('c4444444-0002-0000-0000-000000000002', '32', 1, 'inseam', 81.0),
    ('c4444444-0002-0000-0000-000000000002', '34', 2, 'waist', 87.0),
    ('c4444444-0002-0000-0000-000000000002', '34', 2, 'hip', 103.0),
    ('c4444444-0002-0000-0000-000000000002', '34', 2, 'inseam', 82.0),

    -- Sapphire Chinos
    ('c2222222-0003-0000-0000-000000000003', '32', 1, 'waist', 83.0),
    ('c2222222-0003-0000-0000-000000000003', '32', 1, 'hip', 100.0),
    ('c2222222-0003-0000-0000-000000000003', '34', 2, 'waist', 88.0),
    ('c2222222-0003-0000-0000-000000000003', '34', 2, 'hip', 105.0),

    -- Khaadi Trouser (Women)
    ('c1111111-0003-0000-0000-000000000003', 'S', 1, 'waist', 70.0),
    ('c1111111-0003-0000-0000-000000000003', 'S', 1, 'hip', 96.0),
    ('c1111111-0003-0000-0000-000000000003', 'M', 2, 'waist', 76.0),
    ('c1111111-0003-0000-0000-000000000003', 'M', 2, 'hip', 102.0),
    ('c1111111-0003-0000-0000-000000000003', 'L', 3, 'waist', 82.0),
    ('c1111111-0003-0000-0000-000000000003', 'L', 3, 'hip', 108.0),

    -- Breakout Summer Dress
    ('c3333333-0003-0000-0000-000000000003', 'S', 1, 'chest', 88.0),
    ('c3333333-0003-0000-0000-000000000003', 'S', 1, 'waist', 70.0),
    ('c3333333-0003-0000-0000-000000000003', 'S', 1, 'hip', 94.0),
    ('c3333333-0003-0000-0000-000000000003', 'M', 2, 'chest', 94.0),
    ('c3333333-0003-0000-0000-000000000003', 'M', 2, 'waist', 76.0),
    ('c3333333-0003-0000-0000-000000000003', 'M', 2, 'hip', 100.0),

    -- Outfitters Slip Dress
    ('c5555555-0003-0000-0000-000000000003', 'S', 1, 'chest', 86.0),
    ('c5555555-0003-0000-0000-000000000003', 'S', 1, 'waist', 68.0),
    ('c5555555-0003-0000-0000-000000000003', 'S', 1, 'hip', 92.0),
    ('c5555555-0003-0000-0000-000000000003', 'M', 2, 'chest', 92.0),
    ('c5555555-0003-0000-0000-000000000003', 'M', 2, 'waist', 74.0),
    ('c5555555-0003-0000-0000-000000000003', 'M', 2, 'hip', 98.0)
ON CONFLICT (size_chart_id, size_label, measurement_key) DO UPDATE SET
    value_cm = EXCLUDED.value_cm;

-- 5. Demo Products (3 per retailer, is_demo = true)
INSERT INTO public.products (id, retailer_id, name, category, gender_category, product_url, canonical_url, external_id, size_chart_id, fabric, stretch_pct, thickness, transparency, season, is_active, is_demo, fit_cut)
VALUES
    -- Khaadi Demo Products
    ('p1111111-0001-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Embroidered Lawn Kurta', 'kurta', 'womens', 'https://pk.khaadi.com/p/emb-kurta-101.html', 'https://pk.khaadi.com/p/emb-kurta-101.html', 'KHD-K-101', 'c1111111-0001-0000-0000-000000000001', 'Lawn Cotton', 0, 'light', 'opaque', 'Summer', true, true, 'regular'),
    ('p1111111-0002-0000-0000-000000000002', '11111111-1111-1111-1111-111111111111', 'Floral Buttoned Shirt', 'shirt', 'womens', 'https://pk.khaadi.com/p/floral-shirt-102.html', 'https://pk.khaadi.com/p/floral-shirt-102.html', 'KHD-S-102', 'c1111111-0002-0000-0000-000000000002', 'Cotton Poplin', 0, 'light', 'opaque', 'Summer', true, true, 'regular'),
    ('p1111111-0003-0000-0000-000000000003', '11111111-1111-1111-1111-111111111111', 'Solid Cotton Trouser', 'trouser', 'womens', 'https://pk.khaadi.com/p/cotton-trouser-103.html', 'https://pk.khaadi.com/p/cotton-trouser-103.html', 'KHD-T-103', 'c1111111-0003-0000-0000-000000000001', 'Cotton Cambric', 2, 'medium', 'opaque', 'All Season', true, true, 'regular'),

    -- Sapphire Demo Products
    ('p2222222-0001-0000-0000-000000000001', '22222222-2222-2222-2222-222222222222', 'Printed Daily Kurta', 'kurta', 'womens', 'https://pk.sapphireonline.pk/products/printed-daily-kurta', 'https://pk.sapphireonline.pk/products/printed-daily-kurta', 'SPH-K-201', 'c2222222-0001-0000-0000-000000000001', 'Cotton Lawn', 0, 'light', 'opaque', 'Summer', true, true, 'relaxed'),
    ('p2222222-0002-0000-0000-000000000002', '22222222-2222-2222-2222-222222222222', 'Men Casual Oxford Shirt', 'shirt', 'mens', 'https://pk.sapphireonline.pk/products/men-oxford-shirt', 'https://pk.sapphireonline.pk/products/men-oxford-shirt', 'SPH-S-202', 'c2222222-0002-0000-0000-000000000002', 'Oxford Cotton', 0, 'medium', 'opaque', 'All Season', true, true, 'regular'),
    ('p2222222-0003-0000-0000-000000000003', '22222222-2222-2222-2222-222222222222', 'Men Slim Chino Trouser', 'trouser', 'mens', 'https://pk.sapphireonline.pk/products/men-slim-chino', 'https://pk.sapphireonline.pk/products/men-slim-chino', 'SPH-T-203', 'c2222222-0003-0000-0000-000000000003', 'Cotton Twill', 3, 'medium', 'opaque', 'All Season', true, true, 'slim'),

    -- Breakout Demo Products
    ('p3333333-0001-0000-0000-000000000001', '33333333-3333-3333-3333-333333333333', 'Vintage Graphic Crewneck Tee', 'tshirt_top', 'unisex', 'https://breakout.com.pk/products/graphic-crewneck-tee', 'https://breakout.com.pk/products/graphic-crewneck-tee', 'BRK-T-301', 'c3333333-0001-0000-0000-000000000001', '100% Combed Cotton', 5, 'medium', 'opaque', 'Summer', true, true, 'regular'),
    ('p3333333-0002-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 'Raw Wash Slim Fit Jeans', 'jeans', 'mens', 'https://breakout.com.pk/products/raw-wash-slim-jeans', 'https://breakout.com.pk/products/raw-wash-slim-jeans', 'BRK-J-302', 'c3333333-0002-0000-0000-000000000002', 'Stretch Denim', 2, 'heavy', 'opaque', 'All Season', true, true, 'slim'),
    ('p3333333-0003-0000-0000-000000000003', '33333333-3333-3333-3333-333333333333', 'A-Line Tiered Summer Dress', 'dress', 'womens', 'https://breakout.com.pk/products/tiered-summer-dress', 'https://breakout.com.pk/products/tiered-summer-dress', 'BRK-D-303', 'c3333333-0003-0000-0000-000000000003', 'Rayon Blend', 0, 'light', 'opaque', 'Summer', true, true, 'regular'),

    -- Diners Demo Products
    ('p4444444-0001-0000-0000-000000000001', '44444444-4444-4444-4444-444444444444', 'Executive Non-Iron Formal Shirt', 'shirt', 'mens', 'https://diners.com.pk/products/executive-formal-shirt', 'https://diners.com.pk/products/executive-formal-shirt', 'DNR-S-401', 'c4444444-0001-0000-0000-000000000001', 'Egyptian Cotton', 0, 'medium', 'opaque', 'All Season', true, true, 'regular'),
    ('p4444444-0002-0000-0000-000000000002', '44444444-4444-4444-4444-444444444444', 'Classic Wool Blend Formal Trousers', 'trouser', 'mens', 'https://diners.com.pk/products/formal-trousers', 'https://diners.com.pk/products/formal-trousers', 'DNR-T-402', 'c4444444-0002-0000-0000-000000000002', 'Poly-Viscose Wool Blend', 0, 'heavy', 'opaque', 'Winter', true, true, 'regular'),
    ('p4444444-0003-0000-0000-000000000003', '44444444-4444-4444-4444-444444444444', 'Festive Jamawar Trim Kurta', 'kurta', 'mens', 'https://diners.com.pk/products/festive-kurta', 'https://diners.com.pk/products/festive-kurta', 'DNR-K-403', 'c4444444-0003-0000-0000-000000000003', 'Raw Silk Blend', 0, 'medium', 'opaque', 'Festive', true, true, 'regular'),

    -- Outfitters Demo Products
    ('p5555555-0001-0000-0000-000000000001', '55555555-5555-5555-5555-555555555555', 'Heavyweight Boxy Drop-Shoulder Tee', 'tshirt_top', 'unisex', 'https://outfitters.com.pk/products/heavyweight-boxy-tee', 'https://outfitters.com.pk/products/heavyweight-boxy-tee', 'OFT-T-501', 'c5555555-0001-0000-0000-000000000001', '240 GSM Cotton', 0, 'heavy', 'opaque', 'Summer', true, true, 'relaxed'),
    ('p5555555-0002-0000-0000-000000000002', '55555555-5555-5555-5555-555555555555', 'Wide Leg Utility Carpenter Jeans', 'jeans', 'unisex', 'https://outfitters.com.pk/products/utility-carpenter-jeans', 'https://outfitters.com.pk/products/utility-carpenter-jeans', 'OFT-J-502', 'c5555555-0002-0000-0000-000000000002', 'Rigid Cotton Denim', 0, 'heavy', 'opaque', 'All Season', true, true, 'relaxed'),
    ('p5555555-0003-0000-0000-000000000003', '55555555-5555-5555-5555-555555555555', 'Minimalist Satin Midi Slip Dress', 'dress', 'womens', 'https://outfitters.com.pk/products/satin-slip-dress', 'https://outfitters.com.pk/products/satin-slip-dress', 'OFT-D-503', 'c5555555-0003-0000-0000-000000000003', 'Poly Satin', 2, 'light', 'opaque', 'Summer', true, true, 'regular')
ON CONFLICT (canonical_url) DO UPDATE SET
    name = EXCLUDED.name,
    size_chart_id = EXCLUDED.size_chart_id,
    is_demo = true
WHERE products.is_demo = true;
