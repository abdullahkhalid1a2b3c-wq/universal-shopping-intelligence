<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold tracking-tight text-gray-900">
          {{ $t('auth.signupTitle') }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          {{ $t('auth.signupSubtitle') }}
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleSignup">
        <!-- Error Banner -->
        <div v-if="errorMessage" class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700">
          {{ errorMessage }}
        </div>

        <!-- Success/Info Banner -->
        <div v-if="successMessage" class="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-800 leading-relaxed">
          {{ successMessage }}
        </div>

        <div class="space-y-4 rounded-md">
          <div>
            <label for="email" class="block text-sm font-semibold text-gray-700 mb-1">
              {{ $t('auth.emailLabel') }}
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 mb-1">
              {{ $t('auth.passwordLabel') }}
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              minlength="6"
              required
              class="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
              placeholder="At least 6 characters"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-3.5 px-4 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition shadow-md shadow-indigo-100 disabled:opacity-50"
          >
            <span v-if="loading">{{ $t('common.loading') }}</span>
            <span v-else>{{ $t('auth.signupBtn') }}</span>
          </button>
        </div>

        <div class="text-center">
          <NuxtLink :to="localePath('/login')" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
            {{ $t('auth.hasAccount') }}
          </NuxtLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient()
const localePath = useLocalePath()
const toast = useToast()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleSignup() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const { data, error } = await supabase.auth.signUp({
      email: email.value.trim(),
      password: password.value,
    })

    if (error) {
      errorMessage.value = error.message
      return
    }

    if (data?.session) {
      toast.success(t('auth.signupSuccess'))
      await navigateTo(localePath('/onboarding'))
    } else if (data?.user && !data.session) {
      // Email confirmation is required by Supabase
      successMessage.value = "Account created! A confirmation email has been sent. Please click the link in your email to confirm your account, then proceed to Log in. (Or turn off 'Confirm email' in your Supabase Auth dashboard for instant local testing)."
    }
  } catch (err: any) {
    errorMessage.value = err.message || 'An error occurred during registration'
  } finally {
    loading.value = false
  }
}
</script>

