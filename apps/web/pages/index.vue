<template>
  <div class="space-y-16 sm:space-y-24">
    <!-- Authenticated Customer Dashboard Header Banner -->
    <section v-if="user" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
      <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-8 sm:p-10 border border-slate-800 shadow-2xl relative overflow-hidden">
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-bold uppercase tracking-wider">
              <span>🇵🇰 Customer Intelligence Hub</span>
            </div>
            <h1 class="text-2xl sm:text-4xl font-black tracking-tight">
              Welcome back, <span class="text-indigo-400">{{ user.email?.split('@')[0] }}</span>
            </h1>
            <p class="text-sm text-slate-300 max-w-xl">
              Your universal profile is active. Get precision recommendations across 25+ verified Pakistani fashion brands.
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap items-center gap-3">
            <button
              type="button"
              @click="openAssistant"
              class="px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
            >
              <span>✨</span>
              <span>Ask AI Fit Assistant</span>
            </button>
            <NuxtLink
              :to="localePath('/brands')"
              class="px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition flex items-center gap-2"
            >
              <span>Explore Brands</span>
              <span>&rarr;</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Dashboard Quick Stats & Profile Readiness -->
        <div class="relative z-10 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8 mt-8 border-t border-slate-800/80">
          <div class="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50 flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-lg">
              ✓
            </div>
            <div>
              <p class="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Fit Engine</p>
              <p class="text-sm font-bold text-white">Deterministic Active</p>
            </div>
          </div>

          <div class="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50 flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-lg">
              📏
            </div>
            <div>
              <p class="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Universal Sizing</p>
              <NuxtLink :to="localePath('/profile')" class="text-sm font-bold text-indigo-300 hover:underline">
                View Measurements &rarr;
              </NuxtLink>
            </div>
          </div>

          <div class="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50 flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center font-bold text-lg">
              🛍️
            </div>
            <div>
              <p class="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Catalog</p>
              <p class="text-sm font-bold text-white">25+ Verified Brands</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Guest Hero Section -->
    <section v-else class="relative bg-gradient-to-b from-indigo-950 via-slate-900 to-slate-950 text-white py-20 sm:py-32 overflow-hidden border-b border-slate-800">
      <div class="relative max-w-5xl mx-auto px-4 text-center sm:px-6 lg:px-8 space-y-8">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-200 text-xs font-bold uppercase tracking-wider mb-2">
          <span>🇵🇰 Universal Fit Intelligence for Pakistan</span>
        </div>
        <h1 class="text-4xl sm:text-6xl font-black tracking-tight leading-tight">
          {{ $t('landing.hero.title') }}
        </h1>
        <p class="mx-auto max-w-2xl text-base sm:text-xl text-slate-300 font-normal leading-relaxed">
          {{ $t('landing.hero.subtitle') }}
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <NuxtLink
            :to="localePath('/brands')"
            class="w-full sm:w-auto px-8 py-4 rounded-2xl bg-white text-slate-950 font-black text-sm hover:bg-slate-100 transition shadow-2xl hover:scale-105 duration-200"
          >
            Explore Pakistani Brands &rarr;
          </NuxtLink>
          <NuxtLink
            :to="localePath('/try')"
            class="w-full sm:w-auto px-8 py-4 rounded-2xl bg-indigo-600/80 border border-indigo-500/40 text-white font-bold text-sm hover:bg-indigo-600 transition"
          >
            Find My Size
          </NuxtLink>
        </div>

        <!-- Brands Ticker -->
        <div class="pt-10 border-t border-slate-800 mt-12">
          <p class="text-xs uppercase tracking-widest text-indigo-300 font-bold mb-4">Supported Pakistani Brands</p>
          <div class="flex flex-wrap items-center justify-center gap-6 text-sm font-black tracking-wider text-slate-300">
            <NuxtLink :to="localePath('/brands/khaadi')" class="hover:text-white transition">KHAADI</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/sapphire')" class="hover:text-white transition">SAPPHIRE</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/junaid-jamshed')" class="hover:text-white transition">J.</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/outfitters')" class="hover:text-white transition">OUTFITTERS</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/limelight')" class="hover:text-white transition">LIMELIGHT</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/breakout')" class="hover:text-white transition">BREAKOUT</NuxtLink>
            <span>•</span>
            <NuxtLink :to="localePath('/brands/diners')" class="hover:text-white transition">DINERS</NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Pakistani Brands Spotlight -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <span class="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">Curated Directory</span>
          <h2 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight mt-1">
            Top Pakistani Fashion Labels
          </h2>
        </div>
        <NuxtLink
          :to="localePath('/brands')"
          class="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
        >
          View all 25+ brands &rarr;
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="brand in spotlightBrands"
          :key="brand.slug"
          class="group bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-200 flex flex-col justify-between"
        >
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60">
                Verified Sizing
              </span>
              <span class="text-[10px] text-slate-400 font-semibold">
                {{ brand.category }}
              </span>
            </div>

            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-black text-lg">
                {{ brand.name.charAt(0) }}
              </div>
              <div>
                <h3 class="font-bold text-base text-slate-900 dark:text-white group-hover:text-indigo-600 transition-colors">
                  {{ brand.name }}
                </h3>
                <p class="text-[11px] text-slate-400 font-mono">{{ brand.domain }}</p>
              </div>
            </div>

            <p class="text-xs text-slate-500 leading-relaxed line-clamp-2">
              {{ brand.description }}
            </p>
          </div>

          <div class="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <NuxtLink
              :to="localePath(`/try?retailer=${brand.slug}`)"
              class="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Find Size &rarr;
            </NuxtLink>
            <NuxtLink
              :to="localePath(`/brands/${brand.slug}`)"
              class="text-[11px] text-slate-400 hover:text-slate-600"
            >
              Details
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Sizing Problem & Deterministic Fit Engine Section -->
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white dark:bg-slate-900 p-8 sm:p-12 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-5">
        <span class="text-xs font-bold uppercase tracking-widest text-rose-600">The Problem Solved</span>
        <h2 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
          {{ $t('landing.problem.title') }}
        </h2>
        <p class="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed max-w-3xl">
          {{ $t('landing.problem.description') }}
        </p>

        <!-- Deterministic Zero-ML Callout -->
        <div class="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40 text-xs text-indigo-950 dark:text-indigo-200 flex items-start gap-3">
          <span class="text-lg">🛡️</span>
          <div>
            <p class="font-bold mb-0.5">Strict Sizing Authority Guarantee</p>
            <p>FitSense uses a deterministic, mathematical ease-band engine. AI assists by explaining results, answering fit questions, and translating advice, but your final recommended size is never guessed or altered by generative models.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div class="text-center space-y-2">
        <span class="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">Simple Process</span>
        <h2 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
          {{ $t('landing.howItWorks.title') }}
        </h2>
      </div>

      <div class="grid gap-6 sm:grid-cols-3">
        <div class="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
          <div class="w-12 h-12 bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center font-black text-xl">
            1
          </div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Create profile once</h3>
          <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{{ $t('landing.howItWorks.step1') }}</p>
        </div>

        <div class="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
          <div class="w-12 h-12 bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center font-black text-xl">
            2
          </div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Select any brand</h3>
          <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Pick your favourite brand and clothing category (Kurta, Shirt, Tee, Trousers, Kameez).
          </p>
        </div>

        <div class="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
          <div class="w-12 h-12 bg-indigo-50 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 rounded-2xl flex items-center justify-center font-black text-xl">
            3
          </div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white">Get exact size + ease</h3>
          <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{{ $t('landing.howItWorks.step3') }}</p>
        </div>
      </div>
    </section>

    <!-- B2B Section for Retailers -->
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-slate-900 text-white p-8 sm:p-12 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div class="space-y-2">
          <span class="text-xs font-bold uppercase tracking-widest text-indigo-400">B2B Intelligence</span>
          <h2 class="text-2xl font-black text-white">
            {{ $t('landing.retailers.title') }}
          </h2>
          <p class="text-sm text-slate-300 max-w-xl">
            Connect your brand catalogue, upload size charts with AI assistance, and eliminate sizing returns across Pakistan.
          </p>
        </div>
        <NuxtLink
          :to="localePath('/retailer/onboarding')"
          class="shrink-0 px-6 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition"
        >
          Register Your Brand &rarr;
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const user = useSupabaseUser()
const localePath = useLocalePath()

