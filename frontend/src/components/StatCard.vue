<script setup>
import AppIcon from './AppIcon.vue'
import ProgressBar from './ProgressBar.vue'

defineProps({
  icon: { type: String, required: true },
  title: { type: String, required: true },
  bars: { type: Array, required: true }, // [{label, value, percent, color}]
})
</script>

<template>
  <article class="bg-surface-container-lowest p-8 rounded-xl shadow-sm space-y-6">
    <header class="flex items-center gap-3">
      <AppIcon :name="icon" class="text-primary" />
      <h3 class="text-lg font-bold">{{ title }}</h3>
    </header>
    <div class="space-y-4">
      <ProgressBar
        v-for="bar in bars"
        :key="bar.label"
        :label="bar.label"
        :value="bar.value"
        :percent="bar.percent"
        :color="bar.color"
      />
    </div>
  </article>
</template>
