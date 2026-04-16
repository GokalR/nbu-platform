import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useEduAuthStore = defineStore('eduAuth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('edu_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const status = computed(() => {
    if (loading.value) return 'loading'
    return user.value ? 'authenticated' : 'unauthenticated'
  })

  const session = computed(() =>
    user.value ? { user: user.value } : null,
  )

  async function login(email, password) {
    loading.value = true
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Неверный email или пароль')

      token.value = data.access_token
      localStorage.setItem('edu_token', data.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function register(email, password, fullName) {
    loading.value = true
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка регистрации')

      // Auto-login after registration
      await login(email, password)
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      if (res.ok) {
        user.value = await res.json()
      } else {
        logout()
      }
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('edu_token')
  }

  // Try to restore session on init
  if (token.value) {
    fetchMe()
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    status,
    session,
    login,
    register,
    fetchMe,
    logout,
  }
})
