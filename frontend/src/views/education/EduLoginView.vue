<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useEduAuthStore } from '@/stores/eduAuth'

const router = useRouter()
const auth = useEduAuthStore()
const { t } = useI18n()

const mode = ref('login') // 'login' | 'register'
const email = ref('')
const password = ref('')
const fullName = ref('')
const confirmPassword = ref('')
const error = ref('')
const submitting = ref(false)

async function handleLogin() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/education/dashboard')
  } catch (e) {
    error.value = e.message || t('education.auth.wrongCredentials')
  }
  submitting.value = false
}

async function handleRegister() {
  error.value = ''
  if (password.value.length < 6) { error.value = t('education.auth.passwordMinLength'); return }
  if (password.value !== confirmPassword.value) { error.value = t('education.auth.passwordsMismatch'); return }

  submitting.value = true
  try {
    await auth.register(email.value, password.value, fullName.value)
    router.push('/education/dashboard')
  } catch (e) {
    error.value = e.message || t('education.auth.registerError')
  }
  submitting.value = false
}
</script>

<template>
  <div class="edu-auth">
    <div class="edu-auth__card">
      <!-- Tabs -->
      <div class="edu-tabs" style="margin-bottom: 24px;">
        <button class="edu-tab" :class="{ 'edu-tab--active': mode === 'login' }" @click="mode = 'login'; error = ''">{{ t('education.auth.login') }}</button>
        <button class="edu-tab" :class="{ 'edu-tab--active': mode === 'register' }" @click="mode = 'register'; error = ''">{{ t('education.auth.register') }}</button>
      </div>

      <h1>{{ mode === 'login' ? t('education.auth.loginTitle') : t('education.auth.registerTitle') }}</h1>
      <p class="edu-auth__subtitle">{{ mode === 'login' ? t('education.auth.loginSubtitle') : t('education.auth.registerSubtitle') }}</p>

      <!-- Error -->
      <div v-if="error" style="padding: 10px 14px; background: rgba(220,38,38,0.08); border: 1px solid rgba(220,38,38,0.2); border-radius: 8px; color: var(--edu-error); font-size: 13px; margin-bottom: 16px;">
        {{ error }}
      </div>

      <!-- Login form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin">
        <div class="edu-auth__field">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="student@edupulse.io" required />
        </div>
        <div class="edu-auth__field">
          <label>{{ t('education.auth.password') }}</label>
          <input v-model="password" type="password" placeholder="••••••" required />
        </div>
        <button class="edu-btn edu-btn--primary" style="width: 100%; margin-top: 8px;" :disabled="submitting" type="submit">
          {{ submitting ? t('education.auth.loggingIn') : t('education.auth.loginBtn') }}
        </button>
      </form>

      <!-- Register form -->
      <form v-else @submit.prevent="handleRegister">
        <div class="edu-auth__field">
          <label>{{ t('education.auth.fullName') }}</label>
          <input v-model="fullName" type="text" required />
        </div>
        <div class="edu-auth__field">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="edu-auth__field">
          <label>{{ t('education.auth.password') }} <span style="font-weight: 400; color: var(--edu-text-muted);">{{ t('education.auth.minChars') }}</span></label>
          <input v-model="password" type="password" placeholder="••••••" required />
        </div>
        <div class="edu-auth__field">
          <label>{{ t('education.auth.confirmPassword') }}</label>
          <input v-model="confirmPassword" type="password" placeholder="••••••" required />
        </div>
        <button class="edu-btn edu-btn--primary" style="width: 100%; margin-top: 8px;" :disabled="submitting" type="submit">
          {{ submitting ? t('education.auth.registering') : t('education.auth.registerBtn') }}
        </button>
      </form>

      <p style="text-align: center; font-size: 13px; color: var(--edu-text-muted); margin-top: 20px;">
        <template v-if="mode === 'login'">
          {{ t('education.auth.noAccount') }}
          <a href="#" style="color: var(--edu-accent);" @click.prevent="mode = 'register'">{{ t('education.auth.registerLink') }}</a>
        </template>
        <template v-else>
          {{ t('education.auth.hasAccount') }}
          <a href="#" style="color: var(--edu-accent);" @click.prevent="mode = 'login'">{{ t('education.auth.loginLink') }}</a>
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.edu-auth {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.edu-auth__card {
  width: 100%;
  max-width: 420px;
  background: var(--edu-bg-card);
  border: 1px solid var(--edu-border);
  border-radius: var(--edu-radius-lg);
  padding: 32px;
  box-shadow: var(--edu-shadow);
}
.edu-auth__card h1 {
  font-family: 'Manrope', sans-serif;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 6px;
  color: var(--edu-text);
}
.edu-auth__subtitle { font-size: 14px; color: var(--edu-text-muted); margin: 0 0 20px; }

.edu-auth__field { margin-bottom: 16px; }
.edu-auth__field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--edu-text);
}
.edu-auth__field input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--edu-border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--edu-text);
  background: var(--edu-bg);
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.edu-auth__field input:focus {
  outline: none;
  border-color: var(--edu-accent);
  box-shadow: 0 0 0 3px rgba(0, 61, 124, 0.1);
}
.edu-auth__field input::placeholder { color: var(--edu-text-muted); }
</style>
