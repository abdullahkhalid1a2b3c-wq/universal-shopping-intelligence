<template>
  <div :class="['popup-container', { rtl: language === 'ur' }]" :dir="language === 'ur' ? 'rtl' : 'ltr'">
    <!-- Header -->
    <header class="popup-header">
      <div class="brand">
        <svg class="brand-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.38 3.46L16 2a4 4 0 01-8 0L3.62 3.46a2 2 0 00-1.34 2.23l.58 3.47a1 1 0 00.99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 002-2V10h2.15a1 1 0 00.99-.84l.58-3.47a2 2 0 00-1.34-2.23z"/>
        </svg>
        <span class="brand-name">FitSense</span>
      </div>
      <div class="header-controls">
        <!-- Widget Toggle -->
        <label class="toggle-switch" title="Toggle shopping widget">
          <input type="checkbox" v-model="showWidget" @change="saveWidgetToggle" />
          <span class="slider"></span>
        </label>
      </div>
    </header>

    <!-- Language Selector Bar -->
    <div class="language-bar">
      <button :class="{ active: language === 'en' }" @click="setLanguage('en')">English</button>
      <button :class="{ active: language === 'ur' }" @click="setLanguage('ur')">اردو</button>
      <button :class="{ active: language === 'ur-roman' }" @click="setLanguage('ur-roman')">Roman</button>
    </div>

    <!-- Active User Session View -->
    <div v-if="session" class="session-card">
      <div class="user-info">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-meta">
          <div class="user-email">{{ session.user?.email }}</div>
          <div class="profile-status">
            <span :class="['status-dot', isProfileComplete ? 'complete' : 'pending']"></span>
            <span>{{ isProfileComplete ? t('profileComplete') : t('profileIncomplete') }}</span>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button class="primary-btn" @click="openWebProfile">
          {{ t('manageProfile') }} ↗
        </button>
        <button class="secondary-btn" @click="handleSignOut">
          {{ t('signOut') }}
        </button>
      </div>
    </div>

    <!-- Guest / Login View -->
    <div v-else class="auth-tabs">
      <div class="tab-headers">
        <button :class="{ active: activeTab === 'guest' }" @click="activeTab = 'guest'">
          {{ t('guestMode') }}
        </button>
        <button :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">
          {{ t('signIn') }}
        </button>
      </div>

      <!-- Guest Measurements Panel -->
      <div v-if="activeTab === 'guest'" class="tab-body">
        <p class="section-desc">{{ t('guestDesc') }}</p>
        <div class="form-grid">
          <div class="form-field">
            <label>{{ t('chest') }} (cm)</label>
            <input type="number" v-model.number="guestForm.chest_cm" placeholder="96" />
          </div>
          <div class="form-field">
            <label>{{ t('waist') }} (cm)</label>
            <input type="number" v-model.number="guestForm.waist_cm" placeholder="82" />
          </div>
          <div class="form-field">
            <label>{{ t('hip') }} (cm)</label>
            <input type="number" v-model.number="guestForm.hip_cm" placeholder="98" />
          </div>
        </div>
        <button class="primary-btn full-width" @click="saveGuestMeasurements">
          {{ guestSaved ? t('saved') : t('saveMeasurements') }}
        </button>
        <p class="privacy-note">🔒 {{ t('guestPrivacyNote') }}</p>
      </div>

      <!-- Sign In Panel -->
      <div v-else class="tab-body">
        <form @submit.prevent="handleSignIn" class="login-form">
          <div class="form-group">
            <label>{{ t('email') }}</label>
            <input type="email" v-model="loginForm.email" required placeholder="you@example.com" />
          </div>
          <div class="form-group">
            <label>{{ t('password') }}</label>
            <input type="password" v-model="loginForm.password" required placeholder="••••••••" />
          </div>
          <div v-if="authError" class="auth-error">{{ authError }}</div>
          <button type="submit" class="primary-btn full-width" :disabled="authLoading">
            {{ authLoading ? t('signingIn') : t('signIn') }}
          </button>
        </form>
        <div class="footer-links">
          <a href="#" @click.prevent="openWebSignup">{{ t('noAccount') }} ↗</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { supabase, syncSessionToStorage } from './supabase'

const WEB_APP_URL = 'http://localhost:3000'

const language = ref<'en' | 'ur' | 'ur-roman'>('en')
const showWidget = ref(true)
const activeTab = ref<'guest' | 'login'>('guest')
const session = ref<any>(null)
const isProfileComplete = ref(false)

