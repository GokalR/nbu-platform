<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: String, required: true },
  percent: { type: Number, required: true },
  color: { type: String, default: 'bg-primary' },
})
</script>

<template>
  <div class="space-y-1">
    <div class="flex justify-between text-xs font-semibold mb-1">
      <span class="text-on-surface">{{ label }}</span>
      <span class="text-on-surface-variant">{{ value }}</span>
    </div>
    <div class="h-3 w-full bg-surface-container rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-[width] duration-700 ease-out"
        :class="color"
        :style="{ width: `${percent}%` }"
        role="progressbar"
        :aria-valuenow="percent"
        aria-valuemin="0"
        aria-valuemax="100"
      ></div>
    </div>
  </div>
</template>
