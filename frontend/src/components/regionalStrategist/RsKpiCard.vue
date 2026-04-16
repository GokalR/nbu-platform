<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: String, required: true },
  subtitle: { type: String, default: '' },
  trend: { type: Object, default: null }, // { direction: 'up'|'down'|'flat', value: string }
  status: { type: String, default: 'neutral' }, // positive|negative|info|neutral
})

const TOP_BORDER = {
  positive: 'border-t-green-600',
  negative: 'border-t-red-600',
  info: 'border-t-gold-500',
  neutral: 'border-t-navy-700',
}
const topBorder = computed(() => TOP_BORDER[props.status] || TOP_BORDER.neutral)

const trendClass = computed(() => {
  if (!props.trend) return ''
  if (props.trend.direction === 'up') return 'bg-green-50 text-green-600'
  if (props.trend.direction === 'down') return 'bg-red-50 text-red-600'
  return 'bg-gray-100 text-gray-600'
})
const trendMark = computed(() => {
  if (!props.trend) return ''
  if (props.trend.direction === 'up') return '▲'
  if (props.trend.direction === 'down') return '▼'
  return ''
})
</script>

<template>
  <div
    class="bg-white border border-rs-border rounded-card shadow-rs-card transition-[box-shadow,border-color] duration-200 ease-out hover:shadow-rs-card-hover hover:border-navy-900/15 border-t-[2.5px] py-4 px-5"
    :class="topBorder"
  >
    <div class="flex items-start justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="font-semibold uppercase text-steel-500 text-[11px] tracking-[0.8px] mb-1">{{ label }}</div>
        <div class="font-mono font-bold text-carbon text-[28px] leading-[1.1] tracking-[-0.5px]">{{ value }}</div>
        <div v-if="subtitle" class="font-medium text-[#898989] text-[12px] mt-1">{{ subtitle }}</div>
      </div>
      <span v-if="trend" class="inline-flex items-center font-semibold text-[11px] tracking-[0.3px] rounded-tag py-[3px] px-2 whitespace-nowrap" :class="trendClass">
        {{ trendMark }} {{ trend.value }}
      </span>
    </div>
  </div>
</template>
