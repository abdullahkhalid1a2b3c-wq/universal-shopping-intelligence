# FitSense Privacy & Data Protection Compliance Checklist
## Applicable Standards: PECA (2016) & Personal Data Protection Bill (PDPB Draft)

> **Important Legal Disclaimer**:
> This document details technical and architectural data protection controls implemented in the FitSense codebase. It is designed to prepare the application for regulatory audit under the Prevention of Electronic Crimes Act (PECA 2016) and the draft Personal Data Protection Bill (PDPB) of Pakistan. **These engineering safeguards do not constitute formal legal certifications or legal advice.** Formal sign-off by qualified legal counsel in Pakistan is required prior to public production launch.

---

## 1. Regulatory Context in Pakistan

| Regulation | Scope & Application | FitSense Technical Control |
| --- | --- | --- |
| **PECA 2016** (Prevention of Electronic Crimes Act) | Unauthorized access to data, critical infrastructure, identity protection, cyberstalking/harassment | Strict RLS on all PostgreSQL tables; JWT signature verification; hashed credentials managed by Supabase Auth; no plain measurement leaks |
| **PDPB (Draft)** (Personal Data Protection Bill) | Collection limitation, purpose specification, user consent, right to access, right to erasure, data portability | Mandatory affirmative consent before saving `body_measurements`; granular consent withdrawal; complete account purge; JSON export |

---

## 2. Personal Data Inventory & Classification

| Data Category | Fields | Classification | Storage Location | Retention / Deletion Policy |
| --- | --- | --- | --- | --- |
| **Identity & Account** | Email, User ID, Profile Display Name, Password Hash | Sensitive Personal Data | `auth.users`, `public.profiles` | Deleted immediately upon `DELETE /v1/account` |
| **Body Measurements** | Chest, Waist, Hips, Inseam, Shoulder, Sleeve, Kameez Length (cm) | Highly Sensitive Personal Data | `public.body_measurements`, `public.reference_garments` | Deleted immediately upon consent withdrawal (`/withdraw-consent`) or account deletion |
| **Fit Preferences** | Preferred fit styles (`fitted`, `regular`, `loose`) by category | Personal Data | `public.fit_preferences` | Deleted upon account deletion |
| **Fit Feedback** | Purchased size, fit result, problem area, was_returned | Pseudonymous Performance Data | `public.fit_feedback` | Dissociated (`user_id = NULL`, `body_snapshot = NULL`) if user opts to keep feedback; otherwise completely deleted |
| **Recommendation Logs** | Recommended size, confidence score, category | Operational Event Data | `public.recommendations` | Purged on account deletion |
| **Saved Items** | Saved product links and size bookmarks | Personal Wishlist | `public.saved_items` | Purged on account deletion |

---

## 3. Data Protection Safeguards Implemented

### A. Strict Consent Enforcement
- **No Measurement Storage Without Consent**: The API checks `consents` table for `store_measurements = true` before writing any `body_measurements` or capturing `body_snapshot` in post-purchase feedback.
- **One-Click Consent Withdrawal**: Customers can toggle off measurement storage in `/profile` at any time. Toggling off invokes `POST /v1/account/withdraw-consent`, which:
  1. Sets `granted = false` in `consents`.
  2. Permanently deletes all rows in `body_measurements` for that user.
  3. Nullifies any historical `body_snapshot` in `fit_feedback`.

### B. Right to Data Portability (PDPB Clause on Access)
- Endpoint: `GET /v1/account/export`
- Provides an immediate JSON download containing all data related to the authenticated user across:
  - `profiles`
  - `consents`
  - `body_measurements`
  - `fit_preferences`
  - `reference_garments`
  - `saved_items`
  - `recommendations`
  - `fit_feedback`

### C. Right to Erasure / Right to be Forgotten
- Endpoint: `DELETE /v1/account`
- Two options provided to the customer:
  1. **Full Purge (`keep_anonymous_feedback=false`)**: Completely removes the user from `auth.users`, `profiles`, and all related personal tables including all feedback entries.
  2. **Anonymized Retain (`keep_anonymous_feedback=true`)**: Purges all profile and measurement records, but preserves aggregate sizing feedback rows with `user_id = NULL` and `body_snapshot = NULL` to prevent data skew while completely breaking linkability to the person.

### D. Zero Measurement Logging & Transmission Safeguards
- **FastAPI Structured Logger**: Request body, headers, and measurement queries are excluded from terminal logs. Only HTTP method, route path, status code, and latency are recorded.
- **Sentry Error Monitoring**: Configured with `send_default_pii = False`. No customer measurements or identifiers are transmitted to external error reporting services.
- **AI Boundary Isolation**: The size recommendation engine is 100% deterministic mathematics (`app/fit/engine.py`). Body measurements are NEVER passed to third-party LLMs (e.g., OpenAI, Anthropic, Gemini).

### E. Peer Feedback K-Anonymity ($k \ge 5$)
- Aggregate peer summaries (e.g. "8 people with a similar chest size said Large fit well") strictly enforce:
  - Minimum cluster size of **5** respondents within $\pm 6\text{ cm}$ chest measurement.
  - Zero output if fewer than 5 matching records exist (`has_summary = false`).
  - Absolute suppression of individual user identities, dates, and exact measurements.

---

## 4. UI Compliance Rule
- **No Unverified Legal Claims**: The UI never claims "100% GDPR Compliant" or "Certified under PECA". A plain, humble notice in `/privacy` explicitly states:
  > *"Note: This privacy policy draft is pending formal legal counsel review."*

