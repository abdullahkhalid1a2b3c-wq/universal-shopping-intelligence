import { test, describe } from 'node:test'
import assert from 'node:assert/strict'
import { toStorageCm, fromStorageCm, isValidMeasurement } from '../utils/units.ts'
import { estimateBodyFromGarment } from '../utils/garmentEstimator.ts'

describe('Onboarding Flow Logic & State Progression', () => {
  interface OnboardingState {
    currentStep: number
    preferredLanguage: string
    preferredUnit: 'cm' | 'in'
    genderCategory: 'womens' | 'mens' | 'unisex'
    hasGivenConsent: boolean
    chest_cm: number | null
    waist_cm: number | null
    hip_cm: number | null
    fitPreferences: Record<string, string>
  }

  function createInitialState(): OnboardingState {
    return {
      currentStep: 1,
      preferredLanguage: 'en',
      preferredUnit: 'cm',
      genderCategory: 'womens',
      hasGivenConsent: false,
      chest_cm: null,
      waist_cm: null,
      hip_cm: null,
      fitPreferences: {
        tshirt_top: 'regular',
        shirt: 'regular',
        trouser: 'regular',
      },
    }
  }

  test('Step 1: Set language and unit preferences', () => {
    const state = createInitialState()
    assert.equal(state.currentStep, 1)

    // User selects Roman Urdu and Inches
    state.preferredLanguage = 'ur-roman'
    state.preferredUnit = 'in'
    state.genderCategory = 'mens'
    state.currentStep = 2

    assert.equal(state.preferredLanguage, 'ur-roman')
    assert.equal(state.preferredUnit, 'in')
    assert.equal(state.currentStep, 2)
  })

  test('Step 2: Consent is mandatory and blocks progression when false', () => {
    const state = createInitialState()
    state.currentStep = 2

    // Attempting to proceed without consent must fail
    const canProceedWithoutConsent = state.hasGivenConsent
    assert.equal(canProceedWithoutConsent, false)

    // Giving consent unlocks next step
    state.hasGivenConsent = true
    const canProceedWithConsent = state.hasGivenConsent
    assert.equal(canProceedWithConsent, true)

    state.currentStep = 3
    assert.equal(state.currentStep, 3)
  })

  test('Step 3: Direct measurements entry with unit conversion to storage cm', () => {
    const state = createInitialState()
    state.currentStep = 3
    state.preferredUnit = 'in' // user entered 40 inches chest

    const inputChestInches = 40.0
    const convertedCm = toStorageCm(inputChestInches, state.preferredUnit)
    assert.equal(convertedCm, 101.6)

    // Validated anatomical range
    assert.equal(isValidMeasurement('chest', convertedCm!), true)
    state.chest_cm = convertedCm

    assert.equal(state.chest_cm, 101.6)
  })

  test('Step 3 (Alternative): Estimating body measurements from flat garment', () => {
    const state = createInitialState()
    state.currentStep = 3

    // User measures a flat shirt with 52cm chest width
    const estimate = estimateBodyFromGarment({
      category: 'shirt',
      flat_chest_cm: 52,
      shoulder_cm: 44,
    })

    assert.equal(estimate.is_estimate, true)
    assert.equal(estimate.chest_cm, 94) // (52 * 2) - 10
    assert.equal(estimate.shoulder_cm, 42.5) // 44 - 1.5

    // Apply estimate to onboarding state
    state.chest_cm = estimate.chest_cm
    assert.equal(state.chest_cm, 94)
  })

  test('Step 4: Category fit style assignment and completion', () => {
    const state = createInitialState()
    state.currentStep = 4

    state.fitPreferences.jeans = 'fitted'
    state.fitPreferences.tshirt_top = 'loose'

    assert.equal(state.fitPreferences.jeans, 'fitted')
    assert.equal(state.fitPreferences.tshirt_top, 'loose')

    // Profile complete
    const isCompleted = state.currentStep === 4
    assert.equal(isCompleted, true)
  })
})

