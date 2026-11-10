/**
 * Unit conversion and measurement validation utilities for FitSense.
 * 
 * Rules:
 * - All measurements are internally stored in centimetres (cm).
 * - Conversions to inches occur strictly in the UI layer.
 */

export const CM_PER_INCH = 2.54

export interface MeasurementBounds {
  min: number
  max: number
}

export const MEASUREMENT_BOUNDS: Record<string, MeasurementBounds> = {
  chest: { min: 50, max: 200 },
  waist: { min: 40, max: 180 },
  hip: { min: 50, max: 200 },
  shoulder: { min: 25, max: 70 },
  sleeve: { min: 20, max: 100 },
  inseam: { min: 30, max: 120 },
  thigh: { min: 25, max: 100 },
  torso_length: { min: 30, max: 100 },
  kameez_length: { min: 50, max: 160 },
  height: { min: 50, max: 260 },
  weight: { min: 20, max: 300 },
}

/**
 * Convert centimetres to inches rounded to 1 decimal place.
 */
export function cmToInches(cm: number): number {
  if (isNaN(cm) || cm <= 0) return 0
  return Math.round((cm / CM_PER_INCH) * 10) / 10
}

/**
 * Convert inches to centimetres rounded to 1 decimal place.
 */
export function inchesToCm(inches: number): number {
  if (isNaN(inches) || inches <= 0) return 0
  return Math.round(inches * CM_PER_INCH * 10) / 10
}

/**
 * Convert a user-entered value into centimetres for storage.
 */
export function toStorageCm(value: number | string, unit: 'cm' | 'in'): number | null {
  const numeric = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numeric) || numeric <= 0) return null
  return unit === 'in' ? inchesToCm(numeric) : Math.round(numeric * 10) / 10
}

/**
 * Format a stored centimetre value for display in the active unit.
 */
export function fromStorageCm(cmValue: number | null | undefined, unit: 'cm' | 'in'): number | null {
  if (cmValue == null || isNaN(cmValue) || cmValue <= 0) return null
  return unit === 'in' ? cmToInches(cmValue) : Math.round(cmValue * 10) / 10
}

/**
 * Validate that a measurement in centimetres falls within a sensible anatomical range.
 */
export function isValidMeasurement(key: string, cmValue: number): boolean {
  const bounds = MEASUREMENT_BOUNDS[key]
  if (!bounds) return true
  return cmValue >= bounds.min && cmValue <= bounds.max
}

