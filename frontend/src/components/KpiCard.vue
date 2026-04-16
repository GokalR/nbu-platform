<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  icon: { type: String, required: true },
  value: { type: String, required: true },
  label: { type: String, required: true },
  delta: { type: String, default: '' },
  tone: { type: String, default: 'positive' }, // positive | neutral | negative
})

const toneClass = {
  positive: 'text-tertiary',
  neutral: 'text-on-surface-variant',
  negative: 'text-error',
}
</script>

<template>
  <article
    class="bg-surface-container-lowest p-6 rounded-xl transition-all hover:-translate-y-1 hover:shadow-md"
  >
    <div class="flex items-center justify-between mb-4">
      <AppIcon :name="icon" filled class="text-primary text-3xl" />
      <span v-if="delta" class="font-bold text-xs" :class="toneClass[tone]">{{ delta }}</span>
    </div>
    <div class="display-lg text-4xl font-extrabold text-on-surface mb-1">{{ value }}</div>
    <div class="text-on-surface-variant text-sm font-semibold tracking-wide uppercase">
      {{ label }}
    </div>
  </article>
</template>
