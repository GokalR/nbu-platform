<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRsLang } from '@/composables/useRsLang'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'

const emit = defineEmits(['back', 'complete'])
const { lang } = useRsLang()

const T = {
  ru: {
    title: 'AI анализ выполняется',
    sub: 'Ваши данные обрабатываются — подождите немного',
    back: 'Вернуться к рекомендациям',
  },
  uz: {
    title: 'AI tahlil bajarilmoqda',
    sub: 'Maʻlumotlaringiz qayta ishlanmoqda — bir oz kuting',
    back: 'Tavsiyalarga qaytish',
  },
}

const CRITERIA = {
  ru: [
    { label: 'Личный профиль', threshold: 15 },
    { label: 'Региональный рынок', threshold: 30 },
    { label: 'Финансовые возможности', threshold: 45 },
    { label: 'Бизнес-модель', threshold: 60 },
    { label: 'Анализ конкуренции', threshold: 78 },
    { label: 'Бизнес-план', threshold: 95 },
  ],
  uz: [
    { label: 'Shaxsiy profil', threshold: 15 },
    { label: 'Mintaqaviy bozor', threshold: 30 },
    { label: 'Moliyaviy imkoniyatlar', threshold: 45 },
    { label: 'Biznes-model', threshold: 60 },
    { label: 'Raqobat tahlili', threshold: 78 },
    { label: 'Biznes-plan', threshold: 95 },
  ],
}

const DURATION_MS = 8000
const STEP_MS = 80
const FINALIZE_DELAY_MS = 500

const t = computed(() => T[lang.value])
const criteria = computed(() => CRITERIA[lang.value])

const percent = ref(0)
const finalizing = ref(false)
const displayPercent = computed(() => Math.min(100, Math.round(percent.value)))
let tickId = null
let finalizeTimer = null

onMounted(() => {
  tickId = setInterval(() => {
    percent.value = Math.min(100, percent.value + 100 / (DURATION_MS / STEP_MS))
  }, STEP_MS)
})

watch(percent, (p) => {
  if (p < 100) return
  if (tickId) { clearInterval(tickId); tickId = null }
  finalizing.value = true
  finalizeTimer = setTimeout(() => emit('complete'), FINALIZE_DELAY_MS)
})

onBeforeUnmount(() => {
  if (tickId) clearInterval(tickId)
  if (finalizeTimer) clearTimeout(finalizeTimer)
})
</script>

<template>
  <div class="flex flex-col items-center">
    <div
      :class="[
        'w-full bg-white border border-rs-border rounded-[16px] py-10 md:py-12 px-6 md:px-12 animate-rs-fade-in-up',
        'shadow-[0_2px_8px_rgba(0,0,0,0.06)] transition-opacity duration-300',
        finalizing && 'opacity-85',
      ]"
    >
      <div class="flex justify-center">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 rounded-full border-2 border-navy-900 opacity-10 animate-rs-pulse-outer" />
          <div class="absolute inset-2 rounded-full border-2 border-gold-500 opacity-20 animate-rs-pulse-middle" />
          <div class="absolute inset-4 rounded-full bg-gold-500 opacity-[0.15] animate-rs-pulse-inner" />
          <div class="absolute inset-0 flex items-center justify-center">
            <RsIcon name="brain" :size="24" :stroke-width="2" class="text-navy-900 animate-rs-slow-spin" />
          </div>
        </div>
      </div>

      <h1 class="text-[20px] md:text-[24px] font-bold text-carbon text-center mt-7">{{ t.title }}</h1>
      <p class="text-[14px] md:text-[15px] text-[#898989] text-center mt-2">{{ t.sub }}</p>

      <div class="flex items-center gap-4 mt-8">
        <div class="flex-1 h-[6px] bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full"
            :style="{
              width: `${displayPercent}%`,
              transition: `width ${STEP_MS}ms linear`,
              background: 'linear-gradient(90deg, #193F72, #D7B56D)',
            }"
          />
        </div>
        <span class="font-mono text-[13px] font-semibold text-gold-500 tabular-nums w-10 text-right">
          {{ displayPercent }}%
        </span>
      </div>

      <div class="grid grid-cols-3 md:grid-cols-6 gap-2 mt-10">
        <div v-for="(criterion, i) in criteria" :key="criterion.label" class="flex flex-col items-center gap-2">
          <div
            :class="[
              'w-10 h-10 rounded-full flex items-center justify-center transition-colors duration-300',
              displayPercent >= criterion.threshold
                ? 'bg-green-600 text-white'
                : (i === 0 ? true : displayPercent >= criteria[i - 1].threshold)
                  ? 'bg-gold-500 text-white animate-rs-subtle-pulse'
                  : 'bg-gray-100 text-steel-500',
            ]"
          >
            <span v-if="displayPercent >= criterion.threshold" class="animate-rs-pop-in inline-flex items-center justify-center">
              <RsIcon name="check" :size="18" :stroke-width="3" />
            </span>
            <span v-else class="font-mono text-[13px] font-bold">{{ i + 1 }}</span>
          </div>
          <span
            :class="[
              'text-[11px] font-medium text-center leading-[1.3] max-w-[72px] transition-colors duration-300',
              displayPercent >= criterion.threshold ? 'text-green-600' : 'text-steel-500',
            ]"
          >
            {{ criterion.label }}
          </span>
        </div>
      </div>
    </div>

    <button
      type="button" @click="emit('back')"
      class="mt-6 inline-flex items-center text-[14px] font-medium text-navy-700 hover:bg-navy-900/[0.04] rounded-[8px] py-2 px-3 transition-colors duration-150"
    >
      <RsIcon name="arrow-left" :size="16" class="mr-1" />
      {{ t.back }}
    </button>
  </div>
</template>
