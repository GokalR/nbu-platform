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

// ---------- i18n ----------
const T = {
  ru: {
    kicker: 'National Bank · Tashkent',
    signin: 'Вход', signup: 'Регистрация',
    email: 'Email', emailPh: 'you@company.uz',
    password: 'Пароль', passwordPh: 'Минимум 8 символов',
    passwordShow: 'Показать', passwordHide: 'Скрыть',
    fullName: 'Полное имя', fullNamePh: 'Иван Иванов',
    remember: 'Запомнить меня', forgot: 'Забыли пароль?',
    submit: 'Войти в платформу', submitRegister: 'Создать аккаунт',
    noAccount: 'Нет аккаунта?', haveAccount: 'Уже есть аккаунт?',
    signupCta: 'Зарегистрироваться', signinCta: 'Войти',
    statusOk: 'Все системы работают',
    legal: 'Защищено end-to-end шифрованием',
    copyright: '© 2026 NBU AI Platform',
    heroLine1: 'Войдите в', heroAccent: 'интеллект', heroLine2: 'вашего бизнеса.',
    heroBody: 'Региональная аналитика, AI-советник и инструменты финансового планирования — в одной защищённой платформе Национального Банка.',
    roleTitle: 'Я вхожу как',
    role_sme: 'Малый бизнес', role_corp: 'Корпоративный', role_individual: 'Частное лицо',
  },
  uz: {
    kicker: 'Milliy Bank · Toshkent',
    signin: 'Kirish', signup: 'Ro\'yxatdan o\'tish',
    email: 'Email', emailPh: 'you@company.uz',
    password: 'Parol', passwordPh: 'Kamida 8 ta belgi',
    passwordShow: 'Ko\'rsatish', passwordHide: 'Yashirish',
    fullName: 'To\'liq ism', fullNamePh: 'Ism Familiya',
    remember: 'Meni eslab qol', forgot: 'Parolni unutdingizmi?',
    submit: 'Platformaga kirish', submitRegister: 'Akkaunt yaratish',
    noAccount: 'Akkauntingiz yo\'qmi?', haveAccount: 'Akkauntingiz bormi?',
    signupCta: 'Ro\'yxatdan o\'tish', signinCta: 'Kirish',
    statusOk: 'Barcha tizimlar ishlayapti',
    legal: 'End-to-end shifrlash bilan himoyalangan',
    copyright: '© 2026 NBU AI Platform',
    heroLine1: 'Kirish:', heroAccent: 'intellekt', heroLine2: 'biznesingiz uchun.',
    heroBody: 'Platforma hudud tahlili, AI maslahatchi va moliyaviy rejalashtirish vositalarini bitta himoyalangan muhitda birlashtiradi.',
    roleTitle: 'Men quyidagi sifatida kiraman',
    role_sme: 'Kichik biznes', role_corp: 'Korporativ', role_individual: 'Jismoniy shaxs',
  },
}
const t = computed(() => T[lang.value] || T.ru)

// ---------- Form state ----------
const mode = ref('signin')
const email = ref('')
const password = ref('')
const fullName = ref('')
const showPw = ref(false)
const remember = ref(true)
const loading = ref(false)
const error = ref('')
const role = ref('sme')
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

// AI feed ticker
const tick = ref(0)
let tickTimer = null
const aiFeed = [
  { t: 'AI СОВЕТНИК', m: 'Рост МСБ в Фергане +18% за квартал', c: '#059669' },
  { t: 'АНАЛИТИКА', m: 'Экспорт текстиля Намангана превысил план на 4.2%', c: '#0054A6' },
  { t: 'РЕКОМЕНДАЦИЯ', m: 'Кредитная ёмкость региона Сурхандарья +12%', c: '#F59E0B' },
  { t: 'AI СОВЕТНИК', m: 'Предупреждение: отток рабочей силы в Хорезме', c: '#DC2626' },
]
const aiNow = computed(() => aiFeed[tick.value % aiFeed.length])
onMounted(() => { tickTimer = setInterval(() => tick.value++, 3000) })
onUnmounted(() => clearInterval(tickTimer))

