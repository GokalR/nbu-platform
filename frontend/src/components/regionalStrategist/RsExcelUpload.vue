<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import { rsApi } from '@/services/rsApi'
import { generateLocalAnalysisAsync } from '@/services/rsLocalAnalysis'
import RsIcon from './RsIcon.vue'

const props = defineProps({
  lang: { type: String, default: 'ru' },
  cityId: { type: String, default: null },
  // When false, renders as upload-only (no Analyze button, no footer). Used
  // on Step 2 where user can attach files early; analysis runs later on Step 5.
  showAnalyze: { type: Boolean, default: true },
})

const emit = defineEmits(['uploaded', 'analyzed'])

const store = useRegionalStrategistStore()
const { submissionId, uploads, analysisStatus } = storeToRefs(store)

const L = {
  ru: {
    title: 'Загрузите финансовые отчёты (опционально)',
    hint: 'Два стандартных отчёта из 1С или Документы.uz закрывают весь финансовый профиль предприятия: Форма 1 показывает структуру активов и обязательств на дату, Форма 2 — обороты и прибыль за период. Больше файлов не требуется — все ключевые коэффициенты (маржа, ликвидность, долговая нагрузка, ROA/ROE) считаются по этим двум.',
    balanceTitle: 'Форма 1 — Бухгалтерский баланс',
    balanceDesc: 'Активы, обязательства и капитал на отчётную дату.',
    pnlTitle: 'Форма 2 — Отчёт о финансовых результатах',
    pnlDesc: 'Выручка, себестоимость, прибыль за период.',
    dropZone: 'Перетащите .xlsx сюда или',
    browse: 'выберите файл',
    uploading: 'Обработка…',
    uploaded: 'Принято',
    error: 'Ошибка',
    analyzeBtn: 'Сгенерировать анализ',
    analyzing: 'Анализирую…',
    analysisReady: 'Анализ готов',
    again: 'Перегенерировать',
    privacyNote: 'Файлы не покидают ваш браузер — используются только как подтверждение факта загрузки.',
  },
  uz: {
    title: 'Молиявий ҳисоботларни юкланг (ихтиёрий)',
    hint: '1С ёки Документы.uz дан иккита стандарт ҳисобот корхонанинг тўлиқ молиявий профилини қамрайди: Форма 1 санадаги активлар ва мажбуриятлар тузилмасини, Форма 2 эса давр учун айланма ва фойдани кўрсатади. Бошқа файллар керак эмас — барча асосий коэффициентлар (маржа, ликвидлик, қарз юки, ROA/ROE) шу иккитадан ҳисобланади.',
    balanceTitle: 'Форма 1 — Бухгалтерия баланси',
    balanceDesc: 'Ҳисобот санасидаги активлар, мажбуриятлар ва капитал.',
    pnlTitle: 'Форма 2 — Молиявий натижалар ҳисоботи',
    pnlDesc: 'Давр учун тушум, таннарх ва фойда.',
    dropZone: 'Файлни бу ерга ташланг ёки',
    browse: 'танланг',
    uploading: 'Қайта ишланмоқда…',
    uploaded: 'Қабул қилинди',
    error: 'Хато',
    analyzeBtn: 'Таҳлилни яратиш',
    analyzing: 'Таҳлил қилиняпти…',
    analysisReady: 'Таҳлил тайёр',
    again: 'Қайта яратиш',
    privacyNote: 'Файллар браузерингиздан чиқмайди — фақат юклаш фактини тасдиқлаш учун.',
  },
}
const t = computed(() => L[props.lang] ?? L.ru)

const statusByKind = ref({ balance: 'idle', pnl: 'idle' })
const errorByKind = ref({ balance: null, pnl: null })

const uploadedKinds = computed(() => new Set(uploads.value.map((u) => u.kind)))
const hasAny = computed(() => uploadedKinds.value.size > 0)
const hasBoth = computed(() => uploadedKinds.value.has('balance') && uploadedKinds.value.has('pnl'))
const backendConfigured = computed(() => rsApi.isConfigured())

async function onPick(kind, event) {
  const file = event.target.files?.[0]
  if (!file) return
  await handleFile(kind, file)
  event.target.value = ''
}

async function onDrop(kind, event) {
  event.preventDefault()
  const file = event.dataTransfer.files?.[0]
  if (!file) return
  await handleFile(kind, file)
}

