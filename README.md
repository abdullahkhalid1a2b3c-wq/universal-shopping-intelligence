# FitSense

**Universal Shopping Intelligence Platform** — Universal Fit Intelligence for Pakistani online fashion.

> Medium at Khaadi ≠ Medium at Sapphire. FitSense gives every shopper a product-specific size recommendation they can trust.

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| pnpm | 9+ |
| Python | 3.11+ |

## Quick Start

### 1. Web App (Nuxt 3)

```bash
cd apps/web
cp .env.example .env   # fill in Supabase keys
pnpm install
pnpm dev
```

Runs at **http://localhost:3000**

### 2. API (FastAPI)

```bash
cd apps/api
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in Supabase keys
uvicorn app.main:app --reload --port 8000
```

Runs at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

### 3. Browser Extension (Chrome, Manifest V3)

```bash
cd apps/extension
pnpm install
pnpm build
```

Then load `apps/extension/dist` as an **unpacked extension** in `chrome://extensions` (enable Developer mode).

### 4. Run Tests

```bash
# API tests (from apps/api with venv active)
python -m pytest

# Or from repo root
pnpm test:api
```

## Root Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev:web` | Start the Nuxt dev server |
| `pnpm dev:api` | Start the FastAPI dev server |
| `pnpm build:extension` | Build the browser extension |
| `pnpm test:api` | Run all FastAPI backend tests with pytest |
| `pnpm test:web` | Run web frontend unit tests |
| `pnpm test:extension` | Run browser extension tests |
| `pnpm release:extension` | Verify manifest permissions, scan secrets, and produce production zip |
| `pnpm scan:secrets` | Audit built bundles for credential leaks |
| `pnpm smoke:test` | Run production deployment smoke test |

## Documentation Reference

- **[Deployment Guide](docs/DEPLOYMENT.md)**: Click-by-click manual for Supabase, Render, and Vercel.
- **[Launch Checklist](docs/LAUNCH_CHECKLIST.md)**: Pre-launch sign-off for brand adapters, size charts, and monitoring.
- **[Chrome Store Guide](docs/CHROME_STORE.md)**: Store listing assets, permissions justifications, and pilot install.
- **[Privacy & Regulatory Compliance](docs/PRIVACY_CHECKLIST.md)**: PECA / PDPB alignment and data rights.
- **[Translation Matrix](docs/TRANSLATION_REVIEW.md)**: English, Urdu (اردو), and Roman Urdu 197-key matrix.
- **[Database Architecture](docs/DATABASE.md)**: Supabase schema, RLS policies, views, and indexes.

## Database Setup (Supabase)

In your Supabase project dashboard SQL Editor, execute the following files in order:
1. `supabase/migrations/00001_initial_schema.sql` (Tables, constraints, triggers)
2. `supabase/migrations/00002_rls_and_policies.sql` (Row Level Security & policies)
3. `supabase/migrations/00003_analytics_and_storage.sql` (Aggregated views & storage buckets)
4. `supabase/migrations/00004_size_chart_needs_review_and_feedback_anonymization.sql` (Quality review flag & anonymization)
5. `supabase/seed.sql` (Demo retailers, products, charts & adapters)

## Environment Variables

See `.env.example` in each app directory. **Never commit real keys.**

