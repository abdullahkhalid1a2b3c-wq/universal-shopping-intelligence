<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <AdminNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Retailer Merchant Directory</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Review and approve pending fashion retailers, or suspend inactive accounts.
          </p>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="loadRetailers"
            class="px-3.5 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <!-- Retailers Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="loading" class="p-12 text-center text-gray-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p class="text-sm">Loading retailers...</p>
        </div>

        <div v-else-if="retailers.length === 0" class="p-12 text-center text-gray-400 text-sm">
          No retailers registered yet.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 uppercase tracking-wider text-gray-500 font-semibold">
              <tr>
                <th class="px-6 py-3.5">Brand</th>
                <th class="px-6 py-3.5">Domain</th>
                <th class="px-6 py-3.5">Members</th>
                <th class="px-6 py-3.5">Products</th>
                <th class="px-6 py-3.5">Status</th>
                <th class="px-6 py-3.5 text-right">Moderation Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-gray-700 dark:text-gray-300">
              <tr v-for="ret in retailers" :key="ret.id" class="hover:bg-gray-50/50 dark:hover:bg-gray-900/30">
                <td class="px-6 py-4">
                  <div class="font-bold text-sm text-gray-900 dark:text-white">{{ ret.name }}</div>
                  <div class="text-[11px] font-mono text-gray-400">/{{ ret.slug }}</div>
                </td>
                <td class="px-6 py-4">
                  <a
                    v-if="ret.website_domain"
                    :href="'https://' + ret.website_domain"
                    target="_blank"
                    class="text-indigo-600 dark:text-indigo-400 hover:underline font-mono"
                  >
                    {{ ret.website_domain }}
                  </a>
                  <span v-else class="text-gray-400 italic">No domain</span>
                </td>
                <td class="px-6 py-4 font-mono font-medium">
                  {{ ret.member_count || 0 }}
                </td>
                <td class="px-6 py-4 font-mono font-medium">
                  {{ ret.product_count || 0 }}
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider',
                    ret.status === 'verified' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' :
                    ret.status === 'pending' ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300' :
                    'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                  ]">
                    {{ ret.status }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      v-if="ret.status !== 'verified'"
                      @click="setStatus(ret.id, 'verified')"
                      class="px-3 py-1 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 transition-colors text-[11px]"
                    >
                      Approve / Verify
                    </button>
                    <button
                      v-if="ret.status !== 'suspended'"
                      @click="setStatus(ret.id, 'suspended')"
                      class="px-3 py-1 rounded-lg bg-rose-600 text-white font-semibold hover:bg-rose-700 transition-colors text-[11px]"
                    >
                      Suspend
                    </button>
                    <button
                      v-if="ret.status === 'suspended'"
                      @click="setStatus(ret.id, 'pending')"
                      class="px-3 py-1 rounded-lg bg-gray-600 text-white font-semibold hover:bg-gray-700 transition-colors text-[11px]"
                    >
                      Reset to Pending
                    </button>
                  </div>
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

const loading = ref(true)
const retailers = ref<any[]>([])

const loadRetailers = async () => {
  loading.value = true
  try {
    const data = await apiFetch<any[]>('/v1/admin/retailers')
    retailers.value = data || []
  } catch (err: any) {
    showToast(err.message || 'Failed to load retailers', 'error')
  } finally {
    loading.value = false
  }
}

const setStatus = async (retailerId: string, status: 'pending' | 'verified' | 'suspended') => {
  try {
    await apiFetch(`/v1/admin/retailers/${retailerId}/status`, {
      method: 'PATCH',
      body: { status },
    })
    showToast(`Retailer status updated to ${status}`, 'success')
    loadRetailers()
  } catch (err: any) {
    showToast(err.message || 'Failed to update status', 'error')
  }
}

onMounted(() => {
  loadRetailers()
})
</script>