// Map regions
const regions = [
  { k: 'karakalpak', d: 'M12,60 C18,40 35,28 55,30 C70,32 78,48 72,62 C66,78 48,88 28,82 C18,80 8,72 12,60Z', cx: 42, cy: 56 },
  { k: 'khorezm', d: 'M60,48 C70,42 82,44 86,54 C88,62 82,70 72,68 C64,66 56,58 60,48Z', cx: 73, cy: 56 },
  { k: 'navoi', d: 'M88,58 C104,50 130,54 138,68 C142,80 128,90 110,86 C94,82 82,72 88,58Z', cx: 113, cy: 70 },
  { k: 'bukhara', d: 'M90,82 C102,78 120,82 124,92 C126,100 116,108 102,104 C90,100 84,90 90,82Z', cx: 106, cy: 92 },
  { k: 'samarkand', d: 'M140,80 C152,74 168,78 170,88 C172,98 160,106 148,102 C138,98 132,88 140,80Z', cx: 154, cy: 90 },
  { k: 'kashkadarya', d: 'M158,104 C172,100 188,104 190,116 C192,126 178,132 164,128 C152,124 146,110 158,104Z', cx: 174, cy: 116 },
  { k: 'surkhandarya', d: 'M180,132 C192,128 206,134 208,144 C208,154 196,158 184,154 C176,150 170,138 180,132Z', cx: 194, cy: 144 },
  { k: 'jizzakh', d: 'M172,70 C184,66 196,70 196,80 C196,88 186,92 176,88 C168,86 162,76 172,70Z', cx: 184, cy: 79 },
  { k: 'syrdarya', d: 'M196,66 C206,62 216,64 218,72 C218,80 208,84 200,80 C192,78 188,70 196,66Z', cx: 207, cy: 72 },
  { k: 'tashkent', d: 'M204,50 C218,46 236,52 238,64 C238,74 224,80 212,76 C200,72 192,58 204,50Z', cx: 221, cy: 62 },
  { k: 'namangan', d: 'M238,56 C250,52 264,58 264,66 C264,74 252,78 242,76 C234,74 230,62 238,56Z', cx: 251, cy: 66 },
  { k: 'andijan', d: 'M262,68 C272,66 280,70 280,78 C278,86 268,88 260,84 C254,80 254,72 262,68Z', cx: 270, cy: 77 },
  { k: 'fergana', d: 'M254,82 C266,78 280,82 282,92 C282,100 270,104 260,100 C250,96 244,86 254,82Z', cx: 268, cy: 91 },
]

// Bar chart heights
const bars = Array.from({ length: 16 }, (_, i) => {
  const base = 30 + Math.abs(Math.sin(i * 0.55) * 55) + (i % 4) * 4
  return Math.min(base, 90)
})
</script>

