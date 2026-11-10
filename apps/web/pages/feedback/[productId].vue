<template>
  <div class="max-w-2xl mx-auto px-4 py-8 sm:py-12 space-y-8">
    <div>
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">
        {{ $t('feedback.title') }}
      </h1>
      <p class="text-sm text-gray-500 mt-1">
        {{ $t('feedback.subtitle') }}
      </p>
    </div>

    <!-- Product Summary Card -->
    <div v-if="product" class="p-5 bg-white rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between">
      <div>
        <span class="text-xs font-bold uppercase text-indigo-600">{{ product.retailers?.name }}</span>
        <h2 class="text-base font-bold text-gray-900">{{ product.name }}</h2>
      </div>
      <span class="text-xs px-2.5 py-1 bg-gray-100 text-gray-700 font-semibold rounded-lg capitalize">
        {{ product.category }}
      </span>
    </div>

    <!-- Feedback Form -->
    <form class="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-gray-100 space-y-6" @submit.prevent="submitFeedback">
      <!-- 1. Size Bought -->
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
          {{ $t('feedback.sizeBought') }}
        </label>
        <input
          v-model="sizeBought"
          type="text"
          required
          placeholder="e.g. M, L, or 32"
          class="w-full rounded-xl border border-gray-300 py-3 px-3.5 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
        />
      </div>

      <!-- 2. Fit Result (5 Visual Segmented Options) -->
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
          {{ $t('feedback.fitResult') }}
        </label>
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
          <button
            v-for="opt in fitResults"
            :key="opt.value"
            type="button"
            class="p-3 text-center rounded-2xl border transition flex flex-col items-center justify-center gap-1.5"
            :class="fitResult === opt.value ? 'bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-100' : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'"
            @click="fitResult = opt.value"
          >
            <span class="text-lg">{{ opt.icon }}</span>
            <span class="text-xs font-bold">{{ $t(`feedback.results.${opt.value}`) }}</span>
          </button>
        </div>
      </div>

      <!-- 3. Problem Area -->
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
          {{ $t('feedback.problemArea') }}
        </label>
        <select
          v-model="problemArea"
          class="w-full rounded-xl border border-gray-300 py-3 px-3.5 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
        >
          <option value="none">{{ $t('feedback.problemAreas.none') }}</option>
          <option value="chest">{{ $t('feedback.problemAreas.chest') }}</option>
          <option value="waist">{{ $t('feedback.problemAreas.waist') }}</option>
          <option value="hip">{{ $t('feedback.problemAreas.hip') }}</option>
          <option value="shoulder">{{ $t('feedback.problemAreas.shoulder') }}</option>
          <option value="sleeve">{{ $t('feedback.problemAreas.sleeve') }}</option>
          <option value="length">{{ $t('feedback.problemAreas.length') }}</option>
        </select>
      </div>

      <!-- 4. Was Returned Checkbox -->
      <div class="pt-2">
        <label class="flex items-center gap-3 cursor-pointer">
          <input
            v-model="wasReturned"
            type="checkbox"
            class="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300"
          />
          <span class="text-sm font-semibold text-gray-800">
            {{ $t('feedback.wasReturned') }}
          </span>
        </label>
      </div>

      <!-- 5. Additional Note -->
      <div>
        <label class="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
          {{ $t('feedback.note') }}
        </label>
        <textarea
          v-model="note"
          rows="3"
          class="w-full rounded-xl border border-gray-300 py-2.5 px-3.5 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
          placeholder="e.g. Sleeves were a bit tight around the cuffs..."
        ></textarea>
      </div>

      <!-- Submit Button -->
      <div>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full py-4 px-6 rounded-2xl font-bold text-base text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-lg shadow-indigo-100 disabled:opacity-50"
        >
          <span v-if="isSubmitting">{{ $t('common.loading') }}</span>
          <span v-else>{{ $t('feedback.submitBtn') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth'],
})

const route = useRoute()
const supabase = useSupabaseClient()
const user = useSupabaseUser()
const toast = useToast()
const localePath = useLocalePath()
const { t } = useI18n()

const productId = route.params.productId as string
const product = ref<any>(null)

const sizeBought = ref('')
const fitResult = ref<'too_tight' | 'slightly_tight' | 'perfect' | 'slightly_loose' | 'too_loose'>('perfect')
const problemArea = ref('none')
const wasReturned = ref(false)
const note = ref('')
const isSubmitting = ref(false)

const fitResults = [
  { value: 'too_tight', icon: '😣' },
  { value: 'slightly_tight', icon: '🤏' },
  { value: 'perfect', icon: '✨' },
  { value: 'slightly_loose', icon: '💨' },
  { value: 'too_loose', icon: '👕' },
] as const

onMounted(async () => {
  const { data } = await supabase
    .from('products')
    .select('*, retailers(name)')
    .eq('id', productId)
    .single()
  product.value = data
})

async function submitFeedback() {
  if (!user.value) return
  isSubmitting.value = true

  try {
    // Check consent: only attach body_snapshot if customer granted store_measurements consent
    let bodySnapshot: any = null
    const { data: consent } = await supabase
      .from('consents')
      .select('granted')
      .eq('user_id', user.value.id)
      .eq('consent_type', 'store_measurements')
      .single()

    if (consent?.granted) {
      const { data: bm } = await supabase
        .from('body_measurements')
        .select('*')
        .eq('user_id', user.value.id)
        .single()
      bodySnapshot = bm || null
    }

    await supabase.from('fit_feedback').upsert({
      user_id: user.value.id,
      product_id: productId,
      size_bought: sizeBought.value.trim().toUpperCase(),
      fit_result: fitResult.value,
      problem_area: problemArea.value,
      was_returned: wasReturned.value,
      note: note.value.trim() || null,
      body_snapshot: bodySnapshot,
    })

    toast.success(t('feedback.success'))
    navigateTo(localePath('/saved'))
  } catch (err: any) {
    toast.error(err.message || 'Failed to submit feedback')
  } finally {
    isSubmitting.value = false
  }
}
</script>

