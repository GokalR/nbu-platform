<script setup>
/* Mahalla overview tab — AI insights + top peer comparison.
 * The page hero (MahallaView) already shows title, breadcrumb, rating, and
 * KPI strip, so we don't repeat those here. */
import { computed } from 'vue'
import CerrIcon from './CerrIcon.vue'

const props = defineProps({
  m: { type: Object, required: true },
  rating: { type: Object, default: null },
})

const ai = computed(() => {
  const a = props.m?.ai_insights
  if (!a || (!a.pros?.length && !a.cons?.length)) return null
  return a
})
const peerSet = computed(() => props.m?.peer_profile?.peer_set || null)
const topStrength = computed(() => props.m?.peer_profile?.strengths?.[0] || null)
const topWeakness = computed(() => props.m?.peer_profile?.weaknesses?.[0] || null)
</script>

<template>
  <!-- AI insights — split pros/cons in two columns -->
  <section v-if="ai" class="card mh-ai-card">
    <header class="mh-ai-head">
      <div class="mh-ai-stamp">
        <CerrIcon name="brain" :size="14" />
        <span>AI Анализ</span>
      </div>
    </header>
    <div class="mh-ai-cols">
      <div v-if="ai.pros?.length" class="mh-ai-col">
        <div class="mh-ai-col-h pos">
          <CerrIcon name="check" :size="12" />
          <span>Сильные стороны</span>
          <span class="ct">{{ ai.pros.length }}</span>
        </div>
        <ul class="mh-ai-list">
          <li v-for="(p, i) in ai.pros" :key="`p-${i}`" class="mh-ai-li pos">{{ p }}</li>
        </ul>
      </div>
      <div v-if="ai.cons?.length" class="mh-ai-col">
        <div class="mh-ai-col-h neg">
          <CerrIcon name="warn" :size="12" />
          <span>Проблемы</span>
          <span class="ct">{{ ai.cons.length }}</span>
        </div>
        <ul class="mh-ai-list">
          <li v-for="(p, i) in ai.cons" :key="`c-${i}`" class="mh-ai-li neg">{{ p }}</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- Top peer comparison — featured highlight + lowlight -->
  <section v-if="topStrength || topWeakness" class="card">
    <h3 class="card-title">
      <span class="ico-tile"><CerrIcon name="target" :size="14" /></span>
      Сравнение с пир-группой
      <span v-if="peerSet" class="card-title-end">{{ peerSet.description }}</span>
    </h3>
    <div class="mh-peer-grid">
      <div v-if="topStrength" class="mh-peer-card pos">
        <div class="mh-peer-tag">
          <CerrIcon name="check" :size="11" />
          <span>Топ перцентиль</span>
        </div>
        <div class="mh-peer-label">{{ topStrength.label }}</div>
        <div class="mh-peer-row">
          <span class="mh-peer-val tabular">{{ topStrength.this_value }}</span>
          <span class="mh-peer-vs">
            vs ср. {{ Number(topStrength.district_avg).toFixed(2) }} {{ topStrength.unit }}
          </span>
          <span class="mh-peer-rk">#{{ topStrength.peer_rank }}/{{ topStrength.peer_count }}</span>
        </div>
        <div class="mh-peer-bar">
          <i :style="{ width: `${topStrength.percentile}%` }" />
        </div>
        <div class="mh-peer-foot">
          <span>0</span>
          <span class="emp">перцентиль {{ Math.round(topStrength.percentile) }}</span>
          <span>100</span>
        </div>
      </div>
      <div v-if="topWeakness" class="mh-peer-card neg">
        <div class="mh-peer-tag">
          <CerrIcon name="warn" :size="11" />
          <span>Нижний перцентиль</span>
        </div>
        <div class="mh-peer-label">{{ topWeakness.label }}</div>
        <div class="mh-peer-row">
          <span class="mh-peer-val tabular">{{ topWeakness.this_value }}</span>
          <span class="mh-peer-vs">
            vs ср. {{ Number(topWeakness.district_avg).toFixed(2) }} {{ topWeakness.unit }}
          </span>
          <span class="mh-peer-rk">#{{ topWeakness.peer_rank }}/{{ topWeakness.peer_count }}</span>
        </div>
        <div class="mh-peer-bar">
          <i :style="{ width: `${topWeakness.percentile}%` }" />
        </div>
        <div class="mh-peer-foot">
          <span>0</span>
          <span class="emp">перцентиль {{ Math.round(topWeakness.percentile) }}</span>
          <span>100</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style>
