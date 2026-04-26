<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import UzbekistanMap from '@/components/UzbekistanMap.vue'
import AppIcon from '@/components/AppIcon.vue'
import RegionDropdown from '@/components/RegionDropdown.vue'
import {
  regions,
  regionKeys,
  national,
  regionSpecializations,
  regionSources,
  nationalSource,
} from '@/data/regions'
import { regionColors } from '@/data/regionColors'

const { t, tm } = useI18n()
const router = useRouter()

const selected = ref(null) // null = whole country
const sidebarMode = ref('population') // 'population' | 'specialization'

const selectedSpec = computed(() => {
  if (!selected.value) return null
  const spec = regionSpecializations[selected.value]
  if (!spec) return null
  const bullets = tm(`specializations.bullets.${selected.value}`)
  return {
    icon: spec.icon,
    tag: t(`specializations.tags.${selected.value}`),
    bullets: Array.isArray(bullets) ? bullets : [],
  }
})

const current = computed(() => (selected.value ? regions[selected.value] : national))

const NO_DATA = computed(() => t('home.cards.noData'))

// stat.uz "raqamlarda" infographic — 10 metrics. National total uses GDP
// label, regions use GRP label. Tashkent city replaces the agriculture tile
// with foreign trade turnover (handled in figureTiles below).
const FIGURE_METRICS = [
  { key: 'grp', icon: 'show_chart' },
  { key: 'industry', icon: 'factory' },
  { key: 'agriculture', icon: 'agriculture' },
  { key: 'investment', icon: 'savings' },
  { key: 'construction', icon: 'construction' },
  { key: 'freight', icon: 'local_shipping' },
  { key: 'passenger', icon: 'directions_bus' },
  { key: 'retail', icon: 'storefront' },
  { key: 'services', icon: 'handyman' },
  { key: 'population', icon: 'groups' },
]

function formatPercent(v) {
  if (v == null) return null
  return `${v.toFixed(1)}%`
}

function formatPopCount(n) {
  if (n == null) return null
  return n.toLocaleString('ru-RU')
}

function formatPopDate(iso) {
  if (!iso) return null
  const [y, m, d] = iso.split('-')
  return `${parseInt(d, 10)}.${m}.${y}`
}

// Tone coding for percent metrics. Maps to existing M3 tokens — tertiary for
// growth, error for decline, on-surface for ~100% (no chip backgrounds, the
// tone lives on the value text and the deviation bar fill).
const TONE_CLASSES = {
  pos: { value: 'text-tertiary',           bar: 'bg-tertiary' },
  neu: { value: 'text-on-surface',         bar: 'bg-on-surface-variant' },
  neg: { value: 'text-error',              bar: 'bg-error' },
  na:  { value: 'text-on-surface-variant', bar: 'bg-on-surface-variant' },
}

function tileTone(v) {
  if (v == null) return 'na'
  if (v >= 102) return 'pos'
  if (v >= 99) return 'neu'
  return 'neg'
}

// Deviation bar — visualises distance from 100% on a ±20 п.п. scale, anchored
// at the centre tick. Magnitudes beyond ±20 clamp to the half-width; the
// numeric delta above the bar remains the source of truth.
const BAR_HALF_RANGE = 20

function buildBarStyle(value) {
  if (value == null) return null
  const delta = value - 100
  const widthPct = Math.min(Math.abs(delta) / BAR_HALF_RANGE, 1) * 50
  const w = `${widthPct.toFixed(2)}%`
  return delta >= 0
    ? { left: '50%', width: w }
    : { right: '50%', width: w }
}

function buildTrend(value) {
  const tone = tileTone(value)
  const delta = value != null ? +(value - 100).toFixed(1) : null
  const deltaLabel = delta != null
    ? `${delta >= 0 ? '+' : ''}${delta.toFixed(1)} п.п.`
    : null
  return {
    tone,
    toneClasses: TONE_CLASSES[tone],
    deltaLabel,
    barStyle: buildBarStyle(value),
  }
}

