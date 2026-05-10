<script setup>
/* Mahalla page — full layout (hero-v2 style + 4 tabs + sibling rail).
 * Lives at /regions-v2/mahalla/:stir. */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCerrV2Store } from '@/stores/cerrV2.js'
import { fmt, iconForKpi } from '@/data/cerrV2Format.js'
import CerrIcon from '@/components/cerr-v2/CerrIcon.vue'
import SidebarRail from '@/components/cerr-v2/SidebarRail.vue'
import NavStepper from '@/components/cerr-v2/NavStepper.vue'
import TabOverview from '@/components/cerr-v2/TabOverview.vue'
import TabFarm from '@/components/cerr-v2/TabFarm.vue'
import TabPrograms from '@/components/cerr-v2/TabPrograms.vue'
import TabCompare from '@/components/cerr-v2/TabCompare.vue'

const route = useRoute()
const router = useRouter()
const store = useCerrV2Store()
const { t } = useI18n()

const stir = computed(() => String(route.params.stir || ''))
const activeTab = ref('overview')

watch(stir, async (s) => {
  if (!s) return
  activeTab.value = 'overview'
  await store.loadMahallaOverview(s)
  if (!findDistrictForStir(s)) {
    await store.loadRegions()
    for (const r of store.regions || []) {
      const ds = await store.loadRegionDistricts(r.code)
      let hit = false
      for (const d of ds || []) {
        const list = await store.loadDistrictMahallas(d.code)
        if ((list || []).some((mm) => String(mm.stir) === s)) { hit = true; break }
      }
      if (hit) break
    }
  }
}, { immediate: true })

function findDistrictForStir(s) {
  for (const list of Object.values(store.districtMahallas)) {
    const m = (list || []).find((mm) => String(mm.stir) === s)
    if (m) return m
  }
  return null
}

const m = computed(() => store.mahallaOverview[stir.value] || null)
const summary = computed(() => findDistrictForStir(stir.value))
const districtCode = computed(() => summary.value?.district_oktmo || null)
const district = computed(() => districtCode.value ? store.districtByCode(districtCode.value) : null)

const siblings = computed(() => {
  const list = (districtCode.value && store.districtMahallas[districtCode.value]) || []
  return [...list].sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ru'))
})

/** Parse "5/221" into { pos: 5, total: 221 }. */
function parseRank(s) {
  if (!s || typeof s !== 'string') return { pos: null, total: null }
  const [a, b] = s.split('/').map((p) => Number(p.trim()))
  return { pos: Number.isFinite(a) ? a : null, total: Number.isFinite(b) ? b : null }
}

const ratingContext = computed(() => {
  // Prefer CERR's pre-computed ranks from the overview header.
  const header = m.value?.header || {}
  let { pos: district_pos, total: district_total } = parseRank(header.district_rank)
  const { pos: region_pos, total: region_total } = parseRank(header.region_rank)

  // Fallback: compute district pos/total from sibling rating_scores if header missed it.
  if ((district_pos == null || district_total == null) && summary.value && districtCode.value) {
    const list = store.districtMahallas[districtCode.value] || []
    const sortedDistrict = [...list].sort((a, b) => (a.rating_score ?? Infinity) - (b.rating_score ?? Infinity))
    const idx = sortedDistrict.findIndex((x) => String(x.stir) === stir.value)
    if (idx >= 0) {
      district_pos = idx + 1
      district_total = sortedDistrict.length
    }
  }
  return { district_pos, district_total, region_pos, region_total }
})

const ratingScore = computed(() => {
  const k = (m.value?.kpis || []).find((x) => x.key === 'rating_score')
  return k?.value ?? null
})

/** Tier from a rank/total pair (top 25%, 25-60%, rest). */
function tierFromRank(pos, total) {
  if (!pos || !total) return null
  const ratio = pos / total
  if (ratio <= 0.25) return 'lead'
  if (ratio <= 0.60) return 'mid'
  return 'low'
}
/** Tier from absolute rating SCORE (0-100). */
function tierFromScore(score) {
  if (score == null) return null
  if (score >= 80) return 'lead'
  if (score >= 60) return 'mid'
  return 'low'
}

