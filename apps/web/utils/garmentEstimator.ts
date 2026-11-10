/**
 * Garment-to-Body Measurement Estimator.
 * 
 * Allows a customer to lay their favorite garment flat and calculate
 * approximate starting body measurements.
 * 
 * NOTE: The result is clearly presented to the user as an editable estimate.
 */

export interface FlatGarmentInput {
  category: 'tshirt_top' | 'shirt' | 'trouser' | 'jeans' | 'kurta' | 'dress'
  flat_chest_cm?: number | null
  length_cm?: number | null
  shoulder_cm?: number | null
  flat_waist_cm?: number | null
  inseam_cm?: number | null
}

export interface EstimatedBodyMeasurements {
  chest_cm?: number
  waist_cm?: number
  hip_cm?: number
  shoulder_cm?: number
  inseam_cm?: number
  torso_length_cm?: number
  kameez_length_cm?: number
  is_estimate: true
  source_note: string
}

/**
 * Estimate body measurements from flat garment measurements.
 * 
 * Formula rationale:
 * - Flat chest * 2 gives garment circumference. Standard top ease is ~10 cm, so body chest ≈ (flat_chest * 2) - 10 cm.
 * - Flat waist * 2 gives trouser waistband circumference. Standard waistband ease is ~3 cm.
 * - Flat shoulder width is typically ~1.5 cm wider than anatomical shoulder tip-to-tip.
 * - Inseam and garment length match closely with anatomical inseam and torso/kameez length.
 */
export function estimateBodyFromGarment(garment: FlatGarmentInput): EstimatedBodyMeasurements {
  const estimates: EstimatedBodyMeasurements = {
    is_estimate: true,
    source_note: `Estimated from flat ${garment.category} measurement. Please adjust if needed.`,
  }

  // Chest estimate
  if (garment.flat_chest_cm && garment.flat_chest_cm > 0) {
    const fullCircumference = garment.flat_chest_cm * 2
    // Average baseline ease: 10 cm for tops/shirts/kurtas
    const estimatedChest = fullCircumference - 10
    estimates.chest_cm = Math.max(50, Math.round(estimatedChest * 10) / 10)
  }

  // Shoulder estimate
  if (garment.shoulder_cm && garment.shoulder_cm > 0) {
    const estimatedShoulder = garment.shoulder_cm - 1.5
    estimates.shoulder_cm = Math.max(25, Math.round(estimatedShoulder * 10) / 10)
  }

  // Length estimate
  if (garment.length_cm && garment.length_cm > 0) {
    if (garment.category === 'kurta') {
      estimates.kameez_length_cm = Math.round(garment.length_cm * 10) / 10
    } else {
      estimates.torso_length_cm = Math.round(garment.length_cm * 10) / 10
    }
  }

  // Waist estimate (for trousers/jeans)
  if (garment.flat_waist_cm && garment.flat_waist_cm > 0) {
    const fullWaistCircumference = garment.flat_waist_cm * 2
    const estimatedWaist = fullWaistCircumference - 3
    estimates.waist_cm = Math.max(40, Math.round(estimatedWaist * 10) / 10)
  }

  // Inseam estimate
  if (garment.inseam_cm && garment.inseam_cm > 0) {
    estimates.inseam_cm = Math.round(garment.inseam_cm * 10) / 10
  }

  return estimates
}

