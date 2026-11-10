<template>
  <div class="min-h-[50vh] flex items-center justify-center">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['retailer'],
})

const { currentRetailer, fetchRetailerProfile } = useRetailer()
const localePath = useLocalePath()

onMounted(async () => {
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }

  if (currentRetailer.value) {
    navigateTo(localePath('/retailer/products'))
  } else {
    navigateTo(localePath('/retailer/onboarding'))
  }
})
</script>