<template>
  <div class="v3">
    <!-- LEFT: form side -->
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

        <!-- tabs -->
        <div class="v3-tabs">
          <button v-for="[k,label] in [['signin',t.signin],['signup',t.signup]]" :key="k" :class="['v3-tab',{active:mode===k}]" @click="mode=k">{{ label }}</button>
        </div>

        <!-- role chips (signup) -->
        <div v-if="mode==='signup'" class="v3-roles fade-in">
          <div class="v3-roles-label">{{ t.roleTitle }}</div>
          <div class="v3-roles-row">
            <button v-for="[k,label] in [['sme',t.role_sme],['corp',t.role_corp],['individual',t.role_individual]]" :key="k" :class="['v3-role-chip',{active:role===k}]" @click="role=k">{{ label }}</button>
          </div>
        </div>

        <!-- full name (signup) -->
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
              <input v-model="password" :type="showPw?'text':'password'" :placeholder="t.passwordPh" autocomplete="current-password" @focus="pwFocus=true" @blur="pwFocus=false" @keydown.enter="submit" />
              <button class="v3-pw-toggle" type="button" @click="showPw=!showPw">{{ showPw ? t.passwordHide : t.passwordShow }}</button>
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

      <div class="v3-footer-left">
        <span class="v3-status-dot" /> {{ t.statusOk }}
        <span>·</span> {{ t.legal }}
        <span>·</span> {{ t.copyright }}
      </div>
    </div>

    <!-- RIGHT: dashboard preview -->
    <div class="v3-right">
      <div class="v3-right-grid" />
      <div class="v3-right-glow1" />
      <div class="v3-right-glow2" />

      <!-- floating top badge -->
      <div class="v3-float-top">
        <span class="v3-live-dot" /> 3 узла · Tashkent · Fergana · Samarkand
      </div>

      <div class="v3-dashboard">
        <!-- main card -->
        <div class="v3-dash-card">
          <!-- window chrome -->
          <div class="v3-chrome">
            <div class="v3-chrome-dot" /><div class="v3-chrome-dot" /><div class="v3-chrome-dot" />
            <div class="v3-chrome-url">platform.nbu.uz/dashboard</div>
            <div class="v3-chrome-live"><span class="v3-live-dot-sm" /> LIVE</div>
          </div>

          <!-- header -->
          <div class="v3-dash-header">
            <div>
              <div class="v3-dash-label">АНАЛИТИКА РЕГИОНОВ</div>
              <div class="v3-dash-title">Ферганская область</div>
              <div class="v3-dash-sub">Q2 · 2026 · 15 районов</div>
            </div>
            <div class="v3-dash-badge">+18.2% YoY</div>
          </div>

          <!-- map + KPIs -->
          <div class="v3-map-row">
            <div class="v3-map-box">
              <svg viewBox="0 0 292 170" class="v3-map-svg">
                <g v-for="r in regions" :key="r.k">
                  <path :d="r.d" :fill="r.k==='fergana' ? '#93C5FD' : 'rgba(255,255,255,0.08)'" :stroke="r.k==='fergana' ? '#fff' : 'rgba(255,255,255,0.25)'" :stroke-width="r.k==='fergana' ? 1.2 : 0.7" />
                  <template v-if="r.k==='fergana'">
                    <circle :cx="r.cx" :cy="r.cy" r="3.5" fill="#fff" />
                    <circle :cx="r.cx" :cy="r.cy" r="8" fill="none" stroke="#fff" stroke-width="1" opacity="0.6">
                      <animate attributeName="r" values="4;12;4" dur="2.4s" repeatCount="indefinite" />
                      <animate attributeName="opacity" values="0.8;0;0.8" dur="2.4s" repeatCount="indefinite" />
                    </circle>
                  </template>
                </g>
              </svg>
              <div class="v3-map-footer"><span>14 регионов</span><span>· 199 районов</span></div>
            </div>
            <div class="v3-kpis">
              <div v-for="(s,i) in [{l:'ВРП района',v:'14,240',u:'млрд сум',c:'#fff'},{l:'Инвестиции',v:'2,820',u:'млрд сум',c:'#A7F3D0'},{l:'Активных МСБ',v:'12,840',u:'+342 мес.',c:'#93C5FD'}]" :key="i" class="v3-kpi">
                <div class="v3-kpi-label">{{ s.l }}</div>
                <div class="v3-kpi-value" :style="{color:s.c}">{{ s.v }}</div>
                <div class="v3-kpi-unit">{{ s.u }}</div>
              </div>
            </div>
          </div>

          <!-- bar chart -->
          <div class="v3-chart">
            <div class="v3-chart-head">
              <div class="v3-chart-title">ВРП по кварталам</div>
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

          <!-- AI feed -->
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

        <!-- tool tiles -->
        <div class="v3-tools">
          <div v-for="(x,i) in [{n:'Аналитика',d:'14 регионов',c:'#93C5FD',i:'▦'},{n:'Советник',d:'AI · GPT',c:'#10B981',i:'✦'},{n:'Обучение',d:'Курсы МСБ',c:'#FBBF24',i:'◐'},{n:'Финконтроль',d:'Потоки',c:'#A78BFA',i:'⬡'}]" :key="i" class="v3-tool-tile">
            <div class="v3-tool-top">
              <div class="v3-tool-icon" :style="{background: x.c+'33', color: x.c}">{{ x.i }}</div>
              <div class="v3-tool-dot" :style="{background: x.c, boxShadow: '0 0 6px '+x.c}" />
            </div>
            <div class="v3-tool-name">{{ x.n }}</div>
            <div class="v3-tool-desc">{{ x.d }}</div>
          </div>
        </div>
      </div>

      <!-- floating bottom badge -->
      <div class="v3-float-bottom">
        <div class="v3-float-icon">↑</div>
        <div>
          <div class="v3-float-label">Доход платформы</div>
          <div class="v3-float-val">₽4.2B · +12.4%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ---- Layout ---- */
