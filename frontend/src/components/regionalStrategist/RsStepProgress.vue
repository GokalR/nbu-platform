<script setup>
import RsIcon from './RsIcon.vue'

defineProps({
  steps: { type: Array, required: true }, // [{ label, status: 'completed'|'active'|'upcoming' }]
  percentage: { type: Number, default: 0 },
})
</script>

<template>
  <div class="w-full">
    <div class="flex justify-end mb-2">
      <span class="font-mono text-[13px] font-semibold text-carbon">{{ percentage }}%</span>
    </div>
    <div class="w-full h-1 bg-gray-100 rounded-full overflow-hidden mb-6">
      <div
        class="h-full bg-gold-500 rounded-full"
        :style="{ width: percentage + '%', transition: 'width 600ms cubic-bezier(0.4,0,0.2,1)' }"
      />
    </div>
    <div class="flex items-start gap-3">
      <div v-for="(step, i) in steps" :key="i" class="flex-1 flex flex-col items-center gap-2">
        <div
          class="inline-flex items-center gap-2 rounded-full py-2 px-4 min-w-[140px] justify-center transition-colors duration-200"
          :class="[
            step.status === 'completed' && 'bg-navy-900 text-white',
            step.status === 'active' && 'bg-white border-2 border-gold-500 text-navy-900',
            step.status === 'upcoming' && 'bg-gray-100 text-steel-500',
          ]"
        >
          <span
            class="w-5 h-5 rounded-full flex items-center justify-center font-mono text-[11px] font-bold shrink-0"
            :class="[
              step.status === 'completed' && 'bg-white/20 text-white',
              step.status === 'active' && 'bg-gold-500 text-white',
              step.status === 'upcoming' && 'bg-white text-steel-500',
            ]"
          >
            <RsIcon v-if="step.status === 'completed'" name="check" :size="12" :stroke-width="3" />
            <template v-else>{{ i + 1 }}</template>
          </span>
          <span class="text-[13px] font-medium">{{ step.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
