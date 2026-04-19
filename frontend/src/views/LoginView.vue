<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const auth = useEduAuthStore()
const { locale } = useI18n()

const lang = computed(() => locale.value || 'ru')
const setLang = (v) => { locale.value = v; try { localStorage.setItem('nbu.locale', v) } catch (e) {} }

const T = {
  ru: {
    kicker: 'NATIONAL BANK OF UZBEKISTAN',
    brand: 'NBU AI Platform',
    sub: 'Войдите, чтобы получить доступ к AI-инструментам для бизнеса',
    signin: 'Вход',
    signup: 'Регистрация',
    email: 'Email',
    emailPh: 'you@company.uz',
    password: 'Пароль',
    passwordPh: 'Минимум 8 символов',
    passwordShow: 'Показать',
    passwordHide: 'Скрыть',
    fullName: 'Полное имя',
    fullNamePh: 'Иван Иванов',
    remember: 'Запомнить меня',
    forgot: 'Забыли пароль?',
    submit: 'Войти',
    submitRegister: 'Создать аккаунт',
    noAccount: 'Нет аккаунта?',
    haveAccount: 'Уже есть аккаунт?',
    signupCta: 'Зарегистрироваться',
    signinCta: 'Войти',
    copyright: '© 2026 NBU — National Bank of Uzbekistan',
    tool1: 'Аналитика регионов',
    tool1d: '14 регионов, 199 районов, ВРП-анализ',
    tool2: 'AI Бизнес-советник',
    tool2d: 'Персональный анализ для МСБ',
    tool3: 'Обучение',
    tool3d: 'Курсы финансовой грамотности',
    tool4: 'Финконтроль',
    tool4d: 'Управление денежными потоками бизнеса',
  },
  uz: {
    kicker: 'O\'ZBEKISTON MILLIY BANKI',
    brand: 'NBU AI Platform',
    sub: 'Biznes uchun AI vositalariga kirish uchun tizimga kiring',
    signin: 'Kirish',
    signup: 'Ro\'yxatdan o\'tish',
    email: 'Email',
    emailPh: 'you@company.uz',
    password: 'Parol',
    passwordPh: 'Kamida 8 ta belgi',
    passwordShow: 'Ko\'rsatish',
    passwordHide: 'Yashirish',
    fullName: 'To\'liq ism',
    fullNamePh: 'Ism Familiya',
    remember: 'Meni eslab qol',
    forgot: 'Parolni unutdingizmi?',
    submit: 'Kirish',
    submitRegister: 'Akkaunt yaratish',
    noAccount: 'Akkauntingiz yo\'qmi?',
    haveAccount: 'Akkauntingiz bormi?',
    signupCta: 'Ro\'yxatdan o\'tish',
    signinCta: 'Kirish',
    copyright: '© 2026 NBU — O\'zbekiston Milliy Banki',
    tool1: 'Hududlar tahlili',
    tool1d: '14 viloyat, 199 tuman, YIM tahlil',
    tool2: 'AI Biznes maslahatchi',
    tool2d: 'KOB uchun shaxsiy tahlil',
    tool3: 'Ta\'lim',
    tool3d: 'Moliyaviy savodxonlik kurslari',
    tool4: 'Moliya nazorati',
    tool4d: 'Biznes pul oqimlarini boshqarish',
  },
}

const t = computed(() => T[lang.value] || T.ru)

const tools = computed(() => [
  { icon: '📊', title: t.value.tool1, desc: t.value.tool1d, color: '#7FB5E6' },
  { icon: '🤖', title: t.value.tool2, desc: t.value.tool2d, color: '#10B981' },
  { icon: '📚', title: t.value.tool3, desc: t.value.tool3d, color: '#F59E0B' },
  { icon: '💰', title: t.value.tool4, desc: t.value.tool4d, color: '#8B5CF6' },
])

// Form state
const mode = ref('signin')
const email = ref('')
const password = ref('')
const fullName = ref('')
const showPw = ref(false)
const remember = ref(true)
const loading = ref(false)
const error = ref('')
const emailFocus = ref(false)
const pwFocus = ref(false)
const nameFocus = ref(false)

watch(mode, () => { error.value = '' })

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'signin') {
      await auth.login(email.value, password.value)
    } else {
      await auth.register(email.value, password.value, fullName.value.trim())
    }
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.message
  }
  loading.value = false
}
</script>

