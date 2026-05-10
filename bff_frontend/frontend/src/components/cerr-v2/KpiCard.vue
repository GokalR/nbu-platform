<script setup>
import { computed } from 'vue'
import CerrIcon from './CerrIcon.vue'
import { fmt, iconForKpi } from '@/data/cerrV2Format.js'

const props = defineProps({
  kpi: { type: Object, required: true },
  unit: { type: String, default: '' },
  foot: { type: String, default: '' },
})

const iconName = computed(() => props.kpi.icon || iconForKpi(props.kpi.key))
const delta = computed(() => fmt.delta(props.kpi))

/** Split the displayed value from its inline unit so they can be styled
 *  separately (big bold number + small subscript-y "млн" / "тыс" / etc.) */
const parts = computed(() => {
  const k = props.kpi
  if (k.value == null) return { value: '—', unit: props.unit || '' }
  if (k.format === 'index1') {
    return { value: Number(k.value).toFixed(1).replace('.', ','), unit: props.unit || '' }
  }
  if (k.format === 'thousands' && k.value > 1e5) {
    if (k.value >= 1e6) return { value: (k.value / 1e6).toFixed(2).replace('.', ','), unit: 'млн' }
    return { value: (k.value / 1e3).toFixed(1).replace('.', ','), unit: 'тыс' }
  }
  return { value: fmt.num(k.value), unit: props.unit || '' }
})

/** Tile accent — used for the icon chip background. Green for positive movement,
 *  red for negative, brand-blue for neutral structural counts. */
const accentColor = computed(() => {
  const k = props.kpi
  const d = delta.value
  if (d?.tone === 'pos') return '#14a34a'
  if (d?.tone === 'neg') return '#d83838'
  if (k.direction === 'up') return '#21b6ce'
  if (k.direction === 'down') return '#f59e0b'
  return '#3b7cc4'
})

const hasFoot = computed(() => !!props.foot || !!delta.value)
</script>

<template>
  <div class="kpi cerr-v2-kpi">
    <div class="kpi-head">
      <div
        class="kpi-icon"
        :style="{ background: `${accentColor}22`, color: accentColor }"
      ><CerrIcon :name="iconName" :size="13" /></div>
      <div class="kpi-label">{{ kpi.label }}</div>
    </div>
    <div class="kpi-val-row">
      <span class="kpi-val">{{ parts.value }}</span>
      <span v-if="parts.unit" class="kpi-unit-inline">{{ parts.unit }}</span>
    </div>
    <div v-if="hasFoot" class="kpi-foot">
      <div class="kpi-foot-text">{{ foot || ' ' }}</div>
      <span v-if="delta" :class="`delta ${delta.tone}`">{{ delta.text }}</span>
    </div>
  </div>
</template>

<style>
.cerr-v2-scope .cerr-v2-kpi {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  border-top: 0;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-head {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-direction: row;
  flex: 0;
  margin: 0;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: rgba(255,255,255,.10) !important;
  color: rgba(255,255,255,.85) !important;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-label {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255,255,255,.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-val-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-val {
  font-size: 38px;
  font-weight: 900;
  letter-spacing: -0.03em;
  color: #fff;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-unit-inline {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255,255,255,.5);
  letter-spacing: 0;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0;
  border-top: 0;
  gap: 8px;
  margin-top: -2px;
}
.cerr-v2-scope .cerr-v2-kpi .kpi-foot-text {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,.45);
}
</style>
