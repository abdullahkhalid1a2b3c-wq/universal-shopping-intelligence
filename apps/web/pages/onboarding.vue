<template>
  <div class="max-w-2xl mx-auto px-4 py-8 sm:py-12">
    <!-- Progress Indicator -->
    <ProgressBar
      :current-step="currentStep"
      :total-steps="4"
      :step-names="[
        $t('onboarding.step1'),
        $t('onboarding.step2'),
        $t('onboarding.step3'),
        $t('onboarding.step4'),
      ]"
    />

    <div class="mt-8 bg-slate-900/90 backdrop-blur-2xl p-6 sm:p-10 rounded-3xl shadow-2xl border border-slate-800 space-y-8 text-white">
      <!-- ================= STEP 1: PREFERENCES ================= -->
      <div v-if="currentStep === 1" class="space-y-6">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">
            {{ $t('onboarding.step1Title') }}
          </h2>
          <p class="text-sm text-slate-400 mt-1">
            {{ $t('onboarding.step1Subtitle') }}
          </p>
        </div>

        <div class="space-y-5">
          <!-- Preferred Language -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              {{ $t('onboarding.preferredLanguage') }}
            </label>
            <div class="grid grid-cols-3 gap-3">
              <button
                v-for="l in languages"
                :key="l.code"
                type="button"
                class="py-3 px-3 text-sm font-semibold rounded-2xl border text-center transition"
                :class="selectedLanguage === l.code ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30' : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'"
                @click="setLanguage(l.code)"
              >
                {{ l.name }}
              </button>
            </div>
          </div>

          <!-- Preferred Unit -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              {{ $t('onboarding.preferredUnit') }}
            </label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                class="py-3 px-4 text-sm font-semibold rounded-2xl border text-center transition"
                :class="preferredUnit === 'cm' ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30' : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'"
                @click="preferredUnit = 'cm'"
              >
                Centimetres (cm)
              </button>
              <button
                type="button"
                class="py-3 px-4 text-sm font-semibold rounded-2xl border text-center transition"
                :class="preferredUnit === 'in' ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30' : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'"
                @click="preferredUnit = 'in'"
              >
                Inches (in)
              </button>
            </div>
          </div>

          <!-- Gender Category -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              {{ $t('onboarding.genderCategory') }}
            </label>
            <div class="grid grid-cols-3 gap-3">
              <button
                v-for="g in genderOptions"
                :key="g.value"
                type="button"
                class="py-3 px-2 text-xs sm:text-sm font-semibold rounded-2xl border text-center transition"
                :class="genderCategory === g.value ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30' : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700'"
                @click="genderCategory = g.value"
              >
                {{ $t(`onboarding.gender.${g.value}`) }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= STEP 2: PRIVACY CONSENT (MANDATORY) ================= -->
      <div v-else-if="currentStep === 2" class="space-y-6">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">
            {{ $t('onboarding.step2Title') }}
          </h2>
          <p class="text-sm text-slate-400 mt-1">
            {{ $t('onboarding.step2Subtitle') }}
          </p>
        </div>

        <div class="p-5 bg-indigo-950/40 border border-indigo-900/60 rounded-2xl space-y-3 text-xs sm:text-sm text-indigo-200">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <p>{{ $t('onboarding.consentBullet1') }}</p>
          </div>
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <p>{{ $t('onboarding.consentBullet2') }}</p>
          </div>
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <p>{{ $t('onboarding.consentBullet3') }}</p>
          </div>
        </div>

        <div class="pt-2">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              v-model="hasGivenConsent"
              type="checkbox"
              required
              class="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-slate-700 bg-slate-800 mt-0.5"
            />
            <span class="text-sm font-semibold text-slate-200">
              {{ $t('onboarding.consentCheckbox') }}
            </span>
          </label>
        </div>

        <div class="text-xs">
          <NuxtLink :to="localePath('/privacy')" target="_blank" class="text-indigo-400 hover:text-indigo-300 font-medium">
            {{ $t('onboarding.privacyLink') }} &rarr;
          </NuxtLink>
        </div>
      </div>

      <!-- ================= STEP 3: MEASUREMENTS ================= -->
      <div v-else-if="currentStep === 3" class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 class="text-2xl font-black text-white tracking-tight">
              {{ $t('onboarding.step3Title') }}
            </h2>
            <p class="text-sm text-slate-400 mt-1">
              {{ $t('onboarding.step3Subtitle') }}
            </p>
          </div>

          <!-- Secondary Entry Option: Measure garment button -->
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-indigo-400 bg-indigo-950/60 hover:bg-indigo-900/60 border border-indigo-800/80 rounded-xl transition self-start"
            @click="isGarmentModalOpen = true"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
            </svg>
            <span>{{ $t('onboarding.orGarment') }}</span>
          </button>
        </div>

        <!-- Estimate Banner if applied from garment -->
        <div v-if="appliedEstimateNotice" class="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl text-xs font-semibold text-amber-200 flex items-center justify-between">
          <span>{{ $t('onboarding.estimateBadge') }}</span>
          <button type="button" class="text-amber-400 hover:text-amber-200" @click="appliedEstimateNotice = false">&times;</button>
        </div>

        <!-- Required Fields -->
        <div class="space-y-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-indigo-400">Essential Measurements</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <MeasurementInput
              v-model="chestDisplay"
              field-key="chest"
              :label="$t('measurements.chest')"
              :unit="preferredUnit"
              required
              :tip="$t('measurements.tips.chest')"
            />

            <MeasurementInput
              v-model="waistDisplay"
              field-key="waist"
              :label="$t('measurements.waist')"
              :unit="preferredUnit"
              required
              :tip="$t('measurements.tips.waist')"
            />

            <MeasurementInput
              v-model="hipDisplay"
              field-key="hip"
              :label="$t('measurements.hip')"
              :unit="preferredUnit"
              required
              :tip="$t('measurements.tips.hip')"
            />

            <MeasurementInput
              v-model="shoulderDisplay"
              field-key="shoulder"
              :label="$t('measurements.shoulder')"
              :unit="preferredUnit"
              :tip="$t('measurements.tips.shoulder')"
            />
          </div>
        </div>

        <!-- Optional Fields Toggle -->
        <div class="border-t border-slate-800 pt-4">
          <button
            type="button"
            class="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 focus:outline-none"
            @click="showOptionalMeasurements = !showOptionalMeasurements"
          >
            <span>{{ showOptionalMeasurements ? '▲ Hide additional measurements' : '+ Add sleeve, inseam, kameez length (optional)' }}</span>
          </button>

          <div v-if="showOptionalMeasurements" class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4 animate-fadeIn">
            <MeasurementInput
              v-model="sleeveDisplay"
              field-key="sleeve"
              :label="$t('measurements.sleeve')"
              :unit="preferredUnit"
              :tip="$t('measurements.tips.sleeve')"
            />

            <MeasurementInput
              v-model="inseamDisplay"
              field-key="inseam"
              :label="$t('measurements.inseam')"
              :unit="preferredUnit"
              :tip="$t('measurements.tips.inseam')"
            />

            <MeasurementInput
              v-model="kameezLengthDisplay"
              field-key="kameez_length"
              :label="$t('measurements.kameez_length')"
              :unit="preferredUnit"
              :tip="$t('measurements.tips.kameez_length')"
            />
          </div>
        </div>
      </div>

      <!-- ================= STEP 4: FIT PREFERENCES ================= -->
      <div v-else-if="currentStep === 4" class="space-y-6">
        <div>
          <h2 class="text-2xl font-black text-white tracking-tight">
            {{ $t('onboarding.step4Title') }}
          </h2>
          <p class="text-sm text-slate-400 mt-1">
            {{ $t('onboarding.step4Subtitle') }}
          </p>
        </div>

        <div class="space-y-5">
          <div
            v-for="cat in categories"
            :key="cat.key"
            class="p-4 bg-slate-800/60 rounded-2xl border border-slate-700/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div>
              <span class="text-sm font-bold text-white">{{ cat.name }}</span>
              <p class="text-xs text-slate-400 mt-0.5">
                {{ $t(`onboarding.${fitPreferences[cat.key]}Desc`) }}
              </p>
            </div>

            <!-- Fit Segmented Control -->
            <div class="grid grid-cols-3 gap-1 bg-slate-900 p-1 rounded-xl border border-slate-700 shrink-0">
              <button
                v-for="fitOption in ['fitted', 'regular', 'loose'] as const"
                :key="fitOption"
                type="button"
                class="px-3 py-1.5 text-xs font-bold rounded-lg transition"
                :class="fitPreferences[cat.key] === fitOption ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'"
                @click="fitPreferences[cat.key] = fitOption"
              >
                {{ $t(`common.${fitOption}`) }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ================= ACTIONS / FOOTER ================= -->
      <div class="flex items-center justify-between pt-6 border-t border-slate-800">
        <!-- Skip button: allowed for step 1, 3, 4 (NEVER step 2 consent) -->
        <div>
          <button
            v-if="currentStep !== 2"
            type="button"
            class="text-xs font-bold text-slate-400 hover:text-white transition"
            @click="handleSkip"
          >
            {{ $t('onboarding.skip') }}
          </button>
        </div>

        <!-- Next / Finish button -->
        <button
          type="button"
          :disabled="currentStep === 2 && !hasGivenConsent"
          class="py-3.5 px-7 rounded-2xl font-bold text-sm text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition shadow-lg shadow-indigo-600/30 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
          @click="handleNext"
        >
          <span>{{ currentStep === 4 ? $t('onboarding.finish') : $t('onboarding.next') }}</span>
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Garment Measurement Modal -->
    <GarmentMeasurementModal
      :is-open="isGarmentModalOpen"
      :unit="preferredUnit"
      @close="isGarmentModalOpen = false"
      @applied="onGarmentEstimateApplied"
    />
  </div>
</template>

<script setup lang="ts">
import { toStorageCm, fromStorageCm, cmToInches } from '~/utils/units'
import type { EstimatedBodyMeasurements } from '~/utils/garmentEstimator'

const supabase = useSupabaseClient()
const user = useSupabaseUser()
const localePath = useLocalePath()
const { setLocale, locale } = useI18n()
const toast = useToast()

const currentStep = ref(1)

// Step 1 State
const selectedLanguage = ref(locale.value || 'en')
const preferredUnit = ref<'cm' | 'in'>('cm')
const genderCategory = ref<'womens' | 'mens' | 'unisex'>('womens')

const languages = [
  { code: 'en', name: 'English' },
  { code: 'ur', name: 'اردو' },
  { code: 'ur-roman', name: 'Roman Urdu' },
]

const genderOptions = [
  { value: 'womens' },
  { value: 'mens' },
  { value: 'unisex' },
] as const

function setLanguage(code: string) {
  selectedLanguage.value = code
  setLocale(code)
}

// Step 2 State (Consent)
const hasGivenConsent = ref(false)

// Step 3 State (Measurements in display unit)
const chestDisplay = ref<number | null>(null)
const waistDisplay = ref<number | null>(null)
const hipDisplay = ref<number | null>(null)
const shoulderDisplay = ref<number | null>(null)
const sleeveDisplay = ref<number | null>(null)
const inseamDisplay = ref<number | null>(null)
const kameezLengthDisplay = ref<number | null>(null)
const showOptionalMeasurements = ref(false)

// Garment Estimator Modal
const isGarmentModalOpen = ref(false)
const appliedEstimateNotice = ref(false)

function onGarmentEstimateApplied(estimates: EstimatedBodyMeasurements) {
  appliedEstimateNotice.value = true
  if (estimates.chest_cm) {
    chestDisplay.value = fromStorageCm(estimates.chest_cm, preferredUnit.value)
  }
  if (estimates.shoulder_cm) {
    shoulderDisplay.value = fromStorageCm(estimates.shoulder_cm, preferredUnit.value)
  }
  if (estimates.waist_cm) {
    waistDisplay.value = fromStorageCm(estimates.waist_cm, preferredUnit.value)
  }
  if (estimates.inseam_cm) {
    inseamDisplay.value = fromStorageCm(estimates.inseam_cm, preferredUnit.value)
    showOptionalMeasurements.value = true
  }
  if (estimates.kameez_length_cm) {
    kameezLengthDisplay.value = fromStorageCm(estimates.kameez_length_cm, preferredUnit.value)
    showOptionalMeasurements.value = true
  }
}

// Step 4 State (Category fit preferences)
const categories = [
  { key: 'tshirt_top', name: 'T-Shirts & Tops' },
  { key: 'shirt', name: 'Shirts' },
  { key: 'kurta', name: 'Kurtas' },
  { key: 'trouser', name: 'Trousers' },
  { key: 'jeans', name: 'Jeans' },
  { key: 'dress', name: 'Dresses' },
]

const fitPreferences = ref<Record<string, 'fitted' | 'regular' | 'loose'>>({
  tshirt_top: 'regular',
  shirt: 'regular',
  kurta: 'regular',
  trouser: 'regular',
  jeans: 'fitted',
  dress: 'regular',
})

async function saveCurrentProgress() {
  if (!user.value) return

  const uid = user.value.id

  if (currentStep.value === 1) {
    await supabase.from('profiles').upsert({
      user_id: uid,
      preferred_language: selectedLanguage.value,
      preferred_unit: preferredUnit.value,
      gender_category: genderCategory.value,
    })
  } else if (currentStep.value === 2) {
    if (hasGivenConsent.value) {
      await supabase.from('consents').insert({
        user_id: uid,
        consent_type: 'store_measurements',
        granted: true,
        policy_version: 'v1.0',
      })
    }
  } else if (currentStep.value === 3) {
    const toCm = (val: number | null) => (val != null ? toStorageCm(val, preferredUnit.value) : null)
    await supabase.from('body_measurements').upsert({
      user_id: uid,
      chest_cm: toCm(chestDisplay.value),
      waist_cm: toCm(waistDisplay.value),
      hip_cm: toCm(hipDisplay.value),
      shoulder_cm: toCm(shoulderDisplay.value),
      sleeve_cm: toCm(sleeveDisplay.value),
      inseam_cm: toCm(inseamDisplay.value),
      kameez_length_cm: toCm(kameezLengthDisplay.value),
    })
  } else if (currentStep.value === 4) {
    const rows = Object.entries(fitPreferences.value).map(([cat, fit]) => ({
      user_id: uid,
      category: cat,
      fit,
    }))
    await supabase.from('fit_preferences').upsert(rows)
  }
}

async function handleNext() {
  await saveCurrentProgress()
  if (currentStep.value < 4) {
    currentStep.value++
  } else {
    toast.success('Onboarding complete!')
    navigateTo(localePath('/profile'))
  }
}

function handleSkip() {
  if (currentStep.value < 4) {
    currentStep.value++
  } else {
    navigateTo(localePath('/profile'))
  }
}
</script>