const ratingScoreTier = computed(() => tierFromScore(ratingScore.value))
const districtRankTier = computed(() =>
  tierFromRank(ratingContext.value?.district_pos, ratingContext.value?.district_total)
)
const regionRankTier = computed(() =>
  tierFromRank(ratingContext.value?.region_pos, ratingContext.value?.region_total)
)

/** Tier among district siblings (used by the rail row badge color). */
function ratingTier(score) {
  if (score == null) return 'low'
  const sorted = siblings.value.map((x) => x.rating_score).filter((v) => v != null).sort((a, b) => a - b)
  const idx = sorted.indexOf(score)
  if (idx < 0 || !sorted.length) return 'low'
  const ratio = (idx + 1) / sorted.length
  if (ratio <= 0.25) return 'high'
  if (ratio <= 0.60) return 'mid'
  return 'low'
}

function rowFor(mm) {
  return {
    key: String(mm.stir),
    name: mm.name,
    badge: mm.rating_score != null ? `${Number(mm.rating_score).toFixed(1)}` : '—',
    badgeTone: ratingTier(mm.rating_score),
  }
}

function goSibling(mm) {
  router.push({ name: 'cerr-v2-mahalla', params: { stir: mm.stir } })
}

const TABS = computed(() => [
  { id: 'overview', label: t('cerrV2.tabs.overview'), ico: 'pulse' },
  { id: 'farm',     label: t('cerrV2.tabs.farm'),     ico: 'tractor' },
  { id: 'progr',    label: t('cerrV2.tabs.programs'), ico: 'docs' },
  { id: 'compare',  label: t('cerrV2.tabs.compare'),  ico: 'target' },
])

function tabBadge(id) {
  if (!m.value) return null
  if (id === 'overview') return (m.value.kpis || []).length || null
  if (id === 'farm') {
    const det = m.value.detail || {}
    return ((det.specialization?.items || []).length) + (det.crops?.seasons?.length ? 1 : 0)
  }
  if (id === 'progr') return (m.value.detail?.subsidies?.programs || []).length || null
  if (id === 'compare') return m.value.peer_profile?.peer_set?.count || null
  return null
}

const breadcrumb = computed(() => m.value?.header?.breadcrumb || [])

/** 6-up KPI stats with formatted values + delta chips. Real data from
 *  m.kpis: each KPI has value, change_pct, district_avg, direction. */
const heroStats = computed(() => {
  return (m.value?.kpis || []).map((k) => {
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
      avg: k.district_avg != null ? `ср. р-н: ${fmt.num(Math.round(k.district_avg))}` : null,
    }
  })
})

</script>

