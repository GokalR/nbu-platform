<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  questions: { type: Array, required: true },
  timeLimitSec: { type: Number, default: 1800 },
  passingScore: { type: Number, default: 70 },
})
const emit = defineEmits(['complete'])

const answers = ref({})
const submitted = ref(false)
const timeRemaining = ref(props.timeLimitSec)
let timer = null

const totalQuestions = computed(() => props.questions.length)
const answeredCount = computed(() => Object.keys(answers.value).length)

// Timer
onMounted(() => {
  timer = setInterval(() => {
    if (timeRemaining.value > 0 && !submitted.value) {
      timeRemaining.value--
    }
    if (timeRemaining.value <= 0 && !submitted.value) {
      submitTest()
    }
  }, 1000)
})
onBeforeUnmount(() => clearInterval(timer))

function formatTimer(s) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

const timerColor = computed(() => timeRemaining.value < 300 ? 'var(--edu-error)' : 'var(--edu-accent)')
const timerPct = computed(() => (timeRemaining.value / props.timeLimitSec) * 100)

function selectAnswer(qIdx, optIdx) {
  if (submitted.value) return
  answers.value = { ...answers.value, [qIdx]: optIdx }
}

function selectTF(qIdx, val) {
  if (submitted.value) return
  answers.value = { ...answers.value, [qIdx]: val }
}

// Grading
const results = ref(null)

function submitTest() {
  if (submitted.value) return
  submitted.value = true
  clearInterval(timer)

  let earned = 0
  let total = 0
  const corrections = []

  props.questions.forEach((q, idx) => {
    const points = q.points || 1
    total += points
    const userAnswer = answers.value[idx]
    let isCorrect = false

    if (q.type === 'true_false') {
      isCorrect = userAnswer === q.correctAnswer
    } else {
      isCorrect = q.answerOptions?.[userAnswer]?.isCorrect === true
    }

    if (isCorrect) earned += points
    corrections.push({ questionIndex: idx, correct: isCorrect, userAnswer })
  })

  const scorePercent = total > 0 ? Math.round((earned / total) * 100) : 0
  const passed = scorePercent >= props.passingScore

  results.value = { scorePercent, earned, total, passed, corrections }
  emit('complete', { scorePercent, passed })
}

function restart() {
  answers.value = {}
  submitted.value = false
  results.value = null
  timeRemaining.value = props.timeLimitSec
  timer = setInterval(() => {
    if (timeRemaining.value > 0 && !submitted.value) timeRemaining.value--
    if (timeRemaining.value <= 0 && !submitted.value) submitTest()
  }, 1000)
}
</script>

