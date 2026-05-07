<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'neutral' }, // positive|negative|warning|info|neutral
})

const VARIANTS = {
  positive: 'bg-green-50 text-green-600',
  negative: 'bg-red-50 text-red-600',
  warning: 'bg-amber-50 text-amber-600',
  info: 'bg-blue-50 text-navy-700',
  neutral: 'bg-gray-100 text-gray-600',
}
const cls = computed(() => VARIANTS[props.variant] || VARIANTS.neutral)
</script>

<template>
  <span
    class="inline-flex items-center font-semibold text-[11px] tracking-[0.3px] rounded-tag py-1 px-[10px]"
    :class="cls"
  >
    <slot />
  </span>
</template>
