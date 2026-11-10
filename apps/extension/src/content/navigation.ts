/**
 * Single-Page-App (SPA) navigation listener for FitSense Chrome Extension.
 *
 * Intercepts:
 * - window.history.pushState
 * - window.history.replaceState
 * - window.addEventListener('popstate')
 * - DOM mutations with debounced URL change detection
 */

export function initSpaNavigation(onChange: (newUrl: string) => void): () => void {
  let lastUrl = window.location.href

  function checkUrlChange() {
    const current = window.location.href
    if (current !== lastUrl) {
      lastUrl = current
      onChange(current)
    }
  }

  // 1. Hook history API
  const originalPush = window.history.pushState
  const originalReplace = window.history.replaceState

  window.history.pushState = function (...args) {
    const result = originalPush.apply(this, args)
    checkUrlChange()
    return result
  }

  window.history.replaceState = function (...args) {
    const result = originalReplace.apply(this, args)
    checkUrlChange()
    return result
  }

  // 2. Listen to popstate
  const onPopState = () => {
    checkUrlChange()
  }
  window.addEventListener('popstate', onPopState)

  // 3. MutationObserver fallback with debouncing (300ms)
  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  const observer = new MutationObserver(() => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      checkUrlChange()
    }, 300)
  })

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true })
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      observer.observe(document.body, { childList: true, subtree: true })
    })
  }

  // Return unregister/cleanup function
  return () => {
    window.history.pushState = originalPush
    window.history.replaceState = originalReplace
    window.removeEventListener('popstate', onPopState)
    observer.disconnect()
    if (debounceTimer) clearTimeout(debounceTimer)
  }
}
