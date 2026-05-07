<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true },
  color: { type: String, default: '#0054A6' },
  fill: { type: Boolean, default: true },
  height: { type: Number, default: 40 },
})

const path = computed(() => {
  const n = props.data.length
  if (!n) return ''
  const min = Math.min(...props.data)
  const max = Math.max(...props.data)
  const range = max - min || 1
  const w = 100
  const h = props.height
  const pts = props.data.map((v, i) => {
    const x = (i / (n - 1)) * w
    const y = h - ((v - min) / range) * (h - 4) - 2
    return [x, y]
  })
  return pts.map(([x, y], i) => (i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`)).join(' ')
})

const fillPath = computed(() => {
  if (!props.fill) return ''
  return `${path.value} L 100 ${props.height} L 0 ${props.height} Z`
})

const gradId = computed(() => `spark-${Math.random().toString(36).slice(2, 8)}`)
</script>

<template>
  <svg
    class="fc-spark"
    :viewBox="`0 0 100 ${height}`"
    preserveAspectRatio="none"
  >
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="0.35" />
        <stop offset="100%" :stop-color="color" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path v-if="fill" :d="fillPath" :fill="`url(#${gradId})`" />
    <path :d="path" fill="none" :stroke="color" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round" />
  </svg>
</template>