const guestSaved = ref(false)
const guestForm = reactive({
  chest_cm: undefined as number | undefined,
  waist_cm: undefined as number | undefined,
  hip_cm: undefined as number | undefined,
})

const loginForm = reactive({
  email: '',
  password: '',
})
const authLoading = ref(false)
const authError = ref('')

// Simple dictionary for en, ur, and ur-roman
const translations: Record<string, Record<string, string>> = {
  en: {
    manageProfile: 'Web Profile & Feedback',
    signOut: 'Sign Out',
    profileComplete: 'Measurements recorded',
    profileIncomplete: 'Incomplete measurements',
    guestMode: 'Guest Mode',
    signIn: 'Sign In',
    guestDesc: 'Enter your basic measurements to get size recommendations without an account.',
    chest: 'Chest',
    waist: 'Waist',
    hip: 'Hip',
    saveMeasurements: 'Save Measurements',
    saved: '✓ Saved on Device',
    guestPrivacyNote: 'Stored only in your browser storage. Never uploaded without consent.',
    email: 'Email',
    password: 'Password',
    signingIn: 'Signing in...',
    noAccount: 'Need an account? Sign up on FitSense',
  },
  ur: {
    manageProfile: 'ویب پروفائل اور فیڈ بیک',
    signOut: 'لاگ آؤٹ',
    profileComplete: 'پیمائش مکمل ہے',
    profileIncomplete: 'پیمائش نامکمل ہے',
    guestMode: 'مہمان موڈ',
    signIn: 'لاگ ان کریں',
    guestDesc: 'اکاؤنٹ کے بغیر سائز کی سفارشات حاصل کرنے کے لیے اپنی بنیادی پیمائش درج کریں۔',
    chest: 'سینہ',
    waist: 'کمر',
    hip: 'کولہے',
    saveMeasurements: 'پیمائش محفوظ کریں',
    saved: '✓ ڈیوائس پر محفوظ ہو گیا',
    guestPrivacyNote: 'صرف آپ کے براؤزر میں محفوظ ہے۔ رضامندی کے بغیر کبھی شیئر نہیں ہوگا۔',
    email: 'ای میل',
    password: 'پاس ورڈ',
    signingIn: 'لاگ ان ہو رہا ہے...',
    noAccount: 'اکاؤنٹ نہیں ہے؟ سائن اپ کریں',
  },
  'ur-roman': {
    manageProfile: 'Web Profile & Feedback',
    signOut: 'Sign Out',
    profileComplete: 'Paimaish mukammal hai',
    profileIncomplete: 'Paimaish na-mukammal hai',
    guestMode: 'Guest Mode',
    signIn: 'Sign In',
    guestDesc: 'Baghair account size maloom karnay k liye bunyadi paimaish darj karein.',
    chest: 'Chest',
    waist: 'Kamr',
    hip: 'Hip',
    saveMeasurements: 'Paimaish Save Karein',
    saved: '✓ Device par save ho gaya',
    guestPrivacyNote: 'Sirf aap k browser me mehfooz hai. Marzi k baghair kahin nahi bhejte.',
    email: 'Email',
    password: 'Password',
    signingIn: 'Signing in...',
    noAccount: 'Account nahi hai? Sign up karein',
  },
}

function t(key: string): string {
  const langDict = translations[language.value] || translations.en
  return langDict[key] || translations.en[key] || key
}

const userInitials = computed(() => {
  const email = session.value?.user?.email || 'U'
  return email.slice(0, 2).toUpperCase()
})

onMounted(async () => {
  // Load settings and session from chrome.storage
  if (typeof chrome !== 'undefined' && chrome.storage?.local) {
    const data = await chrome.storage.local.get([
      'fitsense_session',
      'fitsense_language',
      'fitsense_show_widget',
      'fitsense_guest_measurements',
    ])

    if (data.fitsense_language) language.value = data.fitsense_language
    if (data.fitsense_show_widget !== undefined) showWidget.value = data.fitsense_show_widget
    if (data.fitsense_guest_measurements) {
      Object.assign(guestForm, data.fitsense_guest_measurements)
    }
  }

  // Check Supabase session
  const { data: authData } = await supabase.auth.getSession()
  if (authData?.session) {
    session.value = authData.session
    await syncSessionToStorage(authData.session)
    checkProfileCompleteness(authData.session)
  }
})

