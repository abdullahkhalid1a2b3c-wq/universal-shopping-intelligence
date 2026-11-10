# FitSense Vercel Deployment Workflow

This document details the branch lifecycle, deployment pipelines, rollback procedures, and token management for deploying the FitSense Web app (`apps/web`) on Vercel.

---

## 1. Project Configuration & Scope

- **Vercel Project Name**: `universal-shopping-intelligence`
- **Team Scope**: `any-5391`
- **Root Directory**: `apps/web`
- **Framework Preset**: `Nuxt.js` (Nuxt 3)
- **Node.js Version**: `20.x` or `22.x`
- **Package Manager**: `pnpm` (Workspace-aware)

---

## 2. Git Branch Lifecycle & Deployments

FitSense follows Git-driven continuous delivery:

### Production Deployments (`main` Branch)
- Pushes and merged pull requests to the `main` branch trigger **Production Deployments**.
- Production deployments update the canonical production domain (e.g. `https://universal-shopping-intelligence.vercel.app`).
- Production deployments use production environment variables.

### Preview Deployments (All Feature Branches & PRs)
- Pushing to any non-main branch (e.g., `feature/profile-redesign`, `fix/sizing-math`) automatically triggers a **Preview Deployment**.
- Vercel generates an isolated, immutable preview URL (e.g. `https://universal-shopping-intelligence-git-feature-branch-any-5391.vercel.app`).
- Preview environments run against Preview environment variables, allowing safe testing without affecting production shoppers.

---

## 3. Environment Variables Configuration

Set these variables in the Vercel Dashboard under **Project Settings > Environment Variables** (or via Vercel CLI):

| Variable Name | Environment | Description |
| :--- | :--- | :--- |
| `NUXT_PUBLIC_SUPABASE_URL` | Production & Preview | Supabase project URL (`https://<project-id>.supabase.co`) |
| `NUXT_PUBLIC_SUPABASE_KEY` | Production & Preview | Supabase `anon` / public key (safe for browser bundles) |
| `NUXT_PUBLIC_API_BASE_URL` | Production | Deployed FastAPI backend URL (e.g. `https://fitsense-api.onrender.com`) |
| `NUXT_PUBLIC_API_BASE_URL` | Preview | Deployed staging API URL or Render service |
| `NUXT_PUBLIC_FEEDBACK_URL` | Production & Preview | *(Optional)* Link for user feedback in the top Beta banner |

> ⚠️ **Strict Security Rule**: Never add `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET`, or `DATABASE_URL` to Vercel. The web bundle must only access public keys prefixed with `NUXT_PUBLIC_`.

---

## 4. Rollback Procedure (Instant Rollback)

If a production deployment encounters an unexpected runtime issue, roll back in seconds without rebuilding:

1. Go to your [Vercel Dashboard](https://vercel.com/any-5391/universal-shopping-intelligence).
2. Click the **Deployments** tab.
3. Locate the previous healthy deployment that you wish to restore.
4. Click the three dots menu (`...`) on the right of that deployment.
5. Select **Promote to Production** (or **Instant Rollback**).
6. Confirm the action. Vercel immediately switches 100% of incoming production traffic to the selected deployment instantaneously without rebuilding.

---

## 5. Security & Token Hygiene

- **Deployment Token**: Vercel deployment tokens (`VERCEL_TOKEN`) granted for automation or CI/CD must be kept out of version control and stored only in uncommitted local files (e.g., `.env.vercel` in `.gitignore`).
- **Token Revocation**:
  When deployment and verification are complete, revoke or rotate the deployment token:
  1. Open [Vercel Account Tokens](https://vercel.com/account/tokens).
  2. Locate the deployment token used for this session.
  3. Click **Delete** / **Revoke**.

