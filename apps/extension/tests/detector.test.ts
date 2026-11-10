import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Window } from 'happy-dom'
import { detectProductPage } from '../src/content/detector.ts'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const fixturesDir = path.join(__dirname, 'fixtures')

function createDocFromFixture(filename: string): Document {
  const html = fs.readFileSync(path.join(fixturesDir, filename), 'utf-8')
  const window = new Window()
  window.document.write(html)
  return window.document as unknown as Document
}

describe('Product Page Detection', () => {
  it('detects product via JSON-LD schema.org Product (Sapphire fixture)', () => {
    const doc = createDocFromFixture('jsonld_product.html')
    const result = detectProductPage(doc, 'https://sapphireonline.pk/products/lawn-suit')

    assert.equal(result.isProductPage, true)
    assert.equal(result.detectionMethod, 'jsonld')
    assert.equal(result.title, '2 Piece Embroidered Lawn Suit')
    assert.equal(result.externalId, 'SAP-LAWN-2026-01')
  })

  it('detects product via Open Graph tags (Breakout fixture)', () => {
    const doc = createDocFromFixture('opengraph_product.html')
    const result = detectProductPage(doc, 'https://breakout.com.pk/products/men-slim-fit-shirt')

    assert.equal(result.isProductPage, true)
    assert.equal(result.detectionMethod, 'opengraph')
    assert.equal(result.title, 'Men Slim Fit Cotton Casual Shirt')
  })

  it('detects product via Shopify form structure and URL handle (Outfitters fixture)', () => {
    const doc = createDocFromFixture('shopify_product.html')
    const result = detectProductPage(doc, 'https://outfitters.com.pk/products/graphic-tee')

    assert.equal(result.isProductPage, true)
    assert.equal(result.detectionMethod, 'shopify')
    assert.equal(result.handle, 'graphic-tee')
    assert.equal(result.title, 'Classic Relaxed Graphic Tee')
  })

  it('detects product via adapter selectors when specified', () => {
    const doc = createDocFromFixture('shopify_product.html')
    const result = detectProductPage(doc, 'https://custom-brand.pk/items/123', {
      productContainer: '.product-form-container',
      sizeButtons: '.size-swatch-list input',
    })

    assert.equal(result.isProductPage, true)
    assert.equal(result.detectionMethod, 'adapter')
    assert.equal(result.title, 'Classic Relaxed Graphic Tee')
  })

  it('rejects listing / category page (Listing fixture)', () => {
    const doc = createDocFromFixture('listing_page.html')
    const result = detectProductPage(doc, 'https://sapphireonline.pk/collections/women')

    assert.equal(result.isProductPage, false)
  })
})
