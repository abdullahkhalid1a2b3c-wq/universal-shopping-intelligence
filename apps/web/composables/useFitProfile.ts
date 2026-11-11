import { ref, computed } from 'vue'
import { toStorageCm, fromStorageCm, cmToInches, inchesToCm } from '~/utils/units'

export interface FitProfileState {
  chest: number | null
  waist: number | null
  hip: number | null
  shoulder: number | null
  sleeve: number | null
  inseam: number | null
  kameez_length: number | null
  height: number | null
  unit: 'cm' | 'in'
  gender_category: 'womens' | 'mens' | 'unisex'
  fit_preference: 'regular' | 'fitted' | 'loose'
}

const STORAGE_KEY = 'fitsense_user_profile'

// Shared singleton reactive state so updates on any page reflect everywhere
const profileState = ref<FitProfileState>({
  chest: 100,
  waist: 85,
  hip: 105,
  shoulder: 45,
  sleeve: 62,
  inseam: 78,
  kameez_length: 102,
  height: 175,
  unit: 'cm',
  gender_category: 'unisex',
  fit_preference: 'regular',
})

const isLoaded = ref(false)
const isSaving = ref(false)

export function useFitProfile() {
  const user = useSupabaseUser()
  const supabase = useSupabaseClient()
  const toast = useToast()

  const hasProfile = computed(() => {
    return Boolean(
      profileState.value.chest ||
      profileState.value.waist ||
      profileState.value.shoulder ||
      profileState.value.height
    )
  })

  const completenessPercentage = computed(() => {
    const keys: (keyof FitProfileState)[] = ['chest', 'waist', 'hip', 'shoulder', 'height']
    const filled = keys.filter(k => profileState.value[k] != null && Number(profileState.value[k]) > 0)
    return Math.round((filled.length / keys.length) * 100)
  })

  // Load profile from localStorage first (instant for guest & offline), then Supabase if authenticated
  async function loadProfile() {
    if (isLoaded.value) return profileState.value

    // 1. Check local storage
    if (import.meta.client) {
      try {
        const cached = localStorage.getItem(STORAGE_KEY)
        if (cached) {
          const parsed = JSON.parse(cached)
          Object.assign(profileState.value, parsed)
        }
      } catch (err) {
        console.warn('Failed to parse cached profile', err)
      }
    }

    // 2. If logged in, fetch from database and update
    if (user.value) {
      const uid = user.value.id
      try {
        const { data: prof } = await supabase
          .from('profiles')
          .select('preferred_unit, gender_category, height_cm')
          .eq('user_id', uid)
          .single()

        if (prof?.preferred_unit) {
          profileState.value.unit = prof.preferred_unit as 'cm' | 'in'
        }
        if (prof?.gender_category) {
          profileState.value.gender_category = prof.gender_category as any
        }
        if (prof?.height_cm) {
          profileState.value.height = fromStorageCm(prof.height_cm, profileState.value.unit)
        }

        const { data: bm } = await supabase
          .from('body_measurements')
          .select('*')
          .eq('user_id', uid)
          .single()

        if (bm) {
          const u = profileState.value.unit
          if (bm.chest_cm) profileState.value.chest = fromStorageCm(bm.chest_cm, u)
          if (bm.waist_cm) profileState.value.waist = fromStorageCm(bm.waist_cm, u)
          if (bm.hip_cm) profileState.value.hip = fromStorageCm(bm.hip_cm, u)
          if (bm.shoulder_cm) profileState.value.shoulder = fromStorageCm(bm.shoulder_cm, u)
          if (bm.sleeve_cm) profileState.value.sleeve = fromStorageCm(bm.sleeve_cm, u)
          if (bm.inseam_cm) profileState.value.inseam = fromStorageCm(bm.inseam_cm, u)
          if (bm.kameez_length_cm) profileState.value.kameez_length = fromStorageCm(bm.kameez_length_cm, u)
        }

        // Cache the latest synced profile locally
        if (import.meta.client) {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(profileState.value))
        }
      } catch (err) {
        console.warn('Error fetching Supabase measurements', err)
      }
    }

    isLoaded.value = true
    return profileState.value
  }

  // Save profile to localStorage and to Supabase (if authenticated)
  async function saveProfile(customData?: Partial<FitProfileState>) {
    if (customData) {
      Object.assign(profileState.value, customData)
    }

    // Always persist to localStorage for 1-click cross-store memory
    if (import.meta.client) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(profileState.value))
      } catch (e) {
        console.warn('Failed to save profile to localStorage', e)
      }
    }

    // If authenticated, persist to Supabase
    if (user.value) {
      isSaving.value = true
      const uid = user.value.id
      const u = profileState.value.unit
      const toCm = (val: number | null | undefined) => (val != null ? toStorageCm(val, u) : null)

      try {
        // Update profiles table
        await supabase
          .from('profiles')
          .update({
            preferred_unit: profileState.value.unit,
            gender_category: profileState.value.gender_category,
            height_cm: toCm(profileState.value.height),
          })
          .eq('user_id', uid)

        // Upsert body_measurements table
        await supabase.from('body_measurements').upsert({
          user_id: uid,
          chest_cm: toCm(profileState.value.chest),
          waist_cm: toCm(profileState.value.waist),
          hip_cm: toCm(profileState.value.hip),
          shoulder_cm: toCm(profileState.value.shoulder),
          sleeve_cm: toCm(profileState.value.sleeve),
          inseam_cm: toCm(profileState.value.inseam),
          kameez_length_cm: toCm(profileState.value.kameez_length),
        }, { onConflict: 'user_id' })

        toast.success('Fit profile saved and synced across all stores!')
      } catch (err: any) {
        console.error('Failed to sync to database', err)
        toast.error(err.message || 'Saved locally, but database sync failed')
      } finally {
        isSaving.value = false
      }
    } else {
      toast.success('Fit profile saved on your device for instant 1-click sizing!')
    }
  }

  // Switch display units and convert values cleanly
  function setUnit(newUnit: 'cm' | 'in') {
    if (profileState.value.unit === newUnit) return
    const oldUnit = profileState.value.unit
    profileState.value.unit = newUnit

    const keys: (keyof FitProfileState)[] = [
      'chest', 'waist', 'hip', 'shoulder', 'sleeve', 'inseam', 'kameez_length', 'height'
    ]

    for (const k of keys) {
      const val = profileState.value[k]
      if (typeof val === 'number' && val > 0) {
        (profileState.value[k] as any) = newUnit === 'in' ? cmToInches(val) : inchesToCm(val)
      }
    }

    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profileState.value))
    }
  }

  // Auto-estimate shoulders and sleeve lengths proportionally from Height
  function autoEstimateFromHeight() {
    const h = profileState.value.height
    if (!h || h <= 0) {
      toast.info('Please enter your Height first')
      return
    }

    const u = profileState.value.unit
    const heightCm = toStorageCm(h, u) || 175
    const chestCm = toStorageCm(profileState.value.chest || 95, u) || 95

    // Anthropometric Pakistani body ratios:
    const chestOffset = Math.max(0, (chestCm - 86) * 0.08)
    const estShoulderCm = Math.round((heightCm * 0.245 + chestOffset) * 10) / 10
    const estSleeveCm = Math.round((heightCm * 0.365) * 10) / 10
    const estInseamCm = Math.round((heightCm * 0.455) * 10) / 10
    const estKameezCm = Math.round((heightCm * 0.585) * 10) / 10

    profileState.value.shoulder = fromStorageCm(estShoulderCm, u)
    profileState.value.sleeve = fromStorageCm(estSleeveCm, u)
    profileState.value.inseam = fromStorageCm(estInseamCm, u)
    profileState.value.kameez_length = fromStorageCm(estKameezCm, u)

    toast.success('Shoulders, sleeves, and lengths estimated from your height!')
  }

  // Format all measurements in cm for API payload
  function toApiPayload(category?: string) {
    const u = profileState.value.unit
    const toCm = (val: number | null | undefined) => (val != null ? toStorageCm(val, u) : null)

    return {
      chest_cm: toCm(profileState.value.chest),
      waist_cm: toCm(profileState.value.waist),
      hip_cm: toCm(profileState.value.hip),
      shoulder_cm: toCm(profileState.value.shoulder),
      sleeve_cm: toCm(profileState.value.sleeve),
      inseam_cm: toCm(profileState.value.inseam),
      kameez_length_cm: toCm(profileState.value.kameez_length),
      height_cm: toCm(profileState.value.height),
    }
  }

  return {
    profileState,
    hasProfile,
    completenessPercentage,
    isLoaded,
    isSaving,
    loadProfile,
    saveProfile,
    setUnit,
    autoEstimateFromHeight,
    toApiPayload,
  }
}

