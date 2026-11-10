/**
 * FitSense background service worker (Manifest V3).
 *
 * Responsibilities:
 * 1. Store Adapters: Fetches enabled adapters from Supabase using publishable key and caches in chrome.storage.local for 24 hours.
 * 2. API Proxy: Orchestrates lookup, recommendations, and coverage requests to avoid CORS / host restrictions.
 * 3. Token & Settings Management: Syncs user session and guest measurements securely.
 */

import { SUPPORTED_DOMAINS, type DomainAdapter } from '../constants/domains'

const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL || 'https://zoxobxpjgottuhrezgie.supabase.co').replace(/\/$/, '')
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY || 'sb_publishable_jJPwjDyQmg7s5zZZGxMJcQ_JwzWSVC-'
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

const ADAPTER_CACHE_TTL_MS = 24 * 60 * 60 * 1000 // 24 hours

interface CachedAdapters {
  adapters: DomainAdapter[]
  cachedAt: number
}

/**
 * Fetch enabled store adapters from Supabase REST API or return cached.
 * Gracefully falls back to SUPPORTED_DOMAINS if remote is empty or unavailable.
 */
export async function getStoreAdapters(): Promise<DomainAdapter[]> {
  try {
    const stored = await chrome.storage.local.get(['adapters', 'adaptersCachedAt'])
    const now = Date.now()

    if (
      stored.adapters &&
      stored.adaptersCachedAt &&
      now - stored.adaptersCachedAt < ADAPTER_CACHE_TTL_MS
    ) {
      return stored.adapters
    }

    // Fetch from Supabase REST API
    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/store_adapters?is_enabled=eq.true&select=domain,platform,selectors`,
      {
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          Accept: 'application/json',
        },
      }
    )

    if (response.ok) {
      const rows = await response.json()
      if (Array.isArray(rows) && rows.length > 0) {
        const fetchedAdapters: DomainAdapter[] = rows.map((r: any) => ({
          id: r.domain.replace(/\./g, '-'),
          name: r.domain,
          domain: r.domain,
          matchPattern: `*://*.${r.domain}/*`,
          platform: r.platform || 'custom',
          selectors: r.selectors || {},
        }))

        await chrome.storage.local.set({
          adapters: fetchedAdapters,
          adaptersCachedAt: now,
        })
        return fetchedAdapters
      }
    }

    // Graceful fallback if empty table or error
    await chrome.storage.local.set({
      adapters: SUPPORTED_DOMAINS,
      adaptersCachedAt: now,
    })
    return SUPPORTED_DOMAINS
  } catch {
    // Return built-in list without crashing
    return SUPPORTED_DOMAINS
  }
}

// Service worker install event
chrome.runtime.onInstalled.addListener(() => {
  console.log('[FitSense] Service worker installed')
  getStoreAdapters()
})

// Message dispatcher for content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const { type, payload } = message

  switch (type) {
    case 'GET_STORE_ADAPTERS': {
      getStoreAdapters().then((adapters) => sendResponse({ success: true, adapters }))
      return true
    }

    case 'LOOKUP_PRODUCT': {
      const { canonicalUrl } = payload
      const url = `${API_BASE_URL}/v1/products/lookup?url=${encodeURIComponent(canonicalUrl)}`

      fetch(url)
        .then(async (res) => {
          if (!res.ok) {
            return { covered: false }
          }
          return res.json()
        })
        .then((data) => sendResponse({ success: true, data }))
        .catch((err) => sendResponse({ success: false, error: err.message }))
      return true
    }

    case 'GET_RECOMMENDATION': {
      const { productUrl, productId, measurements, fitPreference, lang, token } = payload
      const url = `${API_BASE_URL}/v1/recommend?lang=${encodeURIComponent(lang || 'en')}`

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          product_url: productUrl,
          product_id: productId,
          measurements: measurements || undefined,
          fit_preference: fitPreference || 'regular',
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            throw new Error(err.detail || `HTTP ${res.status}`)
          }
          return res.json()
        })
        .then((data) => sendResponse({ success: true, data }))
        .catch((err) => sendResponse({ success: false, error: err.message }))
      return true
    }

    case 'SUBMIT_COVERAGE_REQUEST': {
      const { pageUrl, domain, token } = payload
      const url = `${API_BASE_URL}/v1/coverage-requests`

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          page_url: pageUrl,
          domain: domain,
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            throw new Error(err.detail || `HTTP ${res.status}`)
          }
          return res.json()
        })
        .then((data) => sendResponse({ success: true, data }))
        .catch((err) => sendResponse({ success: false, error: err.message }))
      return true
    }

    case 'GET_USER_SETTINGS': {
      chrome.storage.local
        .get(['fitsense_session', 'fitsense_guest_measurements', 'fitsense_language', 'fitsense_show_widget'])
        .then((stored) => {
          sendResponse({
            success: true,
            session: stored.fitsense_session || null,
            guestMeasurements: stored.fitsense_guest_measurements || null,
            language: stored.fitsense_language || 'en',
            showWidget: stored.fitsense_show_widget !== false, // default true
          })
        })
      return true
    }

    default:
      sendResponse({ success: false, error: 'Unknown message type' })
      return false
  }
})
