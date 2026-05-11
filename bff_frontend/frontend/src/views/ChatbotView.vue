<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import AppIcon from '@/components/AppIcon.vue'
import {
  openChatStream,
  listChatSessions,
  createChatSession,
  loadChatSession,
  deleteChatSession,
} from '@/services/chatbotApi'

const { t } = useI18n()

const input = ref('')
const messagesContainer = ref(null)
const messages = ref([])
const isThinking = ref(false)
const statusMessage = ref('')
const sessions = ref([])
const activeSessionId = ref('')
const sessionsLoading = ref(false)
let activeStream = null

const hasUserMessages = computed(() => messages.value.some((m) => m.role === 'user'))

onMounted(async () => {
  await refreshSessions()
  if (sessions.value.length > 0) {
    await openSession(sessions.value[0].id)
  } else {
    await startNewChat()
  }
})

onBeforeUnmount(() => {
  activeStream?.close?.()
  activeStream = null
})

function scrollToBottom() {
  nextTick(() => messagesContainer.value?.scrollTo({ top: 1e9, behavior: 'smooth' }))
}

marked.setOptions({ gfm: true, breaks: true })

const _BOLD_SUFFIX_RE = /(\*\*[^*\n]+\*\*)([\p{L}\p{N}])/gu
const _ITALIC_SUFFIX_RE = /(?<![\*])(\*[^*\s][^*\n]*\*)([\p{L}\p{N}])/gu
function _fixBoldSuffix(s) {
  return s.replace(_BOLD_SUFFIX_RE, '$1 $2').replace(_ITALIC_SUFFIX_RE, '$1 $2')
}
function renderMessage(text) {
  if (!text) return ''
  const html = marked.parse(_fixBoldSuffix(String(text)))
  return DOMPurify.sanitize(html, { ADD_ATTR: ['target', 'rel'] })
}

// ---- Session management -------------------------------------------------

async function refreshSessions() {
  sessionsLoading.value = true
  try {
    sessions.value = await listChatSessions()
  } catch (err) {
    sessions.value = []
  } finally {
    sessionsLoading.value = false
  }
}

async function startNewChat() {
  activeStream?.close?.()
  activeStream = null
  isThinking.value = false
  statusMessage.value = ''
  input.value = ''
  try {
    const created = await createChatSession()
    activeSessionId.value = created.id
    messages.value = [{ role: 'assistant', text: t('chatbot.greeting') }]
    await refreshSessions()
  } catch (err) {
    messages.value = [{ role: 'assistant', text: t('chatbot.errorNetwork'), error: true }]
  }
}

async function openSession(id) {
  if (id === activeSessionId.value) return
  activeStream?.close?.()
  activeStream = null
  isThinking.value = false
  statusMessage.value = ''
  try {
    const detail = await loadChatSession(id)
    activeSessionId.value = detail.id
    if (!detail.messages || detail.messages.length === 0) {
      // Empty session — show greeting like a fresh chat.
      messages.value = [{ role: 'assistant', text: t('chatbot.greeting') }]
    } else {
      messages.value = detail.messages.map((m) => ({
        role: m.role,
        text: m.content,
        meta:
          m.role === 'assistant' && m.kind === 'sql_result' && typeof m.row_count === 'number'
            ? { rowCount: m.row_count, columns: [], sql: m.sql || '' }
            : null,
      }))
    }
    scrollToBottom()
  } catch (err) {
    messages.value = [{ role: 'assistant', text: t('chatbot.errorNetwork'), error: true }]
  }
}

async function removeSession(id, evt) {
  evt?.stopPropagation?.()
  try {
    await deleteChatSession(id)
  } catch (err) {
    /* ignore — UI still refreshes below */
  }
  await refreshSessions()
  if (id === activeSessionId.value) {
    if (sessions.value.length > 0) {
      await openSession(sessions.value[0].id)
    } else {
      await startNewChat()
    }
  }
}

// ---- Sending a message --------------------------------------------------

