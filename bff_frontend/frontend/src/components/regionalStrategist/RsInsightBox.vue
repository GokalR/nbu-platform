<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'info' }, // info|warning|danger|success
  title: { type: String, default: '' },
})

const STYLES = {
  info: { bg: 'bg-[rgba(239,246,255,0.5)]', border: 'border-l-navy-700', title: 'text-navy-900' },
  warning: { bg: 'bg-[rgba(255,251,235,0.5)]', border: 'border-l-amber-600', title: 'text-[#92400E]' },
  danger: { bg: 'bg-[rgba(254,242,242,0.5)]', border: 'border-l-red-600', title: 'text-[#991B1B]' },
  success: { bg: 'bg-[rgba(236,253,245,0.5)]', border: 'border-l-green-600', title: 'text-[#065F46]' },
}
const s = computed(() => STYLES[props.variant] || STYLES.info)
</script>

<template>
  <div class="border-l-[3px] rounded-r-[8px] py-3 px-4" :class="[s.bg, s.border]">
    <div v-if="title" class="text-[13px] font-bold mb-1" :class="s.title">{{ title }}</div>
    <div class="text-[13px] font-medium text-carbon leading-[1.6]">
      <slot />
    </div>
  </div>
</template>
