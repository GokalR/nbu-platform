<script setup>
import { ref, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

const { t } = useI18n()

const region = ref("Farg'ona")
const district = ref("Marg'ilon")
const input = ref('')
const messagesContainer = ref(null)

const messages = ref([
  {
    role: 'assistant',
    text: "Salom! Men NBU AI Maslahatchiman. Hududiy iqtisodiy savollaringizni bering.",
  },
])

const isThinking = ref(false)

const SUGGESTION_TO_ANSWER = {
  'ai.suggestions.q1': 'ai.answers.q1',
  'ai.suggestions.q2': 'ai.answers.q2',
  'ai.suggestions.q3': 'ai.answers.q3',
}

function answerFor(text) {
  for (const [qKey, aKey] of Object.entries(SUGGESTION_TO_ANSWER)) {
    if (t(qKey).trim() === text.trim()) return t(aKey)
  }
  return null
}

async function send() {
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  input.value = ''
  await nextTick()
  messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' })
  const predefined = answerFor(text)
  isThinking.value = true
  await nextTick()
  messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' })
  const delay = 1200 + Math.floor(Math.random() * 1800)
  setTimeout(() => {
    isThinking.value = false
    messages.value.push({
      role: 'assistant',
      text: predefined || 'Tahlil tayyorlanmoqda... (demo javob)',
    })
    nextTick(() => messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' }))
  }, delay)
}

const suggestions = ['ai.suggestions.q1', 'ai.suggestions.q2', 'ai.suggestions.q3']
function ask(key) {
  input.value = t(key)
  send()
}
</script>

<template>
  <section class="flex flex-col h-[calc(100vh-7rem)] p-6 lg:p-8 gap-6">
    <header
      class="bg-surface-container-low p-6 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4"
    >
      <div>
        <h1 class="text-3xl font-extrabold tracking-tight text-primary">{{ t('ai.title') }}</h1>
        <p class="text-on-surface-variant text-sm mt-1">{{ t('ai.subtitle') }}</p>
      </div>
      <div class="flex gap-4">
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold uppercase text-on-surface-variant tracking-wider">
            {{ t('ai.region') }}
          </label>
          <div
            class="bg-surface-container-highest px-4 py-2 rounded-lg flex items-center gap-2 min-w-[160px]"
          >
            <AppIcon name="location_on" class="text-sm text-primary" />
            <span class="text-sm font-semibold">{{ region }}</span>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[10px] font-bold uppercase text-on-surface-variant tracking-wider">
            {{ t('ai.districtLabel') }}
          </label>
          <div
            class="bg-surface-container-highest px-4 py-2 rounded-lg flex items-center gap-2 min-w-[160px]"
          >
            <AppIcon name="apartment" class="text-sm text-primary" />
            <span class="text-sm font-semibold">{{ district }}</span>
          </div>
        </div>
      </div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden">
      <!-- Chat -->
      <div class="lg:col-span-3 bg-surface-container-lowest rounded-xl flex flex-col overflow-hidden shadow-sm">
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
          <div
            v-for="(m, i) in messages"
            :key="i"
            class="flex"
            :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[75%] px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-line"
              :class="
                m.role === 'user'
                  ? 'bg-primary text-on-primary rounded-tr-sm'
                  : 'bg-surface-container text-on-surface rounded-tl-sm'
              "
            >
              {{ m.text }}
            </div>
          </div>

          <div v-if="isThinking" class="flex justify-start">
            <div class="bg-surface-container text-on-surface rounded-xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5">
              <span class="thinking-dot" style="animation-delay: 0ms" />
              <span class="thinking-dot" style="animation-delay: 200ms" />
              <span class="thinking-dot" style="animation-delay: 400ms" />
            </div>
          </div>
        </div>
        <form
          class="border-t border-outline-variant/20 p-4 flex items-center gap-3"
          @submit.prevent="send"
        >
          <input
            v-model="input"
            type="text"
            class="flex-1 bg-surface-container rounded-full px-5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            :placeholder="t('ai.placeholder')"
          />
          <button
            type="submit"
            class="bg-primary text-on-primary p-3 rounded-full hover:scale-105 active:scale-95 transition-transform"
            :aria-label="t('ai.send')"
          >
            <AppIcon name="send" filled />
          </button>
        </form>
      </div>

      <!-- Suggestions -->
      <aside class="bg-surface-container-lowest rounded-xl p-6 shadow-sm space-y-4 overflow-y-auto">
        <h3 class="text-sm font-bold text-on-surface uppercase tracking-wider">
          {{ t('ai.suggestions.title') }}
        </h3>
        <ul class="space-y-2">
          <li v-for="key in suggestions" :key="key">
            <button
              type="button"
              class="w-full text-left text-sm p-3 rounded-lg bg-surface-container hover:bg-primary-fixed hover:text-primary transition-colors font-medium"
              @click="ask(key)"
            >
              {{ t(key) }}
            </button>
          </li>
        </ul>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.thinking-dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background-color: currentColor;
  opacity: 0.4;
  animation: thinking-bounce 1.2s infinite ease-in-out;
}
@keyframes thinking-bounce {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.35; }
  40%          { transform: scale(1);   opacity: 0.9;  }
}
</style>
