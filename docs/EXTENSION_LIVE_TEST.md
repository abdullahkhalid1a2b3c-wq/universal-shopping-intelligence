# FitSense Chrome Extension — Live End-to-End Verification Runbook

## Status: BLOCKED
> [!IMPORTANT]
> **Live verification is currently BLOCKED** because migrations `00001`, `00002`, and `00003` are pending execution on the remote Supabase database.
> The extension code, content script, background service worker, Shadow DOM widget, and unit test suites have been built and verified with mocks and fixtures. Once the remote migrations are pushed, follow the exact steps below.

---

## Prerequisites (Execute Once Migrations are Applied)

1. **Push Remote Database Migrations**:
   ```bash
   npx supabase db push
   ```
2. **Verify Schema Status**:
   ```powershell
   apps\api\.venv\Scripts\python scripts/check_supabase.py
   ```
   Ensure all 10 checks return `PASS`.

---

## Step-by-Step Live Testing Procedure

### Step 1: Create Test Retailer, Product & Size Chart (Demo Mode)
Using the Retailer Dashboard (`http://localhost:3000/retailer`) or via the FastAPI backend / Supabase SQL Editor, insert a test demo product:

```sql
-- 1. Test Retailer
INSERT INTO public.retailers (id, name, slug, website_domain, is_demo, status)
VALUES ('11111111-1111-1111-1111-111111111111', 'Outfitters Demo', 'outfitters-demo', 'outfitters.com.pk', true, 'active')
ON CONFLICT (slug) DO NOTHING;

-- 2. Test Store Adapter
INSERT INTO public.store_adapters (domain, platform, selectors, is_enabled)
VALUES (
    'outfitters.com.pk',
    'shopify',
    '{"productContainer": ".product-form", "sizeButtons": ".size-swatch button, input[name=\\"Size\\"] + label"}'::jsonb,
    true
)
ON CONFLICT (domain) DO UPDATE SET is_enabled = true;

-- 3. Test Size Chart (Circumference)
INSERT INTO public.size_charts (id, retailer_id, name, gender_category, measured_as, is_demo, verified_at)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'Men Graphic Tee Sizing',
    'mens',
    'circumference',
    true,
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Size chart measurements (Chest circumference in cm)
INSERT INTO public.size_chart_rows (size_chart_id, size_label, sort_order, measurement_key, value_cm)
VALUES
    ('22222222-2222-2222-2222-222222222222', 'S', 1, 'chest', 92.0),
    ('22222222-2222-2222-2222-222222222222', 'M', 2, 'chest', 100.0),
    ('22222222-2222-2222-2222-222222222222', 'L', 3, 'chest', 108.0),
    ('22222222-2222-2222-2222-222222222222', 'XL', 4, 'chest', 116.0)
ON CONFLICT DO NOTHING;

-- 4. Test Product
INSERT INTO public.products (
    retailer_id, size_chart_id, name, category, gender_category,
    product_url, canonical_url, fabric, stretch_pct, fit_cut, is_active, is_demo
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'Classic Relaxed Graphic Tee',
    't-shirts and tops',
    'mens',
    'https://outfitters.com.pk/products/classic-graphic-tee?utm_source=test',
    'https://outfitters.com.pk/products/classic-graphic-tee',
    'cotton',
    5.0,
    'regular',
    true,
    true
)
ON CONFLICT (canonical_url) DO NOTHING;
```

---

### Step 2: Build and Load Unpacked Extension

1. Build the extension package:
   ```bash
   cd apps/extension
   pnpm run build
   ```
   Verify that `scripts/scan-secrets.js` completes with `0 secret credentials found`.

2. Open Google Chrome and go to `chrome://extensions/`.
3. Enable **Developer mode** (top-right toggle).
4. Click **Load unpacked** and select `e:\fitapp\apps\extension\dist`.
5. Pin the **FitSense** extension icon in your browser toolbar.

---

### Step 3: Configure User Profile / Guest Mode in Popup

1. Click the **FitSense** icon in the Chrome toolbar.
2. **Scenario A (Guest User)**:
   - Stay on the **Guest Mode** tab.
   - Enter measurements:
     - Chest: `98` cm
     - Waist: `84` cm
     - Hip: `100` cm
   - Click **Save Measurements**. Observe `✓ Saved on Device` confirmation.
3. **Scenario B (Signed-in User)**:
   - Switch to the **Sign In** tab.
   - Enter your customer credentials and sign in.
   - Confirm session card displays email and profile completeness status.

---

### Step 4: Open Product Page & Verify Expected Results

1. Ensure the FastAPI backend is running:
   ```bash
   cd apps/api
   apps\api\.venv\Scripts\uvicorn app.main:app --reload --port 8000
   ```
2. In Google Chrome, navigate to the product URL:
   `https://outfitters.com.pk/products/classic-graphic-tee`

#### Expected Verification Checklist:
- [ ] **Widget Injection**: An isolated floating card appears at the bottom-right corner of the window.
- [ ] **Recommended Size**: Displays **M** (chest 100 cm matches user chest 98 cm + 2 cm regular ease).
- [ ] **Confidence Badge**: Displays **High confidence** with a green badge.
- [ ] **Demo Warning**: Displays `🧪 Demo Data — For evaluation only`.
- [ ] **Explanation**: Clear localized explanation (e.g. "Fits comfortably in the chest with standard ease").
- [ ] **See Why Expander**: Clicking `See why ▾` expands the details drawer with score and preference info without page stutter.
- [ ] **Button Highlighting**: Size button 'M' on the retailer page receives an indigo outline (`outline: 2px solid #6366f1`).
- [ ] **Zero Disruption to Checkout**: The Add-to-Cart button remains completely untouched, clickable, and functioning normally.

---

### Step 5: Test Uncovered Product Coverage Request Flow

1. On the same store, navigate to an uncovered product (e.g. `https://outfitters.com.pk/products/uncovered-item-99`).
2. **Expected Verification**:
   - Widget displays: `Size chart not available yet`.
   - Displays description: `We are adding size coverage for this brand. Click to request automatic chart matching.`
   - Click **Request Brand Coverage**.
   - Button displays loading state (`Submitting request...`), then transforms into `✓ Requested! We'll notify you.`.
   - Inspect database table `public.coverage_requests` to confirm the URL and domain `outfitters.com.pk` were recorded.
