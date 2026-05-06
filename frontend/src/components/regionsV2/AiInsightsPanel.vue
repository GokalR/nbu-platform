<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
  insights: { type: [Object, String, null], default: null },
})

// CERR ships ai_insights as either a free-form string or a structured object
// like { summary, strengths: [], weaknesses: [], recommendations: [] }.
// Normalise into a simple shape the template can render.
const blocks = computed(() => {
  const v = props.insights
  if (!v) return []
  if (typeof v === 'string') return [{ kind: 'text', body: v }]
  const out = []
  if (v.summary) out.push({ kind: 'summary', body: v.summary })
  if (Array.isArray(v.strengths) && v.strengths.length) {
    out.push({ kind: 'list', tone: 'positive', label: 'Сильные стороны', items: v.strengths })
  }
  if (Array.isArray(v.weaknesses) && v.weaknesses.length) {
    out.push({ kind: 'list', tone: 'negative', label: 'Слабые стороны', items: v.weaknesses })
  }
  if (Array.isArray(v.recommendations) && v.recommendations.length) {
    out.push({ kind: 'list', tone: 'action', label: 'Рекомендации', items: v.recommendations })
  }
  // Fallback: dump unrecognised shape as JSON so nothing is lost
  if (!out.length) out.push({ kind: 'raw', body: JSON.stringify(v, null, 2) })
  return out
})

const TONE = {
  positive: 'border-emerald-200 bg-emerald-50/40',
  negative: 'border-rose-200 bg-rose-50/40',
  action: 'border-blue-200 bg-blue-50/40',
}
</script>

<template>
  <section class="rounded-2xl bg-gradient-to-br from-violet-50 via-white to-blue-50/50 border border-violet-200/60 p-6">
    <header class="flex items-center gap-2 mb-4">
      <div class="w-9 h-9 rounded-lg bg-violet-100 flex items-center justify-center">
        <AppIcon name="auto_awesome" class="text-violet-700" />
      </div>
      <h3 class="text-lg font-black text-slate-900">{{ $t('regionsV2.aiInsights') }}</h3>
    </header>

    <div v-if="!blocks.length" class="text-sm text-slate-500 italic">{{ $t('regionsV2.noData') }}</div>

    <div v-else class="space-y-4">
      <div
        v-for="(b, i) in blocks"
        :key="i"
        class="text-sm leading-relaxed"
      >
        <p v-if="b.kind === 'summary' || b.kind === 'text'" class="text-slate-700 whitespace-pre-line">
          {{ b.body }}
        </p>
        <pre v-else-if="b.kind === 'raw'" class="text-xs text-slate-600 bg-white rounded-lg p-3 border border-slate-200 overflow-x-auto">{{ b.body }}</pre>
        <div v-else class="rounded-xl border p-4" :class="TONE[b.tone]">
          <div class="text-xs font-bold uppercase tracking-wide text-slate-700 mb-2">{{ b.label }}</div>
          <ul class="space-y-1.5 list-disc list-inside text-slate-700">
            <li v-for="(item, j) in b.items" :key="j">{{ item }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>
