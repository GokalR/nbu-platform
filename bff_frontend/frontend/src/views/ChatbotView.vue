<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import AppIcon from '@/components/AppIcon.vue'
import { openChatStream, ensureChatSessionId } from '@/services/chatbotApi'

const { t } = useI18n()

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([])
const isThinking = ref(false)
const statusMessage = ref('')
let sessionId = ''
let activeStream = null

onMounted(() => {
  sessionId = ensureChatSessionId()
  messages.value.push({ role: 'assistant', text: t('chatbot.greeting') })
})

onBeforeUnmount(() => {
  activeStream?.close?.()
  activeStream = null
})

function scrollToBottom() {
  nextTick(() => messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' }))
}

// GFM-mode marked parses tables, task lists, strikethrough, autolinks. `breaks`
// makes single newlines into <br> so the chatbot's plain-text paragraph style
// renders correctly without the user having to double-newline. DOMPurify is the
// XSS sanitizer — keeps the renderer safe even if the LLM ever returned HTML.
marked.setOptions({ gfm: true, breaks: true })

function renderMessage(text) {
  if (!text) return ''
  const html = marked.parse(String(text))
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target', 'rel'] })
}

function send() {
  const text = input.value.trim()
  if (!text || isThinking.value) return

  // Close any leftover stream from a prior message.
  activeStream?.close?.()
  activeStream = null

  messages.value.push({ role: 'user', text })
  // Push an empty assistant bubble that we fill as tokens arrive.
  messages.value.push({ role: 'assistant', text: '', streaming: true })
  const bubbleIdx = messages.value.length - 1

  input.value = ''
  isThinking.value = true
  statusMessage.value = ''
  scrollToBottom()

  let firstTokenSeen = false

  activeStream = openChatStream(
    { message: text, sessionId },
    {
      onStatus: (status) => {
        statusMessage.value = status?.message || ''
        scrollToBottom()
      },
      onToken: (chunk) => {
        if (!firstTokenSeen) {
          firstTokenSeen = true
          isThinking.value = false
          statusMessage.value = ''
        }
        const bubble = messages.value[bubbleIdx]
        if (bubble) {
          // Re-assign so Vue picks up the change (mutating .text won't
          // always trigger a re-render on the v-html binding).
          messages.value[bubbleIdx] = { ...bubble, text: bubble.text + chunk }
        }
        scrollToBottom()
      },
      onDone: (final) => {
        isThinking.value = false
        statusMessage.value = ''
        const bubble = messages.value[bubbleIdx]
        if (bubble) {
          // Replace with the canonical full answer + metadata from `done`.
          // The streamed tokens already match this text but using the final
          // payload guarantees consistency (e.g. server-side trim/transliterate).
          messages.value[bubbleIdx] = {
            role: 'assistant',
            text: final?.answer || bubble.text || t('chatbot.errorEmpty'),
            meta:
              final?.kind === 'sql_result' && typeof final?.row_count === 'number'
                ? { rowCount: final.row_count, columns: final.columns || [], sql: final.sql || '' }
                : null,
            streaming: false,
          }
        }
        activeStream = null
        scrollToBottom()
      },
      onError: (_detail) => {
        isThinking.value = false
        statusMessage.value = ''
        const bubble = messages.value[bubbleIdx]
        if (bubble && !bubble.text) {
          // No tokens arrived — replace placeholder with an error message.
          messages.value[bubbleIdx] = {
            role: 'assistant',
            text: t('chatbot.errorNetwork'),
            error: true,
            streaming: false,
          }
        } else if (bubble) {
          // We have partial text — keep it but mark stream ended.
          messages.value[bubbleIdx] = { ...bubble, streaming: false }
        }
        activeStream = null
        scrollToBottom()
      },
    },
  )
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
              class="max-w-[75%] px-4 py-3 rounded-xl text-sm leading-relaxed"
              :class="
                m.role === 'user'
                  ? 'bg-primary text-on-primary rounded-tr-sm whitespace-pre-line'
                  : m.error
                    ? 'bg-red-100 text-red-900 rounded-tl-sm whitespace-pre-line'
                    : 'bg-surface-container text-on-surface rounded-tl-sm chat-prose'
              "
            >
              <div v-if="m.role === 'user' || m.error">{{ m.text }}</div>
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
            <div class="bg-surface-container text-on-surface rounded-xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
              <span class="thinking-dot" style="animation-delay: 0ms" />
              <span class="thinking-dot" style="animation-delay: 200ms" />
              <span class="thinking-dot" style="animation-delay: 400ms" />
              <span v-if="statusMessage" class="text-[11px] text-on-surface-variant ml-1">
                {{ statusMessage }}
              </span>
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

/* Prose styles for the assistant bubble. Tailwind's `prose` plugin would do
 * this too but pulling it in for one component is overkill. Tight spacing
 * (mb-2 between paragraphs, no margin on first/last) keeps bubbles compact. */
.chat-prose :deep(> *:first-child) { margin-top: 0; }
.chat-prose :deep(> *:last-child) { margin-bottom: 0; }

.chat-prose :deep(p) { margin: 0 0 0.5rem 0; }
.chat-prose :deep(strong) { font-weight: 700; color: #1e3a8a; }
.chat-prose :deep(em) { font-style: italic; }
.chat-prose :deep(a) {
  color: #1d4ed8;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.chat-prose :deep(a:hover) { color: #1e3a8a; }

.chat-prose :deep(h1),
.chat-prose :deep(h2),
.chat-prose :deep(h3),
.chat-prose :deep(h4) {
  font-weight: 700;
  color: #1e3a8a;
  margin: 0.75rem 0 0.4rem 0;
  line-height: 1.2;
}
.chat-prose :deep(h1) { font-size: 1.15rem; }
.chat-prose :deep(h2) { font-size: 1.05rem; }
.chat-prose :deep(h3) { font-size: 0.95rem; }
.chat-prose :deep(h4) { font-size: 0.9rem; }

.chat-prose :deep(ul),
.chat-prose :deep(ol) {
  margin: 0.25rem 0 0.5rem 0;
  padding-left: 1.25rem;
}
.chat-prose :deep(ul) { list-style-type: disc; }
.chat-prose :deep(ol) { list-style-type: decimal; }
.chat-prose :deep(li) { margin: 0.15rem 0; }
.chat-prose :deep(li > p) { margin: 0; }

.chat-prose :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.85em;
  background: rgba(0, 0, 0, 0.06);
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
}
.chat-prose :deep(pre) {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.4rem 0 0.6rem 0;
}
.chat-prose :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.8rem;
  line-height: 1.45;
}

.chat-prose :deep(blockquote) {
  border-left: 3px solid rgba(30, 58, 138, 0.4);
  padding-left: 0.75rem;
  margin: 0.4rem 0;
  color: #475569;
  font-style: italic;
}

.chat-prose :deep(hr) {
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin: 0.6rem 0;
}

/* Tables: tight, header row tinted, zebra body. Cells wrap their text so a
 * many-column table grows tall instead of overflowing the bubble. */
.chat-prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  margin: 0.4rem 0 0.6rem 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 6px;
  overflow: hidden;
}
.chat-prose :deep(th) {
  background: rgba(30, 58, 138, 0.08);
  font-weight: 700;
  text-align: left;
  padding: 0.4rem 0.6rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  color: #1e3a8a;
}
.chat-prose :deep(td) {
  padding: 0.35rem 0.6rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  vertical-align: top;
}
.chat-prose :deep(tr:last-child td) { border-bottom: none; }
.chat-prose :deep(tr:nth-child(even) td) { background: rgba(0, 0, 0, 0.02); }
</style>
