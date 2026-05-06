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

// Step machine: 'pinfl' | 'category' | 'questions' | 'summary' | 'success'
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
  <div class="sp-wizard">
    <header class="sp-topbar">
      <button class="sp-back" :title="t('smeProfile.exit')" @click="exitWizard">
        <AppIcon name="close" />
      </button>
      <div class="sp-brand">
        <img src="/nbu_logo.png" alt="NBU" />
        <div>
          <div class="sp-brand-title">{{ t('smeProfile.title') }}</div>
          <div class="sp-brand-sub">{{ t('smeProfile.subtitle') }}</div>
        </div>
      </div>
      <div class="sp-lang">
        <button :class="['sp-lang-btn', locale === 'uz' && 'is-active']" @click="locale = 'uz'">UZ</button>
        <button :class="['sp-lang-btn', locale === 'ru' && 'is-active']" @click="locale = 'ru'">RU</button>
      </div>
    </header>

    <div class="sp-progress">
      <div class="sp-progress-bar">
        <div
          class="sp-progress-fill"
          :style="{ width: `${(currentStepNum / totalSteps) * 100}%` }"
        />
      </div>
      <div class="sp-progress-label">
        <span>{{ stepLabel }}</span>
        <span>{{ currentStepNum }} / {{ totalSteps }}</span>
      </div>
    </div>

    <main class="sp-main">
      <div class="sp-content">
        <div v-if="loading" class="flex flex-col items-center justify-center py-24 gap-4">
          <div class="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p class="text-sm text-on-surface-variant">{{ t('smeProfile.loading') }}</p>
        </div>

        <div
          v-else-if="fetchError"
          class="bg-red-50 border border-red-200 rounded-xl p-8 text-center"
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

<style scoped>
.sp-wizard {
  min-height: 100vh;
  background: rgb(var(--md-sys-color-surface) / 1);
  display: flex;
  flex-direction: column;
}
.sp-topbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: white;
  border-bottom: 1px solid rgb(var(--md-sys-color-outline-variant) / 1);
}
.sp-back {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: transparent;
  border: 1px solid rgb(var(--md-sys-color-outline-variant) / 1);
  color: rgb(var(--md-sys-color-on-surface) / 1);
  cursor: pointer;
}
.sp-back:hover {
  background: rgb(var(--md-sys-color-surface-container) / 1);
}
.sp-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}
.sp-brand img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}
.sp-brand-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: rgb(var(--md-sys-color-on-surface) / 1);
}
.sp-brand-sub {
  font-size: 0.75rem;
  color: rgb(var(--md-sys-color-on-surface-variant) / 1);
}
.sp-lang {
  display: flex;
  gap: 0.25rem;
}
.sp-lang-btn {
  padding: 0.4rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  background: transparent;
  border: 1px solid rgb(var(--md-sys-color-outline-variant) / 1);
  color: rgb(var(--md-sys-color-on-surface-variant) / 1);
  cursor: pointer;
}
.sp-lang-btn.is-active {
  background: rgb(var(--md-sys-color-primary) / 1);
  color: white;
  border-color: rgb(var(--md-sys-color-primary) / 1);
}
.sp-progress {
  background: white;
  padding: 0.75rem 1.25rem 1rem;
  border-bottom: 1px solid rgb(var(--md-sys-color-outline-variant) / 1);
}
.sp-progress-bar {
  height: 6px;
  background: rgb(var(--md-sys-color-surface-container) / 1);
  border-radius: 999px;
  overflow: hidden;
}
.sp-progress-fill {
  height: 100%;
  background: rgb(var(--md-sys-color-primary) / 1);
  transition: width 0.25s;
}
.sp-progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: rgb(var(--md-sys-color-on-surface-variant) / 1);
}
.sp-main {
  flex: 1;
  padding: 1.5rem 1rem 3rem;
}
.sp-content {
  max-width: 760px;
  margin: 0 auto;
}
</style>
