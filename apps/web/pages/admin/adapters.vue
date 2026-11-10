<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <AdminNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Store DOM Adapters</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            CSS selector maps that guide the Chrome Extension content script on specific e-commerce store themes.
          </p>
        </div>

        <button
          @click="openAddAdapter"
          class="px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-medium text-xs hover:bg-indigo-700 flex items-center gap-1.5 shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Add Store Adapter</span>
        </button>
      </div>

      <!-- Adapters Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="loading" class="p-12 text-center text-gray-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p class="text-sm">Loading adapters...</p>
        </div>

        <div v-else-if="adapters.length === 0" class="p-12 text-center text-gray-400 text-sm">
          No store adapters configured yet.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 uppercase tracking-wider text-gray-500 font-semibold">
              <tr>
                <th class="px-6 py-3.5">Store Domain</th>
                <th class="px-6 py-3.5">Platform</th>
                <th class="px-6 py-3.5">Selectors Preview</th>
                <th class="px-6 py-3.5">Status</th>
                <th class="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-gray-700 dark:text-gray-300">
              <tr v-for="adapter in adapters" :key="adapter.id" class="hover:bg-gray-50/50 dark:hover:bg-gray-900/30">
                <td class="px-6 py-4 font-bold font-mono text-sm text-gray-900 dark:text-white">
                  {{ adapter.domain }}
                </td>
                <td class="px-6 py-4 capitalize font-medium">
                  {{ adapter.platform }}
                </td>
                <td class="px-6 py-4 font-mono text-[11px] text-gray-500 max-w-xs truncate">
                  {{ JSON.stringify(adapter.selectors) }}
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider',
                    adapter.is_enabled ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]">
                    {{ adapter.is_enabled ? 'Enabled' : 'Disabled' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button
                    @click="editAdapter(adapter)"
                    class="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
                  >
                    Edit Config
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Adapter Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-lg w-full p-6 border border-gray-100 dark:border-gray-700 shadow-2xl">
        <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-700 mb-4">
          <h3 class="font-bold text-sm text-gray-900 dark:text-white">
            {{ isEditingExisting ? 'Edit Store Adapter' : 'Add Store Adapter' }}
          </h3>
          <button @click="showModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <form @submit.prevent="saveAdapter" class="space-y-4 text-xs">
          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Domain *</label>
            <input
              v-model="adapterForm.domain"
              :disabled="isEditingExisting"
              type="text"
              required
              placeholder="e.g. sapphire.pk"
              class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 font-mono"
            />
          </div>

          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Platform</label>
            <select
              v-model="adapterForm.platform"
              class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
            >
              <option value="shopify">Shopify</option>
              <option value="woocommerce">WooCommerce</option>
              <option value="custom">Custom Theme</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">
              DOM Selectors (JSON format)
            </label>
            <textarea
              v-model="adapterForm.selectorsJson"
              rows="7"
              required
              class="w-full p-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 font-mono text-[11px]"
            ></textarea>
            <p v-if="jsonError" class="text-rose-500 font-semibold mt-1">{{ jsonError }}</p>
          </div>

          <div class="flex items-center gap-2 p-3 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/40">
            <input
              v-model="adapterForm.is_enabled"
              id="adapter_enabled"
              type="checkbox"
              class="rounded text-indigo-600 focus:ring-indigo-500"
            />
            <label for="adapter_enabled" class="font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
              Enable adapter for browser extension
            </label>
          </div>

          <div class="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-700">
            <button type="button" @click="showModal = false" class="px-4 py-2 rounded-xl border text-gray-600">
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-5 py-2 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1.5"
            >
              <span v-if="saving" class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></span>
              <span>Save Adapter</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

definePageMeta({
  middleware: ['admin'],
})

const { apiFetch } = useApi()
const { showToast } = useToast()
const route = useRoute()

const loading = ref(true)
const saving = ref(false)
const adapters = ref<any[]>([])

const showModal = ref(false)
const isEditingExisting = ref(false)
const jsonError = ref<string | null>(null)

const adapterForm = reactive({
  domain: '',
  platform: 'custom',
  selectorsJson: '{\n  "product_title": "h1.product-title",\n  "size_options": ".size-swatch input",\n  "price": ".product-price",\n  "size_guide_btn": "#size-guide-modal"\n}',
  is_enabled: true,
})

const loadAdapters = async () => {
  loading.value = true
  try {
    const data = await apiFetch<any[]>('/v1/admin/adapters')
    adapters.value = data || []
  } catch (err: any) {
    showToast(err.message || 'Failed to load adapters', 'error')
  } finally {
    loading.value = false
  }
}

const openAddAdapter = () => {
  isEditingExisting.value = false
  jsonError.value = null
  adapterForm.domain = (route.query.domain as string) || ''
  adapterForm.platform = 'shopify'
  adapterForm.selectorsJson = '{\n  "product_title": ".product-title",\n  "size_options": ".size-item",\n  "size_guide_btn": ".size-chart-link"\n}'
  adapterForm.is_enabled = true
  showModal.value = true
}

const editAdapter = (adapter: any) => {
  isEditingExisting.value = true
  jsonError.value = null
  adapterForm.domain = adapter.domain
  adapterForm.platform = adapter.platform || 'custom'
  adapterForm.selectorsJson = JSON.stringify(adapter.selectors || {}, null, 2)
  adapterForm.is_enabled = adapter.is_enabled !== false
  showModal.value = true
}

const saveAdapter = async () => {
  jsonError.value = null
  let parsedSelectors = {}
  try {
    parsedSelectors = JSON.parse(adapterForm.selectorsJson)
  } catch (e: any) {
    jsonError.value = `Invalid JSON syntax: ${e.message}`
    return
  }

  saving.value = true
  try {
    await apiFetch(`/v1/admin/adapters/${encodeURIComponent(adapterForm.domain.trim().toLowerCase())}`, {
      method: 'PUT',
      body: {
        platform: adapterForm.platform,
        selectors: parsedSelectors,
        is_enabled: adapterForm.is_enabled,
      },
    })

    showToast(`Store adapter for ${adapterForm.domain} saved successfully`, 'success')
    showModal.value = false
    loadAdapters()
  } catch (err: any) {
    showToast(err.message || 'Failed to save adapter', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadAdapters()
  if (route.query.domain) {
    openAddAdapter()
  }
})
</script>
