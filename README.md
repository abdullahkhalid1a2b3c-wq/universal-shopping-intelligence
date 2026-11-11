# FitSense — Universal Shopping Intelligence

**Product-specific size recommendations for Pakistani online fashion.**

FitSense is a universal shopping intelligence platform designed to help shoppers find the right clothing size across different Pakistani fashion brands. It addresses one of the biggest problems in online fashion shopping: sizing inconsistency between retailers.

> A Medium at Khaadi is not necessarily a Medium at Sapphire. FitSense helps shoppers make more confident, product-specific sizing decisions.

---

## Overview

Online fashion retailers use different sizing standards, measurements, and size charts. This makes it difficult for shoppers to identify the correct size when purchasing from multiple brands.

FitSense aims to solve this problem through a unified fit intelligence system that connects product information, brand-specific sizing data, and intelligent size recommendations.

### Core Objectives

- **Universal Fit Intelligence:** Provide product-specific size recommendations instead of relying solely on generic S, M, L, and XL labels.
- **Brand-Aware Sizing:** Account for differences in sizing standards across Pakistani fashion retailers.
- **Shopping Intelligence:** Help shoppers make more informed purchasing decisions.
- **AI-Assisted Recommendations:** Integrate AI services to support intelligent fit-related assistance.
- **Retailer Integration:** Organize product, retailer, size-chart, and brand adapter information through a unified platform.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Nuxt 3, Vue.js |
| Backend | Python, FastAPI |
| Database | Supabase, PostgreSQL |
| Authentication | Supabase Auth |
| AI Integration | Gemini, Mistral, OpenRouter |
| API Communication | REST APIs, HTTPX |
| Browser Extension | Chrome Extension, Manifest V3 |
| Frontend Deployment | Vercel |
| Backend Deployment | Vercel (Python Serverless Functions) |
| Package Management | pnpm |
| Testing | Pytest, frontend and extension test suites |

---

## Project Architecture

FitSense follows a modular monorepo architecture. The frontend, backend, and browser extension are maintained in separate application directories while sharing the same repository.

```text
universal-shopping-intelligence/
│
├── apps/
│   ├── web/                  # Nuxt 3 frontend
│   │   ├── components/
│   │   ├── pages/
│   │   ├── composables/
│   │   └── ...
│   │
│   ├── api/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py       # API entry point
│   │   │   └── fit/
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   │
│   └── extension/            # Chrome browser extension
│
├── supabase/
│   ├── migrations/           # Database migrations
│   └── seed.sql              # Demo and initial data
│
├── docs/                     # Technical documentation
│
├── package.json
├── pnpm-workspace.yaml
└── README.md
```

---

## Getting Started

Follow these instructions to run FitSense locally.

### Prerequisites

Install the following tools before starting:

| Tool | Minimum Version |
|---|---|
| Node.js | 18+ |
| pnpm | 9+ |
| Python | 3.11+ |
| Git | Latest stable version |

### 1. Clone the Repository

```bash
git clone https://github.com/abdullahkhalid1a2b3c-wq/universal-shopping-intelligence.git

cd universal-shopping-intelligence
```

### 2. Install Workspace Dependencies

From the repository root:

```bash
pnpm install
```

### 3. Configure the Frontend

Navigate to the frontend application:

```bash
cd apps/web
```

Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, you can use:

```powershell
Copy-Item .env.example .env
```

Configure the required Supabase and public API environment variables in `.env`.

Start the Nuxt development server:

```bash
pnpm dev
```

Frontend development URL:

**http://localhost:3000**

### 4. Configure the Backend

Open another terminal from the repository root:

