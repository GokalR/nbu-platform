<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
  kpi: { type: Object, required: true },
})

// Format numeric values according to CERR's format hint:
//   "thousands" -> with thousands separators (RU/UZ both use space)
//   "raw"       -> integer with thousands separators
//   "percent"   -> "12.3%"
//   "currency"  -> "1.2M" / "120K" compact
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
  // raw / thousands — both use group separators
  return Math.round(v).toLocaleString('ru-RU')
})

const dirIcon = computed(() => {
  switch (props.kpi.direction) {
    case 'up':   return { icon: 'trending_up',   tone: 'text-emerald-600 bg-emerald-50' }
    case 'down': return { icon: 'trending_down', tone: 'text-rose-600 bg-rose-50' }
    default:     return { icon: 'remove',        tone: 'text-slate-400 bg-slate-50' }
  }
})
</script>

<template>
  <div class="rounded-xl bg-white border border-slate-200/70 p-4 hover:shadow-sm transition-shadow">
    <div class="flex items-start justify-between gap-2">
      <div class="text-xs font-medium text-slate-500 leading-snug">{{ kpi.label }}</div>
      <div
        v-if="kpi.direction"
        class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center"
        :class="dirIcon.tone"
      >
        <AppIcon :name="dirIcon.icon" class="!text-base" />
      </div>
    </div>
    <div class="mt-2 text-2xl font-black text-slate-900 tracking-tight">{{ display }}</div>
    <div
      v-if="kpi.change_pct !== null && kpi.change_pct !== undefined"
      class="mt-1 text-xs font-semibold"
      :class="kpi.change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'"
    >
      {{ kpi.change_pct >= 0 ? '+' : '' }}{{ kpi.change_pct.toFixed(1) }}%
    </div>
  </div>
</template>
