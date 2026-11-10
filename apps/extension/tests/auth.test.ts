import { describe, it, beforeEach } from 'node:test'
import assert from 'node:assert/strict'

// In-memory mock storage simulating chrome.storage.local
class MockChromeStorage {
  private data: Record<string, any> = {}

  async get(keys: string[]): Promise<Record<string, any>> {
    const result: Record<string, any> = {}
    for (const k of keys) {
      if (k in this.data) {
        result[k] = this.data[k]
      }
    }
    return result
  }

  async set(items: Record<string, any>): Promise<void> {
    Object.assign(this.data, items)
  }

  async remove(keys: string | string[]): Promise<void> {
    const arr = Array.isArray(keys) ? keys : [keys]
    for (const k of arr) {
      delete this.data[k]
    }
  }

  clear() {
    this.data = {}
  }
}

// Mock Supabase Auth Client
class MockSupabaseAuth {
  storage: MockChromeStorage

  constructor(storage: MockChromeStorage) {
    this.storage = storage
  }

  async signInWithPassword({ email, password }: { email: string; password: string }) {
    if (password === 'correct-password') {
      const session = {
        access_token: 'mock-jwt-token-xyz',
        user: {
          id: 'mock-user-123',
          email,
        },
      }
      await this.storage.set({ fitsense_session: session })
      return { data: { session }, error: null }
    }
    return { data: { session: null }, error: new Error('Invalid login credentials') }
  }

  async signOut() {
    await this.storage.remove('fitsense_session')
    return { error: null }
  }

  async getSession() {
    const stored = await this.storage.get(['fitsense_session'])
    return { data: { session: stored.fitsense_session || null }, error: null }
  }
}

describe('Extension Auth & Guest Storage Flows', () => {
  let storage: MockChromeStorage
  let auth: MockSupabaseAuth

  beforeEach(() => {
    storage = new MockChromeStorage()
    auth = new MockSupabaseAuth(storage)
  })

  it('signs in successfully and persists session to chrome.storage.local', async () => {
    const res = await auth.signInWithPassword({
      email: 'customer@example.com',
      password: 'correct-password',
    })

    assert.equal(res.error, null)
    assert.equal(res.data.session?.user.email, 'customer@example.com')
    assert.equal(res.data.session?.access_token, 'mock-jwt-token-xyz')

    // Verify persisted in storage
    const stored = await storage.get(['fitsense_session'])
    assert.ok(stored.fitsense_session)
    assert.equal(stored.fitsense_session.user.id, 'mock-user-123')
  })

  it('rejects invalid password and does not persist session', async () => {
    const res = await auth.signInWithPassword({
      email: 'customer@example.com',
      password: 'wrong-password',
    })

    assert.ok(res.error)
    assert.equal(res.error.message, 'Invalid login credentials')

    const stored = await storage.get(['fitsense_session'])
    assert.equal(stored.fitsense_session, undefined)
  })

  it('signs out and clears session from chrome.storage.local', async () => {
    await auth.signInWithPassword({
      email: 'customer@example.com',
      password: 'correct-password',
    })

    await auth.signOut()
    const stored = await storage.get(['fitsense_session'])
    assert.equal(stored.fitsense_session, undefined)
  })

  it('saves guest measurements strictly in local storage without auth token', async () => {
    const guestMeasurements = {
      chest_cm: 98,
      waist_cm: 84,
      hip_cm: 102,
    }

    await storage.set({ fitsense_guest_measurements: guestMeasurements })

    const retrieved = await storage.get(['fitsense_guest_measurements', 'fitsense_session'])
    assert.deepEqual(retrieved.fitsense_guest_measurements, guestMeasurements)
    assert.equal(retrieved.fitsense_session, undefined)
  })
})
