<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useEduAuthStore } from '@/stores/eduAuth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const auth = useEduAuthStore()
const { locale } = useI18n()

const lang = computed(() => locale.value || 'ru')
const setLang = (v) => { locale.value = v; try { localStorage.setItem('nbu.locale', v) } catch {} }

const T = {
  ru: {
    kicker: 'National Bank · Tashkent',
    signin: 'Вход', signup: 'Регистрация',
    email: 'Email', emailPh: 'you@company.uz',
    password: 'Пароль', passwordPh: 'Минимум 8 символов',
    confirmPassword: 'Подтвердите пароль', confirmPasswordPh: 'Введите пароль ещё раз',
    passwordShow: 'Показать', passwordHide: 'Скрыть',
    fullName: 'Полное имя', fullNamePh: 'Иван Иванов',
    remember: 'Запомнить меня', forgot: 'Забыли пароль?',
    submit: 'Войти в платформу', submitRegister: 'Создать аккаунт',
    noAccount: 'Нет аккаунта?', haveAccount: 'Уже есть аккаунт?',
    signupCta: 'Зарегистрироваться', signinCta: 'Войти',
    heroLine1: 'Войдите в', heroAccent: 'интеллект', heroLine2: 'вашего бизнеса.',
    heroBody: 'Региональная аналитика, AI-советник и инструменты финансового планирования — в одной защищённой платформе Национального Банка.',
    roleTitle: 'Я вхожу как',
    role_sme: 'Малый бизнес', role_corp: 'Корпоративный', role_individual: 'Частное лицо',
    err_email: 'Проверьте email',
    err_password_short: 'Пароль должен быть не менее 8 символов',
    err_password_mismatch: 'Пароли не совпадают',
    err_name_required: 'Введите полное имя',
    err_email_taken: 'Этот email уже зарегистрирован',
    err_invalid_credentials: 'Неверный email или пароль',
    dashAnalytics: 'АНАЛИТИКА РЕГИОНОВ',
    dashRegion: 'Ферганская область',
    dashMeta: 'Q2 · 2026 · 15 районов',
    dashMapKicker: 'КАРТА · ФЕРГАНСКАЯ ДОЛИНА',
    dashMapSub: '15 районов · 4 города',
    dashStat1: '15 районов', dashStat2: '4 города', dashStat3: '3.7M чел.',
    kpi1: 'ВРП района', kpi1u: 'млрд сум',
    kpi2: 'Инвестиции', kpi2u: 'млрд сум',
    kpi3: 'Активных МСБ', kpi3u: '+342 мес.',
    chartTitle: 'ВРП по кварталам',
    aiFeed1t: 'AI СОВЕТНИК', aiFeed1m: 'Рост МСБ в Фергане +18% за квартал',
    aiFeed2t: 'АНАЛИТИКА', aiFeed2m: 'Экспорт текстиля Намангана превысил план на 4.2%',
    aiFeed3t: 'РЕКОМЕНДАЦИЯ', aiFeed3m: 'Кредитная ёмкость региона Сурхандарья +12%',
    aiFeed4t: 'AI СОВЕТНИК', aiFeed4m: 'Предупреждение: отток рабочей силы в Хорезме',
    tool1: 'Аналитика', tool1d: '14 регионов',
    tool2: 'Советник', tool2d: 'AI бот',
    tool3: 'Обучение', tool3d: 'Курсы МСБ',
    tool4: 'Финконтроль', tool4d: 'Потоки',
    floatLabel: 'Покрытие платформы', floatVal: '14 регионов · 650K+ бизнесов',
  },
  uz: {
    kicker: 'Milliy Bank · Toshkent',
    signin: 'Kirish', signup: "Ro'yxatdan o'tish",
    email: 'Email', emailPh: 'you@company.uz',
    password: 'Parol', passwordPh: 'Kamida 8 ta belgi',
    confirmPassword: 'Parolni tasdiqlang', confirmPasswordPh: 'Parolni qayta kiriting',
    passwordShow: "Ko'rsatish", passwordHide: 'Yashirish',
    fullName: "To'liq ism", fullNamePh: 'Ism Familiya',
    remember: 'Meni eslab qol', forgot: 'Parolni unutdingizmi?',
    submit: 'Platformaga kirish', submitRegister: 'Akkaunt yaratish',
    noAccount: "Akkauntingiz yo'qmi?", haveAccount: 'Akkauntingiz bormi?',
    signupCta: "Ro'yxatdan o'tish", signinCta: 'Kirish',
    heroLine1: 'Biznesingiz', heroAccent: 'intellektiga', heroLine2: 'kiring.',
    heroBody: 'Platforma hudud tahlili, AI maslahatchi va moliyaviy rejalashtirish vositalarini bitta himoyalangan muhitda birlashtiradi.',
    roleTitle: 'Men quyidagi sifatida kiraman',
    role_sme: 'Kichik biznes', role_corp: 'Korporativ', role_individual: 'Jismoniy shaxs',
    err_email: 'Email ni tekshiring',
    err_password_short: 'Parol kamida 8 ta belgidan iborat boʻlishi kerak',
    err_password_mismatch: 'Parollar mos kelmaydi',
    err_name_required: "To'liq ismni kiriting",
    err_email_taken: 'Bu email allaqachon roʻyxatdan oʻtgan',
    err_invalid_credentials: "Email yoki parol noto'g'ri",
    dashAnalytics: 'HUDUD TAHLILI',
    dashRegion: "Farg'ona viloyati",
    dashMeta: 'Q2 · 2026 · 15 tuman',
    dashMapKicker: "XARITA · FARG'ONA VODIYSI",
    dashMapSub: '15 tuman · 4 shahar',
    dashStat1: '15 tuman', dashStat2: '4 shahar', dashStat3: '3.7M kishi',
    kpi1: 'Tuman YaHM', kpi1u: 'mlrd soʻm',
    kpi2: 'Investitsiya', kpi2u: 'mlrd soʻm',
    kpi3: 'Faol MSB', kpi3u: '+342 oy',
    chartTitle: 'Choraklik YaHM',
    aiFeed1t: 'AI MASLAHATCHI', aiFeed1m: "Farg'onada MSB o'sishi +18%",
    aiFeed2t: 'TAHLIL', aiFeed2m: 'Namangan toʻqimachilik eksporti rejadan 4.2% oshdi',
    aiFeed3t: 'TAVSIYA', aiFeed3m: 'Surxondaryo kredit sigʻimi +12%',
    aiFeed4t: 'AI MASLAHATCHI', aiFeed4m: 'Ogohlantirish: Xorazmda ishchi kuchi oqimi',
    tool1: 'Tahlil', tool1d: '14 viloyat',
    tool2: 'Maslahatchi', tool2d: 'AI bot',
    tool3: "Ta'lim", tool3d: 'KOB kurslari',
    tool4: 'Moliya nazorati', tool4d: 'Oqimlar',
    floatLabel: 'Platforma qamrovi', floatVal: '14 viloyat · 650K+ biznes',
  },
}
const t = computed(() => T[lang.value] || T.ru)

