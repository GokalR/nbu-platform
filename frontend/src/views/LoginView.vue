<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const auth = useEduAuthStore()
const { locale } = useI18n()

const mode = ref('login')
const email = ref('')
const password = ref('')
const fullName = ref('')
const confirmPassword = ref('')
const error = ref('')
const submitting = ref(false)

const lang = computed(() => locale.value || 'ru')
const setLang = (v) => { locale.value = v; try { localStorage.setItem('nbu.locale', v) } catch (e) {} }

const T = {
  ru: {
    badge: 'NATIONAL BANK OF UZBEKISTAN',
    title: 'NBU AI Platform',
    subtitle: 'Войдите, чтобы получить доступ к AI-инструментам для бизнеса',
    loginTab: 'Вход',
    registerTab: 'Регистрация',
    loginTitle: 'Вход в аккаунт',
    registerTitle: 'Создать аккаунт',
    email: 'Email',
    password: 'Пароль',
    confirmPassword: 'Подтвердите пароль',
    fullName: 'Полное имя',
    loginBtn: 'Войти',
    registerBtn: 'Зарегистрироваться',
    loggingIn: 'Входим...',
    registering: 'Регистрация...',
    noAccount: 'Нет аккаунта?',
    hasAccount: 'Уже есть аккаунт?',
    registerLink: 'Зарегистрироваться',
    loginLink: 'Войти',
    minChars: '(мин. 6 символов)',
    passwordsMismatch: 'Пароли не совпадают',
    passwordMinLength: 'Пароль должен быть не менее 6 символов',
    features: [
      { icon: '📊', title: 'Аналитика регионов', desc: '14 регионов, 19 районов Ферганы' },
      { icon: '🤖', title: 'AI Бизнес-советник', desc: 'Персональный анализ для МСБ' },
      { icon: '🎓', title: 'Обучение', desc: 'Курсы финансовой грамотности' },
      { icon: '💰', title: 'Финконтроль', desc: 'Управление финансами бизнеса' },
    ],
  },
  uz: {
    badge: 'OʻZBEKISTON MILLIY BANKI',
    title: 'NBU AI Platform',
    subtitle: 'Biznes uchun AI vositalariga kirish uchun tizimga kiring',
    loginTab: 'Kirish',
    registerTab: 'Roʻyxatdan oʻtish',
    loginTitle: 'Akkauntga kirish',
    registerTitle: 'Akkaunt yaratish',
    email: 'Email',
    password: 'Parol',
    confirmPassword: 'Parolni tasdiqlang',
    fullName: 'Toʻliq ism',
    loginBtn: 'Kirish',
    registerBtn: 'Roʻyxatdan oʻtish',
    loggingIn: 'Kirilmoqda...',
    registering: 'Roʻyxatdan oʻtilmoqda...',
    noAccount: 'Akkauntingiz yoʻqmi?',
    hasAccount: 'Akkauntingiz bormi?',
    registerLink: 'Roʻyxatdan oʻting',
    loginLink: 'Tizimga kiring',
    minChars: '(kamida 6 belgi)',
    passwordsMismatch: 'Parollar mos kelmaydi',
    passwordMinLength: 'Parol kamida 6 belgidan iborat boʻlishi kerak',
    features: [
      { icon: '📊', title: 'Mintaqa tahlili', desc: '14 viloyat, 19 Fargʻona tumani' },
      { icon: '🤖', title: 'AI Biznes-maslahatchi', desc: 'MSB uchun shaxsiy tahlil' },
      { icon: '🎓', title: 'Taʼlim', desc: 'Moliyaviy savodxonlik kurslari' },
      { icon: '💰', title: 'Moliya nazorati', desc: 'Biznes moliyasini boshqarish' },
    ],
  },
}

const t = computed(() => T[lang.value] || T.ru)

async function handleLogin() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.message
  }
  submitting.value = false
}