<template>
  <div class="page with-rail mahalla-page">
    <div :style="{ display: 'flex', flexDirection: 'column', gap: '22px', minWidth: 0 }">
      <!-- Hero (compact) -->
      <section class="hero hero-v2 mahalla-hero">
        <div class="hero-v2-head">
          <div class="hero-v2-l">
            <div class="hv2-eyebrow">{{ $t('cerrV2.eyebrow.mahalla') }} · {{ summary?.district_name || '' }}</div>
            <h2 class="hero-title">{{ m?.header?.title || summary?.name || '—' }}</h2>
            <p class="hv2-breadcrumb">
              <template v-if="breadcrumb.length">{{ breadcrumb.slice(0, -1).join(' · ') }}</template>
              <template v-else-if="summary">{{ summary.region_name }} · {{ summary.district_name }}</template>
              <span class="hv2-breadcrumb-sep">·</span>
              <span class="hv2-breadcrumb-period">
                <CerrIcon name="info" :size="11" /> {{ $t('cerrV2.common.data2025') }}
              </span>
            </p>
          </div>

          <!-- Rating callout (right side of hero) -->
          <div v-if="ratingScore != null" :class="['mh-rating-card', `tier-${ratingScoreTier || 'mid'}`]">
            <div class="mh-rating-num tabular">{{ Number(ratingScore).toFixed(1).replace('.', ',') }}</div>
            <div class="mh-rating-lbl">{{ $t('cerrV2.mahalla.ratingScore') }}</div>
            <div class="mh-rating-ranks">
              <div
                v-if="ratingContext?.district_pos"
                :class="['mh-rank-pill', `tier-${districtRankTier || 'mid'}`]"
              >
                <CerrIcon name="award" :size="11" />
                <span><b>{{ ratingContext.district_pos }}</b> / {{ ratingContext.district_total }}</span>
                <span class="lbl">{{ $t('cerrV2.mahalla.inDistrict') }}</span>
              </div>
              <div
                v-if="ratingContext?.region_pos"
                :class="['mh-rank-pill', `tier-${regionRankTier || 'mid'}`]"
              >
                <CerrIcon name="map" :size="11" />
                <span><b>{{ ratingContext.region_pos }}</b> / {{ ratingContext.region_total }}</span>
                <span class="lbl">{{ $t('cerrV2.mahalla.inRegion') }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="hero-v2-stats mh-stats">
          <div v-for="s in heroStats" :key="s.key" class="hv2-stat">
            <div class="hv2-stat-head">
              <span class="hv2-stat-ico"><CerrIcon :name="s.ico" :size="16" /></span>
              <div class="hv2-stat-label">{{ s.label }}</div>
            </div>
            <div class="hv2-stat-row">
              <span class="hv2-stat-val tabular">{{ s.value }}</span>
              <span v-if="s.delta" :class="['mh-delta', s.deltaTone]">{{ s.delta }}</span>
            </div>
            <div v-if="s.avg" class="mh-avg">{{ s.avg }}</div>
          </div>
        </div>
      </section>

      <!-- Tabs nav -->
      <nav class="cerr-v2-tabs">
        <button
          v-for="t in TABS"
          :key="t.id"
          :class="['tab-btn', activeTab === t.id ? 'active' : '']"
          @click="activeTab = t.id"
        >
          <CerrIcon :name="t.ico" :size="14" /> {{ t.label }}
          <span v-if="tabBadge(t.id) != null" class="badge">{{ tabBadge(t.id) }}</span>
        </button>
      </nav>

      <!-- Tab content -->
      <div v-if="m" class="tab-content">
        <TabOverview v-if="activeTab === 'overview'" :m="m" :rating="ratingContext" />
        <TabFarm v-else-if="activeTab === 'farm'" :m="m" />
        <TabPrograms v-else-if="activeTab === 'progr'" :m="m" />
        <TabCompare v-else-if="activeTab === 'compare'" :m="m" />
      </div>
      <div v-else class="empty-hint">
        <CerrIcon name="info" :size="16" /> {{ $t('cerrV2.common.loading') }}
      </div>
    </div>

    <SidebarRail
      :title="$t('cerrV2.mahalla.siblingsTitle')"
      :count="siblings.length"
      :items="siblings"
      :row-for="rowFor"
      :search-placeholder="$t('cerrV2.mahalla.searchMahalla')"
      :active-key="stir"
      @select="goSibling"
    >
      <template #header-top>
        <NavStepper :mahalla="{ stir, name: m?.header?.title || summary?.name }" />
      </template>
    </SidebarRail>
  </div>
</template>

<style>
/* ============== Mahalla hero — KPI sizing kept bigger; only the outer
 * container chrome (padding, section gap, stats-strip padding) is tight,
 * so the panel as a whole is shorter without shrinking the data tiles. */
.cerr-v2-scope .mahalla-hero {
  padding: 22px 32px 20px;
  gap: 26px;
}
.cerr-v2-scope .mahalla-hero .hero-v2-head {
  grid-template-columns: minmax(0, 1fr) minmax(260px, 340px);
  gap: 32px;
}
.cerr-v2-scope .mahalla-hero .hv2-eyebrow {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.55);
  margin-bottom: 0;
}
.cerr-v2-scope .mahalla-hero .hero-title {
  font-size: clamp(48px, 4.6vw, 64px);
  font-weight: 900;
  letter-spacing: -.034em;
  line-height: 1.04;
  margin: 0 0 2px;
  color: #fff;
}
.cerr-v2-scope .mahalla-hero .hv2-breadcrumb {
  margin: 6px 0 0;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.cerr-v2-scope .mahalla-hero .hv2-breadcrumb-sep {
  color: rgba(255, 255, 255, 0.35);
  font-weight: 700;
}
.cerr-v2-scope .mahalla-hero .hv2-breadcrumb-period {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 0.01em;
}

/* Rating callout on the right of hero head — tinted by tier */
.cerr-v2-scope .mh-rating-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 10px 14px;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4px 12px;
  align-items: center;
  align-self: start;
  backdrop-filter: blur(2px);
  position: relative;
  overflow: hidden;
}
.cerr-v2-scope .mh-rating-card .mh-rating-num {
  grid-row: 1 / 3;
  grid-column: 1;
}
.cerr-v2-scope .mh-rating-card .mh-rating-lbl {
  grid-row: 1;
  grid-column: 2;
  margin-bottom: 0;
}
.cerr-v2-scope .mh-rating-card .mh-rating-ranks {
  grid-row: 2;
  grid-column: 2;
}
.cerr-v2-scope .mh-rating-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: var(--mh-rate-color, rgba(255,255,255,.3));
  opacity: 0.85;
}
.cerr-v2-scope .mh-rating-card.tier-lead { --mh-rate-color: #34d399; }
.cerr-v2-scope .mh-rating-card.tier-mid  { --mh-rate-color: #f5cd65; }
.cerr-v2-scope .mh-rating-card.tier-low  { --mh-rate-color: #f87171; }

.cerr-v2-scope .mh-rating-num {
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -.04em;
  line-height: 0.95;
  font-variant-numeric: tabular-nums;
  color: var(--mh-rate-color, #fff);
  text-shadow: 0 0 24px rgba(255, 255, 255, 0.06);
}
.cerr-v2-scope .mh-rating-lbl {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.3;
  margin-bottom: 6px;
}
.cerr-v2-scope .mh-rating-ranks {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.cerr-v2-scope .mh-rank-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.01em;
  background: rgba(255, 255, 255, 0.10);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.92);
  white-space: nowrap;
}
.cerr-v2-scope .mh-rank-pill b { font-weight: 900; font-variant-numeric: tabular-nums; }
.cerr-v2-scope .mh-rank-pill .lbl { color: rgba(255, 255, 255, 0.6); font-weight: 600; }
.cerr-v2-scope .mh-rank-pill.tier-lead {
  background: rgba(52, 211, 153, 0.18);
  border-color: rgba(52, 211, 153, 0.4);
  color: #d1fae5;
}
.cerr-v2-scope .mh-rank-pill.tier-lead .lbl { color: rgba(209, 250, 229, 0.7); }
.cerr-v2-scope .mh-rank-pill.tier-mid {
  background: rgba(245, 205, 101, 0.16);
  border-color: rgba(245, 205, 101, 0.38);
  color: #fef3c7;
}
.cerr-v2-scope .mh-rank-pill.tier-mid .lbl { color: rgba(254, 243, 199, 0.7); }
.cerr-v2-scope .mh-rank-pill.tier-low {
  background: rgba(248, 113, 113, 0.18);
  border-color: rgba(248, 113, 113, 0.4);
  color: #fecaca;
}
.cerr-v2-scope .mh-rank-pill.tier-low .lbl { color: rgba(254, 202, 202, 0.7); }

/* 6-up stat strip — fixed-height head so values align across tiles.
 * Tight outer chrome (smaller strip padding, no row gaps) keeps the panel
 * short while the inner KPI tiles stay at full size. */
.cerr-v2-scope .mahalla-hero .hero-v2-stats {
  padding: 18px 0 8px;
  border-bottom: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.10);
}
.cerr-v2-scope .mh-stats {
  grid-template-columns: repeat(6, 1fr);
  align-items: stretch;
}
.cerr-v2-scope .mh-stats .hv2-stat {
  padding: 4px 14px;
  display: flex;
  flex-direction: column;
  gap: 0;
  justify-content: flex-start;
}
/* CRITICAL: head has FIXED height (not min-height) and label has overflow:hidden
 * so -webkit-line-clamp actually trims. Keeps every value at the same y-position
 * regardless of label line count (1, 2, or clamped 3 lines). */
.cerr-v2-scope .mh-stats .hv2-stat-head {
  height: 60px;
  align-items: flex-start;
  margin-bottom: 8px;
  flex: 0 0 60px;
}
.cerr-v2-scope .mh-stats .hv2-stat-ico {
  margin-top: 1px;
}
.cerr-v2-scope .mh-stats .hv2-stat-label {
  white-space: normal;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
  font-size: 12.5px;
  letter-spacing: 0.06em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  max-height: 50px;
}
.cerr-v2-scope .mh-stats .hv2-stat-row {
  gap: 10px;
  margin-top: 0;
  flex-wrap: wrap;
}
.cerr-v2-scope .mh-stats .hv2-stat-val {
  font-size: clamp(36px, 3.2vw, 46px);
  font-weight: 900;
  letter-spacing: -.04em;
  line-height: 1;
  color: #fff;
}
.cerr-v2-scope .mh-avg {
  margin-top: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.02em;
}

/* Per-stat delta chip */
.cerr-v2-scope .mh-delta {
  font-size: 13px;
  font-weight: 900;
  letter-spacing: -.005em;
  padding: 2px 7px;
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  line-height: 1.4;
}
.cerr-v2-scope .mh-delta.pos { background: rgba(52, 211, 153, .14); color: #34d399; }
.cerr-v2-scope .mh-delta.neg { background: rgba(248, 113, 113, .14); color: #f87171; }
.cerr-v2-scope .mh-delta.neu { background: rgba(255, 255, 255, .08); color: rgba(255, 255, 255, .6); }

/* Tabs nav as a clean card strip */
.cerr-v2-scope .cerr-v2-tabs {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 6px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  box-shadow: 0 1px 2px rgba(15, 15, 12, 0.04);
}
.cerr-v2-scope .cerr-v2-tabs .tab-btn {
  flex: 1 1 auto;
  min-width: 140px;
  border: 0;
  background: none;
  border-radius: 10px;
  padding: 10px 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: background .14s, color .14s;
}
.cerr-v2-scope .cerr-v2-tabs .tab-btn:hover { background: var(--n-50); color: var(--text); }
.cerr-v2-scope .cerr-v2-tabs .tab-btn.active {
  background: linear-gradient(135deg, var(--brand-navy), var(--brand-navy-bright));
  color: #fff;
  box-shadow: 0 4px 10px -4px rgba(0, 84, 166, .35);
}
.cerr-v2-scope .cerr-v2-tabs .tab-btn .badge {
  margin-left: auto;
  font-size: 10.5px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(0, 0, 0, .06);
  color: var(--text-muted);
  letter-spacing: 0.02em;
}
.cerr-v2-scope .cerr-v2-tabs .tab-btn.active .badge {
  background: rgba(255, 255, 255, .18);
  color: #fff;
}

.cerr-v2-scope .mahalla-page .tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Responsive: stack 6-up on narrow */
@media (max-width: 1280px) {
  .cerr-v2-scope .mh-stats { grid-template-columns: repeat(3, 1fr); row-gap: 18px; }
  .cerr-v2-scope .mh-stats .hv2-stat:nth-child(4) { border-left: none; padding-left: 0; }
}
@media (max-width: 900px) {
  .cerr-v2-scope .mahalla-hero .hero-v2-head { grid-template-columns: 1fr; }
  .cerr-v2-scope .mh-rating-card { align-self: flex-start; }
  .cerr-v2-scope .mh-stats { grid-template-columns: repeat(2, 1fr); }
  .cerr-v2-scope .mh-stats .hv2-stat:nth-child(3) { border-left: none; padding-left: 0; }
}
@media (max-width: 600px) {
  .cerr-v2-scope .mh-stats { grid-template-columns: 1fr; }
  .cerr-v2-scope .mh-stats .hv2-stat { border-left: none; padding-left: 0; }
}
</style>
