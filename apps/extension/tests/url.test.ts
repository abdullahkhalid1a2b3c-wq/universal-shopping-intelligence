import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { normalizeProductUrl } from '../src/utils/url.ts'

const TEST_CASES: [string, string][] = [
  [
    'https://outfitters.com.pk/products/classic-tee/?utm_source=facebook&utm_medium=cpc&variant=12345#reviews',
    'https://outfitters.com.pk/products/classic-tee',
  ],
  [
    'HTTP://KHAADI.COM/products/kurta-01/?fbclid=XYZ&color=blue',
    'http://khaadi.com/products/kurta-01?color=blue',
  ],
  [
    'https://sapphireonline.pk/products/shirt/',
    'https://sapphireonline.pk/products/shirt',
  ],
  [
    'https://breakout.com.pk/?ref=home',
    'https://breakout.com.pk/',
  ],
  [
    'https://diners.com.pk/products/suit-99?gclid=abc&source=instagram&_pos=1&_sid=2&_ss=r&size=38',
    'https://diners.com.pk/products/suit-99?size=38',
  ],
  ['', ''],
]

describe('normalizeProductUrl (matching Python API)', () => {
  for (const [rawUrl, expected] of TEST_CASES) {
    it(`normalizes "${rawUrl}" -> "${expected}"`, () => {
      assert.equal(normalizeProductUrl(rawUrl), expected)
    })
  }
})
