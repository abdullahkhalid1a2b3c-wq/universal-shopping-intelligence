/**
 * Utility to normalize e-commerce product URLs to a canonical form.
 * Matches logic in apps/api/app/utils/url.py.
 */
export const normalizeProductUrl = (rawUrl: string): string => {
  if (!rawUrl) return ''
  try {
    const url = new URL(rawUrl.trim())
    // 1. Lowercase hostname and remove www.
    let host = url.hostname.toLowerCase()
    if (host.startsWith('www.')) {
      host = host.slice(4)
    }

    // 2. Clean pathname, remove trailing slash
    let pathname = url.pathname
    if (pathname.length > 1 && pathname.endsWith('/')) {
      pathname = pathname.slice(0, -1)
    }

    // 3. Keep essential params, drop UTM, tracking, and session params
    const dropPrefixes = ['utm_', 'fbclid', 'gclid', 'ref', '_ga', 'mc_']
    const cleanParams = new URLSearchParams()

    url.searchParams.forEach((val, key) => {
      const lower = key.toLowerCase()
      const shouldDrop = dropPrefixes.some((p) => lower.startsWith(p))
      if (!shouldDrop) {
        cleanParams.append(key, val)
      }
    })

    const queryString = cleanParams.toString() ? `?${cleanParams.toString()}` : ''
    return `${url.protocol}//${host}${pathname}${queryString}`
  } catch {
    return rawUrl.trim()
  }
}
