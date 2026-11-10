<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4 sm:px-0">
    <TransitionGroup
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-center justify-between p-4 rounded-xl shadow-lg border text-sm font-medium"
        :class="bgClass(toast.type)"
      >
        <span>{{ toast.text }}</span>
        <button
          type="button"
          class="ml-4 text-gray-400 hover:text-gray-600 focus:outline-none"
          aria-label="Close"
          @click="remove(toast.id)"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
const { toasts, remove } = useToast()

function bgClass(type: string) {
  switch (type) {
    case 'success':
      return 'bg-emerald-50 text-emerald-900 border-emerald-200'
    case 'error':
      return 'bg-rose-50 text-rose-900 border-rose-200'
    default:
      return 'bg-indigo-50 text-indigo-900 border-indigo-200'
  }
}
</script>

