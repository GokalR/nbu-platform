<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import StepPinfl from '@/components/smeProfile/StepPinfl.vue'
import StepCategory from '@/components/smeProfile/StepCategory.vue'
import StepQuestions from '@/components/smeProfile/StepQuestions.vue'
import StepSummary from '@/components/smeProfile/StepSummary.vue'
import StepSuccess from '@/components/smeProfile/StepSuccess.vue'
import { smeProfileApi } from '@/services/smeProfileApi'

const { t, locale } = useI18n()
const router = useRouter()

const step = ref('pinfl')
const pinflInn = ref('')
const clientInfo = ref(null)
const sphereCount = ref(1)
const currentSphereIdx = ref(0)
const spheres = ref([])

const categories = ref([])
const loading = ref(true)
const fetchError = ref('')

const submitting = ref(false)
const submitError = ref('')

onMounted(async () => {
  const res = await smeProfileApi.fetchQuestions()
  loading.value = false
  if (!res.ok) {
    fetchError.value =
      res.reason === 'no-backend' ? t('smeProfile.errors.noBackend') : t('smeProfile.errors.backend')
    return
  }
  categories.value = res.data.categories || []
})

function onPinflNext({ pinflInn: p, clientInfo: ci, sphereCount: c }) {
  pinflInn.value = p
  clientInfo.value = ci
  sphereCount.value = c
  spheres.value = []
  currentSphereIdx.value = 0
  step.value = 'category'
}

function onCategoryNext({ id, nameRu, nameUz }) {
  const updated = [...spheres.value]
  updated[currentSphereIdx.value] = {
    sphere_number: currentSphereIdx.value + 1,
    category_id: id,
    category_name_ru: nameRu,
    category_name_uz: nameUz,
    answers: updated[currentSphereIdx.value]?.answers ?? [],
  }
  spheres.value = updated
  step.value = 'questions'
}

function onQuestionsNext({ answers }) {
  const updated = [...spheres.value]
  updated[currentSphereIdx.value] = { ...updated[currentSphereIdx.value], answers }
  spheres.value = updated
  if (currentSphereIdx.value < sphereCount.value - 1) {
    currentSphereIdx.value++
    step.value = 'category'
  } else {
    step.value = 'summary'
  }
}

function onBack() {
  if (step.value === 'category') {
    if (currentSphereIdx.value === 0) {
      step.value = 'pinfl'
    } else {
      currentSphereIdx.value--
      step.value = 'questions'
    }
    return
  }
  if (step.value === 'questions') {
    step.value = 'category'
    return
  }
  if (step.value === 'summary') {
    currentSphereIdx.value = sphereCount.value - 1
    step.value = 'questions'
  }
}

async function onSubmit() {
  submitting.value = true
  submitError.value = ''
  const res = await smeProfileApi.submit({
    pinfl_or_inn: pinflInn.value,
    sphere_count: sphereCount.value,
    spheres: spheres.value,
    client_info: clientInfo.value || undefined,
  })
  submitting.value = false
  if (!res.ok) {
    submitError.value =
      res.reason === 'no-backend' ? t('smeProfile.errors.noBackend') : res.error || t('smeProfile.errors.backend')
    return
  }
  step.value = 'success'
}

function onRestart() {
  pinflInn.value = ''
  clientInfo.value = null
  sphereCount.value = 1
  currentSphereIdx.value = 0
  spheres.value = []
  submitError.value = ''
  step.value = 'pinfl'
}

const totalSteps = computed(() => 1 + sphereCount.value * 2 + 1)
const currentStepNum = computed(() => {
  if (step.value === 'pinfl') return 1
  if (step.value === 'category') return 2 + currentSphereIdx.value * 2
  if (step.value === 'questions') return 3 + currentSphereIdx.value * 2
  return totalSteps.value
})
const stepLabel = computed(() => {
  if (step.value === 'pinfl') return t('smeProfile.steps.pinfl')
  if (step.value === 'category')
    return `${t('smeProfile.steps.category')} ${currentSphereIdx.value + 1}/${sphereCount.value}`
  if (step.value === 'questions')
    return `${t('smeProfile.steps.questions')} ${currentSphereIdx.value + 1}/${sphereCount.value}`
  if (step.value === 'summary') return t('smeProfile.steps.summary')
  return t('smeProfile.steps.success')
})

