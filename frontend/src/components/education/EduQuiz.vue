<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  questions: { type: Array, required: true },
})
const emit = defineEmits(['complete'])

const currentIndex = ref(0)
const selectedIndex = ref(null)
const checked = ref(false)
const score = ref(0)
const showResults = ref(false)

const total = computed(() => props.questions.length)
const current = computed(() => props.questions[currentIndex.value])
const progressPct = computed(() => ((currentIndex.value + (checked.value ? 1 : 0)) / total.value) * 100)

const scoreColor = computed(() => {
  const pct = (score.value / total.value) * 100
  if (pct >= 80) return 'var(--edu-success)'
  if (pct >= 60) return 'var(--edu-accent)'
  return 'var(--edu-error)'
})

function select(idx) {
  if (checked.value) return
  selectedIndex.value = idx
}

function check() {
  if (selectedIndex.value === null) return
  checked.value = true
  if (current.value.answerOptions[selectedIndex.value]?.isCorrect) {
    score.value++
  }
}

function next() {
  if (currentIndex.value < total.value - 1) {
    currentIndex.value++
    selectedIndex.value = null
    checked.value = false
  } else {
    showResults.value = true
    emit('complete', { scorePercent: Math.round((score.value / total.value) * 100) })
  }
}

function restart() {
  currentIndex.value = 0
  selectedIndex.value = null
  checked.value = false
  score.value = 0
  showResults.value = false
}

// SVG ring
const ringSize = 120
const ringStroke = 8
const ringRadius = (ringSize - ringStroke) / 2
const ringCircumference = 2 * Math.PI * ringRadius
const ringOffset = computed(() => ringCircumference - ((score.value / total.value) * ringCircumference))
</script>

<template>
  <!-- Results screen -->
  <div v-if="showResults" class="edu-quiz-results">
    <div class="edu-score-ring">
      <svg :width="ringSize" :height="ringSize">
        <circle :cx="ringSize/2" :cy="ringSize/2" :r="ringRadius" fill="none" stroke="#eceef0" :stroke-width="ringStroke" />
        <circle
          :cx="ringSize/2" :cy="ringSize/2" :r="ringRadius"
          fill="none" :stroke="scoreColor" :stroke-width="ringStroke"
          stroke-linecap="round"
          :stroke-dasharray="ringCircumference"
          :stroke-dashoffset="ringOffset"
          style="transition: stroke-dashoffset 0.8s ease;"
        />
      </svg>
      <div style="text-align: center;">
        <div style="font-size: 28px; font-weight: 700; font-family: 'Manrope', sans-serif;">
          {{ score }}/{{ total }}
        </div>
        <div style="font-size: 14px; color: var(--edu-text-muted); margin-top: 4px;">
          {{ Math.round((score / total) * 100) }}% правильных
        </div>
      </div>
    </div>
    <button class="edu-btn edu-btn--primary" style="margin-top: 24px;" @click="restart">
      Пройти ещё раз
    </button>
  </div>

  <!-- Quiz flow -->
  <div v-else class="edu-quiz">
    <!-- Progress bar -->
    <div class="edu-progress-bar" style="margin-bottom: 20px;">
      <div class="edu-progress-bar__fill" :style="{ width: progressPct + '%', background: 'var(--edu-accent)' }" />
    </div>
    <div style="font-size: 13px; color: var(--edu-text-muted); margin-bottom: 16px;">
      Вопрос {{ currentIndex + 1 }} из {{ total }}
    </div>

    <!-- Question -->
    <h3 style="font-size: 17px; font-weight: 600; margin: 0 0 20px; color: var(--edu-text);">
      {{ current.question }}
    </h3>

    <!-- Options -->
    <div style="display: flex; flex-direction: column; gap: 10px;">
      <button
        v-for="(opt, idx) in current.answerOptions"
        :key="idx"
        class="edu-option"
        :class="{
          'edu-option--selected': selectedIndex === idx && !checked,
          'edu-option--correct': checked && opt.isCorrect,
          'edu-option--incorrect': checked && selectedIndex === idx && !opt.isCorrect,
          'edu-option--disabled': checked,
        }"
        @click="select(idx)"
      >
        <span class="edu-option__key">{{ String.fromCharCode(65 + idx) }}</span>
        <span style="flex: 1; font-size: 14px;">{{ opt.text }}</span>
        <span v-if="checked && opt.isCorrect" class="material-symbols-outlined" style="color: var(--edu-success); font-size: 20px;">check_circle</span>
        <span v-else-if="checked && selectedIndex === idx && !opt.isCorrect" class="material-symbols-outlined" style="color: var(--edu-error); font-size: 20px;">cancel</span>
      </button>
    </div>

    <!-- Rationale -->
    <div v-if="checked && current.answerOptions[selectedIndex]?.rationale" style="margin-top: 16px; padding: 12px 16px; background: #f0f4ff; border-radius: 10px; font-size: 13px; color: var(--edu-text-secondary);">
      {{ current.answerOptions[selectedIndex].rationale }}
    </div>

    <!-- Actions -->
    <div style="display: flex; gap: 10px; margin-top: 24px;">
      <button v-if="!checked" class="edu-btn edu-btn--primary" :disabled="selectedIndex === null" @click="check">
        Проверить
      </button>
      <button v-else class="edu-btn edu-btn--primary" @click="next">
        {{ currentIndex < total - 1 ? 'Далее' : 'Результаты' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.edu-quiz { max-width: 640px; }
.edu-quiz-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}
</style>