async function handleFile(kind, file) {
  statusByKind.value[kind] = 'uploading'
  errorByKind.value[kind] = null

  // Local-first path: fake a short processing delay, record the "upload"
  // in the store so the UI reflects both files were received.
  if (!backendConfigured.value) {
    await new Promise((r) => setTimeout(r, 500))
    const fakeUpload = {
      id: `local-${kind}-${Date.now()}`,
      kind,
      original_filename: file.name,
      size_bytes: file.size,
      parsed: null,
      local: true,
    }
    store.addUpload(fakeUpload)
    statusByKind.value[kind] = 'uploaded'
    emit('uploaded', fakeUpload)
    return
  }

  // Backend path (unchanged): create submission if needed, then upload.
  const subId = await ensureSubmission()
  if (!subId) {
    statusByKind.value[kind] = 'error'
    errorByKind.value[kind] = store.analysisError
    return
  }

  const res = await rsApi.uploadExcel(subId, kind, file)
  if (!res.ok) {
    statusByKind.value[kind] = 'error'
    errorByKind.value[kind] = res.error || t.value.error
    return
  }
  store.addUpload(res.data)
  statusByKind.value[kind] = 'uploaded'
  emit('uploaded', res.data)
}

async function ensureSubmission() {
  if (submissionId.value) return submissionId.value
  store.setAnalysisStatus('submitting')
  const res = await rsApi.createSubmission({
    profile: store.profile,
    finance: store.finance,
    city_id: props.cityId,
    lang: props.lang,
  })
  if (!res.ok) {
    store.setAnalysisStatus('error', res.error || 'Не удалось создать сессию')
    return null
  }
  store.setSubmission(res.data.id)
  store.setAnalysisStatus('idle')
  return res.data.id
}

async function runAnalysis() {
  store.setAnalysisStatus('analyzing')

  // Local-first: generate analysis in the browser from profile + finance + city.
  if (!backendConfigured.value) {
    const analysis = await generateLocalAnalysisAsync({
      profile: store.profile,
      finance: store.finance,
      cityId: props.cityId,
      uploads: uploads.value,
      lang: props.lang,
    })
    store.setAnalysis(analysis)
    emit('analyzed', analysis)
    return
  }

  // Backend path.
  if (!submissionId.value) await ensureSubmission()
  if (!submissionId.value) return
  const res = await rsApi.runAnalysis(submissionId.value, { lang: props.lang })
  if (!res.ok) {
    store.setAnalysisStatus('error', res.error || t.value.error)
    return
  }
  store.setAnalysis(res.data)
  emit('analyzed', res.data)
}

function cardClass(kind) {
  const s = statusByKind.value[kind]
  if (uploadedKinds.value.has(kind) || s === 'uploaded') return 'border-emerald-300 bg-emerald-50/40'
  if (s === 'error') return 'border-red-300 bg-red-50/40'
  if (s === 'uploading') return 'border-amber-300 bg-amber-50/40'
  return 'border-rs-border bg-white'
}

// ERKIN PARVOZ NURI OLTIN — real 2024 numbers from the two provided xlsx forms.
// Units: raw UZS (ming som × 1000). Revenue 3.44 млрд, net profit 425 млн.
const ERKIN_PARSED = {
  balance: {
    computed: {
      absolutes: {
        totalAssets: 7_876_771_000,
        equity: 2_746_628_000,
      },
      ratios: {
        currentRatio: 1.19,
        debtToEquity: 1.87,
      },
    },
  },
  pnl: {
    computed: {
      absolutes: {
        revenue: 3_444_401_000,
        netProfit: 425_274_000,
      },
      ratios: {
        grossMargin: 0.33,
        netMargin: 0.1234,
        roa: 0.054,
        roe: 0.155,
      },
    },
  },
}