const currentCategory = computed(() => {
  const s = spheres.value[currentSphereIdx.value]
  if (!s) return null
  return categories.value.find((c) => c.id === s.category_id) || null
})

function exitWizard() {
  if (confirm(t('smeProfile.exitConfirm'))) router.push('/tools')
}
</script>

<template>
  <div class="min-h-screen bg-surface flex flex-col">
    <!-- Top bar -->
    <header class="flex items-center gap-4 px-5 py-4 bg-white border-b border-outline-variant">
      <button
        class="w-10 h-10 inline-flex items-center justify-center rounded-btn border border-outline-variant text-on-surface hover:bg-surface-container transition-colors"
        :title="t('smeProfile.exit')"
        @click="exitWizard"
      >
        <AppIcon name="close" />
      </button>
      <div class="flex items-center gap-3 flex-1">
        <img src="/nbu_logo.png" alt="NBU" class="w-9 h-9 object-contain" />
        <div>
          <div class="text-sm font-bold text-on-surface">{{ t('smeProfile.title') }}</div>
          <div class="text-xs text-on-surface-variant">{{ t('smeProfile.subtitle') }}</div>
        </div>
      </div>
      <div class="flex gap-1">
        <button
          class="px-3 py-1.5 rounded-btn text-xs font-bold border transition-colors"
          :class="locale === 'uz' ? 'bg-primary text-white border-primary' : 'bg-transparent text-on-surface-variant border-outline-variant'"
          @click="locale = 'uz'"
        >UZ</button>
        <button
          class="px-3 py-1.5 rounded-btn text-xs font-bold border transition-colors"
          :class="locale === 'ru' ? 'bg-primary text-white border-primary' : 'bg-transparent text-on-surface-variant border-outline-variant'"
          @click="locale = 'ru'"
        >RU</button>
      </div>
    </header>

    <!-- Progress -->
    <div class="bg-white px-5 pt-3 pb-4 border-b border-outline-variant">
      <div class="h-1.5 bg-surface-container rounded-full overflow-hidden">
        <div
          class="h-full bg-primary transition-all duration-300"
          :style="{ width: `${(currentStepNum / totalSteps) * 100}%` }"
        />
      </div>
      <div class="flex justify-between items-center mt-2 text-xs text-on-surface-variant">
        <span>{{ stepLabel }}</span>
        <span>{{ currentStepNum }} / {{ totalSteps }}</span>
      </div>
    </div>

    <!-- Main content -->
    <main class="flex-1 px-4 py-6 lg:py-8">
      <div class="max-w-3xl mx-auto">
        <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-4">
          <div class="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p class="text-sm text-on-surface-variant">{{ t('smeProfile.loading') }}</p>
        </div>

        <div
          v-else-if="fetchError"
          class="bg-red-50 border border-red-200 rounded-card p-8 text-center"
        >
          <p class="text-base font-semibold text-error">{{ fetchError }}</p>
        </div>

        <template v-else>
          <StepPinfl
            v-if="step === 'pinfl'"
            :initial-value="pinflInn"
            :initial-client-info="clientInfo"
            :initial-sphere-count="sphereCount"
            @next="onPinflNext"
          />
          <StepCategory
            v-else-if="step === 'category'"
            :categories="categories"
            :sphere-idx="currentSphereIdx"
            :sphere-count="sphereCount"
            :selected-id="spheres[currentSphereIdx]?.category_id || ''"
            @next="onCategoryNext"
            @back="onBack"
          />
          <StepQuestions
            v-else-if="step === 'questions' && currentCategory"
            :category="currentCategory"
            :sphere-idx="currentSphereIdx"
            :sphere-count="sphereCount"
            :initial-answers="spheres[currentSphereIdx]?.answers || []"
            @next="onQuestionsNext"
            @back="onBack"
          />
          <StepSummary
            v-else-if="step === 'summary'"
            :pinfl-inn="pinflInn"
            :client-info="clientInfo"
            :sphere-count="sphereCount"
            :spheres="spheres"
            :submitting="submitting"
            :submit-error="submitError"
            @back="onBack"
            @submit="onSubmit"
          />
          <StepSuccess
            v-else-if="step === 'success'"
            :pinfl-inn="pinflInn"
            :client-info="clientInfo"
            :sphere-count="sphereCount"
            :spheres="spheres"
            @restart="onRestart"
          />
        </template>
      </div>
    </main>
  </div>
</template>
