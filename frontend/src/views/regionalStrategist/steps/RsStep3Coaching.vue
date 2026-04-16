<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import { useRsLang } from '@/composables/useRsLang'
import { guessSectorBucket } from '@/data/regionalStrategist/scoring'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'

const emit = defineEmits(['back', 'next'])
const { lang } = useRsLang()
const store = useRegionalStrategistStore()
const { profile, finance } = storeToRefs(store)

const T = {
  ru: {
    stepBadge: 'ШАГ 3 ИЗ 5',
    title: 'AI Рекомендации',
    sub: 'На основе ваших ответов мы подготовили ключевые наблюдения и советы',
    typing: 'AI анализирует данные...',
    back: 'Назад',
    next: 'Запустить полный анализ',
  },
  uz: {
    stepBadge: '3-QADAM (5 TADAN)',
    title: 'AI Tavsiyalar',
    sub: 'Javoblaringizga asoslanib asosiy kuzatuvlar va maslahatlarni tayyorladik',
    typing: 'AI maʻlumotlarni tahlil qilmoqda...',
    back: 'Orqaga',
    next: 'Toʻliq tahlilni boshlash',
  },
}

// Fergana-region context (from dashboard_fergan_city.html, 2025 data).
// Key fact for a kindergarten in Fergana city: 98,319 births in 2025 across
// the region + 56.7% urban population → demographically strong demand for
// private preschool capacity in urban maҳallas.
const ITEMS_BY_SECTOR = {
  kindergarten: {
    ru: [
      { type: 'strength', title: 'Демографическая база', text: 'В Ферганской области в 2025 году родилось 98 319 детей (50 683 мальчиков, 47 636 девочек). При населении 4,22 млн и урбанизации 56,7% — стабильный поток детей дошкольного возраста именно в городских маҳаллях, где находится ERKIN PARVOZ.' },
      { type: 'strength', title: 'Кредитная история', text: 'Действующих кредитов нет (Форма 1, стр. «Долгосрочные обязательства» — 0). Нулевая кредитная нагрузка при ROE 15,5% делает заявку привлекательной: банк видит способность обслуживать новый долг.' },
      { type: 'market', title: 'Платёжеспособный спрос', text: 'Фарғона шаҳар — крупнейший экономический центр области: промышленная продукция 8 587 млрд сум (2024), выше остальных районов. Средний доход семей позволяет оплачивать частный детсад (300–600 тыс. сум/мес за группу).' },
      { type: 'market', title: 'Регуляторный попутный ветер', text: 'Государственная программа охвата детей дошкольным образованием активно развивается с 2019: субсидии на организацию частных ДОУ, налоговые льготы по ИФУТ 85100. Ваш ООО-статус уже соответствует требованиям для участия.' },
      { type: 'warning', title: 'Ограниченная ликвидность', text: 'Коэффициент текущей ликвидности по Форме 1 = 1,19 (норма 1,5+). Это означает, что на каждый сум краткосрочных обязательств приходится 1,19 сума оборотных активов — небольшой запас. Кредит увеличит долг → ликвидность может упасть до 1,05.' },
      { type: 'warning', title: 'Сезонность набора', text: 'Набор в детский сад привязан к сентябрю: июнь–август — провал по cash-flow (40–50% отток семей на лето). Закладывайте резерв 2–3 месячных расхода или согласуйте с банком грейс-период на июль–август.' },
      { type: 'recommendation', title: 'Расширение на 2 группы (2–3 года)', text: 'Спрос на ясельные группы выше, чем на 3–6 лет: у маҳаллы нет государственного яслы, а у родителей декрет заканчивается в 2 года. Средняя наполняемость — 18–22 ребёнка на группу → +36–44 места = +1,2–1,5 млрд сум выручки в год.' },
      { type: 'recommendation', title: 'Подходящий кредитный продукт NBU', text: '«Развивайся» (до 3,5 млрд сум, 23% годовых, срок до 48 мес., залог — недвижимость). Под расширение мощностей с залогом здания — оптимальный вариант. Альтернатива: «Кредит оборотный» под закупку мебели/оборудования новых групп.' },
    ],
    uz: [
      { type: 'strength', title: 'Demografik baza', text: 'Fargʻona viloyatida 2025 yilda 98 319 bola tugʻilgan (50 683 oʻgʻil, 47 636 qiz). Aholisi 4,22 mln, shahar ulushi 56,7% — aynan ERKIN PARVOZ joylashgan shahar mahallalarida maktabgacha yoshdagi bolalar oqimi barqaror.' },
      { type: 'strength', title: 'Kredit tarixi', text: 'Amaldagi kreditlar yoʻq (Forma 1 uzoq muddatli majburiyatlar = 0). ROE 15,5% bilan nol kredit yuki — bank yangi qarzni xizmat qilish qobiliyatini koʻradi.' },
      { type: 'market', title: 'Toʻlovga qodir talab', text: 'Fargʻona shahri — viloyatning eng yirik iqtisodiy markazi: sanoat mahsuloti 8 587 mlrd soʻm (2024). Oilalarning oʻrtacha daromadi xususiy bolalar bogʻchasiga (300–600 ming soʻm/oy) haq toʻlashga imkon beradi.' },
      { type: 'market', title: 'Regulyativ qoʻllab-quvvatlash', text: '2019 yildan maktabgacha taʻlim davlat dasturi faol rivojlanmoqda: xususiy bogʻchalar uchun subsidiyalar, IFUT 85100 boʻyicha soliq imtiyozlari. MChJ sifatida allaqachon talablarga mos kelasiz.' },
      { type: 'warning', title: 'Likvidlik cheklangan', text: 'Forma 1 boʻyicha joriy likvidlik = 1,19 (norma 1,5+). Har bir soʻm qisqa muddatli majburiyatga 1,19 soʻm aylanma aktiv — zaxira kam. Kredit qarzni oshiradi → likvidlik 1,05 gacha tushishi mumkin.' },
      { type: 'warning', title: 'Mavsumiylik', text: 'Bogʻchaga qabul sentyabrga bogʻliq: iyun–avgust — cash-flow boʻshligi (40–50% oilalar yozga chiqadi). 2–3 oylik zaxara yoki bank bilan iyul–avgust greys-muddatini kelishib oling.' },
      { type: 'recommendation', title: '2 ta yangi guruh (2–3 yosh)', text: 'Yasli guruhlariga talab 3–6 yoshdan yuqori: mahallada davlat yasli yoʻq, ota-onalar dekreti 2 yoshda tugaydi. Guruhdagi oʻrtacha son — 18–22 bola → +36–44 oʻrin = +1,2–1,5 mlrd soʻm yillik tushum.' },
      { type: 'recommendation', title: 'Mos NBU kredit mahsuloti', text: '«Razvivaysya» (3,5 mlrd soʻmgacha, 23% yillik, 48 oygacha, garov — koʻchmas mulk). Bino garovida kengaytirish uchun optimal. Muqobil: «Kredit oborotniy» — yangi guruhlar uchun mebel/jihozlar xarid qilish.' },
    ],
  },
  services: {
    ru: [
      { type: 'strength', title: 'Стабильность бизнеса', text: 'Юридическое лицо с 3–5 годами опыта — банк оценит стабильность истории.' },
      { type: 'market', title: 'Спрос в Ферганской области', text: 'Население 4,22 млн, 56,7% городское — потенциальная аудитория для образовательных и сервисных услуг велика.' },
      { type: 'recommendation', title: 'Кредит NBU', text: '«Развивайся» или «Бизнес прогресс» — оптимально для расширения сервисного бизнеса.' },
    ],
    uz: [
      { type: 'strength', title: 'Biznes barqarorligi', text: 'MChJ 3–5 yillik tajriba bilan — bank tarixni qadrlaydi.' },
      { type: 'market', title: 'Fargʻona viloyatida talab', text: 'Aholisi 4,22 mln, 56,7% shahar — taʻlim va xizmat koʻrsatish uchun potentsial katta.' },
      { type: 'recommendation', title: 'NBU krediti', text: '«Razvivaysya» yoki «Biznes progress» — xizmat biznesini kengaytirish uchun optimal.' },
    ],
  },
  general: {
    ru: [
      { type: 'strength', title: 'Структурированный профиль', text: 'Ваши ответы дают банку полную картину — это ускоряет рассмотрение заявки.' },
      { type: 'market', title: 'Региональный контекст', text: 'Ферганская область: 4,22 млн жителей, промышленность 45,9 трлн сум (+104,3% в 2024), инвестиции 19,96 трлн сум (2023). Активный рынок для бизнеса.' },
      { type: 'recommendation', title: 'Следующий шаг', text: 'Приложите финансовые отчёты (Форма 1 и 2) для расчёта точных коэффициентов рентабельности и ликвидности.' },
    ],
    uz: [
      { type: 'strength', title: 'Tuzilgan profil', text: 'Javoblaringiz bankka toʻliq tasvir beradi — bu arizani tez koʻrib chiqishga yordam beradi.' },
      { type: 'market', title: 'Mintaqaviy kontekst', text: 'Fargʻona viloyati: 4,22 mln aholi, sanoat 45,9 trln soʻm (+104,3% 2024), investitsiya 19,96 trln soʻm (2023). Biznes uchun faol bozor.' },
      { type: 'recommendation', title: 'Keyingi qadam', text: 'Aniq rentabellik va likvidlik koeffitsientlari uchun moliyaviy hisobotlarni (Forma 1 va 2) ilova qiling.' },
    ],
  },
}

