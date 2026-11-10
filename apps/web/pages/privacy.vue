<template>
  <div class="max-w-3xl mx-auto px-4 py-8 sm:py-12 space-y-8">
    <!-- Header -->
    <div class="space-y-2">
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">
        {{ $t('privacy.title') }}
      </h1>
      <p class="text-sm text-gray-500">
        {{ $t('privacy.subtitle') }}
      </p>
    </div>

    <!-- Legal Review Notice Alert -->
    <div class="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3 text-xs text-amber-900">
      <svg class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <span class="font-bold uppercase tracking-wider block mb-0.5">Notice</span>
        <p>{{ $t('privacy.legalNotice') }}</p>
      </div>
    </div>

    <!-- Privacy Policy Content -->
    <div class="bg-white p-6 sm:p-10 rounded-3xl shadow-sm border border-gray-100 space-y-6 text-sm text-gray-700 leading-relaxed">
      <div>
        <h2 class="text-base font-bold text-gray-900 mb-1">{{ $t('privacy.sections.whatWeCollect') }}</h2>
        <p>{{ $t('privacy.sections.whatWeCollectBody') }}</p>
      </div>

      <div>
        <h2 class="text-base font-bold text-gray-900 mb-1">{{ $t('privacy.sections.howWeUse') }}</h2>
        <p>{{ $t('privacy.sections.howWeUseBody') }}</p>
      </div>

      <div>
        <h2 class="text-base font-bold text-gray-900 mb-1">{{ $t('privacy.sections.rights') }}</h2>
        <p>{{ $t('privacy.sections.rightsBody') }}</p>
      </div>

      <!-- GDPR / Portability & Deletion Actions (For signed-in users) -->
      <div v-if="user" class="pt-6 border-t border-gray-100 flex flex-col sm:flex-row items-center gap-4">
        <button
          type="button"
          :disabled="isDownloading"
          class="w-full sm:w-auto px-5 py-3 rounded-xl border border-gray-300 hover:bg-gray-50 text-gray-800 font-semibold text-xs transition flex items-center justify-center gap-2"
          @click="downloadUserData"
        >
          <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>{{ isDownloading ? $t('common.loading') : $t('privacy.downloadBtn') }}</span>
        </button>

        <button
          type="button"
          class="w-full sm:w-auto px-5 py-3 rounded-xl bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-700 font-semibold text-xs transition flex items-center justify-center gap-2"
          @click="showDeleteModal = true"
        >
          <svg class="w-4 h-4 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>{{ $t('privacy.deleteAccountBtn') }}</span>
        </button>
      </div>
    </div>

    <!-- Permanent Deletion Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showDeleteModal = false"></div>
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-gray-100 text-center">
          <div class="w-12 h-12 mx-auto bg-rose-50 text-rose-600 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <div>
            <h3 class="text-lg font-bold text-gray-900">{{ $t('privacy.confirmModal.title') }}</h3>
            <p class="text-xs text-gray-600 mt-2">{{ $t('privacy.confirmModal.text') }}</p>
          </div>

          <div class="flex items-center justify-center gap-3">
            <button
              type="button"
              class="px-5 py-2.5 rounded-xl border border-gray-300 text-xs font-semibold text-gray-700 hover:bg-gray-50 transition"
              @click="showDeleteModal = false"
            >
              {{ $t('privacy.confirmModal.cancelBtn') }}
            </button>
            <button
              type="button"
              :disabled="isDeleting"
              class="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition shadow-md shadow-rose-200 disabled:opacity-50"
              @click="confirmDeleteAccount"
            >
              {{ isDeleting ? $t('common.loading') : $t('privacy.confirmModal.confirmBtn') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const toast = useToast()
const localePath = useLocalePath()

const isDownloading = ref(false)
const showDeleteModal = ref(false)
const isDeleting = ref(false)

async function downloadUserData() {
  isDownloading.value = true
  try {
    const data = await api.get('/v1/account/export')
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `fitsense-my-data-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
    toast.success('Data export downloaded successfully')
  } catch (err: any) {
    toast.error('Failed to export data')
  } finally {
    isDownloading.value = false
  }
}

async function confirmDeleteAccount() {
  isDeleting.value = true
  try {
    await api.delete('/v1/account')
    await supabase.auth.signOut()
    toast.info('Account and all measurements permanently deleted')
    showDeleteModal.value = false
    navigateTo(localePath('/'))
  } catch (err: any) {
    toast.error('Failed to delete account')
  } finally {
    isDeleting.value = false
  }
}
</script>

