# FitSense Production Deployment Guide

A step-by-step, click-by-click operational manual for launching FitSense to production across **Supabase** (Database & Auth), **Render** (FastAPI Backend), and **Vercel** (Nuxt 3 Frontend).

---

## 1. Supabase Production Settings

Before deploying code, configure your live Supabase project.

### 1.1 Where to Find Each Key
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard/projects) and open your project.
2. In the left navigation, click **Project Settings** (gear icon) > **API**.
3. Locate the following values:
   - **Project URL**: `https://<your-project-id>.supabase.co`
     - Needed for: `SUPABASE_URL` (API) and `NUXT_PUBLIC_SUPABASE_URL` (Web).
   - **anon / public key**:
     - Needed for: `SUPABASE_PUBLISHABLE_KEY` (API) and `NUXT_PUBLIC_SUPABASE_KEY` (Web).
   - **service_role key (secret)**:
     - Needed for: `SUPABASE_SERVICE_KEY` (API only on Render). **Never put this in Vercel or frontend bundles.**
4. Scroll down to **JWT Settings**:
   - **JWT Secret**: Click to reveal and copy.
     - Needed for: `SUPABASE_JWT_SECRET` (API only on Render).

---

### 1.2 Authentication URL Configuration
1. In the left sidebar, click **Authentication** > **URL Configuration**.
2. **Site URL**: Enter your production frontend domain (e.g. `https://fitsense.vercel.app`).
3. **Redirect URLs**: Click **Add URL** and add each of the following:
   - `https://fitsense.vercel.app/**`
   - `https://fitsense.vercel.app/profile`
   - `https://fitsense.vercel.app/saved`
   - `http://localhost:3000/**` (for local development)
4. Click **Save**.

---

### 1.3 Email Confirmation Settings & Custom SMTP Provider
1. Go to **Authentication** > **Providers** > **Email**.
2. **Confirm email**: Ensure "Enable Email Confirmations" is turned **ON** for production shoppers.
3. **Custom SMTP Recommendation**:
   > ⚠️ **Critical Warning on Default Supabase Email**:
   > Supabase's built-in email service is capped at **30 emails per hour** for the entire project. In a public launch, confirmation emails will queue up and bounce.
