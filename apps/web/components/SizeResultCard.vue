<template>
  <div class="bg-slate-900 rounded-3xl shadow-2xl border border-slate-800 overflow-hidden transition">
    <!-- Top Result Header -->
    <div class="bg-gradient-to-br from-indigo-950 via-slate-900 to-purple-950 p-6 sm:p-8 text-white relative border-b border-slate-800">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span class="text-xs uppercase tracking-widest font-bold text-indigo-400">
            {{ $t('try.recommendedSize') }}
          </span>
          <h2 class="text-5xl sm:text-6xl font-black tracking-tight text-white mt-1">
            {{ result.recommended_size }}
          </h2>
        </div>

        <!-- Confidence Badge -->
        <div class="flex flex-col items-start sm:items-end">
          <span class="text-xs text-slate-400 mb-1 font-semibold uppercase tracking-wider">{{ $t('try.confidence') }}</span>
          <div
            class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black uppercase tracking-wider shadow-inner"
            :class="confidenceBadgeClasses"
          >
            <span class="w-2.5 h-2.5 rounded-full" :class="confidenceDotClasses"></span>
            <span>{{ result.confidence_label }} ({{ result.confidence_score }}%)</span>
          </div>
        </div>
      </div>

      <!-- Localized Explanation Sentence -->
      <div class="mt-6 pt-5 border-t border-slate-800/80 text-slate-200 text-sm sm:text-base leading-relaxed font-semibold">
        {{ explanation }}
      </div>
    </div>

    <!-- Peer Feedback Summary Banner (k-anonymity >= 5 similar chest) -->
    <div
      v-if="feedbackSummary?.has_summary && feedbackSummary.summary_text"
      class="bg-indigo-950/40 border-b border-indigo-900/60 px-6 py-3.5 flex items-center gap-3 text-xs text-indigo-200 font-medium"
    >
      <div class="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <span>{{ feedbackSummary.summary_text }}</span>
    </div>

    <!-- Warnings Banner -->
    <div v-if="result.warnings && result.warnings.length > 0" class="bg-amber-950/40 border-b border-amber-900/50 p-4 space-y-1.5">
      <div v-for="warning in formattedWarnings" :key="warning" class="flex items-center gap-2 text-xs font-bold text-amber-300">
        <svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{{ warning }}</span>
      </div>
    </div>

    <!-- Body Content -->
    <div class="p-6 sm:p-8 space-y-6">
      <!-- Alternative Size Card -->
      <div
        v-if="result.alternative_size"
        class="flex items-center justify-between p-4 bg-slate-800/80 rounded-2xl border border-slate-700 shadow-inner"
      >
        <div>
          <span class="text-xs font-black uppercase text-indigo-400 tracking-wider">
            {{ $t('try.alternative') }}
          </span>
          <p class="text-base font-black text-white mt-0.5">
            Size {{ result.alternative_size.size_label }}
          </p>
          <p class="text-xs text-slate-300 mt-0.5">{{ result.alternative_size.reason }}</p>
        </div>
      </div>

      <!-- Expandable "Why this size?" Section -->
      <div class="border rounded-2xl overflow-hidden border-slate-800 bg-slate-800/40">
        <button
          type="button"
          class="w-full flex items-center justify-between p-4 bg-slate-800/80 hover:bg-slate-800 transition text-left focus:outline-none"
          @click="isExpanded = !isExpanded"
        >
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="text-sm font-black text-white">{{ $t('try.whySection') }}</span>
          </div>
          <svg
            class="w-4 h-4 text-slate-400 transform transition-transform"
            :class="{ 'rotate-180': isExpanded }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <div v-if="isExpanded" class="p-4 divide-y divide-slate-800 space-y-4">
          <div
            v-for="dim in result.per_dimension"
            :key="dim.dimension"
            class="pt-3 first:pt-0 space-y-2.5"
          >
            <div class="flex items-center justify-between">
              <span class="text-sm font-bold capitalize text-white">{{ dim.dimension }}</span>
              <span
                class="px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider shadow-sm"
                :class="verdictBadgeClasses(dim.verdict)"
              >
                {{ $t(`try.verdict.${dim.verdict}`) }}
              </span>
            </div>

            <!-- Metric Breakdown -->
            <div class="grid grid-cols-4 text-center text-xs text-slate-300 bg-slate-900/90 p-3 rounded-xl border border-slate-800">
              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-bold">{{ $t('try.bodyLabel') }}</span>
                <span class="font-black text-white text-xs mt-0.5 block">{{ formatVal(dim.body_cm) }} {{ unit }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-bold">{{ $t('try.garmentLabel') }}</span>
                <span class="font-black text-white text-xs mt-0.5 block">{{ formatVal(dim.garment_cm) }} {{ unit }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-bold">{{ $t('try.easeLabel') }}</span>
                <span class="font-black text-indigo-400 text-xs mt-0.5 block">{{ formatEase(dim.ease_cm) }} {{ unit }}</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px] uppercase font-bold">{{ $t('try.targetBand') }}</span>
                <span class="font-black text-slate-200 text-xs mt-0.5 block">
                  {{ formatVal(dim.target_band[0]) }} - {{ formatVal(dim.target_band[1]) }}
                </span>
              </div>
            </div>

            <!-- Visual Horizontal Ease Bar -->
            <div class="space-y-1">
              <div class="relative w-full h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-700">
                <!-- Target Band Zone (Middle) -->
                <div class="absolute inset-y-0 left-1/4 right-1/4 bg-emerald-500/20 border-x border-emerald-400/40"></div>
                <!-- Actual Ease Indicator Pip -->
                <div
                  class="absolute top-0 bottom-0 w-3 rounded-full bg-indigo-500 -ml-1.5 transition-all shadow-[0_0_10px_rgba(99,102,241,0.8)]"
                  :style="{ left: calculatePipPosition(dim.ease_cm, dim.target_band) }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 pt-2">
        <button
          type="button"
          class="flex-1 py-3.5 px-5 bg-indigo-600 hover:bg-indigo-500 text-white font-black rounded-xl transition text-center shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2"
          @click="$emit('save-size')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span>{{ $t('try.saveSizeBtn') }}</span>
        </button>

        <button
          type="button"
          class="py-3.5 px-5 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 font-bold rounded-xl transition text-center flex items-center justify-center gap-2"
          @click="askAssistantAboutFit"
        >
          <span>✨</span>
          <span>Ask AI Why</span>
        </button>

        <a
          v-if="productUrl"
          :href="productUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="py-3.5 px-5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold rounded-xl transition text-center flex items-center justify-center gap-1.5"
        >
          <span>{{ $t('try.viewProduct') }}</span>
          <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { cmToInches } from '~/utils/units'

const props = defineProps<{
  result: any
  explanation: string
  productUrl?: string
  unit: 'cm' | 'in'
  feedbackSummary?: {
    has_summary: boolean
    summary_text?: string
    sample_size?: number
  }
}>()

defineEmits<{
  (e: 'save-size'): void
}>()

const isExpanded = ref(true)

const confidenceBadgeClasses = computed(() => {
  switch (props.result.confidence_label) {
    case 'high':
      return 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40'
    case 'medium':
      return 'bg-amber-500/20 text-amber-300 border border-amber-400/40'
    default:
      return 'bg-rose-500/20 text-rose-300 border border-rose-400/40'
  }
})

const confidenceDotClasses = computed(() => {
  switch (props.result.confidence_label) {
    case 'high':
      return 'bg-emerald-400'
    case 'medium':
      return 'bg-amber-400'
    default:
      return 'bg-rose-400'
  }
})

const formattedWarnings = computed(() => {
  if (!props.result.warnings) return []
  return props.result.warnings.map((w: string) => {
    if (w === 'demo_data') return 'Demo data size chart'
    if (w === 'chart_not_verified') return 'This brand size chart has not been verified yet'
    if (w === 'between_two_sizes') return 'You are currently between two sizes'
    if (w === 'no_good_fit') return 'No ideal match in this chart — size may feel tight or loose'
    if (w.startsWith('missing_dimension:')) {
      const dim = w.split(':')[1]
      return `Adding your ${dim} measurement would significantly improve recommendation confidence.`
    }
    return w
  })
})

function formatVal(cmVal: number) {
  if (props.unit === 'in') {
    return cmToInches(cmVal)
  }
  return cmVal
}

function formatEase(cmVal: number) {
  const prefix = cmVal > 0 ? '+' : ''
  const val = props.unit === 'in' ? cmToInches(cmVal) : cmVal
  return `${prefix}${val}`
}

function verdictBadgeClasses(verdict: string) {
  switch (verdict) {
    case 'good':
      return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
    case 'snug':
      return 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
    case 'roomy':
      return 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
    case 'too_tight':
      return 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
    default:
      return 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
  }
}

function calculatePipPosition(ease: number, band: [number, number]): string {
  const [lo, hi] = band
  const minRange = lo - 4
  const maxRange = hi + 4
  const percent = ((ease - minRange) / (maxRange - minRange)) * 100
  const clamped = Math.max(5, Math.min(95, percent))
  return `${clamped}%`
}

const isAssistantOpen = useState('fitsense_assistant_open', () => false)

function askAssistantAboutFit() {
  isAssistantOpen.value = true
}
</script>
