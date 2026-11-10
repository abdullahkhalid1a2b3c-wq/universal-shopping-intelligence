# FitSense Pre-Launch Verification Checklist

Before opening FitSense to public shoppers or retail brand partners, complete and sign off on each item below.

---

## 1. Size Chart Data Integrity & Real Brand Calibration

- [ ] **Audit Demo Data**:
  - Open `/admin/data-quality` and review the **Demo / Seed Charts** tab.
  - Identify all charts with `is_demo = true`.
- [ ] **Replace with Genuine Brand Specifications**:
  - Obtain real, production size charts from partner brands or verified brand garment tags.
  - Upload via CSV in `/retailer/size-charts` or enter through the sizing table builder.
  - Verify measurement mode: correctly specify `circumference` vs `flat` (half-circumference).
- [ ] **Certify & Verify Charts**:
  - Review sanity check warnings (chest progression, waist bounds, sleeve bounds).
  - Stamp each verified chart with `verified_at = now()` and clear the `is_demo` flag.
  - Confirm the UI removes the "🧪 Demo Data" disclaimer banner on verified products.

---

## 2. Store Adapters Staged Rollout (One Brand at a Time)

Enable and verify store adapters progressively in `/admin/adapters`:

- [ ] **Brand 1: Khaadi (`khaadi.com`)**:
  - Verify product detection on Kurtas, 2-Piece, and 3-Piece unstitched/stitched.
  - Verify size swatch button selector highlighting (`.swatch-option.text`).
  - Toggle `is_enabled = true`.
- [ ] **Brand 2: Sapphire (`sapphireonline.pk`)**:
  - Verify JSON-LD Schema.org product metadata extraction.
  - Verify Shopify variant radio and swatch highlighting.
  - Toggle `is_enabled = true`.
- [ ] **Brand 3: Breakout (`breakout.com.pk`)**:
  - Verify Western wear (tees, jeans, shirts) size recommendation.
  - Toggle `is_enabled = true`.
- [ ] **Brand 4: Diners (`diners.com.pk`)**:
  - Verify formal suiting, dress shirts, and casual kurtas.
  - Toggle `is_enabled = true`.
- [ ] **Brand 5: Outfitters (`outfitters.com.pk`)**:
  - Verify casual street wear tops and denim fit recommendations.
  - Toggle `is_enabled = true`.

---

## 3. Legal, Privacy & Compliance Sign-Off

- [ ] **Legal Counsel Review**:
  - Submit `docs/PRIVACY_CHECKLIST.md` and `apps/web/pages/privacy.vue` to licensed Pakistani legal counsel.
  - Audit alignment with PECA 2016 (Prevention of Electronic Crimes Act) and PDPB (Personal Data Protection Bill draft).
  - Update any formal company registration names or data protection officer (DPO) contact details.
- [ ] **Consent Verification**:
  - Confirm new shoppers cannot save `body_measurements` without checking the mandatory consent toggle during onboarding.
  - Confirm consent withdrawal in `/profile` immediately clears `body_measurements` and historical `body_snapshot` values.
- [ ] **Data Subject Rights**:
  - Test `GET /v1/account/export`: verify full JSON data portability download.
  - Test `DELETE /v1/account`: verify user erasure and anonymization options.
- [ ] **Measurement Leak Audit**:
  - Run `pnpm scan:secrets` to confirm zero credentials in bundles.
  - Confirm server logs never print customer measurement values or authorization tokens.

---

## 4. Urdu Localization & Typography Review

- [ ] **197-Key Translation Verification**:
  - Review `docs/TRANSLATION_REVIEW.md` matrix with a native Urdu editor.
  - Verify culturally appropriate, respectful Pakistani terminology for garment sizing.
- [ ] **RTL Rendering & Font Display**:
  - Switch language to **اردو** in web header and extension popup.
  - Verify Right-to-Left (RTL) layout mirrors correctly without overlapping buttons.
  - Confirm `Noto Naskh Arabic` / `Noto Nastaliq Urdu` font loads with appropriate line height (`1.75`).
- [ ] **Roman Urdu Readability**:
  - Verify **Roman Urdu** (`ur-roman`) strings use familiar colloquial phrasing (e.g. *"Miltay jultay chest size walay 8 buyers ne bataya k M size fit aya"*).

---

## 5. Database Security & Tenant Isolation

- [ ] **RLS Verification**:
  - Execute `supabase/tests/test_rls_isolation.sql` against the database.
  - Verify:
    - User A cannot read or modify User B's profiles or body measurements.
    - Retailer A cannot read or modify Retailer B's size charts or adapters.
    - Anonymous requests cannot read profiles or measurements.
- [ ] **Security Definer & Triggers**:
  - Confirm role escalation triggers protect against unauthorized promotion to `admin` or `verified`.

---

## 6. Infrastructure, Monitoring & Backups

- [ ] **Sentry Error Monitoring**:
  - Configure `SENTRY_DSN` in Render environment variables.
  - Confirm Sentry initialization runs with `send_default_pii = False`.
- [ ] **Custom SMTP Configuration**:
  - Disconnect default Supabase email sender (capped at 30/hr).
  - Connect dedicated SMTP provider (Resend / SendGrid / Amazon SES).
  - Verify email confirmation arrives in inbox without spam flagging.
- [ ] **Database Backups**:
  - Confirm automated daily backups are active in Supabase Project Settings.
- [ ] **Cold Start Strategy**:
  - Keep Render API warm using an external 10-minute ping or upgrade to Render Starter plan ($7/mo).

---

## 7. Pilot User Community & Feedback Loop

- [ ] **Dedicated Pilot Feedback Channel**:
  - Create a private WhatsApp community group or Slack/Discord channel for pilot testers and retail brand managers.
  - Provide direct link: `https://fitsense.vercel.app/feedback/[productId]`.
- [ ] **Review Feedback Anomaly Flags**:
  - Monitor `/retailer/analytics` and `/admin/data-quality` for any charts flagged with `needs_review = true` (>30% reporting too tight or too loose).
  - Review customer notes to fine-tune ease bands or alert brand pattern makers.

