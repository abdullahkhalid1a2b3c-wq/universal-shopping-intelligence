<template>
  <div class="min-h-screen bg-gray-50/50 dark:bg-gray-950 pb-20">
    <RetailerNav />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Top Action Bar -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Brand Size Charts</h2>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Maintain verified garment measurement tables. Accurate charts are the backbone of high-confidence size recommendations.
          </p>
        </div>

        <button
          v-if="!isEditing"
          @click="startCreateChart"
          class="px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-medium text-sm hover:bg-indigo-700 transition-colors shadow-sm flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Size Chart</span>
        </button>
      </div>

      <!-- LIST VIEW -->
      <div v-if="!isEditing">
        <div v-if="loading" class="p-12 text-center text-gray-400">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p class="text-sm">Loading size charts...</p>
        </div>

        <div v-else-if="sizeCharts.length === 0" class="bg-white dark:bg-gray-800 rounded-2xl p-12 text-center border border-gray-200 dark:border-gray-700">
          <svg class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p class="text-base font-medium text-gray-900 dark:text-white">No size charts created yet</p>
          <p class="text-xs text-gray-500 mt-1">Create your first chart manually or import from a brand CSV.</p>
          <button @click="startCreateChart" class="mt-4 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold">
            Create First Chart
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="chart in sizeCharts"
            :key="chart.id"
            class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm hover:border-indigo-300 dark:hover:border-indigo-700 transition-all flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-2 mb-3">
                <h3 class="font-bold text-gray-900 dark:text-white text-base">{{ chart.name }}</h3>
                <!-- Verified Badge -->
                <span
                  v-if="chart.verified_at"
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center gap-1"
                >
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  Verified
                </span>
                <span
                  v-else
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                >
                  Unverified
                </span>
              </div>

              <div class="space-y-1.5 text-xs text-gray-500 dark:text-gray-400">
                <div class="flex items-center justify-between">
                  <span>Category:</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200 capitalize">{{ formatCategory(chart.category) }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span>Measured As:</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200 capitalize">{{ chart.measured_as }}</span>
                </div>
                <div class="flex items-center justify-between">
                  <span>Source Unit:</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200 uppercase">{{ chart.unit_source }}</span>
                </div>
                <div v-if="chart.is_demo" class="mt-2 text-amber-600 dark:text-amber-400 font-semibold text-[11px]">
                  * Seed / Demo Data
                </div>
              </div>
            </div>

            <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between">
              <button
                @click="editChart(chart)"
                class="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Edit & Verify →
              </button>
              <button
                @click="deleteChart(chart.id)"
                class="text-xs text-rose-500 hover:text-rose-700 p-1"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- EDITOR VIEW -->
      <div v-else class="space-y-8">
        <!-- Editor Header Actions -->
        <div class="flex items-center justify-between bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <button @click="isEditing = false" class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h2 class="text-lg font-bold text-gray-900 dark:text-white">
                {{ activeChart.id ? 'Edit Size Chart' : 'New Size Chart' }}
              </h2>
              <p class="text-xs text-gray-400">All values are stored in centimetres (cm).</p>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              @click="showImportCSVModal = true"
              class="px-3.5 py-2 rounded-xl border border-gray-200 dark:border-gray-700 text-xs font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-1.5"
            >
              <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span>Import CSV</span>
            </button>
            <button
              @click="saveChart(false)"
              :disabled="saving"
              class="px-4 py-2 rounded-xl bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs font-semibold hover:opacity-90 disabled:opacity-50"
            >
              Save Draft
            </button>
          </div>
        </div>

        <!-- Layout Grid: Left = Meta & Side-by-side Source Image, Right = Editable Grid & Sanity Warnings -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <!-- LEFT COLUMN: Chart Details & Source Image Viewer (4 cols) -->
          <div class="lg:col-span-4 space-y-6">
            <!-- Chart Settings Card -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 space-y-4">
              <h3 class="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider">Chart Configuration</h3>

              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Chart Name *</label>
                <input
                  v-model="activeChart.name"
                  type="text"
                  placeholder="e.g. Khaadi Pret Stitched Kurta 2026"
                  class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-xs focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                  <select
                    v-model="activeChart.category"
                    @change="updateColumnsForCategory"
                    class="w-full p-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-xs"
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
                  <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Gender</label>
                  <select
                    v-model="activeChart.gender_category"
                    class="w-full p-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-xs"
                  >
                    <option value="womens">Womens</option>
                    <option value="mens">Mens</option>
                    <option value="unisex">Unisex</option>
                  </select>
                </div>
              </div>

              <!-- Measured As Selector with Visual Explainer -->
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Measured As *
                </label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    @click="setMeasuredAs('circumference')"
                    :class="[
                      'p-2.5 rounded-xl border text-xs font-medium text-left transition-all',
                      activeChart.measured_as === 'circumference'
                        ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-bold'
                        : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400'
                    ]"
                  >
                    <div class="font-semibold mb-0.5">Circumference (360°)</div>
                    <div class="text-[10px] text-gray-400">Total body or garment circumference (e.g. Chest 96–104 cm).</div>
                  </button>

                  <button
                    type="button"
                    @click="setMeasuredAs('flat')"
                    :class="[
                      'p-2.5 rounded-xl border text-xs font-medium text-left transition-all',
                      activeChart.measured_as === 'flat'
                        ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-bold'
                        : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400'
                    ]"
                  >
                    <div class="font-semibold mb-0.5">Flat (Laid Flat)</div>
                    <div class="text-[10px] text-gray-400">Garment measured flat seam-to-seam (e.g. Chest 48–52 cm).</div>
                  </button>
                </div>
              </div>

              <!-- Source Unit Selector -->
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Original Source Unit
                </label>
                <div class="flex items-center gap-3">
                  <label class="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="radio"
                      value="cm"
                      v-model="activeChart.unit_source"
                      class="text-indigo-600 focus:ring-indigo-500"
                    />
                    <span>Centimetres (cm)</span>
                  </label>
                  <label class="flex items-center gap-2 text-xs cursor-pointer">
                    <input
                      type="radio"
                      value="in"
                      v-model="activeChart.unit_source"
                      class="text-indigo-600 focus:ring-indigo-500"
                    />
                    <span>Inches (in)</span>
                  </label>
                </div>
              </div>

              <!-- Source Note & Date -->
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Source Note / Link</label>
                <input
                  v-model="activeChart.source_note"
                  type="text"
                  placeholder="e.g. Brand size guide page (captured Nov 2026)"
                  class="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-xs focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <!-- Published Chart Image Upload & Viewer -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider">Source Chart Image</h3>
                <label class="cursor-pointer text-xs font-semibold text-indigo-600 hover:underline">
                  <span>Upload / Replace</span>
                  <input type="file" accept="image/*" class="hidden" @change="uploadSourceImage" />
                </label>
              </div>

              <p class="text-xs text-gray-500">
                Upload a screenshot or photo of the brand's published size chart to verify values side-by-side.
              </p>

              <!-- Image Display -->
              <div v-if="sourceImageUrl" class="relative rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden max-h-96 bg-gray-900/5">
                <img :src="sourceImageUrl" alt="Source size chart" class="w-full object-contain cursor-zoom-in" />
              </div>

              <div v-else class="p-8 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-xl text-center text-gray-400">
                <svg class="w-8 h-8 mx-auto mb-2 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-xs">No source image uploaded yet.</p>
              </div>
            </div>
          </div>

          <!-- RIGHT COLUMN: Editable Grid, Sanity Alerts & Verification (8 cols) -->
          <div class="lg:col-span-8 space-y-6">
            <!-- Sanity Warnings Panel -->
            <div v-if="sanityWarnings.length > 0" class="p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs">
              <div class="flex items-center gap-2 font-bold text-amber-800 dark:text-amber-300 mb-2">
                <svg class="w-5 h-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Automated Sanity Check Warnings ({{ sanityWarnings.length }})</span>
              </div>
              <p class="text-amber-700 dark:text-amber-300/80 mb-3">
                FitSense detected unusual sizing patterns. To mark this chart as <strong>Verified</strong>, either fix the values or acknowledge each warning if it accurately reflects the retailer's published chart:
              </p>
              <div class="space-y-2">
                <label
                  v-for="(warn, idx) in sanityWarnings"
                  :key="idx"
                  class="flex items-start gap-2.5 p-2 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-amber-200/60 dark:border-amber-800/40 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    v-model="acknowledgedWarnings[idx]"
                    class="mt-0.5 rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span class="text-amber-900 dark:text-amber-200">{{ warn }}</span>
                </label>
              </div>
            </div>

            <!-- Editable Grid Card -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
              <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <div>
                  <h3 class="font-bold text-gray-900 dark:text-white text-sm">Measurement Grid</h3>
                  <p class="text-xs text-gray-400">Rows = Sizes. Columns = Measurement dimensions in cm.</p>
                </div>
                <button
                  type="button"
                  @click="addSizeRow"
                  class="px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold text-xs hover:bg-indigo-100 flex items-center gap-1"
                >
                  + Add Size Row
                </button>
              </div>

              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                  <thead class="bg-gray-50/75 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 uppercase tracking-wider text-gray-500 font-semibold">
                    <tr>
                      <th class="px-4 py-3 w-28">Size Label</th>
                      <th v-for="col in activeColumns" :key="col" class="px-4 py-3 capitalize">
                        {{ col }} (cm)
                      </th>
                      <th class="px-4 py-3 w-16 text-right">Del</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                    <tr v-for="(row, rIdx) in gridRows" :key="rIdx" class="hover:bg-gray-50/30 dark:hover:bg-gray-900/20">
                      <td class="px-4 py-2.5">
                        <input
                          v-model="row.size_label"
                          @input="triggerSanityCheck"
                          type="text"
                          placeholder="e.g. S, 32"
                          class="w-full px-2.5 py-1.5 font-bold uppercase rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
                        />
                      </td>
                      <td v-for="col in activeColumns" :key="col" class="px-4 py-2.5">
                        <input
                          v-model.number="row[col]"
                          @input="triggerSanityCheck"
                          type="number"
                          step="0.5"
                          placeholder="—"
                          class="w-20 px-2 py-1.5 font-mono rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 focus:ring-1 focus:ring-indigo-500"
                        />
                      </td>
                      <td class="px-4 py-2.5 text-right">
                        <button
                          type="button"
                          @click="removeSizeRow(rIdx)"
                          class="text-rose-500 hover:text-rose-700 text-sm p-1"
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Verification Action Banner -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div class="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-2">
                  <span>Verification Status:</span>
                  <span v-if="activeChart.verified_at" class="text-emerald-600 dark:text-emerald-400">Verified</span>
                  <span v-else class="text-amber-500">Unverified Draft</span>
                </div>
                <p class="text-xs text-gray-400 mt-0.5">
                  Verified size charts are prioritized by the recommendation engine and trusted by shoppers.
                </p>
              </div>

              <div class="flex items-center gap-3">
                <button
                  type="button"
                  @click="saveChart(true)"
                  :disabled="!canMarkVerified || saving"
                  class="px-5 py-2.5 rounded-xl bg-emerald-600 text-white font-semibold text-xs hover:bg-emerald-700 transition-colors shadow-sm disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span>{{ activeChart.verified_at ? 'Update & Re-verify' : 'Mark as Verified' }}</span>
                </button>
              </div>
            </div>

            <!-- "TEST THIS CHART" Panel -->
            <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 flex items-center justify-center">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 class="font-bold text-sm text-gray-900 dark:text-white">Test This Chart Live</h3>
                </div>
                <span class="text-xs text-gray-400">Simulate customer body measurements</span>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div>
                  <label class="block text-gray-500 mb-1">Chest (cm)</label>
                  <input v-model.number="testBody.chest" type="number" class="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 font-mono" />
                </div>
                <div>
                  <label class="block text-gray-500 mb-1">Waist (cm)</label>
                  <input v-model.number="testBody.waist" type="number" class="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 font-mono" />
                </div>
                <div>
                  <label class="block text-gray-500 mb-1">Hip (cm)</label>
                  <input v-model.number="testBody.hip" type="number" class="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 font-mono" />
                </div>
                <div>
                  <label class="block text-gray-500 mb-1">Fit Style</label>
                  <select v-model="testFitPreference" class="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <option value="fitted">Fitted</option>
                    <option value="regular">Regular</option>
                    <option value="loose">Loose</option>
                  </select>
                </div>
              </div>

              <div class="flex items-center justify-between pt-2">
                <button
                  type="button"
                  @click="runChartTest"
                  :disabled="testingChart"
                  class="px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 flex items-center gap-1.5"
                >
                  <span v-if="testingChart" class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></span>
                  <span>Run Recommendation Engine</span>
                </button>

                <!-- Recommendation Result -->
                <div v-if="testResult" class="flex items-center gap-3 bg-gray-50 dark:bg-gray-900 px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700">
                  <span class="text-xs text-gray-500">Recommended Size:</span>
                  <span class="text-base font-extrabold text-indigo-600 dark:text-indigo-400 font-mono">{{ testResult.recommended_size }}</span>
                  <span class="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                    {{ testResult.confidence_score }}% Confidence
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CSV Import Modal -->
    <div v-if="showImportCSVModal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-3xl max-w-xl w-full p-6 border border-gray-100 dark:border-gray-700 shadow-2xl">
        <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700 mb-4">
          <h3 class="text-base font-bold text-gray-900 dark:text-white">Import Size Chart CSV</h3>
          <button @click="showImportCSVModal = false" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div class="space-y-4 text-xs">
          <div class="flex items-center justify-between p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-800 dark:text-indigo-300">
            <span>Download CSV template for this category:</span>
            <button @click="downloadTemplate" class="px-3 py-1 rounded-lg bg-indigo-600 text-white font-semibold">
              Download Template
            </button>
          </div>

          <div>
            <label class="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Paste CSV Text</label>
            <textarea
              v-model="csvText"
              rows="6"
              placeholder="size_label,chest,waist,hip,shoulder,length&#10;S,96,82,98,43,70&#10;M,102,88,104,45,72"
              class="w-full p-3 font-mono rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
            ></textarea>
          </div>

          <div v-if="csvErrors.length > 0" class="p-3 rounded-xl bg-rose-50 text-rose-700">
            <ul class="list-disc pl-4 space-y-0.5">
              <li v-for="(err, idx) in csvErrors" :key="idx">{{ err }}</li>
            </ul>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button @click="showImportCSVModal = false" class="px-4 py-2 rounded-xl border text-gray-600">Cancel</button>
            <button @click="applyImportedCSV" class="px-4 py-2 rounded-xl bg-indigo-600 text-white font-semibold">
              Preview & Populate Grid
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