const isAssistantOpen = useState('fitsense_assistant_open', () => false)

const openAssistant = () => {
  isAssistantOpen.value = true
}

const spotlightBrands = [
  {
    name: 'Khaadi',
    slug: 'khaadi',
    domain: 'pk.khaadi.com',
    category: 'Eastern Pret / Unstitched',
    description: 'Pakistan lifestyle giant famous for vibrant hand-woven aesthetics, kurtas, and modern fusion wear.',
  },
  {
    name: 'Sapphire',
    slug: 'sapphire',
    domain: 'pk.sapphireonline.pk',
    category: 'Women & Men Fashion',
    description: 'High-street fashion leader delivering premium unstitched lawn, ready-to-wear kurtas, and men’s shirts.',
  },
  {
    name: 'J. (Junaid Jamshed)',
    slug: 'junaid-jamshed',
    domain: 'junaidjamshed.com',
    category: 'Traditional Eastern',
    description: 'Benchmark eastern clothing house for traditional shalwar kameez, festive waistcoats, and sherwanis.',
  },
  {
    name: 'Outfitters',
    slug: 'outfitters',
    domain: 'outfitters.com.pk',
    category: 'Western Streetwear',
    description: 'Youth fashion brand with oversized tees, cargo pants, winter hoodies, and denim collections.',
  },
]
</script>
