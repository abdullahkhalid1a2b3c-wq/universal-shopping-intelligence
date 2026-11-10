# FitSense Chrome Extension (Manifest V3)

FitSense is a privacy-first browser extension providing accurate, brand-specific size recommendations across Pakistan's leading fashion e-commerce retailers (Khaadi, Sapphire, Breakout, Diners, Outfitters).

---

## 1. Extension Permissions & Rationale

Per Chrome Web Store policies, FitSense requests the minimum necessary permissions to function:

| Permission | Scope | Technical Justification |
| :--- | :--- | :--- |
| `storage` | Browser-local storage | Caches active user authentication tokens, language selection (`en`, `ur`, `ur-roman`), widget visibility preference, guest body measurements (`chest`, `waist`, `hip`), and enabled store adapters for 24 hours. Data stored here never leaves the local browser unless explicitly submitted with consent. |
| `host_permissions` | 5 specific brand domains:<br>• `*://*.khaadi.com/*`<br>• `*://*.sapphireonline.pk/*`<br>• `*://*.breakout.com.pk/*`<br>• `*://*.diners.com.pk/*`<br>• `*://*.outfitters.com.pk/*` | Content script execution is strictly restricted to verified supported fashion retailer domains. It detects the active product page, renders an isolated Shadow DOM size badge, and highlights the corresponding size selector button. FitSense **cannot** run on or read any other domain. |

---

## 2. Privacy Policy & Data Disclosure (Chrome Web Store Listing)

### Single Purpose
FitSense provides garment size recommendations on supported fashion store product pages by comparing user body measurements with verified retailer size charts.

### What Data We Collect & Transmit
When viewing a supported product page, FitSense transmits only:
1. **The Product Page URL**: Normalized to canonical form (tracking tags and personal identifiers stripped) to look up garment size charts.
2. **Body Measurements Required for Fit Analysis**:
   - *Signed-in users*: Securely loaded from your encrypted FitSense account profile using your Supabase authentication token.
   - *Guest users*: Transient measurements (chest, waist, hip) entered in the popup are stored **strictly in local browser storage** and transmitted anonymously to the sizing API only when requesting a recommendation.
3. **Language Preference**: To return fit explanations in English, Urdu (RTL), or Roman Urdu.

### What We NEVER Collect, Inspect, or Store
- **No Browsing History**: FitSense does not track which sites you visit outside of detecting supported product URLs on the 5 explicitly whitelisted retailer domains.
- **No Cart or Checkout Inspection**: FitSense never reads shopping carts, checkout forms, credit card numbers, billing addresses, or payment details.
- **No Form Interception**: FitSense never accesses input fields on retailer websites.
- **No Personal Identity Scraping**: Customer names, emails, addresses, and phone numbers on retailer stores are never touched.
- **No AI Influence on Sizing**: Fit recommendations are calculated solely by deterministic, mathematical garment-to-body comparison algorithms. AI is never permitted to adjust recommended size labels.

---

## 3. Architecture & Security

- **Shadow DOM Isolation**: The recommendation widget is injected inside an open Shadow DOM root (`#fitsense-widget-root`). Retailer website styles cannot alter the widget, and widget styles cannot leak into the retailer's checkout or product layout.
- **Non-Intrusive Button Highlighting**: Recommended size buttons are subtly outlined using CSS borders. Add-to-cart buttons are never modified, blocked, or intercepted.
- **SPA Navigation Observer**: Intercepts `history.pushState`, `history.replaceState`, and `popstate` alongside a debounced `MutationObserver` to seamlessly refresh recommendations as shoppers browse Single-Page Applications (Next.js, Nuxt, Shopify headless).
- **Automated Secret Scanning**: Every production build executes `scripts/scan-secrets.js` across `dist/` before packaging. Builds automatically fail if private keys, service role credentials, or database connection strings are present.

---

## 4. Development & Build Commands

```bash
# Run unit tests (URL normalization, detection fixtures, Shadow DOM widget, Auth flow)
pnpm run test

# Build production bundle with automated secret scanning
pnpm run build

# Package extension into zip archive for Chrome Web Store
pnpm run zip

# Development build with live file watcher
pnpm run dev
```

---

## 5. Loading Unpacked Extension in Chrome

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle on **Developer mode** in the top-right corner.
3. Click **Load unpacked** in the top-left toolbar.
4. Select the directory: `e:\fitapp\apps\extension\dist`.
5. The **FitSense — Universal Size & Fit Assistant** extension is now active.
