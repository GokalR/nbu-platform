<script setup>
/* "Сравнение" tab — peer-group comparison.
 *
 * The peer group is built by CERR:
 *   1. Take all mahallas in the same district.
 *   2. Filter to those with similar population (~ ±30% of this mahalla).
 *   3. If too narrow (rare), fall back to the entire district.
 *   4. For each of CERR's ~31 socioeconomic indicators, compute this mahalla's
 *      rank within the peer group → percentile.
 *   5. Pick the top 5 (strengths) and bottom 5 (weaknesses) by percentile.
 *
 * Interpretation:
 *   - direction: 'down'  → lower value is better (e.g. unemployment)
 *   - direction: 'up'    → higher value is better
 *   - percentile is normalized so 100 = best in the peer group regardless of direction. */
import { computed } from 'vue'
import CerrIcon from './CerrIcon.vue'

const props = defineProps({
  m: { type: Object, required: true },
})

const peerSet = computed(() => props.m?.peer_profile?.peer_set || null)
const indicatorCount = computed(() => props.m?.peer_profile?.indicator_count || 0)
const strengths = computed(() => props.m?.peer_profile?.strengths || [])
const weaknesses = computed(() => props.m?.peer_profile?.weaknesses || [])

/** Pull the population band out of the description. CERR formats it as
 *  "<district> + аҳолиси X–Y оралиғида (N маҳалла)". Returns { low, high } or null. */
const popBand = computed(() => {
  const d = peerSet.value?.description
  if (!d) return null
  const m = d.match(/(\d[\d\s]*)[–-](\d[\d\s]*)/)
  if (!m) return null
  const low = Number(m[1].replace(/\s/g, ''))
  const high = Number(m[2].replace(/\s/g, ''))
  if (!Number.isFinite(low) || !Number.isFinite(high)) return null
  return { low, high }
})

const districtName = computed(() => {
  const d = peerSet.value?.description
  return d ? d.split('+')[0].trim() : ''
})

function fmtNum(v) {
  if (v == null) return '—'
  if (typeof v !== 'number') return String(v)
  return Math.abs(v) < 100 ? v.toFixed(2).replace('.', ',') : Math.round(v).toLocaleString('ru-RU').replace(/,/g, ' ')
}
function fmtBand(n) { return Math.round(n).toLocaleString('ru-RU').replace(/,/g, ' ') }
</script>