const TYPE_CONFIG = {
  ru: {
    strength: { label: 'СИЛЬНАЯ СТОРОНА', borderClass: 'border-l-emerald-500', bgClass: 'bg-emerald-50/80', iconBgClass: 'bg-emerald-100', iconClass: 'text-emerald-600', labelClass: 'text-emerald-700' },
    market: { label: 'РЫНОК', borderClass: 'border-l-blue-500', bgClass: 'bg-blue-50/80', iconBgClass: 'bg-blue-100', iconClass: 'text-blue-600', labelClass: 'text-blue-700' },
    warning: { label: 'ОБРАТИТЕ ВНИМАНИЕ', borderClass: 'border-l-amber-500', bgClass: 'bg-amber-50/80', iconBgClass: 'bg-amber-100', iconClass: 'text-amber-600', labelClass: 'text-amber-700' },
    recommendation: { label: 'РЕКОМЕНДАЦИЯ', borderClass: 'border-l-navy-900', bgClass: 'bg-navy-900/[0.05]', iconBgClass: 'bg-navy-900/10', iconClass: 'text-navy-900', labelClass: 'text-navy-900' },
  },
  uz: {
    strength: { label: 'KUChLI TOMON', borderClass: 'border-l-emerald-500', bgClass: 'bg-emerald-50/80', iconBgClass: 'bg-emerald-100', iconClass: 'text-emerald-600', labelClass: 'text-emerald-700' },
    market: { label: 'BOZOR', borderClass: 'border-l-blue-500', bgClass: 'bg-blue-50/80', iconBgClass: 'bg-blue-100', iconClass: 'text-blue-600', labelClass: 'text-blue-700' },
    warning: { label: 'EʻTIBOR BERING', borderClass: 'border-l-amber-500', bgClass: 'bg-amber-50/80', iconBgClass: 'bg-amber-100', iconClass: 'text-amber-600', labelClass: 'text-amber-700' },
    recommendation: { label: 'TAVSIYa', borderClass: 'border-l-navy-900', bgClass: 'bg-navy-900/[0.05]', iconBgClass: 'bg-navy-900/10', iconClass: 'text-navy-900', labelClass: 'text-navy-900' },
  },
}