const figuresHeader = computed(() => {
  const r = current.value
  const period = r.raqamlarda?.period
  const subtitleKey =
    period === '2025' ? 'home.figures.subtitle2025'
    : period === '2026Q1' ? 'home.figures.subtitle2026Q1'
    : 'home.figures.subtitleNoPeriod'
  const title = selected.value
    ? t('home.figures.titleRegion', { name: t(`regions.${selected.value}`) })
    : t('home.figures.titleNational')
  return { title, subtitle: t(subtitleKey) }
})

const periodFootnote = computed(() => {
  const period = current.value.raqamlarda?.period
  if (period === '2025') return t('home.figures.vs2024')
  if (period === '2026Q1') return t('home.figures.vs2025Q1')
  return ''
})

// Source attribution shown at the bottom of the raqamlarda section.
// `note` distinguishes sites that were unreachable, sites that published
// only a partial bulletin, and the headline-only Andijon case.
const figuresSource = computed(() => {
  const src = selected.value ? regionSources[selected.value] : nationalSource
  if (!src) return { text: t('home.figures.source', { site: 'stat.uz' }), tone: 'neutral' }
  const params = { site: src.site }
  if (src.note === 'unreachable') return { text: t('home.figures.sourceUnreachable', params), tone: 'warning' }
  if (src.note === 'partial') return { text: t('home.figures.sourcePartial', params), tone: 'warning' }
  if (src.note === 'headlineOnly') return { text: t('home.figures.sourceHeadlineOnly', params), tone: 'warning' }
  return { text: t('home.figures.source', params), tone: 'neutral' }
})

// Empty / partial badge surfaced in the section header.
const figuresBadge = computed(() => {
  const rd = current.value.raqamlarda || {}
  // Treat agriculture as covered if the region instead reports tashqi_savdo
  // (Tashkent city — the city bulletin replaces the agriculture tile with
  // foreign trade turnover).
  const hasAgriOrFx = rd.agriculture != null || rd.tashqi_savdo != null
  const others = ['grp', 'industry', 'investment', 'construction', 'freight', 'passenger', 'retail', 'services']
  const present = (hasAgriOrFx ? 1 : 0) + others.filter((k) => rd[k] != null).length
  const total = 1 + others.length
  if (present === 0) return { kind: 'empty', label: t('home.figures.noDataBadge') }
  if (present < total) return { kind: 'partial', label: t('home.figures.partialBadge') }
  return null
})

const figureTiles = computed(() => {
  const rd = current.value.raqamlarda || {}
  const isNational = !selected.value
  return FIGURE_METRICS.map((m) => {
    if (m.key === 'population') {
      const value = formatPopCount(rd.populationCount)
      let footnote = ''
      if (value != null) {
        if (rd.populationCaption === 'currentCount') {
          footnote = t('home.figures.currentCount')
        } else {
          const dateStr = formatPopDate(rd.populationDate)
          if (dateStr) footnote = t('home.figures.asOfDate', { date: dateStr })
        }
      }
      return {
        key: m.key,
        icon: m.icon,
        label: t('home.figures.metrics.population'),
        value: value ?? NO_DATA.value,
        footnote,
        isPercent: false,
        hasData: value != null,
        direction: 'flat',
      }
    }
    // Tashkent city replaces the agriculture tile with foreign trade turnover.
    if (m.key === 'agriculture' && rd.agriculture == null && rd.tashqi_savdo != null) {
      const v = rd.tashqi_savdo
      const trend = buildTrend(v)
      return {
        key: 'tashqi_savdo',
        icon: 'currency_exchange',
        label: t('home.figures.metrics.tashqi_savdo'),
        value: formatPercent(v),
        footnote: periodFootnote.value,
        isPercent: true,
        hasData: true,
        direction: v > 100 ? 'up' : v < 100 ? 'down' : 'flat',
        ...trend,
      }
    }
    const labelKey = m.key === 'grp' && isNational
      ? 'home.figures.metrics.gdp'
      : `home.figures.metrics.${m.key}`
    const v = rd[m.key]
    const value = formatPercent(v)
    const trend = buildTrend(v)
    return {
      key: m.key,
      icon: m.icon,
      label: t(labelKey),
      value: value ?? NO_DATA.value,
      footnote: value ? periodFootnote.value : '',
      isPercent: true,
      hasData: value != null,
      direction: v == null ? 'flat' : v > 100 ? 'up' : v < 100 ? 'down' : 'flat',
      ...trend,
    }
  })
})

