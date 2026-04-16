<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'

const router = useRouter()
const auth = useEduAuthStore()

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
    error.value = e.message || 'Неверный email или пароль'
  }
  submitting.value = false
}

async function handleRegister() {
  error.value = ''
  if (password.value.length < 6) { error.value = 'Пароль должен быть не менее 6 символов'; return }
  if (password.value !== confirmPassword.value) { error.value = 'Пароли не совпадают'; return }

  submitting.value = true
  try {
    await auth.register(email.value, password.value, fullName.value)
    router.push('/education/dashboard')
  } catch (e) {
    error.value = e.message || 'Ошибка регистрации'
  }
  submitting.value = false
}
</script>

<template>
  <div class="edu-auth">
    <div class="edu-auth__card">
      <!-- Tabs -->
      <div class="edu-tabs" style="margin-bottom: 24px;">
        <button class="edu-tab" :class="{ 'edu-tab--active': mode === 'login' }" @click="mode = 'login'; error = ''">Вход</button>
        <button class="edu-tab" :class="{ 'edu-tab--active': mode === 'register' }" @click="mode = 'register'; error = ''">Регистрация</button>
      </div>

      <h1>{{ mode === 'login' ? 'Вход в систему' : 'Создать аккаунт' }}</h1>
      <p class="edu-auth__subtitle">{{ mode === 'login' ? 'Войдите для доступа к курсам' : 'Зарегистрируйтесь для начала обучения' }}</p>

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
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••" required />
        </div>
        <button class="edu-btn edu-btn--primary" style="width: 100%; margin-top: 8px;" :disabled="submitting" type="submit">
          {{ submitting ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <!-- Register form -->
      <form v-else @submit.prevent="handleRegister">
        <div class="edu-auth__field">
          <label>Полное имя</label>
          <input v-model="fullName" type="text" placeholder="Имя Фамилия" required />
        </div>
        <div class="edu-auth__field">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="edu-auth__field">
          <label>Пароль <span style="font-weight: 400; color: var(--edu-text-muted);">(мин. 6 символов)</span></label>
          <input v-model="password" type="password" placeholder="••••••" required />
        </div>
        <div class="edu-auth__field">
          <label>Подтвердите пароль</label>
          <input v-model="confirmPassword" type="password" placeholder="••••••" required />
        </div>
        <button class="edu-btn edu-btn--primary" style="width: 100%; margin-top: 8px;" :disabled="submitting" type="submit">
          {{ submitting ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p style="text-align: center; font-size: 13px; color: var(--edu-text-muted); margin-top: 20px;">
        <template v-if="mode === 'login'">
          Нет аккаунта?
          <a href="#" style="color: var(--edu-accent);" @click.prevent="mode = 'register'">Зарегистрироваться</a>
        </template>
        <template v-else>
          Уже есть аккаунт?
          <a href="#" style="color: var(--edu-accent);" @click.prevent="mode = 'login'">Войти</a>
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