async function handleRegister() {
  error.value = ''
  if (password.value.length < 6) { error.value = t.value.passwordMinLength; return }
  if (password.value !== confirmPassword.value) { error.value = t.value.passwordsMismatch; return }
  submitting.value = true
  try {
    await auth.register(email.value, password.value, fullName.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.message
  }
  submitting.value = false
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex">
    <!-- Left side — branding -->
    <div class="hidden lg:flex lg:w-1/2 flex-col justify-center px-16 text-white">
      <div class="mb-8">
        <div class="inline-block px-3 py-1 bg-white/10 rounded-full text-xs font-semibold tracking-wider mb-6">
          {{ t.badge }}
        </div>
        <h1 class="text-5xl font-bold mb-4">{{ t.title }}</h1>
        <p class="text-lg text-blue-200/80">{{ t.subtitle }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4 mt-8">
        <div v-for="f in t.features" :key="f.title"
             class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur">
          <div class="text-2xl mb-2">{{ f.icon }}</div>
          <div class="font-semibold text-sm">{{ f.title }}</div>
          <div class="text-xs text-blue-200/60 mt-1">{{ f.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Right side — form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6">
      <div class="w-full max-w-md">
        <!-- Lang switcher -->
        <div class="flex justify-end mb-6">
          <div class="inline-flex bg-white/10 rounded-full p-[2px]">
            <button v-for="l in ['RU', 'UZ']" :key="l"
                    @click="setLang(l.toLowerCase())"
                    class="text-xs font-semibold py-1.5 px-3 rounded-full transition"
                    :class="lang === l.toLowerCase() ? 'bg-white text-slate-900' : 'text-white/60 hover:text-white'">
              {{ l }}
            </button>
          </div>
        </div>

        <!-- Card -->
        <div class="bg-white rounded-2xl shadow-2xl p-8">
          <!-- Mobile branding -->
          <div class="lg:hidden text-center mb-6">
            <h2 class="text-2xl font-bold text-slate-800">{{ t.title }}</h2>
            <p class="text-sm text-slate-500 mt-1">{{ t.subtitle }}</p>
          </div>

          <!-- Tabs -->
          <div class="flex bg-slate-100 rounded-xl p-1 mb-6">
            <button @click="mode = 'login'; error = ''"
                    class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition"
                    :class="mode === 'login' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'">
              {{ t.loginTab }}
            </button>
            <button @click="mode = 'register'; error = ''"
                    class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition"
                    :class="mode === 'register' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'">
              {{ t.registerTab }}
            </button>
          </div>

          <!-- Error -->
          <div v-if="error"
               class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
            {{ error }}
          </div>

          <!-- Login form -->
          <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ t.email }}</label>
              <input v-model="email" type="email" placeholder="you@example.com" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ t.password }}</label>
              <input v-model="password" type="password" placeholder="••••••" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <button type="submit" :disabled="submitting"
                    class="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition disabled:opacity-50">
              {{ submitting ? t.loggingIn : t.loginBtn }}
            </button>
          </form>

          <!-- Register form -->
          <form v-else @submit.prevent="handleRegister" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ t.fullName }}</label>
              <input v-model="fullName" type="text" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ t.email }}</label>
              <input v-model="email" type="email" placeholder="you@example.com" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">
                {{ t.password }} <span class="font-normal text-slate-400">{{ t.minChars }}</span>
              </label>
              <input v-model="password" type="password" placeholder="••••••" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">{{ t.confirmPassword }}</label>
              <input v-model="confirmPassword" type="password" placeholder="••••••" required
                     class="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
            </div>
            <button type="submit" :disabled="submitting"
                    class="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition disabled:opacity-50">
              {{ submitting ? t.registering : t.registerBtn }}
            </button>
          </form>

          <p class="text-center text-sm text-slate-500 mt-5">
            <template v-if="mode === 'login'">
              {{ t.noAccount }}
              <a href="#" class="text-blue-600 font-medium" @click.prevent="mode = 'register'">{{ t.registerLink }}</a>
            </template>
            <template v-else>
              {{ t.hasAccount }}
              <a href="#" class="text-blue-600 font-medium" @click.prevent="mode = 'login'">{{ t.loginLink }}</a>
            </template>
          </p>
        </div>

        <p class="text-center text-xs text-white/30 mt-6">
          &copy; 2026 NBU — National Bank of Uzbekistan
        </p>
      </div>
    </div>
  </div>
</template>
