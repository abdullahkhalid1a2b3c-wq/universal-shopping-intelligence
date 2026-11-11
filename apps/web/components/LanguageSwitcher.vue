<template>
  <div class="relative inline-block">
    <select
      :value="locale"
      aria-label="Select language"
      style="color-scheme: dark;"
      class="rounded-xl border border-slate-700 bg-slate-800/90 text-white font-bold px-3 py-1.5 text-xs focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 transition cursor-pointer shadow-inner appearance-none pr-7"
      @change="onChange"
    >
      <option value="en" class="bg-slate-900 text-white">English</option>
      <option value="ur" class="bg-slate-900 text-white">اردو</option>
      <option value="ur-roman" class="bg-slate-900 text-white">Roman Urdu</option>
    </select>
    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2 text-slate-400 text-[10px]">
      ▼
    </div>
  </div>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()

function onChange(event: Event) {
  const code = (event.target as HTMLSelectElement).value
  navigateTo(switchLocalePath(code))
}
</script>
