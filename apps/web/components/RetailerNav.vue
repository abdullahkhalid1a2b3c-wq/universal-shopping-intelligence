<template>
  <div class="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 mb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Status Notice if Pending -->
      <div v-if="currentRetailer && currentRetailer.status === 'pending'" class="py-2.5 px-4 mb-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-sm flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse"></span>
          <span><strong>{{ currentRetailer.name }}</strong> is currently <strong>pending verification</strong> by the FitSense admin team. Your products and size charts are visible to your team but not yet public.</span>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-amber-200 dark:bg-amber-800">Pending Review</span>
      </div>

      <!-- Retailer Title and Switcher -->
      <div class="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ currentRetailer ? currentRetailer.name : 'Retailer Portal' }}
            </h1>
            <span v-if="currentRetailer" :class="[
              'text-xs px-2.5 py-0.5 rounded-full font-medium uppercase tracking-wider',
              currentRetailer.status === 'verified' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' :
              currentRetailer.status === 'pending' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
              'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
            ]">
              {{ currentRetailer.status }}
            </span>
          </div>
          <p v-if="currentRetailer?.website_domain" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ currentRetailer.website_domain }} · Role: {{ isOwner ? 'Owner' : 'Editor' }}
          </p>
        </div>

        <!-- Navigation Tabs -->
        <nav class="flex space-x-1 sm:space-x-2 overflow-x-auto pb-2 md:pb-0" aria-label="Retailer Tabs">
          <NuxtLink
            :to="localePath('/retailer/products')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/retailer/products') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Products
          </NuxtLink>
          <NuxtLink
            :to="localePath('/retailer/size-charts')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/retailer/size-charts') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Size Charts
          </NuxtLink>
          <NuxtLink
            :to="localePath('/retailer/analytics')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/retailer/analytics') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Analytics & Feedback
          </NuxtLink>
          <NuxtLink
            :to="localePath('/retailer/settings')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/retailer/settings') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Settings & Team
          </NuxtLink>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const localePath = useLocalePath()
const { currentRetailer, isOwner } = useRetailer()

const isActive = (path: string) => {
  return route.path.includes(path)
}
</script>