function send() {
  const text = input.value.trim()
  if (!text || isThinking.value || !activeSessionId.value) return

  activeStream?.close?.()
  activeStream = null

  messages.value.push({ role: 'user', text })
  messages.value.push({ role: 'assistant', text: '', streaming: true })
  const bubbleIdx = messages.value.length - 1

  input.value = ''
  isThinking.value = true
  statusMessage.value = ''
  scrollToBottom()

  let firstTokenSeen = false

  activeStream = openChatStream(
    { message: text, sessionId: activeSessionId.value },
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
          messages.value[bubbleIdx] = { ...bubble, text: bubble.text + chunk }
        }
        scrollToBottom()
      },
      onDone: (final) => {
        isThinking.value = false
        statusMessage.value = ''
        const bubble = messages.value[bubbleIdx]
        if (bubble) {
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
        // Refresh sessions so the sidebar shows the new title + recency order.
        refreshSessions()
      },
      onError: () => {
        isThinking.value = false
        statusMessage.value = ''
        const bubble = messages.value[bubbleIdx]
        if (bubble && !bubble.text) {
          messages.value[bubbleIdx] = {
            role: 'assistant',
            text: t('chatbot.errorNetwork'),
            error: true,
            streaming: false,
          }
        } else if (bubble) {
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

function formatSessionDate(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const today = new Date()
    const sameDay = d.toDateString() === today.toDateString()
    if (sameDay) {
      return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
    }
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } catch {
    return ''
  }
}
</script>

<template>
  <section class="flex flex-col h-[calc(100vh-7rem)] p-6 lg:p-8 gap-6">
    <header class="bg-surface-container-low p-6 rounded-xl">
      <h1 class="text-3xl font-extrabold tracking-tight text-primary">{{ t('chatbot.title') }}</h1>
      <p class="text-on-surface-variant text-sm mt-1">{{ t('chatbot.subtitle') }}</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 overflow-hidden">
      <!-- ============ Left sidebar: chat history ============= -->
      <aside class="bg-surface-container-lowest rounded-xl shadow-sm flex flex-col overflow-hidden">
        <div class="p-4 border-b border-outline-variant/20">
          <button
            type="button"
            class="w-full bg-primary text-on-primary text-sm font-bold py-2.5 rounded-lg hover:scale-[1.01] active:scale-[0.99] transition-transform flex items-center justify-center gap-2"
            @click="startNewChat"
          >
            <AppIcon name="add" />
            {{ t('chatbot.newChat') }}
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-1">
          <div v-if="sessionsLoading" class="text-center text-xs text-on-surface-variant py-4">
            …
          </div>
          <div
            v-else-if="sessions.length === 0"
            class="text-center text-xs text-on-surface-variant py-4 px-2"
          >
            {{ t('chatbot.noSessions') }}
          </div>
          <button
            v-for="s in sessions"
            :key="s.id"
            type="button"
            class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors group flex items-start gap-2"
            :class="
              s.id === activeSessionId
                ? 'bg-primary-fixed text-primary font-semibold'
                : 'hover:bg-surface-container text-on-surface'
            "
            @click="openSession(s.id)"
          >
            <span class="flex-1 truncate leading-snug">
              {{ s.title || t('chatbot.untitled') }}
            </span>
            <span class="text-[10px] text-on-surface-variant flex-shrink-0 mt-0.5">
              {{ formatSessionDate(s.last_message_at) }}
            </span>
            <span
              role="button"
              :aria-label="t('chatbot.deleteSession')"
              class="opacity-0 group-hover:opacity-70 hover:opacity-100 hover:text-red-700 flex-shrink-0"
              @click.stop="removeSession(s.id, $event)"
            >
              <AppIcon name="delete" />
            </span>
          </button>
        </div>
      </aside>

      <!-- ============ Main chat area ============= -->
      <div
        class="lg:col-span-3 bg-surface-container-lowest rounded-xl flex flex-col overflow-hidden shadow-sm"
      >
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
            <div
              class="bg-surface-container text-on-surface rounded-xl rounded-tl-sm px-4 py-3 flex items-center gap-2"
            >
              <span class="thinking-dot" style="animation-delay: 0ms" />
              <span class="thinking-dot" style="animation-delay: 200ms" />
              <span class="thinking-dot" style="animation-delay: 400ms" />
              <span v-if="statusMessage" class="text-[11px] text-on-surface-variant ml-1">
                {{ statusMessage }}
              </span>
            </div>
          </div>

          <!-- Suggestion chips visible only on a fresh (empty-conversation) session -->
          <div
            v-if="!hasUserMessages && !isThinking"
            class="grid grid-cols-1 md:grid-cols-2 gap-2 pt-4"
          >
            <button
              v-for="key in suggestions"
              :key="key"
              type="button"
              class="text-left text-xs p-3 rounded-lg bg-surface-container hover:bg-primary-fixed hover:text-primary transition-colors font-medium"
              @click="ask(key)"
            >
              {{ t(key) }}
            </button>
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
            :disabled="isThinking || !activeSessionId"
          />
          <button
            type="submit"
            class="bg-primary text-on-primary p-3 rounded-full hover:scale-105 active:scale-95 transition-transform disabled:opacity-50"
            :aria-label="t('chatbot.send')"
            :disabled="isThinking || !activeSessionId"
          >
            <AppIcon name="send" filled />
          </button>
        </form>
      </div>
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
