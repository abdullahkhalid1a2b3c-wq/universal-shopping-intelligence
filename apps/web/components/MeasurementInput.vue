<template>
  <div class="space-y-1.5">
    <div class="flex items-center justify-between">
      <label :for="fieldId" class="block text-xs font-bold uppercase tracking-wider text-slate-200">
        {{ label }}
        <span v-if="required" class="text-rose-400 text-xs ml-0.5">*</span>
      </label>

      <!-- How to measure tip toggle -->
      <button
        type="button"
        class="inline-flex items-center text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition focus:outline-none"
        @click="showTip = !showTip"
      >
        <svg class="w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ showTip ? $t('common.close') : 'How to measure' }}</span>
      </button>
    </div>

    <!-- Illustrated Tip Drawer -->
    <div
      v-if="showTip"
      class="p-3.5 bg-indigo-950/90 border border-indigo-800/80 rounded-2xl text-xs text-indigo-200 space-y-2 animate-fadeIn shadow-lg"
    >
      <div class="flex items-start gap-3">
        <!-- Anatomical SVG Measurement Diagram -->
        <svg class="w-12 h-12 text-indigo-600 dark:text-indigo-400 shrink-0" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2">
          <!-- Torso outline -->
          <circle cx="32" cy="10" r="6" />
          <path d="M22 20h20l4 18h-8v22h-12v-22h-8l4-18z" />
          <!-- Measurement indicator line based on fieldKey -->
          <g v-if="fieldKey === 'chest'" stroke="#e11d48" stroke-width="2.5" stroke-dasharray="2 2">
            <line x1="20" y1="26" x2="44" y2="26" />
          </g>
          <g v-else-if="fieldKey === 'waist'" stroke="#e11d48" stroke-width="2.5" stroke-dasharray="2 2">
            <line x1="24" y1="34" x2="40" y2="34" />
          </g>
          <g v-else-if="fieldKey === 'hip'" stroke="#e11d48" stroke-width="2.5" stroke-dasharray="2 2">
            <line x1="22" y1="40" x2="42" y2="40" />
          </g>
          <g v-else-if="fieldKey === 'shoulder'" stroke="#e11d48" stroke-width="2.5">
            <line x1="20" y1="20" x2="44" y2="20" />
          </g>
          <g v-else-if="fieldKey === 'inseam'" stroke="#e11d48" stroke-width="2.5">
            <line x1="30" y1="42" x2="30" y2="60" />
          </g>
          <g v-else-if="fieldKey === 'height'" stroke="#e11d48" stroke-width="2.5">
            <line x1="14" y1="4" x2="14" y2="60" />
            <line x1="10" y1="4" x2="18" y2="4" />
            <line x1="10" y1="60" x2="18" y2="60" />
          </g>
          <g v-else stroke="#e11d48" stroke-width="2.5">
            <line x1="20" y1="20" x2="20" y2="52" />
          </g>
        </svg>
        <p class="leading-relaxed pt-1 text-slate-700 dark:text-slate-300">{{ tip }}</p>
      </div>
    </div>

    <!-- Input Field -->
    <div class="relative rounded-2xl shadow-sm">
      <input
        :id="fieldId"
        type="number"
        step="0.5"
        :min="bounds?.minDisplay"
        :max="bounds?.maxDisplay"
        :value="modelValue ?? ''"
        :placeholder="placeholder"
        style="color-scheme: dark;"
        class="block w-full rounded-2xl border border-slate-700 bg-slate-800/95 py-3 px-4 pr-12 text-white font-black placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 text-sm transition shadow-inner"
        :class="{ 'border-rose-400 focus:border-rose-500 focus:ring-rose-500': isOutOfRange }"
        @input="onInput"
      />
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3.5">
        <span class="text-xs font-black uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">{{ unit }}</span>
      </div>
    </div>

    <!-- Validation notice -->
    <p v-if="isOutOfRange" class="text-xs text-rose-500 font-semibold">
      Expected range: {{ bounds?.minDisplay }} - {{ bounds?.maxDisplay }} {{ unit }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { MEASUREMENT_BOUNDS, cmToInches } from '~/utils/units'

const props = defineProps<{
  fieldKey: string
  label: string
  modelValue: number | null
  unit: 'cm' | 'in'
  required?: boolean
  tip?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [val: number | null]
}>()

const showTip = ref(false)
const fieldId = computed(() => `field-${props.fieldKey}`)

const bounds = computed(() => {
  const b = MEASUREMENT_BOUNDS[props.fieldKey]
  if (!b) return null
  return {
    minDisplay: props.unit === 'in' ? cmToInches(b.min) : b.min,
    maxDisplay: props.unit === 'in' ? cmToInches(b.max) : b.max,
  }
})

const placeholder = computed(() => {
  if (!bounds.value) return '0'
  const mid = Math.round((bounds.value.minDisplay + bounds.value.maxDisplay) / 2)
  return `${mid}`
})

const isOutOfRange = computed(() => {
  if (props.modelValue == null || !bounds.value) return false
  return props.modelValue < bounds.value.minDisplay || props.modelValue > bounds.value.maxDisplay
})

function onInput(e: Event) {
  const target = e.target as HTMLInputElement
  const val = target.value ? parseFloat(target.value) : null
  emit('update:modelValue', val)
}
</script>
