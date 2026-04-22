<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRsLang } from '@/composables/useRsLang'
import { useRsReference } from '@/composables/useRsReference'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import RsStatusTag from '@/components/regionalStrategist/RsStatusTag.vue'
import RsInsightBox from '@/components/regionalStrategist/RsInsightBox.vue'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'
import RsMargilanHeatmap from '@/components/regionalStrategist/RsMargilanHeatmap.vue'
import RsFerganaHeatmap from '@/components/regionalStrategist/RsFerganaHeatmap.vue'
import RsInputSummary from '@/components/regionalStrategist/RsInputSummary.vue'
import RsScoreBreakdown from '@/components/regionalStrategist/RsScoreBreakdown.vue'
import RsClaudeAnalysis from '@/components/regionalStrategist/RsClaudeAnalysis.vue'
import { STEP5_T } from './rs-step5-i18n'
import { CITIES } from '@/data/regionalStrategist/cities'
import { matchCreditProducts, collateralLabel } from '@/data/regionalStrategist/credit-products'
import { computeScore, peerMediansFor } from '@/data/regionalStrategist/scoring'
import { rsApi } from '@/services/rsApi'
import { generateLocalAnalysisAsync } from '@/services/rsLocalAnalysis'

// Map user's business direction to a sector key the backend uses to filter
// enterprises and the Yandex map. Kept as a pure lookup so the composable
// can react when the user changes their answer.
function directionToSector(direction = '') {
  const d = String(direction || '').toLowerCase()
  if (/tsentr|o.?quv|учебн|детск|богча|бо.?ча|sad|bog|kindergarten/.test(d)) return 'education'
  if (/tikuv|shvey|швей|atlas|textile|тексти|одежд|kiy/.test(d)) return 'textiles'
  if (/non|khleb|хлеб|konditer|кондитер|food|oshpaz|pitan/.test(d)) return 'food'
  if (/avto|auto|transport|mashin/.test(d)) return 'auto'
  if (/mebel|furniture|мебел/.test(d)) return 'furniture'
  if (/salon|krasot|gozall|go.?zall|parikmax|sartarosh|beauty/.test(d)) return 'beauty'
  if (/med|tibbiy|medit/.test(d)) return 'medical'
  return ''
}

const emit = defineEmits(['restart'])
const { lang } = useRsLang()
const showMap = ref(false)
watch(showMap, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})
const onEsc = (e) => { if (e.key === 'Escape') showMap.value = false }
if (typeof window !== 'undefined') window.addEventListener('keydown', onEsc)
onUnmounted(() => {
  window.removeEventListener('keydown', onEsc)
  document.body.style.overflow = ''
})

const store = useRegionalStrategistStore()
const { profile, finance, submissionId, uploads, analysis, analysisStatus } = storeToRefs(store)

// Detect pilot city from the user's profile answers. Only Fergana + Margilan
// have real data; everything else shows a "data not yet available" state.
const resolvedCityId = computed(() => {
  const h = [profile.value.hudud, profile.value.viloyat, profile.value.mahalla].join(' ').toLowerCase()
  if (/marg|марғ|марг/.test(h)) return 'margilan'
  if (/farg|фарғ|ферг|фарг/.test(h)) return 'fergana'
  return null
})
const isPilotCity = computed(() => resolvedCityId.value !== null)
const isMargilan = computed(() => resolvedCityId.value === 'margilan')
const isFergana = computed(() => resolvedCityId.value === 'fergana')

// Sector key derived from user's direction answer, feeds enterprise filter + map.
const resolvedSector = computed(() => directionToSector(finance.value.businessDirection))

// Backend-driven reference data (city KPIs, districts, enterprises, credit products).
// Non-pilot cities get empty refs — UI renders no-data banners for affected sections.
const {
  city: backendCity,
  districts: backendDistricts,
  enterprises: backendEnterprises,
  products: backendProducts,
  hasCityData,
  hasDistrictData,
  hasEnterpriseData,
} = useRsReference({ cityId: resolvedCityId, sector: resolvedSector })

const selectedCity = computed(() => {
  if (backendCity.value) return backendCity.value.data || backendCity.value
  if (resolvedCityId.value && CITIES[resolvedCityId.value]) return CITIES[resolvedCityId.value]
  return null
})

const t = computed(() => STEP5_T[lang.value])

// Yandex map covers education centers only today. For other sectors, render
// a "no coverage yet" banner instead of the iframe. Passing region + sector
// as URL params lets the static HTML filter its marker dataset accordingly.
const mapHasCoverage = computed(() => isPilotCity.value && resolvedSector.value === 'education')
const mapSrc = computed(() => {
  const region = resolvedCityId.value || ''
  const sector = resolvedSector.value || ''
  const qs = new URLSearchParams()
  if (region) qs.set('region', region)
  if (sector) qs.set('sector', sector)
  const query = qs.toString()
  return `/maps/fergana-education/index.html${query ? `?${query}` : ''}`
})

// Label the user's own region (what they picked), regardless of pilot status.
const userPickedLabel = computed(() => {
  const h = (profile.value.hudud || '').trim()
  const v = (profile.value.viloyat || '').trim()
  return h || v || (isPilotCity.value ? selectedCity.value.name[lang.value] : '')
})
const isCityDataReal = computed(() => {
  if (!isPilotCity.value) return false
  if (isMargilan.value) return true
  const h = (profile.value.hudud || '').toLowerCase()
  return !h
})

// Pick the most recent upload with computed ratios/absolutes (from backend parse).
const extractedFinancials = computed(() => {
  const ups = [...(uploads.value || [])].sort((a, b) => {
    const ta = new Date(a.created_at || 0).getTime()
    const tb = new Date(b.created_at || 0).getTime()
    return tb - ta
  })
  for (const u of ups) {
    const c = u?.parsed?.computed
    if (c && (c.ratios || c.absolutes)) {
      return { ratios: c.ratios || {}, absolutes: c.absolutes || {} }
    }
  }
  return null
})

const formatPct = (v) => (v == null || isNaN(v) ? '—' : `${(v * 100).toFixed(1)}%`)
const formatRatio = (v) => (v == null || isNaN(v) ? '—' : Number(v).toFixed(2))
const formatUzs = (v) => {
  if (v == null || isNaN(v)) return '—'
  const n = Number(v)
  if (Math.abs(n) >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(2)} ${lang.value === 'uz' ? 'mlrd' : 'млрд'}`
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)} ${lang.value === 'uz' ? 'mln' : 'млн'}`
  return n.toLocaleString('ru-RU')
}

const financialMetrics = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const r = f.ratios || {}
  const a = f.absolutes || {}
  const L = lang.value
  return [
    { key: 'revenue',      label: L === 'uz' ? 'Tushum'            : 'Выручка',             value: formatUzs(a.revenue),      kind: 'abs' },
    { key: 'netProfit',    label: L === 'uz' ? 'Sof foyda'         : 'Чистая прибыль',      value: formatUzs(a.netProfit),    kind: 'abs' },
    { key: 'grossMargin',  label: L === 'uz' ? 'Yalpi marja'        : 'Валовая маржа',       value: formatPct(r.grossMargin),  kind: 'pct' },
    { key: 'netMargin',    label: L === 'uz' ? 'Sof marja'         : 'Чистая маржа',        value: formatPct(r.netMargin),    kind: 'pct' },
    { key: 'roa',          label: 'ROA',                                                    value: formatPct(r.roa),          kind: 'pct' },
    { key: 'roe',          label: 'ROE',                                                    value: formatPct(r.roe),          kind: 'pct' },
    { key: 'currentRatio', label: L === 'uz' ? 'Joriy likvidlik'   : 'Текущ. ликвидность',  value: formatRatio(r.currentRatio), kind: 'ratio' },
    { key: 'debtToEquity', label: L === 'uz' ? 'Qarz/kapital'      : 'Долг/капитал',        value: formatRatio(r.debtToEquity), kind: 'ratio' },
  ].filter((m) => m.value !== '—')
})

/* ── Excel aggregates section helpers ────────────────────── */
const uploadedFiles = computed(() => (uploads.value || []).filter((u) => u?.original_filename || u?.id))
const hasExcelData = computed(() => uploadedFiles.value.length > 0 || !!extractedFinancials.value)