<template>
  <!-- Methodology card explaining how the peer group is built -->
  <section class="card mh-cmp-howto">
    <header class="mh-cmp-howto-h">
      <div class="ico-tile"><CerrIcon name="target" :size="14" /></div>
      <div>
        <div class="t">{{ $t('cerrV2.compare.title') }}</div>
        <div class="s">{{ $t('cerrV2.compare.sub') }}</div>
      </div>
    </header>
    <ol class="mh-cmp-steps">
      <li>
        <span class="n">1</span>
        <div>
          <b>{{ $t('cerrV2.compare.step1Bold') }}</b>
          <div class="muted">{{ $t('cerrV2.compare.step1Sub', { name: districtName || $t('cerrV2.compare.sameDistrict') }) }}</div>
        </div>
      </li>
      <li>
        <span class="n">2</span>
        <div>
          <b>{{ $t('cerrV2.compare.step2Bold') }}</b> {{ $t('cerrV2.compare.step2Range') }}
          <div v-if="popBand" class="muted">
            {{ $t('cerrV2.compare.step2RangeText', { low: fmtBand(popBand.low), high: fmtBand(popBand.high) }) }}
          </div>
        </div>
      </li>
      <li>
        <span class="n">3</span>
        <div>
          <b>{{ $t('cerrV2.compare.step3Bold', { n: peerSet?.count ?? 0 }) }}</b> {{ $t('cerrV2.compare.step3Sub') }}
          <div v-if="peerSet?.fallback_to_district" class="muted">
            {{ $t('cerrV2.compare.step3Note', { n: peerSet?.count }) }}
          </div>
        </div>
      </li>
      <li>
        <span class="n">4</span>
        <div>
          <b>{{ $t('cerrV2.compare.step4Bold', { n: indicatorCount || '31' }) }}</b> {{ $t('cerrV2.compare.step4Sub') }}
        </div>
      </li>
      <li>
        <span class="n">5</span>
        <div>
          <b>{{ $t('cerrV2.compare.step5Bold') }}</b> {{ $t('cerrV2.compare.step5Sub') }}
        </div>
      </li>
    </ol>
  </section>

  <!-- Strengths -->
  <section v-if="strengths.length" class="card mh-cmp-card">
    <header class="mh-cmp-h pos">
      <div class="t-l">
        <CerrIcon name="check" :size="14" />
        <span class="t">{{ $t('cerrV2.compare.strengths') }}</span>
        <span class="ct">{{ strengths.length }}</span>
      </div>
      <div class="t-r">{{ $t('cerrV2.compare.strengthsSub') }}</div>
    </header>
    <div class="mh-cmp-list">
      <div v-for="(p, i) in strengths" :key="`s-${i}`" class="mh-cmp-row pos">
        <div class="row-head">
          <span class="rank">#{{ p.peer_rank }} <span class="of">/ {{ p.peer_count }}</span></span>
          <span class="lbl">{{ p.label }}</span>
          <span :class="['pct-chip', 'pos']">{{ Math.round(p.percentile) }}%</span>
        </div>
        <div class="row-vals">
          <div class="me">
            <span class="num">{{ fmtNum(p.this_value) }}</span>
            <span class="me-lbl">{{ $t('cerrV2.compare.thisMahalla') }}</span>
          </div>
          <div class="vs-sep">vs</div>
          <div class="avg">
            <span class="num">{{ fmtNum(p.district_avg) }}</span>
            <span class="me-lbl">{{ $t('cerrV2.compare.peerAvg') }}</span>
          </div>
          <div class="unit">{{ p.unit }}</div>
          <div v-if="p.direction" class="dir" :title="p.direction === 'down' ? $t('cerrV2.compare.lessIsBetterAlt') : $t('cerrV2.compare.moreIsBetterAlt')">
            {{ p.direction === 'down' ? $t('cerrV2.compare.lessIsBetter') : $t('cerrV2.compare.moreIsBetter') }}
          </div>
        </div>
        <div class="pct-bar pos"><i :style="{ width: `${p.percentile}%` }" /></div>
      </div>
    </div>
  </section>

  <!-- Weaknesses -->
  <section v-if="weaknesses.length" class="card mh-cmp-card">
    <header class="mh-cmp-h neg">
      <div class="t-l">
        <CerrIcon name="warn" :size="14" />
        <span class="t">{{ $t('cerrV2.compare.weaknesses') }}</span>
        <span class="ct">{{ weaknesses.length }}</span>
      </div>
      <div class="t-r">{{ $t('cerrV2.compare.weaknessesSub') }}</div>
    </header>
    <div class="mh-cmp-list">
      <div v-for="(p, i) in weaknesses" :key="`w-${i}`" class="mh-cmp-row neg">
        <div class="row-head">
          <span class="rank">#{{ p.peer_rank }} <span class="of">/ {{ p.peer_count }}</span></span>
          <span class="lbl">{{ p.label }}</span>
          <span :class="['pct-chip', 'neg']">{{ Math.round(p.percentile) }}%</span>
        </div>
        <div class="row-vals">
          <div class="me">
            <span class="num">{{ fmtNum(p.this_value) }}</span>
            <span class="me-lbl">{{ $t('cerrV2.compare.thisMahalla') }}</span>
          </div>
          <div class="vs-sep">vs</div>
          <div class="avg">
            <span class="num">{{ fmtNum(p.district_avg) }}</span>
            <span class="me-lbl">{{ $t('cerrV2.compare.peerAvg') }}</span>
          </div>
          <div class="unit">{{ p.unit }}</div>
          <div v-if="p.direction" class="dir" :title="p.direction === 'down' ? $t('cerrV2.compare.lessIsBetterAlt') : $t('cerrV2.compare.moreIsBetterAlt')">
            {{ p.direction === 'down' ? $t('cerrV2.compare.lessIsBetter') : $t('cerrV2.compare.moreIsBetter') }}
          </div>
        </div>
        <div class="pct-bar neg"><i :style="{ width: `${p.percentile}%` }" /></div>
      </div>
    </div>
  </section>
</template>

<style>
/* ============== Comparison tab ============== */
.cerr-v2-scope .mh-cmp-howto {
  padding: 18px 22px;
  background: linear-gradient(135deg, rgba(0, 84, 166, 0.04), rgba(33, 182, 206, 0.04));
  border: 1px solid rgba(0, 84, 166, 0.14);
  border-radius: 14px;
}
.cerr-v2-scope .mh-cmp-howto-h {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-cmp-howto-h .t { font-size: 14px; font-weight: 800; color: var(--text); }
.cerr-v2-scope .mh-cmp-howto-h .s { font-size: 12px; color: var(--text-soft); margin-top: 2px; }
.cerr-v2-scope .mh-cmp-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px 14px;
}
.cerr-v2-scope .mh-cmp-steps li {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  font-size: 12.5px;
  line-height: 1.45;
  color: var(--text);
}
.cerr-v2-scope .mh-cmp-steps b { font-weight: 700; }
.cerr-v2-scope .mh-cmp-steps .muted {
  font-size: 11.5px;
  color: var(--text-soft);
  margin-top: 2px;
  font-weight: 500;
}
.cerr-v2-scope .mh-cmp-steps .muted .emp { color: var(--brand-navy); font-weight: 800; }
.cerr-v2-scope .mh-cmp-steps .n {
  flex-shrink: 0;
  width: 22px; height: 22px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--brand-navy), var(--brand-navy-bright));
  color: #fff;
  font-size: 11px; font-weight: 800;
  display: grid; place-items: center;
  margin-top: 1px;
}