definePageMeta({
  middleware: ['retailer'],
})

const { currentRetailer, fetchRetailerProfile } = useRetailer()
const { showToast } = useToast()
const { apiFetch } = useApi()
const supabase = useSupabaseClient()
const user = useSupabaseUser()

const loading = ref(true)
const saving = ref(false)
const sizeCharts = ref<any[]>([])
const isEditing = ref(false)

const sourceImageUrl = ref<string | null>(null)
const sanityWarnings = ref<string[]>([])
const acknowledgedWarnings = ref<boolean[]>([])

const showImportCSVModal = ref(false)
const csvText = ref('')
const csvErrors = ref<string[]>([])

// Test chart state
const testingChart = ref(false)
const testBody = reactive({ chest: 98, waist: 82, hip: 98 })
const testFitPreference = ref('regular')
const testResult = ref<any>(null)

const activeChart = reactive({
  id: '',
  name: '',
  category: 'shirt',
  gender_category: 'mens',
  measured_as: 'circumference',
  unit_source: 'cm',
  source_note: '',
  verified_at: null as string | null,
})

const gridRows = ref<any[]>([
  { size_label: 'S', chest: 96, waist: 82, shoulder: 43, length: 70, sleeve: 61 },
  { size_label: 'M', chest: 102, waist: 88, shoulder: 45, length: 72, sleeve: 62 },
  { size_label: 'L', chest: 108, waist: 94, shoulder: 47, length: 74, sleeve: 63 },
  { size_label: 'XL', chest: 114, waist: 100, shoulder: 49, length: 76, sleeve: 64 },
])