async function loadErkinSamples() {
  const files = [
    { kind: 'balance', url: '/samples/ERKIN_PARVOZ_balance.xlsx', name: 'ERKIN_PARVOZ_balance.xlsx' },
    { kind: 'pnl',     url: '/samples/ERKIN_PARVOZ_pnl.xlsx',     name: 'ERKIN_PARVOZ_pnl.xlsx' },
  ]
  for (const f of files) {
    statusByKind.value[f.kind] = 'uploading'
    errorByKind.value[f.kind] = null
    try {
      const res = await fetch(f.url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      const fakeUpload = {
        id: `erkin-${f.kind}-${Date.now()}`,
        kind: f.kind,
        original_filename: f.name,
        size_bytes: blob.size,
        parsed: {
          ...ERKIN_PARSED[f.kind],
          company: 'ERKIN PARVOZ NURI OLTIN MCHJ',
          ifut: '85100',
        },
        local: true,
        created_at: new Date().toISOString(),
      }
      store.addUpload(fakeUpload)
      statusByKind.value[f.kind] = 'uploaded'
      emit('uploaded', fakeUpload)
    } catch (e) {
      statusByKind.value[f.kind] = 'error'
      errorByKind.value[f.kind] = e.message || 'fetch failed'
    }
  }
}
</script>

<template>
  <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
    <div class="px-8 py-6"
         style="background: rgba(41,87,162,0.04); border-bottom: 1px solid rgba(41,87,162,0.1);">
      <div class="flex items-center gap-4">
        <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-navy-900 shrink-0">
          <RsIcon name="file-check" :size="16" class="text-white" />
        </span>
        <div class="min-w-0">
          <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.title }}</h2>
          <p class="font-sans text-[13px] text-gray-600 mt-1">{{ t.hint }}</p>
        </div>
      </div>
    </div>

    <div class="px-8 py-7 space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <label
          v-for="k in ['balance', 'pnl']" :key="k"
          :class="['flex items-start gap-3 rounded-[10px] border-2 border-dashed py-4 px-5 cursor-pointer transition-colors', cardClass(k)]"
          @dragover.prevent
          @drop="onDrop(k, $event)"
        >
          <span class="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full bg-gray-100">
            <RsIcon :name="uploadedKinds.has(k) ? 'check' : 'file-check'" :size="18"
                    :class="uploadedKinds.has(k) ? 'text-emerald-600' : 'text-steel-500'" />
          </span>
          <div class="flex-1 min-w-0">
            <div class="font-sans text-[14px] font-semibold text-carbon">
              {{ k === 'balance' ? t.balanceTitle : t.pnlTitle }}
            </div>
            <div class="text-[12px] text-steel-500 mt-[2px] leading-[1.4]">
              {{ k === 'balance' ? t.balanceDesc : t.pnlDesc }}
            </div>
            <div v-if="statusByKind[k] === 'uploading'" class="text-[12px] text-amber-700 mt-2">{{ t.uploading }}</div>
            <div v-else-if="uploadedKinds.has(k)" class="text-[12px] text-emerald-700 mt-2 truncate">
              {{ t.uploaded }} · {{ uploads.find((u) => u.kind === k)?.original_filename }}
            </div>
            <div v-else-if="statusByKind[k] === 'error'" class="text-[12px] text-red-700 mt-2 break-words">
              {{ errorByKind[k] }}
            </div>
            <div v-else class="text-[12px] text-steel-500 mt-2">
              {{ t.dropZone }} <span class="text-navy-900 font-semibold underline">{{ t.browse }}</span>
            </div>
            <input type="file" accept=".xlsx,.xls,.xltx" class="hidden" @change="onPick(k, $event)" />
          </div>
        </label>
      </div>

      <div class="flex items-center justify-between gap-3 flex-wrap">
        <p class="text-[12px] text-steel-500 italic">{{ t.privacyNote }}</p>
        <button
          type="button"
          @click="loadErkinSamples"
          class="inline-flex items-center gap-2 text-[12px] font-semibold text-navy-900 border border-gold-500/40 bg-gold-500/[0.06] hover:bg-gold-500/[0.14] rounded-[8px] py-[6px] px-3 transition-colors"
          :title="lang === 'uz' ? 'ERKIN PARVOZ намуна файлларини юклаш' : 'Загрузить образцы ERKIN PARVOZ (баланс + ОПиУ)'"
        >
          <RsIcon name="file-check" :size="13" class="text-gold-500" />
          {{ lang === 'uz' ? 'Намуна: ERKIN PARVOZ (2 файл)' : 'Образцы: ERKIN PARVOZ (2 файла)' }}
        </button>
      </div>

      <div v-if="showAnalyze" class="flex items-center justify-between gap-4 pt-2 border-t border-rs-border">
        <div class="text-[12px] text-steel-500">
          <template v-if="hasAny">
            {{ hasBoth ? '2/2' : '1/2' }} {{ lang === 'uz' ? 'файл' : 'файлов' }}
          </template>
          <template v-else>
            {{ lang === 'uz' ? 'Файлларсиз ҳам таҳлил қилиш мумкин' : 'Можно запустить анализ и без файлов' }}
          </template>
        </div>
        <button
          type="button"
          :disabled="analysisStatus === 'analyzing'"
          @click="runAnalysis"
          class="inline-flex items-center gap-2 font-sans text-[13px] font-bold text-navy-900 bg-gold-500 hover:bg-[#C9A85F] disabled:opacity-50 rounded-[8px] py-[10px] px-5 transition-colors"
        >
          <RsIcon name="sparkles" :size="14" />
          <span v-if="analysisStatus === 'analyzing'">{{ t.analyzing }}</span>
          <span v-else-if="analysisStatus === 'ready'">{{ t.analysisReady }} · {{ t.again }}</span>
          <span v-else>{{ t.analyzeBtn }}</span>
        </button>
      </div>
    </div>
  </section>
</template>