const kindLabel = (kind) => {
  const map = {
    ru: { balance: 'Баланс', pnl: 'ОПиУ', cashflow: 'ДДС' },
    uz: { balance: 'Balans', pnl: 'FZH', cashflow: 'PH' },
  }
  return map[lang.value]?.[kind] || kind || (lang.value === 'uz' ? 'Fayl' : 'Файл')
}

const formatSize = (bytes) => {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

const absoluteHighlights = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const a = f.absolutes || {}
  const L = lang.value
  const items = [
    { key: 'revenue',     raw: a.revenue,     label: L === 'uz' ? 'Yillik tushum'  : 'Годовая выручка', icon: 'trending-up',  color: '#0054A6', tint: '#EEF4FF',
      hint: L === 'uz' ? 'OPiU: jami tushum' : 'ОПиУ: итого выручка' },
    { key: 'netProfit',   raw: a.netProfit,   label: L === 'uz' ? 'Sof foyda'      : 'Чистая прибыль',  icon: 'sparkles',     color: '#10B981', tint: '#E6F7EE',
      hint: L === 'uz' ? 'Soliqdan soʻng'    : 'После налогов' },
    { key: 'totalAssets', raw: a.totalAssets, label: L === 'uz' ? 'Jami aktivlar'  : 'Итого активов',   icon: 'briefcase',    color: '#8B5CF6', tint: '#F3E8FF',
      hint: L === 'uz' ? 'Balans yakuni'     : 'Итог баланса' },
    { key: 'equity',      raw: a.equity,      label: L === 'uz' ? 'Oʻz kapital'     : 'Собственный капитал', icon: 'shield',  color: '#F59E0B', tint: '#FEF3C7',
      hint: L === 'uz' ? 'Passiv: III boʻlim': 'Пассив: раздел III' },
  ]
  return items
    .filter((m) => m.raw != null && !isNaN(m.raw))
    .map((m) => ({ ...m, value: formatUzs(m.raw) }))
})

// Sector-aware peer medians: a kindergarten's 12% net margin should not be
// compared to a retailer's 8% — use the bucket that matches businessDirection.
const PEER_MEDIANS = computed(() => peerMediansFor(finance.value.businessDirection))

const ratioBars = computed(() => {
  const f = extractedFinancials.value
  if (!f) return []
  const r = f.ratios || {}
  const L = lang.value
  const defs = [
    { key: 'grossMargin',  label: L === 'uz' ? 'Yalpi marja'      : 'Валовая маржа',      max: 0.6,  pct: true,  higherBetter: true },
    { key: 'netMargin',    label: L === 'uz' ? 'Sof marja'       : 'Чистая маржа',       max: 0.25, pct: true,  higherBetter: true },
    { key: 'roa',          label: 'ROA',                                                  max: 0.2,  pct: true,  higherBetter: true },
    { key: 'roe',          label: 'ROE',                                                  max: 0.35, pct: true,  higherBetter: true },
    { key: 'currentRatio', label: L === 'uz' ? 'Joriy likvidlik' : 'Текущ. ликвидность', max: 3,    pct: false, higherBetter: true },
    { key: 'debtToEquity', label: L === 'uz' ? 'Qarz/kapital'    : 'Долг/капитал',       max: 3,    pct: false, higherBetter: false },
  ]
  const clamp = (v, max) => Math.max(0, Math.min(100, (v / max) * 100))
  const fmtV = (v, pct) => (pct ? formatPct(v) : formatRatio(v))
  return defs
    .map((d) => {
      const user = r[d.key]
      const peer = PEER_MEDIANS.value[d.key]
      if (user == null || isNaN(user)) return null
      const diff = d.higherBetter ? user - peer : peer - user
      const ratio = diff / Math.max(Math.abs(peer), 0.01)
      const verdictTone = ratio >= 0.1 ? 'good' : ratio >= -0.15 ? 'warn' : 'bad'
      const verdictLabel = verdictTone === 'good'
        ? (L === 'uz' ? 'yaxshi' : 'выше')
        : verdictTone === 'warn' ? (L === 'uz' ? 'oʻrtacha' : 'средне')
        : (L === 'uz' ? 'past' : 'ниже')
      return {
        key: d.key,
        label: d.label,
        userLabel: fmtV(user, d.pct),
        peerLabel: fmtV(peer, d.pct),
        userBar: clamp(user, d.max),
        peerBar: clamp(peer, d.max),
        verdictTone,
        verdictLabel,
      }
    })
    .filter(Boolean)
})

const excelInsight = computed(() => {
  const f = extractedFinancials.value
  if (!f) return null
  const r = f.ratios || {}
  const L = lang.value
  const strong = []
  const weak = []

  if (r.netMargin != null) {
    if (r.netMargin >= 0.10) strong.push(L === 'uz' ? `sof marja ${(r.netMargin*100).toFixed(1)}% — yaxshi darajada` : `чистая маржа ${(r.netMargin*100).toFixed(1)}% — хороший уровень`)
    else if (r.netMargin >= 0.05) strong.push(L === 'uz' ? `sof marja ${(r.netMargin*100).toFixed(1)}%` : `чистая маржа ${(r.netMargin*100).toFixed(1)}%`)
    else weak.push(L === 'uz' ? `sof marja past (${(r.netMargin*100).toFixed(1)}%)` : `чистая маржа низкая (${(r.netMargin*100).toFixed(1)}%)`)
  }
  if (r.currentRatio != null) {
    if (r.currentRatio >= 1.5) strong.push(L === 'uz' ? 'likvidlik sogʻlom (>1.5)' : 'ликвидность здоровая (>1.5)')
    else if (r.currentRatio >= 1.0) weak.push(L === 'uz' ? `joriy likvidlik chegarada (${r.currentRatio.toFixed(2)}) — qisqa muddatli majburiyatlar cheklangan` : `текущая ликвидность на границе (${r.currentRatio.toFixed(2)}) — ограниченный запас по краткосрочным обязательствам`)
    else weak.push(L === 'uz' ? 'likvidlik xavfli (<1.0)' : 'ликвидность в зоне риска (<1.0)')
  }
  if (r.debtToEquity != null) {
    if (r.debtToEquity > 2) weak.push(L === 'uz' ? 'qarz yuki yuqori (D/E>2)' : 'высокая долговая нагрузка (D/E>2)')
    else if (r.debtToEquity > 1.5) weak.push(L === 'uz' ? `D/E ${r.debtToEquity.toFixed(2)} — yuqori` : `D/E ${r.debtToEquity.toFixed(2)} — повышенный`)
  }
  if (r.roe != null && r.roe > 0.12) strong.push(L === 'uz' ? `ROE ${(r.roe*100).toFixed(1)}% — kapital samarali ishlatilmoqda` : `ROE ${(r.roe*100).toFixed(1)}% — капитал работает эффективно`)
  if (r.roa != null && r.roa < 0.03) weak.push(L === 'uz' ? 'aktivlar rentabelligi past (ROA<3%)' : 'рентабельность активов низкая (ROA<3%)')

  if (!strong.length && !weak.length) return null
  const good = strong.length ? (L === 'uz' ? `Kuchli tomonlar: ${strong.join('; ')}.` : `Сильные стороны: ${strong.join('; ')}.`) : ''
  const bad = weak.length ? (L === 'uz' ? ` Eʻtibor berilishi kerak: ${weak.join('; ')}.` : ` Требует внимания: ${weak.join('; ')}.`) : ''
  return (good + bad).trim()
})

// On arrival at results: try backend API first, fall back to local generator.
const runLocalAnalysis = async () => {
  store.setAnalysisStatus('analyzing')
  const result = await generateLocalAnalysisAsync({
    profile: profile.value,
    finance: finance.value,
    cityId: resolvedCityId.value,
    uploads: uploads.value,
    lang: lang.value,
  })
  store.setAnalysis(result)
}

