<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Header Hero Banner -->
    <div class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-8 sm:p-12 border border-slate-800 shadow-2xl">
      <div class="relative z-10 max-w-2xl space-y-3">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-bold uppercase tracking-wider">
          <span>🇵🇰 Pakistan Brand Directory</span>
        </div>
        <h1 class="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
          Explore Pakistani Fashion Brands
        </h1>
        <p class="text-sm sm:text-base text-slate-300 leading-relaxed">
          Universal size intelligence across Pakistan's leading fashion houses. Select a brand to find your exact recommended size based on verified size charts.
        </p>
      </div>
      <div class="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-indigo-500/10 to-transparent pointer-events-none"></div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/70 dark:border-slate-800 shadow-sm space-y-5">
      <!-- Search Bar -->
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by brand name (e.g. Khaadi, Sapphire, J., Outfitters, Diners)..."
          class="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <!-- Category Filter Pills -->
      <div class="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        <button
          v-for="cat in categoryFilters"
          :key="cat.value"
          type="button"
          @click="selectedCategory = cat.value"
          class="px-4 py-2 rounded-xl text-xs font-bold transition whitespace-nowrap"
          :class="
            selectedCategory === cat.value
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
              : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
          "
        >
          {{ cat.label }}
        </button>
      </div>

      <!-- A–Z Alphabetical Navigation Bar -->
      <div class="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-1.5 flex-wrap">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 mr-2">A–Z:</span>
        <button
          v-for="char in alphabet"
          :key="char"
          type="button"
          @click="selectedLetter = char"
          class="w-7 h-7 rounded-lg text-xs font-bold flex items-center justify-center transition"
          :class="
            selectedLetter === char
              ? 'bg-indigo-600 text-white'
              : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
          "
        >
          {{ char }}
        </button>
      </div>
    </div>

    <!-- Active Filter Info -->
    <div class="flex items-center justify-between text-xs text-slate-500 font-medium">
      <p>Showing <span class="font-bold text-slate-900 dark:text-white">{{ filteredBrands.length }}</span> Pakistani brands</p>
      <button
        v-if="searchQuery || selectedCategory !== 'all' || selectedLetter !== 'ALL'"
        type="button"
        @click="resetFilters"
        class="text-indigo-600 hover:underline font-bold"
      >
        Clear filters
      </button>
    </div>

    <!-- Brand Cards Grid -->
    <div v-if="filteredBrands.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink
        v-for="brand in filteredBrands"
        :key="brand.slug"
        :to="localePath(`/brands/${brand.slug}`)"
        class="group bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200/80 dark:border-slate-800 hover:border-indigo-500/60 dark:hover:border-indigo-500/60 transition-all duration-200 shadow-sm hover:shadow-xl hover:-translate-y-1 flex flex-col justify-between"
      >
        <div class="space-y-4">
          <!-- Top Row: Badge & COD -->
          <div class="flex items-center justify-between gap-2">
            <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Verified Charts
            </span>
            <span v-if="brand.supports_cod" class="text-[10px] font-semibold text-slate-400">
              COD Available
            </span>
          </div>

          <!-- Brand Identity -->
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-50 to-slate-100 dark:from-slate-800 dark:to-slate-800/80 border border-slate-200/60 dark:border-slate-700 flex items-center justify-center font-black text-xl text-indigo-600 dark:text-indigo-400 shadow-inner group-hover:scale-105 transition-transform">
              {{ brand.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-black text-lg text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                {{ brand.name }}
              </h3>
              <p class="text-xs text-slate-400 font-mono">
                {{ brand.website_domain }}
              </p>
            </div>
          </div>

          <!-- Description -->
          <p class="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
            {{ brand.description }}
          </p>

          <!-- Category Tags -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <span
              v-for="cat in brand.categories?.slice(0, 4)"
              :key="cat"
              class="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 capitalize"
            >
              {{ cat }}
            </span>
          </div>
        </div>

        <!-- Footer Action -->
        <div class="pt-5 mt-5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <span class="text-xs font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
            Find My Size &rarr;
          </span>
          <span class="text-[11px] text-slate-400 font-medium">
            Official Guide
          </span>
        </div>
      </NuxtLink>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-16 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/60 dark:border-slate-800 space-y-4">
      <div class="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto text-xl">
        🔍
      </div>
      <h3 class="text-base font-bold text-slate-900 dark:text-white">No brands match your filter</h3>
      <p class="text-xs text-slate-500 max-w-sm mx-auto">
        Try adjusting your search query, selecting another category, or clearing the A-Z initial filter.
      </p>
      <button
        type="button"
        @click="resetFilters"
        class="px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition"
      >
        Reset Filters
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8000'
const localePath = useLocalePath()

const brands = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('all')
const selectedLetter = ref('ALL')

const alphabet = ['ALL', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')]

const categoryFilters = [
  { label: 'All Brands', value: 'all' },
  { label: "Women's Fashion", value: 'women' },
  { label: "Men's Fashion", value: 'men' },
  { label: "Kids' Fashion", value: 'kids' },
  { label: 'Eastern Wear (Kurtas/Shalwar)', value: 'eastern' },
  { label: 'Western Wear (Tees/Jeans)', value: 'western' },
]

const resetFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = 'all'
  selectedLetter.value = 'ALL'
}

onMounted(async () => {
  try {
    const res = await $fetch<{ brands: any[] }>(`${apiBase}/v1/retailers/directory`)
    if (res && res.brands) {
      brands.value = res.brands
    }
  } catch (err) {
    // Graceful fallback
    brands.value = []
  } finally {
    isLoading.value = false
  }
})

const filteredBrands = computed(() => {
  return brands.value.filter((b) => {
    // Search query filter
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      const match =
        b.name?.toLowerCase().includes(q) ||
        b.slug?.toLowerCase().includes(q) ||
        b.website_domain?.toLowerCase().includes(q)
      if (!match) return false
    }

    // Category filter
    if (selectedCategory.value !== 'all') {
      const cats = b.categories || []
      const aud = b.target_audience || []
      const matchCat = cats.includes(selectedCategory.value) || aud.includes(selectedCategory.value)
      if (!matchCat) return false
    }

    // A-Z letter filter
    if (selectedLetter.value !== 'ALL') {
      if (!b.name?.toUpperCase().startsWith(selectedLetter.value)) {
        return false
      }
    }

    return true
  })
})
</script>