async function checkProfileCompleteness(activeSession: any) {
  try {
    const { data } = await supabase
      .from('body_measurements')
      .select('chest_cm, waist_cm')
      .eq('user_id', activeSession.user.id)
      .limit(1)

    if (data && data.length > 0 && (data[0].chest_cm || data[0].waist_cm)) {
      isProfileComplete.value = true
    } else {
      isProfileComplete.value = false
    }
  } catch {
    isProfileComplete.value = false
  }
}

async function setLanguage(lang: 'en' | 'ur' | 'ur-roman') {
  language.value = lang
  if (typeof chrome !== 'undefined' && chrome.storage?.local) {
    await chrome.storage.local.set({ fitsense_language: lang })
  }
}

async function saveWidgetToggle() {
  if (typeof chrome !== 'undefined' && chrome.storage?.local) {
    await chrome.storage.local.set({ fitsense_show_widget: showWidget.value })
  }
}

async function saveGuestMeasurements() {
  if (typeof chrome !== 'undefined' && chrome.storage?.local) {
    await chrome.storage.local.set({
      fitsense_guest_measurements: {
        chest_cm: guestForm.chest_cm || null,
        waist_cm: guestForm.waist_cm || null,
        hip_cm: guestForm.hip_cm || null,
      },
    })
  }
  guestSaved.value = true
  setTimeout(() => {
    guestSaved.value = false
  }, 2000)
}

async function handleSignIn() {
  authLoading.value = true
  authError.value = ''
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: loginForm.email.trim(),
      password: loginForm.password,
    })
    if (error) throw error
    if (data?.session) {
      session.value = data.session
      await syncSessionToStorage(data.session)
      checkProfileCompleteness(data.session)
    }
  } catch (err: any) {
    authError.value = err.message || 'Failed to sign in'
  } finally {
    authLoading.value = false
  }
}

async function handleSignOut() {
  await supabase.auth.signOut()
  session.value = null
  await syncSessionToStorage(null)
}

function openWebProfile() {
  if (typeof chrome !== 'undefined' && chrome.tabs) {
    chrome.tabs.create({ url: `${WEB_APP_URL}/profile` })
  } else {
    window.open(`${WEB_APP_URL}/profile`, '_blank')
  }
}

function openWebSignup() {
  if (typeof chrome !== 'undefined' && chrome.tabs) {
    chrome.tabs.create({ url: `${WEB_APP_URL}/signup` })
  } else {
    window.open(`${WEB_APP_URL}/signup`, '_blank')
  }
}
</script>

<style scoped>
.popup-container {
  width: 320px;
  min-height: 400px;
  background: #ffffff;
  color: #1e293b;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 16px;
  box-sizing: border-box;
}

.popup-container.rtl {
  direction: rtl;
  text-align: right;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4f46e5;
  font-weight: 700;
  font-size: 16px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}
.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #cbd5e1;
  transition: .3s;
  border-radius: 20px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #4f46e5;
}
input:checked + .slider:before {
  transform: translateX(16px);
}

.language-bar {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
  margin-bottom: 16px;
  gap: 2px;
}
.language-bar button {
  flex: 1;
  background: none;
  border: none;
  padding: 5px 0;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
}
.language-bar button.active {
  background: #ffffff;
  color: #4f46e5;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* User Session */
.session-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #e0e7ff;
  color: #4f46e5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}
.user-email {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.profile-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot.complete { background: #10b981; }
.status-dot.pending { background: #f59e0b; }

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Tabs */
.tab-headers {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 14px;
}
.tab-headers button {
  flex: 1;
  background: none;
  border: none;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.tab-headers button.active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
}

.section-desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 12px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.form-field label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
}
.form-field input, .form-group input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 13px;
  box-sizing: border-box;
}

.form-group {
  margin-bottom: 12px;
}
.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
}

.primary-btn {
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.primary-btn:hover { background: #4338ca; }
.primary-btn.full-width { width: 100%; }

.secondary-btn {
  background: transparent;
  color: #64748b;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.secondary-btn:hover { background: #f8fafc; color: #1e293b; }

.privacy-note {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 10px;
  line-height: 1.3;
  text-align: center;
}

.auth-error {
  font-size: 12px;
  color: #dc2626;
  margin-bottom: 10px;
  padding: 6px 10px;
  background: #fee2e2;
  border-radius: 6px;
}

.footer-links {
  margin-top: 14px;
  text-align: center;
}
.footer-links a {
  font-size: 12px;
  color: #4f46e5;
  text-decoration: none;
}
.footer-links a:hover {
  text-decoration: underline;
}
</style>