const mode = ref('signin')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const fullName = ref('')
const showPw = ref(false)
const showPwConfirm = ref(false)
const remember = ref(true)
const loading = ref(false)
const error = ref('')
const role = ref('sme')
const emailFocus = ref(false)
const pwFocus = ref(false)
const pwConfirmFocus = ref(false)
const nameFocus = ref(false)

watch(mode, () => {
  error.value = ''
  passwordConfirm.value = ''
})

function validateSignup() {
  if (!fullName.value.trim()) return t.value.err_name_required
  if (password.value.length < 8) return t.value.err_password_short
  if (password.value !== passwordConfirm.value) return t.value.err_password_mismatch
  return null
}

function mapBackendError(message) {
  if (!message) return ''
  const m = String(message).toLowerCase()
  if (m.includes('email_taken')) return t.value.err_email_taken
  if (m.includes('password_too_short')) return t.value.err_password_short
  if (m.includes('full_name_required')) return t.value.err_name_required
  if (m.includes('invalid email or password')) return t.value.err_invalid_credentials
  return message
}

async function submit() {
  error.value = ''
  if (mode.value === 'signup') {
    const v = validateSignup()
    if (v) { error.value = v; return }
  }
  loading.value = true
  try {
    if (mode.value === 'signin') {
      await auth.login(email.value.trim(), password.value)
    } else {
      await auth.register(email.value.trim(), password.value, fullName.value.trim())
    }
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = mapBackendError(e.message)
  }
  loading.value = false
}

