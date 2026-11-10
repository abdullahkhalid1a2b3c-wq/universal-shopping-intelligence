<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:py-12 space-y-8">
    <div>
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">
        {{ $t('saved.title') }}
      </h1>
      <p class="text-sm text-gray-500 mt-1">
        {{ $t('saved.subtitle') }}
      </p>
    </div>

    <!-- Empty State -->
    <div
      v-if="!isLoading && savedItems.length === 0"
      class="text-center py-16 px-4 bg-white rounded-3xl border border-gray-100 space-y-4"
    >
      <div class="w-16 h-16 mx-auto bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
      </div>
      <p class="text-sm font-medium text-gray-600 max-w-sm mx-auto">
        {{ $t('saved.empty') }}
      </p>
      <NuxtLink
        :to="localePath('/try')"
        class="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-md transition"
      >
        {{ $t('nav.try') }}
      </NuxtLink>
    </div>

    <!-- Items Grid -->
    <div v-else class="space-y-4">
      <div
        v-for="item in savedItems"
        :key="item.id"
        class="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition hover:border-indigo-100"
      >
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-indigo-600 uppercase tracking-wider">
              {{ item.products?.retailers?.name || 'Retailer' }}
            </span>
            <span class="text-xs text-gray-300">•</span>
            <span class="text-xs text-gray-500 capitalize">{{ item.products?.category }}</span>
          </div>
          <h3 class="text-base font-bold text-gray-900">
            {{ item.products?.name }}
          </h3>
          <p class="text-xs text-gray-500">
            Recommended Size: <span class="font-bold text-indigo-700 text-sm ml-1">{{ item.size_label }}</span>
          </p>

          <!-- 5-Day Post-Purchase Prompt -->
          <div
            v-if="isOlderThanFiveDays(item.created_at) && item.status !== 'bought'"
            class="mt-3 p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 space-y-2"
          >
            <p class="font-bold">{{ $t('saved.buyPrompt') }}</p>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg transition"
                @click="onMarkBought(item)"
              >
                {{ $t('saved.boughtBtn') }}
              </button>
              <button
                type="button"
                class="px-3 py-1.5 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition"
                @click="dismissPrompt(item.id)"
              >
                {{ $t('saved.dismissBtn') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
          <a
            v-if="item.products?.product_url"
            :href="item.products.product_url"
            target="_blank"
            rel="noopener noreferrer"
            class="px-4 py-2 text-xs font-bold rounded-xl bg-gray-900 text-white hover:bg-black transition flex items-center gap-1.5"
          >
            <span>Visit Store</span>
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>

          <NuxtLink
            :to="localePath(`/feedback/${item.product_id}`)"
            class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
          >
            {{ $t('saved.feedbackBtn') }} &rarr;
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth'],
})

const supabase = useSupabaseClient()
const user = useSupabaseUser()
const localePath = useLocalePath()
const toast = useToast()

const savedItems = ref<any[]>([])
const isLoading = ref(true)

onMounted(async () => {
  if (!user.value) return
  try {
    const { data } = await supabase
      .from('saved_items')
      .select('*, products(*, retailers(*))')
      .eq('user_id', user.value.id)
      .neq('status', 'dismissed')
      .order('created_at', { ascending: false })
    savedItems.value = data || []
  } finally {
    isLoading.value = false
  }
})

function isOlderThanFiveDays(createdAt: string): boolean {
  if (!createdAt) return false
  const diffMs = Date.now() - new Date(createdAt).getTime()
  // Greater than 5 days in milliseconds
  return diffMs > 5 * 24 * 60 * 60 * 1000
}

async function onMarkBought(item: any) {
  await supabase
    .from('saved_items')
    .update({ status: 'bought', bought_at: new Date().toISOString() })
    .eq('id', item.id)

  navigateTo(localePath(`/feedback/${item.product_id}`))
}

async function dismissPrompt(id: string) {
  await supabase.from('saved_items').update({ status: 'dismissed' }).eq('id', id)
  savedItems.value = savedItems.value.filter((i) => i.id !== id)
  toast.info('Item dismissed')
}
</script>

