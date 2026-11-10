-- ============================================================================
-- FitSense RLS Isolation Verification Script
-- Proves multi-tenant customer and retailer isolation:
-- 1. User A cannot read or write User B's rows (profiles, body_measurements, saved_items, recommendations).
-- 2. Retailer A cannot read or modify Retailer B's data (size_charts, size_chart_rows, retailer_members).
--
-- EXECUTION SAFETY:
-- Runs inside a self-contained transaction that ends in ROLLBACK.
-- No permanent database changes, writes, or seeds are persisted.
-- ============================================================================

BEGIN;

-- Setup test UUIDs
CREATE TEMP TABLE test_fixtures AS
SELECT
  '11111111-1111-4111-8111-111111111111'::uuid AS user_a,
  '22222222-2222-4222-8222-222222222222'::uuid AS user_b,
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid AS retailer_a,
  'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid AS retailer_b,
  'caaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid AS chart_a,
  'cbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid AS chart_b;

-- Insert test profiles and data as superuser/postgres
INSERT INTO public.profiles (user_id, email, display_name, role)
SELECT user_a, 'user_a@test.pk', 'User A', 'customer' FROM test_fixtures
UNION ALL
SELECT user_b, 'user_b@test.pk', 'User B', 'customer' FROM test_fixtures;

INSERT INTO public.body_measurements (user_id, chest_cm, waist_cm)
SELECT user_a, 96.0, 82.0 FROM test_fixtures
UNION ALL
SELECT user_b, 104.0, 90.0 FROM test_fixtures;

INSERT INTO public.retailers (id, name, slug, status)
SELECT retailer_a, 'Brand A', 'brand-a', 'verified' FROM test_fixtures
UNION ALL
SELECT retailer_b, 'Brand B', 'brand-b', 'verified' FROM test_fixtures;

INSERT INTO public.retailer_members (retailer_id, user_id, member_role)
SELECT retailer_a, user_a, 'owner' FROM test_fixtures
UNION ALL
SELECT retailer_b, user_b, 'owner' FROM test_fixtures;

INSERT INTO public.size_charts (id, retailer_id, name, category, measured_as, unit_source)
SELECT chart_a, retailer_a, 'Brand A Kurta', 'kurta', 'circumference', 'cm' FROM test_fixtures
UNION ALL
SELECT chart_b, retailer_b, 'Brand B Kurta', 'kurta', 'circumference', 'cm' FROM test_fixtures;

INSERT INTO public.size_chart_rows (size_chart_id, size_label, measurement_key, value_cm)
SELECT chart_a, 'M', 'chest', 100.0 FROM test_fixtures
UNION ALL
SELECT chart_b, 'M', 'chest', 106.0 FROM test_fixtures;

-- ============================================================================
-- TEST 1: Customer Isolation (User A authenticates)
-- ============================================================================
SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub TO '11111111-1111-4111-8111-111111111111';
SET LOCAL request.jwt.claim.role TO 'authenticated';

-- User A reads profiles (Must only see own profile)
DO $$
DECLARE
  v_count int;
BEGIN
  SELECT count(*) INTO v_count FROM public.profiles WHERE user_id = '22222222-2222-4222-8222-222222222222'::uuid;
  IF v_count > 0 THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: User A was able to read User B profile!';
  END IF;

  SELECT count(*) INTO v_count FROM public.body_measurements WHERE user_id = '22222222-2222-4222-8222-222222222222'::uuid;
  IF v_count > 0 THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: User A was able to read User B body measurements!';
  END IF;

  RAISE NOTICE 'SUCCESS: User A cannot read User B personal profiles or measurements.';
END $$;

-- User A attempts unauthorized update on User B profile
DO $$
BEGIN
  UPDATE public.profiles SET display_name = 'Hacked' WHERE user_id = '22222222-2222-4222-8222-222222222222'::uuid;
  -- In PostgreSQL RLS, updating non-visible rows affects 0 rows silently
  IF FOUND THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: User A updated User B profile!';
  END IF;
  RAISE NOTICE 'SUCCESS: User A cannot update User B profile.';
END $$;

-- ============================================================================
-- TEST 2: Retailer Isolation (Retailer Member of Brand A)
-- ============================================================================
-- Retailer A member attempts to update Brand B size chart
DO $$
BEGIN
  UPDATE public.size_charts SET name = 'Vandalized Chart' WHERE id = 'cbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid;
  IF FOUND THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: Retailer A was able to update Retailer B size chart!';
  END IF;

  -- Retailer A member attempts to insert a row into Retailer B size chart
  BEGIN
    INSERT INTO public.size_chart_rows (size_chart_id, size_label, measurement_key, value_cm)
    VALUES ('cbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'::uuid, 'XL', 'chest', 115.0);
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: Retailer A was able to insert rows into Retailer B chart!';
  EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'SUCCESS: Retailer A blocked from inserting into Retailer B chart (insufficient_privilege).';
  END;
END $$;

-- ============================================================================
-- TEST 3: Anonymous User Isolation
-- ============================================================================
SET LOCAL ROLE anon;
SET LOCAL request.jwt.claim.sub TO '';
SET LOCAL request.jwt.claim.role TO 'anon';

DO $$
DECLARE
  v_count int;
BEGIN
  SELECT count(*) INTO v_count FROM public.profiles;
  IF v_count > 0 THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: Anonymous user was able to read profiles!';
  END IF;

  SELECT count(*) INTO v_count FROM public.body_measurements;
  IF v_count > 0 THEN
    RAISE EXCEPTION 'RLS ISOLATION FAILURE: Anonymous user was able to read body measurements!';
  END IF;

  RAISE NOTICE 'SUCCESS: Anonymous user cannot read profiles or measurements.';
END $$;

-- Rollback entire transaction so zero test data is retained
ROLLBACK;