const ANALYTICS_REGIONS = new Set(['fergana', 'samarqand'])
const unavailableToast = ref(null)

function reset() {
  selected.value = null
}
function onRegionSelect(/* key */) {
  // All regions are selectable — no gating here.
}
function gotoAnalytics() {
  if (selected.value && !ANALYTICS_REGIONS.has(selected.value)) {
    unavailableToast.value = t('home.regionUnavailable')
    setTimeout(() => { unavailableToast.value = null }, 3000)
    return
  }
  router.push({ name: 'districts', query: { region: selected.value || '' } })
}

// Sorted region list (by population) for sidebar
const sortedRegions = computed(() =>
  regionKeys
    .map((k) => ({ key: k, ...regions[k] }))
    .sort((a, b) => b.populationRaw - a.populationRaw),
)
</script>

<template>
  <div>
  <section class="p-6 lg:p-8 space-y-8">
    <!-- Map (top, full width) -->
    <div class="space-y-4">
      <header class="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-on-surface">
            {{ selected ? t(`regions.${selected}`) : t('home.map.title') }}
          </h2>
          <p class="text-sm text-on-surface-variant mt-1">{{ t('home.map.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="selected"
            type="button"
            class="text-xs font-bold text-primary inline-flex items-center gap-1 hover:underline"
            @click="reset"
          >
            <AppIcon name="restart_alt" />
            {{ t('home.map.reset') }}
          </button>
          <button
            v-if="selected"
            type="button"
            class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-bold inline-flex items-center gap-2 hover:scale-105 active:scale-95 transition-transform"
            @click="gotoAnalytics"
          >
            <AppIcon name="analytics" />
            {{ t('regionInfo.viewAnalytics') }}
          </button>
          <div class="lg:hidden">
            <RegionDropdown v-model="selected" :regions="sortedRegions" :available-regions="AVAILABLE_REGIONS" @unavailable="onRegionSelect" />
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_300px] gap-6 items-start">
        <UzbekistanMap v-model="selected" @select="onRegionSelect" />

        <!-- Right column: summary (top) + region list (bottom) stacked -->
        <div class="hidden lg:flex flex-col gap-4 min-h-0">
          <!-- Compact summary panel -->
          <aside
            class="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm p-4 flex flex-col gap-3"
          >
            <header class="flex items-center justify-between gap-2">
              <span class="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant truncate">
                {{ selected ? t(`regions.${selected}`) : t('home.map.nationalTitle') }}
              </span>
              <span
                v-if="selected && selectedSpec"
                class="inline-flex items-center gap-1 text-primary"
              >
                <AppIcon :name="selectedSpec.icon" filled class="!text-[18px]" />
              </span>
            </header>

            <!-- Specialization tag + bullets (selected) / empty state -->
            <div v-if="selected && selectedSpec" class="flex gap-2.5 min-w-0">
              <span
                class="block w-[3px] rounded-full flex-shrink-0"
                :style="{ backgroundColor: regionColors[selected]?.selected }"
              ></span>
              <div class="flex flex-col gap-1 min-w-0">
                <p class="text-sm font-bold text-on-surface leading-snug">
                  {{ selectedSpec.tag }}
                </p>
                <p
                  v-if="selectedSpec.bullets.length"
                  class="text-[12px] text-on-surface-variant leading-snug"
                >
                  {{ selectedSpec.bullets.join(' · ') }}
                </p>
              </div>
            </div>
            <div v-else class="flex items-center gap-2 text-on-surface-variant">
              <AppIcon name="ads_click" class="!text-[16px] text-primary" />
              <p class="text-xs leading-snug">{{ t('home.map.emptyHint') }}</p>
            </div>
          </aside>

          <!-- Region list -->
          <aside
            class="flex-1 min-h-0 flex flex-col bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-sm overflow-hidden"
          >
            <header class="px-3 py-2 bg-surface-container-low flex items-center justify-between gap-2">
              <span class="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant truncate">
                {{ sidebarMode === 'specialization' ? t('specializations.sidebarTitle') : t('home.districts.title') }}
              </span>
              <div class="flex bg-surface-container rounded-full p-0.5 text-[10px] font-bold">
                <button
                  type="button"
                  class="px-2 py-0.5 rounded-full transition-colors"
                  :class="sidebarMode === 'population' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-on-surface'"
                  @click="sidebarMode = 'population'"
                >
                  {{ t('specializations.sortByPopulation') }}
                </button>
                <button
                  type="button"
                  class="px-2 py-0.5 rounded-full transition-colors"
                  :class="sidebarMode === 'specialization' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-on-surface'"
                  @click="sidebarMode = 'specialization'"
                >
                  {{ t('specializations.sortBySpecialization') }}
                </button>
              </div>
            </header>
            <ul class="flex-1 overflow-y-auto py-1">
              <li v-for="r in sortedRegions" :key="r.key">
                <button
                  type="button"
                  class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-surface-container transition-colors text-left"
                  :class="[selected === r.key ? 'bg-primary-fixed' : '']"
                  @click="selected = selected === r.key ? null : r.key"
                >
                  <template v-if="sidebarMode === 'specialization'">
                    <span
                      class="w-6 h-6 rounded-md flex-shrink-0 flex items-center justify-center text-primary"
                      :style="{ backgroundColor: regionColors[r.key]?.base }"
                    >
                      <AppIcon :name="regionSpecializations[r.key]?.icon || 'public'" class="!text-[15px]" />
                    </span>
                    <span class="flex-1 min-w-0">
                      <span class="block text-[13px] font-semibold truncate">
                        {{ t(`regionsShort.${r.key}`) }}
                      </span>
                      <span class="block text-[10px] text-on-surface-variant truncate">
                        {{ t(`specializations.tags.${r.key}`) }}
                      </span>
                    </span>
                  </template>
                  <template v-else>
                    <span
                      class="w-2 h-2 rounded-full flex-shrink-0"
                      :style="{ backgroundColor: regionColors[r.key]?.selected }"
                    ></span>
                    <span class="text-[13px] font-semibold flex-1 truncate">
                      {{ t(`regionsShort.${r.key}`) }}
                    </span>
                    <span class="text-[10px] font-bold text-primary bg-primary-fixed px-1.5 py-0.5 rounded">
                      {{ r.population }}
                    </span>
                  </template>
                </button>
              </li>
            </ul>
          </aside>
        </div>
      </div>

    </div>

    <!-- Data section: detailed stat cards for selected region or whole country -->
    <div class="space-y-6">
      <header class="flex items-center gap-2">
        <AppIcon name="location_on" filled class="text-primary" />
        <h3 class="text-lg font-bold tracking-tight text-on-surface">
          {{ selected ? t(`regions.${selected}`) : t('home.map.nationalTitle') }}
        </h3>
        <span class="text-xs text-on-surface-variant">
          · {{ t('regionInfo.districts') }}: {{ current.districts }}
          <template v-if="current.cities">· {{ t('regionInfo.cities') }}: {{ current.cities }}</template>
          · {{ t('regionInfo.area') }}: {{ current.area }}
        </span>
      </header>

      <!-- stat.uz "raqamlarda" infographic — 10 verified metrics -->
      <section class="bg-surface-container-lowest rounded-xl shadow-sm p-6 lg:p-8 space-y-6">
        <header class="flex flex-col items-center text-center gap-1">
          <h3 class="text-xl lg:text-2xl font-extrabold tracking-tight text-on-surface uppercase">
            {{ figuresHeader.title }}
          </h3>
          <p class="text-sm text-on-surface-variant">{{ figuresHeader.subtitle }}</p>
          <span
            v-if="figuresBadge"
            class="mt-1 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide"
            :class="figuresBadge.kind === 'empty'
              ? 'bg-error-container text-on-error-container'
              : 'bg-tertiary-container text-on-tertiary-container'"
          >
            <AppIcon
              :name="figuresBadge.kind === 'empty' ? 'block' : 'warning'"
              class="!text-[12px]"
            />
            {{ figuresBadge.label }}
          </span>
        </header>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-5 lg:gap-6">
          <article
            v-for="tile in figureTiles"
            :key="tile.key"
            class="flex flex-col items-center text-center gap-3 p-5 rounded-xl bg-surface-container-low hover:bg-surface-container transition-colors"
          >
            <span
              class="w-11 h-11 rounded-full bg-primary-fixed text-primary flex items-center justify-center"
            >
              <AppIcon :name="tile.icon" filled class="!text-[22px]" />
            </span>
            <p class="text-[12px] font-semibold uppercase tracking-wide text-on-surface-variant leading-snug min-h-[2.75rem] flex items-center justify-center">
              {{ tile.label }}
            </p>
            <p
              class="text-[34px] font-extrabold leading-none tracking-tight flex items-baseline gap-1"
              :class="tile.isPercent && tile.hasData
                ? tile.toneClasses.value
                : (tile.hasData ? 'text-on-surface' : 'text-on-surface-variant')"
            >
              <span>{{ tile.value }}</span>
              <AppIcon
                v-if="tile.isPercent && tile.hasData && tile.direction === 'up'"
                name="arrow_drop_up"
                class="!text-[28px]"
              />
              <AppIcon
                v-else-if="tile.isPercent && tile.hasData && tile.direction === 'down'"
                name="arrow_drop_down"
                class="!text-[28px]"
              />
            </p>

            <!-- Delta in п.п. (tone-coloured, single secondary line) -->
            <p
              v-if="tile.isPercent && tile.hasData"
              class="tabular-nums text-[13px] font-bold leading-none"
              :class="tile.toneClasses.value"
            >
              {{ tile.deltaLabel }}
            </p>

            <!-- Deviation bar: ±20 п.п. visual range, centred at 100% -->
            <div
              v-if="tile.isPercent && tile.hasData"
              class="relative w-full h-2 rounded-full bg-surface-container"
              role="img"
              :aria-label="tile.deltaLabel"
            >
              <span class="absolute left-1/2 -top-1 -bottom-1 w-px bg-outline-variant"></span>
              <span
                class="absolute top-0 bottom-0 rounded-full"
                :class="tile.toneClasses.bar"
                :style="tile.barStyle"
              ></span>
            </div>

            <p
              v-if="tile.footnote"
              class="text-[11px] text-on-surface-variant leading-tight mt-auto"
            >
              {{ tile.footnote }}
            </p>
          </article>
        </div>
        <p
          class="text-[10px] text-right italic"
          :class="figuresSource.tone === 'warning' ? 'text-error' : 'text-on-surface-variant'"
        >
          {{ figuresSource.text }}
        </p>
      </section>

      <!-- Detailed analytics CTA (only when a region is selected) -->
      <transition name="slide-fade">
        <div
          v-if="selected"
          class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-primary text-on-primary rounded-xl px-6 py-5 shadow-lg"
        >
          <div class="flex items-center gap-3">
            <AppIcon name="analytics" filled />
            <div>
              <p class="text-xs uppercase tracking-widest opacity-80 font-bold">
                {{ t(`regions.${selected}`) }}
              </p>
              <p class="text-lg font-bold">{{ t('common.details') }}</p>
            </div>
          </div>
          <button
            type="button"
            class="bg-on-primary text-primary px-5 py-2.5 rounded-lg text-sm font-bold inline-flex items-center gap-2 hover:scale-105 active:scale-95 transition-transform self-start md:self-auto"
            @click="gotoAnalytics"
          >
            {{ t('nav.districts') }}
            <AppIcon name="arrow_forward" />
          </button>
        </div>
      </transition>
    </div>

    <!-- Floating action button -->
    <button
      type="button"
      class="fixed bottom-8 right-8 bg-primary text-white p-4 rounded-full shadow-2xl hover:scale-110 active:scale-95 transition-all z-50 flex items-center gap-2 group"
    >
      <AppIcon name="add_chart" filled />
      <span
        class="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 font-bold text-sm whitespace-nowrap"
      >
        {{ t('common.createReport') }}
      </span>
    </button>
  </section>

  <!-- Unavailable region toast -->
  <div v-if="unavailableToast"
    class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-on-surface text-surface px-5 py-3 rounded-xl shadow-lg text-sm font-semibold flex items-center gap-2">
    <AppIcon name="info" class="!text-[18px]" />
    {{ unavailableToast }}
  </div>
  </div>
</template>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
