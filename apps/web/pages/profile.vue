<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:py-12 space-y-8">
    <!-- Header & Interactive Completeness Card -->
    <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div class="space-y-2">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-bold uppercase tracking-wider">
          <span>🇵🇰 Universal Fashion Profile</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black text-white tracking-tight">
          {{ $t('profile.title') }}
        </h1>
        <p class="text-xs sm:text-sm text-slate-300 max-w-lg leading-relaxed">
          {{ $t('profile.subtitle') }}
        </p>
      </div>

      <!-- Completeness Meter -->
      <div class="p-5 bg-slate-800/80 border border-slate-700/80 rounded-2xl min-w-[260px] space-y-3 shadow-inner">
        <div class="flex items-center justify-between text-xs font-bold">
          <span class="text-slate-300 uppercase tracking-wider">{{ $t('profile.completeness') }}</span>
          <span
            class="px-2.5 py-0.5 rounded-full text-xs font-black shadow-sm"
            :class="
              completenessPercentage >= 80
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30'
                : completenessPercentage >= 50
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-400/30'
                : 'bg-amber-500/20 text-amber-300 border border-amber-400/30'
            "
          >
            {{ completenessPercentage }}%
          </span>
        </div>
        <div class="w-full h-3 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-700">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="
              completenessPercentage >= 80
                ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                : completenessPercentage >= 50
                ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
                : 'bg-gradient-to-r from-amber-500 to-orange-400'
            "
            :style="{ width: `${completenessPercentage}%` }"
          ></div>
        </div>
        <p class="text-[11px] text-slate-400 leading-tight">
          <span v-if="completenessPercentage >= 80" class="text-emerald-400 font-semibold">
            ✓ High-precision fitting unlocked across all brands!
          </span>
          <span v-else>
            Add chest, waist, and hip measurements to unlock 90%+ confidence recommendations.
          </span>
        </p>
      </div>
    </div>

    <!-- Main Profile Edit Form -->
    <form class="space-y-8" @submit.prevent="saveProfile">
      <!-- Section 1: Basic Preferences -->
      <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
        <div class="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div class="w-9 h-9 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-base">
            👤
          </div>
          <div>
            <h2 class="text-lg font-black text-white">
              {{ $t('profile.sections.basics') }}
            </h2>
            <p class="text-xs text-slate-400">Personal identity and measurement unit defaults</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <!-- Display Name -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
              Display Name
            </label>
            <input
              v-model="profile.display_name"
              type="text"
              class="w-full rounded-2xl border border-slate-700 bg-slate-800 text-white font-bold py-3 px-4 text-sm placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 transition shadow-inner"
              placeholder="e.g. Abdullah Khalid"
            />
          </div>

          <!-- Preferred Unit -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
              {{ $t('onboarding.preferredUnit') }}
            </label>
            <div class="relative">
              <select
                v-model="profile.preferred_unit"
                style="color-scheme: dark;"
                class="w-full rounded-2xl border border-slate-700 bg-slate-800 text-white font-bold py-3 px-4 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 transition shadow-inner appearance-none cursor-pointer"
                @change="onUnitChange"
              >
                <option value="cm" class="bg-slate-900 text-white py-2">Centimetres (cm)</option>
                <option value="in" class="bg-slate-900 text-white py-2">Inches (in)</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                ▼
              </div>
            </div>
          </div>

          <!-- Shopping Category -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
              {{ $t('onboarding.genderCategory') }}
            </label>
            <div class="relative">
              <select
                v-model="profile.gender_category"
                style="color-scheme: dark;"
                class="w-full rounded-2xl border border-slate-700 bg-slate-800 text-white font-bold py-3 px-4 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 transition shadow-inner appearance-none cursor-pointer"
              >
                <option value="womens" class="bg-slate-900 text-white py-2">Women's Fashion (Eastern & Western)</option>
                <option value="mens" class="bg-slate-900 text-white py-2">Men's Fashion (Kurta & Western)</option>
                <option value="unisex" class="bg-slate-900 text-white py-2">Unisex / All Collections</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
                ▼
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 2: Body Measurements -->
      <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-base">
              📐
            </div>
            <div>
              <h2 class="text-lg font-black text-white">
                {{ $t('profile.sections.measurements') }}
              </h2>
              <p class="text-xs text-slate-400">
                Stored in cm internally; seamlessly displayed in {{ profile.preferred_unit.toUpperCase() }}.
              </p>
            </div>
          </div>
          <span class="text-xs font-bold uppercase tracking-wider text-purple-400 px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full">
            Active: {{ profile.preferred_unit.toUpperCase() }}
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
          <MeasurementInput
            v-model="measurements.chest"
            field-key="chest"
            :label="$t('measurements.chest')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.chest')"
            required
          />

          <MeasurementInput
            v-model="measurements.waist"
            field-key="waist"
            :label="$t('measurements.waist')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.waist')"
          />

          <MeasurementInput
            v-model="measurements.hip"
            field-key="hip"
            :label="$t('measurements.hip')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.hip')"
          />

          <MeasurementInput
            v-model="measurements.shoulder"
            field-key="shoulder"
            :label="$t('measurements.shoulder')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.shoulder')"
          />

          <MeasurementInput
            v-model="measurements.sleeve"
            field-key="sleeve"
            :label="$t('measurements.sleeve')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.sleeve')"
          />

          <MeasurementInput
            v-model="measurements.inseam"
            field-key="inseam"
            :label="$t('measurements.inseam')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.inseam')"
          />

          <MeasurementInput
            v-model="measurements.kameez_length"
            field-key="kameez_length"
            :label="$t('measurements.kameez_length')"
            :unit="profile.preferred_unit"
            :tip="$t('measurements.tips.kameez_length')"
          />
        </div>

        <!-- AI Assistant Measurement Helper Callout -->
        <div class="p-4 rounded-2xl bg-indigo-950/50 border border-indigo-900/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <span class="text-2xl shrink-0">✨</span>
            <div class="text-xs">
              <p class="font-bold text-indigo-200">Unsure about taking measurements?</p>
              <p class="text-slate-300 mt-0.5">
                Ask the AI Fit Assistant about measuring tape placement, converting flat clothes, or brand-specific ease allowances.
              </p>
            </div>
          </div>
          <button
            type="button"
            @click="isAssistantOpen = true"
            class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md transition shrink-0"
          >
            Ask AI Assistant &rarr;
          </button>
        </div>
      </div>

      <!-- Section 3: Fit Preferences -->
      <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
        <div class="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div class="w-9 h-9 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-base">
            ✨
          </div>
          <div>
            <h2 class="text-lg font-black text-white">
              {{ $t('profile.sections.preferences') }}
            </h2>
            <p class="text-xs text-slate-400">Custom ease preference per clothing category</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            v-for="cat in categories"
            :key="cat.key"
            class="p-4 bg-slate-800/80 rounded-2xl border border-slate-700/80 flex items-center justify-between shadow-inner"
          >
            <span class="text-sm font-bold text-slate-200">{{ cat.name }}</span>
            <div class="grid grid-cols-3 gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                v-for="fit in ['fitted', 'regular', 'loose'] as const"
                :key="fit"
                type="button"
                class="px-2.5 py-1 text-xs font-bold rounded-lg transition"
                :class="
                  fitPreferences[cat.key] === fit
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                "
                @click="fitPreferences[cat.key] = fit"
              >
                {{ $t(`common.${fit}`) }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Section 4: Privacy & Data Protection -->
      <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-800 space-y-6">
        <div class="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div class="w-9 h-9 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-base">
            🔒
          </div>
          <div>
            <h2 class="text-lg font-black text-white">
              {{ $t('profile.sections.privacy') }}
            </h2>
            <p class="text-xs text-slate-400">GDPR compliance, consent toggles, and data portability</p>
          </div>
        </div>

        <!-- Consent Toggle -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-800/60 border border-slate-700">
          <div>
            <h4 class="text-sm font-bold text-white">{{ $t('profile.storeMeasurementsTitle') }}</h4>
            <p class="text-xs text-slate-400 mt-1 max-w-md leading-relaxed">
              {{ $t('profile.storeMeasurementsDesc') }}
            </p>
          </div>
          <button
            type="button"
            class="relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="hasMeasurementConsent ? 'bg-indigo-600' : 'bg-slate-700'"
            @click="handleConsentToggle"
          >
            <span
              class="pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
              :class="hasMeasurementConsent ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>

        <!-- Portability & Account Erasure -->
        <div class="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div>
            <h4 class="text-sm font-bold text-white">{{ $t('profile.dataRightsTitle') }}</h4>
            <p class="text-xs text-slate-400 mt-0.5">
              {{ $t('profile.dataRightsDesc') }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="px-4 py-2.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition flex items-center gap-2 shadow-sm"
              @click="downloadMyData"
            >
              <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>{{ $t('profile.downloadDataBtn') }}</span>
            </button>

            <button
              type="button"
              class="px-4 py-2.5 rounded-xl border border-rose-800/60 bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 text-xs font-bold transition flex items-center gap-2 shadow-sm"
              @click="showDeleteModal = true"
            >
              <svg class="w-4 h-4 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>{{ $t('profile.deleteAccountBtn') }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Save Changes Action Bar -->
      <div class="sticky bottom-4 z-30 p-4 rounded-2xl bg-slate-900/90 backdrop-blur-xl border border-slate-700 shadow-2xl flex items-center justify-between gap-4">
        <div class="hidden sm:flex items-center gap-2 text-xs text-slate-300">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Ready to sync your profile across 27+ Pakistani fashion stores.</span>
        </div>
        <button
          type="submit"
          :disabled="isSaving"
          class="w-full sm:w-auto py-3.5 px-8 rounded-xl font-black text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition shadow-xl shadow-indigo-600/30 hover:scale-[1.02] active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2.5"
        >
          <span v-if="isSaving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
          <span v-if="isSaving">{{ $t('common.loading') }}</span>
          <span v-else class="flex items-center gap-2">
            <span>💾</span>
            <span>{{ $t('profile.saveChanges') }}</span>
          </span>
        </button>
      </div>
    </form>

    <!-- Delete Account Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 backdrop-blur-md"
    >
      <div class="bg-slate-900 rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-5 shadow-2xl border border-slate-800">
        <div class="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        <div>
          <h3 class="text-lg font-black text-white">{{ $t('profile.deleteModalTitle') }}</h3>
          <p class="text-xs text-slate-300 mt-1 leading-relaxed">
            {{ $t('profile.deleteModalDesc') }}
          </p>
        </div>

        <div class="p-3 bg-slate-800 rounded-xl border border-slate-700">
          <label class="flex items-start gap-2.5 cursor-pointer">
            <input
              v-model="keepAnonymousFeedback"
              type="checkbox"
              class="w-4 h-4 mt-0.5 rounded text-indigo-600 focus:ring-indigo-500 border-slate-600 bg-slate-700"
            />
            <span class="text-xs text-slate-300 font-medium">
              {{ $t('profile.keepAnonymousFeedbackCheckbox') }}
            </span>
          </label>
        </div>

        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            class="px-4 py-2 text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 rounded-xl transition"
            @click="showDeleteModal = false"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            type="button"
            class="px-5 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 rounded-xl transition shadow-md shadow-rose-900/40"
            :disabled="isDeletingAccount"
            @click="executeAccountDeletion"
          >
            <span v-if="isDeletingAccount">{{ $t('common.loading') }}</span>
            <span v-else>{{ $t('profile.confirmDeleteBtn') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toStorageCm, fromStorageCm, cmToInches, inchesToCm } from '~/utils/units'

definePageMeta({
  middleware: ['auth'],
})

const supabase = useSupabaseClient()
const user = useSupabaseUser()
const toast = useToast()
const { t } = useI18n()
const api = useApi()

const isSaving = ref(false)
const hasMeasurementConsent = ref(true)
const showDeleteModal = ref(false)
const isAssistantOpen = useState('fitsense_assistant_open', () => false)
const keepAnonymousFeedback = ref(true)
const isDeletingAccount = ref(false)

const profile = ref({
  display_name: '',
  preferred_unit: 'cm' as 'cm' | 'in',
  gender_category: 'womens',
})

const measurements = ref<Record<string, number | null>>({
  chest: null,
  waist: null,
  hip: null,
  shoulder: null,
  sleeve: null,
  inseam: null,
  kameez_length: null,
})

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

// Calculate profile completeness score reactively
const completenessPercentage = computed(() => {
  let score = 0
  if (profile.value.display_name && profile.value.display_name.trim().length > 0) score += 10
  if (profile.value.gender_category) score += 10
  if (measurements.value.chest && measurements.value.chest > 0) score += 25
  if (measurements.value.waist && measurements.value.waist > 0) score += 20
  if (measurements.value.hip && measurements.value.hip > 0) score += 20
  if (measurements.value.shoulder && measurements.value.shoulder > 0) score += 15
  return Math.min(100, score)
})

// Load user data on mount
onMounted(async () => {
  if (!user.value) return
  const uid = user.value.id

  // 1. Profile
  const { data: prof } = await supabase.from('profiles').select('*').eq('user_id', uid).single()
  if (prof) {
    profile.value.display_name = prof.display_name || ''
    profile.value.preferred_unit = prof.preferred_unit || 'cm'
    profile.value.gender_category = prof.gender_category || 'womens'
  }

  // 2. Measurements
  const { data: bm } = await supabase.from('body_measurements').select('*').eq('user_id', uid).single()
  if (bm) {
    const unit = profile.value.preferred_unit
    measurements.value.chest = fromStorageCm(bm.chest_cm, unit)
    measurements.value.waist = fromStorageCm(bm.waist_cm, unit)
    measurements.value.hip = fromStorageCm(bm.hip_cm, unit)
    measurements.value.shoulder = fromStorageCm(bm.shoulder_cm, unit)
    measurements.value.sleeve = fromStorageCm(bm.sleeve_cm, unit)
    measurements.value.inseam = fromStorageCm(bm.inseam_cm, unit)
    measurements.value.kameez_length = fromStorageCm(bm.kameez_length_cm, unit)
  }

  // 3. Fit Preferences
  const { data: fps } = await supabase.from('fit_preferences').select('*').eq('user_id', uid)
  if (fps && fps.length > 0) {
    fps.forEach((r: any) => {
      fitPreferences.value[r.category] = r.fit
    })
  }

  // 4. Measurement Consent
  const { data: consentRow } = await supabase
    .from('consents')
    .select('granted')
    .eq('user_id', uid)
    .eq('consent_type', 'store_measurements')
    .single()
  if (consentRow) {
    hasMeasurementConsent.value = !!consentRow.granted
  }
})

async function handleConsentToggle() {
  if (hasMeasurementConsent.value) {
    const confirmed = window.confirm(
      t('profile.withdrawConsentConfirm') ||
      'Withdrawing consent will delete your stored body measurements and clear body snapshots from previous feedback. Continue?'
    )
    if (!confirmed) return

    try {
      await api.post('/v1/account/withdraw-consent')
      hasMeasurementConsent.value = false
      for (const k of Object.keys(measurements.value)) {
        measurements.value[k] = null
      }
      toast.success(t('profile.consentWithdrawnSuccess') || 'Measurement consent withdrawn')
    } catch (err: any) {
      toast.error(err.message || 'Failed to withdraw consent')
    }
  } else {
    try {
      if (!user.value) return
      await supabase.from('consents').upsert({
        user_id: user.value.id,
        consent_type: 'store_measurements',
        granted: true,
      }, { onConflict: 'user_id,consent_type' })
      hasMeasurementConsent.value = true
      toast.success(t('profile.consentGrantedSuccess') || 'Measurement consent enabled')
    } catch (err: any) {
      toast.error(err.message || 'Failed to update consent')
    }
  }
}

async function downloadMyData() {
  try {
    const res = await api.get<any>('/v1/account/export')
    const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `fitsense_data_export_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success(t('profile.exportSuccess') || 'Data export downloaded successfully')
  } catch (err: any) {
    toast.error(err.message || 'Failed to download data export')
  }
}

async function executeAccountDeletion() {
  isDeletingAccount.value = true
  try {
    await api.delete(`/v1/account?keep_anonymous_feedback=${keepAnonymousFeedback.value}`)
    await supabase.auth.signOut()
    toast.success(t('profile.accountDeletedSuccess') || 'Your account and data have been deleted')
    navigateTo('/')
  } catch (err: any) {
    toast.error(err.message || 'Failed to delete account')
  } finally {
    isDeletingAccount.value = false
    showDeleteModal.value = false
  }
}

function onUnitChange() {
  const isInch = profile.value.preferred_unit === 'in'
  for (const key of Object.keys(measurements.value)) {
    const val = measurements.value[key]
    if (val != null) {
      measurements.value[key] = isInch ? cmToInches(val) : inchesToCm(val)
    }
  }
}

async function saveProfile() {
  if (!user.value) return
  isSaving.value = true
  const uid = user.value.id

  try {
    // 1. Profile
    await supabase.from('profiles').upsert({
      user_id: uid,
      display_name: profile.value.display_name,
      preferred_unit: profile.value.preferred_unit,
      gender_category: profile.value.gender_category,
    }, { onConflict: 'user_id' })

    // 2. Measurements in cm
    const unit = profile.value.preferred_unit
    const toCm = (val: number | null) => (val != null ? toStorageCm(val, unit) : null)

    await supabase.from('body_measurements').upsert({
      user_id: uid,
      chest_cm: toCm(measurements.value.chest),
      waist_cm: toCm(measurements.value.waist),
      hip_cm: toCm(measurements.value.hip),
      shoulder_cm: toCm(measurements.value.shoulder),
      sleeve_cm: toCm(measurements.value.sleeve),
      inseam_cm: toCm(measurements.value.inseam),
      kameez_length_cm: toCm(measurements.value.kameez_length),
    }, { onConflict: 'user_id' })

    // 3. Fit Preferences
    const rows = Object.entries(fitPreferences.value).map(([cat, fit]) => ({
      user_id: uid,
      category: cat,
      fit,
    }))
    await supabase.from('fit_preferences').upsert(rows, { onConflict: 'user_id,category' })

    toast.success(t('profile.savedSuccess') || 'Profile and measurements saved successfully!')
  } catch (err: any) {
    toast.error(err.message || 'Failed to save changes')
  } finally {
    isSaving.value = false
  }
}
</script>
