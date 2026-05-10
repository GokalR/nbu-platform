<script setup>
/* District screen: hero KPIs + rating histogram + mahalla map + macro themes + mahalla rail. */
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import { fmt, iconForKpi } from '@/data/cerrV2Format.js'
import { groupMacroByTheme } from '@/data/macroThemes.js'
import EntityMap from '@/components/cerr-v2/EntityMap.vue'
import HistogramCard from '@/components/cerr-v2/HistogramCard.vue'
import ThemeBlock from '@/components/cerr-v2/ThemeBlock.vue'
import SidebarRail from '@/components/cerr-v2/SidebarRail.vue'
import CerrIcon from '@/components/cerr-v2/CerrIcon.vue'
import NavStepper from '@/components/cerr-v2/NavStepper.vue'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()
const { t: tFn } = useI18n()

const districtCode = computed(() => Number(route.params.districtCode))

watch(districtCode, async (code) => {
  if (!code) return
  await store.loadRegions()
  // Determine owning region (lazy: scan loaded regions, else load all overviews)
  let regionCode = null
  for (const list of Object.values(store.regionDistricts)) {
    if ((list || []).find((d) => d.code === code)) {
      regionCode = (list[0] || {}).region_code
      break
    }
  }
  if (!regionCode) {
    // Fallback: load each region's districts list once.
    for (const r of store.regions || []) {
      const ds = await store.loadRegionDistricts(r.code)
      if ((ds || []).find((d) => d.code === code)) { regionCode = r.code; break }
    }
  }
  await Promise.all([
    store.loadDistrictOverview(code),
    store.loadDistrictMacro(code),
    store.loadDistrictMahallas(code),
    store.loadDistrictGeo(code),
  ])
}, { immediate: true })

const district = computed(() => store.districtByCode(districtCode.value))
const overview = computed(() => store.districtOverview[districtCode.value] || null)
const macro = computed(() => store.districtMacro[districtCode.value] || null)
const mahallas = computed(() => store.districtMahallas[districtCode.value] || [])
const geo = computed(() => store.districtGeo[districtCode.value])

const heroKpis = computed(() => {
  const k = (overview.value?.kpis || []).filter((x) =>
    ['population', 'active_businesses', 'unemployed', 'rating_score'].includes(x.key)
  )
  // Add investment + industry from macro.indicators highlighted points if present.
  const m = macro.value
  if (m?.indicators) {
    for (const ind of m.indicators) {
      if (['investment_volume_mln_usd', 'industry_volume_bln_uzs'].includes(ind.key)) {
        const me = (ind.points || []).find((p) => p.highlighted)
        if (me) {
          k.push({
            key: ind.key === 'investment_volume_mln_usd' ? 'investment' : 'industry',
            label: ind.label,
            value: me.value,
            format: 'raw',
            direction: ind.direction || 'up',
            unit: ind.unit,
          })
        }
      }
    }
  }
  return k
})

/** KPI strip data (mahalla-hero look): formatted value + delta chip. */
const heroStats = computed(() => {
  return heroKpis.value.map((k) => {
    const dir = k.direction
    let tone = 'neu'
    if (k.change_pct != null) {
      if (dir === 'down') tone = k.change_pct > 0 ? 'neg' : 'pos'
      else tone = k.change_pct > 0 ? 'pos' : 'neg'
    }
    return {
      key: k.key,
      label: k.label,
      ico: iconForKpi(k.key),
      value: fmt.num(k.value),
      delta: k.change_pct != null
        ? `${k.change_pct > 0 ? '+' : ''}${Number(k.change_pct).toFixed(1).replace('.', ',')}%`
        : null,
      deltaTone: tone,
    }
  })
})

const histogram = computed(() => overview.value?.rating_histogram || [])
const macroThemes = computed(() => groupMacroByTheme(macro.value))

/** Mahalla list for the rail — alphabetical (per user request). Rank/tier is
 *  still computed from rating_score (see mahallaTier) for the badge color. */
const mahallaList = computed(() => {
  return mahallas.value.slice().sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'))
})

/** Higher rating_score = better. Rank mahallas within THIS district and tier by
 *  rank-percentile so every district gets a balanced 4-band split regardless of
 *  the score scale (some districts cluster 5-15, others 50-90). */
const TIER_COLOR = {
  lead: '#bfe5d4',
  mid:  '#f5e3b8',
  low:  '#f7c9b8',
  risk: '#eecccc',
}
function tierForRatio(ratio) {
  if (ratio == null) return null
  if (ratio <= 0.25) return 'lead'
  if (ratio <= 0.60) return 'mid'
  if (ratio <= 0.85) return 'low'
  return 'risk'
}

const mahallaTier = computed(() => {
  // Summary `rating_score` is the mahalla's place rank within its region
  // (lower number = better — e.g. rating_score 5 means 5th best in Sirdaryo).
  // Sort ASCENDING so position 1 → lowest value → best → "lead" tier.
  const arr = mahallas.value
    .filter((m) => m.rating_score != null)
    .slice()
    .sort((a, b) => a.rating_score - b.rating_score)
  const total = arr.length || 1
  const out = new Map()
  arr.forEach((m, i) => out.set(String(m.stir), tierForRatio((i + 1) / total)))
  return out
})

const tierCounts = computed(() => {
  const c = { lead: 0, mid: 0, low: 0, risk: 0 }
  for (const t of mahallaTier.value.values()) if (t in c) c[t]++
  return c
})

