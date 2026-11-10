<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <RetailerNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Action Bar -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div class="flex flex-1 items-center gap-3 max-w-lg">
          <!-- Search -->
          <div class="relative flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search products by title or URL..."
              class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <svg class="w-4 h-4 text-gray-400 absolute left-3.5 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <!-- Category Filter -->
          <select
            v-model="selectedCategory"
            class="px-3.5 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Categories</option>
            <option value="tshirt_top">T-Shirts & Tops</option>
            <option value="shirt">Shirts</option>
            <option value="kurta">Kurtas</option>
            <option value="trouser">Trousers</option>
            <option value="jeans">Jeans</option>
            <option value="dress">Dresses</option>
          </select>
        </div>

        <!-- Buttons -->
        <div class="flex items-center gap-3">
          <button
            @click="showBulkModal = true"
            class="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm font-medium transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span>Bulk CSV Import</span>
          </button>

          <button
            @click="openAddModal"
            class="px-4 py-2.5 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700 text-sm font-medium transition-colors shadow-sm flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <span>Add Product</span>
          </button>
        </div>
      </div>

      <!-- Products Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="loading" class="p-12 text-center text-gray-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p class="text-sm">Loading product catalogue...</p>
        </div>

        <div v-else-if="filteredProducts.length === 0" class="p-12 text-center text-gray-400">
          <svg class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <p class="text-base font-medium text-gray-900 dark:text-white">No products found</p>
          <p class="text-xs text-gray-500 mt-1">Add your first product or import a CSV catalogue to get started.</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              <tr>
                <th class="px-6 py-3.5">Product</th>
                <th class="px-6 py-3.5">Category</th>
                <th class="px-6 py-3.5">Size Chart</th>
                <th class="px-6 py-3.5">Fabric & Stretch</th>
                <th class="px-6 py-3.5">Active</th>
                <th class="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-gray-700 dark:text-gray-300">
              <tr v-for="prod in filteredProducts" :key="prod.id" class="hover:bg-gray-50/50 dark:hover:bg-gray-900/30 transition-colors">
                <td class="px-6 py-4">
                  <div class="font-medium text-gray-900 dark:text-white">{{ prod.name }}</div>
                  <a
                    :href="prod.product_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-indigo-600 dark:text-indigo-400 hover:underline truncate max-w-xs block mt-0.5"
                  >
                    {{ prod.canonical_url || prod.product_url }}
                  </a>
                </td>
                <td class="px-6 py-4">
                  <span class="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 capitalize">
                    {{ formatCategory(prod.category) }}
                  </span>
                  <span v-if="prod.gender_category" class="text-xs text-gray-400 block mt-1 capitalize">
                    {{ prod.gender_category }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span v-if="prod.size_charts?.name" class="font-medium text-gray-800 dark:text-gray-200">
                    {{ prod.size_charts.name }}
                  </span>
                  <span v-else class="text-xs text-amber-600 dark:text-amber-400 font-medium">
                    No chart linked
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="text-xs">{{ prod.fabric || 'Unspecified fabric' }}</div>
                  <div class="text-xs text-gray-400 mt-0.5">Stretch: {{ prod.stretch_pct || 0 }}%</div>
                </td>
                <td class="px-6 py-4">
                  <!-- Active Toggle -->
                  <button
                    @click="toggleActive(prod)"
                    type="button"
                    :class="[
                      'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none',
                      prod.is_active ? 'bg-indigo-600' : 'bg-gray-200 dark:bg-gray-700'
                    ]"
                  >
                    <span
                      :class="[
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                        prod.is_active ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                </td>
                <td class="px-6 py-4 text-right">
                  <button
                    @click="deleteProduct(prod.id)"
                    class="text-xs font-medium text-rose-600 hover:text-rose-700 p-1"
                    title="Delete product"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Product Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-2xl w-full p-6 sm:p-8 border border-gray-100 dark:border-gray-700 shadow-2xl my-8 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700 mb-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Add New Product</h2>
          <button @click="showAddModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="saveProduct" class="space-y-5">
          <!-- Name -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              Product Title <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="productForm.name"
              type="text"
              required
              placeholder="e.g. Classic Lawn Stitched Kurta"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <!-- Category & Gender -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Category <span class="text-rose-500">*</span>
              </label>
              <select
                v-model="productForm.category"
                required
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="tshirt_top">T-Shirt & Tops</option>
                <option value="shirt">Button-Down Shirt</option>
                <option value="kurta">Kurta / Kameez</option>
                <option value="trouser">Trousers / Shalwar</option>
                <option value="jeans">Jeans / Denim</option>
                <option value="dress">Dress</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
                Gender Category
              </label>
              <select
                v-model="productForm.gender_category"
                class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="womens">Womens</option>
                <option value="mens">Mens</option>
                <option value="unisex">Unisex</option>
              </select>
            </div>
          </div>

          <!-- Product URL & Canonical Preview -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              Store Product Page URL <span class="text-rose-500">*</span>
            </label>
            <input
              v-model="productForm.product_url"
              type="url"
              required
              placeholder="https://brand.pk/products/stitched-kurta-24"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <!-- Canonical URL Preview -->
            <div v-if="derivedCanonicalUrl" class="mt-2 p-2.5 rounded-lg bg-gray-100 dark:bg-gray-900 text-xs text-gray-600 dark:text-gray-400 font-mono">
              <span class="text-indigo-600 dark:text-indigo-400 font-semibold">Matched Canonical URL:</span> {{ derivedCanonicalUrl }}
            </div>
          </div>

          <!-- Size Chart Selection -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              Associated Size Chart <span class="text-rose-500">*</span>
            </label>
            <select
              v-model="productForm.size_chart_id"
              required
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="" disabled>Select a size chart</option>
              <option v-for="chart in sizeCharts" :key="chart.id" :value="chart.id">
                {{ chart.name }} ({{ chart.category }} · {{ chart.measured_as }})
              </option>
            </select>
          </div>

          <!-- Fabric & Stretch Slider -->
          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-1">
              Fabric Composition
            </label>
            <input
              v-model="productForm.fabric"
              type="text"
              placeholder="e.g. 100% Lawn Cotton, 98% Cotton 2% Spandex"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <!-- Stretch Percentage Slider (0-40) with helper text -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                Fabric Stretch: <span class="text-indigo-600 dark:text-indigo-400 font-bold">{{ productForm.stretch_pct }}%</span>
              </label>
              <span class="text-xs text-gray-400">0% – 40%</span>
            </div>
            <input
              v-model.number="productForm.stretch_pct"
              type="range"
              min="0"
              max="40"
              step="1"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span v-if="productForm.stretch_pct === 0"><strong>0%:</strong> Woven cotton, lawn, or rigid denim (no stretch).</span>
              <span v-else-if="productForm.stretch_pct <= 10"><strong>1-10%:</strong> Light stretch (comfort blend, stretch denim).</span>
              <span v-else-if="productForm.stretch_pct <= 19"><strong>11-19%:</strong> Medium stretch blend.</span>
              <span v-else><strong>20%+:</strong> High stretch (rib knit, jersey, spandex, activewear).</span>
            </p>
          </div>

          <!-- Thickness, Transparency, Fit Cut, Shrinkage -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Thickness</label>
              <select v-model="productForm.thickness" class="w-full p-2 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <option value="light">Light</option>
                <option value="medium">Medium</option>
                <option value="heavy">Heavy</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Transparency</label>
              <select v-model="productForm.transparency" class="w-full p-2 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <option value="opaque">Opaque</option>
                <option value="slightly_sheer">Slightly Sheer</option>
                <option value="sheer">Sheer</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Fit Cut</label>
              <select v-model="productForm.fit_cut" class="w-full p-2 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <option value="regular">Regular</option>
                <option value="slim">Slim</option>
                <option value="relaxed">Relaxed</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Shrinkage %</label>
              <input v-model.number="productForm.shrinkage_pct" type="number" min="0" max="10" step="0.5" class="w-full p-2 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900" />
            </div>
          </div>

          <!-- Buttons -->
          <div class="pt-4 flex items-center justify-end gap-3 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="showAddModal = false"
              class="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-medium text-sm hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2"
            >
              <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              <span>Save Product</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Bulk Import Modal -->
    <div v-if="showBulkModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-2xl w-full p-6 sm:p-8 border border-gray-100 dark:border-gray-700 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700 mb-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Bulk Import Products from CSV</h2>
          <button @click="showBulkModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between p-3.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900 text-xs">
            <span class="text-indigo-800 dark:text-indigo-300">Need the CSV format? Download our sample template.</span>
            <button @click="downloadTemplate" class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700">
              Download Template
            </button>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider mb-2">
              Paste CSV Content or Upload File
            </label>
            <textarea
              v-model="csvInput"
              rows="7"
              placeholder="name,category,gender_category,product_url,stretch_pct,thickness,fit_cut&#10;Oxford Shirt,shirt,mens,https://brand.pk/shirt-1,0,medium,regular"
              class="w-full p-3 font-mono text-xs rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            ></textarea>
          </div>

          <!-- Row Validation Errors Display -->
          <div v-if="validationErrors.length > 0" class="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-800 dark:text-rose-300">
            <div class="font-bold mb-2 flex items-center gap-1.5">
              <svg class="w-4 h-4 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Validation Errors ({{ validationErrors.length }} found):</span>
            </div>
            <ul class="list-disc pl-5 space-y-1 max-h-36 overflow-y-auto">
              <li v-for="(err, idx) in validationErrors" :key="idx">
                <span class="font-semibold">Row {{ err.row }} [{{ err.field }}]:</span> {{ err.message }}
              </li>
            </ul>
          </div>

          <div v-if="validCount > 0" class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            ✓ {{ validCount }} valid rows ready for import.
          </div>

          <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              @click="showBulkModal = false"
              class="px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              Cancel
            </button>
            <button
              @click="validateAndImportCSV"
              :disabled="importing || !csvInput.trim()"
              class="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-medium text-sm hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2"
            >
              <span v-if="importing" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              <span>Validate & Import</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { normalizeProductUrl } from '~/utils/url'

