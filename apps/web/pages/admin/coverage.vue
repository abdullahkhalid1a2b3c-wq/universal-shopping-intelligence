<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <AdminNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Store Coverage Requests</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Aggregated customer requests for unsupported online clothing stores. Prioritize scrapers and retailer outreach by demand.
          </p>
        </div>

        <button
          @click="loadCoverage"
          class="px-3.5 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold hover:bg-gray-50 flex items-center gap-1.5"
        >
          <svg class="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="loading" class="p-12 text-center text-gray-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p class="text-sm">Aggregating requests...</p>
        </div>

        <div v-else-if="coverageList.length === 0" class="p-12 text-center text-gray-400 text-sm">
          No coverage requests recorded yet.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 uppercase tracking-wider text-gray-500 font-semibold">
              <tr>
                <th class="px-6 py-3.5">Store Domain</th>
                <th class="px-6 py-3.5">Request Count</th>
                <th class="px-6 py-3.5">Sample Requested URLs</th>
                <th class="px-6 py-3.5">Latest Request</th>
                <th class="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-gray-700 dark:text-gray-300">
              <tr v-for="(item, idx) in coverageList" :key="idx" class="hover:bg-gray-50/50 dark:hover:bg-gray-900/30">
                <td class="px-6 py-4">
                  <div class="font-bold text-sm text-gray-900 dark:text-white font-mono">{{ item.domain }}</div>
                </td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold font-mono bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                    {{ item.request_count }} requests
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="space-y-1 max-w-md">
                    <a
                      v-for="(url, uIdx) in item.sample_urls"
                      :key="uIdx"
                      :href="url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-indigo-600 dark:text-indigo-400 hover:underline block truncate font-mono text-[11px]"
                    >
                      {{ url }}
                    </a>
                  </div>
                </td>
                <td class="px-6 py-4 text-gray-400 font-mono text-[11px]">
                  {{ item.latest_request ? new Date(item.latest_request).toLocaleString() : '—' }}
                </td>
                <td class="px-6 py-4 text-right">
                  <NuxtLink
                    :to="localePath(`/admin/adapters?domain=${encodeURIComponent(item.domain)}`)"
                    class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-semibold text-xs hover:bg-indigo-700 transition-colors inline-block"
                  >
                    + Add Adapter
                  </NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({
  middleware: ['admin'],
})

const { apiFetch } = useApi()
const { showToast } = useToast()
const localePath = useLocalePath()

const loading = ref(true)
const coverageList = ref<any[]>([])

const loadCoverage = async () => {
  loading.value = true
  try {
    const data = await apiFetch<any[]>('/v1/admin/coverage')
    coverageList.value = data || []
  } catch (err: any) {
    showToast(err.message || 'Failed to load coverage requests', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCoverage()
})
</script>
