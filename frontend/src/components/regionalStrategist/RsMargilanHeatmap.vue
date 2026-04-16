<script setup>
import { computed, ref } from 'vue'
import { useRsLang } from '@/composables/useRsLang'
import { rsFormatNumber } from './rs-utils'
import {
  MARGILAN_PATHS,
  MARGILAN_CENTROIDS,
  MARGILAN_OUTLINE,
  MARGILAN_VIEWBOX,
  MARGILAN_MAHALLAS,
} from '@/data/regionalStrategist/margilan-paths'

const { lang } = useRsLang()

const SUBSECTORS = {
  ru: [
    { name: 'IT и программирование', share: 32, color: '#2957A2' },
    { name: 'Иностранные языки', share: 25, color: '#059669' },
    { name: 'Подготовка к ОТМ', share: 18, color: '#D7B56D' },
    { name: 'Бухгалтерия / бизнес', share: 15, color: '#7C3AED' },
    { name: 'Дизайн и ремёсла', share: 10, color: '#EC4899' },
  ],
  uz: [
    { name: 'IT va dasturlash', share: 32, color: '#2957A2' },
    { name: 'Xorijiy tillar', share: 25, color: '#059669' },
    { name: 'OTMga tayyorgarlik', share: 18, color: '#D7B56D' },
    { name: 'Buxgalteriya / biznes', share: 15, color: '#7C3AED' },
    { name: 'Dizayn va hunarmandchilik', share: 10, color: '#EC4899' },
  ],
}

