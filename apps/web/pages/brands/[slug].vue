<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-xs font-semibold text-slate-400">
      <NuxtLink :to="localePath('/brands')" class="hover:text-indigo-600 transition">
        Brands Directory
      </NuxtLink>
      <span>/</span>
      <span class="text-slate-900 dark:text-white capitalize">{{ brand?.name || slug }}</span>
    </nav>

    <!-- Loading Skeleton -->
    <div v-if="isLoading" class="animate-pulse space-y-6">
      <div class="h-48 rounded-3xl bg-slate-200 dark:bg-slate-800"></div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="h-64 rounded-3xl bg-slate-200 dark:bg-slate-800"></div>
        <div class="md:col-span-2 h-64 rounded-3xl bg-slate-200 dark:bg-slate-800"></div>
      </div>
    </div>

    <!-- Brand Profile View -->
    <div v-else-if="brand" class="space-y-10">
      <!-- Hero Card -->
      <div class="bg-white dark:bg-slate-900 rounded-3xl p-8 sm:p-10 border border-slate-200/80 dark:border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div class="flex items-start sm:items-center gap-6">
          <div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-600 to-purple-700 text-white flex items-center justify-center font-black text-3xl shadow-lg shadow-indigo-600/30 shrink-0">
            {{ brand.name.charAt(0) }}
          </div>
          <div class="space-y-2">
            <div class="flex items-center gap-3 flex-wrap">
              <h1 class="text-2xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
                {{ brand.name }}
              </h1>
              <span class="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Verified Sizing
              </span>
            </div>
            <p class="text-sm text-slate-500 dark:text-slate-400 font-mono">
              {{ brand.website_domain }}
            </p>
            <p class="text-sm text-slate-600 dark:text-slate-300 max-w-xl leading-relaxed">
              {{ brand.description }}
            </p>
          </div>
        </div>

        <!-- Action CTAs -->
        <div class="flex flex-col sm:flex-row md:flex-col gap-3 shrink-0">
          <div v-if="hasProfile" class="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-3 py-1.5 rounded-xl border border-emerald-200 dark:border-emerald-800 flex items-center gap-1.5">
            <span>✓</span>
            <span>Profile Ready: {{ profileState.chest }}{{ profileState.unit }} chest, {{ profileState.shoulder ? `${profileState.shoulder}${profileState.unit} shldr` : `${profileState.height}${profileState.unit} ht` }}</span>
          </div>

          <NuxtLink
            :to="localePath(`/try?retailer=${brand.slug}${hasProfile ? '&autocalculate=true' : ''}`)"
            class="px-6 py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm text-center shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/40 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-2"
          >
            <span>{{ hasProfile ? '⚡' : '🎯' }}</span>
            <span>{{ hasProfile ? `1-Click Size in ${brand.name}` : `Find My Size in ${brand.name}` }}</span>
          </NuxtLink>
          <button
            type="button"
            @click="openAssistantForBrand"
            class="px-6 py-3.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 font-bold text-sm text-center border border-indigo-200 dark:border-indigo-800/80 transition flex items-center justify-center gap-2"
          >
            <span>✨</span>
            <span>Ask AI About Sizing</span>
          </button>
        </div>
      </div>

      <!-- Detail Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Left: Brand Specs & Links -->
        <div class="space-y-6">
          <div class="bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
            <h3 class="text-sm font-bold uppercase tracking-wider text-slate-400">
              Brand Intelligence
            </h3>
            
            <div class="space-y-3 text-xs divide-y divide-slate-100 dark:divide-slate-800">
              <div class="pt-2 flex justify-between">
                <span class="text-slate-500">Origin Market:</span>
                <span class="font-bold text-slate-800 dark:text-slate-200">Pakistan 🇵🇰</span>
              </div>
              <div class="pt-2 flex justify-between">
                <span class="text-slate-500">Cash on Delivery:</span>
                <span class="font-bold text-emerald-600 dark:text-emerald-400">
                  {{ brand.supports_cod ? 'Supported across Pakistan' : 'Prepaid Only' }}
                </span>
              </div>
              <div class="pt-2 flex justify-between">
                <span class="text-slate-500">Data Source:</span>
                <span class="font-bold text-slate-800 dark:text-slate-200 capitalize">Official Brand Guide</span>
              </div>
              <div class="pt-2 flex justify-between">
                <span class="text-slate-500">Partnership Status:</span>
                <span class="font-bold text-indigo-600 dark:text-indigo-400">Independent Sizing Guide</span>
              </div>
            </div>

            <!-- Outbound Links -->
            <div class="pt-4 space-y-2 border-t border-slate-100 dark:border-slate-800">
              <a
                v-if="brand.official_size_chart_url"
                :href="brand.official_size_chart_url"
                target="_blank"
                rel="noopener noreferrer"
                class="block w-full py-2.5 px-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:text-indigo-600 font-semibold text-xs text-center border border-slate-200 dark:border-slate-700 transition"
              >
                Official Size Guide &rarr;
              </a>
              <a
                v-if="brand.return_policy_url"
                :href="brand.return_policy_url"
                target="_blank"
                rel="noopener noreferrer"
                class="block w-full py-2.5 px-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:text-indigo-600 font-semibold text-xs text-center border border-slate-200 dark:border-slate-700 transition"
              >
                Returns & Exchange Policy &rarr;
              </a>
            </div>
          </div>
        </div>

        <!-- Right: Size Chart Reference & Sizing Advice -->
        <div class="md:col-span-2 space-y-6">
          <div class="bg-white dark:bg-slate-900 rounded-3xl p-6 sm:p-8 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-lg font-black text-slate-900 dark:text-white">
                  {{ brand.name }} Standard Sizing Benchmark
                </h2>
                <p class="text-xs text-slate-500 mt-0.5">
                  Universal cm circumference guidelines used by FitSense deterministic recommendation engine.
                </p>
              </div>
              <span class="text-xs font-mono px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-bold">
                Unit: cm
              </span>
            </div>

            <!-- Standard Reference Table -->
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                    <th class="py-3 px-3">Size Label</th>
                    <th class="py-3 px-3">Chest (cm)</th>
                    <th class="py-3 px-3">Waist (cm)</th>
                    <th class="py-3 px-3">Shoulder (cm)</th>
                    <th class="py-3 px-3">Typical Fit</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60 font-medium text-slate-700 dark:text-slate-300">
                  <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td class="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400">XS</td>
                    <td class="py-3 px-3">88 – 92</td>
                    <td class="py-3 px-3">72 – 76</td>
                    <td class="py-3 px-3">36 – 38</td>
                    <td class="py-3 px-3 text-slate-400">Fitted</td>
                  </tr>
                  <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td class="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400">S</td>
                    <td class="py-3 px-3">94 – 98</td>
                    <td class="py-3 px-3">78 – 82</td>
                    <td class="py-3 px-3">40 – 42</td>
                    <td class="py-3 px-3 text-slate-400">Regular</td>
                  </tr>
                  <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td class="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400">M</td>
                    <td class="py-3 px-3">100 – 106</td>
                    <td class="py-3 px-3">84 – 90</td>
                    <td class="py-3 px-3">43 – 45</td>
                    <td class="py-3 px-3 text-slate-400">Regular</td>
                  </tr>
                  <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td class="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400">L</td>
                    <td class="py-3 px-3">108 – 114</td>
                    <td class="py-3 px-3">92 – 98</td>
                    <td class="py-3 px-3">46 – 48</td>
                    <td class="py-3 px-3 text-slate-400">Comfort</td>
                  </tr>
                  <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                    <td class="py-3 px-3 font-bold text-indigo-600 dark:text-indigo-400">XL</td>
                    <td class="py-3 px-3">116 – 122</td>
                    <td class="py-3 px-3">100 – 108</td>
                    <td class="py-3 px-3">49 – 51</td>
                    <td class="py-3 px-3 text-slate-400">Relaxed</td>
                  </tr>
                </tbody>
              </table>
            </div>

              <!-- Find Size CTA Banner -->
              <div class="p-6 rounded-2xl bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/40 dark:to-purple-950/40 border border-indigo-100 dark:border-indigo-900/40 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="space-y-1 text-center sm:text-left">
                  <p class="font-bold text-sm text-indigo-950 dark:text-indigo-200">
                    {{ hasProfile ? `Find your guaranteed size in ${brand.name}` : 'Ready to test your measurements?' }}
                  </p>
                  <p class="text-xs text-indigo-800/80 dark:text-indigo-300/80">
                    {{ hasProfile ? `FitSense automatically matches your active profile against ${brand.name}'s verified size charts with 1 click.` : `FitSense matches your body measurements against ${brand.name} sizing charts.` }}
                  </p>
                </div>
                <NuxtLink
                  :to="localePath(`/try?retailer=${brand.slug}${hasProfile ? '&autocalculate=true' : ''}`)"
                  class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md transition shrink-0 flex items-center gap-1.5"
                >
                  <span>{{ hasProfile ? '⚡' : '🎯' }}</span>
                  <span>{{ hasProfile ? `1-Click Size in ${brand.name}` : 'Find My Size &rarr;' }}</span>
                </NuxtLink>
              </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 404 Brand Not Found -->
    <div v-else class="text-center py-20 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 space-y-4">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Brand Not Found</h2>
      <p class="text-xs text-slate-500">
        We could not locate "{{ slug }}" in our verified Pakistani fashion catalog.
      </p>
      <NuxtLink
        :to="localePath('/brands')"
        class="inline-block px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition"
      >
        &larr; Return to Brands Directory
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFitProfile } from '~/composables/useFitProfile'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8000'
const localePath = useLocalePath()

const { profileState, hasProfile, loadProfile } = useFitProfile()

const slug = computed(() => String(route.params.slug || ''))
const brand = ref<any | null>(null)
const isLoading = ref(true)

const isAssistantOpen = useState('fitsense_assistant_open', () => false)

const openAssistantForBrand = () => {
  isAssistantOpen.value = true
}

onMounted(async () => {
  // Load customer's universal profile for instant 1-click recommendations
  await loadProfile()

  try {
    const res = await $fetch<any>(`${apiBase}/v1/retailers/${slug.value}`)
    brand.value = res
  } catch (err) {
    brand.value = null
  } finally {
    isLoading.value = false
  }
})
</script>

