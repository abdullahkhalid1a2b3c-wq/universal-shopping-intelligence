# FitSense Chrome Web Store Submission & Pilot Installation Guide

This document covers everything required to submit the FitSense Chrome Extension (Manifest V3) to the Google Chrome Web Store, along with instructions for internal and external pilot testers to install the extension unpacked.

---

## 1. Extension Details & Metadata

| Field | Value | Notes |
| :--- | :--- | :--- |
| **Extension Name** | `FitSense — Universal Size & Fit Assistant` | Under 45 characters |
| **Short Description** | `Get your exact size recommendation on Pakistan's top fashion stores.` | Maximum 132 characters |
| **Version** | `0.1.0` | Matches `manifest.json` |
| **Category** | `Shopping` | Primary category |
| **Primary Language** | `English` | Also localized for Urdu (`ur`) and Roman Urdu (`ur-roman`) |
| **Privacy Policy URL** | `https://fitsense.vercel.app/privacy` | Must be publicly accessible HTTPS URL |
| **Support URL / Email** | `support@fitsense.pk` (or contact form URL) | Required for store listing |

---

## 2. Store Listing Long Description

```markdown
FitSense solves the universal sizing problem for Pakistani online fashion shoppers.

A "Medium" or size "38" fits differently across Khaadi, Sapphire, Breakout, Diners, and Outfitters. Every brand uses different garment allowances, forcing shoppers to hesitate, buy multiple sizes, or deal with frustrating post-purchase returns.

FitSense gives you instant, high-confidence size recommendations right on the retailer's product page — without guessing.

KEY FEATURES:
• One Universal Profile: Enter your measurements once (or estimate them from a shirt you already own) and get recommendations across all supported Pakistani stores.
• Real Size Charts: Recommendations are computed by comparing your body profile directly against each brand's genuine garment measurements — no averages, no guessing.
• Floating Sizing Widget: Clean, isolated floating badge showing your recommended size, confidence score, and fit explanation directly on the product page.
• Size Swatch Highlighting: Automatically highlights your recommended size button on the store so you never click the wrong variant.
• Full Language Support: Available in English, Urdu (اردو), and Roman Urdu.
• Guest Mode: Try instant size recommendations with just a chest measurement — no account required.
• Strict Privacy: Your body measurements are NEVER sold or shared with retailers. Zero tracking of browsing outside supported stores.

SUPPORTED PAKISTANI FASHION STORES:
1. Khaadi (khaadi.com)
2. Sapphire (sapphireonline.pk)
3. Breakout (breakout.com.pk)
4. Diners (diners.com.pk)
5. Outfitters (outfitters.com.pk)
(More brands added weekly via community coverage requests!)
```

---

## 3. Required Screenshots & Media Specifications

Prepare and capture the following assets before creating the store draft:

1. **Store Icon**:
   - `128x128` PNG (transparent background).
2. **Promotional Marquee Tiles**:
   - Small promo tile: `440x280` PNG.
   - Large promo tile (optional): `920x680` PNG.
   - Marquee promo tile (optional): `1400x560` PNG.
3. **Store Screenshots (1280x800 or 640x400 PNG)**:
   - **Screenshot 1 — Product Page Recommendation**: Show the floating widget mounted on Khaadi or Sapphire displaying "Recommended Size: M (High confidence)" and the highlighted size swatch.
   - **Screenshot 2 — Fit Explanation Drawer**: Expanded "See why" drawer showing ease allowance breakdown against garment dimensions.
   - **Screenshot 3 — Popup Extension Interface**: The Vue 3 popup showing signed-in status, profile completeness meter, and language switcher.
   - **Screenshot 4 — Urdu Localization (اردو)**: Floating widget and popup rendered in full Right-to-Left (RTL) Nastaliq Urdu typography.
   - **Screenshot 5 — Coverage Request**: An unsupported product page displaying the "Request Brand Coverage" prompt.

---

## 4. Permission Justifications (Mandatory for Review)

Google Chrome Web Store reviewers require an explicit single-purpose justification for every requested permission:

### A. `permissions: ["storage"]`
> **Justification provided to Google**:
> *"The `storage` permission is used solely to store the shopper's preferred measurement units (cm vs inches), active language (English, Urdu, Roman Urdu), local authentication session token, and a 24-hour cache of store selector configurations. No user data stored is ever transmitted to unauthorized third parties."*

### B. `host_permissions: ["*://*.khaadi.com/*", "*://*.sapphireonline.pk/*", "*://*.breakout.com.pk/*", "*://*.diners.com.pk/*", "*://*.outfitters.com.pk/*"]`
> **Justification provided to Google**:
> *"FitSense operates strictly on the 5 specific Pakistani fashion retailer domains supported by the platform. The extension injects an isolated Shadow DOM widget on product pages of these domains to detect the clothing item, query our sizing recommendation API, and highlight the recommended size button. No broad wildcard permissions (`<all_urls>` or `*://*/*`) are requested."*

---

## 5. Review Timeline & Best Practices

- **Google Web Store Review Duration**: Initial submission typically takes **2 to 7 business days** to be reviewed and approved by Google's Trust & Safety team.
- **Single Purpose Policy**: FitSense strictly complies with Chrome's Single Purpose policy: it only calculates and shows clothing size recommendations.
- **Code Quality**: Built files in `dist/` are audited for clean, readable code with zero obfuscated scripts, remote code execution (`eval`), or hardcoded credentials.

---

## 6. Pilot Testing: Unpacked Installation Guide

For pilot brand partners, beta testers, and internal team members before the extension is published on the Chrome Web Store:

### Step 1: Package or Obtain the Build
Run the automated release script:
```bash
pnpm release:extension
```
This produces both the built unpacked directory at `apps/extension/dist/` and the zip bundle at `apps/extension/dist-zip/fitsense-extension.zip`.

### Step 2: Enable Developer Mode in Chrome
1. Open Google Chrome.
2. Navigate to `chrome://extensions/` in the URL address bar.
3. In the top-right corner, toggle the **Developer mode** switch to **ON**.

### Step 3: Load the Extension
1. Click the **Load unpacked** button in the top-left toolbar.
2. In the file picker, browse to `e:\fitapp\apps\extension\dist` (or unzip `fitsense-extension.zip` and select the unzipped directory).
3. Click **Select Folder**.

### Step 4: Verify Installation
1. The **FitSense — Universal Size & Fit Assistant** card will appear in your extensions list.
2. Click the puzzle icon in Chrome's toolbar and pin **FitSense** to your browser bar.
3. Click the FitSense icon: the popup will open allowing you to log in or configure guest measurements.
4. Navigate to any product page on [Khaadi](https://khaadi.com), [Sapphire](https://sapphireonline.pk), [Breakout](https://breakout.com.pk), [Diners](https://diners.com.pk), or [Outfitters](https://outfitters.com.pk).
5. The isolated floating recommendation badge will appear in the bottom corner with your size recommendation.

