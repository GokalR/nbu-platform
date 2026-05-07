<script setup>
import { computed } from 'vue'

const props = defineProps({
  color: { type: String, default: 'gold' }, // gold | navy
})

const borderColor = computed(() => (props.color === 'gold' ? '#D7B56D' : '#193F72'))
const textClass = computed(() => (props.color === 'gold' ? 'text-gold-500' : 'text-navy-900'))
</script>

<template>
  <div
    class="pl-3 text-[12px] font-bold uppercase tracking-[1px]"
    :class="textClass"
    :style="{ borderLeft: `3px solid ${borderColor}` }"
  >
    <slot />
  </div>
</template>
