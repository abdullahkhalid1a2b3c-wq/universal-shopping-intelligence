<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold tracking-tight text-gray-900">
          {{ $t('auth.loginTitle') }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          {{ $t('auth.loginSubtitle') }}
        </p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <!-- Error Banner -->
        <div v-if="errorMessage" class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700">
          {{ errorMessage }}
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
              required
              class="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-indigo-600 focus:ring-1 focus:ring-indigo-600"
              placeholder="••••••••"
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
            <span v-else>{{ $t('auth.loginBtn') }}</span>
          </button>
        </div>

        <div class="text-center">
          <NuxtLink :to="localePath('/signup')" class="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
            {{ $t('auth.noAccount') }}
          </NuxtLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
const supabase = useSupabaseClient()
const localePath = useLocalePath()
const route = useRoute()
const toast = useToast()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    const { error } = await supabase.auth.signInWithPassword({
      email: email.value.trim(),
      password: password.value,
    })

    if (error) {
      const msg = error.message.toLowerCase()
      if (msg.includes('invalid login credentials')) {
        errorMessage.value = "Invalid email or password. If you haven't created an account yet, please click 'Sign up' below first."
      } else if (msg.includes('email not confirmed')) {
        errorMessage.value = "Email not confirmed. Please check your inbox for the Supabase confirmation email, or turn off 'Confirm email' in your Supabase Auth dashboard."
      } else {
        errorMessage.value = error.message
      }
      return
    }

    toast.success(t('auth.loginSuccess'))
    const redirectUrl = (route.query.redirect as string) || localePath('/profile')
    await navigateTo(redirectUrl)
  } catch (err: any) {
    errorMessage.value = err.message || 'An error occurred during sign in'
  } finally {
    loading.value = false
  }
}
</script>