definePageMeta({
  middleware: ['retailer'],
})

const { currentRetailer, fetchRetailerProfile } = useRetailer()
const { showToast } = useToast()
const { apiFetch } = useApi()
const supabase = useSupabaseClient()

const loading = ref(true)
const products = ref<any[]>([])
const sizeCharts = ref<any[]>([])
const searchQuery = ref('')
const selectedCategory = ref('')

const showAddModal = ref(false)
const saving = ref(false)
const showBulkModal = ref(false)
const importing = ref(false)
const csvInput = ref('')
const validationErrors = ref<any[]>([])
const validCount = ref(0)

const productForm = ref({
  name: '',
  category: 'shirt',
  gender_category: 'mens',
  product_url: '',
  size_chart_id: '',
  fabric: '',
  stretch_pct: 0,
  thickness: 'medium',
  transparency: 'opaque',
  shrinkage_pct: 0,
  season: 'All-Season',
  fit_cut: 'regular',
})

const derivedCanonicalUrl = computed(() => {
  return normalizeProductUrl(productForm.value.product_url)
})

const formatCategory = (cat: string) => {
  const map: Record<string, string> = {
    tshirt_top: 'T-Shirt & Tops',
    shirt: 'Shirt',
    kurta: 'Kurta',
    trouser: 'Trouser',
    jeans: 'Jeans',
    dress: 'Dress',
  }
  return map[cat] || cat
}