4. Go to **Project Settings** > **Authentication** > **SMTP Settings**.
5. Enable **Custom SMTP** and connect a dedicated transactional email provider:
   - **Recommended Providers**: [Resend](https://resend.com) (recommended: 3,000 free emails/mo), [SendGrid](https://sendgrid.com), or [Amazon SES](https://aws.amazon.com/ses/).
   - Fill in:
     - **Sender Email**: `noreply@yourdomain.com` or `auth@fitsense.pk`
     - **Sender Name**: `FitSense`
     - **Host**: `smtp.resend.com` (or your provider's SMTP host)
     - **Port**: `587` (TLS)
     - **User**: `resend` (or provider username)
     - **Password**: API key from your SMTP provider
6. Click **Save Changes**.

---

### 1.4 Database Backups
1. Go to **Project Settings** > **Database** > **Backups**.
2. Verify that **Scheduled Daily Backups** are active.
3. On Supabase Pro ($25/mo), Point-in-Time Recovery (PITR) can be enabled to restore the database to any individual second in the past 7 days.

---

## 2. Deploying the API on Render

The FastAPI backend runs inside a secure, unprivileged Docker container.

### 2.1 Connect Repository & Create Web Service
1. Log in to [Render](https://render.com).
2. Click **New +** in the top navigation > **Web Service**.
3. Connect your Git repository (`fitapp`).
4. Choose **Deploy with Render Blueprint** (auto-detects `render.yaml`) OR manually configure:
   - **Name**: `fitsense-api`
   - **Environment**: `Docker`
   - **Docker Context**: `apps/api`
   - **Dockerfile Path**: `apps/api/Dockerfile`
   - **Region**: `Oregon (US West)` or nearest to your users
   - **Instance Type**: `Free` (or `Starter` at $7/mo)
   - **Health Check Path**: `/health`

### 2.2 Configure Environment Variables in Render
In the **Environment** tab, add the following variables:

| Environment Variable | Description / Source |
| :--- | :--- |
| `SUPABASE_URL` | Supabase Project URL (`https://<project-id>.supabase.co`) |
| `SUPABASE_SERVICE_KEY` | Supabase secret `service_role` key |
| `SUPABASE_JWT_SECRET` | Supabase JWT Secret |
| `SUPABASE_PUBLISHABLE_KEY`| Supabase `anon` public key |
| `ALLOWED_ORIGINS` | `https://fitsense.vercel.app,http://localhost:3000` |
| `SENTRY_DSN` | *(Optional)* Sentry DSN for crash monitoring |

### 2.3 Verify API Health
Once the deployment finishes (status shows **Live**):
1. Copy your Render service URL: `https://fitsense-api.onrender.com`.
2. Open in your browser or run in terminal:
   ```bash
   curl -i https://fitsense-api.onrender.com/health
   ```
3. You must receive:
   ```json
   HTTP/1.1 200 OK
   {"status":"ok","version":"0.1.0"}
   ```

---

## 3. Deploying the Web App on Vercel

The Nuxt 3 web application deploys as a static and edge-rendered application on Vercel.

### 3.1 Import Project
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** > **Project**.
3. Select your Git repository.

### 3.2 Configure Build & Root Directory
In the project configuration screen:
1. **Framework Preset**: `Nuxt.js`
2. **Root Directory**: Click **Edit** and choose `apps/web`.
3. **Build Command**: `pnpm build` (default)
4. **Output Directory**: `.output/public` (default)

### 3.3 Set Environment Variables
Add the following 3 variables in the Vercel dashboard:

| Variable Name | Value | Purpose |
| :--- | :--- | :--- |
| `NUXT_PUBLIC_SUPABASE_URL` | `https://<project-id>.supabase.co` | Browser client connection to Supabase |
| `NUXT_PUBLIC_SUPABASE_KEY` | `eyJ...` (Supabase **anon** key) | Browser anonymous auth key |
| `NUXT_PUBLIC_API_BASE_URL` | `https://fitsense-api.onrender.com` | Deployed FastAPI backend URL |

> **Security Rule**: Never add `SUPABASE_SERVICE_KEY` or `SUPABASE_JWT_SECRET` to Vercel. Frontend bundles must only access public keys.

4. Click **Deploy**.
5. Once complete, your site will be live at `https://fitsense.vercel.app` (or your custom domain).

---

## 4. Set CORS `ALLOWED_ORIGINS` on the API

To allow browser requests from your new Vercel domain to the Render API:
1. Return to your [Render Dashboard](https://dashboard.render.com).
2. Open your `fitsense-api` service > **Environment**.
3. Update `ALLOWED_ORIGINS` to include your exact Vercel URL:
   ```text
   ALLOWED_ORIGINS=https://fitsense.vercel.app,http://localhost:3000
   ```
4. Click **Save Changes**. Render will automatically redeploy with the updated CORS whitelist in ~30 seconds.

---

## 5. Running the Smoke Test Suite

Verify complete end-to-end production connectivity:

```bash
python scripts/smoke_test.py --api-url https://fitsense-api.onrender.com --web-url https://fitsense.vercel.app
```

The script will verify:
1. `GET /health` returns 200 and `"status": "ok"`.
2. `GET /v1/products/lookup` succeeds against the database.
3. `POST /v1/recommend` computes a guest fit recommendation without auth credentials.
4. Web frontend home page responds with HTTP 200.
5. Preflight `OPTIONS` headers verify that CORS allows `https://fitsense.vercel.app`.

---

## 6. Elevating Your Account to Administrator

Once you sign up through the web app, grant your account the `admin` role via Supabase:

1. In Supabase Dashboard, open **SQL Editor**.
2. Run the following query with your sign-up email:
   ```sql
   UPDATE public.profiles
   SET role = 'admin'
   WHERE email = 'your-email@example.com';
   ```
3. Refresh the web app. The `/admin/retailers` and `/admin/data-quality` links will now be visible and accessible in the top navigation.

---

## 7. Rollback Procedures

If an issue occurs after a release:

### 7.1 Web Frontend Rollback (Instant)
1. Open your project on [Vercel](https://vercel.com).
2. Go to the **Deployments** tab.
3. Locate the previous stable deployment.
4. Click the three dots (`...`) > **Rollback to this Deployment**.
5. Traffic is redirected instantly (< 2 seconds) with zero downtime.

### 7.2 API Backend Rollback
1. Open the `fitsense-api` service on [Render](https://dashboard.render.com).
2. Go to the **Events** or **Deploy History** tab.
3. Find the previous successful build.
4. Click **Rollback** to immediately redeploy that image.

---

## 8. Free-Tier Cold Starts & Production Upgrades

### Render Free Tier Latency
- Render's **Free Web Service** automatically spins down to sleep after **15 minutes of inactivity**.
- When an idle instance receives a new request, it incurs a **cold start latency of 40 to 60 seconds** while the container boots.
- **Production Recommendation**:
  - Upgrade the Render service to the **Starter Plan ($7/month)** to keep the API running 24/7 with zero cold starts.
  - Or configure a free uptime monitor (e.g. [UptimeRobot](https://uptimerobot.com) or [Better Stack](https://betterstack.com)) pinging `https://fitsense-api.onrender.com/health` every 10 minutes to keep the instance warm.

### Total MVP Production Cost Breakdown
- **Supabase**: Free Tier ($0/mo) up to 500MB database, 50,000 monthly active users.
- **Vercel**: Hobby Plan ($0/mo) with generous global edge bandwidth.
- **Render**: Free Plan ($0/mo) or Starter Plan ($7/mo) for persistent uptime.
- **Total Initial Monthly Cost**: **$0 to $7 / month**.

