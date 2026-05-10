<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { sendChatMessage, ensureChatSessionId } from '@/services/chatbotApi'

const { t } = useI18n()

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([])
const isThinking = ref(false)
let sessionId = ''

onMounted(() => {
  sessionId = ensureChatSessionId()
  messages.value.push({ role: 'assistant', text: t('chatbot.greeting') })
})

function scrollToBottom() {
  nextTick(() => messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' }))
}

// Tiny markdown renderer — escapes HTML first (XSS-safe), then applies the
// inline markers the chatbot actually emits: **bold**, *italic*, `code`, and
// turns "1) " / "- " line starts into a styled list-like row. Paragraph and
// line breaks are preserved by the surrounding `whitespace: pre-line` CSS.
function renderMessage(text) {
  if (!text) return ''
  const escaped = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
  return escaped
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code class="bg-surface-container-high px-1 rounded text-[0.85em]">$1</code>')
}

async function send() {
  const text = input.value.trim()
  if (!text || isThinking.value) return

  messages.value.push({ role: 'user', text })
  input.value = ''
  isThinking.value = true
  scrollToBottom()

  try {
    const result = await sendChatMessage({ message: text, sessionId })
    const answer = result.answer || t('chatbot.errorEmpty')
    const meta =
      result.kind === 'sql_result' && typeof result.row_count === 'number'
        ? { rowCount: result.row_count, columns: result.columns || [], sql: result.sql || '' }
        : null
    messages.value.push({ role: 'assistant', text: answer, meta })
  } catch (err) {
    messages.value.push({ role: 'assistant', text: t('chatbot.errorNetwork'), error: true })
  } finally {
    isThinking.value = false
    scrollToBottom()
  }
}

const suggestions = [
  'chatbot.suggestions.q1',
  'chatbot.suggestions.q2',
  'chatbot.suggestions.q3',
  'chatbot.suggestions.q4',
  'chatbot.suggestions.q5',
  'chatbot.suggestions.q6',
]
function ask(key) {
  input.value = t(key)
  send()
}
</script>

<template>
  <section class="flex flex-col h-[calc(100vh-7rem)] p-6 lg:p-8 gap-6">
    <header class="bg-surface-container-low p-6 rounded-xl">
      <h1 class="text-3xl font-extrabold tracking-tight text-primary">{{ t('chatbot.title') }}</h1>
      <p class="text-on-surface-variant text-sm mt-1">{{ t('chatbot.subtitle') }}</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden">
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
                  : m.error
                    ? 'bg-red-100 text-red-900 rounded-tl-sm'
                    : 'bg-surface-container text-on-surface rounded-tl-sm chat-prose'
              "
            >
              <div v-if="m.role === 'user'">{{ m.text }}</div>
              <div v-else v-html="renderMessage(m.text)" />
              <div
                v-if="m.meta"
                class="mt-2 pt-2 border-t border-outline-variant/20 text-[11px] text-on-surface-variant"
              >
                {{ t('chatbot.metaRows', { n: m.meta.rowCount }) }}
              </div>
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
            :placeholder="t('chatbot.placeholder')"
            :disabled="isThinking"
          />
          <button
            type="submit"
            class="bg-primary text-on-primary p-3 rounded-full hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
            :aria-label="t('chatbot.send')"
            :disabled="isThinking"
          >
            <AppIcon name="send" filled />
          </button>
        </form>
      </div>

      <aside class="bg-surface-container-lowest rounded-xl p-6 shadow-sm space-y-4 overflow-y-auto">
        <h3 class="text-sm font-bold text-on-surface uppercase tracking-wider">
          {{ t('chatbot.suggestions.title') }}
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

.chat-prose :deep(strong) {
  font-weight: 700;
  color: rgb(var(--md-sys-color-primary, 30 58 138));
}
.chat-prose :deep(em) {
  font-style: italic;
}
.chat-prose :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
</style>
