/**
 * Canonical product URL normalization utility for FitSense Chrome Extension.
 *
 * Implements the identical normalization logic as apps/api/app/utils/url.py:
 * 1. Lowercases scheme and hostname
 * 2. Strips tracking and marketing parameters (utm_*, fbclid, gclid, variant, etc.)
 * 3. Strips URL fragments (#)
 * 4. Strips trailing slashes on paths (unless path is '/')
 */

export const TRACKING_PARAMS = new Set([
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
  'fbclid',
  'gclid',
  'ref',
  'source',
  '_pos',
  '_sid',
  '_ss',
  'variant',
])

export function normalizeProductUrl(rawUrl: string): string {
  if (!rawUrl || typeof rawUrl !== 'string') {
    return ''
  }

  const trimmed = rawUrl.trim()
  if (!trimmed) {
    return ''
  }

  try {
    // Handle URLs without scheme
    const urlString = trimmed.includes('://') ? trimmed : `https://${trimmed}`
    const parsed = new URL(urlString)

    const scheme = (parsed.protocol || 'https:').toLowerCase().replace(':', '')
    const hostname = parsed.hostname.toLowerCase()

    // Filter query parameters
    const params = new URLSearchParams()
    // Sort or preserve non-tracking params
    for (const [key, val] of parsed.searchParams.entries()) {
      if (!TRACKING_PARAMS.has(key.toLowerCase())) {
        params.append(key, val)
      }
    }

    // Path normalization: strip trailing slash unless path is '/'
    let pathname = parsed.pathname || '/'
    if (pathname.length > 1 && pathname.endsWith('/')) {
      pathname = pathname.slice(0, -1)
    }

    const queryString = params.toString()
    return `${scheme}://${hostname}${pathname}${queryString ? `?${queryString}` : ''}`
  } catch {
    return ''
  }
}
