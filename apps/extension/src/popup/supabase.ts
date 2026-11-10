/**
 * Supabase client configured for Chrome Extension popup with chrome.storage.local session persistence.
 */

import { createClient, type Session } from '@supabase/supabase-js'

const SUPABASE_URL = (import.meta.env.VITE_SUPABASE_URL || 'https://zoxobxpjgottuhrezgie.supabase.co').replace(/\/$/, '')
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_KEY || 'sb_publishable_jJPwjDyQmg7s5zZZGxMJcQ_JwzWSVC-'

// Chrome storage adapter for Supabase Auth
const chromeStorageAdapter = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        const result = await chrome.storage.local.get([key])
        return result[key] || null
      }
      return localStorage.getItem(key)
    } catch {
      return null
    }
  },
  setItem: async (key: string, value: string): Promise<void> => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        await chrome.storage.local.set({ [key]: value })
      } else {
        localStorage.setItem(key, value)
      }
    } catch {
      // Ignore storage errors
    }
  },
  removeItem: async (key: string): Promise<void> => {
    try {
      if (typeof chrome !== 'undefined' && chrome.storage?.local) {
        await chrome.storage.local.remove([key])
      } else {
        localStorage.removeItem(key)
      }
    } catch {
      // Ignore storage errors
    }
  },
}

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    storage: chromeStorageAdapter,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
})

export async function syncSessionToStorage(session: Session | null): Promise<void> {
  if (typeof chrome !== 'undefined' && chrome.storage?.local) {
    await chrome.storage.local.set({ fitsense_session: session })
  }
}
