<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:py-12 space-y-8">
    <!-- Header Hero Title -->
    <div class="text-center max-w-2xl mx-auto space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-bold uppercase tracking-wider">
        <span>🇵🇰 Universal Size Intelligence</span>
      </div>
      <h1 class="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
        Universal Size Finder
      </h1>
      <p class="text-sm sm:text-base text-slate-300 leading-relaxed">
        Select any verified Pakistani brand and clothing item to discover your ideal size computed by our deterministic rules engine.
      </p>
    </div>

    <!-- Product Selection Card (High-Contrast Obsidian Luxury Card) -->
    <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-10 rounded-3xl shadow-2xl border border-slate-800 space-y-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <!-- Retailer Select -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
            1. Select Pakistani Brand <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <select
              v-model="selectedRetailerSlug"
              style="color-scheme: dark;"
              class="w-full rounded-2xl border border-slate-700 bg-slate-800 text-white font-bold py-3.5 px-4 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 transition shadow-inner appearance-none cursor-pointer"
              @change="onRetailerChange"
            >
              <option value="" disabled class="bg-slate-900 text-slate-400">Choose a brand...</option>
              <option
                v-for="ret in retailers"
                :key="ret.id"
                :value="ret.slug"
                class="bg-slate-900 text-white py-2 font-semibold"
              >
                {{ ret.name }}
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
              ▼
            </div>
          </div>
        </div>

        <!-- Product Select with Search Filter -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
            2. Select Clothing Item <span class="text-rose-500">*</span>
          </label>
          <div class="relative">
            <select
              v-model="selectedProductId"
              style="color-scheme: dark;"
              :disabled="!selectedRetailerSlug || isLoadingProducts"
              class="w-full rounded-2xl border border-slate-700 bg-slate-800 text-white font-bold py-3.5 px-4 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 transition shadow-inner disabled:opacity-40 appearance-none cursor-pointer"
            >
              <option value="" disabled class="bg-slate-900 text-slate-400">
                {{ isLoadingProducts ? 'Loading brand catalog...' : 'Choose a product...' }}
              </option>
              <option
                v-for="prod in products"
                :key="prod.id"
                :value="prod.id"
                class="bg-slate-900 text-white py-2 font-semibold"
              >
                {{ prod.name }} ({{ prod.category.toUpperCase() }})
              </option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
              ▼
            </div>
          </div>
        </div>
      </div>

      <!-- Measurements Section (Always accessible for guaranteed high confidence recommendations) -->
      <div class="p-6 bg-slate-800/60 border border-slate-700/80 rounded-2xl space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 text-sm font-bold">
              📐
            </div>
            <div>
              <div class="flex items-center gap-2">
                <p class="text-xs text-white font-bold">
                  {{ user ? 'Active Body Measurements' : 'Guest Fitting Measurements' }}
                </p>
                <span
                  v-if="user && hasLoadedSavedProfile"
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30"
                >
                  ✓ Synced with Profile
                </span>
                <span
                  v-else-if="user"
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-400/30"
                >
                  Not saved in profile yet
                </span>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5">
                Exact measurements ensure our rules engine calculates recommendations with 90%+ confidence.
              </p>
            </div>
          </div>

          <!-- Unit toggle & 1-click Save to Profile button -->
          <div class="flex items-center gap-2">
            <button
              v-if="user && !hasLoadedSavedProfile"
              type="button"
              @click="saveMeasurementsToProfile"
              :disabled="isSavingToProfile || !measurements.chest"
              class="px-3 py-1.5 rounded-xl bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-sm disabled:opacity-40"
            >
              <span>💾</span>
              <span>{{ isSavingToProfile ? 'Saving...' : 'Save to Profile' }}</span>
            </button>
            <div class="flex items-center bg-slate-900 rounded-xl p-1 border border-slate-700 text-xs font-bold">
              <button
                type="button"
                @click="switchUnit('cm')"
                class="px-2.5 py-1 rounded-lg transition"
                :class="activeUnit === 'cm' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'"
              >
                CM
              </button>
              <button
                type="button"
                @click="switchUnit('in')"
                class="px-2.5 py-1 rounded-lg transition"
                :class="activeUnit === 'in' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'"
              >
                IN
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
          <MeasurementInput
            v-model="measurements.chest"
            field-key="chest"
            :label="$t('measurements.chest')"
            :unit="activeUnit"
            required
            :tip="$t('measurements.tips.chest')"
          />
          <MeasurementInput
            v-model="measurements.waist"
            field-key="waist"
            :label="$t('measurements.waist')"
            :unit="activeUnit"
            :tip="$t('measurements.tips.waist')"
          />
          <MeasurementInput
            v-model="measurements.hip"
            field-key="hip"
            :label="$t('measurements.hip')"
            :unit="activeUnit"
            :tip="$t('measurements.tips.hip')"
          />
        </div>
      </div>

      <!-- Calculate Size Button -->
      <div class="pt-2">
        <button
          type="button"
          :disabled="!selectedProductId || isComputing"
          class="w-full py-4 px-6 rounded-2xl font-black text-base text-white bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition-all shadow-xl shadow-indigo-600/30 hover:scale-[1.01] active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-3"
          @click="calculateSize"
        >
          <span v-if="isComputing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
          <span v-if="isComputing">{{ $t('common.loading') }}</span>
          <span v-else class="flex items-center gap-2">
            <span>🎯</span>
            <span>{{ $t('try.findSizeBtn') }}</span>
          </span>
        </button>
      </div>
    </div>

    <!-- Size Result Presentation -->
    <div v-if="recommendationData" class="animate-fadeIn">
      <SizeResultCard
        :result="recommendationData.recommendation"
        :explanation="recommendationData.explanation"
        :product-url="activeProductUrl"
        :unit="activeUnit"
        @save-size="handleSaveSize"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toStorageCm, fromStorageCm, cmToInches, inchesToCm } from '~/utils/units'