<template>
  <!-- Results -->
  <div v-if="results" class="edu-test-results">
    <div
      class="edu-badge"
      :style="{ background: results.passed ? 'rgba(5,150,105,0.12)' : 'rgba(220,38,38,0.12)', color: results.passed ? 'var(--edu-success)' : 'var(--edu-error)', fontSize: '16px', padding: '10px 24px', marginBottom: '16px' }"
    >
      {{ results.passed ? t('education.test.passed') : t('education.test.failed') }}
    </div>

    <div style="font-size: 32px; font-weight: 700; font-family: 'Manrope', sans-serif; color: var(--edu-text);">
      {{ results.scorePercent }}%
    </div>
    <div style="font-size: 14px; color: var(--edu-text-muted); margin: 8px 0 24px;">
      {{ t('education.test.scoreOf', { earned: results.earned, total: results.total, passing: passingScore }) }}
    </div>

    <!-- Score bar -->
    <div class="edu-progress-bar" style="max-width: 400px; margin: 0 auto 24px;">
      <div class="edu-progress-bar__fill" :style="{ width: results.scorePercent + '%', background: results.passed ? 'var(--edu-success)' : 'var(--edu-error)' }" />
    </div>

    <!-- Question review -->
    <div style="max-width: 700px; margin: 0 auto;">
      <h3 style="font-size: 16px; font-weight: 600; margin: 0 0 16px;">{{ t('education.test.reviewAnswers') }}</h3>
      <div v-for="(q, idx) in questions" :key="idx" class="edu-card" style="padding: 16px; margin-bottom: 10px;">
        <div style="display: flex; gap: 12px; align-items: start;">
          <span class="material-symbols-outlined" :style="{ color: results.corrections[idx].correct ? 'var(--edu-success)' : 'var(--edu-error)', fontSize: '22px' }">
            {{ results.corrections[idx].correct ? 'check_circle' : 'cancel' }}
          </span>
          <div style="flex: 1;">
            <div style="font-size: 14px; font-weight: 500; color: var(--edu-text);">{{ q.question }}</div>
            <div v-if="!results.corrections[idx].correct" style="font-size: 13px; color: var(--edu-success); margin-top: 6px;">
              {{ t('education.test.correctAnswer') }}
              <template v-if="q.type === 'true_false'">{{ q.correctAnswer ? t('education.test.true') : t('education.test.false') }}</template>
              <template v-else>
                {{ q.answerOptions?.find(o => o.isCorrect)?.text || '—' }}
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button class="edu-btn edu-btn--primary" style="margin-top: 24px;" @click="restart">{{ t('education.test.retryTest') }}</button>
  </div>

  <!-- Test form -->
  <div v-else class="edu-test">
    <!-- Timer bar -->
    <div style="position: sticky; top: 0; z-index: 10; background: var(--edu-bg-card); padding: 12px 0; border-bottom: 1px solid var(--edu-border); margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 14px; font-weight: 600;" :style="{ color: timerColor }">
          <span class="material-symbols-outlined" style="font-size: 18px; vertical-align: middle;">timer</span>
          {{ formatTimer(timeRemaining) }}
        </span>
        <span style="font-size: 13px; color: var(--edu-text-muted);">
          {{ t('education.test.answeredOf', { done: answeredCount, total: totalQuestions }) }}
        </span>
      </div>
      <div class="edu-progress-bar">
        <div class="edu-progress-bar__fill" :style="{ width: timerPct + '%', background: timerColor }" />
      </div>
    </div>

    <!-- Questions -->
    <div v-for="(q, idx) in questions" :key="idx" class="edu-card" style="padding: 20px; margin-bottom: 16px;">
      <div style="display: flex; gap: 12px; margin-bottom: 16px;">
        <span class="edu-option__key">{{ idx + 1 }}</span>
        <h4 style="margin: 0; font-size: 15px; font-weight: 600; color: var(--edu-text); line-height: 1.4;">{{ q.question }}</h4>
      </div>

      <!-- MCQ options -->
      <div v-if="q.type !== 'true_false'" style="display: flex; flex-direction: column; gap: 8px; padding-left: 40px;">
        <button
          v-for="(opt, oidx) in q.answerOptions"
          :key="oidx"
          class="edu-option"
          :class="{ 'edu-option--selected': answers[idx] === oidx }"
          @click="selectAnswer(idx, oidx)"
        >
          <span class="edu-option__key">{{ String.fromCharCode(65 + oidx) }}</span>
          <span style="flex: 1; font-size: 14px;">{{ opt.text }}</span>
        </button>
      </div>

      <!-- True/False -->
      <div v-else style="display: flex; gap: 10px; padding-left: 40px;">
        <button
          class="edu-btn"
          :class="answers[idx] === true ? 'edu-btn--primary' : 'edu-btn--outline'"
          @click="selectTF(idx, true)"
        >{{ t('education.test.true') }}</button>
        <button
          class="edu-btn"
          :class="answers[idx] === false ? 'edu-btn--primary' : 'edu-btn--outline'"
          @click="selectTF(idx, false)"
        >{{ t('education.test.false') }}</button>
      </div>
    </div>

    <!-- Submit -->
    <div style="text-align: center; padding: 24px 0;">
      <button class="edu-btn edu-btn--primary" style="padding: 12px 32px; font-size: 15px;" @click="submitTest">
        {{ t('education.test.submit', { done: answeredCount, total: totalQuestions }) }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.edu-test { max-width: 740px; }
.edu-test-results { text-align: center; padding: 32px 20px; }
</style>
