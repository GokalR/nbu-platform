<script setup>
import { ref, computed, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { businessPlanApi } from '@/services/businessPlanApi'

const { t, locale } = useI18n()
const router = useRouter()

// ---------------- form state ----------------
// STEP_KEYS[i] is the label key for step i. Step 9 is the loading screen.
const STEP_KEYS = [
  'orgType',           // 1
  'founder',           // 2
  'project',           // 3
  'assets',            // 4
  'products',          // 5
  'team',              // 6
  'utilities',         // 7
  'review',            // 8
  'result',            // 9 (loading / submit)
]

const step = ref(1)
const submitting = ref(false)
const submitError = ref('')

// Streaming progress state. Updated by businessPlanApi.generateStream() as
// SSE events arrive from the backend. `phase` is one of:
//   'validate' | 'candidates' | 'scoring' | 'llm.start' | 'llm.section' |
//   'finalize' | 'done' | 'error'
// When phase === 'llm.section', `section` carries the LLM section name.
const progress = ref({ phase: '', pct: 0, section: '' })

// Smoothed progress bar — interpolates toward `progress.value.pct` so the
// bar moves continuously instead of jumping between events.
const smoothedPct = ref(0)
let _smoothTimer = null
function _startSmoothing() {
  _stopSmoothing()
  _smoothTimer = setInterval(() => {
    const target = progress.value.pct || 0
    const cur = smoothedPct.value
    if (cur >= target) return
    // Tick up by 0.5% every 100ms — fast enough to feel alive, slow
    // enough that we never overshoot real events.
    smoothedPct.value = Math.min(target, cur + 0.5)
  }, 100)
}
function _stopSmoothing() {
  if (_smoothTimer) {
    clearInterval(_smoothTimer)
    _smoothTimer = null
  }
}

// Bilingual labels for each phase. We don't put these in locale files —
// they're tightly coupled to the streaming protocol and only used here.
const PHASE_LABELS = {
  validate:    { ru: 'Проверка анкеты',           uz: 'Anketa tekshiruvi' },
  candidates:  { ru: 'Подбор продуктов НБУ',      uz: 'NBU mahsulotlarini tanlash' },
  scoring:     { ru: 'Кредитный скоринг',         uz: 'Kredit skoring' },
  'llm.start': { ru: 'Подготовка анализа…',       uz: 'Tahlilga tayyorlanish…' },
  finalize:    { ru: 'Финализация',               uz: 'Yakunlash' },
  done:        { ru: 'Готово',                    uz: 'Tayyor' },
}

const SECTION_LABELS = {
  summary:              { ru: 'Резюме',                       uz: 'Xulosa' },
  executiveSummary:     { ru: 'Резюме для банка',             uz: 'Bank uchun xulosa' },
  marketContext:        { ru: 'Контекст рынка',               uz: 'Bozor konteksti' },
  operations:           { ru: 'Операционная модель',          uz: 'Operatsion model' },
  teamAssessment:       { ru: 'Оценка команды',               uz: 'Jamoa baholanishi' },
  financialsAssessment: { ru: 'Финансовый анализ',            uz: 'Moliyaviy tahlil' },
  extrasCategorization: { ru: 'Структура расходов',           uz: 'Xarajatlar tarkibi' },
  milestones:           { ru: 'Дорожная карта',               uz: 'Yoʻl xaritasi' },
  risks:                { ru: 'Идентификация рисков',         uz: 'Xatarlar' },
  kpis:                 { ru: 'Ключевые показатели (KPI)',    uz: 'Asosiy koʻrsatkichlar' },
  recommendedProducts:  { ru: 'Подбор кредита',               uz: 'Kredit tanlash' },
  actionableNextSteps:  { ru: 'Следующие шаги',               uz: 'Keyingi qadamlar' },
}

const progressLabel = computed(() => {
  const lng = locale.value === 'uz' ? 'uz' : 'ru'
  const p = progress.value
  if (!p.phase) return ''
  if (p.phase === 'llm.section') {
    return SECTION_LABELS[p.section]?.[lng] || PHASE_LABELS['llm.start'][lng]
  }
  return PHASE_LABELS[p.phase]?.[lng] || ''
})

// Industry categories — must match the backend dropdown source of truth in
// `services/industry_benchmarks.list_categories()`. If you add a category
// there, also add the locale keys `businessPlan.industries.<key>` in ru/uz.
const INDUSTRY_CATEGORIES = [
  'bakery', 'retail_food', 'manufacturing', 'services',
  'construction', 'agriculture', 'transport',
]

const form = reactive({
  organization: {
    type: 'legal_entity', // legal_entity | individual
    inn: '',
    uniqueCode: '',
    name: '',
    address: '',
    foundedDate: '',
    industryCategory: '',  // dropdown selection; empty = "Other / specify below"
    mainActivity: '',       // free-text refinement (kept for narrative)
    vatPayer: true,         // 12% VAT regime (default) vs 4% turnover (false)
    founder: '',
    director: '',
    charterCapital: 0,
  },
  project: {
    purpose: '',
    location: '',
    ownContribution: 0,
    loanAmount: 0,
    totalValue: 0,
    startupMonths: 3,
    termMonths: 36,
    graceMonths: 6,
    interestRate: 24,
  },
  assets: {
    creditFinanced: [{ name: '', qty: 0, unit: '' }],
    selfFinanced: [{ name: '', qty: 0, unit: '' }],
  },
  products: [
    { name: '', monthlyVolume: 0, unit: '', price: 0, currency: 'UZS' },
  ],
  team: [{ role: '', count: 0, salary: 0 }],
  utilities: {
    electricityKwh: 0,
    gasM3: 0,
    waterM3: 0,
    extras: [{ name: '', amount: 0 }],
  },
})

// Auto-compute total project value as ownContribution + loanAmount
const totalProjectValue = computed(
  () => Number(form.project.ownContribution || 0) + Number(form.project.loanAmount || 0),
)

// ---------------- derived totals (review step) ----------------
const monthlyPayroll = computed(() =>
  form.team.reduce((s, r) => s + Number(r.count || 0) * Number(r.salary || 0), 0),
)
const annualPayroll = computed(() => monthlyPayroll.value * 12)

const utilitiesMonthly = computed(() => {
  const e = Number(form.utilities.electricityKwh || 0) * 900
  const g = Number(form.utilities.gasM3 || 0) * 1800
  const w = Number(form.utilities.waterM3 || 0) * 5500
  const extras = (form.utilities.extras || []).reduce(
    (s, r) => s + Number(r.amount || 0),
    0,
  )
  return { electricity: e, gas: g, water: w, extras, total: e + g + w + extras }
})

const monthlyRevenue = computed(() =>
  form.products.reduce(
    (s, p) => s + Number(p.monthlyVolume || 0) * Number(p.price || 0),
    0,
  ),
)

// ---------------- validation per step ----------------
function isStepValid(s) {
  switch (s) {
    case 1:
      return ['legal_entity', 'individual'].includes(form.organization.type)
    case 2:
      return (
        form.organization.name.trim() &&
        form.organization.address.trim() &&
        form.organization.mainActivity.trim() &&
        form.organization.industryCategory &&
        form.organization.founder.trim()
      )
    case 3:
      return (
        form.project.purpose.trim() &&
        form.project.location.trim() &&
        Number(form.project.loanAmount) > 0 &&
        Number(form.project.termMonths) > 0
      )
    case 4:
      return form.assets.creditFinanced.some((a) => a.name?.trim())
    case 5:
      return form.products.some(
        (p) => p.name?.trim() && Number(p.monthlyVolume) > 0 && Number(p.price) > 0,
      )
    case 6:
      return form.team.some(
        (r) => r.role?.trim() && Number(r.count) > 0 && Number(r.salary) > 0,
      )
    case 7:
      // utilities are optional but at least one of E/G/W or an extra item should
      // exist for a meaningful plan
      return (
        Number(form.utilities.electricityKwh) > 0 ||
        Number(form.utilities.gasM3) > 0 ||
        Number(form.utilities.waterM3) > 0 ||
        form.utilities.extras.some((e) => e.name?.trim() && Number(e.amount) > 0)
      )
    case 8:
      return true
    default:
      return true
  }
}

const currentStepValid = computed(() => isStepValid(step.value))
const stepStatus = (i) => {
  if (i < step.value) return 'done'
  if (i === step.value) return 'current'
  return 'pending'
}

function nextStep() {
  if (!currentStepValid.value) return
  if (step.value < 8) step.value += 1
  else if (step.value === 8) submit()
}

// Quick-test template: a realistic bakery in Tashkent. One click fills the
// whole form so you can skip to the review step and submit immediately.
function fillTemplate() {
  Object.assign(form.organization, {
    type: 'legal_entity',
    inn: '126156934',
    uniqueCode: '2395',
    name: 'Issiq Non Ishlab Chiqarish',
    address: 'Toshkent shahri, Yunusobod tumani, A. Temur ko‘chasi 115',
    foundedDate: '2024-04-07',
    industryCategory: 'bakery',
    mainActivity: 'Non mahsulotlarini ishlab chiqarish',
    vatPayer: true,
    founder: "Muhsinov Alisher Azizbek o'g'li",
    director: 'Muhsinov Alisher',
    charterCapital: 50_000_000,
  })
  Object.assign(form.project, {
    purpose: 'Oylik 85 000 dona quvvatga ega non zavodini ochish',
    location: 'Toshkent shahri, Yunusobod tumani',
    ownContribution: 50_000_000,
    loanAmount: 250_000_000,
    totalValue: 300_000_000,
    startupMonths: 3,
    termMonths: 36,
    graceMonths: 6,
    interestRate: 24,
  })
  form.assets.creditFinanced = [
    { name: 'Non pishirish pechi (o‘rta hajmli)', qty: 2, unit: 'dona' },
    { name: 'Xamir qoruvchi mashina (50 kg)', qty: 2, unit: 'dona' },
    { name: 'Xamir achitish shkafi', qty: 1, unit: 'dona' },
    { name: 'Non qoliplari', qty: 2000, unit: 'dona' },
  ]
  form.assets.selfFinanced = [
    { name: 'Yetkazib berish furgon', qty: 1, unit: 'dona' },
  ]
  form.products = [
    { name: '1-navli non', monthlyVolume: 35_000, unit: 'dona', price: 3950, currency: 'UZS' },
    { name: '2-navli non', monthlyVolume: 50_000, unit: 'dona', price: 3500, currency: 'UZS' },
  ]
  form.team = [
    { role: 'Nonvoy', count: 8, salary: 5_500_000 },
    { role: 'Yuk tashuvchi-haydovchi', count: 3, salary: 4_000_000 },
    { role: 'Buxgalter', count: 1, salary: 6_000_000 },
    { role: 'Sotuv menejeri', count: 1, salary: 7_000_000 },
  ]
  Object.assign(form.utilities, {
    electricityKwh: 2300,
    gasM3: 4000,
    waterM3: 2000,
  })
  form.utilities.extras = [
    { name: 'Ijara haqi', amount: 8_000_000 },
    { name: 'Un va tarkibiy mahsulotlar', amount: 120_000_000 },
  ]
  step.value = 8 // jump straight to review
}
function prevStep() {
  if (step.value > 1) step.value -= 1
}

// Click-to-jump from the stepper sidebar. Going backwards is always free;
// going forward only as far as the previous step's validation lets us
// (so a user can't skip required fields). Step 9 is loading — never
// jumpable.
function goToStep(target) {
  if (submitting.value) return
  if (target < 1 || target > 8) return
  if (target <= step.value) {
    step.value = target
    return
  }
  // Forward jump — every step from current up to target-1 must be valid.
  for (let s = step.value; s < target; s++) {
    if (!isStepValid(s)) {
      step.value = s
      return
    }
  }
  step.value = target
}

// ---------------- row helpers ----------------
function addAssetCredit() {
  form.assets.creditFinanced.push({ name: '', qty: 0, unit: '' })
}
function removeAssetCredit(i) {
  form.assets.creditFinanced.splice(i, 1)
}
function addAssetSelf() {
  form.assets.selfFinanced.push({ name: '', qty: 0, unit: '' })
}
function removeAssetSelf(i) {
  form.assets.selfFinanced.splice(i, 1)
}
function addProduct() {
  form.products.push({ name: '', monthlyVolume: 0, unit: '', price: 0, currency: 'UZS' })
}
function removeProduct(i) {
  form.products.splice(i, 1)
}
function addTeamRow() {
  form.team.push({ role: '', count: 0, salary: 0 })
}
function removeTeamRow(i) {
  form.team.splice(i, 1)
}
function addExtra() {
  form.utilities.extras.push({ name: '', amount: 0 })
}
function removeExtra(i) {
  form.utilities.extras.splice(i, 1)
}

// ---------------- submission ----------------
async function submit() {
  submitting.value = true
  submitError.value = ''
  step.value = 9 // show loading screen
  progress.value = { phase: 'validate', pct: 0, section: '' }
  smoothedPct.value = 0
  _startSmoothing()

  // Update totalValue from current ownContribution + loanAmount
  form.project.totalValue = totalProjectValue.value

  // Strip empty rows so backend doesn't have to
  const cleanAssets = (rows) => rows.filter((r) => (r.name || '').trim())
  const cleanProducts = form.products.filter((p) => (p.name || '').trim())
  const cleanTeam = form.team.filter((r) => (r.role || '').trim())
  const cleanExtras = form.utilities.extras.filter((e) => (e.name || '').trim())

  const payload = {
    lang: locale.value,
    organization: { ...form.organization },
    project: { ...form.project },
    assets: {
      creditFinanced: cleanAssets(form.assets.creditFinanced),
      selfFinanced: cleanAssets(form.assets.selfFinanced),
    },
    products: cleanProducts,
    team: cleanTeam,
    utilities: { ...form.utilities, extras: cleanExtras },
  }

  // Streaming endpoint with live progress. Falls back to non-streaming
  // automatically if the SSE channel is unavailable (returns same shape).
  const res = await businessPlanApi.generateStream(payload, (p) => {
    progress.value = p
  })
  submitting.value = false
  _stopSmoothing()

  if (!res.ok) {
    // Validation errors from the input gate come back as res.errors
    if (res.errors && Array.isArray(res.errors) && res.errors.length) {
      submitError.value = res.errors.map((e) => e.message).join(' • ')
    } else {
      submitError.value =
        res.reason === 'no-backend'
          ? t('businessPlan.errors.noBackend')
          : res.error || t('businessPlan.errors.generic')
    }
    step.value = 8 // back to review
    return
  }

  // Snap progress to 100 before navigating so the bar isn't mid-animation
  smoothedPct.value = 100
  progress.value = { phase: 'done', pct: 100, section: '' }

  // The streaming endpoint returns only the id; the result page will load
  // the full plan via getPlan() (no sessionStorage cache for streamed
  // results — keeps the protocol simple).
  router.push({ name: 'business-plan-result', params: { id: res.data.id } })
}

function exitWizard() {
  if (confirm(t('businessPlan.exitConfirm'))) router.push('/tools')
}

// Stop the smoothing interval if the user navigates away mid-generation.
onUnmounted(() => _stopSmoothing())
</script>

<template>
  <div class="bp-wizard">
    <!-- top bar -->
    <header class="bp-topbar">
      <button class="bp-back" @click="exitWizard" :title="t('businessPlan.exit')">
        <AppIcon name="close" />
      </button>
      <div class="bp-brand">
        <img src="/nbu_logo.png" alt="NBU" />
        <div>
          <div class="bp-brand-title">{{ t('businessPlan.title') }}</div>
          <div class="bp-brand-sub">{{ t('businessPlan.subtitle') }}</div>
        </div>
      </div>
      <div class="bp-lang">
        <button
          :class="['bp-lang-btn', locale === 'uz' && 'is-active']"
          @click="locale = 'uz'"
        >UZ</button>
        <button
          :class="['bp-lang-btn', locale === 'ru' && 'is-active']"
          @click="locale = 'ru'"
        >RU</button>
      </div>
    </header>

    <main class="bp-main">
      <!-- left: stepper -->
      <aside class="bp-stepper">
        <ol>
          <li
            v-for="(key, i) in STEP_KEYS.slice(0, 8)"
            :key="key"
            :class="['bp-step', `is-${stepStatus(i + 1)}`, 'is-clickable']"
            role="button"
            tabindex="0"
            @click="goToStep(i + 1)"
            @keyup.enter="goToStep(i + 1)"
          >
            <span class="bp-step-num">
              <AppIcon v-if="stepStatus(i + 1) === 'done'" name="check" />
              <template v-else>{{ i + 1 }}</template>
            </span>
            <span class="bp-step-label">{{ t(`businessPlan.steps.${key}`) }}</span>
          </li>
          <li :class="['bp-step', step === 9 ? 'is-current' : 'is-pending']">
            <span class="bp-step-num">9</span>
            <span class="bp-step-label">{{ t('businessPlan.steps.result') }}</span>
          </li>
        </ol>
      </aside>

      <!-- right: panel -->
      <section class="bp-panel">
        <!-- STEP 1: org type -->
        <div v-if="step === 1" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.orgType') }}</h2>
          <p class="bp-step-hint">{{ t('businessPlan.hints.orgType') }}</p>
          <div class="bp-choice-stack">
            <button
              :class="['bp-choice', form.organization.type === 'legal_entity' && 'is-active']"
              @click="form.organization.type = 'legal_entity'"
            >
              <AppIcon name="apartment" />
              {{ t('businessPlan.orgTypes.legal_entity') }}
            </button>
            <button
              :class="['bp-choice', form.organization.type === 'individual' && 'is-active']"
              @click="form.organization.type = 'individual'"
            >
              <AppIcon name="person" />
              {{ t('businessPlan.orgTypes.individual') }}
            </button>
          </div>

          <!-- Quick-test template -->
          <div class="bp-template">
            <div class="bp-template-divider">
              <span>{{ t('businessPlan.template.or') }}</span>
            </div>
            <button class="bp-template-btn" @click="fillTemplate">
              <AppIcon name="auto_fix_high" />
              <span>
                <strong>{{ t('businessPlan.template.title') }}</strong>
                <small>{{ t('businessPlan.template.subtitle') }}</small>
              </span>
            </button>
          </div>
        </div>

        <!-- STEP 2: founder / org details -->
        <div v-else-if="step === 2" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.founder') }}</h2>
          <div class="bp-grid-2">
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.inn') }}</span>
              <input v-model="form.organization.inn" inputmode="numeric" placeholder="123456789" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.uniqueCode') }}</span>
              <input v-model="form.organization.uniqueCode" />
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.name') }}</span>
              <input v-model="form.organization.name" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.foundedDate') }}</span>
              <input v-model="form.organization.foundedDate" type="date" />
            </label>
            <label class="bp-field bp-col-span-2">
              <span class="req">{{ t('businessPlan.fields.address') }}</span>
              <input v-model="form.organization.address" />
            </label>

            <!-- Industry category — drives benchmark selection for scoring -->
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.industryCategory') }}</span>
              <select v-model="form.organization.industryCategory">
                <option value="">{{ t('businessPlan.industries.select') }}</option>
                <option v-for="cat in INDUSTRY_CATEGORIES" :key="cat" :value="cat">
                  {{ t(`businessPlan.industries.${cat}`) }}
                </option>
                <option value="other">{{ t('businessPlan.industries.other') }}</option>
              </select>
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.mainActivity') }}</span>
              <input v-model="form.organization.mainActivity"
                     :placeholder="t('businessPlan.placeholders.mainActivity')" />
            </label>

            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.founder') }}</span>
              <input v-model="form.organization.founder" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.director') }}</span>
              <input v-model="form.organization.director" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.charterCapital') }}</span>
              <input v-model.number="form.organization.charterCapital" type="number" min="0" />
            </label>

            <!-- VAT regime — drives turnover-tax computation for non-payers -->
            <label class="bp-field bp-col-span-2 bp-checkbox-field">
              <input type="checkbox" v-model="form.organization.vatPayer" />
              <span>
                <strong>{{ t('businessPlan.fields.vatPayer') }}</strong>
                <small>{{ t('businessPlan.hints.vatPayer') }}</small>
              </span>
            </label>
          </div>
        </div>

        <!-- STEP 3: project / financing -->
        <div v-else-if="step === 3" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.project') }}</h2>

          <h3 class="bp-section-h">{{ t('businessPlan.sections.projectDescription') }}</h3>
          <div class="bp-grid-2">
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.projectPurpose') }}</span>
              <input v-model="form.project.purpose" />
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.projectLocation') }}</span>
              <input v-model="form.project.location" />
            </label>
          </div>

          <h3 class="bp-section-h">{{ t('businessPlan.sections.financing') }}</h3>
          <div class="bp-grid-3">
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.ownContribution') }}</span>
              <input v-model.number="form.project.ownContribution" type="number" min="0" />
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.loanAmount') }}</span>
              <input v-model.number="form.project.loanAmount" type="number" min="0" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.totalValue') }}</span>
              <input :value="totalProjectValue" type="number" disabled class="bp-readonly" />
            </label>
          </div>

          <h3 class="bp-section-h">{{ t('businessPlan.sections.creditTerms') }}</h3>
          <div class="bp-grid-4">
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.startupMonths') }}</span>
              <input v-model.number="form.project.startupMonths" type="number" min="0" />
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.termMonths') }}</span>
              <input v-model.number="form.project.termMonths" type="number" min="1" />
            </label>
            <label class="bp-field">
              <span>{{ t('businessPlan.fields.graceMonths') }}</span>
              <input v-model.number="form.project.graceMonths" type="number" min="0" />
            </label>
            <label class="bp-field">
              <span class="req">{{ t('businessPlan.fields.interestRate') }}</span>
              <input v-model.number="form.project.interestRate" type="number" step="0.1" min="0" />
            </label>
          </div>
        </div>

        <!-- STEP 4: assets -->
        <div v-else-if="step === 4" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.assets') }}</h2>

          <div class="bp-table-block">
            <div class="bp-table-h">
              <h3 class="bp-section-h !mb-0">{{ t('businessPlan.sections.creditAssets') }}</h3>
              <button class="bp-add" @click="addAssetCredit">
                <AppIcon name="add" /> {{ t('businessPlan.actions.addAsset') }}
              </button>
            </div>
            <table class="bp-table">
              <thead>
                <tr>
                  <th>{{ t('businessPlan.cols.name') }}</th>
                  <th class="num">{{ t('businessPlan.cols.qty') }}</th>
                  <th>{{ t('businessPlan.cols.unit') }}</th>
                  <th class="act"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in form.assets.creditFinanced" :key="i">
                  <td><input v-model="row.name" /></td>
                  <td><input v-model.number="row.qty" type="number" min="0" class="num" /></td>
                  <td><input v-model="row.unit" /></td>
                  <td class="act">
                    <button class="bp-icon-btn" @click="removeAssetCredit(i)" :title="t('common.delete')">
                      <AppIcon name="delete" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="bp-table-block">
            <div class="bp-table-h">
              <h3 class="bp-section-h !mb-0">{{ t('businessPlan.sections.selfAssets') }}</h3>
              <button class="bp-add" @click="addAssetSelf">
                <AppIcon name="add" /> {{ t('businessPlan.actions.addAsset') }}
              </button>
            </div>
            <table class="bp-table">
              <thead>
                <tr>
                  <th>{{ t('businessPlan.cols.name') }}</th>
                  <th class="num">{{ t('businessPlan.cols.qty') }}</th>
                  <th>{{ t('businessPlan.cols.unit') }}</th>
                  <th class="act"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in form.assets.selfFinanced" :key="i">
                  <td><input v-model="row.name" /></td>
                  <td><input v-model.number="row.qty" type="number" min="0" class="num" /></td>
                  <td><input v-model="row.unit" /></td>
                  <td class="act">
                    <button class="bp-icon-btn" @click="removeAssetSelf(i)" :title="t('common.delete')">
                      <AppIcon name="delete" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- STEP 5: products / services -->
        <div v-else-if="step === 5" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.products') }}</h2>
          <p class="bp-step-hint">{{ t('businessPlan.hints.products') }}</p>

          <div
            v-for="(p, i) in form.products"
            :key="i"
            class="bp-card"
          >
            <div class="bp-card-h">
              <h4>{{ t('businessPlan.cards.product') }} #{{ i + 1 }}</h4>
              <button class="bp-icon-btn" @click="removeProduct(i)">
                <AppIcon name="close" />
              </button>
            </div>
            <div class="bp-grid-2">
              <label class="bp-field bp-col-span-2">
                <span class="req">{{ t('businessPlan.fields.productName') }}</span>
                <input v-model="p.name" />
              </label>
              <label class="bp-field">
                <span class="req">{{ t('businessPlan.fields.monthlyVolume') }}</span>
                <input v-model.number="p.monthlyVolume" type="number" min="0" />
              </label>
              <label class="bp-field">
                <span class="req">{{ t('businessPlan.fields.unit') }}</span>
                <input v-model="p.unit" :placeholder="t('businessPlan.placeholders.unit')" />
              </label>
              <label class="bp-field">
                <span class="req">{{ t('businessPlan.fields.unitPrice') }}</span>
                <input v-model.number="p.price" type="number" min="0" />
              </label>
              <label class="bp-field">
                <span>{{ t('businessPlan.fields.currency') }}</span>
                <select v-model="p.currency">
                  <option value="UZS">UZS</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                </select>
              </label>
            </div>
          </div>

          <button class="bp-add bp-add-block" @click="addProduct">
            <AppIcon name="add" /> {{ t('businessPlan.actions.addProduct') }}
          </button>
        </div>

        <!-- STEP 6: team -->
        <div v-else-if="step === 6" class="bp-step-body">
          <div class="bp-table-block">
            <div class="bp-table-h">
              <h2 class="bp-step-title !mb-0">{{ t('businessPlan.steps.team') }}</h2>
              <button class="bp-add" @click="addTeamRow">
                <AppIcon name="add" /> {{ t('businessPlan.actions.addEmployee') }}
              </button>
            </div>
            <table class="bp-table">
              <thead>
                <tr>
                  <th>{{ t('businessPlan.cols.role') }}</th>
                  <th class="num">{{ t('businessPlan.cols.count') }}</th>
                  <th class="num">{{ t('businessPlan.cols.monthlySalary') }}</th>
                  <th class="num">{{ t('businessPlan.cols.annualSalary') }}</th>
                  <th class="act"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(r, i) in form.team" :key="i">
                  <td><input v-model="r.role" /></td>
                  <td><input v-model.number="r.count" type="number" min="0" class="num" /></td>
                  <td><input v-model.number="r.salary" type="number" min="0" class="num" /></td>
                  <td class="num readonly-cell">
                    {{ ((Number(r.count || 0) * Number(r.salary || 0)) * 12).toLocaleString('ru-RU') }}
                  </td>
                  <td class="act">
                    <button class="bp-icon-btn" @click="removeTeamRow(i)">
                      <AppIcon name="delete" />
                    </button>
                  </td>
                </tr>
                <tr class="bp-total-row">
                  <td>{{ t('businessPlan.cols.total') }}</td>
                  <td class="num">{{ form.team.reduce((s, r) => s + Number(r.count || 0), 0) }}</td>
                  <td class="num">{{ monthlyPayroll.toLocaleString('ru-RU') }}</td>
                  <td class="num">{{ annualPayroll.toLocaleString('ru-RU') }}</td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- STEP 7: utilities -->
        <div v-else-if="step === 7" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.utilities') }}</h2>
          <p class="bp-step-hint">{{ t('businessPlan.hints.utilities') }}</p>

          <div class="bp-card">
            <div class="bp-card-h"><h4>{{ t('businessPlan.sections.utilitiesCalc') }}</h4></div>
            <div class="bp-util-row">
              <label class="bp-field">
                <span>{{ t('businessPlan.fields.electricity') }}</span>
                <input v-model.number="form.utilities.electricityKwh" type="number" min="0" />
              </label>
              <span class="bp-util-unit">{{ t('businessPlan.units.kwh') }}</span>
              <span class="bp-util-out">{{ utilitiesMonthly.electricity.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</span>
            </div>
            <div class="bp-util-row">
              <label class="bp-field">
                <span>{{ t('businessPlan.fields.gas') }}</span>
                <input v-model.number="form.utilities.gasM3" type="number" min="0" />
              </label>
              <span class="bp-util-unit">{{ t('businessPlan.units.m3') }}</span>
              <span class="bp-util-out">{{ utilitiesMonthly.gas.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</span>
            </div>
            <div class="bp-util-row">
              <label class="bp-field">
                <span>{{ t('businessPlan.fields.water') }}</span>
                <input v-model.number="form.utilities.waterM3" type="number" min="0" />
              </label>
              <span class="bp-util-unit">{{ t('businessPlan.units.m3') }}</span>
              <span class="bp-util-out">{{ utilitiesMonthly.water.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</span>
            </div>
          </div>

          <div class="bp-card">
            <div class="bp-card-h">
              <h4>{{ t('businessPlan.sections.otherFixed') }}</h4>
              <button class="bp-add" @click="addExtra">
                <AppIcon name="add" /> {{ t('businessPlan.actions.addExpense') }}
              </button>
            </div>
            <div v-for="(e, i) in form.utilities.extras" :key="i" class="bp-extra-row">
              <input v-model="e.name" :placeholder="t('businessPlan.placeholders.expenseName')" />
              <input v-model.number="e.amount" type="number" min="0" :placeholder="t('businessPlan.units.uzs')" />
              <button class="bp-icon-btn" @click="removeExtra(i)">
                <AppIcon name="delete" />
              </button>
            </div>
          </div>

          <div class="bp-summary">
            <div>
              <span>{{ t('businessPlan.summary.monthlyExpense') }}</span>
              <strong>{{ utilitiesMonthly.total.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</strong>
            </div>
            <div>
              <span>{{ t('businessPlan.summary.annualExpense') }}</span>
              <strong>{{ (utilitiesMonthly.total * 12).toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</strong>
            </div>
          </div>
        </div>

        <!-- STEP 8: review -->
        <div v-else-if="step === 8" class="bp-step-body">
          <h2 class="bp-step-title">{{ t('businessPlan.steps.review') }}</h2>
          <p class="bp-step-hint">{{ t('businessPlan.hints.review') }}</p>

          <div class="bp-review-grid">
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.org') }}</div>
              <div class="bp-review-val">{{ form.organization.name }}</div>
              <div class="bp-review-sub">{{ t(`businessPlan.orgTypes.${form.organization.type}`) }}</div>
            </div>
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.loan') }}</div>
              <div class="bp-review-val">{{ Number(form.project.loanAmount).toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</div>
              <div class="bp-review-sub">{{ form.project.termMonths }} {{ t('businessPlan.units.months') }} · {{ form.project.interestRate }}%</div>
            </div>
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.monthlyRevenue') }}</div>
              <div class="bp-review-val">{{ monthlyRevenue.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</div>
            </div>
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.team') }}</div>
              <div class="bp-review-val">{{ form.team.reduce((s, r) => s + Number(r.count || 0), 0) }} {{ t('businessPlan.review.people') }}</div>
              <div class="bp-review-sub">{{ monthlyPayroll.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzsPerMonth') }}</div>
            </div>
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.monthlyExpense') }}</div>
              <div class="bp-review-val">{{ utilitiesMonthly.total.toLocaleString('ru-RU') }} {{ t('businessPlan.units.uzs') }}</div>
            </div>
            <div class="bp-review-card">
              <div class="bp-review-label">{{ t('businessPlan.review.products') }}</div>
              <div class="bp-review-val">{{ form.products.filter((p) => p.name).length }}</div>
            </div>
          </div>

          <div v-if="submitError" class="bp-error">{{ submitError }}</div>
        </div>

        <!-- STEP 9: loading -->
        <div v-else-if="step === 9" class="bp-step-body bp-loading">
          <div class="bp-spinner"></div>
          <h2 class="bp-step-title">{{ t('businessPlan.loading.title') }}</h2>
          <p class="bp-progress-stage">
            {{ progressLabel || t('businessPlan.loading.hint') }}
          </p>
          <div class="bp-progress-bar">
            <div class="bp-progress-fill" :style="{ width: smoothedPct + '%' }"></div>
          </div>
          <p class="bp-progress-pct">{{ Math.floor(smoothedPct) }}%</p>
        </div>

        <!-- nav -->
        <div v-if="step <= 8" class="bp-nav">
          <button
            class="bp-btn bp-btn-secondary"
            :disabled="step === 1"
            @click="prevStep"
          >
            <AppIcon name="arrow_back" />
            {{ t('businessPlan.actions.prev') }}
          </button>
          <button
            class="bp-btn bp-btn-primary"
            :disabled="!currentStepValid || submitting"
            @click="nextStep"
          >
            <template v-if="step === 8">
              {{ t('businessPlan.actions.generate') }}
              <AppIcon name="auto_awesome" />
            </template>
            <template v-else>
              {{ t('businessPlan.actions.next') }}
              <AppIcon name="arrow_forward" />
            </template>
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Layout */
.bp-wizard {
  min-height: 100vh;
  background: #f4f6fa;
  display: flex;
  flex-direction: column;
}
.bp-topbar {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.bp-back {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
  display: grid;
  place-items: center;
  cursor: pointer;
  color: #475569;
}
.bp-back:hover {
  background: #f1f5f9;
}
.bp-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.bp-brand img {
  height: 36px;
}
.bp-brand-title {
  font-weight: 800;
  color: #003d7c;
  font-size: 17px;
  line-height: 1.1;
}
.bp-brand-sub {
  color: #64748b;
  font-size: 12px;
}
.bp-lang {
  display: flex;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}
.bp-lang-btn {
  padding: 8px 14px;
  background: #fff;
  border: 0;
  cursor: pointer;
  font-weight: 700;
  color: #64748b;
  font-size: 13px;
}
.bp-lang-btn.is-active {
  background: #003d7c;
  color: #fff;
}

.bp-main {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  padding: 24px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

/* Stepper */
.bp-stepper {
  background: #fff;
  border-radius: 16px;
  padding: 20px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  align-self: start;
  position: sticky;
  top: 24px;
}
.bp-stepper ol {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.bp-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  color: #64748b;
  user-select: none;
}
.bp-step.is-clickable { cursor: pointer; transition: background 0.15s; }
.bp-step.is-clickable:hover { background: rgba(0, 61, 124, 0.06); }
.bp-step.is-clickable:focus-visible {
  outline: 2px solid #003d7c; outline-offset: 2px;
}
.bp-step.is-current {
  background: rgba(0, 61, 124, 0.08);
  color: #003d7c;
  font-weight: 700;
}
.bp-step.is-done {
  color: #1e293b;
}
.bp-step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #e2e8f0;
  color: #64748b;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}
.bp-step.is-current .bp-step-num {
  background: #003d7c;
  color: #fff;
}
.bp-step.is-done .bp-step-num {
  background: #16a34a;
  color: #fff;
}

/* Panel */
.bp-panel {
  background: #fff;
  border-radius: 16px;
  padding: 32px 36px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  min-height: 540px;
}
.bp-step-body {
  flex: 1;
}
.bp-step-title {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px 0;
  text-align: center;
}
.bp-step-hint {
  color: #64748b;
  text-align: center;
  margin: 0 0 24px 0;
  font-size: 14px;
}
.bp-section-h {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin: 24px 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.bp-section-h:first-child {
  margin-top: 0;
}

/* Choice buttons */
.bp-choice-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 480px;
  margin: 24px auto 0;
}
.bp-choice {
  padding: 16px 20px;
  border-radius: 12px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.18s;
}
.bp-choice:hover {
  border-color: #003d7c;
}
.bp-choice.is-active {
  background: #003d7c;
  color: #fff;
  border-color: #003d7c;
}

/* Quick-test template button */
.bp-template {
  max-width: 480px;
  margin: 32px auto 0;
}
.bp-template-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}
.bp-template-divider::before,
.bp-template-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}
.bp-template-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 12px;
  border: 1.5px dashed #003d7c;
  background: #f0f7ff;
  color: #003d7c;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: all 0.18s;
}
.bp-template-btn:hover {
  background: #003d7c;
  color: #fff;
}
.bp-template-btn span {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bp-template-btn strong { font-size: 14px; font-weight: 700; }
.bp-template-btn small { font-size: 12px; opacity: 0.85; }

/* Fields */
.bp-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.bp-grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
.bp-grid-4 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 16px;
}
.bp-col-span-2 {
  grid-column: span 2;
}
.bp-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.bp-field span {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}
.bp-field span.req::after {
  content: ' *';
  color: #dc2626;
}
.bp-field input,
.bp-field select {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 14px;
  color: #0f172a;
  font-family: inherit;
}
.bp-field input:focus,
.bp-field select:focus {
  outline: none;
  border-color: #003d7c;
  box-shadow: 0 0 0 3px rgba(0, 61, 124, 0.12);
}
.bp-field input.bp-readonly {
  background: #f1f5f9;
  color: #475569;
}

/* Inline checkbox field — used for VAT regime + similar yes/no questions */
.bp-checkbox-field {
  flex-direction: row !important;
  align-items: flex-start;
  gap: 12px !important;
  padding: 12px 14px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
}
.bp-checkbox-field:hover { background: #f1f5f9; }
.bp-checkbox-field input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 2px 0 0 0 !important;
  cursor: pointer;
  accent-color: #003d7c;
  padding: 0 !important;
  flex-shrink: 0;
}
.bp-checkbox-field span {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bp-checkbox-field strong {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}
.bp-checkbox-field small {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  line-height: 1.4;
}

/* Tables */
.bp-table-block {
  margin-bottom: 24px;
}
.bp-table-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.bp-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  font-size: 14px;
}
.bp-table thead {
  background: #f8fafc;
}
.bp-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.5px;
}
.bp-table th.num,
.bp-table td.num {
  text-align: right;
}
.bp-table th.act,
.bp-table td.act {
  width: 48px;
  text-align: center;
}
.bp-table td {
  padding: 8px;
  border-top: 1px solid #f1f5f9;
}
.bp-table input {
  width: 100%;
  border: 1px solid transparent;
  background: transparent;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}
.bp-table input:focus {
  outline: none;
  border-color: #003d7c;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 61, 124, 0.12);
}
.bp-table input.num {
  text-align: right;
}
.bp-total-row {
  background: #f8fafc;
  font-weight: 700;
  color: #0f172a;
}
.bp-total-row td {
  padding: 10px 12px;
}
.readonly-cell {
  padding: 6px 8px;
  color: #64748b;
}

/* Cards */
.bp-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fff;
}
.bp-card-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.bp-card-h h4 {
  font-size: 14px;
  font-weight: 700;
  color: #003d7c;
  margin: 0;
}

/* Buttons */
.bp-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #16a34a;
  color: #fff;
  border: 0;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}
.bp-add:hover {
  background: #15803d;
}
.bp-add-block {
  width: 100%;
  justify-content: center;
  padding: 12px;
}
.bp-icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: grid;
  place-items: center;
}
.bp-icon-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

/* Utilities step */
.bp-util-row {
  display: grid;
  grid-template-columns: 1fr 80px 220px;
  align-items: end;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}
.bp-util-row:last-child {
  border-bottom: 0;
}
.bp-util-unit {
  color: #64748b;
  font-size: 12px;
  padding-bottom: 12px;
}
.bp-util-out {
  color: #003d7c;
  font-weight: 700;
  font-size: 16px;
  padding-bottom: 8px;
  text-align: right;
}
.bp-extra-row {
  display: grid;
  grid-template-columns: 1fr 200px 40px;
  gap: 8px;
  margin-bottom: 8px;
}
.bp-extra-row input {
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
}
.bp-summary {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.bp-summary > div {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.bp-summary span {
  color: #475569;
  font-weight: 600;
  font-size: 14px;
}
.bp-summary strong {
  color: #003d7c;
  font-size: 18px;
  font-weight: 800;
}

/* Review step */
.bp-review-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.bp-review-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}
.bp-review-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}
.bp-review-val {
  font-size: 18px;
  font-weight: 800;
  color: #003d7c;
}
.bp-review-sub {
  color: #64748b;
  font-size: 13px;
  margin-top: 4px;
}
.bp-error {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 14px;
}

/* Loading */
.bp-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 400px;
}
.bp-spinner {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 4px solid rgba(0, 61, 124, 0.15);
  border-top-color: #003d7c;
  animation: spin 0.9s linear infinite;
  margin-bottom: 24px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Progress bar (streaming generation) */
.bp-progress-stage {
  color: #475569;
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 16px 0;
  text-align: center;
  min-height: 20px; /* prevent layout jump when label changes */
}
.bp-progress-bar {
  width: 320px;
  max-width: 80%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
  margin: 8px 0 12px 0;
}
.bp-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #003d7c 0%, #1e6bb8 100%);
  border-radius: 999px;
  transition: width 0.25s ease-out;
}
.bp-progress-pct {
  color: #003d7c;
  font-size: 13px;
  font-weight: 700;
  margin: 0;
}

/* Nav */
.bp-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}
.bp-btn {
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  border: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.bp-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.bp-btn-primary {
  background: #003d7c;
  color: #fff;
}
.bp-btn-primary:not(:disabled):hover {
  background: #00306a;
}
.bp-btn-secondary {
  background: #f1f5f9;
  color: #475569;
}
.bp-btn-secondary:not(:disabled):hover {
  background: #e2e8f0;
}

/* Step 0 — financials uploader */
.bp-step.is-optional .bp-step-num { background: #fff; border: 1.5px dashed #94a3b8; color: #64748b; }
.bp-step.is-optional.is-current .bp-step-num { border-color: #003d7c; color: #fff; background: #003d7c; }
.bp-step.is-optional.is-done .bp-step-num { border: 0; }
.bp-step-optional {
  display: block; font-size: 10px; color: #94a3b8; font-weight: 500; margin-top: 1px;
}

.bp-fin-uploader { max-width: 600px; margin: 24px auto 0; display: flex; flex-direction: column; gap: 12px; }
.bp-fin-row { width: 100%; }
.bp-fin-file {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 18px; border-radius: 12px;
  border: 1.5px dashed #cbd5e1; background: #f8fafc;
  cursor: pointer; transition: all 0.18s;
}
.bp-fin-file:hover { border-color: #003d7c; background: #f0f7ff; }
.bp-fin-file input { display: none; }
.bp-fin-file-l { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.bp-fin-file-l strong { color: #003d7c; font-size: 14px; font-weight: 700; }
.bp-fin-file-l small { color: #64748b; font-size: 12px; }
.bp-fin-actions { display: flex; gap: 10px; justify-content: center; margin-top: 8px; }
.bp-mini-spinner {
  width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  animation: spin 0.7s linear infinite; display: inline-block;
}

.bp-fin-result { max-width: 600px; margin: 16px auto 0; }
.bp-fin-success {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 10px;
  background: #d1fae5; color: #065f46;
  font-size: 14px;
}
.bp-fin-figures {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.bp-fin-figures > div {
  background: #f8fafc; border-radius: 10px; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 2px;
}
.bp-fin-figures span {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  color: #64748b; letter-spacing: 0.5px;
}
.bp-fin-figures strong {
  font-size: 16px; color: #003d7c; font-weight: 800;
}
.bp-fin-figures strong small {
  font-size: 11px; color: #94a3b8; font-weight: 600;
}
.bp-fin-note {
  display: flex; gap: 8px; align-items: flex-start;
  padding: 10px 14px; border-radius: 8px;
  background: #f0f7ff; color: #003d7c;
  font-size: 13px; line-height: 1.5; margin: 12px 0 0 0;
  border-left: 3px solid #003d7c;
}

@media (max-width: 900px) {
  .bp-main {
    grid-template-columns: 1fr;
  }
  .bp-stepper {
    position: static;
  }
  .bp-grid-2,
  .bp-grid-3,
  .bp-grid-4 {
    grid-template-columns: 1fr;
  }
  .bp-review-grid {
    grid-template-columns: 1fr 1fr;
  }
  .bp-verdict-banner { grid-template-columns: 1fr; }
}
</style>
