<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import KpiCard from '@/components/KpiCard.vue'
import StatCard from '@/components/StatCard.vue'
import UzbekistanMap from '@/components/UzbekistanMap.vue'
import AppIcon from '@/components/AppIcon.vue'
import RegionDropdown from '@/components/RegionDropdown.vue'
import { regions, regionKeys, national, regionSpecializations } from '@/data/regions'
import { regionColors } from '@/data/regionColors'

const { t, tm } = useI18n()
const router = useRouter()

const selected = ref(null) // null = whole country
const sidebarMode = ref('population') // 'population' | 'specialization'
const selectedYear = ref(2025)
const availableYears = [2021, 2022, 2023, 2024, 2025]

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

const populationRank = computed(() => {
  if (!selected.value) return null
  const sorted = regionKeys
    .map((k) => ({ k, p: regions[k].populationRaw }))
    .sort((a, b) => b.p - a.p)
  const idx = sorted.findIndex((x) => x.k === selected.value)
  return idx >= 0 ? idx + 1 : null
})

const snapshotStats = computed(() => {
  if (!selected.value) {
    return [
      { label: t('home.kpi.population'), value: national.population },
      { label: t('home.kpi.gdpGrowth'), value: national.gdpGrowth },
      { label: t('home.kpi.exports'), value: national.exports },
      { label: t('home.snapshot.regions'), value: String(regionKeys.length) },
    ]
  }
  const r = regions[selected.value]
  return [
    { label: t('home.kpi.population'), value: r.population },
    { label: t('home.kpi.gdpGrowth'), value: r.gdpGrowth ?? t('home.cards.noData') },
    { label: t('home.kpi.exports'), value: r.exports },
    {
      label: t('home.snapshot.populationRank'),
      value: populationRank.value ? `#${populationRank.value} / ${regionKeys.length}` : '—',
    },
  ]
})

const kpis = computed(() => [
  {
    key: 'population',
    icon: 'groups',
    value: current.value.population,
    delta: '+1.2%',
    tone: 'positive',
  },
  {
    key: 'gdpGrowth',
    icon: 'trending_up',
    value: current.value.gdpGrowth ?? t('home.cards.noData'),
    delta: current.value.gdpDelta ?? '',
    tone: current.value.gdpGrowth == null ? 'neutral' : 'positive',
  },
  {
    key: 'exports',
    icon: 'payments',
    value: current.value.exports,
    delta: t('home.kpi.target'),
    tone: 'positive',
  },
  {
    key: 'mahallas',
    icon: 'location_city',
    value: current.value.mahallas.toLocaleString(),
    delta: t('home.kpi.total'),
    tone: 'neutral',
  },
])

const NO_DATA = computed(() => t('home.cards.noData'))

function buildVerified(arr, colors) {
  return arr.map((b, i) => ({
    label: t(b.labelKey),
    value: b.value ?? NO_DATA.value,
    percent: b.value == null ? 0 : b.percent,
    color: colors[i],
  }))
}

const economicBars = computed(() => {
  if (current.value.verified?.economic) {
    return buildVerified(current.value.verified.economic, ['bg-primary', 'bg-primary-container', 'bg-primary opacity-60'])
  }
  return [
    {
      label: t('home.cards.industry'),
      value: scaleVal(current.value.bars.industry, '$', ' mln'),
      percent: current.value.bars.industry,
      color: 'bg-primary',
    },
    {
      label: t('home.cards.agriculture'),
      value: scaleVal(current.value.bars.agriculture, '$', ' mln'),
      percent: current.value.bars.agriculture,
      color: 'bg-primary-container',
    },
    {
      label: t('home.cards.services'),
      value: scaleVal(current.value.bars.services, '$', ' mln'),
      percent: current.value.bars.services,
      color: 'bg-primary opacity-60',
    },
  ]
})

const populationBars = computed(() => {
  if (current.value.verified?.population) {
    return buildVerified(current.value.verified.population, ['bg-tertiary', 'bg-tertiary-container', 'bg-tertiary opacity-60'])
  }
  return [
    {
      label: t('home.cards.employed'),
      value: pctOfPop(current.value.employment.employed, 0.55),
      percent: current.value.employment.employed,
      color: 'bg-tertiary',
    },
    {
      label: t('home.cards.selfEmployed'),
      value: pctOfPop(current.value.employment.selfEmployed, 0.22),
      percent: current.value.employment.selfEmployed,
      color: 'bg-tertiary-container',
    },
    {
      label: t('home.cards.education'),
      value: pctOfPop(current.value.employment.education, 0.04),
      percent: current.value.employment.education,
      color: 'bg-tertiary opacity-60',
    },
  ]
})

const bankBars = computed(() => {
  if (current.value.verified?.bank) {
    return buildVerified(current.value.verified.bank, ['bg-primary-container', 'bg-primary', 'bg-secondary'])
  }
  return [
    {
      label: t('home.cards.credits'),
      value: scaleVal(current.value.bank.credits, '', ' trln'),
      percent: current.value.bank.credits,
      color: 'bg-primary-container',
    },
    {
      label: t('home.cards.newBusiness'),
      value: `${(current.value.bank.newBusiness * 80).toLocaleString()} ta`,
      percent: current.value.bank.newBusiness,
      color: 'bg-primary',
    },
    {
      label: t('home.cards.exporters'),
      value: `${current.value.bank.exporters * 12} ta`,
      percent: current.value.bank.exporters,
      color: 'bg-secondary',
    },
  ]
})

function scaleVal(percent, prefix = '', suffix = '') {
  return `${prefix}${(percent * 5).toFixed(0)}${suffix}`
}

function pctOfPop(percent, factor) {
  const popMln =
    parseFloat(String(current.value.population).replace(/[^\d.]/g, '')) || 1
  const v = popMln * factor * (percent / 100) * 4
  return v >= 1 ? `${v.toFixed(1)} mln` : `${(v * 1000).toFixed(0)}k`
}

const ANALYTICS_REGIONS = new Set(['fergana', 'samarqand'])
// Regions that open straight into a viloyat-level dashboard (no district picker).
const REGION_DASHBOARD_DISTRICT = { samarqand: 'samarqand_region' }
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
  const query = { region: selected.value || '' }
  const regionDistrict = selected.value && REGION_DASHBOARD_DISTRICT[selected.value]
  if (regionDistrict) query.district = regionDistrict
  router.push({ name: 'districts', query })
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
          <div class="inline-flex items-center gap-1 bg-surface-container-lowest border border-outline-variant/40 rounded-lg px-2 py-1">
            <AppIcon name="calendar_today" class="!text-[14px] text-on-surface-variant" />
            <select
              v-model="selectedYear"
              class="bg-transparent text-xs font-bold text-on-surface focus:outline-none cursor-pointer pr-1"
              aria-label="Year"
            >
              <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
            </select>
          </div>
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

      <!-- KPI cards between map and region selection (fills the gap) -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-6">
        <KpiCard
          v-for="kpi in kpis"
          :key="kpi.key"
          :icon="kpi.icon"
          :value="kpi.value"
          :label="t(`home.kpi.${kpi.key}`)"
          :delta="kpi.delta"
          :tone="kpi.tone"
        />
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

      <!-- Stat cards (dynamic) -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 lg:gap-8">
        <StatCard icon="finance" :title="t('home.cards.economic')" :bars="economicBars" />
        <StatCard icon="person_search" :title="t('home.cards.population')" :bars="populationBars" />
        <StatCard icon="storefront" :title="t('home.cards.bank')" :bars="bankBars" />
      </div>

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