/* Card containing rows */
.cerr-v2-scope .mh-cmp-card {
  padding: 0;
  border-radius: 14px;
  overflow: hidden;
}
.cerr-v2-scope .mh-cmp-h {
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-cmp-h.pos { background: linear-gradient(90deg, rgba(20, 163, 74, 0.08), transparent); }
.cerr-v2-scope .mh-cmp-h.neg { background: linear-gradient(90deg, rgba(216, 56, 56, 0.08), transparent); }
.cerr-v2-scope .mh-cmp-h .t-l { display: inline-flex; align-items: center; gap: 8px; }
.cerr-v2-scope .mh-cmp-h .t {
  font-size: 14px; font-weight: 800; letter-spacing: -0.005em; text-transform: uppercase;
}
.cerr-v2-scope .mh-cmp-h.pos .t, .cerr-v2-scope .mh-cmp-h.pos > .t-l > svg { color: var(--pos-700); }
.cerr-v2-scope .mh-cmp-h.neg .t, .cerr-v2-scope .mh-cmp-h.neg > .t-l > svg { color: var(--neg-700); }
.cerr-v2-scope .mh-cmp-h .ct {
  font-size: 11px; font-weight: 800;
  padding: 2px 8px; border-radius: 6px;
  background: var(--n-100); color: var(--text-muted);
}
.cerr-v2-scope .mh-cmp-h .t-r {
  font-size: 11.5px; font-weight: 600; color: var(--text-soft);
}

.cerr-v2-scope .mh-cmp-list {
  display: flex;
  flex-direction: column;
}
.cerr-v2-scope .mh-cmp-row {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cerr-v2-scope .mh-cmp-row:last-child { border-bottom: 0; }
.cerr-v2-scope .mh-cmp-row .row-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.cerr-v2-scope .mh-cmp-row .rank {
  font-size: 12px; font-weight: 800; color: var(--text-muted);
  min-width: 56px;
  font-variant-numeric: tabular-nums;
}
.cerr-v2-scope .mh-cmp-row .rank .of { color: var(--text-faint); font-weight: 600; }
.cerr-v2-scope .mh-cmp-row .lbl {
  font-size: 13.5px; font-weight: 700; color: var(--text);
  flex: 1;
  line-height: 1.35;
}
.cerr-v2-scope .mh-cmp-row .pct-chip {
  font-size: 11.5px; font-weight: 800;
  padding: 3px 9px; border-radius: 999px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.cerr-v2-scope .mh-cmp-row .pct-chip.pos { background: var(--pos-50); color: var(--pos-700); }
.cerr-v2-scope .mh-cmp-row .pct-chip.neg { background: var(--neg-50); color: var(--neg-700); }

.cerr-v2-scope .mh-cmp-row .row-vals {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 14px;
  padding-left: 68px;
}
.cerr-v2-scope .mh-cmp-row .me, .cerr-v2-scope .mh-cmp-row .avg {
  display: inline-flex; flex-direction: column; gap: 1px;
}
.cerr-v2-scope .mh-cmp-row .num {
  font-size: 18px; font-weight: 900; letter-spacing: -0.018em;
  font-variant-numeric: tabular-nums;
  color: var(--text);
  line-height: 1;
}
.cerr-v2-scope .mh-cmp-row.pos .me .num { color: var(--pos-700); }
.cerr-v2-scope .mh-cmp-row.neg .me .num { color: var(--neg-700); }
.cerr-v2-scope .mh-cmp-row .avg .num { color: var(--text-soft); }
.cerr-v2-scope .mh-cmp-row .me-lbl {
  font-size: 10px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--text-faint);
}
.cerr-v2-scope .mh-cmp-row .vs-sep {
  font-size: 11px; font-weight: 800; color: var(--text-faint);
  text-transform: uppercase;
  align-self: center;
}
.cerr-v2-scope .mh-cmp-row .unit {
  font-size: 11.5px; font-weight: 600; color: var(--text-soft);
  align-self: center;
}
.cerr-v2-scope .mh-cmp-row .dir {
  margin-left: auto;
  font-size: 11px; font-weight: 700;
  padding: 2px 9px; border-radius: 6px;
  background: var(--n-50);
  color: var(--text-muted);
  letter-spacing: 0.01em;
  align-self: center;
}

/* Percentile bar */
.cerr-v2-scope .mh-cmp-row .pct-bar {
  height: 6px;
  border-radius: 999px;
  background: var(--n-100);
  overflow: hidden;
  margin-left: 68px;
  margin-top: 2px;
}
.cerr-v2-scope .mh-cmp-row .pct-bar i {
  display: block; height: 100%;
  border-radius: 999px;
  transition: width .25s ease;
}
.cerr-v2-scope .mh-cmp-row .pct-bar.pos i {
  background: linear-gradient(90deg, var(--pos-500), var(--pos-600));
}
.cerr-v2-scope .mh-cmp-row .pct-bar.neg i {
  background: linear-gradient(90deg, var(--neg-500), #b91c1c);
}

@media (max-width: 720px) {
  .cerr-v2-scope .mh-cmp-row .row-vals { padding-left: 0; }
  .cerr-v2-scope .mh-cmp-row .pct-bar { margin-left: 0; }
  .cerr-v2-scope .mh-cmp-row .dir { margin-left: 0; }
}
</style>
