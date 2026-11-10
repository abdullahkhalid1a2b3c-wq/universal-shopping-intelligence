<template>
  <div :dir="direction" :class="locale === 'ur' ? 'font-urdu' : 'font-sans'" class="min-h-screen bg-slate-50/70 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased">
    <!-- Global Toasts -->
    <ToastNotification />

    <!-- Global Beta Banner -->
    <div class="bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 text-indigo-100 px-4 py-1.5 text-xs text-center border-b border-indigo-500/20 flex items-center justify-center gap-2">
      <span class="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-bold uppercase tracking-wider text-[10px] border border-indigo-400/30">Beta</span>
      <span class="font-medium text-slate-300">FitSense is in active beta preview.</span>
      <a
        v-if="feedbackUrl"
        :href="feedbackUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="underline font-bold text-indigo-400 hover:text-indigo-300 transition ml-1"
      >
        Share feedback &rarr;
      </a>
    </div>

    <!-- AI Fit Assistant Floating Widget -->
    <AIFitAssistant />

    <!-- Interactive Flying Clothing Humor Bird -->
    <ClothingHumorBird />

    <!-- Navigation Header -->
    <header class="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 border-b border-slate-200/60 dark:border-slate-800 transition-colors">
      <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <!-- Logo & Main Navigation -->
        <div class="flex items-center gap-7">
          <NuxtLink :to="localePath('/')" class="flex items-center gap-2.5 text-xl font-black tracking-tight text-indigo-600 dark:text-indigo-400 group">
            <span class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white flex items-center justify-center font-black text-sm shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              F
            </span>
            <div class="flex flex-col">
              <span class="leading-none font-black text-slate-900 dark:text-white">FitSense</span>
              <span class="text-[9px] text-indigo-500 font-semibold tracking-widest uppercase">Universal Fit</span>
            </div>
          </NuxtLink>

          <!-- Desktop Links -->
          <div class="hidden md:flex items-center gap-5 text-sm font-semibold text-slate-600 dark:text-slate-300">
            <NuxtLink :to="localePath('/brands')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition flex items-center gap-1.5">
              <span>🇵🇰</span>
              <span>Brands Directory</span>
            </NuxtLink>
            <NuxtLink :to="localePath('/try')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
              {{ $t('nav.try') }}
            </NuxtLink>
            <NuxtLink v-if="user" :to="localePath('/saved')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
              {{ $t('nav.saved') }}
            </NuxtLink>
            <NuxtLink v-if="user" :to="localePath('/profile')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
              {{ $t('nav.profile') }}
            </NuxtLink>
            <NuxtLink v-if="user" :to="localePath('/retailer/products')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
              Retailer Hub
            </NuxtLink>
            <NuxtLink v-if="user && currentRole === 'admin'" :to="localePath('/admin/retailers')" class="text-indigo-600 dark:text-indigo-400 font-bold hover:underline">
              Admin
            </NuxtLink>
          </div>
        </div>

        <!-- Right Side: AI Assistant Pill, Language, Auth -->
        <div class="flex items-center gap-3">
          <!-- AI Assistant Header Button -->
          <button
            type="button"
            @click="toggleAssistant"
            class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200/60 dark:border-indigo-800/60 hover:bg-indigo-100 transition shadow-sm"
          >
            <span>✨</span>
            <span>Ask AI</span>
          </button>

          <LanguageSwitcher />

          <!-- User Authenticated -->
          <div v-if="user" class="flex items-center gap-3">
            <NuxtLink
              :to="localePath('/profile')"
              class="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 transition border border-slate-200/60 dark:border-slate-700"
            >
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span class="max-w-[130px] truncate">{{ user.email }}</span>
            </NuxtLink>
            <button
              type="button"
              class="text-xs font-semibold text-slate-500 hover:text-rose-600 transition"
              @click="handleLogout"
            >
              {{ $t('nav.logout') }}
            </button>
          </div>

          <!-- Guest State -->
          <div v-else class="flex items-center gap-2">
            <NuxtLink
              :to="localePath('/login')"
              class="text-xs font-semibold px-3 py-2 text-slate-700 dark:text-slate-300 hover:text-indigo-600 transition"
            >
              {{ $t('nav.login') }}
            </NuxtLink>
            <NuxtLink
              :to="localePath('/signup')"
              class="text-xs font-bold px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 transition"
            >
              {{ $t('nav.signup') }}
            </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- Mobile Submenu Bar -->
      <div class="md:hidden flex items-center justify-around py-2.5 border-t border-slate-100 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-400 bg-white/60 dark:bg-slate-900/60">
        <NuxtLink :to="localePath('/brands')" class="hover:text-indigo-600 py-1">
          Brands
        </NuxtLink>
        <NuxtLink :to="localePath('/try')" class="hover:text-indigo-600 py-1">
          {{ $t('nav.try') }}
        </NuxtLink>
        <NuxtLink v-if="user" :to="localePath('/saved')" class="hover:text-indigo-600 py-1">
          {{ $t('nav.saved') }}
        </NuxtLink>
        <NuxtLink v-if="user" :to="localePath('/profile')" class="hover:text-indigo-600 py-1">
          {{ $t('nav.profile') }}
        </NuxtLink>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 pb-16">
      <slot />
    </main>

    <!-- Premium Footer -->
    <footer class="bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 py-10 text-xs text-slate-500 dark:text-slate-400">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
        <div class="space-y-1">
          <p class="font-bold text-slate-800 dark:text-slate-200">
            FitSense — Universal Fit Intelligence for Pakistan
          </p>
          <p class="text-[11px] text-slate-400">
            Precision deterministic size calculations powered by verified Pakistani fashion charts.
          </p>
        </div>
        <div class="flex items-center gap-5 font-medium">
          <NuxtLink :to="localePath('/brands')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
            Brand Directory
          </NuxtLink>
          <NuxtLink :to="localePath('/try')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
            Find My Size
          </NuxtLink>
          <NuxtLink :to="localePath('/privacy')" class="hover:text-indigo-600 dark:hover:text-indigo-400 transition">
            {{ $t('nav.privacy') }}
          </NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue'

const config = useRuntimeConfig()
const feedbackUrl = computed(() => config.public.feedbackUrl || '')
const user = useSupabaseUser()
const supabase = useSupabaseClient()
const localePath = useLocalePath()
const { locale } = useI18n()
const toast = useToast()

const currentRole = ref('customer')
const isAssistantOpen = useState('fitsense_assistant_open', () => false)

const toggleAssistant = () => {
  isAssistantOpen.value = !isAssistantOpen.value
}

watchEffect(async () => {
  if (user.value) {
    const { data } = await supabase
      .from('profiles')
      .select('role')
      .eq('user_id', user.value.id)
      .maybeSingle()
    if (data?.role) {
      currentRole.value = data.role
    }
  } else {
    currentRole.value = 'customer'
  }
})

const direction = computed(() => (locale.value === 'ur' ? 'rtl' : 'ltr'))

async function handleLogout() {
  await supabase.auth.signOut()
  toast.info('Logged out')
  navigateTo(localePath('/login'))
}
</script>

<style>
.font-urdu {
  font-family: 'Noto Naskh Arabic', 'Noto Nastaliq Urdu', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.75;
}
</style>
