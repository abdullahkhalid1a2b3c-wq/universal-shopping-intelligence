<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <AdminNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Data Quality & Verification Audit</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Audit size charts across all brands to identify unverified tables, seed demo data, and mathematical anomalies.
          </p>
        </div>

        <button
          @click="loadQualityAudit"
          class="px-3.5 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold hover:bg-gray-50 flex items-center gap-1.5"
        >
          <svg class="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Run Audit</span>
        </button>
      </div>

      <!-- KPI Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-5 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-gray-200 dark:border-gray-700">
          <div class="text-xs font-semibold text-gray-400 uppercase">Total Charts</div>
          <div class="text-2xl font-extrabold text-gray-900 dark:text-white font-mono mt-1">
            {{ auditData.total_charts || 0 }}
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/20">
          <div class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase">Fit Accuracy</div>
          <div class="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-1">
            {{ auditData.accuracy?.accuracy_pct ?? 0 }}%
          </div>
          <div class="text-[10px] text-gray-400 mt-0.5">
            {{ auditData.accuracy?.acceptable_fit_count || 0 }} / {{ auditData.accuracy?.followed_recommendation_count || 0 }} acceptable
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-purple-200 dark:border-purple-900/50 bg-purple-50/20">
          <div class="text-xs font-semibold text-purple-600 dark:text-purple-400 uppercase">Needs Review</div>
          <div class="text-2xl font-extrabold text-purple-600 dark:text-purple-400 font-mono mt-1">
            {{ auditData.needs_review_count || 0 }}
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-amber-200 dark:border-amber-900/50 bg-amber-50/20">
          <div class="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase">Unverified Drafts</div>
          <div class="text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1">
            {{ auditData.unverified_count || 0 }}
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-5 border border-rose-200 dark:border-rose-900/50 bg-rose-50/20">
          <div class="text-xs font-semibold text-rose-600 dark:text-rose-400 uppercase">Anomalies</div>
          <div class="text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-1">
            {{ auditData.warnings_count || 0 }}
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 flex space-x-4">
        <button
          @click="activeTab = 'needs_review'"
          :class="[
            'pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors',
            activeTab === 'needs_review' ? 'border-purple-500 text-purple-600' : 'border-transparent text-gray-400 hover:text-gray-700'
          ]"
        >
          Needs Review ({{ auditData.needs_review_count || 0 }})
        </button>
        <button
          @click="activeTab = 'warnings'"
          :class="[
            'pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors',
            activeTab === 'warnings' ? 'border-rose-500 text-rose-600' : 'border-transparent text-gray-400 hover:text-gray-700'
          ]"
        >
          Anomalies & Warnings ({{ auditData.warnings_count || 0 }})
        </button>
        <button
          @click="activeTab = 'unverified'"
          :class="[
            'pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors',
            activeTab === 'unverified' ? 'border-amber-500 text-amber-600' : 'border-transparent text-gray-400 hover:text-gray-700'
          ]"
        >
          Unverified Charts ({{ auditData.unverified_count || 0 }})
        </button>
        <button
          @click="activeTab = 'demo'"
          :class="[
            'pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors',
            activeTab === 'demo' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-400 hover:text-gray-700'
          ]"
        >
          Demo / Seed Charts ({{ auditData.demo_count || 0 }})
        </button>
      </div>

      <!-- Tab: Needs Review -->
      <div v-if="activeTab === 'needs_review'" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="auditData.needs_review_charts?.length === 0" class="p-12 text-center text-gray-400 text-sm">
          ✓ No size charts currently flagged for feedback review.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 font-semibold uppercase">
              <tr>
                <th class="px-6 py-3.5">Chart & Retailer</th>
                <th class="px-6 py-3.5">Category</th>
                <th class="px-6 py-3.5">Status & Alert</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="chart in auditData.needs_review_charts" :key="chart.id" class="hover:bg-gray-50/50">
                <td class="px-6 py-4">
                  <div class="font-bold text-sm text-gray-900 dark:text-white">{{ chart.name }}</div>
                  <div class="text-xs text-indigo-600 font-medium">{{ chart.retailer_name }}</div>
                </td>
                <td class="px-6 py-4 capitalize font-medium">{{ chart.category }}</td>
                <td class="px-6 py-4">
                  <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300">
                    <span>⚠️ Needs Review</span>
                  </span>
                  <p class="text-[11px] text-gray-500 mt-1">
                    Customer feedback exceeds 30% dissatisfaction threshold for at least one size.
                  </p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 1: Warnings Table -->
      <div v-if="activeTab === 'warnings'" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="loading" class="p-12 text-center text-gray-400 text-sm">
          Auditing charts...
        </div>
        <div v-else-if="auditData.charts_with_warnings?.length === 0" class="p-12 text-center text-gray-400 text-sm">
          ✓ No charts have active mathematical warnings or anomalies.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 font-semibold uppercase">
              <tr>
                <th class="px-6 py-3.5">Chart & Retailer</th>
                <th class="px-6 py-3.5">Category & Mode</th>
                <th class="px-6 py-3.5">Detected Warnings</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="chart in auditData.charts_with_warnings" :key="chart.id" class="hover:bg-gray-50/50">
                <td class="px-6 py-4">
                  <div class="font-bold text-sm text-gray-900 dark:text-white">{{ chart.name }}</div>
                  <div class="text-xs text-indigo-600 font-medium">{{ chart.retailer_name }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="capitalize font-medium">{{ chart.category }} ({{ chart.measured_as }})</div>
                  <div class="text-[11px] text-gray-400">Unit: {{ chart.unit_source }}</div>
                </td>
                <td class="px-6 py-4">
                  <ul class="space-y-1">
                    <li v-for="(warn, wIdx) in chart.warnings" :key="wIdx" class="text-rose-600 dark:text-rose-400 font-medium flex items-start gap-1.5">
                      <span class="text-rose-500 mt-0.5">⚠️</span>
                      <span>{{ warn }}</span>
                    </li>
                  </ul>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 2: Unverified Charts -->
      <div v-if="activeTab === 'unverified'" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="auditData.unverified_charts?.length === 0" class="p-12 text-center text-gray-400 text-sm">
          ✓ All charts in the database have been verified.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 font-semibold uppercase">
              <tr>
                <th class="px-6 py-3.5">Chart Name</th>
                <th class="px-6 py-3.5">Retailer</th>
                <th class="px-6 py-3.5">Category</th>
                <th class="px-6 py-3.5">Measurement Mode</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="chart in auditData.unverified_charts" :key="chart.id" class="hover:bg-gray-50/50">
                <td class="px-6 py-4 font-bold text-gray-900 dark:text-white">{{ chart.name }}</td>
                <td class="px-6 py-4 font-medium">{{ chart.retailer_name }}</td>
                <td class="px-6 py-4 capitalize">{{ chart.category }}</td>
                <td class="px-6 py-4 capitalize">{{ chart.measured_as }} ({{ chart.unit_source }})</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab 3: Demo Charts -->
      <div v-if="activeTab === 'demo'" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div v-if="auditData.demo_charts?.length === 0" class="p-12 text-center text-gray-400 text-sm">
          No seed demo charts present.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 font-semibold uppercase">
              <tr>
                <th class="px-6 py-3.5">Demo Chart Name</th>
                <th class="px-6 py-3.5">Retailer</th>
                <th class="px-6 py-3.5">Category</th>
                <th class="px-6 py-3.5">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="chart in auditData.demo_charts" :key="chart.id" class="hover:bg-gray-50/50">
                <td class="px-6 py-4 font-bold text-gray-900 dark:text-white">{{ chart.name }}</td>
                <td class="px-6 py-4 font-medium">{{ chart.retailer_name }}</td>
                <td class="px-6 py-4 capitalize">{{ chart.category }}</td>
                <td class="px-6 py-4">
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-100 text-amber-800">
                    is_demo = true
                  </span>
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
const activeTab = ref<'needs_review' | 'warnings' | 'unverified' | 'demo'>('needs_review')
const auditData = ref<any>({
  unverified_charts: [],
  demo_charts: [],
  charts_with_warnings: [],
  needs_review_charts: [],
  total_charts: 0,
  needs_review_count: 0,
  accuracy: { accuracy_pct: 0, acceptable_fit_count: 0, followed_recommendation_count: 0 },
})

const loadQualityAudit = async () => {
  loading.value = true
  try {
    const data = await apiFetch<any>('/v1/admin/data-quality')
    auditData.value = data || {}
  } catch (err: any) {
    showToast(err.message || 'Failed to run quality audit', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadQualityAudit()
})
</script>
