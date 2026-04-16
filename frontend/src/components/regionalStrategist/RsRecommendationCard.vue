<script setup>
import { computed, onMounted, ref } from 'vue'
import RsScoreRing from './RsScoreRing.vue'
import RsStatusTag from './RsStatusTag.vue'

const props = defineProps({
  rank: { type: Number, required: true },
  title: { type: String, required: true },
  score: { type: Number, required: true },
  metrics: { type: Array, default: () => [] }, // [{ label, value }]
  advantages: { type: Array, default: () => [] },
  risks: { type: Array, default: () => [] },
  recommendationLabel: { type: String, default: 'Рекомендация' },
  viewDetailsLabel: { type: String, default: 'Подробнее →' },
})

const animated = ref(false)
onMounted(() => setTimeout(() => { animated.value = true }, 80))

const rankBg = computed(() => {
  if (props.rank === 1) return 'bg-navy-900'
  if (props.rank === 2) return 'bg-navy-700'
  return 'bg-steel-500'
})
</script>

<template>
  <div class="bg-white border border-rs-border rounded-card shadow-rs-card transition-[box-shadow,border-color,transform] duration-200 ease-out hover:shadow-rs-card-raised hover:border-navy-900/15 hover:-translate-y-[1px] p-5">
    <div class="flex items-center gap-5">
      <div :class="['w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold text-white text-[14px] shrink-0', rankBg]">
        {{ rank }}
      </div>
      <RsScoreRing :score="score" size="md" />
      <div class="flex-1 min-w-0">
        <div class="flex items-baseline gap-3 mb-1">
          <h3 class="text-[18px] font-bold text-carbon leading-tight">{{ title }}</h3>
          <span class="text-[11px] font-semibold uppercase tracking-[0.8px] text-steel-500">
            {{ recommendationLabel }} #{{ rank }}
          </span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
          <div v-for="m in metrics" :key="m.label">
            <div class="flex items-center justify-between mb-[6px]">
              <span class="text-[11px] font-semibold uppercase tracking-[0.8px] text-steel-500">{{ m.label }}</span>
              <span class="font-mono text-[11px] font-semibold text-carbon">{{ m.value }}</span>
            </div>
            <div class="w-full h-[5px] bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-gold-500 rounded-full"
                :style="{ width: animated ? m.value + '%' : '0%', transition: 'width 600ms cubic-bezier(0.4,0,0.2,1)' }"
              />
            </div>
          </div>
        </div>
        <div class="flex flex-wrap gap-2 mt-4">
          <RsStatusTag v-for="(a, i) in advantages" :key="'adv'+i" variant="positive">{{ a }}</RsStatusTag>
          <RsStatusTag v-for="(r, i) in risks" :key="'risk'+i" variant="warning">{{ r }}</RsStatusTag>
        </div>
      </div>
      <button class="shrink-0 text-[14px] font-semibold text-navy-700 hover:bg-blue-50 rounded-[8px] py-2 px-3 transition-colors duration-200">
        {{ viewDetailsLabel }}
      </button>
    </div>
  </div>
</template>
