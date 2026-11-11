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
        One-time profile building: enter your measurements once, and instantly get your guaranteed size across Khaadi, Sapphire, Outfitters, and all top Pakistani brands.
      </p>
    </div>

    <!-- Product Selection & Universal Profile Card (High-Contrast Obsidian Luxury Card) -->
    <div class="bg-slate-900/90 backdrop-blur-xl p-6 sm:p-10 rounded-3xl shadow-2xl border border-slate-800 space-y-8">
      
      <!-- 1-Time Universal Sizing Profile Section -->
      <div class="p-6 bg-slate-800/70 border border-slate-700/80 rounded-2xl space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/30 to-purple-500/30 border border-indigo-400/40 text-indigo-300 flex items-center justify-center shrink-0 text-lg font-bold shadow-sm">
              ✨
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <p class="text-sm text-white font-extrabold tracking-wide">
                  Universal Customer Fit Profile
                </p>
                <span
                  v-if="hasProfile"
                  class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 flex items-center gap-1 shadow-sm"
                >
                  <span>✓</span> Active & Reusable
                </span>
                <span
                  v-else
                  class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-400/30"
                >
                  1-Time Setup
                </span>
              </div>
              <p class="text-xs text-slate-300 mt-1">
                Your body measurements are remembered across all shops. Height, chest, and shoulder dimensions predict exact fit with 95%+ confidence.
              </p>
            </div>
          </div>

          <!-- Unit Switcher & Quick Actions -->
          <div class="flex items-center gap-2 self-start sm:self-auto shrink-0">
            <button
              type="button"
              @click="showMeasurementEditor = !showMeasurementEditor"
              class="px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 transition flex items-center gap-1.5"
            >
              <span>{{ showMeasurementEditor ? '▲ Collapse' : '✏️ Adjust' }}</span>
            </button>

            <div class="flex items-center bg-slate-900 rounded-xl p-1 border border-slate-700 text-xs font-bold">
              <button
                type="button"
                @click="setUnit('cm')"
                class="px-2.5 py-1 rounded-lg transition"
                :class="profileState.unit === 'cm' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'"
              >
                CM
              </button>
              <button
                type="button"
                @click="setUnit('in')"
                class="px-2.5 py-1 rounded-lg transition"
                :class="profileState.unit === 'in' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'"
              >
                IN
              </button>
            </div>
          </div>
        </div>

        <!-- Sleek Profile Pill Summary (Visible when collapsed or active) -->
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2.5 pt-1 text-xs">
          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Chest / Bust</span>
            <span class="font-extrabold text-white text-sm mt-0.5">
              {{ profileState.chest ? `${profileState.chest} ${profileState.unit}` : '—' }}
            </span>
          </div>

          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Height</span>
            <span class="font-extrabold text-indigo-300 text-sm mt-0.5">
              {{ profileState.height ? `${profileState.height} ${profileState.unit}` : '—' }}
            </span>
          </div>

          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Shoulder</span>
            <span class="font-extrabold text-indigo-300 text-sm mt-0.5">
              {{ profileState.shoulder ? `${profileState.shoulder} ${profileState.unit}` : '—' }}
            </span>
          </div>

          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Waist</span>
            <span class="font-extrabold text-white text-sm mt-0.5">
              {{ profileState.waist ? `${profileState.waist} ${profileState.unit}` : '—' }}
            </span>
          </div>

          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Hips</span>
            <span class="font-extrabold text-white text-sm mt-0.5">
              {{ profileState.hip ? `${profileState.hip} ${profileState.unit}` : '—' }}
            </span>
          </div>

          <div class="bg-slate-900/80 border border-slate-700/60 rounded-xl px-3 py-2 flex flex-col">
            <span class="text-[10px] uppercase font-bold text-slate-400">Sleeve</span>
            <span class="font-extrabold text-white text-sm mt-0.5">
              {{ profileState.sleeve ? `${profileState.sleeve} ${profileState.unit}` : '—' }}
            </span>
          </div>
        </div>

        <!-- Full Measurement Inputs Drawer (Expandable for editing) -->
        <div v-show="showMeasurementEditor" class="space-y-5 pt-3 border-t border-slate-700/60 animate-fadeIn">
          
          <!-- Smart Auto-Estimation Banner -->
          <div class="p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-800/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <div class="flex items-center gap-2.5">
              <span class="text-lg">💡</span>
              <p class="text-indigo-200 leading-snug">
                <strong>Don't have all your measurements?</strong> Enter your <strong>Height</strong> & <strong>Chest</strong>, and click auto-estimate to calculate accurate shoulder, sleeve, and length proportions!
              </p>
            </div>
            <button
              type="button"
              @click="autoEstimateFromHeight"
              class="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition shrink-0 flex items-center gap-1.5 shadow-sm"
            >
              <span>✨</span>
              <span>Auto-Estimate from Height</span>
            </button>
          </div>

          <!-- Section A: Primary Dimensions -->
          <div>
            <h4 class="text-[11px] uppercase tracking-wider font-extrabold text-indigo-400 mb-2.5">
              Primary Dimensions (Crucial for Tops, Kurtas & Dresses)
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <MeasurementInput
                v-model="profileState.chest"
                field-key="chest"
                :label="$t('measurements.chest')"
                :unit="profileState.unit"
                required
                :tip="$t('measurements.tips.chest')"
              />
              <MeasurementInput
                v-model="profileState.height"
                field-key="height"
                :label="$t('measurements.height')"
                :unit="profileState.unit"
                required
                :tip="$t('measurements.tips.height')"
              />
              <MeasurementInput
                v-model="profileState.waist"
                field-key="waist"
                :label="$t('measurements.waist')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.waist')"
              />
              <MeasurementInput
                v-model="profileState.hip"
                field-key="hip"
                :label="$t('measurements.hip')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.hip')"
              />
            </div>
          </div>

          <!-- Section B: Proportions & Sizing Details -->
          <div>
            <h4 class="text-[11px] uppercase tracking-wider font-extrabold text-indigo-400 mb-2.5">
              Proportions & Sizing Details (Eliminates Fit Warnings)
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <MeasurementInput
                v-model="profileState.shoulder"
                field-key="shoulder"
                :label="$t('measurements.shoulder')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.shoulder')"
              />
              <MeasurementInput
                v-model="profileState.sleeve"
                field-key="sleeve"
                :label="$t('measurements.sleeve')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.sleeve')"
              />
              <MeasurementInput
                v-model="profileState.inseam"
                field-key="inseam"
                :label="$t('measurements.inseam')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.inseam')"
              />
              <MeasurementInput
                v-model="profileState.kameez_length"
                field-key="kameez_length"
                :label="$t('measurements.kameez_length')"
                :unit="profileState.unit"
                :tip="$t('measurements.tips.kameez_length')"
              />
            </div>
          </div>

          <!-- Save to Profile Button -->
          <div class="flex justify-end pt-2">
            <button
              type="button"
              @click="handleSaveProfile"
              :disabled="isSaving || !profileState.chest"
              class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs transition shadow-md flex items-center gap-2 disabled:opacity-40"
            >
              <span>💾</span>
              <span>{{ isSaving ? 'Saving Profile...' : 'Save & Lock Universal Profile' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Retailer & Product Selection -->
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

      <!-- 1-Click Calculate Size Button -->
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
            <span>{{ selectedRetailerName ? `Recommend My Size in ${selectedRetailerName}` : $t('try.findSizeBtn') }}</span>
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
        :unit="profileState.unit"
        @save-size="handleSaveSize"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFitProfile } from '~/composables/useFitProfile'

const api = useApi()
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const toast = useToast()
const { locale, t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()

// Initialize central cross-store Fit Profile
const {
  profileState,
  hasProfile,
  isSaving,
  loadProfile,
  saveProfile,
  setUnit,
  autoEstimateFromHeight,
  toApiPayload,
} = useFitProfile()

const showMeasurementEditor = ref(false)
const retailers = ref<any[]>([])
const products = ref<any[]>([])
const selectedRetailerSlug = ref('')
const selectedProductId = ref('')
const isLoadingProducts = ref(false)
const isComputing = ref(false)
const recommendationData = ref<any>(null)

const selectedRetailerName = computed(() => {
  const match = retailers.value.find((r) => r.slug === selectedRetailerSlug.value)
  return match?.name || ''
})

const activeProductUrl = computed(() => {
  const p = products.value.find((item) => item.id === selectedProductId.value)
  return p?.product_url || ''
})

onMounted(async () => {
  // Load unified universal profile (from localStorage and/or Supabase)
  await loadProfile()

  // If no measurements entered yet, open editor by default so user can set it up once
  if (!profileState.value.chest) {
    showMeasurementEditor.value = true
  }

  // Load Retailers Catalog
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
      
      // If autocalculate requested via 1-click brand button, run immediately!
      if (route.query.autocalculate === 'true' && selectedProductId.value) {
        await calculateSize()
      }
    }
  } catch (err: any) {
    console.error('Failed to load retailers', err)
  }
})

async function handleSaveProfile() {
  await saveProfile()
  showMeasurementEditor.value = false
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
    const selectedProd = products.value.find((p) => p.id === selectedProductId.value)
    
    // Always attach complete body measurements (chest, waist, hip, shoulder, sleeve, height)
    const payload: any = {
      product_id: selectedProductId.value,
      measurements: toApiPayload(selectedProd?.category),
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
