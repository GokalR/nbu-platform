<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { rsScoreColor } from './rs-utils'

const props = defineProps({
  label: { type: String, required: true },
  score: { type: Number, required: true },
  description: { type: String, default: '' },
  improvements: { type: Array, default: () => [] },
})

const animated = ref(0)
const color = computed(() => rsScoreColor(props.score))
onMounted(() => setTimeout(() => { animated.value = props.score }, 50))
watch(() => props.score, (v) => setTimeout(() => { animated.value = v }, 50))
</script>

<template>
  <div class="bg-white border border-rs-border rounded-card shadow-rs-card p-5">
    <div class="flex items-center justify-between mb-2">
      <div class="text-[14px] font-semibold text-carbon">{{ label }}</div>
      <div class="font-mono text-[16px] font-bold tabular-nums" :style="{ color }">{{ score }}</div>
    </div>
    <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full"
        :style="{ width: animated + '%', background: color, transition: 'width 800ms cubic-bezier(0.4,0,0.2,1)' }"
      />
    </div>
    <p class="text-[13px] font-medium text-[#898989] mt-2 leading-[1.6]">{{ description }}</p>
    <ul v-if="improvements && improvements.length" class="mt-3 space-y-1">
      <li v-for="(imp, i) in improvements" :key="i" class="flex items-start gap-2 text-[12px] font-medium text-carbon">
        <span class="text-gold-500 mt-[1px] leading-none">•</span>
        <span>{{ imp }}</span>
      </li>
    </ul>
  </div>
</template>
