import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, describe, it, expect, vi } from 'vitest'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] ?? null),
    setItem: vi.fn((key, value) => { store[key] = value }),
    removeItem: vi.fn((key) => { delete store[key] }),
    clear: vi.fn(() => { store = {} }),
  }
})()
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock the api service
vi.mock('@/services/api', () => ({ BACKEND_URL: 'http://test' }))

import { useEduAuthStore } from '../eduAuth'

describe('eduAuth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('user is null', () => {
      const store = useEduAuthStore()
      expect(store.user).toBeNull()
    })

    it('isAuthenticated is false', () => {
      const store = useEduAuthStore()
      expect(store.isAuthenticated).toBe(false)
    })

    it('status is "unauthenticated"', () => {
      const store = useEduAuthStore()
      expect(store.status).toBe('unauthenticated')
    })
  })

  describe('logout', () => {
    it('clears user and token', () => {
      const store = useEduAuthStore()
      // Manually set user and token to simulate logged-in state
      store.user = { email: 'test@test.com' }
      store.token = 'abc123'

      store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
    })

    it('removes token from localStorage', () => {
      const store = useEduAuthStore()
      store.token = 'abc123'

      store.logout()

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('edu_token')
    })
  })

  describe('token initialization', () => {
    it('reads token from localStorage on store creation', () => {
      // Set a token in localStorage before creating the store
      localStorageMock.getItem.mockReturnValueOnce('stored-token')

      // Need a fresh pinia so the store factory runs again
      setActivePinia(createPinia())

      // Mock fetch so fetchMe doesn't fail
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({}),
      })

      const store = useEduAuthStore()
      expect(store.token).toBe('stored-token')
    })
  })
})