const api = useApi()
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const toast = useToast()
const { locale, t } = useI18n()
const localePath = useLocalePath()

const route = useRoute()
const retailers = ref<any[]>([])
const products = ref<any[]>([])
const selectedRetailerSlug = ref('')
const selectedProductId = ref('')
const isLoadingProducts = ref(false)
const isComputing = ref(false)
const isSavingToProfile = ref(false)
const hasLoadedSavedProfile = ref(false)
const recommendationData = ref<any>(null)

const activeUnit = ref<'cm' | 'in'>('cm')

const measurements = ref<Record<string, number | null>>({
  chest: 100,
  waist: 85,
  hip: 105,
})

const activeProductUrl = computed(() => {
  const p = products.value.find((item) => item.id === selectedProductId.value)
  return p?.product_url || ''
})

onMounted(async () => {
  try {
    retailers.value = await api.get<any[]>('/v1/retailers')
    const queryRetailer = String(route.query.retailer || '').trim().toLowerCase()
    const match = retailers.value.find((r) => r.slug === queryRetailer)
    if (match) {
      selectedRetailerSlug.value = match.slug
    } else if (retailers.value.length > 0) {
      selectedRetailerSlug.value = retailers.value[0].slug
    }
    if (selectedRetailerSlug.value) {
      await loadProducts(selectedRetailerSlug.value)
    }
  } catch (err: any) {
    console.error('Failed to load retailers', err)
  }

  // If user is logged in, load unit preference and body measurements
  if (user.value) {
    const uid = user.value.id
    try {
      const { data: prof } = await supabase
        .from('profiles')
        .select('preferred_unit')
        .eq('user_id', uid)
        .single()
      if (prof?.preferred_unit) {
        activeUnit.value = prof.preferred_unit
      }

      const { data: bm } = await supabase
        .from('body_measurements')
        .select('*')
        .eq('user_id', uid)
        .single()
      if (bm && (bm.chest_cm || bm.waist_cm || bm.hip_cm)) {
        hasLoadedSavedProfile.value = true
        if (bm.chest_cm) measurements.value.chest = fromStorageCm(bm.chest_cm, activeUnit.value)
        if (bm.waist_cm) measurements.value.waist = fromStorageCm(bm.waist_cm, activeUnit.value)
        if (bm.hip_cm) measurements.value.hip = fromStorageCm(bm.hip_cm, activeUnit.value)
      }
    } catch (e) {
      console.warn('Could not load user measurements', e)
    }
  }
})

function switchUnit(newUnit: 'cm' | 'in') {
  if (activeUnit.value === newUnit) return
  activeUnit.value = newUnit
  for (const k of ['chest', 'waist', 'hip']) {
    const val = measurements.value[k]
    if (val != null) {
      measurements.value[k] = newUnit === 'in' ? cmToInches(val) : inchesToCm(val)
    }
  }
}

async function saveMeasurementsToProfile() {
  if (!user.value) return
  isSavingToProfile.value = true
  const uid = user.value.id
  const unit = activeUnit.value
  const toCm = (val: number | null) => (val != null ? toStorageCm(val, unit) : null)

  try {
    await supabase.from('body_measurements').upsert({
      user_id: uid,
      chest_cm: toCm(measurements.value.chest),
      waist_cm: toCm(measurements.value.waist),
      hip_cm: toCm(measurements.value.hip),
    }, { onConflict: 'user_id' })
    hasLoadedSavedProfile.value = true
    toast.success('Measurements saved to your profile!')
  } catch (err: any) {
    toast.error(err.message || 'Failed to save measurements')
  } finally {
    isSavingToProfile.value = false
  }
}

async function onRetailerChange() {
  selectedProductId.value = ''
  recommendationData.value = null
  if (selectedRetailerSlug.value) {
    await loadProducts(selectedRetailerSlug.value)
  }
}

async function loadProducts(slug: string) {
  isLoadingProducts.value = true
  try {
    const res = await api.get<any[]>(`/v1/retailers/${slug}/products`)
    products.value = res || []
    if (products.value.length > 0) {
      selectedProductId.value = products.value[0].id
    }
  } catch {
    products.value = []
  } finally {
    isLoadingProducts.value = false
  }
}

async function calculateSize() {
  if (!selectedProductId.value) return
  isComputing.value = true
  recommendationData.value = null

  try {
    const toCm = (val: number | null) => (val != null ? toStorageCm(val, activeUnit.value) : null)

    // Always attach exact body measurements for deterministic precision
    const payload: any = {
      product_id: selectedProductId.value,
      measurements: {
        chest_cm: toCm(measurements.value.chest),
        waist_cm: toCm(measurements.value.waist),
        hip_cm: toCm(measurements.value.hip),
      },
    }

    const res = await api.post<any>('/v1/recommend', payload, {
      lang: locale.value,
    })
    recommendationData.value = res
  } catch (err: any) {
    toast.error(err.message || 'Failed to calculate size')
  } finally {
    isComputing.value = false
  }
}

async function handleSaveSize() {
  if (!user.value) {
    toast.info('Please log in to save your sizes')
    navigateTo(localePath('/login'))
    return
  }

  try {
    await supabase.from('saved_items').insert({
      user_id: user.value.id,
      product_id: selectedProductId.value,
      size_label: recommendationData.value?.recommendation?.recommended_size || 'M',
      status: 'saved',
    })
    toast.success(t('try.savedSizeSuccess'))
  } catch (err: any) {
    toast.error(err.message || 'Failed to save item')
  }
}
</script>