const tick = ref(0)
let tickTimer = null
const aiFeed = computed(() => [
  { t: t.value.aiFeed1t, m: t.value.aiFeed1m, c: '#059669' },
  { t: t.value.aiFeed2t, m: t.value.aiFeed2m, c: '#0054A6' },
  { t: t.value.aiFeed3t, m: t.value.aiFeed3m, c: '#F59E0B' },
  { t: t.value.aiFeed4t, m: t.value.aiFeed4m, c: '#DC2626' },
])
const aiNow = computed(() => aiFeed.value[tick.value % aiFeed.value.length])
onMounted(() => { tickTimer = setInterval(() => tick.value++, 3000) })
onUnmounted(() => clearInterval(tickTimer))

const bars = Array.from({ length: 16 }, (_, i) => {
  const base = 30 + Math.abs(Math.sin(i * 0.55) * 55) + (i % 4) * 4
  return Math.min(base, 90)
})
</script>

<template>
  <div class="v3">
    <!-- LEFT: dashboard preview -->
    <div class="v3-right">
      <div class="v3-right-grid" />
      <div class="v3-right-glow1" />
      <div class="v3-right-glow2" />

      <div class="v3-dashboard">
        <div class="v3-dash-card">
          <div class="v3-chrome">
            <div class="v3-chrome-dot" /><div class="v3-chrome-dot" /><div class="v3-chrome-dot" />
            <div class="v3-chrome-url">platform.nbu.uz/dashboard</div>
            <div class="v3-chrome-live"><span class="v3-live-dot-sm" /> LIVE</div>
          </div>

          <div class="v3-dash-header">
            <div>
              <div class="v3-dash-label">{{ t.dashAnalytics }}</div>
              <div class="v3-dash-title">{{ t.dashRegion }}</div>
              <div class="v3-dash-sub">{{ t.dashMeta }}</div>
            </div>
            <div class="v3-dash-badge">+18.2% ВРП</div>
          </div>

          <div class="v3-map-row">
            <div class="v3-map-box">
              <div class="v3-map-header">
                <div>
                  <div class="v3-map-kicker">{{ t.dashMapKicker }}</div>
                  <div class="v3-map-sub">{{ t.dashMapSub }}</div>
                </div>
                <div class="v3-map-active">FERGANA ACTIVE</div>
              </div>
              <div class="v3-map-img-wrap">
                <img src="/assets/fergana_map.png" alt="Ferganskaya dolina" class="v3-map-img" />
              </div>
              <div class="v3-map-footer">
                <span>{{ t.dashStat1 }}</span>
                <span>{{ t.dashStat2 }}</span>
                <span>{{ t.dashStat3 }}</span>
              </div>
            </div>
            <div class="v3-kpis">
              <div class="v3-kpi">
                <div class="v3-kpi-label">{{ t.kpi1 }}</div>
                <div class="v3-kpi-value" style="color:#fff">14,240</div>
                <div class="v3-kpi-unit">{{ t.kpi1u }}</div>
              </div>
              <div class="v3-kpi">
                <div class="v3-kpi-label">{{ t.kpi2 }}</div>
                <div class="v3-kpi-value" style="color:#A7F3D0">2,820</div>
                <div class="v3-kpi-unit">{{ t.kpi2u }}</div>
              </div>
              <div class="v3-kpi">
                <div class="v3-kpi-label">{{ t.kpi3 }}</div>
                <div class="v3-kpi-value" style="color:#93C5FD">12,840</div>
                <div class="v3-kpi-unit">{{ t.kpi3u }}</div>
              </div>
            </div>
          </div>

          <div class="v3-chart">
            <div class="v3-chart-head">
              <div class="v3-chart-title">{{ t.chartTitle }}</div>
              <div class="v3-chart-legend">
                <span><span class="v3-legend-box sky" />2024</span>
                <span><span class="v3-legend-box green" />2025</span>
              </div>
            </div>
            <div class="v3-bars">
              <div v-for="(h,i) in bars" :key="i" class="v3-bar-col">
                <div class="v3-bar" :class="{accent: i>=12}" :style="{height: h+'px'}" />
              </div>
            </div>
            <div class="v3-chart-labels"><span>Q1</span><span>Q2</span><span>Q3</span><span>Q4</span></div>
          </div>

          <div class="v3-ai-feed" :key="tick" :style="{'--feed-color': aiNow.c}">
            <div class="v3-ai-icon" :style="{background: aiNow.c, boxShadow: '0 0 14px '+aiNow.c+'88'}">✦</div>
            <div class="v3-ai-body">
              <div class="v3-ai-tag" :style="{color: aiNow.c}">{{ aiNow.t }}</div>
              <div class="v3-ai-msg">{{ aiNow.m }}</div>
            </div>
            <div class="v3-ai-dots">
              <div v-for="(_,i) in aiFeed" :key="i" :class="['v3-ai-dot',{active: i===tick%aiFeed.length}]" />
            </div>
          </div>
        </div>

        <div class="v3-tools">
          <div class="v3-tool-tile">
            <div class="v3-tool-top">
              <div class="v3-tool-icon" style="background:#93C5FD33;color:#93C5FD">▦</div>
              <div class="v3-tool-dot" style="background:#93C5FD;box-shadow:0 0 6px #93C5FD" />
            </div>
            <div class="v3-tool-name">{{ t.tool1 }}</div>
            <div class="v3-tool-desc">{{ t.tool1d }}</div>
          </div>
          <div class="v3-tool-tile">
            <div class="v3-tool-top">
              <div class="v3-tool-icon" style="background:#10B98133;color:#10B981">✦</div>
              <div class="v3-tool-dot" style="background:#10B981;box-shadow:0 0 6px #10B981" />
            </div>
            <div class="v3-tool-name">{{ t.tool2 }}</div>
            <div class="v3-tool-desc">{{ t.tool2d }}</div>
          </div>
          <div class="v3-tool-tile">
            <div class="v3-tool-top">
              <div class="v3-tool-icon" style="background:#FBBF2433;color:#FBBF24">◐</div>
              <div class="v3-tool-dot" style="background:#FBBF24;box-shadow:0 0 6px #FBBF24" />
            </div>
            <div class="v3-tool-name">{{ t.tool3 }}</div>
            <div class="v3-tool-desc">{{ t.tool3d }}</div>
          </div>
          <div class="v3-tool-tile">
            <div class="v3-tool-top">
              <div class="v3-tool-icon" style="background:#A78BFA33;color:#A78BFA">⬡</div>
              <div class="v3-tool-dot" style="background:#A78BFA;box-shadow:0 0 6px #A78BFA" />
            </div>
            <div class="v3-tool-name">{{ t.tool4 }}</div>
            <div class="v3-tool-desc">{{ t.tool4d }}</div>
          </div>
        </div>
      </div>

      <div class="v3-float-bottom">
        <div class="v3-float-icon">↑</div>
        <div>
          <div class="v3-float-label">{{ t.floatLabel }}</div>
          <div class="v3-float-val">{{ t.floatVal }}</div>
        </div>
      </div>
    </div>

    <!-- RIGHT: form side -->
    <div class="v3-left">
      <header class="v3-header">
        <div class="v3-logo">
          <div class="v3-logo-mark">N</div>
          <div>
            <div class="v3-logo-text">NBU AI Platform</div>
            <div class="v3-logo-sub">{{ t.kicker }}</div>
          </div>
        </div>
        <div class="v3-lang">
          <button v-for="l in ['RU','UZ']" :key="l" :class="['v3-lang-btn', {active: lang===l.toLowerCase()}]" @click="setLang(l.toLowerCase())">{{ l }}</button>
        </div>
      </header>

      <div class="v3-form-area">
        <h1 class="v3-hero">{{ t.heroLine1 }}<br/><span class="v3-accent">{{ t.heroAccent }}</span><br/>{{ t.heroLine2 }}</h1>
        <p class="v3-body">{{ t.heroBody }}</p>

        <div class="v3-tabs">
          <button v-for="[k,label] in [['signin',t.signin],['signup',t.signup]]" :key="k" :class="['v3-tab',{active:mode===k}]" @click="mode=k">{{ label }}</button>
        </div>

        <div v-if="mode==='signup'" class="v3-roles fade-in">
          <div class="v3-roles-label">{{ t.roleTitle }}</div>
          <div class="v3-roles-row">
            <button v-for="[k,label] in [['sme',t.role_sme],['corp',t.role_corp],['individual',t.role_individual]]" :key="k" :class="['v3-role-chip',{active:role===k}]" @click="role=k">{{ label }}</button>
          </div>
        </div>

        <div v-if="mode==='signup'" class="v3-field-group fade-in">
          <label class="v3-field-label">{{ t.fullName }}</label>
          <div :class="['v3-field',{focus:nameFocus}]">
            <input v-model="fullName" type="text" :placeholder="t.fullNamePh" autocomplete="name" @focus="nameFocus=true" @blur="nameFocus=false" />
          </div>
        </div>

        <div class="v3-fields">
          <div class="v3-field-group">
            <label class="v3-field-label">{{ t.email }}</label>
            <div :class="['v3-field',{focus:emailFocus}]">
              <input v-model="email" type="email" :placeholder="t.emailPh" autocomplete="email" @focus="emailFocus=true" @blur="emailFocus=false" />
            </div>
          </div>
          <div class="v3-field-group">
            <label class="v3-field-label">{{ t.password }}</label>
            <div :class="['v3-field',{focus:pwFocus}]">
              <input v-model="password" :type="showPw?'text':'password'" :placeholder="t.passwordPh" :autocomplete="mode==='signup' ? 'new-password' : 'current-password'" @focus="pwFocus=true" @blur="pwFocus=false" @keydown.enter="mode==='signin' && submit()" />
              <button class="v3-pw-toggle" type="button" @click="showPw=!showPw">{{ showPw ? t.passwordHide : t.passwordShow }}</button>
            </div>
          </div>
          <div v-if="mode==='signup'" class="v3-field-group fade-in">
            <label class="v3-field-label">{{ t.confirmPassword }}</label>
            <div :class="['v3-field',{focus:pwConfirmFocus}]">
              <input v-model="passwordConfirm" :type="showPwConfirm?'text':'password'" :placeholder="t.confirmPasswordPh" autocomplete="new-password" @focus="pwConfirmFocus=true" @blur="pwConfirmFocus=false" @keydown.enter="submit" />
              <button class="v3-pw-toggle" type="button" @click="showPwConfirm=!showPwConfirm">{{ showPwConfirm ? t.passwordHide : t.passwordShow }}</button>
            </div>
          </div>
        </div>

        <div v-if="error" class="v3-error fade-in">▲ {{ error }}</div>

        <div v-if="mode==='signin'" class="v3-row">
          <label class="v3-remember"><input type="checkbox" v-model="remember" />{{ t.remember }}</label>
          <a href="#" class="v3-forgot" @click.prevent>{{ t.forgot }}</a>
        </div>
        <div v-else class="v3-spacer" />

        <button class="v3-submit" :disabled="loading" @click="submit">
          <span v-if="loading" class="v3-spinner" />
          <template v-else>{{ mode==='signin' ? t.submit : t.submitRegister }} <span class="v3-arrow">→</span></template>
        </button>

        <div class="v3-switch">
          {{ mode==='signin' ? t.noAccount : t.haveAccount }}
          <button @click="mode = mode==='signin'?'signup':'signin'">{{ mode==='signin' ? t.signupCta : t.signinCta }} →</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.v3 {
  min-height: 100vh;
  background: #F5F8FC;
  color: #0F1A2B;
  display: grid;
  grid-template-columns: minmax(540px, 1.15fr) minmax(480px, 1fr);
  font-family: 'Manrope', 'Inter', system-ui, sans-serif;
  position: relative; overflow: hidden;
}

