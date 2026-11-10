/**
 * FitSense Content Script.
 *
 * Runs on supported retailer domains:
 * - Detects product page without inspecting personal data or crawling listing pages.
 * - Queries background service worker for catalogue coverage and size recommendations.
 * - Mounts isolated Shadow DOM floating widget.
 * - Listens for SPA navigations to update recommendations seamlessly.
 */

import { detectProductPage } from './detector'
import { renderWidget, removeWidget, highlightSizeButton } from './widget'
import { initSpaNavigation } from './navigation'
import { normalizeProductUrl } from '../utils/url'
import type { DomainAdapter } from '../constants/domains'

let activeAdapters: DomainAdapter[] = []

async function sendMessageAsync(type: string, payload: any = {}): Promise<any> {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type, payload }, (response) => {
      resolve(response || {})
    })
  })
}

async function handlePageEvaluation() {
  // 1. Fetch user settings (widget toggle, language, auth/guest)
  const settingsRes = await sendMessageAsync('GET_USER_SETTINGS')
  const settings = settingsRes?.success ? settingsRes : { showWidget: true, language: 'en' }

  if (!settings.showWidget) {
    removeWidget()
    return
  }

  // 2. Fetch adapters if not yet cached
  if (!activeAdapters || activeAdapters.length === 0) {
    const adaptRes = await sendMessageAsync('GET_STORE_ADAPTERS')
    activeAdapters = adaptRes?.adapters || []
  }

  const hostname = window.location.hostname.toLowerCase()
  const matchedAdapter = activeAdapters.find((a) => hostname.includes(a.domain))

  // 3. Detect Product Page (Adapter -> JSON-LD -> Open Graph -> Shopify)
  const detection = detectProductPage(
    document,
    window.location.href,
    matchedAdapter?.selectors
  )

  if (!detection.isProductPage) {
    removeWidget()
    return
  }

  // 4. Canonical URL Normalization
  const canonicalUrl = normalizeProductUrl(window.location.href)
  if (!canonicalUrl) {
    return
  }

  // 5. Look up product in FitSense catalogue
  const lookupRes = await sendMessageAsync('LOOKUP_PRODUCT', { canonicalUrl })
  const lookupData = lookupRes?.data

  if (lookupData?.covered && lookupData?.product) {
    const product = lookupData.product
    const sizeChart = lookupData.size_chart || {}

    // Call Recommendation API
    const recPayload = {
      productUrl: canonicalUrl,
      productId: product.id,
      lang: settings.language || 'en',
      token: settings.session?.access_token || undefined,
      measurements: !settings.session ? settings.guestMeasurements : undefined,
    }

    const recRes = await sendMessageAsync('GET_RECOMMENDATION', recPayload)

    if (recRes?.success && recRes?.data?.recommendation) {
      const rec = recRes.data.recommendation
      const explanation = recRes.data.explanation

      renderWidget({
        covered: true,
        recommendation: {
          recommendedSize: rec.recommended_size,
          confidenceScore: rec.confidence_score,
          confidenceLabel: rec.confidence_label,
          explanation: explanation || 'Recommended based on your fit profile.',
          isDemo: product.is_demo || sizeChart.is_demo,
          isUnverified: !sizeChart.verified_at,
          details: {
            fitPreference: rec.fit_preference,
          },
        },
        productUrl: canonicalUrl,
        domain: hostname,
        language: settings.language,
      })

      // Try highlighting the recommended size button (fails silently if absent)
      highlightSizeButton(rec.recommended_size, matchedAdapter?.selectors?.sizeButtons)
    } else {
      // Inconclusive recommendation fallback
      renderWidget({
        covered: false,
        productUrl: canonicalUrl,
        domain: hostname,
        language: settings.language,
        onRequestCoverage: async () => {
          const res = await sendMessageAsync('SUBMIT_COVERAGE_REQUEST', {
            pageUrl: canonicalUrl,
            domain: hostname,
            token: settings.session?.access_token,
          })
          return res.success
        },
      })
    }
  } else {
    // Uncovered product
    renderWidget({
      covered: false,
      productUrl: canonicalUrl,
      domain: hostname,
      language: settings.language,
      onRequestCoverage: async () => {
        const res = await sendMessageAsync('SUBMIT_COVERAGE_REQUEST', {
          pageUrl: canonicalUrl,
          domain: hostname,
          token: settings.session?.access_token,
        })
        return res.success
      },
    })
  }
}

// Initial evaluation on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    handlePageEvaluation()
  })
} else {
  handlePageEvaluation()
}

// Hook SPA navigation to re-evaluate without full page reloads
initSpaNavigation(() => {
  handlePageEvaluation()
})
