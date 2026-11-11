<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-black uppercase tracking-wider text-indigo-400">
        Step {{ currentStep }} of {{ totalSteps }}
      </span>
      <span class="text-xs font-bold text-slate-300">
        {{ stepNames[currentStep - 1] }}
      </span>
    </div>

    <!-- Progress Bar Track -->
    <div class="w-full h-2.5 bg-slate-900 border border-slate-700/80 rounded-full overflow-hidden p-0.5 shadow-inner">
      <div
        class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-300 ease-out shadow-sm"
        :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  currentStep: number
  totalSteps: number
  stepNames: string[]
}>()
</script>