```bash
cd apps/api
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create the backend environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the required Supabase and AI provider credentials.

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend API:

**http://localhost:8000**

Interactive API documentation:

**http://localhost:8000/docs**

Health check:

**http://localhost:8000/health**

### 5. Configure the Chrome Extension

From the repository root:

```bash
cd apps/extension
pnpm install
pnpm build
```

To load the extension in Chrome:

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Select **Load unpacked**.
4. Choose the `apps/extension/dist` directory.

---

## Environment Configuration

FitSense uses environment variables to configure database connectivity, authentication, AI providers, and communication between the frontend and backend.

Environment files are maintained separately for each application.

| Application | Configuration |
|---|---|
| Frontend | `apps/web/.env` |
| Backend | `apps/api/.env` |

### Backend Environment Variables

The backend recognizes the following configuration variables:

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase publishable key |
| `SUPABASE_ANON_KEY` | Alternative name for the publishable key |
| `SUPABASE_JWT_SECRET` | JWT verification configuration |
| `GEMINI_MODEL` | Gemini model configuration |
| `MISTRAL_API_KEY` | Mistral API authentication |
| `OPEN_ROUTER_API_KEY` | OpenRouter API authentication |
| `OPENROUTER_API_KEY` | Alternative OpenRouter variable name |
| `SUPABASE_SECRET_KEY` | Optional privileged Supabase operations |
| `SUPABASE_SERVICE_KEY` | Alternative privileged Supabase key |
| `SENTRY_DSN` | Optional error monitoring configuration |

### Frontend Environment Variables

| Variable | Purpose |
|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | Base URL of the FastAPI backend |
| Supabase frontend variables | Configure frontend Supabase connectivity |

Refer to the `.env.example` files in each application for the complete configuration expected by the codebase.

**Security guidelines:**

- Never commit `.env` files containing real credentials.
- Never expose Supabase secret or service-role keys in frontend code.
- Never expose private AI provider API keys through public Nuxt variables.
- Use Vercel Environment Variables for production configuration.
- Keep `.env.example` files limited to placeholder values.

---

## Database Setup

FitSense uses **Supabase (PostgreSQL)** for database management, authentication, and related application services.

To initialize a new database:

1. Open your Supabase project dashboard.
2. Navigate to **SQL Editor**.
3. Execute the migration files in the following order.

| Order | Migration | Description |
|---|---|---|
| 1 | `00001_initial_schema.sql` | Database tables, constraints, and triggers |
| 2 | `00002_rls_and_policies.sql` | Row Level Security and access policies |
| 3 | `00003_analytics_and_storage.sql` | Aggregated views and storage buckets |
| 4 | `00004_size_chart_needs_review_and_feedback_anonymization.sql` | Quality review flags and feedback anonymization |

After completing the migrations, execute:

```text
supabase/seed.sql
```

This loads the initial demo retailers, products, size charts, and adapters.

**Important:** Review the migration files and target Supabase project before executing database operations. Do not run production migrations blindly.

---

## Deployment

FitSense uses Vercel for production deployment.

The frontend and backend are maintained as separate Vercel projects.

### Frontend Deployment

| Setting | Value |
|---|---|
| Framework | Nuxt.js |
| Root Directory | `apps/web` |
| Build Command | `pnpm build` |
| Install Command | `pnpm install` |
| Output Directory | Managed by Nuxt |

Production website:

**https://universal-shopping-intelligence.vercel.app**

### Backend Deployment

| Setting | Value |
|---|---|
| Framework | FastAPI |
| Root Directory | `apps/api` |
| Runtime | Python |
| Application Entry Point | `app.main:app` |

Backend API:

**https://universal-shopping-intelligence-q29.vercel.app**

API documentation:

**https://universal-shopping-intelligence-q29.vercel.app/docs**

Health endpoint:

**https://universal-shopping-intelligence-q29.vercel.app/health**

### Automatic Deployment Workflow

Both Vercel projects are connected to the GitHub repository.

For the frontend, pushing changes to the connected production branch triggers a new deployment automatically.

```text
Local Development
       |
       v
Git Commit
       |
       v
GitHub Repository
       |
       v
Vercel Build
       |
       v
Production Deployment
       |
       v
Live FitSense Website
```

The backend is a separate deployment and must also receive a deployment when backend code changes.

For additional deployment instructions, refer to `docs/DEPLOYMENT.md`.

---

## Available Root Scripts

Run these commands from the repository root.

| Command | Description |
|---|---|
| `pnpm dev:web` | Start the Nuxt frontend |
| `pnpm dev:api` | Start the FastAPI backend |
| `pnpm build:extension` | Build the Chrome extension |
| `pnpm test:api` | Run backend tests |
| `pnpm test:web` | Run frontend unit tests |
| `pnpm test:extension` | Run extension tests |
| `pnpm release:extension` | Validate extension permissions, scan secrets, and generate a production ZIP |
| `pnpm scan:secrets` | Scan built bundles for credential leaks |
| `pnpm smoke:test` | Run production deployment smoke tests |

---

## Testing

FitSense includes testing workflows for its individual applications.

### Backend Tests

From `apps/api`, with the virtual environment activated:

```bash
python -m pytest
```

Alternatively, from the repository root:

```bash
pnpm test:api
```

### Frontend Tests

```bash
pnpm test:web
```

### Extension Tests

```bash
pnpm test:extension
```

### Production Smoke Test

```bash
pnpm smoke:test
```

Run the relevant tests after making changes, particularly before pushing production updates.

---

## Documentation

Additional technical and project documentation is available in the `docs/` directory.

| Document | Description |
|---|---|
| [Deployment Guide](docs/DEPLOYMENT.md) | Supabase and Vercel deployment instructions |
| [Launch Checklist](docs/LAUNCH_CHECKLIST.md) | Pre-launch checks for brand adapters, size charts, and monitoring |
| [Chrome Store Guide](docs/CHROME_STORE.md) | Chrome Web Store listing, assets, and permissions |
| [Privacy Checklist](docs/PRIVACY_CHECKLIST.md) | PECA / PDPB alignment and data rights |
| [Translation Matrix](docs/TRANSLATION_REVIEW.md) | English, Urdu, and Roman Urdu translation review |
| [Database Architecture](docs/DATABASE.md) | Supabase schema, RLS policies, views, and indexes |

---

## Contributing

Contributions and improvements are welcome.

A recommended development workflow:

1. Create a separate branch for your changes.
2. Make changes within the relevant application directory.
3. Run the appropriate tests.
4. Review environment files and ensure no credentials are included.
5. Commit and push your changes.
6. Open a pull request for review.

---

## Security

If you discover a security vulnerability, avoid publishing sensitive details, API keys, or exploitable information in public issues.

Never commit private credentials, access tokens, or production secrets to the repository.

---

## Project

**FitSense — Universal Shopping Intelligence Platform**

Built to make online fashion shopping more reliable through product-specific fit intelligence.

**Repository:** [GitHub — Universal Shopping Intelligence](https://github.com/abdullahkhalid1a2b3c-wq/universal-shopping-intelligence)

**Frontend:** [Live FitSense Website](https://universal-shopping-intelligence.vercel.app)

**Backend:** [FastAPI Documentation](https://universal-shopping-intelligence-q29.vercel.app/docs)