.v3 {
  min-height: 100vh;
  background: #F5F8FC;
  color: #0F1A2B;
  display: grid;
  grid-template-columns: minmax(480px, 1fr) minmax(540px, 1.15fr);
  font-family: 'Manrope', 'Inter', system-ui, sans-serif;
  position: relative; overflow: hidden;
}

/* ---- LEFT ---- */
.v3-left {
  padding: 40px 56px;
  display: flex; flex-direction: column;
  justify-content: space-between;
  position: relative; z-index: 2;
}
.v3-header { display: flex; align-items: center; justify-content: space-between; }
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
  font-size: 54px; line-height: 1.02; letter-spacing: -1.8px;
  margin: 0; font-weight: 800;
}
.v3-accent { color: #003D7C; }
.v3-body {
  font-size: 15px; color: #334155; margin-top: 18px;
  max-width: 460px; line-height: 1.55;
}

/* tabs */
.v3-tabs {
  display: inline-flex; margin-top: 32px; margin-bottom: 20px;
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

/* roles */
.v3-roles { margin-bottom: 18px; }
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

/* fields */
.v3-fields { display: flex; flex-direction: column; gap: 14px; max-width: 460px; }
.v3-field-group { margin-bottom: 0; }
.v3-field-label {
  display: block; font-size: 11px; letter-spacing: 0.6px;
  text-transform: uppercase; color: #64748B; margin-bottom: 6px; font-weight: 700;
}
.v3-field {
  display: flex; align-items: center; background: #fff;
  border: 1.5px solid rgba(0,61,124,0.12);
  border-radius: 10px; transition: all .18s;
}
.v3-field.focus {
  border-color: #003D7C;
  box-shadow: 0 0 0 4px rgba(0,61,124,0.09);
}
.v3-field input {
  flex: 1; border: none; background: transparent;
  padding: 13px 16px; font-size: 15px; color: #0F1A2B;
  outline: none; font-family: inherit;
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
  display: flex; align-items: center; gap: 6px;
}

.v3-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 16px; margin-bottom: 22px; max-width: 460px;
}
.v3-remember {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #334155; cursor: pointer;
}
.v3-remember input { width: 15px; height: 15px; accent-color: #003D7C; }
.v3-forgot { font-size: 13px; color: #003D7C; font-weight: 600; text-decoration: none; }
.v3-spacer { height: 22px; }

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

.v3-switch {
  margin-top: 16px; font-size: 13px; color: #64748B; max-width: 460px;
}
.v3-switch button {
  background: transparent; border: none;
  color: #003D7C; cursor: pointer;
  font-weight: 700; padding: 0; font-size: 13px;
  font-family: inherit;
}

.v3-footer-left {
  font-size: 11px; letter-spacing: 0.4px; color: #64748B;
  display: flex; align-items: center; gap: 8px;
}
.v3-status-dot {
  width: 6px; height: 6px; border-radius: 999px; background: #059669;
  display: inline-block;
}

/* ---- RIGHT ---- */
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
  position: absolute; top: -140px; right: -140px;
  width: 460px; height: 460px; border-radius: 50%;
  background: radial-gradient(circle, rgba(147,197,253,0.33), transparent 70%);
  filter: blur(30px); animation: floaty 7s ease-in-out infinite;
  pointer-events: none;
}
.v3-right-glow2 {
  position: absolute; bottom: -180px; left: -80px;
  width: 380px; height: 380px; border-radius: 50%;
  background: radial-gradient(circle, rgba(0,84,166,0.4), transparent 70%);
  filter: blur(30px); pointer-events: none;
}

.v3-float-top {
  position: absolute; top: 32px; right: 32px; z-index: 3;
  padding: 8px 12px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  backdrop-filter: blur(12px);
  border-radius: 999px;
  font-size: 11px; font-weight: 600; color: #fff;
  display: flex; align-items: center; gap: 8px;
  font-family: 'JetBrains Mono', monospace; letter-spacing: 0.4px;
}
.v3-live-dot {
  width: 6px; height: 6px; border-radius: 50%; display: inline-block;
  background: #10B981; box-shadow: 0 0 8px #10B981;
  animation: pulse 2s infinite;
}

.v3-dashboard {
  position: relative; z-index: 2;
  width: 100%; max-width: 600px;
  transform: perspective(1400px) rotateY(-7deg) rotateX(3deg);
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
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 14px;
  padding: 14px 0;
  border-top: 1px solid rgba(255,255,255,0.12);
  border-bottom: 1px solid rgba(255,255,255,0.12);
  margin-bottom: 14px;
}
.v3-map-box {
  background: rgba(0,0,0,0.18); border-radius: 10px; padding: 10px;
  display: flex; flex-direction: column; justify-content: space-between;
}
.v3-map-svg { width: 100%; height: auto; display: block; }
.v3-map-footer {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 10px; font-family: 'JetBrains Mono', monospace;
  color: rgba(255,255,255,0.55); letter-spacing: 0.4px; margin-top: 4px;
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

/* chart */
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
.v3-legend-box {
  width: 8px; height: 8px; border-radius: 2px; display: inline-block;
}
.v3-legend-box.sky { background: #93C5FD; }
.v3-legend-box.green { background: linear-gradient(to top, #059669, #10B981); }

.v3-bars {
  height: 110px; display: flex; align-items: flex-end; gap: 6px; padding: 4px 0;
}
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

/* AI feed */
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
.v3-ai-dot {
  width: 4px; height: 4px; border-radius: 50%;
  background: rgba(255,255,255,0.25);
}
.v3-ai-dot.active { background: #fff; }

/* tool tiles */
.v3-tools {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
}
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

/* floating badges */
.v3-float-bottom {
  position: absolute; bottom: 28px; left: 28px; z-index: 3;
  padding: 10px 14px;
  background: #fff; color: #003D7C;
  border-radius: 10px;
  font-size: 12px; font-weight: 700;
  box-shadow: 0 20px 50px -15px rgba(0,0,0,0.5);
  display: flex; align-items: center; gap: 10px;
  transform: rotate(-2deg);
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

/* animations */
.fade-in { animation: slideUp .3s ease; }
@keyframes slideUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fade { from { opacity:0; } to { opacity:1; } }
@keyframes floaty { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-6px); } }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.55; } }

/* responsive */
@media (max-width: 1024px) {
  .v3 { grid-template-columns: 1fr; }
  .v3-right { display: none; }
  .v3-left { padding: 24px; }
}
</style>
