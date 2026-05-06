<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

// CERR-style KPI tile: 56px icon column, label (uppercase muted), big tabular value,
// optional delta pill. Lives inside .regions-v2 scope so the .kpi / .delta classes
// are available.
const props = defineProps({
  kpi: { type: Object, required: true },
})

const ICON_BY_KEY = {
  population: 'people',
  active_businesses: 'storefront',
  unemployed: 'work_off',
  rating_score: 'leaderboard',
  problem_loans: 'warning',
  area: 'crop_landscape',
}

const display = computed(() => {
  const v = props.kpi.value
  if (v === null || v === undefined) return '—'
  if (typeof v !== 'number') return String(v)
  const fmt = props.kpi.format || 'raw'
  if (fmt === 'percent') return `${v.toFixed(1)}%`
  if (fmt === 'currency') {
    if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
    if (Math.abs(v) >= 1_000) return `${(v / 1_000).toFixed(1)}K`
    return v.toLocaleString('ru-RU')
  }
  return Math.round(v).toLocaleString('ru-RU')
})

const tone = computed(() => {
  switch (props.kpi.direction) {
    case 'up': return 'tone-up'
    case 'down': return 'tone-down'
    default: return 'tone-neu'
  }
})

const icon = computed(() => ICON_BY_KEY[props.kpi.key] || 'analytics')

const deltaPill = computed(() => {
  const c = props.kpi.change_pct
  if (c === null || c === undefined) return null
  const sign = c >= 0 ? 'up' : 'down'
  return { sign, text: `${c >= 0 ? '+' : ''}${c.toFixed(1)}%` }
})
</script>

<template>
  <div class="kpi">
    <div class="kpi-icon" :class="tone">
      <AppIcon :name="icon" />
    </div>
    <div class="kpi-body">
      <div class="kpi-label">{{ kpi.label }}</div>
      <div class="kpi-value">{{ display }}</div>
      <div v-if="deltaPill" class="kpi-foot">
        <span class="delta" :class="deltaPill.sign">
          <AppIcon :name="deltaPill.sign === 'up' ? 'trending_up' : 'trending_down'" class="!text-xs" />
          {{ deltaPill.text }}
        </span>
      </div>
    </div>
  </div>
</template>
