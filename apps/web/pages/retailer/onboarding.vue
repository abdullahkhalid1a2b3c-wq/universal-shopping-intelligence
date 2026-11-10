<template>
  <div class="max-w-2xl mx-auto px-4 py-12">
    <div class="bg-white dark:bg-gray-800 rounded-3xl p-8 border border-gray-100 dark:border-gray-700 shadow-xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-14 h-14 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Register Your Fashion Brand</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Connect your store to FitSense to reduce sizing returns and boost customer sizing confidence.
        </p>
      </div>

      <!-- Pending Verification Policy Callout -->
      <div class="p-4 mb-6 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs text-amber-800 dark:text-amber-300">
        <p class="font-semibold mb-1">Status Policy Notice:</p>
        <p>New retailer accounts are registered with <strong>pending</strong> status. Once created, you can immediately add your products and upload size charts. They will become visible to all public shoppers and the browser extension as soon as our admin team verifies your brand domain.</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Retailer Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Brand / Retailer Name <span class="text-rose-500">*</span>
          </label>
          <input
            v-model="form.name"
            @input="generateSlug"
            type="text"
            required
            placeholder="e.g. Khaadi, Sapphire, Breakout"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
          />
        </div>

        <!-- Slug -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Unique Slug <span class="text-rose-500">*</span>
          </label>
          <div class="flex items-center">
            <span class="px-3 py-3 rounded-l-xl border border-r-0 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 text-xs text-gray-500">
              fitsense.pk/
            </span>
            <input
              v-model="form.slug"
              type="text"
              required
              placeholder="brand-name"
              class="w-full px-4 py-3 rounded-r-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-mono"
            />
          </div>
          <p class="text-xs text-gray-400 mt-1">Used for catalog identification and extension URL matching.</p>
        </div>

        <!-- Website Domain -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Official Website Domain
          </label>
          <input
            v-model="form.website_domain"
            type="text"
            placeholder="e.g. khaadi.com or pk.sapphireonline.pk"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
          />
        </div>

        <!-- Cash on Delivery -->
        <div class="flex items-center gap-3 p-4 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/50">
          <input
            v-model="form.supports_cod"
            id="supports_cod"
            type="checkbox"
            class="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-700"
          />
          <label for="supports_cod" class="text-sm font-medium text-gray-800 dark:text-gray-200 cursor-pointer">
            Supports Cash on Delivery (COD) in Pakistan
          </label>
        </div>

        <!-- Return Policy URL -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Return & Exchange Policy Link
          </label>
          <input
            v-model="form.return_policy_url"
            type="url"
            placeholder="https://brand.pk/pages/returns-exchange"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
          />
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="submitting || !form.name || !form.slug"
          class="w-full py-4 px-6 rounded-xl font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <span v-if="submitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
          <span>Create Retailer Profile</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const { createRetailer, currentRetailer } = useRetailer()
const { showToast } = useToast()
const localePath = useLocalePath()

const submitting = ref(false)

const form = reactive({
  name: '',
  slug: '',
  website_domain: '',
  supports_cod: true,
  return_policy_url: '',
})

const generateSlug = () => {
  form.slug = form.name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    const res = await createRetailer({
      name: form.name,
      slug: form.slug,
      website_domain: form.website_domain,
      supports_cod: form.supports_cod,
      return_policy_url: form.return_policy_url,
    })

    if (res.success) {
      showToast('Retailer profile registered successfully (pending verification).', 'success')
      navigateTo(localePath('/retailer/products'))
    } else {
      showToast(res.error || 'Failed to create retailer', 'error')
    }
  } catch (err: any) {
    showToast(err.message || 'An error occurred', 'error')
  } finally {
    submitting.value = false
  }
}
</script>
