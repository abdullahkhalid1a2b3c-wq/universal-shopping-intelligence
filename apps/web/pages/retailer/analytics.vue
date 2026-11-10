<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <RetailerNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <!-- Title & Export -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Fit Analytics & Feedback</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Real customer sizing metrics, fit feedback distributions, and post-purchase return diagnostics.
          </p>
        </div>

        <button
          @click="exportAnalyticsCSV"
          :disabled="loading"
          class="px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2 shadow-sm"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>Export Analytics CSV</span>
        </button>
      </div>

      <!-- KPI Summary Cards -->
      <!-- Size Charts Needing Review Warning Banner -->
      <div v-if="analyticsData.charts_needing_review?.length > 0" class="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200">
        <div class="flex items-center gap-2 font-bold text-sm">
          <span>⚠️</span>
          <span>{{ analyticsData.charts_needing_review.length }} Size Chart(s) Flagged for Review</span>
        </div>
        <p class="text-xs text-amber-700 dark:text-amber-300 mt-1">
          Customer feedback has identified sizing discrepancies (>30% reported too tight or too loose) on products linked to these charts.
        </p>
        <div class="mt-2 flex flex-wrap gap-2">
          <span
            v-for="c in analyticsData.charts_needing_review"
            :key="c.id"
            class="px-2.5 py-1 bg-white dark:bg-gray-800 rounded-lg text-xs font-semibold border border-amber-300 dark:border-amber-700"
          >
            {{ c.name }} ({{ c.category }})
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Recommendations</div>
          <div class="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 font-mono">
            {{ totalRecommendations }}
          </div>
          <p class="text-[11px] text-gray-400 mt-1">Generated via web size finder & extension</p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Feedback Responses</div>
          <div class="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {{ totalFeedbackCount }}
          </div>
          <p class="text-[11px] text-gray-400 mt-1">Post-purchase customer ratings</p>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm">
          <div class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Return Reports</div>
          <div class="text-3xl font-extrabold text-rose-600 dark:text-rose-400 font-mono">
            {{ analyticsData.total_returns || 0 }}
          </div>
          <p class="text-[11px] text-gray-400 mt-1">Reported size-related returns</p>
        </div>
      </div>

      <!-- Actionable Plain-Language Sizing Hints -->
      <div v-if="analyticsData.plain_language_hints?.length > 0" class="p-6 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900">
        <div class="flex items-center gap-2 mb-3 text-indigo-900 dark:text-indigo-200 font-bold text-sm">
          <svg class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>FitSense Automated Diagnostic Hints</span>
        </div>
        <div class="space-y-2">
          <div
            v-for="(hint, idx) in analyticsData.plain_language_hints"
            :key="idx"
            class="p-3 rounded-xl bg-white dark:bg-gray-800 border border-indigo-100 dark:border-indigo-900/60 text-xs text-gray-800 dark:text-gray-200 flex items-start gap-2.5 shadow-sm"
          >
            <span class="inline-block w-2 h-2 rounded-full bg-indigo-500 mt-1 flex-shrink-0"></span>
            <span>{{ hint }}</span>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Weekly Recommendations Line Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-sm text-gray-900 dark:text-white mb-1">Recommendations Over Time</h3>
            <p class="text-xs text-gray-400 mb-4">Weekly volume of size recommendations generated for your products.</p>
          </div>
          <div class="h-64 relative">
            <canvas ref="weeklyChartCanvas"></canvas>
            <div v-if="!hasWeeklyData" class="absolute inset-0 flex items-center justify-center text-xs text-gray-400">
              No weekly recommendation events recorded yet.
            </div>
          </div>
        </div>

        <!-- Stacked Fit Feedback Distribution Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col justify-between">
          <div>
            <h3 class="font-bold text-sm text-gray-900 dark:text-white mb-1">Fit Distribution by Product & Size</h3>
            <p class="text-xs text-gray-400 mb-4">Stacked breakdown: Too Tight vs Perfect vs Too Loose.</p>
          </div>
          <div class="h-64 relative">
            <canvas ref="feedbackChartCanvas"></canvas>
            <div v-if="!hasFeedbackData" class="absolute inset-0 flex items-center justify-center text-xs text-gray-400">
              No customer fit feedback submitted yet.
            </div>
          </div>
        </div>
      </div>

      <!-- Problem Products Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <h3 class="font-bold text-base text-gray-900 dark:text-white">Flagged Problem Products</h3>
            <span class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
              Threshold: >25% Tight or Loose
            </span>
          </div>
          <p class="text-xs text-gray-500 mt-1">
            Products where buyers report consistent fit discrepancies (requires at least 10 responses for statistical confidence).
          </p>
        </div>

        <div v-if="analyticsData.problem_products?.length === 0" class="p-12 text-center text-gray-400 text-sm">
          ✓ No problem products detected. Sizing across all products is within acceptable tolerance.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 text-gray-500 font-semibold uppercase tracking-wider">
              <tr>
                <th class="px-6 py-3.5">Product Name</th>
                <th class="px-6 py-3.5">Size</th>
                <th class="px-6 py-3.5">Issue Detected</th>
                <th class="px-6 py-3.5">Discrepancy %</th>
                <th class="px-6 py-3.5">Responses</th>
                <th class="px-6 py-3.5">Diagnostic Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-gray-700 dark:text-gray-300">
              <tr v-for="(item, idx) in analyticsData.problem_products" :key="idx" class="hover:bg-gray-50/50 dark:hover:bg-gray-900/30">
                <td class="px-6 py-4 font-semibold text-gray-900 dark:text-white">
                  {{ item.product_name }}
                </td>
                <td class="px-6 py-4 font-mono font-bold">
                  {{ item.size_label }}
                </td>
                <td class="px-6 py-4 capitalize font-medium" :class="item.problem_type.includes('small') ? 'text-rose-600' : 'text-amber-600'">
                  {{ item.problem_type }}
                </td>
                <td class="px-6 py-4 font-mono font-bold">
                  {{ Number(item.percentage).toFixed(0) }}%
                </td>
                <td class="px-6 py-4 font-mono">
                  {{ item.total_responses }}
                </td>
                <td class="px-6 py-4">
                  <span v-if="item.has_sufficient_sample" class="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300">
                    High Confidence Problem
                  </span>
                  <span v-else class="text-[11px] text-gray-400 italic">
                    {{ item.note || 'Sample size < 10' }}
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
import { ref, computed, onMounted, nextTick } from 'vue'
import {
  Chart,
  LineController,
  BarController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

Chart.register(
  LineController,
  BarController,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

definePageMeta({
  middleware: ['retailer'],
})

const { currentRetailer, fetchRetailerProfile } = useRetailer()
const { apiFetch } = useApi()
const { showToast } = useToast()

const loading = ref(true)
const analyticsData = ref<any>({
  recommendations_per_week: [],
  feedback_distribution: [],
  problem_products: [],
  total_returns: 0,
  plain_language_hints: [],
})

const weeklyChartCanvas = ref<HTMLCanvasElement | null>(null)
const feedbackChartCanvas = ref<HTMLCanvasElement | null>(null)
let weeklyChartInstance: Chart | null = null
let feedbackChartInstance: Chart | null = null

const totalRecommendations = computed(() => {
  return (analyticsData.value.recommendations_per_week || []).reduce(
    (sum: number, w: any) => sum + (Number(w.count) || 0),
    0
  )
})

const totalFeedbackCount = computed(() => {
  return (analyticsData.value.feedback_distribution || []).reduce(
    (sum: number, f: any) => sum + (Number(f.total_feedback) || 0),
    0
  )
})

const hasWeeklyData = computed(() => {
  return (analyticsData.value.recommendations_per_week || []).length > 0
})

const hasFeedbackData = computed(() => {
  return (analyticsData.value.feedback_distribution || []).length > 0
})

const loadAnalytics = async () => {
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }
  if (!currentRetailer.value) return

  loading.value = true
  try {
    const data = await apiFetch<any>(`/v1/retailer/analytics?retailer_id=${currentRetailer.value.id}`)
    analyticsData.value = data || {}

    await nextTick()
    renderCharts()
  } catch (err: any) {
    showToast(err.message || 'Failed to load analytics', 'error')
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  // 1. Weekly Line Chart
  if (weeklyChartCanvas.value) {
    if (weeklyChartInstance) weeklyChartInstance.destroy()

    const weeks = (analyticsData.value.recommendations_per_week || []).map((w: any) => w.week)
    const counts = (analyticsData.value.recommendations_per_week || []).map((w: any) => w.count)

    // Fallback placeholder data if empty so the chart renders cleanly
    const displayLabels = weeks.length > 0 ? weeks : ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    const displayCounts = counts.length > 0 ? counts : [0, 0, 0, 0]

    weeklyChartInstance = new Chart(weeklyChartCanvas.value, {
      type: 'line',
      data: {
        labels: displayLabels,
        datasets: [
          {
            label: 'Recommendations',
            data: displayCounts,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          y: { beginAtZero: true },
        },
      },
    })
  }

  // 2. Feedback Stacked Bar Chart
  if (feedbackChartCanvas.value) {
    if (feedbackChartInstance) feedbackChartInstance.destroy()

    const dist = analyticsData.value.feedback_distribution || []
    const labels = dist.map((d: any) => `${d.product_name} (${d.size_label})`)
    const tightData = dist.map((d: any) => d.pct_too_tight)
    const perfectData = dist.map((d: any) => d.pct_perfect)
    const looseData = dist.map((d: any) => d.pct_too_loose)

    const displayLabels = labels.length > 0 ? labels : ['Product A (M)', 'Product B (L)']
    const displayTight = tightData.length > 0 ? tightData : [20, 10]
    const displayPerfect = perfectData.length > 0 ? perfectData : [70, 85]
    const displayLoose = looseData.length > 0 ? looseData : [10, 5]

    feedbackChartInstance = new Chart(feedbackChartCanvas.value, {
      type: 'bar',
      data: {
        labels: displayLabels,
        datasets: [
          {
            label: 'Too Tight / Small',
            data: displayTight,
            backgroundColor: '#f43f5e',
          },
          {
            label: 'Spot On / Perfect',
            data: displayPerfect,
            backgroundColor: '#10b981',
          },
          {
            label: 'Too Loose / Large',
            data: displayLoose,
            backgroundColor: '#f59e0b',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true },
          y: { stacked: true, max: 100 },
        },
        plugins: {
          legend: { position: 'bottom' },
        },
      },
    })
  }
}

const exportAnalyticsCSV = () => {
  const rows: string[] = []
  rows.push('Section,Item,Metric,Value')

  // Recommendations
  rows.push(`Summary,Recommendations,Total,${totalRecommendations.value}`)
  rows.push(`Summary,Feedback,Total,${totalFeedbackCount.value}`)
  rows.push(`Summary,Returns,Total,${analyticsData.value.total_returns || 0}`)

  // Weekly data
  ;(analyticsData.value.recommendations_per_week || []).forEach((w: any) => {
    rows.push(`Weekly Recommendations,${w.week},Count,${w.count}`)
  })

  // Feedback distribution
  ;(analyticsData.value.feedback_distribution || []).forEach((f: any) => {
    rows.push(`Feedback Distribution,${f.product_name} Size ${f.size_label},Too Tight %,${f.pct_too_tight}`)
    rows.push(`Feedback Distribution,${f.product_name} Size ${f.size_label},Perfect %,${f.pct_perfect}`)
    rows.push(`Feedback Distribution,${f.product_name} Size ${f.size_label},Too Loose %,${f.pct_too_loose}`)
  })

  // Problem products
  ;(analyticsData.value.problem_products || []).forEach((p: any) => {
    rows.push(`Problem Products,${p.product_name} Size ${p.size_label},${p.problem_type},${p.percentage}% (${p.total_responses} responses)`)
  })

  const blob = new Blob([rows.join('\n')], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `fitsense-analytics-${currentRetailer.value?.slug || 'retailer'}.csv`
  a.click()
  URL.revokeObjectURL(url)
  showToast('Analytics CSV exported successfully', 'success')
}

onMounted(() => {
  loadAnalytics()
})
</script>
