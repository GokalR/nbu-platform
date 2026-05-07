<script setup>
import { computed } from 'vue'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import { useRsLang } from '@/composables/useRsLang'
import RsHeader from '@/components/regionalStrategist/RsHeader.vue'
import RsStepProgress from '@/components/regionalStrategist/RsStepProgress.vue'
import RsStep0PathSelect from './steps/RsStep0PathSelect.vue'
import RsStep1Profile from './steps/RsStep1Profile.vue'
import RsStep2Finance from './steps/RsStep2Finance.vue'
import RsStep3Coaching from './steps/RsStep3Coaching.vue'
import RsStep4Analyzing from './steps/RsStep4Analyzing.vue'
import RsStep5Results from './steps/RsStep5Results.vue'

const store = useRegionalStrategistStore()
const { lang } = useRsLang()

const STEP_LABELS = {
  ru: ['Личный профиль', 'Финансовые вопросы', 'AI Рекомендации', 'AI Анализ', 'Результат'],
  uz: ['Shaxsiy maʻlumotlar', 'Moliyaviy savollar', 'AI Tavsiyalar', 'AI Tahlil', 'Natija'],
}
const STEP_PERCENTAGES = [20, 40, 60, 80, 100]

const labels = computed(() => STEP_LABELS[lang.value])
const steps = computed(() =>
  labels.value.map((label, i) => {
    const num = i + 1
    if (store.step === 5) return { label, status: 'completed' }
    const status =
      num < store.step ? 'completed' : num === store.step ? 'active' : 'upcoming'
    return { label, status }
  }),
)
const percentage = computed(() =>
  store.step >= 1 && store.step <= 5 ? STEP_PERCENTAGES[store.step - 1] : 0,
)

const containerWidth = computed(() => {
  if (store.step === 0) return 'max-w-[820px]'
  if (store.step === 5) return 'max-w-[1100px]'
  if (store.step === 4) return 'max-w-[640px]'
  if (store.step === 3) return 'max-w-[820px]'
  return 'max-w-[780px]'
})
</script>

<template>
  <div class="min-h-screen bg-[#F1F2F7]">
    <RsHeader active-nav="businessTest" />

    <main v-if="store.step > 0" class="max-w-[1100px] mx-auto px-6 md:px-10 pt-10">
      <RsStepProgress :steps="steps" :percentage="percentage" />
    </main>

    <div
      :class="[containerWidth, 'mx-auto px-4 md:px-6', store.step === 0 ? 'mt-16' : 'mt-8', 'mb-16']"
      :key="store.step"
    >
      <RsStep0PathSelect v-if="store.step === 0" @select="store.choosePath" />
      <RsStep1Profile
        v-else-if="store.step === 1"
        @back="store.goTo(0)"
        @next="store.goTo(2)"
      />
      <RsStep2Finance
        v-else-if="store.step === 2"
        @back="store.goTo(1)"
        @next="store.goTo(3)"
      />
      <RsStep3Coaching
        v-else-if="store.step === 3"
        @back="store.goTo(2)"
        @next="store.goTo(4)"
      />
      <RsStep4Analyzing
        v-else-if="store.step === 4"
        @back="store.goTo(3)"
        @complete="store.goTo(5)"
      />
      <RsStep5Results
        v-else-if="store.step === 5"
        @restart="store.reset"
      />
    </div>
  </div>
</template>