.v3-left {
  padding: 120px 56px 56px;
  display: flex; flex-direction: column;
  justify-content: center;
  gap: 48px;
  position: relative; z-index: 2;
}
.v3-header {
  position: absolute; top: 40px; left: 56px; right: 56px;
  display: flex; align-items: center; justify-content: space-between;
}
.v3-logo { display: flex; align-items: center; gap: 12px; }
.v3-logo-mark {
  width: 34px; height: 34px; border-radius: 9px;
  background: #003D7C; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 15px;
  box-shadow: 0 6px 20px -6px rgba(0,61,124,0.4);
}
.v3-logo-text { font-weight: 800; font-size: 15px; color: #003D7C; letter-spacing: -0.2px; }
.v3-logo-sub {
  font-size: 10.5px; letter-spacing: 1.4px; text-transform: uppercase;
  color: #64748B; font-family: 'JetBrains Mono', monospace;
}

.v3-lang {
  display: inline-flex; padding: 3px; border-radius: 999px;
  border: 1px solid rgba(0,61,124,0.12);
  background: rgba(255,255,255,0.6);
}
.v3-lang-btn {
  padding: 6px 12px; border: none; border-radius: 999px;
  font-size: 12px; font-weight: 600; letter-spacing: 0.4px;
  cursor: pointer; transition: all .15s;
  background: transparent; color: rgba(0,61,124,0.6);
}
.v3-lang-btn.active { background: #003D7C; color: #fff; }

.v3-form-area { max-width: 520px; width: 100%; position: relative; }
.v3-hero {
  font-size: clamp(2rem, 3.6vw, 3.25rem);
  line-height: 1.02; letter-spacing: -1.2px;
  margin: 0; font-weight: 800;
}
.v3-accent { color: #003D7C; }
.v3-body {
  font-size: 15px; color: #334155; margin-top: 18px;
  max-width: 460px; line-height: 1.55;
}

.v3-tabs {
  display: inline-flex; margin-top: 28px; margin-bottom: 18px;
  background: #E6EEF8; border-radius: 10px; padding: 4px;
}
.v3-tab {
  padding: 9px 20px; border-radius: 7px; border: none;
  font-size: 13px; font-weight: 700; cursor: pointer;
  transition: all .18s;
  background: transparent; color: #003D7C;
}
.v3-tab.active {
  background: #003D7C; color: #fff;
  box-shadow: 0 6px 16px -6px rgba(0,61,124,0.4);
}

.v3-roles { margin-bottom: 16px; }
.v3-roles-label {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
  color: #64748B; margin-bottom: 10px; font-weight: 700;
}
.v3-roles-row { display: flex; gap: 8px; flex-wrap: wrap; }
.v3-role-chip {
  padding: 8px 14px; border-radius: 999px;
  border: 1px solid rgba(0,61,124,0.12);
  background: transparent; color: #003D7C;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all .15s;
}
.v3-role-chip.active {
  border-color: #003D7C; background: #003D7C; color: #fff;
}

.v3-fields { display: flex; flex-direction: column; gap: 12px; max-width: 460px; margin-bottom: 0; }
.v3-field-group { margin-bottom: 12px; }
.v3-fields .v3-field-group { margin-bottom: 0; }
.v3-field-label {
  display: block; font-size: 11px; letter-spacing: 0.6px;
  text-transform: uppercase; color: #64748B; margin-bottom: 6px; font-weight: 700;
}
.v3-field {
  display: flex; align-items: center; background: #fff;
  border: 1.5px solid rgba(0,61,124,0.12);
  border-radius: 10px; transition: all .18s;
  max-width: 460px;
}
.v3-field.focus {
  border-color: #003D7C;
  box-shadow: 0 0 0 4px rgba(0,61,124,0.09);
}
.v3-field input {
  flex: 1; border: none; background: transparent;
  padding: 13px 16px; font-size: 15px; color: #0F1A2B;
  outline: none; font-family: inherit; min-width: 0;
}
.v3-field input::placeholder { color: #94A3B8; }
.v3-pw-toggle {
  background: transparent; border: none;
  margin-right: 8px; padding: 6px 10px; border-radius: 6px;
  font-size: 12px; color: #64748B; font-weight: 600;
  cursor: pointer; font-family: inherit;
}

.v3-error {
  margin-top: 10px; font-size: 12px; color: #DC2626; font-weight: 600;
  display: flex; align-items: center; gap: 6px; max-width: 460px;
}

.v3-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 14px; margin-bottom: 20px; max-width: 460px;
}
.v3-remember {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #334155; cursor: pointer;
}
.v3-remember input { width: 15px; height: 15px; accent-color: #003D7C; }
.v3-forgot { font-size: 13px; color: #003D7C; font-weight: 600; text-decoration: none; }
.v3-spacer { height: 18px; }

.v3-submit {
  width: 100%; max-width: 460px;
  padding: 15px 20px; border-radius: 10px; border: none;
  background: linear-gradient(135deg, #003D7C, #0054A6);
  color: #fff; font-size: 14px; font-weight: 700; letter-spacing: 0.2px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  box-shadow: 0 10px 28px -10px rgba(0,61,124,0.5);
  transition: transform .1s, box-shadow .18s;
  font-family: inherit;
}
.v3-submit:hover:not(:disabled) { transform: scale(1.005); }
.v3-submit:active { transform: scale(0.99); }
.v3-submit:disabled { opacity: 0.4; cursor: not-allowed; }
.v3-arrow { opacity: 0.7; }
.v3-spinner {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  animation: spin .7s linear infinite;
  display: inline-block;
}

.v3-switch { margin-top: 14px; font-size: 13px; color: #64748B; max-width: 460px; }
.v3-switch button {
  background: transparent; border: none;
  color: #003D7C; cursor: pointer;
  font-weight: 700; padding: 0; font-size: 13px;
  font-family: inherit;
}

.v3-right {
  position: relative; overflow: hidden;
  background: linear-gradient(155deg, #002855 0%, #003D7C 55%, #0054A6 100%);
  padding: 48px;
  display: flex; align-items: center; justify-content: center;
}
.v3-right-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: radial-gradient(ellipse 80% 70% at 55% 40%, #000 50%, transparent 90%);
  pointer-events: none;
}
.v3-right-glow1 {
  position: absolute; top: -140px; left: -140px;
  width: 460px; height: 460px; border-radius: 50%;
  background: radial-gradient(circle, rgba(147,197,253,0.33), transparent 70%);
  filter: blur(30px); animation: floaty 7s ease-in-out infinite;
  pointer-events: none;
}
.v3-right-glow2 {
  position: absolute; bottom: -180px; right: -80px;
  width: 380px; height: 380px; border-radius: 50%;
  background: radial-gradient(circle, rgba(0,84,166,0.4), transparent 70%);
  filter: blur(30px); pointer-events: none;
}

.v3-dashboard {
  position: relative; z-index: 2;
  width: 100%; max-width: 600px;
  transform: perspective(1400px) rotateY(7deg) rotateX(3deg);
  transform-origin: center center;
  display: flex; flex-direction: column; gap: 16px;
}

.v3-dash-card {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 18px; padding: 22px;
  backdrop-filter: blur(16px);
  box-shadow: 0 50px 100px -40px rgba(0,0,0,0.6);
  color: #fff;
}

.v3-chrome {
  display: flex; align-items: center; gap: 6px; margin-bottom: 16px;
}
.v3-chrome-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.25); }
.v3-chrome-url {
  margin-left: 10px; flex: 1;
  font-size: 10.5px; color: rgba(255,255,255,0.55);
  font-family: 'JetBrains Mono', monospace; letter-spacing: 0.4px;
}
.v3-chrome-live {
  font-size: 10px; color: #93C5FD;
  font-family: 'JetBrains Mono', monospace; letter-spacing: 0.8px;
  display: flex; align-items: center; gap: 6px;
}
.v3-live-dot-sm {
  width: 5px; height: 5px; border-radius: 50%; display: inline-block;
  background: #10B981; box-shadow: 0 0 8px #10B981;
}

.v3-dash-header {
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;
}
.v3-dash-label {
  font-size: 10px; letter-spacing: 1.6px; text-transform: uppercase;
  color: #93C5FD; font-family: 'JetBrains Mono', monospace; font-weight: 700;
}
.v3-dash-title { font-size: 20px; font-weight: 800; margin-top: 4px; letter-spacing: -0.4px; }
.v3-dash-sub { font-size: 11.5px; color: rgba(255,255,255,0.65); margin-top: 3px; font-weight: 500; }
.v3-dash-badge {
  padding: 5px 10px; border-radius: 6px;
  background: rgba(16,185,129,0.18); border: 1px solid rgba(16,185,129,0.4);
  font-size: 11px; font-weight: 700; color: #A7F3D0;
  font-family: 'JetBrains Mono', monospace;
}

.v3-map-row {
  display: grid; grid-template-columns: 1.5fr 1fr; gap: 14px;
  padding: 14px 0;
  border-top: 1px solid rgba(255,255,255,0.12);
  border-bottom: 1px solid rgba(255,255,255,0.12);
  margin-bottom: 14px;
}
.v3-map-box {
  background: linear-gradient(160deg, rgba(0,0,0,0.28), rgba(0,61,124,0.3));
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; padding: 12px 12px 10px;
  display: flex; flex-direction: column; justify-content: space-between;
}
.v3-map-header {
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;
}
.v3-map-kicker {
  font-size: 9px; letter-spacing: 1.4px; text-transform: uppercase;
  color: #93C5FD; font-family: 'JetBrains Mono', monospace; font-weight: 700;
}
.v3-map-sub { font-size: 11px; color: rgba(255,255,255,0.55); margin-top: 2px; }
.v3-map-active {
  padding: 3px 7px; background: rgba(16,185,129,0.18);
  border: 1px solid rgba(16,185,129,0.4); border-radius: 4px;
  font-size: 9px; font-family: 'JetBrains Mono', monospace;
  font-weight: 700; color: #A7F3D0;
}
.v3-map-img-wrap {
  flex: 1; display: flex; align-items: center; justify-content: center;
  padding: 6px;
}
.v3-map-img {
  width: 100%; height: auto; display: block;
  filter: drop-shadow(0 6px 16px rgba(0,0,0,0.35));
}
.v3-map-footer {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 10px; font-family: 'JetBrains Mono', monospace;
  color: rgba(255,255,255,0.55); letter-spacing: 0.4px; margin-top: 6px;
}

.v3-kpis { display: flex; flex-direction: column; gap: 6px; }
.v3-kpi {
  padding: 9px 11px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
}
.v3-kpi-label {
  font-size: 9.5px; color: rgba(255,255,255,0.55);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600;
}
.v3-kpi-value { font-size: 17px; font-weight: 800; margin-top: 1px; letter-spacing: -0.3px; }
.v3-kpi-unit { font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 1px; }

.v3-chart { margin-bottom: 14px; }
.v3-chart-head {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.v3-chart-title {
  font-size: 11px; font-weight: 700; letter-spacing: 0.4px;
  text-transform: uppercase; color: rgba(255,255,255,0.7);
}
.v3-chart-legend {
  display: flex; gap: 10px; font-size: 10px; color: rgba(255,255,255,0.6);
  font-family: 'JetBrains Mono', monospace;
}
.v3-chart-legend span { display: inline-flex; align-items: center; gap: 4px; }
.v3-legend-box { width: 8px; height: 8px; border-radius: 2px; display: inline-block; }
.v3-legend-box.sky { background: #93C5FD; }
.v3-legend-box.green { background: linear-gradient(to top, #059669, #10B981); }

.v3-bars { height: 110px; display: flex; align-items: flex-end; gap: 6px; padding: 4px 0; }
.v3-bar-col { flex: 1; }
.v3-bar {
  background: linear-gradient(to top, rgba(127,181,230,0.53), #93C5FD);
  border-radius: 3px; transition: all .3s;
}
.v3-bar.accent {
  background: linear-gradient(to top, #059669, #10B981);
  box-shadow: 0 0 14px rgba(16,185,129,0.33);
}
.v3-chart-labels {
  display: flex; justify-content: space-between;
  font-size: 9.5px; color: rgba(255,255,255,0.4); margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.v3-ai-feed {
  padding: 13px 14px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--feed-color) 20%, transparent), rgba(255,255,255,0.05));
  border: 1px solid color-mix(in srgb, var(--feed-color) 33%, transparent);
  border-radius: 10px;
  display: flex; align-items: center; gap: 12px;
  animation: fade .4s ease;
}
.v3-ai-icon {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; color: #fff; font-weight: 800;
  flex-shrink: 0;
}
.v3-ai-body { flex: 1; min-width: 0; }
.v3-ai-tag {
  font-size: 10px; font-family: 'JetBrains Mono', monospace;
  letter-spacing: 1px; font-weight: 700;
}
.v3-ai-msg { font-size: 13px; margin-top: 2px; font-weight: 500; color: rgba(255,255,255,0.95); }
.v3-ai-dots { display: flex; gap: 3px; }
.v3-ai-dot { width: 4px; height: 4px; border-radius: 50%; background: rgba(255,255,255,0.25); }
.v3-ai-dot.active { background: #fff; }

.v3-tools { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.v3-tool-tile {
  padding: 12px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 10px;
  backdrop-filter: blur(12px);
  color: #fff;
}
.v3-tool-top {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;
}
.v3-tool-icon {
  width: 22px; height: 22px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.v3-tool-dot { width: 5px; height: 5px; border-radius: 50%; }
.v3-tool-name { font-size: 12px; font-weight: 700; letter-spacing: -0.1px; }
.v3-tool-desc {
  font-size: 9.5px; color: rgba(255,255,255,0.55);
  font-family: 'JetBrains Mono', monospace; margin-top: 2px; letter-spacing: 0.3px;
}

.v3-float-bottom {
  position: absolute; bottom: 28px; right: 28px; z-index: 3;
  padding: 10px 14px;
  background: #fff; color: #003D7C;
  border-radius: 10px;
  font-size: 12px; font-weight: 700;
  box-shadow: 0 20px 50px -15px rgba(0,0,0,0.5);
  display: flex; align-items: center; gap: 10px;
  transform: rotate(2deg);
}
.v3-float-icon {
  width: 26px; height: 26px; border-radius: 7px; background: #059669;
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 800;
}
.v3-float-label {
  font-size: 9px; letter-spacing: 1px; text-transform: uppercase;
  color: #64748B; font-weight: 700;
}
.v3-float-val { font-size: 14px; letter-spacing: -0.3px; }

.fade-in { animation: slideUp .3s ease; }
@keyframes slideUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fade { from { opacity:0; } to { opacity:1; } }
@keyframes floaty { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.55; } }

@media (max-width: 1024px) {
  .v3 { grid-template-columns: 1fr; }
  .v3-right { display: none; }
  .v3-left { padding: 96px 24px 32px; }
  .v3-header { top: 24px; left: 24px; right: 24px; }
}
</style>
