<template>
  <div class="min-h-[50vh] flex items-center justify-center">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['admin'],
})

const localePath = useLocalePath()

onMounted(() => {
  navigateTo(localePath('/admin/retailers'))
})
</script>
