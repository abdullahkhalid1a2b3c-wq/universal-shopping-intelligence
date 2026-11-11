<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-8 sm:py-12 relative overflow-hidden">
    <!-- Ambient Background Glows -->
    <div class="pointer-events-none absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-b from-indigo-600/20 via-purple-600/10 to-transparent blur-3xl opacity-70"></div>
    <div class="pointer-events-none absolute -bottom-40 right-10 w-[450px] h-[450px] bg-purple-600/15 blur-3xl rounded-full"></div>
    <div class="pointer-events-none absolute -bottom-40 left-10 w-[450px] h-[450px] bg-indigo-600/15 blur-3xl rounded-full"></div>

    <div class="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
      
      <!-- Left Fashion Showcase Glimpse (Women's Pret & Ethnic Fashion) -->
      <div class="hidden lg:flex lg:col-span-3 flex-col gap-4 animate-fadeIn">
        <div class="group relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-2xl transition hover:border-indigo-500/40">
          <div class="aspect-[3/4] relative overflow-hidden">
            <img
              src="/images/fashion/women-pret.jpg"
              alt="Pakistani Women's Embroidered Pret"
              class="w-full h-full object-cover object-top transition duration-700 group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
            <div class="absolute top-3 left-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-rose-500/20 text-rose-300 border border-rose-400/30 backdrop-blur-md">
                <span>🌸</span> Women's Pret
              </span>
            </div>
            <div class="absolute bottom-4 inset-x-4 space-y-1">
              <p class="text-xs font-black text-white tracking-wide">
                Khaadi & Sapphire Pret
              </p>
              <p class="text-[11px] text-slate-300 leading-snug">
                Calibrated bust, waist & shoulder ease for ready-to-wear kurtas.
              </p>
            </div>
          </div>
        </div>

        <!-- Trust Metric Card -->
        <div class="p-4 rounded-2xl border border-slate-800/80 bg-slate-900/40 backdrop-blur-sm text-xs space-y-1.5">
          <div class="flex items-center gap-2 text-indigo-400 font-bold">
            <span>✨</span>
            <span>1-Time Universal Setup</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-relaxed">
            Save your measurements once. Never worry about different size charts across Pakistani stores again.
          </p>
        </div>
      </div>

      <!-- Center: Obsidian Luxury Modern Login Card -->
      <div class="lg:col-span-6 w-full max-w-md mx-auto">
        <div class="bg-slate-900/90 backdrop-blur-2xl p-7 sm:p-10 rounded-3xl shadow-2xl border border-slate-800 relative space-y-7">
          
          <!-- Top subtle glow strip -->
          <div class="absolute top-0 inset-x-8 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent"></div>

          <!-- Header -->
          <div class="text-center space-y-2">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-400/20 text-indigo-300 text-[11px] font-extrabold uppercase tracking-wider">
              <span>🇵🇰 Universal Size Intelligence</span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black text-white tracking-tight">
              {{ $t('auth.loginTitle') }}
            </h2>
            <p class="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-xs mx-auto">
              {{ $t('auth.loginSubtitle') }}
            </p>
          </div>

          <!-- Form -->
          <form class="space-y-5" @submit.prevent="handleLogin">
            <!-- Error Banner -->
            <div
              v-if="errorMessage"
              class="p-4 bg-rose-950/60 border border-rose-800/80 rounded-2xl text-xs font-semibold text-rose-200 leading-relaxed animate-fadeIn"
            >
              <div class="flex items-start gap-2">
                <span class="text-rose-400 text-sm">⚠️</span>
                <span>{{ errorMessage }}</span>
              </div>
            </div>

            <!-- Email Field -->
            <div class="space-y-1.5">
              <label for="email" class="block text-xs font-bold uppercase tracking-wider text-slate-300">
                {{ $t('auth.emailLabel') }}
              </label>
              <div class="relative">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.206" />
                  </svg>
                </div>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  required
                  style="color-scheme: dark;"
                  class="w-full rounded-2xl border border-slate-700 bg-slate-800/90 pl-11 pr-4 py-3.5 text-sm text-white font-medium placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 transition shadow-inner"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <!-- Password Field with Show/Hide -->
            <div class="space-y-1.5">
              <label for="password" class="block text-xs font-bold uppercase tracking-wider text-slate-300">
                {{ $t('auth.passwordLabel') }}
              </label>
              <div class="relative">
                <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  style="color-scheme: dark;"
                  class="w-full rounded-2xl border border-slate-700 bg-slate-800/90 pl-11 pr-11 py-3.5 text-sm text-white font-medium placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 transition shadow-inner"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center pr-4 text-slate-400 hover:text-white transition"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-4 px-6 rounded-2xl font-black text-sm text-white bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition-all shadow-xl shadow-indigo-600/30 hover:scale-[1.01] active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <span v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              <span v-if="loading">{{ $t('common.loading') }}</span>
              <span v-else class="flex items-center gap-2">
                <span>🔐</span>
                <span>{{ $t('auth.loginBtn') }}</span>
              </span>
            </button>

            <!-- Bottom Navigation Links -->
            <div class="pt-2 text-center space-y-2">
              <div>
                <NuxtLink
                  :to="localePath('/signup')"
                  class="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition"
                >
                  {{ $t('auth.noAccount') }}
                </NuxtLink>
              </div>
              <div>
                <NuxtLink
                  :to="localePath('/try')"
                  class="text-[11px] font-semibold text-slate-400 hover:text-slate-200 transition"
                >
                  ⚡ Or continue as Guest to test sizing &rarr;
                </NuxtLink>
              </div>
            </div>
          </form>
        </div>
      </div>

      <!-- Right Fashion Showcase Glimpses (Men's & Kids Fashion) -->
      <div class="hidden lg:flex lg:col-span-3 flex-col gap-4 animate-fadeIn">
        <!-- Men's Card -->
        <div class="group relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-2xl transition hover:border-indigo-500/40">
          <div class="aspect-[4/3] relative overflow-hidden">
            <img
              src="/images/fashion/men-style.jpg"
              alt="Cougar Men's Contemporary Fashion"
              class="w-full h-full object-cover object-top transition duration-700 group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
            <div class="absolute top-3 left-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-400/30 backdrop-blur-md">
                <span>🧥</span> Men's Style
              </span>
            </div>
            <div class="absolute bottom-3 inset-x-3">
              <p class="text-xs font-black text-white">Cougar Men's Collection</p>
              <p class="text-[10px] text-slate-300">Jackets, shirts & tailored denim sizing</p>
            </div>
          </div>
        </div>

        <!-- Kids Card -->
        <div class="group relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-2xl transition hover:border-indigo-500/40">
          <div class="aspect-[4/3] relative overflow-hidden">
            <img
              src="/images/fashion/kids-wear.jpg"
              alt="Cougar Kids Fashion"
              class="w-full h-full object-cover object-center transition duration-700 group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
            <div class="absolute top-3 left-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 backdrop-blur-md">
                <span>🎈</span> Kids Collection
              </span>
            </div>
            <div class="absolute bottom-3 inset-x-3">
              <p class="text-xs font-black text-white">Junior Fashion Wear</p>
              <p class="text-[10px] text-slate-300">Height-based children's sizing</p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Mobile Fashion Glimpse Strip (Visible on mobile/tablet) -->
    <div class="lg:hidden mt-8 w-full max-w-md mx-auto grid grid-cols-3 gap-2">
      <div class="rounded-2xl overflow-hidden border border-slate-800 relative aspect-square">
        <img src="/images/fashion/women-pret.jpg" alt="Women" class="w-full h-full object-cover object-top" />
        <div class="absolute inset-0 bg-slate-950/40 flex items-end p-1.5">
          <span class="text-[9px] font-bold text-white">Women</span>
        </div>
      </div>
      <div class="rounded-2xl overflow-hidden border border-slate-800 relative aspect-square">
        <img src="/images/fashion/men-style.jpg" alt="Men" class="w-full h-full object-cover object-top" />
        <div class="absolute inset-0 bg-slate-950/40 flex items-end p-1.5">
          <span class="text-[9px] font-bold text-white">Men</span>
        </div>
      </div>
      <div class="rounded-2xl overflow-hidden border border-slate-800 relative aspect-square">
        <img src="/images/fashion/kids-wear.jpg" alt="Kids" class="w-full h-full object-cover object-center" />
        <div class="absolute inset-0 bg-slate-950/40 flex items-end p-1.5">
          <span class="text-[9px] font-bold text-white">Kids</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const supabase = useSupabaseClient()
const localePath = useLocalePath()
const route = useRoute()
const toast = useToast()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
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
    const redirectUrl = String(route.query.redirect || '')
    if (redirectUrl.startsWith('/') && !redirectUrl.startsWith('//')) {
      await navigateTo(redirectUrl)
    } else {
      await navigateTo(localePath('/profile'))
    }
  } catch (err: any) {
    errorMessage.value = err.message || 'An unexpected error occurred during login'
  } finally {
    loading.value = false
  }
}
</script>
