<script setup>
import { computed } from 'vue'
import RsIcon from './RsIcon.vue'

const props = defineProps({
  analysis: { type: Object, required: true },
  lang: { type: String, default: 'ru' },
})

const L = {
  ru: {
    title: 'Детальный AI-разбор заявки',
    subtitle: 'Интегрированный вывод: профиль, финансы из Excel и региональный контекст',
    badge: 'Итоговый разбор',
    verdict: { good: 'Хороший потенциал', fair: 'Средний потенциал', weak: 'Требует доработки' },
    verdictHint: {
      good: 'Заявка выглядит сильно — можно подавать на стандартные продукты НБУ без предварительной доработки.',
      fair: 'Есть доработки — закройте слабые места ниже, прежде чем подавать заявку.',
      weak: 'Перед подачей закройте ключевые пробелы — иначе заявка будет рассмотрена с повышенным риском.',
    },
    sections: {
      summary: 'Резюме по бизнесу', strengths: 'Сильные стороны', weaknesses: 'Слабые места',
      peer: 'Сравнение с медианой по отрасли', cityFit: 'Соответствие локации',
      product: 'Рекомендуемый продукт NBU', nextSteps: 'План действий на 30–90 дней', risks: 'Риски и их митигация',
    },
    peerCols: { metric: 'Показатель', user: 'Ваш бизнес', median: 'Медиана отрасли', comment: 'Интерпретация' },
    methodology: 'Методология: взвешенная оценка 5 факторов (профиль 25%, финансы 30%, локация 15%, идея 20%, готовность 10%). Данные: ваши ответы + загруженная финансовая отчётность + stat.uz по Фарғона вилояти.',
  },
  uz: {
    title: 'Ariza bo'yicha batafsil AI-tahlil',
    subtitle: 'Profil, Excel moliya va mintaqa kontekstidan birgalikdagi xulosa',
    badge: 'Yakuniy tahlil',
    verdict: { good: 'Yaxshi potentsial', fair: 'O'rta potentsial', weak: 'Takomillashtirish kerak' },
    verdictHint: {
      good: 'Ariza kuchli — NBU standart mahsulotlariga tayyor.',
      fair: 'Takomillashtirish kerak — quyidagi zaif joylarni yoping.',
      weak: 'Taqdim etishdan oldin asosiy bo'shliqlarni yoping — aks holda yuqori xatar bilan ko'riladi.',
    },
    sections: {
      summary: 'Biznes bo'yicha xulosa', strengths: 'Kuchli tomonlar', weaknesses: 'Zaif joylar',
      peer: 'Soha medianasi bilan qiyoslash', cityFit: 'Lokatsiyaga moslik',
      product: 'Tavsiya etilgan NBU mahsuloti', nextSteps: '30–90 kunlik harakat rejasi', risks: 'Xatarlar va ularni yumshatish',
    },
    peerCols: { metric: 'Ko'rsatkich', user: 'Sizning biznes', median: 'Soha medianasi', comment: 'Izoh' },
    methodology: 'Metodologiya: 5 omil bo'yicha vaznli baho (profil 25%, moliya 30%, lokatsiya 15%, g'oya 20%, tayyorlik 10%). Manba: javoblar + yuklangan hisobot + stat.uz.',
  },
}
const t = computed(() => L[props.lang] ?? L.ru)
const out = computed(() => props.analysis?.output ?? {})

const verdictCls = computed(() => {
  const v = out.value?.verdict
  if (v === 'good') return 'text-emerald-700 bg-emerald-50 border-emerald-200'
  if (v === 'fair') return 'text-amber-700 bg-amber-50 border-amber-200'
  return 'text-red-700 bg-red-50 border-red-200'
})

const verdictHeroStyle = computed(() => {
  const v = out.value?.verdict
  if (v === 'good') return { bg: 'from-emerald-50 to-white', ring: 'border-emerald-200', dot: 'bg-emerald-500', title: 'text-emerald-800' }
  if (v === 'fair') return { bg: 'from-amber-50 to-white',  ring: 'border-amber-200',  dot: 'bg-amber-500',  title: 'text-amber-800' }
  return { bg: 'from-red-50 to-white', ring: 'border-red-200', dot: 'bg-red-500', title: 'text-red-800' }
})

const fmtPct = (n) => (n == null ? '—' : `${(n * 100).toFixed(1)}%`)
const fmtNum = (n) => (n == null ? '—' : (Math.abs(n) < 10 ? n.toFixed(2) : Math.round(n).toLocaleString('ru-RU')))
</script>

<template>
  <section class="bg-white border border-rs-border rounded-[12px] overflow-hidden shadow-rs-card">
    <div class="px-8 py-6"
         style="background: linear-gradient(90deg, rgba(41,87,162,0.05), rgba(215,181,109,0.05)); border-bottom: 1px solid rgba(41,87,162,0.1);">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-4 min-w-0">
          <span class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-navy-900 shrink-0">
            <RsIcon name="sparkles" :size="16" class="text-white" />
          </span>
          <div class="min-w-0">
            <h2 class="font-sans text-[20px] font-bold text-carbon">{{ t.title }}</h2>
            <p class="font-sans text-[13px] text-gray-600 mt-1">{{ t.subtitle }}</p>
          </div>
        </div>
        <div class="shrink-0 flex items-center gap-2">
          <span class="inline-flex text-[11px] font-bold uppercase tracking-[0.5px] text-gold-500 bg-gold-500/10 border border-gold-500/20 rounded-[6px] py-1 px-2">
            {{ t.badge }}
          </span>
          <span v-if="out.verdict"
                :class="['inline-flex text-[11px] font-bold uppercase tracking-[0.5px] rounded-[6px] py-1 px-2 border', verdictCls]">
            {{ t.verdict[out.verdict] || out.verdict }}
          </span>
        </div>
      </div>
    </div>

    <div class="px-8 py-7 space-y-7">
      <!-- Verdict hero — big, colour-keyed, with summary inline -->
      <div v-if="out.verdict || out.summary"
           :class="['rounded-[12px] border bg-gradient-to-b p-6', verdictHeroStyle.ring, verdictHeroStyle.bg]">
        <div v-if="out.verdict" class="flex items-center gap-3 mb-3">
          <span :class="['w-2.5 h-2.5 rounded-full', verdictHeroStyle.dot]" />
          <div :class="['font-sans text-[22px] font-bold leading-tight', verdictHeroStyle.title]">
            {{ t.verdict[out.verdict] || out.verdict }}
          </div>
        </div>
        <p v-if="out.verdict && t.verdictHint[out.verdict]"
           class="font-sans text-[13px] font-medium text-carbon/70 mb-3">
          {{ t.verdictHint[out.verdict] }}
        </p>
        <p v-if="out.summary" class="text-[15px] text-carbon leading-[1.65]">{{ out.summary }}</p>
      </div>

      <!-- Strengths + Weaknesses grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" v-if="out.strengths?.length || out.weaknesses?.length">
        <div v-if="out.strengths?.length" class="rounded-[10px] border border-emerald-200 bg-emerald-50 p-4">
          <div class="text-[12px] font-bold uppercase tracking-[0.5px] text-emerald-700 mb-2">{{ t.sections.strengths }}</div>
          <ul class="space-y-2">
            <li v-for="s in out.strengths" :key="s" class="flex items-start gap-2 text-[13px] text-carbon leading-[1.5]">
              <span class="w-[5px] h-[5px] rounded-full bg-emerald-500 mt-[7px] shrink-0" />{{ s }}
            </li>
          </ul>
        </div>
        <div v-if="out.weaknesses?.length" class="rounded-[10px] border border-red-200 bg-red-50 p-4">
          <div class="text-[12px] font-bold uppercase tracking-[0.5px] text-red-700 mb-2">{{ t.sections.weaknesses }}</div>
          <ul class="space-y-2">
            <li v-for="w in out.weaknesses" :key="w" class="flex items-start gap-2 text-[13px] text-carbon leading-[1.5]">
              <span class="w-[5px] h-[5px] rounded-full bg-red-400 mt-[7px] shrink-0" />{{ w }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Peer comparison table -->
      <div v-if="out.peerComparison?.length">
        <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 mb-2">{{ t.sections.peer }}</div>
        <div class="border border-rs-border rounded-[10px] overflow-hidden">
          <table class="w-full text-[13px]">
            <thead class="bg-navy-900/[0.03]">
              <tr>
                <th class="text-left py-3 px-4 font-semibold text-[11px] uppercase tracking-[0.5px] text-steel-500">{{ t.peerCols.metric }}</th>
                <th class="text-right py-3 px-4 font-semibold text-[11px] uppercase tracking-[0.5px] text-steel-500">{{ t.peerCols.user }}</th>
                <th class="text-right py-3 px-4 font-semibold text-[11px] uppercase tracking-[0.5px] text-steel-500">{{ t.peerCols.median }}</th>
                <th class="text-left py-3 px-4 font-semibold text-[11px] uppercase tracking-[0.5px] text-steel-500">{{ t.peerCols.comment }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-rs-border">
              <tr v-for="(r, i) in out.peerComparison" :key="i" class="hover:bg-navy-900/[0.02]">
                <td class="py-3 px-4 text-carbon font-medium">{{ r.metric }}</td>
                <td class="py-3 px-4 text-right font-mono font-semibold text-carbon">{{ typeof r.user === 'number' && r.user < 2 ? fmtPct(r.user) : fmtNum(r.user) }}</td>
                <td class="py-3 px-4 text-right font-mono text-steel-500">{{ typeof r.peerMedian === 'number' && r.peerMedian < 2 ? fmtPct(r.peerMedian) : fmtNum(r.peerMedian) }}</td>
                <td class="py-3 px-4 text-gray-600 text-[12px]">{{ r.comment }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- City fit -->
      <div v-if="out.cityFit">
        <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 mb-2">{{ t.sections.cityFit }}</div>
        <p class="text-[14px] text-carbon leading-[1.6]">{{ out.cityFit }}</p>
      </div>

      <!-- Recommended product -->
      <div v-if="out.recommendedProduct?.name"
           class="rounded-[10px] border border-rs-border py-4 px-5"
           style="border-top: 3px solid #D7B56D;">
        <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-gold-500 mb-1">{{ t.sections.product }}</div>
        <div class="font-sans text-[16px] font-bold text-carbon">{{ out.recommendedProduct.name }}</div>
        <p v-if="out.recommendedProduct.reason" class="text-[13px] text-gray-600 mt-1 leading-[1.5]">{{ out.recommendedProduct.reason }}</p>
      </div>

      <!-- Next steps — numbered cards in priority order -->
      <div v-if="out.nextSteps?.length">
        <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 mb-3">{{ t.sections.nextSteps }}</div>
        <ol class="space-y-2.5">
          <li v-for="(s, i) in out.nextSteps" :key="i"
              class="flex items-start gap-4 border border-rs-border rounded-[10px] py-3 px-4 hover:border-navy-900/30 transition-colors">
            <span :class="['shrink-0 w-8 h-8 rounded-full inline-flex items-center justify-center font-mono text-[13px] font-bold text-white',
                           i === 0 ? 'bg-gold-500' : i < out.nextSteps.length - 1 ? 'bg-navy-900' : 'bg-emerald-500']">
              {{ i + 1 }}
            </span>
            <span class="text-[14px] text-carbon leading-[1.55] pt-[6px]">{{ s }}</span>
          </li>
        </ol>
      </div>

      <!-- Risks -->
      <div v-if="out.risks?.length" class="rounded-[10px] border border-amber-200 bg-amber-50 p-4">
        <div class="text-[12px] font-bold uppercase tracking-[0.5px] text-amber-700 mb-2">{{ t.sections.risks }}</div>
        <ul class="space-y-2">
          <li v-for="r in out.risks" :key="r" class="flex items-start gap-2 text-[13px] text-carbon leading-[1.5]">
            <RsIcon name="alert-triangle" :size="12" class="text-amber-600 mt-[4px] shrink-0" />{{ r }}
          </li>
        </ul>
      </div>

      <div class="pt-3 border-t border-rs-border text-[11px] text-steel-500 leading-[1.55] italic">
        {{ t.methodology }}
      </div>
    </div>
  </section>
</template>