const loadData = async () => {
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }
  if (!currentRetailer.value) return

  loading.value = true
  try {
    // 1. Fetch products
    const { data: prods } = await supabase
      .table('products')
      .select('*, size_charts(id, name, measured_as)')
      .eq('retailer_id', currentRetailer.value.id)
      .order('created_at', { ascending: false })

    products.value = prods || []

    // 2. Fetch size charts
    const { data: charts } = await supabase
      .table('size_charts')
      .select('id, name, category, measured_as')
      .eq('retailer_id', currentRetailer.value.id)
      .order('name')

    sizeCharts.value = charts || []
  } catch (err: any) {
    showToast(err.message || 'Error loading catalogue', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const filteredProducts = computed(() => {
  return products.value.filter((p) => {
    const matchesSearch = !searchQuery.value ||
      p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.product_url.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCat = !selectedCategory.value || p.category === selectedCategory.value
    return matchesSearch && matchesCat
  })
})

const openAddModal = () => {
  productForm.value = {
    name: '',
    category: 'shirt',
    gender_category: 'mens',
    product_url: '',
    size_chart_id: sizeCharts.value[0]?.id || '',
    fabric: '',
    stretch_pct: 0,
    thickness: 'medium',
    transparency: 'opaque',
    shrinkage_pct: 0,
    season: 'All-Season',
    fit_cut: 'regular',
  }
  showAddModal.value = true
}

const saveProduct = async () => {
  if (!currentRetailer.value) return
  saving.value = true

  const canonical = derivedCanonicalUrl.value || productForm.value.product_url

  try {
    const { data, error } = await supabase
      .table('products')
      .insert({
        retailer_id: currentRetailer.value.id,
        name: productForm.value.name.trim(),
        category: productForm.value.category,
        gender_category: productForm.value.gender_category,
        product_url: productForm.value.product_url.trim(),
        canonical_url: canonical,
        size_chart_id: productForm.value.size_chart_id || null,
        fabric: productForm.value.fabric.trim() || null,
        stretch_pct: productForm.value.stretch_pct,
        thickness: productForm.value.thickness,
        transparency: productForm.value.transparency,
        shrinkage_pct: productForm.value.shrinkage_pct,
        season: productForm.value.season,
        fit_cut: productForm.value.fit_cut,
        is_active: true,
      })
      .select('*, size_charts(id, name, measured_as)')
      .single()

    if (error) throw error

    showToast('Product added successfully', 'success')
    products.value.unshift(data)
    showAddModal.value = false
  } catch (err: any) {
    showToast(err.message || 'Failed to save product', 'error')
  } finally {
    saving.value = false
  }
}

const toggleActive = async (prod: any) => {
  const newStatus = !prod.is_active
  try {
    const { error } = await supabase
      .table('products')
      .update({ is_active: newStatus })
      .eq('id', prod.id)

    if (error) throw error
    prod.is_active = newStatus
    showToast(`Product ${newStatus ? 'activated' : 'deactivated'}`, 'info')
  } catch (err: any) {
    showToast(err.message || 'Failed to update status', 'error')
  }
}

const deleteProduct = async (id: string) => {
  if (!confirm('Are you sure you want to delete this product?')) return
  try {
    const { error } = await supabase
      .table('products')
      .delete()
      .eq('id', id)

    if (error) throw error
    products.value = products.value.filter((p) => p.id !== id)
    showToast('Product deleted', 'success')
  } catch (err: any) {
    showToast(err.message || 'Failed to delete product', 'error')
  }
}

const downloadTemplate = async () => {
  try {
    const text = await apiFetch<string>('/v1/retailer/products/template')
    const blob = new Blob([text], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'fitsense-products-template.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    showToast('Failed to download template', 'error')
  }
}

const validateAndImportCSV = async () => {
  if (!currentRetailer.value) return
  importing.value = true
  validationErrors.value = []

  try {
    const parseRes = await apiFetch<any>('/v1/retailer/products/import-csv', {
      method: 'POST',
      body: { csv_content: csvInput.value },
    })

    if (!parseRes.success && parseRes.errors?.length > 0) {
      validationErrors.value = parseRes.errors
      validCount.value = parseRes.valid_count || 0
      showToast('Validation failed. Please correct the highlighted errors.', 'error')
      return
    }

    if (!parseRes.valid_rows || parseRes.valid_rows.length === 0) {
      showToast('No valid product rows to import', 'error')
      return
    }

    // Insert valid rows into database
    const insertPayload = parseRes.valid_rows.map((r: any) => ({
      retailer_id: currentRetailer.value!.id,
      name: r.name,
      category: r.category,
      gender_category: r.gender_category || 'unisex',
      product_url: r.product_url,
      canonical_url: normalizeProductUrl(r.product_url),
      fabric: r.fabric || null,
      stretch_pct: r.stretch_pct || 0,
      thickness: r.thickness || 'medium',
      transparency: r.transparency || 'opaque',
      shrinkage_pct: r.shrinkage_pct || 0,
      season: r.season || 'All-Season',
      fit_cut: r.fit_cut || 'regular',
      is_active: true,
    }))

    const { data: inserted, error: insertErr } = await supabase
      .table('products')
      .upsert(insertPayload, { onConflict: 'canonical_url' })
      .select('*, size_charts(id, name, measured_as)')

    if (insertErr) throw insertErr

    showToast(`Successfully imported ${inserted?.length || insertPayload.length} products!`, 'success')
    showBulkModal.value = false
    csvInput.value = ''
    loadData()
  } catch (err: any) {
    showToast(err.message || 'Import failed', 'error')
  } finally {
    importing.value = false
  }
}
</script>