onMounted(async () => {
  if (analysis.value || analysisStatus.value === 'analyzing') return

  if (rsApi.isConfigured()) {
    store.setAnalysisStatus('analyzing')

    // Ensure submission exists (Step 2 uploads may have already created one).
    let backendOk = false
    if (!submissionId.value) {
      const created = await rsApi.createSubmission({
        profile: profile.value,
        finance: finance.value,
        city_id: resolvedCityId.value,
        lang: lang.value,
      })
      if (created.ok) {
        store.setSubmission(created.data.id)
      } else {
        // Backend unavailable — fall back to local analysis
        await runLocalAnalysis()
        return
      }
    }

    const res = await rsApi.runAnalysis(submissionId.value, {
      lang: lang.value,
      rules_score: scoreResult.value,
    })
    if (res.ok) {
      store.setAnalysis(res.data)
      backendOk = true
    }

    // If backend analysis failed, fall back to local generator instead of error
    if (!backendOk) {
      await runLocalAnalysis()
    }
    return
  }

  // No backend configured — local generator.
  await runLocalAnalysis()
})

// Map finance inputs to matcher arguments.
// Parse loan-amount option strings like '200–500 млн', '500 млн – 1 млрд', 'Более 1 млрд'
// into a representative numeric value in sum.  Uses the midpoint of a range.
function parseLoanAmount(raw) {
  const s = String(raw || '').toLowerCase()
  if (!s) return 0
  const mult = s.includes('млрд') ? 1e9 : 1e6 // default to млн
  // Extract all numbers from the string
  const nums = s.match(/[\d.]+/g)?.map(Number).filter(Number.isFinite) || []
  if (!nums.length) return 0
  if (nums.length === 1) {
    // "До 50 млн" → 50 млн; "Более 1 млрд" → 1 млрд; "50 млн гача" → 50 млн
    return nums[0] * mult
  }
  // Range like "200–500 млн" or "500 млн – 1 млрд"
  // If both млн and млрд present (e.g. '500 млн – 1 млрд'), parse individually
  if (s.includes('млн') && s.includes('млрд')) {
    return Math.round((nums[0] * 1e6 + nums[1] * 1e9) / 2)
  }
  return Math.round((nums[0] + nums[1]) / 2 * mult)
}

const matcherInputs = computed(() => {
  const amt = parseLoanAmount(finance.value.loanAmount)
  const collMap = {
    'Недвижимость': 'realEstate',
    'Автотранспорт': 'vehicle',
    'Страховой полис': 'insurance',
    'Недвижимость + автотранспорт': 'realEstate',
  }
  const coll = collMap[finance.value.collateralType] || (finance.value.hasCollateral === 'Да' ? 'realEstate' : null)
  const purposeMap = {
    'Оборотные средства': 'working',
    'Основные средства': 'fixed',
    'Покупка автотранспорта': 'vehicle',
    'Покупка недвижимости': 'realEstate',
  }
  const purpose = purposeMap[finance.value.businessGoal] || 'any'
  const entity = /ИП|ЯТТ/i.test(profile.value.entityType || '') ? 'IP' : 'LLC'
  const firstTime = profile.value.businessAge === '' || /нет|йўқ|менее/i.test(profile.value.businessAge || '')
  return { loanAmount: amt, collateral: coll, purpose, entityType: entity, firstTime, lang: lang.value }
})

const matchedProducts = computed(() => matchCreditProducts(matcherInputs.value).slice(0, 4))
const primaryMatch = computed(() => matchedProducts.value[0])
const altMatches = computed(() => matchedProducts.value.slice(1))

const formatProductCollateral = (p) =>
  p.collateral.map((c) => collateralLabel(c, lang.value)).join(' · ')

/* ── Live score from user data ────────────────────── */
const scoreResult = computed(() =>
  computeScore(profile.value, finance.value, resolvedCityId.value || 'fergana', extractedFinancials.value),
)
const RADIUS = 54
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const scoreOffset = computed(() => CIRCUMFERENCE - (scoreResult.value.total / 100) * CIRCUMFERENCE)
const scoreColor = computed(() =>
  scoreResult.value.total >= 70 ? '#16a34a' : scoreResult.value.total >= 50 ? '#d97706' : '#dc2626',
)
const verdictLabel = computed(() => {
  const map = {
    good: { ru: 'Хороший потенциал', uz: 'Yaxshi potentsial', cls: 'text-emerald-600 bg-emerald-50' },
    fair: { ru: 'Средний потенциал', uz: 'Oʻrta potentsial', cls: 'text-amber-600 bg-amber-50' },
    weak: { ru: 'Требует доработки', uz: 'Takomillashtirish kerak', cls: 'text-red-600 bg-red-50' },
  }
  return map[scoreResult.value.verdict]
})

/* ── SWOT colour map (inlined, was SWOTCard) ──────── */
const SWOT_STYLES = {
  emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', title: 'text-emerald-700', dot: 'bg-emerald-500' },
  red:     { bg: 'bg-red-50',     border: 'border-red-200',     title: 'text-red-700',     dot: 'bg-red-400' },
  blue:    { bg: 'bg-blue-50',    border: 'border-blue-200',    title: 'text-blue-700',    dot: 'bg-blue-500' },
  amber:   { bg: 'bg-amber-50',   border: 'border-amber-200',   title: 'text-amber-700',   dot: 'bg-amber-500' },
}

// Prefer Claude's SWOT (analysis.output.swot) over the static i18n fallback.
// Fallback only kicks in when Claude hasn't run or returned an incomplete payload.
const claudeSwot = computed(() => analysis.value?.output?.swot || null)
const swotFromClaude = computed(() =>
  Boolean(
    claudeSwot.value &&
      Array.isArray(claudeSwot.value.strengths) &&
      claudeSwot.value.strengths.length,
  ),
)
const swotQuadrants = computed(() => {
  const src = swotFromClaude.value ? claudeSwot.value : t.value.SWOT
  return [
    { title: t.value.swotStrengths,     color: 'emerald', items: src.strengths     || [] },
    { title: t.value.swotWeaknesses,    color: 'red',     items: src.weaknesses    || [] },
    { title: t.value.swotOpportunities, color: 'blue',    items: src.opportunities || [] },
    { title: t.value.swotThreats,       color: 'amber',   items: src.threats       || [] },
  ]
})

// Action plan — prefer Claude's structured nextSteps, fall back to static i18n.
// Claude shape: [{ order, title, why, deadline }]. Legacy/static shape: [{ title, body }].
const claudeNextSteps = computed(() => analysis.value?.output?.nextSteps || null)
const actionPlanFromClaude = computed(() =>
  Array.isArray(claudeNextSteps.value) && claudeNextSteps.value.length > 0,
)
const actionPlanItems = computed(() => {
  if (actionPlanFromClaude.value) {
    return claudeNextSteps.value.map((s, i) => ({
      title: s.title || s.name || '',
      body: s.why || s.description || '',
      deadline: s.deadline || '',
      status: null,
      order: s.order ?? i + 1,
    }))
  }
  return (t.value.ACTION_STEPS || []).map((s, i) => ({
    title: s.title || '',
    body: s.desc || s.body || '',
    deadline: s.week || '',
    status: s.status || 'neutral',
    order: i + 1,
  }))
})

// Score explanations from Claude (optional, one per factor).
const scoreExplanations = computed(() => analysis.value?.output?.scoreExplanations || [])

// Did the Claude call finish successfully and return useful output?
const hasClaudeOutput = computed(() => {
  const o = analysis.value?.output
  return Boolean(o && (o.summary || o.swot || o.nextSteps))
})
const claudeFailed = computed(() => analysisStatus.value === 'error')

/* ── Action step circle colour ────────────────────── */
const stepCircleClass = (i, total) => {
  if (i < 2) return 'bg-gold-500'
  if (i >= 6) return 'bg-emerald-500'
  return 'bg-navy-900'
}

const onDownload = () => {
  // eslint-disable-next-line no-alert
  alert(t.value.downloadAlert)
}

async function retryAnalysis() {
  if (!rsApi.isConfigured() || !submissionId.value) return
  if (analysisStatus.value === 'analyzing') return
  store.setAnalysisStatus('analyzing')
  const res = await rsApi.runAnalysis(submissionId.value, {
    lang: lang.value,
    rules_score: scoreResult.value,
  })
  if (res.ok) {
    store.setAnalysis(res.data)
  } else {
    store.setAnalysisStatus('error', res.error || 'Analysis failed')
  }
}
</script>