const HEATMAP_T = {
  ru: {
    title: 'Тепловая карта возможностей — Маргилан',
    sub: 'Потенциал каждой махалли для образовательных курсов',
    source: 'Источник: OSM + NBU Data Office',
    popLabel: 'Население города',
    avgLabel: 'Ср. балл',
    centersLabel: 'Учебных центров',
    bestLabel: '★ Лучшая махалля',
    bestBadge: '★ ЛУЧШИЙ ВАРИАНТ',
    subsectorsLabel: 'Направления курсов',
    rankingTitle: 'Рейтинг махаллей',
    popCol: 'Население',
    compCol: 'Конкуренция',
    scoreCol: 'Балл',
    entLabel: 'Предприятий',
    mahallaWord: 'махаллей',
    legend: [
      { color: '#059669', label: 'Отлично', range: '85–100' },
      { color: '#2957A2', label: 'Хорошо', range: '75–84' },
      { color: '#D7B56D', label: 'Умеренно', range: '60–74' },
      { color: '#DC2626', label: 'Слабо', range: '0–59' },
    ],
  },
  uz: {
    title: 'Imkoniyatlar issiqlik xartasi — Marg'ilon',
    sub: 'Har bir mahallaning ta'lim kurslari uchun potentsiali',
    source: 'Manba: OSM + NBU Data Office',
    popLabel: 'Shahar aholisi',
    avgLabel: 'O'rt. ball',
    centersLabel: 'O'quv markazlari',
    bestLabel: '★ Eng yaxshi mahalla',
    bestBadge: '★ ENG YaXShI VARIANT',
    subsectorsLabel: 'Kurs yo'nalishlari',
    rankingTitle: 'Mahallalar reytingi',
    popCol: 'Aholi',
    compCol: 'Raqobat',
    scoreCol: 'Ball',
    entLabel: 'Korxonalar',
    mahallaWord: 'mahalla',
    legend: [
      { color: '#059669', label: 'A'lo', range: '85–100' },
      { color: '#2957A2', label: 'Yaxshi', range: '75–84' },
      { color: '#D7B56D', label: 'O'rtacha', range: '60–74' },
      { color: '#DC2626', label: 'Past', range: '0–59' },
    ],
  },
}

const heatColor = (s) => (s >= 85 ? '#059669' : s >= 75 ? '#2957A2' : s >= 60 ? '#D7B56D' : '#DC2626')
const competitionColor = (c) => (c === 'низкая' ? '#059669' : c === 'средняя' ? '#D97706' : '#DC2626')
const labelFill = (s) => (s >= 75 || s < 60 ? '#fff' : '#193F72')

const ht = computed(() => HEATMAP_T[lang.value])
const subsectors = computed(() => SUBSECTORS[lang.value])

const sorted = computed(() => [...MARGILAN_MAHALLAS].sort((a, b) => b.score - a.score))
const best = computed(() => sorted.value[0])
const avgScore = computed(() =>
  Math.round(MARGILAN_MAHALLAS.reduce((s, d) => s + d.score, 0) / MARGILAN_MAHALLAS.length),
)
const maxScore = computed(() => best.value.score)

const hoveredId = ref(null)
const tip = ref({ x: 0, y: 0 })
const containerRef = ref(null)

const hovered = computed(() =>
  hoveredId.value ? MARGILAN_MAHALLAS.find((d) => d.id === hoveredId.value) || null : null,
)

const handleMouseMove = (e) => {
  if (!containerRef.value) return
  const r = containerRef.value.getBoundingClientRect()
  tip.value = { x: e.clientX - r.left, y: e.clientY - r.top }
}

const tooltipStyle = computed(() => {
  const offsetW = containerRef.value?.offsetWidth ?? 400
  return {
    left: `${Math.min(tip.value.x + 16, offsetW - 270)}px`,
    top: tip.value.y < 200 ? `${tip.value.y + 24}px` : `${tip.value.y - 8}px`,
    transform: tip.value.y < 200 ? 'none' : 'translateY(-100%)',
  }
})
</script>

<template>
  <div class="space-y-8">
    <!-- Header + Legend -->
    <div class="flex items-start justify-between gap-6 flex-wrap">
      <div>
        <h2 class="text-[20px] md:text-[22px] font-bold text-carbon">{{ ht.title }}</h2>
        <p class="text-[14px] md:text-[15px] text-[#898989] mt-1">
          {{ ht.sub }} · {{ MARGILAN_MAHALLAS.length }} {{ ht.mahallaWord }} · {{ ht.source }}
        </p>
      </div>
      <div class="flex items-center gap-5 shrink-0 pt-1 flex-wrap">
        <div v-for="l in ht.legend" :key="l.label" class="flex items-center gap-[6px]">
          <span class="w-[10px] h-[10px] rounded-[3px] shrink-0" :style="{ background: l.color }" />
          <span class="text-[12px] text-[#898989] whitespace-nowrap">{{ l.range }}</span>
        </div>
      </div>
    </div>

    <!-- Map + Stats -->
    <div class="flex gap-6 flex-wrap lg:flex-nowrap">
      <!-- Map -->
      <div
        ref="containerRef"
        class="relative flex-1 min-w-0 bg-[#F8F9FC] rounded-[10px] border border-rs-border/60 p-4"
        @mousemove="handleMouseMove"
      >
        <svg :viewBox="MARGILAN_VIEWBOX" class="w-full h-auto" style="min-height: 340px">
          <defs>
            <filter id="mhover-shadow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.2" />
            </filter>
          </defs>

          <path :d="MARGILAN_OUTLINE" fill="#e8eef4" stroke="#c0cdd8" stroke-width="1" opacity="0.3" />

          <g
            v-for="d in MARGILAN_MAHALLAS" :key="d.id"
            class="cursor-pointer"
            :style="{ filter: d.id === hoveredId ? 'url(#mhover-shadow)' : 'none' }"
            @mouseenter="hoveredId = d.id" @mouseleave="hoveredId = null"
          >
            <path
              :d="MARGILAN_PATHS[d.id]"
              :fill="heatColor(d.score)"
              :fill-opacity="d.id === hoveredId ? 0.95 : 0.75"
              :stroke="d.id === hoveredId ? '#193F72' : '#fff'"
              :stroke-width="d.id === hoveredId ? 2.5 : 1.5"
              style="transition: fill-opacity 150ms ease, stroke 150ms ease, stroke-width 150ms ease"
            />
            <path
              v-if="d.id === best.id && d.id !== hoveredId"
              :d="MARGILAN_PATHS[d.id]" fill="none" stroke="#D7B56D" stroke-width="2.5" stroke-dasharray="8 4"
            >
              <animate attributeName="stroke-dashoffset" values="0;24" dur="1.5s" repeatCount="indefinite" />
            </path>
            <text
              :x="MARGILAN_CENTROIDS[d.id][0]" :y="MARGILAN_CENTROIDS[d.id][1] - 5"
              text-anchor="middle" :fill="labelFill(d.score)"
              font-size="9" font-family="'Inter', sans-serif" font-weight="600"
              style="pointer-events: none"
            >{{ d.name }}</text>
            <text
              :x="MARGILAN_CENTROIDS[d.id][0]" :y="MARGILAN_CENTROIDS[d.id][1] + 11"
              text-anchor="middle" :fill="labelFill(d.score)"
              font-size="13" font-family="'JetBrains Mono', monospace" font-weight="700"
              style="pointer-events: none"
            >{{ d.score }}</text>
          </g>
        </svg>

        <!-- Tooltip -->
        <div v-if="hovered" class="absolute z-10 pointer-events-none" :style="tooltipStyle">
          <div
            class="bg-white rounded-[10px] py-4 px-5 border border-rs-border/50"
            style="box-shadow: 0 12px 32px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.06); min-width: 240px; max-width: 290px;"
          >
            <div v-if="hovered.id === best.id" class="text-[11px] font-bold text-gold-500 mb-1 tracking-wide">
              {{ ht.bestBadge }}
            </div>
            <div class="text-[15px] font-bold text-carbon">{{ hovered.name }}</div>
            <div class="font-mono text-[22px] font-bold mt-1" :style="{ color: heatColor(hovered.score) }">
              {{ hovered.score }}/100
            </div>
            <div class="space-y-[5px] mt-3">
              <div class="flex items-center justify-between gap-4">
                <span class="text-[12px] text-steel-500">{{ ht.popCol }}</span>
                <span class="font-mono text-[12px] font-medium text-carbon">{{ rsFormatNumber(hovered.population) }}</span>
              </div>
              <div class="flex items-center justify-between gap-4">
                <span class="text-[12px] text-steel-500">{{ ht.entLabel }}</span>
                <span class="font-mono text-[12px] font-medium text-carbon">~{{ hovered.businesses }}</span>
              </div>
              <div class="flex items-center justify-between gap-4">
                <span class="text-[12px] text-steel-500">{{ ht.compCol }}</span>
                <span class="text-[12px] font-semibold" :style="{ color: competitionColor(hovered.competition) }">
                  {{ hovered.competition }}
                </span>
              </div>
            </div>
            <div class="text-[12px] italic text-[#898989] mt-3 pt-3 border-t border-rs-border leading-[1.45]">
              {{ hovered.verdict }}
            </div>
          </div>
        </div>
      </div>

      <!-- Stats sidebar -->
      <div class="w-full lg:w-[180px] shrink-0 space-y-4">
        <div class="bg-[#F8F9FC] rounded-[10px] border border-rs-border/60 p-4 space-y-4">
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ ht.popLabel }}</div>
            <div class="font-mono text-[22px] font-bold text-navy-900 mt-[2px]">261,948</div>
            <div class="text-[10px] text-steel-500">stat.uz, 2024</div>
          </div>
          <div class="h-px bg-rs-border" />
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ ht.avgLabel }}</div>
            <div class="font-mono text-[22px] font-bold mt-[2px]" :style="{ color: heatColor(avgScore) }">{{ avgScore }}</div>
          </div>
          <div class="h-px bg-rs-border" />
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500">{{ ht.centersLabel }}</div>
            <div class="font-mono text-[14px] font-bold text-carbon mt-[2px]">31</div>
            <div class="text-[10px] text-steel-500">NBU Data Office</div>
          </div>
        </div>

        <div
          class="rounded-[10px] p-4"
          style="background: linear-gradient(135deg, rgba(5,150,105,0.06), rgba(5,150,105,0.02)); border: 1px solid rgba(5,150,105,0.2);"
        >
          <div class="text-[11px] font-bold uppercase tracking-[0.5px] text-green-600">{{ ht.bestLabel }}</div>
          <div class="text-[14px] font-bold text-carbon mt-1">{{ best.name }}</div>
          <div class="font-mono text-[18px] font-bold mt-[2px]" :style="{ color: heatColor(best.score) }">
            {{ best.score }}/100
          </div>
        </div>

        <div class="bg-[#F8F9FC] rounded-[10px] border border-rs-border/60 p-4">
          <div class="text-[11px] font-semibold uppercase tracking-[0.5px] text-steel-500 mb-3">
            {{ ht.subsectorsLabel }}
          </div>
          <div class="space-y-[6px]">
            <div v-for="s in subsectors" :key="s.name">
              <div class="flex items-center justify-between mb-[2px]">
                <span class="text-[11px] text-[#898989]">{{ s.name }}</span>
                <span class="font-mono text-[11px] font-semibold text-carbon">{{ s.share }}%</span>
              </div>
              <div class="h-[4px] bg-rs-border/60 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :style="{ width: `${s.share}%`, background: s.color }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ranking -->
    <div>
      <h3 class="text-[16px] font-bold text-carbon mb-4">{{ ht.rankingTitle }}</h3>
      <div class="space-y-[6px]">
        <div
          v-for="(d, i) in sorted" :key="d.id"
          class="flex items-center gap-3 group"
          @mouseenter="hoveredId = d.id" @mouseleave="hoveredId = null"
        >
          <span class="font-mono text-[12px] font-medium text-steel-500 w-[18px] text-right shrink-0">{{ i + 1 }}</span>
          <span
            class="text-[13px] text-carbon w-[110px] shrink-0 truncate"
            :style="{ fontWeight: i < 3 ? 600 : 400 }"
          >{{ d.name }}</span>
          <div class="flex-1 h-[20px] bg-gray-100 rounded-[4px] overflow-hidden">
            <div
              class="h-full rounded-[4px] flex items-center justify-end pr-2 transition-all duration-300 group-hover:opacity-90"
              :style="{ width: `${Math.max((d.score / maxScore) * 100, 8)}%`, background: heatColor(d.score) }"
            >
              <span class="font-mono text-[11px] font-bold text-white">{{ d.score }}</span>
            </div>
          </div>
          <span class="font-mono text-[11px] text-steel-500 w-[70px] shrink-0 text-right">
            {{ rsFormatNumber(d.population) }}
          </span>
          <span class="text-[11px] font-semibold w-[65px] shrink-0 text-right" :style="{ color: competitionColor(d.competition) }">
            {{ d.competition }}
          </span>
        </div>
      </div>
      <div class="flex items-center justify-end gap-8 mt-2 pt-2 border-t border-rs-border/50">
        <span class="text-[10px] text-steel-500">{{ ht.scoreCol }}</span>
        <span class="text-[10px] text-steel-500 w-[70px] text-right">{{ ht.popCol }}</span>
        <span class="text-[10px] text-steel-500 w-[65px] text-right">{{ ht.compCol }}</span>
      </div>
    </div>
  </div>
</template>
