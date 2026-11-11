<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity" @click="close"></div>

    <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
      <div
        class="relative transform overflow-hidden rounded-3xl bg-slate-900 border border-slate-800 text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg p-6 sm:p-8 space-y-6 text-white"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-slate-800 pb-4">
          <div class="flex items-center gap-3">
            <div class="p-2.5 bg-indigo-500/20 border border-indigo-400/30 text-indigo-400 rounded-2xl">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-black text-white">{{ $t('onboarding.garmentModalTitle') }}</h3>
              <p class="text-xs text-slate-400 mt-0.5">{{ $t('onboarding.garmentModalDesc') }}</p>
            </div>
          </div>
          <button type="button" class="text-slate-400 hover:text-white transition focus:outline-none" @click="close">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Garment Category Selector -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">Garment Type</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="cat in categories"
              :key="cat.value"
              type="button"
              class="py-2.5 px-3 text-xs font-bold rounded-xl border text-center transition"
              :class="garmentCategory === cat.value ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30' : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'"
              @click="garmentCategory = cat.value"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <!-- Flat Input Fields -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">
              {{ $t('onboarding.flatChest') }} ({{ unit }})
            </label>
            <input
              v-model.number="flatChest"
              type="number"
              step="0.5"
              placeholder="e.g. 52"
              style="color-scheme: dark;"
              class="w-full rounded-xl border border-slate-700 bg-slate-800/95 py-2.5 px-3 text-sm text-white font-bold focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-inner"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">
              {{ $t('onboarding.garmentShoulder') }} ({{ unit }})
            </label>
            <input
              v-model.number="shoulder"
              type="number"
              step="0.5"
              placeholder="e.g. 44"
              style="color-scheme: dark;"
              class="w-full rounded-xl border border-slate-700 bg-slate-800/95 py-2.5 px-3 text-sm text-white font-bold focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-inner"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">
              {{ $t('onboarding.garmentLength') }} ({{ unit }})
            </label>
            <input
              v-model.number="length"
              type="number"
              step="0.5"
              placeholder="e.g. 70"
              style="color-scheme: dark;"
              class="w-full rounded-xl border border-slate-700 bg-slate-800/95 py-2.5 px-3 text-sm text-white font-bold focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-inner"
            />
          </div>

          <div v-if="garmentCategory === 'trouser' || garmentCategory === 'jeans'">
            <label class="block text-xs font-bold text-slate-300 mb-1">
              {{ $t('onboarding.flatWaist') }} ({{ unit }})
            </label>
            <input
              v-model.number="flatWaist"
              type="number"
              step="0.5"
              placeholder="e.g. 40"
              style="color-scheme: dark;"
              class="w-full rounded-xl border border-slate-700 bg-slate-800/95 py-2.5 px-3 text-sm text-white font-bold focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 shadow-inner"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            type="button"
            class="px-4 py-2 text-xs font-bold text-slate-400 hover:text-white rounded-xl transition"
            @click="close"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            type="button"
            class="px-5 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition shadow-lg shadow-indigo-600/30"
            @click="applyEstimate"
          >
            {{ $t('onboarding.calculateEstimateBtn') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { estimateBodyFromGarment, type EstimatedBodyMeasurements } from '~/utils/garmentEstimator'
import { inchesToCm, cmToInches } from '~/utils/units'

const props = defineProps<{
  isOpen: boolean
  unit: 'cm' | 'in'
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'applied', estimates: EstimatedBodyMeasurements): void
}>()

const garmentCategory = ref<'tshirt_top' | 'shirt' | 'kurta' | 'trouser' | 'jeans'>('tshirt_top')
const flatChest = ref<number | null>(null)
const shoulder = ref<number | null>(null)
const length = ref<number | null>(null)
const flatWaist = ref<number | null>(null)

const categories = [
  { value: 'tshirt_top', label: 'T-Shirt / Top' },
  { value: 'shirt', label: 'Shirt' },
  { value: 'kurta', label: 'Kurta' },
  { value: 'trouser', label: 'Trouser' },
  { value: 'jeans', label: 'Jeans' },
] as const

function close() {
  emit('close')
}

function applyEstimate() {
  if (!flatChest.value) return

  const toCm = (val: number | null) => {
    if (val == null) return undefined
    return props.unit === 'in' ? inchesToCm(val) : val
  }

  const rawEstimates = estimateBodyFromGarment({
    category: garmentCategory.value,
    flatChestWidthCm: toCm(flatChest.value)!,
    garmentLengthCm: toCm(length.value),
    shoulderWidthCm: toCm(shoulder.value),
    flatWaistWidthCm: toCm(flatWaist.value),
  })

  emit('applied', rawEstimates)
  close()
}
</script>