<template>
  <div class="login-page">
    <!-- Background grid -->
    <div class="login-bg-grid" />
    <div class="login-bg-glow" />

    <!-- Header -->
    <header class="login-header">
      <div class="login-logo">
        <div class="login-logo-mark">N</div>
        <div>
          <div class="login-logo-text">NBU AI Platform</div>
          <div class="login-logo-sub">secure · v4.2</div>
        </div>
      </div>
      <div class="login-lang">
        <button
          v-for="l in ['RU', 'UZ']" :key="l"
          :class="['login-lang-btn', { active: lang === l.toLowerCase() }]"
          @click="setLang(l.toLowerCase())"
        >{{ l }}</button>
      </div>
    </header>

    <!-- Content -->
    <div class="login-content">
      <!-- Left: branding -->
      <div class="login-left">
        <div class="login-left-inner">
          <div class="login-kicker">{{ t.kicker }}</div>
          <h1 class="login-title">{{ t.brand }}</h1>
          <p class="login-subtitle">{{ t.sub }}</p>

          <div class="login-tools-grid">
            <div v-for="(tool, i) in tools" :key="i" class="login-tool-card">
              <div class="login-tool-icon" :style="{ background: tool.color + '22', color: tool.color }">
                {{ tool.icon }}
              </div>
              <div class="login-tool-info">
                <div class="login-tool-title">{{ tool.title }}</div>
                <div class="login-tool-desc">{{ tool.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: form card -->
      <div class="login-right">
        <div class="login-card">
          <!-- Tabs -->
          <div class="login-tabs">
            <button
              v-for="[k, label] in [['signin', t.signin], ['signup', t.signup]]" :key="k"
              :class="['login-tab', { active: mode === k }]"
              @click="mode = k"
            >{{ label }}</button>
          </div>

          <!-- Full name (signup only) -->
          <div v-if="mode === 'signup'" class="login-field-group fade-in">
            <label class="login-field-label">{{ t.fullName }}</label>
            <div :class="['login-field', { focus: nameFocus }]">
              <input
                v-model="fullName"
                type="text"
                :placeholder="t.fullNamePh"
                autocomplete="name"
                @focus="nameFocus = true"
                @blur="nameFocus = false"
              />
            </div>
          </div>

          <!-- Email -->
          <div class="login-field-group">
            <label class="login-field-label">{{ t.email }}</label>
            <div :class="['login-field', { focus: emailFocus }]">
              <input
                v-model="email"
                type="email"
                :placeholder="t.emailPh"
                autocomplete="email"
                @focus="emailFocus = true"
                @blur="emailFocus = false"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="login-field-group">
            <label class="login-field-label">{{ t.password }}</label>
            <div :class="['login-field', { focus: pwFocus }]">
              <input
                v-model="password"
                :type="showPw ? 'text' : 'password'"
                :placeholder="t.passwordPh"
                autocomplete="current-password"
                @focus="pwFocus = true"
                @blur="pwFocus = false"
                @keydown.enter="submit"
              />
              <button class="login-pw-toggle" type="button" @click="showPw = !showPw">
                {{ showPw ? t.passwordHide : t.passwordShow }}
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="login-error fade-in">
            ▲ {{ error }}
          </div>

          <!-- Remember / forgot (signin only) -->
          <div v-if="mode === 'signin'" class="login-row">
            <label class="login-remember">
              <input type="checkbox" v-model="remember" />
              {{ t.remember }}
            </label>
            <a href="#" class="login-forgot" @click.prevent>{{ t.forgot }}</a>
          </div>
          <div v-else class="login-spacer" />

          <!-- Submit -->
          <button class="login-submit" :disabled="loading" @click="submit">
            <span v-if="loading" class="login-spinner" />
            <template v-else>
              {{ mode === 'signin' ? t.submit : t.submitRegister }}
              <span class="login-arrow">→</span>
            </template>
          </button>

          <!-- Switch mode -->
          <div class="login-switch">
            {{ mode === 'signin' ? t.noAccount : t.haveAccount }}
            <button @click="mode = mode === 'signin' ? 'signup' : 'signin'">
              {{ mode === 'signin' ? t.signupCta : t.signinCta }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="login-footer">
      <span>{{ t.copyright }}</span>
    </footer>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(175deg, #001935 0%, #003D7C 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', 'Manrope', system-ui, sans-serif;
  position: relative;
  overflow: hidden;
}

.login-bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, #000 40%, transparent 85%);
  pointer-events: none;
}
.login-bg-glow {
  position: absolute;
  top: -120px; right: -120px;
  width: 380px; height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(147,197,253,0.25), transparent 70%);
  filter: blur(30px);
  pointer-events: none;
}

.login-header {
  position: relative; z-index: 2;
  padding: 24px 40px;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.login-logo {
  display: flex; align-items: center; gap: 12px;
}
.login-logo-mark {
  width: 34px; height: 34px; border-radius: 9px;
  background: #fff; color: #003D7C;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 15px;
}
.login-logo-text { font-weight: 800; font-size: 15px; }
.login-logo-sub {
  font-size: 10.5px; letter-spacing: 1.4px; text-transform: uppercase;
  color: rgba(147,197,253,0.7);
  font-family: 'JetBrains Mono', monospace;
}

.login-lang {
  display: inline-flex; padding: 3px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.03);
}
.login-lang-btn {
  padding: 6px 12px; border: none; border-radius: 999px;
  font-size: 12px; font-weight: 600; letter-spacing: 0.4px;
  cursor: pointer; transition: all 0.15s;
  background: transparent; color: rgba(255,255,255,0.7);
}
.login-lang-btn.active { background: #fff; color: #003D7C; }

.login-content {
  position: relative; z-index: 2;
  flex: 1;
  display: grid; grid-template-columns: 1.1fr 1fr;
  align-items: center;
  padding: 40px;
  gap: 60px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}
.login-left { display: flex; align-items: center; }
.login-left-inner { max-width: 520px; }
.login-kicker {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
  color: rgba(147,197,253,0.7);
  margin-bottom: 16px;
}
.login-title {
  font-size: 42px; font-weight: 800; line-height: 1.05;
  letter-spacing: -1.2px; margin: 0;
}
.login-subtitle {
  font-size: 15px; color: rgba(255,255,255,0.65);
  margin-top: 14px; line-height: 1.55;
}

.login-tools-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 12px; margin-top: 36px;
}
.login-tool-card {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 16px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  backdrop-filter: blur(8px);
  transition: background 0.2s;
}
.login-tool-card:hover { background: rgba(255,255,255,0.1); }
.login-tool-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.login-tool-info { flex: 1; }
.login-tool-title { font-size: 13px; font-weight: 700; color: #fff; }
.login-tool-desc { font-size: 11.5px; color: rgba(255,255,255,0.55); margin-top: 2px; }

.login-right { display: flex; align-items: center; justify-content: center; }
.login-card {
  width: 100%; max-width: 420px;
  background: rgba(255,255,255,0.97);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 20px;
  padding: 36px;
  color: #0F1A2B;
  box-shadow: 0 20px 60px -20px rgba(0,0,0,0.4);
}

.login-tabs {
  display: grid; grid-template-columns: 1fr 1fr;
  background: #F1F2F7;
  border-radius: 10px; padding: 4px;
  margin-bottom: 24px;
}
.login-tab {
  padding: 10px 14px; border-radius: 7px; border: none;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.18s;
  background: transparent; color: #64748B;
}
.login-tab.active { background: #003D7C; color: #fff; }

.login-field-group { margin-bottom: 16px; }
.login-field-label {
  display: block; font-size: 12px; font-weight: 500;
  letter-spacing: 0.3px; text-transform: uppercase;
  color: #64748B; margin-bottom: 8px;
}
.login-field {
  display: flex; align-items: center;
  background: #fff;
  border: 1.5px solid #E2E8F0;
  border-radius: 12px;
  transition: border-color 0.18s;
}
.login-field.focus { border-color: #003D7C; }
.login-field input {
  flex: 1; border: none; background: transparent;
  padding: 14px 16px; font-size: 15px; color: #0F1A2B;
  outline: none; font-family: inherit;
}
.login-field input::placeholder { color: #94A3B8; }
.login-pw-toggle {
  background: transparent; border: none;
  margin-right: 8px; padding: 6px 10px; border-radius: 8px;
  font-size: 12px; color: #64748B; cursor: pointer;
  font-family: inherit;
}

.login-error {
  margin-top: -4px; margin-bottom: 12px;
  font-size: 12px; font-weight: 600;
  color: #DC2626;
}

.login-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 4px; margin-bottom: 20px;
}
.login-remember {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #64748B; cursor: pointer;
}
.login-remember input { width: 15px; height: 15px; accent-color: #003D7C; cursor: pointer; }
.login-forgot {
  font-size: 13px; color: #003D7C; font-weight: 600;
  text-decoration: none;
}
.login-spacer { height: 20px; }

.login-submit {
  width: 100%; padding: 15px 20px; border-radius: 12px; border: none;
  background: #003D7C; color: #fff;
  font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: background 0.15s;
  font-family: inherit;
}
.login-submit:hover:not(:disabled) { background: #002B5C; }
.login-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.login-arrow { opacity: 0.6; font-weight: 400; }
.login-spinner {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

.login-switch {
  margin-top: 20px; font-size: 13px; text-align: center;
  color: #64748B;
}
.login-switch button {
  background: transparent; border: none;
  color: #003D7C; cursor: pointer;
  font-weight: 700; padding: 0; font-size: 13px;
  text-decoration: underline; text-underline-offset: 3px;
  font-family: inherit;
}

.login-footer {
  position: relative; z-index: 2;
  padding: 18px 40px;
  border-top: 1px solid rgba(255,255,255,0.06);
  font-size: 11px; letter-spacing: 0.8px;
  color: rgba(255,255,255,0.4);
  font-family: 'JetBrains Mono', monospace;
  text-align: center;
}

.fade-in { animation: slideUp 0.3s ease; }
@keyframes slideUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 900px) {
  .login-content { grid-template-columns: 1fr; padding: 24px; gap: 32px; }
  .login-left { display: none; }
  .login-header { padding: 16px 24px; }
  .login-footer { padding: 16px 24px; }
}
</style>
