<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-bold uppercase tracking-wider text-indigo-600">
        Step {{ currentStep }} of {{ totalSteps }}
      </span>
      <span class="text-xs font-semibold text-gray-500">
        {{ stepNames[currentStep - 1] }}
      </span>
    </div>

    <!-- Progress Bar Track -->
    <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
      <div
        class="h-full bg-indigo-600 rounded-full transition-all duration-300 ease-out"
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