const activeColumns = computed(() => {
  if (['trouser', 'jeans'].includes(activeChart.category)) {
    return ['waist', 'hip', 'inseam', 'thigh', 'rise', 'length']
  }
  return ['chest', 'shoulder', 'length', 'sleeve', 'waist', 'hip']
})

const canMarkVerified = computed(() => {
  if (sanityWarnings.value.length === 0) return true
  // All warnings must be checked/acknowledged
  return sanityWarnings.value.every((_, idx) => acknowledgedWarnings.value[idx] === true)
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

const loadSizeCharts = async () => {
  if (!currentRetailer.value) {
    await fetchRetailerProfile()
  }
  if (!currentRetailer.value) return

  loading.value = true
  try {
    const { data, error } = await supabase
      .table('size_charts')
      .select('*')
      .eq('retailer_id', currentRetailer.value.id)
      .order('created_at', { ascending: false })

    if (error) throw error
    sizeCharts.value = data || []
  } catch (err: any) {
    showToast(err.message || 'Failed to load size charts', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSizeCharts()
})

const startCreateChart = () => {
  activeChart.id = ''
  activeChart.name = ''
  activeChart.category = 'shirt'
  activeChart.gender_category = 'mens'
  activeChart.measured_as = 'circumference'
  activeChart.unit_source = 'cm'
  activeChart.source_note = ''
  activeChart.verified_at = null
  sourceImageUrl.value = null

  gridRows.value = [
    { size_label: 'S', chest: 96, waist: 82, shoulder: 43, length: 70, sleeve: 61 },
    { size_label: 'M', chest: 102, waist: 88, shoulder: 45, length: 72, sleeve: 62 },
    { size_label: 'L', chest: 108, waist: 94, shoulder: 47, length: 74, sleeve: 63 },
    { size_label: 'XL', chest: 114, waist: 100, shoulder: 49, length: 76, sleeve: 64 },
  ]
  sanityWarnings.value = []
  acknowledgedWarnings.value = []
  isEditing.value = true
  triggerSanityCheck()
}

const editChart = async (chart: any) => {
  activeChart.id = chart.id
  activeChart.name = chart.name
  activeChart.category = chart.category
  activeChart.gender_category = chart.gender_category || 'mens'
  activeChart.measured_as = chart.measured_as || 'circumference'
  activeChart.unit_source = chart.unit_source || 'cm'
  activeChart.source_note = chart.source_note || ''
  activeChart.verified_at = chart.verified_at
  sourceImageUrl.value = null

  // Fetch rows
  const { data: rows } = await supabase
    .table('size_chart_rows')
    .select('size_label, measurement_key, value_cm')
    .eq('size_chart_id', chart.id)

  if (rows && rows.length > 0) {
    // Transform rows from key-value to grid rows
    const sizeMap: Record<string, any> = {}
    for (const r of rows) {
      if (!sizeMap[r.size_label]) {
        sizeMap[r.size_label] = { size_label: r.size_label }
      }
      sizeMap[r.size_label][r.measurement_key] = r.value_cm
    }
    gridRows.value = Object.values(sizeMap)
  }

  isEditing.value = true
  triggerSanityCheck()
}

const setMeasuredAs = (mode: 'flat' | 'circumference') => {
  activeChart.measured_as = mode
  triggerSanityCheck()
}

const updateColumnsForCategory = () => {
  if (['trouser', 'jeans'].includes(activeChart.category)) {
    gridRows.value = [
      { size_label: '30', waist: 76, hip: 94, inseam: 78, thigh: 56, rise: 25, length: 102 },
      { size_label: '32', waist: 81, hip: 99, inseam: 79, thigh: 58, rise: 26, length: 103 },
      { size_label: '34', waist: 86, hip: 104, inseam: 80, thigh: 60, rise: 27, length: 104 },
    ]
  }
  triggerSanityCheck()
}

const addSizeRow = () => {
  const row: Record<string, any> = { size_label: '' }
  activeColumns.value.forEach((c) => {
    row[c] = null
  })
  gridRows.value.push(row)
}

const removeSizeRow = (idx: number) => {
  gridRows.value.splice(idx, 1)
  triggerSanityCheck()
}

const triggerSanityCheck = async () => {
  try {
    const res = await apiFetch<any>('/v1/retailer/size-charts/validate', {
      method: 'POST',
      body: {
        rows: gridRows.value,
        measured_as: activeChart.measured_as,
        category: activeChart.category,
        gender_category: activeChart.gender_category,
      },
    })
    sanityWarnings.value = res.warnings || []
    acknowledgedWarnings.value = new Array(sanityWarnings.value.length).fill(false)
  } catch {
    // Fallback silent
  }
}

const uploadSourceImage = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !currentRetailer.value) return

  try {
    const path = `${currentRetailer.value.id}/${Date.now()}-${file.name}`
    const { error: uploadErr } = await supabase.storage
      .from('size-chart-images')
      .upload(path, file)

    if (uploadErr) throw uploadErr

    const { data: urlData } = supabase.storage
      .from('size-chart-images')
      .getPublicUrl(path)

    sourceImageUrl.value = urlData.publicUrl
    showToast('Source screenshot uploaded successfully', 'success')
  } catch (err: any) {
    showToast(err.message || 'Image upload failed', 'error')
  }
}

const downloadTemplate = async () => {
  try {
    const text = await apiFetch<string>(`/v1/retailer/size-charts/template?category=${activeChart.category}`)
    const blob = new Blob([text], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `fitsense-${activeChart.category}-template.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    showToast('Failed to download template', 'error')
  }
}

const applyImportedCSV = async () => {
  csvErrors.value = []
  try {
    const res = await apiFetch<any>('/v1/retailer/size-charts/parse-csv', {
      method: 'POST',
      body: {
        csv_content: csvText.value,
        unit_source: activeChart.unit_source,
        measured_as: activeChart.measured_as,
        category: activeChart.category,
      },
    })

    if (!res.success && res.errors?.length > 0) {
      csvErrors.value = res.errors
      return
    }

    if (res.rows && res.rows.length > 0) {
      gridRows.value = res.rows
      showToast(`Populated grid with ${res.rows.length} sizes from CSV`, 'success')
      showImportCSVModal.value = false
      csvText.value = ''
      triggerSanityCheck()
    }
  } catch (err: any) {
    csvErrors.value = [err.message || 'Failed to parse CSV']
  }
}

const saveChart = async (markVerified = false) => {
  if (!currentRetailer.value) return
  if (!activeChart.name.trim()) {
    showToast('Please enter a name for this size chart', 'error')
    return
  }

  saving.value = true
  try {
    const chartPayload: any = {
      retailer_id: currentRetailer.value.id,
      name: activeChart.name.trim(),
      category: activeChart.category,
      gender_category: activeChart.gender_category,
      measured_as: activeChart.measured_as,
      unit_source: activeChart.unit_source,
      source_note: activeChart.source_note.trim() || null,
    }

    if (markVerified) {
      chartPayload.verified_at = new Date().toISOString()
      chartPayload.verified_by = user.value?.id || null
    }

    let chartId = activeChart.id

    if (chartId) {
      const { error } = await supabase
        .table('size_charts')
        .update(chartPayload)
        .eq('id', chartId)
      if (error) throw error
    } else {
      const { data: newChart, error } = await supabase
        .table('size_charts')
        .insert(chartPayload)
        .select()
        .single()
      if (error) throw error
      chartId = newChart.id
      activeChart.id = newChart.id
    }

    // Replace size_chart_rows
    await supabase.table('size_chart_rows').delete().eq('size_chart_id', chartId)

    const rowInserts: any[] = []
    gridRows.value.forEach((row, sIdx) => {
      const sizeLabel = String(row.size_label || '').trim().toUpperCase()
      if (!sizeLabel) return

      activeColumns.value.forEach((colKey) => {
        const val = row[colKey]
        if (val !== undefined && val !== null && val !== '') {
          rowInserts.push({
            size_chart_id: chartId,
            size_label: sizeLabel,
            measurement_key: colKey,
            value_cm: Number(val),
            sort_order: sIdx,
          })
        }
      })
    })

    if (rowInserts.length > 0) {
      const { error: rowsErr } = await supabase.table('size_chart_rows').insert(rowInserts)
      if (rowsErr) throw rowsErr
    }

    showToast(markVerified ? 'Size chart verified and published!' : 'Size chart draft saved', 'success')
    isEditing.value = false
    loadSizeCharts()
  } catch (err: any) {
    showToast(err.message || 'Failed to save size chart', 'error')
  } finally {
    saving.value = false
  }
}

const deleteChart = async (id: string) => {
  if (!confirm('Are you sure you want to delete this size chart? Products using it will lose their sizing reference.')) return
  try {
    const { error } = await supabase.table('size_charts').delete().eq('id', id)
    if (error) throw error
    sizeCharts.value = sizeCharts.value.filter((c) => c.id !== id)
    showToast('Size chart deleted', 'success')
  } catch (err: any) {
    showToast(err.message || 'Failed to delete size chart', 'error')
  }
}

const runChartTest = async () => {
  testingChart.value = true
  testResult.value = null

  try {
    // 1. Find or pick a product linked to this chart, or use test engine
    const { data: prods } = await supabase
      .table('products')
      .select('id')
      .eq('size_chart_id', activeChart.id)
      .limit(1)

    const productId = prods?.[0]?.id

    if (!productId) {
      showToast('To test this chart live, at least one product must be linked to it.', 'info')
      // Fallback preview: pick size based on lowest delta
      let bestSize = gridRows.value[0]?.size_label || 'M'
      let minDelta = 999
      gridRows.value.forEach((r) => {
        const cVal = activeChart.measured_as === 'flat' ? (r.chest || 50) * 2 : (r.chest || 100)
        const d = Math.abs(cVal - testBody.chest)
        if (d < minDelta) {
          minDelta = d
          bestSize = r.size_label
        }
      })
      testResult.value = {
        recommended_size: bestSize,
        confidence_score: 85,
      }
      return
    }

    const rec = await apiFetch<any>('/v1/recommend', {
      method: 'POST',
      body: {
        product_id: productId,
        fit_preference: testFitPreference.value,
        measurements: {
          chest: testBody.chest,
          waist: testBody.waist,
          hip: testBody.hip,
        },
      },
    })

    testResult.value = {
      recommended_size: rec.recommendation.recommended_size,
      confidence_score: rec.recommendation.confidence_score,
      explanation: rec.explanation,
    }
  } catch (err: any) {
    showToast(err.message || 'Test recommendation failed', 'error')
  } finally {
    testingChart.value = false
  }
}
</script>