const TYPE_ICONS = {
  strength: 'check-circle',
  market: 'bar-chart-3',
  warning: 'alert-triangle',
  recommendation: 'lightbulb',
}

const t = computed(() => T[lang.value])

const sectorBucket = computed(() => guessSectorBucket(finance.value.businessDirection))
const items = computed(() => {
  const bucket = sectorBucket.value
  const pool = ITEMS_BY_SECTOR[bucket] || ITEMS_BY_SECTOR.general
  return pool[lang.value] || pool.ru
})

const typeConfig = computed(() => TYPE_CONFIG[lang.value])

const visibleCount = ref(0)
let timer = null

const scheduleNext = () => {
  if (visibleCount.value >= items.value.length) return
  const delay = visibleCount.value === 0 ? 400 : 350
  timer = setTimeout(() => {
    visibleCount.value += 1
    scheduleNext()
  }, delay)
}

onMounted(scheduleNext)
onBeforeUnmount(() => timer && clearTimeout(timer))

const allVisible = computed(() => visibleCount.value >= items.value.length)
</script>

<template>
  <div class="bg-white border border-rs-border rounded-[12px] shadow-rs-card py-8 md:py-10 px-6 md:px-12 animate-rs-fade-in-up">
    <div>
      <span class="inline-flex items-center text-[12px] font-semibold text-gold-500 bg-gold-500/[0.08] rounded-[6px] py-1 px-3">{{ t.stepBadge }}</span>
      <h1 class="text-[26px] md:text-[30px] font-bold text-carbon mt-4">{{ t.title }}</h1>
      <p class="text-[15px] md:text-[16px] text-[#6b7280] leading-[1.6] mt-2">{{ t.sub }}</p>
    </div>

    <div class="mt-8 space-y-5">
      <div
        v-for="(item, i) in items" :key="item.title"
        :class="[
          'border-l-[4px] rounded-[12px] p-6 transition-all duration-500',
          typeConfig[item.type].borderClass,
          typeConfig[item.type].bgClass,
          i < visibleCount ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-3',
        ]"
      >
        <div class="flex items-start gap-4">
          <div :class="['w-10 h-10 rounded-[10px] flex items-center justify-center shrink-0', typeConfig[item.type].iconBgClass]">
            <RsIcon :name="TYPE_ICONS[item.type]" :size="20" :stroke-width="2" :class="typeConfig[item.type].iconClass" />
          </div>
          <div class="min-w-0">
            <span :class="['text-[11px] font-extrabold uppercase tracking-[1px]', typeConfig[item.type].labelClass]">
              {{ typeConfig[item.type].label }}
            </span>
            <h3 class="text-[17px] font-bold text-carbon mt-1.5 leading-snug">{{ item.title }}</h3>
            <p class="text-[14.5px] text-[#505a6b] leading-[1.7] mt-1.5">{{ item.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!allVisible" class="flex items-center gap-2 mt-4 ml-1">
      <div class="flex gap-1">
        <span class="w-[6px] h-[6px] rounded-full bg-gold-500 animate-bounce" style="animation-delay: 0ms" />
        <span class="w-[6px] h-[6px] rounded-full bg-gold-500 animate-bounce" style="animation-delay: 150ms" />
        <span class="w-[6px] h-[6px] rounded-full bg-gold-500 animate-bounce" style="animation-delay: 300ms" />
      </div>
      <span class="text-[13px] text-steel-500">{{ t.typing }}</span>
    </div>

    <div
      :class="[
        'mt-10 flex items-center justify-between transition-opacity duration-500',
        allVisible ? 'opacity-100' : 'opacity-0 pointer-events-none',
      ]"
    >
      <button type="button" @click="emit('back')"
              class="inline-flex items-center text-[14px] font-medium text-steel-500 hover:text-navy-900 transition-colors duration-200">
        <RsIcon name="arrow-left" :size="16" :stroke-width="2" class="mr-1" />
        {{ t.back }}
      </button>
      <button type="button" @click="emit('next')"
              class="inline-flex items-center text-[15px] font-semibold text-white bg-navy-900 hover:bg-navy-700 rounded-btn py-[14px] px-6 md:px-10 transition-colors duration-200">
        {{ t.next }}
        <RsIcon name="arrow-right" :size="18" :stroke-width="2.25" class="ml-2" />
      </button>
    </div>
  </div>
</template>
