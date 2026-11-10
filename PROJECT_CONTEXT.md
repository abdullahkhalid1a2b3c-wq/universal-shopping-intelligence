=== PRODUCT ===
FitSense is a Universal Shopping Intelligence Platform. First product: Universal Fit Intelligence for Pakistani online fashion.
A customer creates one reusable body and preference profile. The platform compares it with each product's REAL size chart and returns a product-specific size recommendation with an explanation and a confidence level. Retailers use the same data through a dashboard (and later a widget) to reduce sizing-related returns.
Problem: Medium at Khaadi, Sapphire, Breakout, Diners and Outfitters fits differently, so shoppers buy several sizes, hesitate, or abandon the cart.
We are NOT building a marketplace, checkout, price-comparison site, virtual try-on app or generic size calculator. Customers are redirected to the retailer to buy.
Customers use it free. Retailers pay (B2B SaaS), but billing is out of scope for the MVP.

=== MVP SCOPE (build only this) ===
Customer: account, measurement profile, fit preference per category, product-specific size recommendation with explanation, saved products and sizes, post-purchase fit feedback.
Retailer/admin: retailer and brand management, product catalogue, size-chart upload (CSV), garment measurement setup, fit configuration, basic analytics.
Browser extension (Chrome, Manifest V3): detect supported product pages, find the product in our database, show the recommended size, highlight that size on the page, link back to the retailer.
Explicitly OUT of scope: virtual try-on, checkout, payments, photo-based measurement, machine learning, price tracking, AI chat assistant.
Categories: t-shirts and tops, shirts, trousers, jeans, kurtas, basic dresses.

=== STACK ===
Monorepo: apps/web (Nuxt 3 + TypeScript + Tailwind + Pinia + @nuxtjs/supabase + @nuxtjs/i18n), apps/api (Python 3.11+, FastAPI, Pydantic v2, pytest), apps/extension (Vue 3 + TypeScript + Vite, Manifest V3), supabase/ (SQL migrations and seed).
Backend services: Supabase (PostgreSQL, Auth, Storage). The FastAPI API verifies the Supabase JWT and reads data with the service key.
Hosting plan: web on Vercel, API on Render, database on Supabase.

=== DATA RULES (critical) ===
1. Keep THREE things separate and never mix them: body measurements (the customer), garment measurements (the product's real size chart values), and retailer size labels (S, M, L, 32, etc.). Labels are not interchangeable between brands.
2. Store every measurement in centimetres. Convert to inches only in the UI.
3. Every size chart records whether values are 'flat' (laid flat, half circumference) or 'circumference'. The engine converts flat values to full circumference.
4. The engine must show uncertainty. If data is missing, lower the confidence and say why. Never invent data.
5. Demo or seed data must be flagged is_demo = true and shown with a 'Demo data' label in the UI. Never present invented size charts as real brand data.
6. Body data is personal data: collect the minimum, require explicit consent before saving measurements, encrypt in transit, support export and full deletion, never log measurements.

=== ENGINEERING RULES ===
- TypeScript strict mode. Python type hints everywhere. Small files, clear names, no dead code.
- All secrets come from environment variables. Create .env.example files with placeholder values for each app. Never commit real keys.
- Mobile-first UI, accessible (labels, contrast, keyboard use), English plus Urdu (right-to-left) plus Roman Urdu.
- Every feature gets tests where logic exists (the fit engine must have thorough unit tests).
- Supabase Row Level Security is ON for every table. Users can only access their own data.
- After each task: run tests and the dev servers, fix errors, then give me (1) what you built, (2) how to run and check it, (3) anything I must do by hand (keys, dashboard settings).
- Ask me before doing anything destructive or any action that needs my secret keys.
- If a requirement here is unclear or conflicts with another, ask before building.

