<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- Floating Trigger Pill Button -->
    <button
      v-if="!isOpen"
      type="button"
      @click="isOpen = true"
      class="group flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-700 text-white shadow-2xl hover:shadow-indigo-500/30 hover:scale-105 active:scale-95 transition-all duration-200 border border-white/20"
      aria-label="Open AI Fit Assistant"
    >
      <div class="relative flex items-center justify-center">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping absolute"></span>
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 relative"></span>
      </div>
      <span class="font-bold text-xs tracking-wide">AI Fit Assistant</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-white/20 text-indigo-100 font-medium">✨</span>
    </button>

    <!-- Slide-over Drawer / Chat Window -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-8 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform translate-y-8 opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="w-[92vw] sm:w-[420px] h-[580px] max-h-[85vh] flex flex-col bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-800 overflow-hidden"
      >
        <!-- Header -->
        <div class="px-5 py-4 bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-950 text-white flex items-center justify-between border-b border-indigo-700/50">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center text-sm font-black shadow-inner">
              ✨
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="font-bold text-sm tracking-tight">FitSense Assistant</h3>
                <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  AI Active
                </span>
              </div>
              <p class="text-[11px] text-indigo-200">Universal Fit & Sizing Advisor</p>
            </div>
          </div>
          <button
            type="button"
            @click="isOpen = false"
            class="text-indigo-200 hover:text-white p-1 rounded-lg hover:bg-white/10 transition"
            aria-label="Close"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Chat Conversation Messages Area -->
        <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50/70 dark:bg-gray-900/50">
          <!-- Initial Welcome Message -->
          <div class="flex items-start gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs flex items-center justify-center shrink-0 mt-0.5">
              FS
            </div>
            <div class="max-w-[85%] bg-white dark:bg-gray-800 p-3.5 rounded-2xl rounded-tl-sm border border-gray-100 dark:border-gray-700/60 shadow-sm text-xs leading-relaxed text-gray-800 dark:text-gray-200 space-y-2">
              <p class="font-medium">
                Hello! I'm your universal Pakistani fashion fit advisor. How can I assist with your sizing today?
              </p>
              <p class="text-[11px] text-gray-500 dark:text-gray-400">
                You can ask about brand differences, how to measure, or why a specific size fits best.
              </p>
            </div>
          </div>

          <!-- Dynamic Messages -->
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="flex items-start gap-2.5"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              v-if="msg.role !== 'user'"
              class="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs flex items-center justify-center shrink-0 mt-0.5"
            >
              FS
            </div>
            <div
              class="max-w-[85%] p-3.5 rounded-2xl text-xs leading-relaxed shadow-sm"
              :class="
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-tr-sm'
                  : 'bg-slate-800 text-slate-100 rounded-tl-sm border border-slate-700/80'
              "
            >
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</div>
              <div v-else class="space-y-1 assistant-html leading-relaxed" v-html="formatMarkdown(msg.content)"></div>
            </div>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="flex items-start gap-2.5">
            <div class="w-7 h-7 rounded-lg bg-indigo-600 text-white text-xs flex items-center justify-center shrink-0">
              FS
            </div>
            <div class="bg-slate-800 px-4 py-3 rounded-2xl border border-slate-700 flex items-center gap-1.5 shadow-sm">
              <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></span>
              <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></span>
              <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        </div>

        <!-- Quick Suggestion Chips -->
        <div
          class="px-4 py-2 bg-slate-900 border-t border-slate-800 flex items-center gap-1.5 overflow-x-auto hide-scrollbar"
          style="scrollbar-width: none; -ms-overflow-style: none;"
        >
          <button
            v-for="chip in quickChips"
            :key="chip"
            type="button"
            @click="sendQuickPrompt(chip)"
            class="shrink-0 text-[11px] font-medium px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 hover:bg-indigo-900/60 hover:text-indigo-300 border border-slate-700 transition"
          >
            {{ chip }}
          </button>
        </div>

        <!-- Message Input Box -->
        <form @submit.prevent="sendMessage" class="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Ask about sizing, brands, ease..."
            :disabled="isLoading"
            class="flex-1 px-3.5 py-2.5 text-xs rounded-xl bg-slate-800 border border-slate-700 text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            :disabled="isLoading || !inputMessage.trim()"
            class="w-9 h-9 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            aria-label="Send"
          >
            <svg class="w-4 h-4 transform rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          </button>
        </form>

        <!-- Guardrail Footer Notice -->
        <div class="px-4 py-1.5 bg-gray-50 dark:bg-gray-950 text-center border-t border-gray-100 dark:border-gray-800">
          <p class="text-[9px] text-gray-400">
            Recommendations are deterministically computed by FitSense rules engine.
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl || 'http://localhost:8000'
const supabase = useSupabaseClient()

const isOpen = useState('fitsense_assistant_open', () => false)
const inputMessage = ref('')
const isLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<Message[]>([])

const quickChips = [
  'How does Khaadi kurta fit?',
  'Why Medium instead of Large?',
  'How do I measure my chest?',
  'Difference between fitted and regular?',
]

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function formatMarkdown(text: string): string {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // headers ###
  html = html.replace(/^### (.*$)/gim, '<h4 class="font-bold text-indigo-300 mt-2 mb-1">$1</h4>')
  // bold **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-indigo-200">$1</strong>')
  // bullet items
  html = html.replace(/^\* (.*$)/gim, '<div class="flex items-start gap-1.5 ml-1 my-0.5"><span class="text-indigo-400 font-bold">•</span><span>$1</span></div>')
  // numbered items
  html = html.replace(/^(\d+)\. (.*$)/gim, '<div class="flex items-start gap-1.5 ml-1 my-0.5"><span class="text-indigo-400 font-bold">$1.</span><span>$2</span></div>')
  // line breaks
  html = html.replace(/\n\n/g, '<div class="h-2"></div>')
  html = html.replace(/\n/g, '<br/>')
  return html
}

const sendQuickPrompt = (promptText: string) => {
  inputMessage.value = promptText
  sendMessage()
}

const sendMessage = async () => {
  const text = inputMessage.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ role: 'user', content: text })
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const { data: sessionData } = await supabase.auth.getSession()
    const token = sessionData?.session?.access_token

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const payload = {
      messages: messages.value.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      include_profile_measurements: true,
    }

    const res = await $fetch<{ reply: string }>(`${apiBase}/v1/ai/chat`, {
      method: 'POST',
      headers,
      body: payload,
    })

    if (res && res.reply) {
      messages.value.push({ role: 'assistant', content: res.reply })
    } else {
      messages.value.push({
        role: 'assistant',
        content: 'I apologize, but I could not retrieve an answer at this time. Please check the brand size chart directly.',
      })
    }
  } catch (err: any) {
    messages.value.push({
      role: 'assistant',
      content:
        'FitSense Assistant is running in offline mode. Your final clothing size is always deterministically calculated by our zero-ML fit engine under "Find My Size".',
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

