<template>
  <div class="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 mb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <span class="p-1 rounded-lg bg-indigo-600 text-white text-xs">ADMIN</span>
              FitSense Administration
            </h1>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Global management of retailers, DOM store adapters, coverage requests, and sizing data quality.
          </p>
        </div>

        <!-- Navigation Tabs -->
        <nav class="flex space-x-1 sm:space-x-2 overflow-x-auto pb-2 md:pb-0" aria-label="Admin Tabs">
          <NuxtLink
            :to="localePath('/admin/retailers')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/admin/retailers') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Retailers Verification
          </NuxtLink>
          <NuxtLink
            :to="localePath('/admin/coverage')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/admin/coverage') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Coverage Requests
          </NuxtLink>
          <NuxtLink
            :to="localePath('/admin/adapters')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/admin/adapters') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Store Adapters
          </NuxtLink>
          <NuxtLink
            :to="localePath('/admin/data-quality')"
            class="px-3.5 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors"
            :class="isActive('/admin/data-quality') ? 'bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'"
          >
            Data Quality Audit
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

const isActive = (path: string) => {
  return route.path.includes(path)
}
</script>