/* AI card */
.cerr-v2-scope .mh-ai-card {
  padding: 20px 22px;
  border-radius: 14px;
}
.cerr-v2-scope .mh-ai-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 14px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.cerr-v2-scope .mh-ai-stamp {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(0, 84, 166, .12), rgba(33, 182, 206, .12));
  border: 1px solid rgba(0, 84, 166, .2);
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--brand-navy);
}
.cerr-v2-scope .mh-ai-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 22px;
}
.cerr-v2-scope .mh-ai-col-h {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.cerr-v2-scope .mh-ai-col-h.pos { color: var(--pos-700); }
.cerr-v2-scope .mh-ai-col-h.neg { color: var(--neg-700); }
.cerr-v2-scope .mh-ai-col-h .ct {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--n-100);
  color: var(--text-muted);
  letter-spacing: 0.02em;
}
.cerr-v2-scope .mh-ai-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.cerr-v2-scope .mh-ai-li {
  position: relative;
  padding: 10px 12px 10px 30px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.45;
  font-weight: 500;
  color: var(--text);
}
.cerr-v2-scope .mh-ai-li.pos {
  background: rgba(20, 163, 74, .06);
  border: 1px solid rgba(20, 163, 74, .14);
}
.cerr-v2-scope .mh-ai-li.neg {
  background: rgba(216, 56, 56, .06);
  border: 1px solid rgba(216, 56, 56, .14);
}
.cerr-v2-scope .mh-ai-li::before {
  content: "";
  position: absolute;
  left: 12px;
  top: 17px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.cerr-v2-scope .mh-ai-li.pos::before { background: var(--pos-500); }
.cerr-v2-scope .mh-ai-li.neg::before { background: var(--neg-500); }

/* Peer comparison cards */
.cerr-v2-scope .mh-peer-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.cerr-v2-scope .mh-peer-card {
  border-radius: 12px;
  padding: 14px 18px;
  border: 1px solid var(--border);
  background: var(--surface);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cerr-v2-scope .mh-peer-card.pos { border-left: 3px solid var(--pos-500); }
.cerr-v2-scope .mh-peer-card.neg { border-left: 3px solid var(--neg-500); }
.cerr-v2-scope .mh-peer-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  padding: 3px 9px;
  border-radius: 999px;
  width: fit-content;
}
.cerr-v2-scope .mh-peer-card.pos .mh-peer-tag { background: var(--pos-50); color: var(--pos-700); }
.cerr-v2-scope .mh-peer-card.neg .mh-peer-tag { background: var(--neg-50); color: var(--neg-700); }
.cerr-v2-scope .mh-peer-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
}
.cerr-v2-scope .mh-peer-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}
.cerr-v2-scope .mh-peer-val {
  font-size: 24px;
  font-weight: 900;
  letter-spacing: -.025em;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}
.cerr-v2-scope .mh-peer-vs {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-soft);
}
.cerr-v2-scope .mh-peer-rk {
  margin-left: auto;
  font-size: 11.5px;
  font-weight: 800;
  padding: 3px 9px;
  border-radius: 6px;
  background: var(--n-100);
  color: var(--text-muted);
}
.cerr-v2-scope .mh-peer-bar {
  height: 6px;
  border-radius: 3px;
  background: var(--n-100);
  overflow: hidden;
}
.cerr-v2-scope .mh-peer-card.pos .mh-peer-bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--pos-500), var(--pos-600)); }
.cerr-v2-scope .mh-peer-card.neg .mh-peer-bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--neg-500), #b91c1c); }
.cerr-v2-scope .mh-peer-foot {
  display: flex;
  justify-content: space-between;
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-faint);
  font-variant-numeric: tabular-nums;
}
.cerr-v2-scope .mh-peer-foot .emp {
  font-weight: 800;
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .cerr-v2-scope .mh-ai-cols { grid-template-columns: 1fr; }
  .cerr-v2-scope .mh-peer-grid { grid-template-columns: 1fr; }
}
</style>
