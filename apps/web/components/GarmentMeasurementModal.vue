<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" @click="close"></div>

    <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
      <div
        class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg p-6 space-y-6"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b pb-4">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">{{ $t('onboarding.garmentModalTitle') }}</h3>
              <p class="text-xs text-gray-500">{{ $t('onboarding.garmentModalDesc') }}</p>
            </div>
          </div>
          <button type="button" class="text-gray-400 hover:text-gray-600 focus:outline-none" @click="close">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Garment Category Selector -->
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">Garment Type</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="cat in categories"
              :key="cat.value"
              type="button"
              class="py-2.5 px-3 text-xs font-medium rounded-xl border text-center transition"
              :class="garmentCategory === cat.value ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
              @click="garmentCategory = cat.value"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <!-- Flat Input Fields -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              {{ $t('onboarding.flatChest') }} ({{ unit }})
            </label>
            <input
              v-model.number="flatChest"
              type="number"
              step="0.5"
              placeholder="e.g. 52"
              class="w-full rounded-xl border border-gray-300 py-2 px-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              {{ $t('onboarding.garmentShoulder') }} ({{ unit }})
            </label>
            <input
              v-model.number="shoulder"
              type="number"
              step="0.5"
              placeholder="e.g. 44"
              class="w-full rounded-xl border border-gray-300 py-2 px-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              {{ $t('onboarding.garmentLength') }} ({{ unit }})
            </label>
            <input
              v-model.number="length"
              type="number"
              step="0.5"
              placeholder="e.g. 70"
              class="w-full rounded-xl border border-gray-300 py-2 px-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
            />
          </div>

          <div v-if="garmentCategory === 'trouser' || garmentCategory === 'jeans'">
            <label class="block text-xs font-semibold text-gray-700 mb-1">
              {{ $t('onboarding.flatWaist') }} ({{ unit }})
            </label>
            <input
              v-model.number="flatWaist"
              type="number"
              step="0.5"
              placeholder="e.g. 40"
              class="w-full rounded-xl border border-gray-300 py-2 px-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t">
          <button
            type="button"
            class="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-xl transition"
            @click="close"
          >
            {{ $t('common.cancel') }}
          </button>
          <button
            type="button"
            class="px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition shadow-md shadow-indigo-200"
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
  // Convert from display unit to cm if needed before computing estimate
  const toCm = (val: number | null) => (val && props.unit === 'in' ? inchesToCm(val) : val)

  const estimates = estimateBodyFromGarment({
    category: garmentCategory.value,
    flat_chest_cm: toCm(flatChest.value),
    shoulder_cm: toCm(shoulder.value),
    length_cm: toCm(length.value),
    flat_waist_cm: toCm(flatWaist.value),
  })

  emit('applied', estimates)
  close()
}
</script>

