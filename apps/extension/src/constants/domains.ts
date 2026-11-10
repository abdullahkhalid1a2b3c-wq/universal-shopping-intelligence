/**
 * Supported retailer domains and default adapter configurations.
 * Centralized list for Manifest V3 host permissions, content scripts, and fallback selectors.
 */

export interface DomainAdapter {
  id: string
  name: string
  domain: string
  matchPattern: string
  platform: 'shopify' | 'woocommerce' | 'custom'
  selectors: {
    productContainer?: string
    sizeButtons?: string
    addToCartButton?: string
  }
}

export const SUPPORTED_DOMAINS: DomainAdapter[] = [
  {
    id: 'khaadi',
    name: 'Khaadi',
    domain: 'khaadi.com',
    matchPattern: '*://*.khaadi.com/*',
    platform: 'custom',
    selectors: {
      productContainer: '.product-info-main, .product-view',
      sizeButtons: '.swatch-option.text, [data-option-type="size"]',
      addToCartButton: '#product-addtocart-button, button.tocart',
    },
  },
  {
    id: 'sapphire',
    name: 'Sapphire',
    domain: 'sapphireonline.pk',
    matchPattern: '*://*.sapphireonline.pk/*',
    platform: 'shopify',
    selectors: {
      productContainer: '.product-form, .product-single__meta',
      sizeButtons: '.size-swatch-list button, .variant-input input[type="radio"] + label, [data-option-name*="Size"] button',
      addToCartButton: 'button[name="add"], .product-form__submit',
    },
  },
  {
    id: 'breakout',
    name: 'Breakout',
    domain: 'breakout.com.pk',
    matchPattern: '*://*.breakout.com.pk/*',
    platform: 'shopify',
    selectors: {
      productContainer: '.product-form, .product__info-container',
      sizeButtons: '.variant-input input[type="radio"] + label, .size-swatch button',
      addToCartButton: 'button[name="add"], .add-to-cart',
    },
  },
  {
    id: 'diners',
    name: 'Diners',
    domain: 'diners.com.pk',
    matchPattern: '*://*.diners.com.pk/*',
    platform: 'shopify',
    selectors: {
      productContainer: '.product-single, .product-form',
      sizeButtons: '.swatch-element input[type="radio"] + label, .size-box',
      addToCartButton: '#AddToCart, button[name="add"]',
    },
  },
  {
    id: 'outfitters',
    name: 'Outfitters',
    domain: 'outfitters.com.pk',
    matchPattern: '*://*.outfitters.com.pk/*',
    platform: 'shopify',
    selectors: {
      productContainer: '.product-form, .product__info-container',
      sizeButtons: '.size-swatch button, input[name="Size"] + label, .variant-input label',
      addToCartButton: 'button[name="add"], .product-form__submit',
    },
  },
]

export const SUPPORTED_HOST_PATTERNS = SUPPORTED_DOMAINS.map((d) => d.matchPattern)
