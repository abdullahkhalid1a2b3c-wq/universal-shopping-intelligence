<template>
  <div class="pointer-events-none fixed inset-0 z-50 overflow-hidden">
    <!-- Flying Sparrow with High-Contrast Humor Banner -->
    <transition
      enter-active-class="transition-opacity duration-500 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-700 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isVisible"
        class="pointer-events-auto absolute top-28 sm:top-32 flex items-center gap-3 fly-across cursor-pointer select-none group"
        title="Hover to pause & read! Click ✕ to dismiss."
      >
        <!-- Illustrated Animated Flying Sparrow SVG -->
        <div class="relative w-14 h-12 shrink-0 drop-shadow-[0_4px_12px_rgba(99,102,241,0.5)] sparrow-flutter">
          <svg viewBox="0 0 100 80" class="w-full h-full" fill="none">
            <!-- Tail Feathers -->
            <path d="M15 48 L2 58 L12 42 Z" fill="#7C3AED" />
            <path d="M18 45 L0 50 L14 38 Z" fill="#6366F1" />
            <!-- Bird Body -->
            <ellipse cx="45" cy="42" rx="26" ry="17" fill="#4F46E5" />
            <path d="M30 40 Q45 55 62 44 Q50 32 30 40 Z" fill="#6366F1" />
            <!-- Soft Belly -->
            <ellipse cx="48" cy="46" rx="16" ry="10" fill="#E0E7FF" opacity="0.95" />
            <!-- Bird Head -->
            <circle cx="68" cy="30" r="14" fill="#4338CA" />
            <!-- Cute Eye -->
            <circle cx="73" cy="28" r="4.5" fill="#FFFFFF" />
            <circle cx="74.5" cy="27.5" r="2.2" fill="#0F172A" />
            <circle cx="75.5" cy="26.5" r="1" fill="#FFFFFF" />
            <!-- Golden Beak -->
            <polygon points="80,31 98,34 80,39" fill="#F59E0B" />
            <polygon points="80,34 94,36 80,39" fill="#D97706" />
            <!-- Beak Holding Ribbon Thread -->
            <line x1="88" y1="36" x2="88" y2="48" stroke="#FBBF24" stroke-width="2.5" stroke-linecap="round" />
            <!-- Flapping Wing -->
            <path
              d="M38 38 C32 12, 54 2, 60 16 C63 26, 52 38, 38 38 Z"
              fill="#A5B4FC"
              class="wing-flap"
            />
          </svg>
        </div>

        <!-- High-Contrast Glowing Humor Banner -->
        <div class="relative flex items-center bg-slate-950/95 backdrop-blur-xl text-white px-5 py-3 rounded-2xl shadow-[0_10px_35px_rgba(245,158,11,0.35)] border-2 border-amber-400 font-bold max-w-xs sm:max-w-md ring-1 ring-amber-400/40">
          <!-- Ribbon Fishtail Notch Left -->
          <div class="absolute -left-2 top-1/2 -translate-y-1/2 w-3 h-3 bg-amber-400 transform rotate-45 shadow-sm"></div>

          <div class="flex-1 space-y-0.5 pr-2">
            <div class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-amber-400">
              <span>🧵 Tailor Wisdom</span>
              <span class="text-slate-500">•</span>
              <span class="text-slate-400 text-[9px] lowercase">(hover to pause)</span>
            </div>
            <p class="text-xs sm:text-sm font-black text-white leading-snug drop-shadow-md">
              {{ currentJoke }}
            </p>
          </div>

          <!-- Close button -->
          <button
            type="button"
            class="ml-2 -mr-1 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            @click.stop="dismissBird"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      </div>
    </transition>

    <!-- Bottom-Left Flying Humor Launcher Button -->
    <div class="pointer-events-auto fixed bottom-6 left-6 z-40">
      <button
        type="button"
        @click="triggerSparrow"
        class="group flex items-center gap-2 px-3.5 py-2 rounded-full bg-slate-900/90 hover:bg-slate-800 text-amber-300 hover:text-amber-200 border border-amber-400/50 shadow-xl text-xs font-bold transition hover:scale-105 active:scale-95"
        title="Summon the FitSense humor sparrow!"
      >
        <span class="group-hover:animate-bounce">🕊️</span>
        <span class="text-[11px]">Fashion Humor</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isVisible = ref(false)
const currentJoke = ref('')

const clothingJokes = [
  "Master Tailor: 'Baji, 2 inch loose rakha hai, baad mein tight ho sakta hai!' 😂",
  "Why is Khaadi Medium the same size as Outfitters Large? That's why FitSense exists! 🕊️",
  "Tailor's sacred promise: 'Jumma ko pakka mil jaye ga'... 3 Jummas ago 🧵",
  "When the size tag says 'Free Size' ... but your shoulders say 'Trial by Combat' 🙈",
  "Ammi at dinner: 'Beta thora loose kurta pehno, sehat achi lagti hai!' ☕",
  "If you can't sit cross-legged on the dastarkhwan, your shalwar size is WRONG! 🍗",
  "When you buy Slim Fit and realize breathing is now an optional luxury 😅",
  "Eid morning emergency: The sleeves are 3 inches shorter than human anatomy! 😭",
]

let flightTimeout: any = null

const triggerSparrow = () => {
  if (isVisible.value) return
  const randomJoke = clothingJokes[Math.floor(Math.random() * clothingJokes.length)]
  currentJoke.value = randomJoke
  isVisible.value = true

  // Hide automatically after 9 seconds of smooth flight
  clearTimeout(flightTimeout)
  flightTimeout = setTimeout(() => {
    isVisible.value = false
  }, 9200)
}

const dismissBird = () => {
  clearTimeout(flightTimeout)
  isVisible.value = false
}

onMounted(() => {
  // First flight after 4 seconds
  setTimeout(() => {
    triggerSparrow()
  }, 4000)

  // Fly across periodically
  setInterval(() => {
    triggerSparrow()
  }, 65000)
})
</script>

<style scoped>
@keyframes flyAcrossScreen {
  0% {
    transform: translateX(-120vw) translateY(0px);
  }
  20% {
    transform: translateX(-60vw) translateY(-14px);
  }
  50% {
    transform: translateX(0vw) translateY(8px);
  }
  80% {
    transform: translateX(60vw) translateY(-12px);
  }
  100% {
    transform: translateX(120vw) translateY(0px);
  }
}

.fly-across {
  animation: flyAcrossScreen 9s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

.fly-across:hover {
  animation-play-state: paused;
}

@keyframes wingFlapAnimation {
  0%, 100% {
    transform: rotate(0deg) scaleY(1);
    transform-origin: 45px 38px;
  }
  50% {
    transform: rotate(-35deg) scaleY(0.7);
    transform-origin: 45px 38px;
  }
}

.wing-flap {
  animation: wingFlapAnimation 0.2s ease-in-out infinite;
}

@keyframes gentleFlutter {
  0%, 100% {
    transform: translateY(0px) rotate(1deg);
  }
  50% {
    transform: translateY(-5px) rotate(-2deg);
  }
}

.sparrow-flutter {
  animation: gentleFlutter 0.75s ease-in-out infinite;
}
</style>