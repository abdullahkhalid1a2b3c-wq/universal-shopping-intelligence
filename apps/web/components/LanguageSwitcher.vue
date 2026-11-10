<template>
  <select
    :value="locale"
    aria-label="Select language"
    class="rounded-md border-gray-300 bg-white px-2 py-1 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
    @change="onChange"
  >
    <option value="en">English</option>
    <option value="ur">اردو</option>
    <option value="ur-roman">Roman Urdu</option>
  </select>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()

function onChange(event: Event) {
  const code = (event.target as HTMLSelectElement).value
  navigateTo(switchLocalePath(code))
}
</script>