function rowFor(m) {
  const t = mahallaTier.value.get(String(m.stir))
  const tone = t === 'lead' ? 'high' : t === 'mid' ? 'mid' : 'low'
  return {
    key: m.stir,
    name: m.name,
    badge: m.rating_score != null ? `${Number(m.rating_score).toFixed(1)}` : '—',
    badgeTone: tone,
  }
}

const mGetKey = (f) => String(f.properties.stir || f.properties.STIR || '')
const mGetLabel = (f) => {
  const name = f.properties.mahalla_name || f.properties.name
  const score = f.properties.rating_score
  return score != null ? `${name} · ${Number(score).toFixed(1)}` : name
}
const mColorize = (f) => {
  const stir = String(f.properties.stir || f.properties.STIR || '')
  const t = mahallaTier.value.get(stir)
  return TIER_COLOR[t] || '#f0f1f4'
}

const sideHistogram = computed(() => {
  if (!histogram.value.length) return null
  const top10 = histogram.value[0]?.count || 0
  const total = histogram.value.reduce((s, b) => s + b.count, 0)
  return {
    big: `${top10} / ${total}`,
    lbl: 'Махаллей в топ-10%',
    desc: `Распределение махаллей района по рейтинговым группам.`,
    chips: [
      { tone: 'good', count: histogram.value[0]?.count || 0, label: 'лидеров' },
      { tone: 'mid', count: histogram.value[2]?.count || 0, label: 'средних' },
      { tone: 'bad', count: histogram.value[histogram.value.length - 1]?.count || 0, label: 'в зоне риска' },
    ],
  }
})

function openTier(stir) {
  router.push({ name: 'cerr-v2-mahalla', params: { stir: String(stir) } })
}
</script>

<template>
  <div class="page with-rail district-page">
    <div :style="{ display: 'flex', flexDirection: 'column', gap: '22px', minWidth: 0 }">
      <section class="hero hero-v2 mahalla-hero entity-hero">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <div class="hv2-eyebrow">{{ $t('cerrV2.eyebrow.district') }}</div>
            <h2 class="hero-title">{{ overview?.header?.title || district?.name || '—' }}</h2>
            <p class="hv2-breadcrumb">
              <span>{{ $t('cerrV2.country.title') }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ district?.region_name }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span>{{ $t('cerrV2.region.mahallasCount', { n: district?.mahalla_count }) }}</span>
              <span class="hv2-breadcrumb-sep">·</span>
              <span class="hv2-breadcrumb-period">
                <CerrIcon name="info" :size="11" /> {{ $t('cerrV2.common.data2025') }}
              </span>
            </p>
          </div>
        </div>
        <div class="hero-v2-stats mh-stats" :data-count="heroStats.length">
          <div v-for="s in heroStats" :key="s.key" class="hv2-stat">
            <div class="hv2-stat-head">
              <span class="hv2-stat-ico"><CerrIcon :name="s.ico" :size="16" /></span>
              <div class="hv2-stat-label">{{ s.label }}</div>
            </div>
            <div class="hv2-stat-row">
              <span class="hv2-stat-val tabular">{{ s.value }}</span>
              <span v-if="s.delta" :class="['mh-delta', s.deltaTone]">{{ s.delta }}</span>
            </div>
          </div>
        </div>
      </section>

      <HistogramCard v-if="histogram.length" :histogram="histogram" :side="sideHistogram" />

      <section v-if="geo" class="card map-card">
        <div class="map-grid">
          <EntityMap
            :geo="geo"
            :width="620"
            :height="420"
            :get-key="mGetKey"
            :get-label="mGetLabel"
            :colorize="mColorize"
            :selectable="() => true"
            :show-labels="false"
            :label-min="28"
            :title="overview?.header?.title || district?.name || ''"
            :subtitle="district ? `${district.region_name} · ${district.mahalla_count} махаллей` : ''"
            @select="(k) => openTier(String(k))"
          />
          <div class="map-side">
            <div class="map-side-h">{{ $t('cerrV2.district.ratingMahalla') }}</div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#bfe5d4' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.lead') }}</span>
              <span class="n tabular">{{ tierCounts.lead }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f5e3b8' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.mid') }}</span>
              <span class="n tabular">{{ tierCounts.mid }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#f7c9b8' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.low') }}</span>
              <span class="n tabular">{{ tierCounts.low }}</span>
            </div>
            <div class="map-tier">
              <span class="sw" :style="{ background: '#eecccc' }" />
              <span class="lbl">{{ $t('cerrV2.region.tier.risk') }}</span>
              <span class="n tabular">{{ tierCounts.risk }}</span>
            </div>
            <div class="map-focus">
              <div class="eye">{{ $t('cerrV2.common.hint') }}</div>
              <div class="hint">{{ $t('cerrV2.district.clickHintMahalla') }}</div>
            </div>
          </div>
        </div>
      </section>

      <div v-if="macroThemes.length" class="section-h">
        <span>{{ macro?.indicators?.length || 0 }} макропоказателей · {{ macroThemes.length }} тематических блока</span>
      </div>
      <div v-if="macroThemes.length" class="macro-themes">
        <ThemeBlock v-for="t in macroThemes" :key="t.id" :theme="t" />
      </div>
    </div>

    <SidebarRail
      :title="$t('cerrV2.district.siblingsTitle')"
      :count="mahallas.length"
      :items="mahallaList"
      :row-for="rowFor"
      :search-placeholder="$t('cerrV2.district.searchMahalla')"
      :meta-right="$t('cerrV2.common.sortAlpha')"
      @select="(m) => openTier(m.stir)"
    >
      <template #header-top><NavStepper /></template>
    </SidebarRail>
  </div>
</template>
