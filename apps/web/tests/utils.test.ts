import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import {
  cmToInches,
  inchesToCm,
  toStorageCm,
  fromStorageCm,
  isValidMeasurement,
} from '../utils/units.ts'
import { estimateBodyFromGarment } from '../utils/garmentEstimator.ts'
import { normalizeProductUrl } from '../utils/url.ts'

describe('Product URL Normalizer', () => {
  test('strips utm parameters, trailing slashes, and www', () => {
    const raw = 'https://www.khaadi.com/products/lawn-kurta/?utm_source=facebook&utm_campaign=summer&ref=123'
    const canonical = normalizeProductUrl(raw)
    assert.equal(canonical, 'https://khaadi.com/products/lawn-kurta')
  })

  test('preserves functional variant parameters while dropping tracking', () => {
    const raw = 'https://sapphire.pk/product-1?variant=392819&gclid=xyz'
    const canonical = normalizeProductUrl(raw)
    assert.equal(canonical, 'https://sapphire.pk/product-1?variant=392819')
  })
})

describe('Unit Conversion Helpers', () => {
  test('cmToInches converts correctly with rounding', () => {
    assert.equal(cmToInches(100), 39.4)
    assert.equal(cmToInches(2.54), 1.0)
    assert.equal(cmToInches(0), 0)
    assert.equal(cmToInches(-5), 0)
  })

  test('inchesToCm converts correctly with rounding', () => {
    assert.equal(inchesToCm(40), 101.6)
    assert.equal(inchesToCm(1), 2.5)
    assert.equal(inchesToCm(0), 0)
  })

  test('toStorageCm normalizes values to cm', () => {
    assert.equal(toStorageCm(100, 'cm'), 100)
    assert.equal(toStorageCm(39.37, 'in'), 100)
    assert.equal(toStorageCm('105.5', 'cm'), 105.5)
    assert.equal(toStorageCm('', 'cm'), null)
    assert.equal(toStorageCm(-10, 'cm'), null)
  })

  test('fromStorageCm displays value in active unit', () => {
    assert.equal(fromStorageCm(100, 'cm'), 100)
    assert.equal(fromStorageCm(100, 'in'), 39.4)
    assert.equal(fromStorageCm(null, 'cm'), null)
    assert.equal(fromStorageCm(undefined, 'in'), null)
  })

  test('isValidMeasurement checks anatomical boundaries', () => {
    assert.equal(isValidMeasurement('chest', 100), true)
    assert.equal(isValidMeasurement('chest', 30), false) // below min 50
    assert.equal(isValidMeasurement('chest', 250), false) // above max 200
    assert.equal(isValidMeasurement('waist', 75), true)
  })
})

describe('Garment to Body Estimator', () => {
  test('estimates body chest and shoulder from flat shirt measurements', () => {
    const res = estimateBodyFromGarment({
      category: 'shirt',
      flat_chest_cm: 55, // 110 cm full circumference
      shoulder_cm: 45,
      length_cm: 72,
    })

    assert.equal(res.is_estimate, true)
    // 55 * 2 - 10 = 100 cm chest
    assert.equal(res.chest_cm, 100)
    // 45 - 1.5 = 43.5 cm shoulder
    assert.equal(res.shoulder_cm, 43.5)
    assert.equal(res.torso_length_cm, 72)
    assert.equal(typeof res.source_note, 'string')
  })

  test('estimates waist and inseam from flat trouser measurements', () => {
    const res = estimateBodyFromGarment({
      category: 'trouser',
      flat_waist_cm: 42, // 84 cm circumference
      inseam_cm: 78,
    })

    assert.equal(res.is_estimate, true)
    // 42 * 2 - 3 = 81 cm waist
    assert.equal(res.waist_cm, 81)
    assert.equal(res.inseam_cm, 78)
  })
})

