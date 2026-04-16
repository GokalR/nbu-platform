<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  cards: { type: Array, required: true },
})
const emit = defineEmits(['complete'])

const currentIndex = ref(0)
const isFlipped = ref(false)
const reviewed = ref(0)
const isAdvancing = ref(false)

const total = computed(() => props.cards.length)
const current = computed(() => props.cards[currentIndex.value])
const done = computed(() => reviewed.value >= total.value)
const progressPct = computed(() => (reviewed.value / total.value) * 100)

function flipCard() {
  if (isAdvancing.value) return
  isFlipped.value = !isFlipped.value
}

function handleNext() {
  if (isAdvancing.value) return
  isAdvancing.value = true
  reviewed.value++

  setTimeout(() => {
    isFlipped.value = false
    if (currentIndex.value < total.value - 1) {
      currentIndex.value++
    }
    isAdvancing.value = false

    if (reviewed.value >= total.value) {
      emit('complete')
    }
  }, 300)
}

function restart() {
  currentIndex.value = 0
  isFlipped.value = false
  reviewed.value = 0
  isAdvancing.value = false
}
</script>

<template>
  <!-- Completion -->
  <div v-if="done" style="text-align: center; padding: 48px 20px;">
    <span class="material-symbols-outlined" style="font-size: 56px; color: var(--edu-success);">check_circle</span>
    <h3 style="font-family: 'Manrope', sans-serif; font-size: 20px; margin: 16px 0 8px;">Все карточки изучены!</h3>
    <p style="color: var(--edu-text-muted); font-size: 14px;">{{ total }} из {{ total }} карточек просмотрено</p>
    <button class="edu-btn edu-btn--primary" style="margin-top: 20px;" @click="restart">Повторить</button>
  </div>

  <!-- Flashcard flow -->
  <div v-else class="edu-fc">
    <!-- Progress -->
    <div class="edu-progress-bar" style="margin-bottom: 16px;">
      <div class="edu-progress-bar__fill" :style="{ width: progressPct + '%', background: 'var(--edu-accent)' }" />
    </div>
    <div style="font-size: 13px; color: var(--edu-text-muted); margin-bottom: 20px; text-align: center;">
      {{ reviewed }}/{{ total }}
    </div>

    <!-- Card with stack effect -->
    <div class="edu-flashcard-scene">
      <!-- Ghost cards behind -->
      <div v-if="currentIndex < total - 1" style="position: absolute; inset: 8px 8px 0; background: #f0f4ff; border-radius: 16px; border: 1px solid var(--edu-border); opacity: 0.5;" />
      <div v-if="currentIndex < total - 2" style="position: absolute; inset: 16px 16px 0; background: #e8efff; border-radius: 16px; border: 1px solid var(--edu-border); opacity: 0.3;" />

      <div class="edu-flashcard" :class="{ 'edu-flashcard--flipped': isFlipped }" @click="flipCard">
        <div class="edu-flashcard__face edu-flashcard__front">
          <div style="font-size: 12px; color: var(--edu-text-muted); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">Вопрос</div>
          <div style="font-size: 17px; font-weight: 600; color: var(--edu-text);">{{ current.front }}</div>
        </div>
        <div class="edu-flashcard__face edu-flashcard__back">
          <div style="font-size: 12px; opacity: 0.7; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px;">Ответ</div>
          <div style="font-size: 16px; line-height: 1.5;">{{ current.back }}</div>
        </div>
      </div>
    </div>

    <!-- Tap hint -->
    <p v-if="!isFlipped" style="text-align: center; font-size: 13px; color: var(--edu-text-muted); margin-top: 16px;">
      Нажмите на карточку чтобы перевернуть
    </p>

    <!-- Rating buttons -->
    <div v-if="isFlipped" style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
      <button
        v-for="label in ['Ещё раз', 'Трудно', 'Хорошо', 'Легко']"
        :key="label"
        class="edu-btn edu-btn--outline"
        style="font-size: 13px; padding: 8px 16px;"
        @click.stop="handleNext"
      >
        {{ label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.edu-fc { max-width: 540px; margin: 0 auto; }
</style>
