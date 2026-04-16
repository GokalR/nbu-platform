<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { rsScoreColor } from './rs-utils'

const props = defineProps({
  score: { type: Number, required: true },
  size: { type: String, default: 'md' }, // sm | md | lg
  label: { type: String, default: '' },
})

const SIZE_MAP = {
  sm: { px: 48, stroke: 4, font: 14 },
  md: { px: 72, stroke: 6, font: 20 },
  lg: { px: 96, stroke: 8, font: 28 },
}

const dim = computed(() => SIZE_MAP[props.size] || SIZE_MAP.md)
const radius = computed(() => (dim.value.px - dim.value.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const color = computed(() => rsScoreColor(props.score))

const animated = ref(0)
const offset = computed(
  () => circumference.value - (animated.value / 100) * circumference.value,
)

onMounted(() => {
  setTimeout(() => { animated.value = props.score }, 50)
})
watch(() => props.score, (v) => {
  setTimeout(() => { animated.value = v }, 50)
})
</script>

<template>
  <div class="inline-flex flex-col items-center gap-2">
    <div class="relative" :style="{ width: dim.px + 'px', height: dim.px + 'px' }">
      <svg :width="dim.px" :height="dim.px" class="-rotate-90" aria-hidden="true">
        <circle
          :cx="dim.px / 2" :cy="dim.px / 2" :r="radius"
          :stroke-width="dim.stroke" stroke="#F1F2F7" fill="none"
        />
        <circle
          :cx="dim.px / 2" :cy="dim.px / 2" :r="radius"
          :stroke-width="dim.stroke" :stroke="color" fill="none"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="offset"
          style="transition: stroke-dashoffset 800ms cubic-bezier(0.4,0,0.2,1)"
        />
      </svg>
      <div
        class="absolute inset-0 flex items-center justify-center font-mono font-bold text-carbon"
        :style="{ fontSize: dim.font + 'px', letterSpacing: '-0.5px' }"
      >
        {{ score }}
      </div>
    </div>
    <div v-if="label" class="font-semibold uppercase text-steel-500 text-[11px] tracking-[0.8px]">
      {{ label }}
    </div>
  </div>
</template>
