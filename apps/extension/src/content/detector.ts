/**
 * Product page detection module for FitSense Chrome Extension.
 *
 * Strict Privacy & Scope Constraints:
 * - Reads only the page the user is currently viewing.
 * - Never crawls listing pages, category pages, or external links.
 * - Never inspects or accesses cart data, checkout forms, login fields, or personal user data.
 *
 * Detection Order:
 * 1. Adapter selectors (if defined for the active domain)
 * 2. JSON-LD schema.org Product definition
 * 3. Open Graph product tags (og:type=product)
 * 4. Shopify product structure / endpoint indicators
 */

export interface DetectedProduct {
  isProductPage: boolean
  title?: string
  externalId?: string
  detectionMethod?: 'adapter' | 'jsonld' | 'opengraph' | 'shopify'
  handle?: string
}

export function detectProductPage(
  doc: Document = document,
  currentUrl: string = window.location.href,
  adapterSelectors?: { productContainer?: string; sizeButtons?: string }
): DetectedProduct {
  // 1. Adapter Selectors
  if (adapterSelectors?.productContainer) {
    try {
      const container = doc.querySelector(adapterSelectors.productContainer)
      if (container) {
        const titleEl = container.querySelector('h1, .product-title, .product__title') || doc.querySelector('h1')
        const title = titleEl ? titleEl.textContent?.trim() : undefined
        return {
          isProductPage: true,
          title,
          detectionMethod: 'adapter',
        }
      }
    } catch {
      // Invalid selector syntax, proceed to next step
    }
  }

  // 2. JSON-LD schema.org Product
  try {
    const jsonLdScripts = doc.querySelectorAll('script[type="application/ld+json"]')
    for (const script of Array.from(jsonLdScripts)) {
      const text = script.textContent?.trim()
      if (!text) continue

      let parsed: any
      try {
        parsed = JSON.parse(text)
      } catch {
        continue
      }

      // Handle direct Product or @graph array
      const items = Array.isArray(parsed)
        ? parsed
        : parsed?.['@graph'] && Array.isArray(parsed['@graph'])
          ? parsed['@graph']
          : [parsed]

      for (const item of items) {
        const type = item?.['@type']
        const isProduct =
          type === 'Product' ||
          (Array.isArray(type) && type.includes('Product'))

        if (isProduct) {
          const title = item.name || item.title || doc.querySelector('h1')?.textContent?.trim()
          const externalId = item.sku || item.productID || item.mpn || undefined
          return {
            isProductPage: true,
            title,
            externalId,
            detectionMethod: 'jsonld',
          }
        }
      }
    }
  } catch {
    // Proceed to next step
  }

  // 3. Open Graph Product Tags
  try {
    const ogTypeMeta = doc.querySelector('meta[property="og:type"], meta[name="og:type"]')
    const ogType = ogTypeMeta?.getAttribute('content')?.toLowerCase()

    if (ogType === 'product' || ogType === 'og:product') {
      const ogTitleMeta = doc.querySelector('meta[property="og:title"], meta[name="og:title"]')
      const title = ogTitleMeta?.getAttribute('content')?.trim() || doc.querySelector('h1')?.textContent?.trim()
      return {
        isProductPage: true,
        title,
        detectionMethod: 'opengraph',
      }
    }
  } catch {
    // Proceed to next step
  }

  // 4. Shopify Product URL & DOM structure
  try {
    const pathname = new URL(currentUrl, 'https://dummy.local').pathname
    const productMatch = pathname.match(/\/products\/([a-zA-Z0-9-_]+)/)
    if (productMatch && productMatch[1]) {
      const handle = productMatch[1]
      // Check for Shopify product form or variant input
      const hasShopifyForm = !!doc.querySelector('form[action*="/cart/add"], [data-product-handle], .product-form')
      const title = doc.querySelector('h1')?.textContent?.trim()

      if (hasShopifyForm || pathname.includes('/products/')) {
        return {
          isProductPage: true,
          title,
          handle,
          detectionMethod: 'shopify',
        }
      }
    }
  } catch {
    // Return non-product
  }

  return {
    isProductPage: false,
  }
}
