<script setup>
/** District macro-indicator theme block. Sourced from district.macro.indicators[]
 *  grouped by macroThemes.js.  Sparkline dropped per Q2. */
import CerrIcon from './CerrIcon.vue'
import { fmt } from '@/data/cerrV2Format.js'

const props = defineProps({
  theme: { type: Object, required: true },
})

function tone(rank, total) {
  if (!rank || !total) return 'mid'
  const r = rank / total
  return r <= 0.25 ? 'good' : r <= 0.6 ? 'mid' : 'bad'
}
function indTone(t) { return t === 'good' ? 'var(--pos-500)' : t === 'mid' ? 'var(--warn-500)' : 'var(--neg-500)' }
function fmtVal(v) {
  if (v == null) return '—'
  if (typeof v === 'number') {
    if (Math.abs(v) >= 1000) return fmt.num(v)
    return v.toFixed(1).replace('.', ',')
  }
  return String(v)
}
function pctPos(rank, total) {
  if (!rank || !total) return 50
  return ((total - rank + 1) / total) * 100
}
</script>

<template>
  <div :class="['theme-block', `theme-${theme.id}`]">
    <div class="theme-head">
      <div class="theme-icon"><CerrIcon :name="theme.icon" :size="16" /></div>
      <div>
        <div class="theme-name">{{ theme.name }}</div>
        <div :style="{ fontSize: '11px', color: 'var(--text-soft)', fontWeight: 600 }">{{ theme.sub }}</div>
      </div>
    </div>

    <div v-if="theme.headline" class="headline-ind">
      <div class="left">
        <div :class="['rank-chip', tone(theme.headline.rank, theme.headline.total)]">
          #{{ theme.headline.rank ?? '—' }} из {{ theme.headline.total ?? '—' }}
        </div>
        <div class="lbl">{{ theme.headline.label }}</div>
        <div class="val tabular">
          {{ fmtVal(theme.headline.value) }}<span class="unit">{{ theme.headline.unit }}</span>
        </div>
      </div>
    </div>

    <div>
      <div v-for="(r, i) in theme.rows" :key="i" class="ind-row">
        <div class="nm">{{ r.label }}</div>
        <div class="v tabular">{{ fmtVal(r.value) }}<span class="u">{{ r.unit }}</span></div>
        <div class="pos-bar">
          <i :style="{ left: `${pctPos(r.rank, r.total) - 4}%`, background: indTone(tone(r.rank, r.total)) }" />
        </div>
      </div>
    </div>
  </div>
</template>