<template>
  <div class="animate-rs-fade-in-up space-y-8 rs-step5-root">
    <!-- Restart link -->
    <button
      type="button"
      @click="emit('restart')"
      class="font-sans text-[14px] font-medium text-navy-700 hover:bg-navy-900/[0.04] rounded-[8px] py-2 px-3 transition-colors duration-150"
    >
      {{ t.restartBtn }}
    </button>

    <!-- ═══ REGION / CITY SELECTION BANNER ═══ -->
    <section
      class="rounded-[14px] overflow-hidden border shadow-rs-card"
      :class="isPilotCity
        ? 'border-navy-200 bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900'
        : 'border-amber-200 bg-gradient-to-r from-amber-50 via-white to-amber-50'"
    >
      <div class="px-8 py-7 flex flex-wrap items-center justify-between gap-6">
        <div class="flex items-center gap-5 min-w-0">
          <span
            class="inline-flex items-center justify-center w-14 h-14 rounded-[14px] shrink-0"
            :class="isPilotCity ? 'bg-gold-500/20 text-gold-400' : 'bg-amber-100 text-amber-700'"
          >
            <RsIcon name="building-2" :size="26" />
          </span>
          <div class="min-w-0">
            <div
              class="font-mono text-[11px] font-bold uppercase tracking-[1.5px] mb-1"
              :class="isPilotCity ? 'text-gold-400' : 'text-amber-700'"
            >
              {{ lang === 'uz' ? 'Siz tanlagan hudud' : 'Выбранный вами регион' }}
            </div>
            <h3
              class="font-sans text-[22px] font-bold leading-tight truncate"
              :class="isPilotCity ? 'text-white' : 'text-carbon'"
            >
              <template v-if="profile.viloyat">{{ profile.viloyat }}</template>
              <template v-else-if="isPilotCity">{{ selectedCity.name[lang] }}</template>
              <template v-else>{{ lang === 'uz' ? 'Hudud koʻrsatilmagan' : 'Регион не указан' }}</template>
            </h3>
            <div
              class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 font-sans text-[13px]"
              :class="isPilotCity ? 'text-white/80' : 'text-gray-700'"
            >
              <span v-if="profile.hudud" class="inline-flex items-center gap-1.5">
                <RsIcon name="landmark" :size="13" />
                {{ profile.hudud }}
              </span>
              <span v-if="profile.hudud && profile.mahalla" :class="isPilotCity ? 'text-white/30' : 'text-gray-300'">·</span>
              <span v-if="profile.mahalla" class="inline-flex items-center gap-1.5">
                <RsIcon name="user" :size="13" />
                {{ lang === 'uz' ? 'mahalla' : 'махалля' }}: {{ profile.mahalla }}
              </span>
            </div>
          </div>
        </div>

        <div class="shrink-0 flex items-center gap-3">
          <span
            v-if="isPilotCity && isCityDataReal"
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-emerald-500/15 text-emerald-300 border border-emerald-400/30"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            {{ lang === 'uz' ? 'Toʻliq maʻlumot' : 'Полные данные' }}
          </span>
          <span
            v-else-if="isPilotCity"
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-gold-500/15 text-gold-300 border border-gold-400/30"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-gold-400"></span>
            {{ lang === 'uz' ? 'Pilot shahar' : 'Пилотный город' }}
          </span>
          <span
            v-else
            class="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] rounded-full py-1.5 px-3 bg-amber-100 text-amber-800 border border-amber-200"
          >
            <RsIcon name="alert-triangle" :size="12" />
            {{ lang === 'uz' ? 'Maʻlumotlar cheklangan' : 'Данные ограничены' }}
          </span>
        </div>
      </div>
    </section>

    <!-- ═══ CITY CONTEXT — moved to top as first content section. Pilot cities only; non-pilots get honest banner. ═══ -->
    <section v-if="isPilotCity" class="bg-white border border-rs-border rounded-[16px] overflow-hidden shadow-rs-card">
      <div class="px-10 py-8 flex items-start justify-between gap-5"
           style="background: linear-gradient(135deg, rgba(25,63,114,0.06) 0%, rgba(215,181,109,0.04) 100%); border-bottom: 1px solid rgba(25,63,114,0.1);">
        <div class="flex items-start gap-5">
          <span class="inline-flex items-center justify-center w-14 h-14 rounded-[14px] bg-navy-900 shrink-0 shadow-md">
            <RsIcon name="landmark" :size="26" class="text-gold-400" />
          </span>
          <div class="min-w-0">
            <div class="font-mono text-[12px] font-bold uppercase tracking-[1.5px] text-gold-500 mb-1">
              {{ lang === 'uz' ? 'Shahar konteksti' : 'Контекст города' }}
            </div>
            <h2 class="font-sans text-[30px] font-bold text-carbon leading-tight">{{ userPickedLabel }}</h2>
            <p class="font-sans text-[15px] text-gray-600 mt-2 max-w-[620px] leading-[1.5]">{{ t.cityContextHint }}</p>
          </div>
        </div>
        <span v-if="!isCityDataReal"
              class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-amber-700 bg-amber-50 border border-amber-200 rounded-[6px] py-1.5 px-2.5 self-start"
              :title="lang === 'uz' ? 'Shahar boʻyicha batafsil maʻlumotlar tayyorlanmoqda — quyida viloyat boʻyicha' : 'Детальные данные по городу в разработке — ниже показаны областные'">
          {{ lang === 'uz' ? 'Viloyat boʻyicha maʻlumotlar' : 'Данные по области' }}
        </span>
      </div>

      <!-- KPI tiles — bigger numbers, more breathing room -->
      <div class="px-10 py-9 grid grid-cols-2 md:grid-cols-4 gap-6">
        <div class="border border-rs-border/70 rounded-[12px] p-5 bg-gradient-to-br from-white to-navy-900/[0.02]">
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Aholi' : 'Население' }}</div>
          <div class="font-mono text-[34px] font-bold text-carbon mt-2 leading-none">
            {{ selectedCity.populationK.toLocaleString('ru-RU') }}<span class="text-[17px] font-medium text-steel-500 ml-1">{{ lang === 'uz' ? 'ming' : 'тыс.' }}</span>
          </div>
          <div class="text-[12px] text-steel-500 mt-2">{{ lang === 'uz' ? 'shahar markazi' : 'жители города' }}</div>
        </div>
        <div class="border border-rs-border/70 rounded-[12px] p-5 bg-gradient-to-br from-white to-navy-900/[0.02]">
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Sanoat' : 'Промышленность' }}</div>
          <div class="font-mono text-[34px] font-bold text-carbon mt-2 leading-none">
            {{ Math.round(selectedCity.industryBlnUzs).toLocaleString('ru-RU') }}<span class="text-[17px] font-medium text-steel-500 ml-1">{{ lang === 'uz' ? 'mlrd' : 'млрд' }}</span>
          </div>
          <div class="text-[12px] text-steel-500 mt-2">2024 · +104.3%</div>
        </div>
        <div class="border border-rs-border/70 rounded-[12px] p-5 bg-gradient-to-br from-white to-navy-900/[0.02]">
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">
            {{ selectedCity.id === 'margilan' ? (lang === 'uz' ? 'Eksport' : 'Экспорт') : (lang === 'uz' ? 'Investitsiya' : 'Инвестиции') }}
          </div>
          <div class="font-mono text-[34px] font-bold text-carbon mt-2 leading-none">
            {{ (selectedCity.exportsBlnUzs ?? selectedCity.investmentsBlnUzs).toLocaleString('ru-RU') }}<span class="text-[17px] font-medium text-steel-500 ml-1">{{ lang === 'uz' ? 'mlrd' : 'млрд' }}</span>
          </div>
          <div class="text-[12px] text-steel-500 mt-2">{{ selectedCity.id === 'margilan' ? '2023' : '2023 · +29.4%' }}</div>
        </div>
        <div class="border border-rs-border/70 rounded-[12px] p-5 bg-gradient-to-br from-white to-navy-900/[0.02]">
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Mahallalar' : 'Махаллей' }}</div>
          <div class="font-mono text-[34px] font-bold text-carbon mt-2 leading-none">
            {{ selectedCity.mahallas.toLocaleString('ru-RU') }}
          </div>
          <div class="text-[12px] text-steel-500 mt-2">{{ lang === 'uz' ? 'oʻzini oʻzi boshqarish' : 'самоуправления' }}</div>
        </div>
      </div>

      <!-- Regional demographic + social context row -->
      <div class="px-10 pb-3 grid grid-cols-2 md:grid-cols-4 gap-6 border-t border-rs-border/50 pt-7">
        <div>
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Tugʻilish (viloyat)' : 'Рождаемость (область)' }}</div>
          <div class="font-mono text-[28px] font-bold text-carbon mt-2 leading-none">98 319</div>
          <div class="text-[12px] text-steel-500 mt-2">{{ lang === 'uz' ? '2025 · yangi oilalar' : '2025 · новорождённые' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Nikohlar (viloyat)' : 'Браки (область)' }}</div>
          <div class="font-mono text-[28px] font-bold text-carbon mt-2 leading-none">28 896</div>
          <div class="text-[12px] text-steel-500 mt-2">2025</div>
        </div>
        <div>
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Shahar ulushi' : 'Городское население' }}</div>
          <div class="font-mono text-[28px] font-bold text-carbon mt-2 leading-none">56.7<span class="text-[17px] font-medium text-steel-500 ml-1">%</span></div>
          <div class="text-[12px] text-steel-500 mt-2">{{ lang === 'uz' ? 'viloyat boʻyicha' : 'по области' }}</div>
        </div>
        <div>
          <div class="text-[11px] font-bold uppercase tracking-[1px] text-steel-500">{{ lang === 'uz' ? 'Tuman va shaharlar' : 'Районов и городов' }}</div>
          <div class="font-mono text-[28px] font-bold text-carbon mt-2 leading-none">15 + 4</div>
          <div class="text-[12px] text-steel-500 mt-2">{{ lang === 'uz' ? 'maʻmuriy birliklar' : 'административных единиц' }}</div>
        </div>
      </div>

      <div class="px-10 pb-9 pt-7">
        <div class="text-[12px] font-bold uppercase tracking-[1px] text-steel-500 mb-3">
          {{ lang === 'uz' ? 'Tavsiya etilgan sohalar' : 'Рекомендуемые отрасли' }}
        </div>
        <div class="flex flex-wrap gap-2.5">
          <span v-for="sec in selectedCity.topSectors || selectedCity.industries" :key="sec.key"
                class="inline-flex items-center gap-2.5 text-[14px] font-semibold text-navy-900 bg-navy-900/[0.05] border border-navy-900/[0.08] rounded-[10px] py-2 px-4">
            {{ lang === 'uz' ? sec.nameUz : sec.nameRu }}
            <span class="font-mono text-[12px] font-medium text-steel-500">{{ sec.blnUzs }} {{ lang === 'uz' ? 'mlrd' : 'млрд' }}</span>
          </span>
        </div>
      </div>
    </section>

    <!-- Non-pilot region: show honest 'no data yet' banner instead of city KPIs -->
    <section v-else class="bg-amber-50 border border-amber-200 rounded-[16px] overflow-hidden">
      <div class="px-10 py-8 flex items-start gap-5">
        <span class="inline-flex items-center justify-center w-14 h-14 rounded-[14px] bg-amber-500 shrink-0 shadow-md">
          <RsIcon name="alert-triangle" :size="24" class="text-white" />
        </span>
        <div class="min-w-0">
          <div class="font-mono text-[12px] font-bold uppercase tracking-[1.5px] text-amber-700 mb-1">
            {{ lang === 'uz' ? 'Shahar konteksti' : 'Контекст города' }}
          </div>
          <h2 class="font-sans text-[24px] font-bold text-amber-900 leading-tight">
            {{ lang === 'uz'
              ? 'Bu hudud boʻyicha batafsil maʻlumotlar hozircha mavjud emas'
              : 'Детальные данные по этому региону пока недоступны' }}
          </h2>
          <p class="font-sans text-[14px] text-amber-800 mt-2 leading-[1.55] max-w-[640px]">
            {{ lang === 'uz'
              ? 'Pilot shaharlar: Fargʻona va Margʻilon. AI tahlili sizning profil va moliyaviy maʻlumotlaringiz asosida umumiy tavsiya beradi.'
              : 'Пилотные города: Фергана и Маргилан. AI-анализ даст общую рекомендацию по вашему профилю и финансам без опоры на региональные показатели.' }}
          </p>
          <p v-if="userPickedLabel" class="font-sans text-[13px] text-amber-700 mt-3">
            {{ lang === 'uz' ? 'Siz tanlagan hudud:' : 'Ваш выбор:' }}
            <span class="font-semibold">{{ userPickedLabel }}</span>
          </p>
        </div>
      </div>
    </section>

    <!-- ═══ A — YOUR ANSWERS FROM STEP 1 + STEP 2 ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div class="px-8 py-6"
           style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);">
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-gold-500 shrink-0 font-mono text-[15px] font-bold text-white">A</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">
              {{ lang === 'uz' ? 'Siz toʻldirgan maʻlumotlar' : 'Ваши ответы' }}
              <span class="font-normal text-steel-500 text-[15px]">
                · {{ lang === 'uz' ? '1- va 2-qadam' : 'Шаг 1 и Шаг 2' }}
              </span>
            </h2>
            <p class="font-sans text-[13px] text-gray-600 mt-1">
              {{ lang === 'uz'
                ? 'Quyidagi ball, SWOT va tavsiyalar siz byorgan javoblar asosida hisoblangan'
                : 'Балл, SWOT и рекомендации ниже рассчитаны на основании ваших ответов в анкете' }}
            </p>
          </div>
        </div>
      </div>
      <div class="px-8 py-7">
        <RsInputSummary :profile="profile" :finance="finance" :lang="lang" />
      </div>
    </section>

    <!-- ═══ B — AGGREGATED EXCEL DATA (only when user uploaded financials) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div class="px-8 py-6"
           style="background: rgba(16,185,129,0.05); border-bottom: 1px solid rgba(16,185,129,0.15);">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-emerald-500 shrink-0 font-mono text-[15px] font-bold text-white">B</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">
                {{ lang === 'uz' ? 'Excel fayldan agregat maʻlumotlar' : 'Агрегаты из вашего Excel' }}
              </h2>
              <p class="font-sans text-[13px] text-gray-600 mt-1">
                {{ lang === 'uz'
                  ? 'Standart 1S / Dokumenti.uz shakllari boʻyicha avtomatik hisoblandi'
                  : 'Автоматически посчитано по стандартным формам 1С / Документы.uz' }}
              </p>
            </div>
          </div>
          <span v-if="uploadedFiles.length"
                class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-[6px] py-1 px-2">
            {{ uploadedFiles.length }} {{ lang === 'uz' ? 'fayl' : 'файл(ов)' }}
          </span>
        </div>
      </div>

      <!-- Empty state — user skipped Excel upload -->
      <div v-if="!hasExcelData" class="px-8 py-10 flex items-start gap-5">
        <span class="inline-flex items-center justify-center w-11 h-11 rounded-full bg-amber-50 shrink-0">
          <RsIcon name="file-question" :size="20" class="text-amber-600" />
        </span>
        <div class="max-w-[560px]">
          <div class="font-sans text-[15px] font-semibold text-carbon">
            {{ lang === 'uz' ? 'Excel fayl yuklanmagan' : 'Excel файл не загружен' }}
          </div>
          <p class="font-sans text-[13px] text-gray-600 mt-1 leading-[1.6]">
            {{ lang === 'uz'
              ? 'Moliya koʻrsatkichlari faqat Shag 2 da qoʻlda kiritilgan daromad/xarajatga asoslanadi. 1S yoki Dokumenti.uz dan Balans va Foyda va zarar hisobotini yuklasangiz, tahlil aniqroq boʻladi.'
              : 'Финансовые показатели взяты только из введённых вручную на Шаге 2 сумм дохода и расходов. Загрузите Баланс и Отчёт о прибылях из 1С или Документы.uz — тогда анализ будет точнее.' }}
          </p>
        </div>
      </div>

      <!-- Loaded state -->
      <div v-else class="px-8 py-8 space-y-7">
        <!-- Uploaded files list -->
        <div v-if="uploadedFiles.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div v-for="u in uploadedFiles" :key="u.id || u.original_filename"
               class="flex items-center gap-3 border border-rs-border rounded-[10px] py-3 px-4 bg-navy-900/[0.02]">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-[8px] bg-emerald-50 shrink-0">
              <RsIcon name="file-spreadsheet" :size="18" class="text-emerald-600" />
            </span>
            <div class="min-w-0 flex-1">
              <div class="font-sans text-[13px] font-semibold text-carbon truncate">
                {{ u.original_filename || (lang === 'uz' ? 'Fayl' : 'Файл') }}
              </div>
              <div class="flex items-center gap-2 mt-[2px]">
                <span class="text-[10px] font-bold uppercase tracking-[0.5px] rounded-[4px] py-[2px] px-[6px]"
                      :class="u.kind === 'balance' ? 'bg-blue-50 text-blue-700' : u.kind === 'pnl' ? 'bg-purple-50 text-purple-700' : 'bg-slate-100 text-slate-600'">
                  {{ kindLabel(u.kind) }}
                </span>
                <span v-if="u.size_bytes" class="text-[11px] text-steel-500 font-mono">
                  {{ formatSize(u.size_bytes) }}
                </span>
              </div>
            </div>
            <RsIcon name="check-circle" :size="18" class="text-emerald-500 shrink-0" />
          </div>
        </div>

        <!-- Headline absolute numbers -->
        <div v-if="absoluteHighlights.length"
             class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="m in absoluteHighlights" :key="m.key"
               class="border border-rs-border rounded-[10px] p-4 bg-gradient-to-br from-white to-navy-900/[0.02]">
            <div class="flex items-center justify-between">
              <div class="text-[10px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ m.label }}</div>
              <span class="inline-flex items-center justify-center w-6 h-6 rounded-[6px]"
                    :style="{ background: m.tint }">
                <RsIcon :name="m.icon" :size="12" :style="{ color: m.color }" />
              </span>
            </div>
            <div class="font-mono text-[20px] font-bold text-carbon mt-2">{{ m.value }}</div>
            <div class="font-sans text-[11px] text-steel-500 mt-1">{{ m.hint }}</div>
          </div>
        </div>

        <!-- Ratio bars (user's own ratios only) -->
        <div v-if="ratioBars.length">
          <div class="flex items-center justify-between gap-3 mb-3">
            <div class="font-sans text-[12px] font-semibold uppercase tracking-[1px] text-steel-500">
              {{ lang === 'uz' ? 'Moliyaviy koeffitsientlar' : 'Финансовые коэффициенты' }}
            </div>
          </div>
          <div class="border border-rs-border rounded-[10px] divide-y divide-rs-border">
            <div v-for="r in ratioBars" :key="r.key" class="py-3 px-4">
              <div class="flex items-center justify-between mb-2">
                <div class="font-sans text-[13px] font-medium text-carbon">{{ r.label }}</div>
                <div class="flex items-center gap-3 font-mono text-[12px]">
                  <span class="font-bold text-carbon">{{ r.userLabel }}</span>
                </div>
              </div>
              <div class="relative h-[8px] bg-slate-100 rounded-full overflow-hidden">
                <div class="absolute inset-y-0 left-0 bg-emerald-500 rounded-full transition-all"
                     :style="{ width: r.userBar + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Insight -->
        <div v-if="excelInsight"
             class="rounded-[8px] py-4 px-5 flex gap-3 items-start"
             style="border-left: 3px solid #10B981; background: rgba(16,185,129,0.06);">
          <RsIcon name="sparkles" :size="16" class="text-emerald-600 mt-[2px] shrink-0" />
          <div>
            <div class="font-sans text-[13px] font-bold text-emerald-700 mb-1">
              {{ lang === 'uz' ? 'Xulosa' : 'Вывод по финансам' }}
            </div>
            <div class="font-sans text-[14px] font-medium text-carbon leading-[1.6]">{{ excelInsight }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ AI ANALYSIS (demo: local generator runs on mount; backend-powered if VITE_API_URL is set) ═══ -->
    <RsClaudeAnalysis v-if="analysis" :analysis="analysis" :lang="lang" />

    <div v-else-if="analysisStatus === 'analyzing'"
         class="bg-white border border-rs-border rounded-[12px] py-6 px-8 text-center text-[13px] text-steel-500 italic">
      {{ lang === 'uz' ? 'AI tahlil qilyapti…' : 'AI анализирует…' }}
    </div>
    <div v-else-if="claudeFailed && !hasClaudeOutput"
         class="bg-amber-50 border border-amber-200 rounded-[12px] py-5 px-6">
      <div class="flex items-start gap-4">
        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-amber-500 shrink-0">
          <RsIcon name="alert-triangle" :size="18" class="text-white" />
        </span>
        <div class="flex-1 min-w-0">
          <h3 class="font-sans text-[15px] font-bold text-amber-900">
            {{ lang === 'uz' ? 'AI tahlili hozircha mavjud emas' : 'AI-анализ временно недоступен' }}
          </h3>
          <p class="font-sans text-[13px] text-amber-800 mt-1 leading-[1.5]">
            {{ lang === 'uz'
              ? 'Quyida siz kiritgan maʻlumot va shablon boʻyicha natijalar koʻrsatilgan. AI tahlilini qayta urinib koʻrish mumkin.'
              : 'Ниже показаны результаты по вашим данным и шаблонные рекомендации. Можно повторить попытку AI-анализа.' }}
          </p>
          <div v-if="store.analysisError" class="font-mono text-[11px] text-amber-700/80 mt-2 truncate">
            {{ store.analysisError }}
          </div>
          <button
            type="button"
            @click="retryAnalysis"
            :disabled="analysisStatus === 'analyzing'"
            class="mt-3 inline-flex items-center gap-2 text-[13px] font-semibold text-white bg-amber-600 hover:bg-amber-700 disabled:opacity-60 rounded-[8px] py-2 px-4 transition-colors"
          >
            <RsIcon name="refresh-cw" :size="14" />
            {{ analysisStatus === 'analyzing'
              ? (lang === 'uz' ? 'Urinish…' : 'Пробуем…')
              : (lang === 'uz' ? 'Qayta urinish' : 'Повторить') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ EDUCATION MAP — preview + click to expand fullscreen ═══ -->
    <section v-if="isPilotCity" class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6 flex items-center justify-between gap-4"
        style="background: rgba(25,63,114,0.03); border-bottom: 1px solid rgba(25,63,114,0.08);"
      >
        <div class="flex items-center gap-4 min-w-0">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-navy-900 shrink-0">
            <RsIcon name="map-pin" :size="16" class="text-white" />
          </span>
          <div class="min-w-0">
            <h3 class="font-sans text-[20px] font-bold text-carbon leading-tight">{{ t.section7MapTitle }}</h3>
            <p class="font-sans text-[13px] text-gray-600 mt-1">{{ t.section7MapSub }}</p>
          </div>
        </div>
        <button
          v-if="mapHasCoverage"
          type="button"
          @click="showMap = true"
          class="shrink-0 inline-flex items-center gap-2 text-[13px] font-semibold text-white rounded-[10px] py-2.5 px-5 transition-all hover:shadow-lg bg-navy-900 hover:bg-navy-800"
        >
          <RsIcon name="maximize-2" :size="15" />
          {{ lang === 'uz' ? 'Toʻliq ekranda ochish' : 'Открыть на весь экран' }}
        </button>
      </div>
      <!-- Inline map preview (education only) or no-coverage panel for other sectors -->
      <div v-if="mapHasCoverage" class="relative cursor-pointer group overflow-hidden" style="height: 480px;" @click="showMap = true">
        <iframe
          :src="mapSrc"
          class="w-full border-0 pointer-events-none absolute left-0"
          style="height: 1100px; top: -600px;"
          loading="lazy"
          tabindex="-1"
          :title="t.section7MapTitle"
        />
        <div class="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-white/90 to-transparent pointer-events-none" />
        <div class="absolute inset-0 bg-transparent group-hover:bg-black/[0.04] transition-colors flex items-center justify-center">
          <span class="inline-flex items-center gap-2 text-[14px] font-bold text-white rounded-full py-3 px-7 shadow-xl opacity-0 group-hover:opacity-100 scale-95 group-hover:scale-100 transition-all duration-200" style="background:rgba(20,159,168,0.94); backdrop-filter: blur(4px);">
            <RsIcon name="maximize-2" :size="16" />
            {{ lang === 'uz' ? 'Xaritani kattalashtirish' : 'Открыть карту' }}
          </span>
        </div>
      </div>
      <div v-else class="px-8 py-10 text-center">
        <div class="mx-auto w-12 h-12 rounded-full bg-amber-50 border border-amber-200 flex items-center justify-center mb-3">
          <RsIcon name="map-pin" :size="20" class="text-amber-600" />
        </div>
        <h4 class="font-sans text-[15px] font-bold text-carbon">
          {{ lang === 'uz'
            ? 'Bu soha uchun xarita maʻlumotlari tayyorlanmoqda'
            : 'Данные карты для этой отрасли готовятся' }}
        </h4>
        <p class="font-sans text-[13px] text-gray-600 mt-2 max-w-[520px] mx-auto leading-[1.55]">
          {{ lang === 'uz'
            ? 'Hozircha xarita faqat taʻlim markazlari uchun toʻldirilgan. Boshqa sohalar uchun — keyingi yangilanishda.'
            : 'Сейчас карта заполнена только по образовательным центрам. Другие отрасли — в следующих обновлениях.' }}
        </p>
      </div>
    </section>


    <!-- ═══ SECTION 1 — AI Scoring ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);"
      >
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">1</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section1Title }}</h2>
            <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section1Sub }}</p>
          </div>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="flex flex-col md:flex-row gap-8 md:gap-10">
          <!-- ScoreCircle (live) -->
          <div class="flex flex-col items-center gap-3 shrink-0">
            <div class="relative w-[140px] h-[140px]">
              <svg viewBox="0 0 120 120" class="w-full h-full -rotate-90">
                <circle cx="60" cy="60" :r="RADIUS" fill="none" stroke="#f3f4f6" stroke-width="10" />
                <circle
                  cx="60" cy="60" :r="RADIUS" fill="none"
                  :stroke="scoreColor" stroke-width="10" stroke-linecap="round"
                  :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="scoreOffset"
                  class="transition-all duration-1000"
                />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="font-mono text-[36px] font-bold text-carbon leading-none">{{ scoreResult.total }}</span>
                <span class="font-sans text-[12px] font-medium text-steel-500">{{ t.outOf100 }}</span>
              </div>
            </div>
            <span :class="['font-sans text-[14px] font-semibold rounded-[6px] py-1 px-3', verdictLabel.cls]">
              {{ verdictLabel[lang] }}
            </span>
            <p class="text-[11px] text-steel-500 text-center max-w-[160px] leading-[1.4]">
              {{ lang === 'uz' ? 'Har bir omilni ochib, qanday hisoblanganini koʻring' : 'Раскройте любой фактор, чтобы увидеть как он посчитан' }}
            </p>
          </div>

          <!-- Live breakdown — Claude-produced `scoreExplanations` fill in the
               per-factor "why + how to improve" block when the analysis succeeded. -->
          <div class="flex-1 min-w-0">
            <RsScoreBreakdown
              :factors="scoreResult.factors"
              :lang="lang"
              :explanations="scoreExplanations"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 2 — SWOT ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">2</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section2Title }}</h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section2Sub }}</p>
            </div>
          </div>
          <span v-if="swotFromClaude"
                class="shrink-0 inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-[6px] py-1 px-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            {{ lang === 'uz' ? 'AI tahlili' : 'AI-анализ' }}
          </span>
          <span v-else
                class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2"
                :title="t.demoBadgeHint">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="q in swotQuadrants" :key="q.title"
            :class="['rounded-[10px] border p-5', SWOT_STYLES[q.color].bg, SWOT_STYLES[q.color].border]"
          >
            <h4 :class="['font-sans text-[13px] font-bold uppercase tracking-[0.5px] mb-3', SWOT_STYLES[q.color].title]">
              {{ q.title }}
            </h4>
            <ul class="space-y-2">
              <li v-for="item in q.items" :key="item" class="flex items-start gap-2">
                <span :class="['w-[5px] h-[5px] rounded-full mt-[7px] shrink-0', SWOT_STYLES[q.color].dot]" />
                <span class="font-sans text-[13px] text-carbon leading-[1.5]">{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 3 — Geographic Heatmap (Margilan if matched, Fergana as default) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.04); border-bottom: 1px solid rgba(215,181,109,0.12);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-gold-500">3</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">
                {{ isMargilan
                  ? t.section3Title
                  : (lang === 'uz' ? 'Fargʻona viloyati — imkoniyatlar xaritasi' : 'Ферганская область — карта возможностей') }}
              </h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">
                {{ isMargilan
                  ? t.section3Sub
                  : (lang === 'uz' ? 'Har bir tuman uchun ball, aholi, raqobat va verdikt' : 'По каждому району — балл, население, конкуренция и вердикт') }}
              </p>
            </div>
          </div>
          <span class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8 space-y-6">
        <RsFerganaHeatmap :direction="finance.businessDirection" />

        <RsInsightBox v-if="isMargilan" variant="info" :title="t.locationInsightTitle">
          {{ t.locationInsightText }}
        </RsInsightBox>
        <RsInsightBox v-else variant="info"
          :title="lang === 'uz' ? 'Fergʻona viloyati uchun tavsiya' : 'Что это значит для вашего бизнеса в Фергане'"
        >
          {{ lang === 'uz'
            ? 'Fargʻona shahri — viloyat markazi, 328 409 aholi, sanoat mahsuloti 8 587 mlrd soʻm (2024). Viloyat boʻyicha 2025 yilda 98 319 tugʻilish, 28 896 nikoh — isteʻmol bozori barqaror oʻsmoqda. Oʻz biznesingiz joylashgan tumanni yuqoridagi reytingda koʻring.'
            : 'Фарғона шаҳар — столица области с 328 409 жителей и промышленной продукцией 8 587 млрд сум (2024). За 2025 год в области 98 319 рождений и 28 896 браков — потребительский рынок стабильно растёт. Найдите ваш район в рейтинге выше — он учитывает население, плотность бизнеса и конкуренцию.' }}
        </RsInsightBox>
      </div>
    </section>

    <!-- SECTION 4 (Business Plan) removed — it was almost entirely demo content
         (startup/monthly costs, revenue forecast) hardcoded for one sector.
         Actionable content now lives in Claude's nextSteps (Section 6 below). -->

    <!-- ═══ SECTION 5 — NBU Credit Products (climactic recommendation) ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(215,181,109,0.08); border-bottom: 1px solid rgba(215,181,109,0.2);"
      >
        <div class="flex items-center gap-4">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-gold-500">5</span>
          <div>
            <h2 class="font-sans text-[20px] font-bold text-carbon">
              {{ lang === 'uz' ? 'Sizga tavsiya qilingan NBU mahsulotlari' : 'Рекомендуемые продукты NBU для вас' }}
            </h2>
            <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">
              {{ lang === 'uz'
                ? 'Siz kiritgan profil, moliyaviy holat va Excel maʻlumotlari asosida tanlangan'
                : 'Подобрано по вашему профилю, финансам и данным из загруженных Excel-файлов' }}
            </p>
          </div>
        </div>
      </div>
      <div class="px-8 py-8 space-y-6">
        <!-- Primary product — live match -->
        <div v-if="primaryMatch"
          class="border border-rs-border rounded-[10px] overflow-hidden"
          style="border-top: 3px solid #D7B56D;"
        >
          <div class="px-6 py-5 flex items-center justify-between">
            <div>
              <div class="font-sans text-[11px] font-semibold text-gold-500 uppercase tracking-[0.5px] mb-1">
                {{ primaryMatch.product.tier === 'easy' ? (lang === 'uz' ? 'Engil mahsulot' : 'Облегчённый продукт') : (lang === 'uz' ? 'Standart mahsulot' : 'Стандартный продукт') }}
              </div>
              <h3 class="font-sans text-[20px] font-bold text-carbon">
                {{ primaryMatch.product.name[lang] }}
              </h3>
            </div>
            <span class="font-sans text-[12px] font-bold text-emerald-600 bg-emerald-50 rounded-[6px] py-[6px] px-[14px] uppercase tracking-[0.5px]">
              {{ t.recommendedBadge }}
            </span>
          </div>
          <div class="px-6 pb-6">
            <div class="divide-y divide-rs-border">
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.rateLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.rateLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.amountLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.amountLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.termLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.termLabel[lang] }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.collateralLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ formatProductCollateral(primaryMatch.product) }}</div>
              </div>
              <div class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.purposeLabel.replace(':','') }}</div>
                <div class="font-sans text-[14px] font-medium text-carbon">{{ primaryMatch.product.purposeLabel[lang] }}</div>
              </div>
              <div v-if="primaryMatch.reasons.length" class="flex gap-6 py-3">
                <div class="w-44 shrink-0 font-sans text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 pt-[2px]">{{ t.matchReasons }}</div>
                <ul class="space-y-1">
                  <li v-for="r in primaryMatch.reasons" :key="r" class="flex items-start gap-2">
                    <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[7px] shrink-0" />
                    <span class="font-sans text-[13px] text-carbon leading-[1.5]">{{ r }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional products -->
        <div v-if="altMatches.length">
          <div class="font-sans text-[12px] font-semibold uppercase tracking-[1px] text-steel-500 mb-4">
            {{ t.altProductsLabel }}
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              v-for="m in altMatches" :key="m.product.id"
              class="border border-rs-border rounded-[10px] py-[14px] px-[18px]"
            >
              <div class="font-sans text-[15px] font-semibold text-carbon">{{ m.product.name[lang] }}</div>
              <div class="font-sans text-[12px] font-normal text-gray-600 mt-[2px]">
                {{ m.product.tier === 'easy' ? (lang === 'uz' ? 'Engil' : 'Облегчённый') : (lang === 'uz' ? 'Standart' : 'Стандартный') }}
              </div>
              <div class="mt-3 space-y-1">
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.rateLabel }}</span> {{ m.product.rateLabel[lang] }}
                </div>
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.amountLabel }}</span> {{ m.product.amountLabel[lang] }}
                </div>
                <div class="font-sans text-[12px] text-steel-500">
                  <span class="font-semibold">{{ t.termLabel }}</span> {{ m.product.termLabel[lang] }}
                </div>
              </div>
              <p class="font-sans text-[12px] font-normal text-gray-600 mt-2 leading-[1.4]">{{ m.product.purposeLabel[lang] }}</p>
            </div>
          </div>
        </div>

        <p class="font-sans text-[12px] text-steel-500 italic">{{ t.catalogNote }}</p>
      </div>
    </section>

    <!-- ═══ SECTION 6 — Action Plan ═══ -->
    <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
      <div
        class="px-8 py-6"
        style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <span class="inline-flex items-center justify-center w-9 h-9 rounded-full font-mono text-[15px] font-bold text-white shrink-0 bg-navy-900">6</span>
            <div>
              <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.section6Title }}</h2>
              <p class="font-sans text-[14px] font-normal text-gray-600 mt-1">{{ t.section6Sub }}</p>
            </div>
          </div>
          <span v-if="actionPlanFromClaude"
                class="shrink-0 inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-[0.5px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-[6px] py-1 px-2">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            {{ lang === 'uz' ? 'AI tahlili' : 'AI-анализ' }}
          </span>
          <span v-else
                class="shrink-0 inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 rounded-[6px] py-1 px-2">
            {{ t.demoBadge }}
          </span>
        </div>
      </div>
      <div class="px-8 py-8">
        <div class="space-y-3">
          <div
            v-for="(s, i) in actionPlanItems" :key="`${s.order}-${s.title}`"
            class="flex items-start gap-4 border border-rs-border rounded-[10px] p-4"
          >
            <div class="flex flex-col items-center shrink-0">
              <span
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center font-mono text-[13px] font-bold text-white',
                  stepCircleClass(i, actionPlanItems.length),
                ]"
              >
                {{ s.order }}
              </span>
              <div v-if="i < actionPlanItems.length - 1" class="w-[2px] h-4 bg-rs-border mt-1" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <span class="font-sans text-[15px] font-semibold text-carbon">{{ s.title }}</span>
                <RsStatusTag v-if="s.status" :variant="s.status">{{ s.deadline }}</RsStatusTag>
                <span v-else-if="s.deadline"
                      class="inline-flex items-center text-[11px] font-semibold uppercase tracking-[0.5px] text-navy-700 bg-navy-900/[0.06] rounded-[6px] py-1 px-2">
                  {{ s.deadline }}
                </span>
              </div>
              <p v-if="s.body" class="font-sans text-[13px] text-gray-600 mt-1 leading-[1.5]">{{ s.body }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SECTION 7 — CTA ═══ -->
    <section
      class="rounded-[16px] py-14 px-10 text-center"
      style="background: linear-gradient(135deg, #0F2847, #193F72);"
    >
      <h2 class="font-sans text-[24px] font-bold text-white">{{ t.ctaTitle }}</h2>
      <p class="font-sans text-[15px] font-normal text-white/65 mt-2">{{ t.ctaSubtitle }}</p>
      <div class="flex items-center justify-center gap-4 mt-7">
        <a
          href="https://nbu.uz"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center justify-center font-sans text-[15px] font-bold text-navy-900 bg-gold-500 hover:bg-[#C9A85F] rounded-btn py-[14px] px-8 transition-colors duration-200"
        >
          {{ t.applyBtn }}
        </a>
        <button
          type="button"
          @click="onDownload"
          class="inline-flex items-center justify-center font-sans text-[15px] font-semibold text-white border-[1.5px] border-white/30 hover:bg-white/10 rounded-btn py-[13px] px-8 transition-colors duration-200"
        >
          {{ t.downloadBtn }}
        </button>
      </div>
      <button
        type="button"
        @click="emit('restart')"
        class="font-sans text-[14px] font-medium text-white/45 hover:text-white/70 mt-5 transition-colors duration-150"
      >
        {{ t.restartCta }}
      </button>
    </section>
  </div>

  <!-- ═══ FULLSCREEN MAP OVERLAY ═══ -->
  <Teleport to="body">
    <Transition name="rs-map-overlay">
      <div
        v-if="showMap"
        class="fixed inset-0 z-[9999]"
        style="background: #f1f2f7;"
      >
        <!-- Floating close button -->
        <button
          type="button"
          @click="showMap = false"
          class="absolute top-4 right-4 z-10 inline-flex items-center gap-2 text-[13px] font-semibold text-gray-600 hover:text-carbon bg-white/95 hover:bg-white border border-gray-200 rounded-[10px] py-2 px-3.5 shadow-lg backdrop-blur-sm transition-colors"
        >
          <RsIcon name="x" :size="16" />
          {{ lang === 'uz' ? 'Yopish' : 'Закрыть' }}
        </button>
        <!-- Map iframe fills full screen -->
        <iframe
          :src="mapSrc"
          class="w-full h-full border-0"
          :title="t.section7MapTitle"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<style>
/* Unscoped so bumps cascade into child Vue components on this page. */
.rs-step5-root .text-\[10px\]  { font-size: 12px !important; }
.rs-step5-root .text-\[11px\]  { font-size: 13px !important; font-weight: 600; }
.rs-step5-root .text-\[12px\]  { font-size: 14px !important; font-weight: 500; }
.rs-step5-root .text-\[13px\]  { font-size: 15px !important; font-weight: 500; }
.rs-step5-root .text-\[14px\]  { font-size: 16px !important; }
.rs-step5-root .text-\[15px\]  { font-size: 17px !important; }
.rs-step5-root .text-\[16px\]  { font-size: 19px !important; }
.rs-step5-root .text-\[17px\]  { font-size: 20px !important; }
.rs-step5-root .text-\[18px\]  { font-size: 22px !important; }
.rs-step5-root .text-\[20px\]  { font-size: 24px !important; }
.rs-step5-root .text-\[22px\]  { font-size: 26px !important; }
.rs-step5-root .text-\[24px\]  { font-size: 28px !important; }
.rs-step5-root .text-\[28px\]  { font-size: 32px !important; }
.rs-step5-root .text-\[30px\]  { font-size: 34px !important; }
.rs-step5-root .text-\[34px\]  { font-size: 38px !important; }
.rs-step5-root .text-\[36px\]  { font-size: 42px !important; }
.rs-step5-root .text-\[42px\]  { font-size: 48px !important; }

/* Bump weights one step up so text reads bolder everywhere. */
.rs-step5-root .font-normal    { font-weight: 500 !important; }
.rs-step5-root .font-medium    { font-weight: 600 !important; }
.rs-step5-root .font-semibold  { font-weight: 700 !important; }

/* Map overlay transition */
.rs-map-overlay-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.rs-map-overlay-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.rs-map-overlay-enter-from   { opacity: 0; transform: translateY(12px) scale(0.98); }
.rs-map-overlay-leave-to     { opacity: 0; transform: translateY(12px) scale(0.98); }
</style>
