<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'

// CERR's .ai-card: dark navy gradient with structured groups for
// summary / strengths / weaknesses / recommendations.
const props = defineProps({
  insights: { type: [Object, String, null], default: null },
})

const blocks = computed(() => {
  const v = props.insights
  if (!v) return []
  if (typeof v === 'string') return [{ kind: 'text', body: v }]
  const out = []
  if (v.summary) out.push({ kind: 'text', body: v.summary })
  if (Array.isArray(v.strengths) && v.strengths.length) {
    out.push({ kind: 'list', label: 'Сильные стороны', items: v.strengths })
  }
  if (Array.isArray(v.weaknesses) && v.weaknesses.length) {
    out.push({ kind: 'list', label: 'Слабые стороны', items: v.weaknesses })
  }
  if (Array.isArray(v.recommendations) && v.recommendations.length) {
    out.push({ kind: 'list', label: 'Рекомендации', items: v.recommendations })
  }
  if (!out.length) out.push({ kind: 'raw', body: JSON.stringify(v, null, 2) })
  return out
})
</script>

<template>
  <section class="ai-card">
    <header class="ai-card-head">
      <span class="badge">
        <AppIcon name="auto_awesome" class="!text-sm" />
        AI
      </span>
      <h3>{{ $t('regionsV2.aiInsights') }}</h3>
    </header>
    <div class="ai-card-body">
      <div v-if="!blocks.length" style="opacity:.7;font-style:italic">
        {{ $t('regionsV2.noData') }}
      </div>
      <template v-else>
        <p v-for="(b, i) in blocks.filter((x) => x.kind === 'text')" :key="'t' + i">
          {{ b.body }}
        </p>
        <pre
          v-for="(b, i) in blocks.filter((x) => x.kind === 'raw')"
          :key="'r' + i"
          style="font-size:11px;opacity:.7;overflow:auto;background:#ffffff0d;padding:10px;border-radius:8px"
        >{{ b.body }}</pre>
        <div
          v-for="(b, i) in blocks.filter((x) => x.kind === 'list')"
          :key="'l' + i"
          class="group"
        >
          <div class="group-label">{{ b.label }}</div>
          <ul>
            <li v-for="(item, j) in b.items" :key="j">{{ item }}</li>
          </ul>
        </div>
      </template>
    </div>
    <footer class="ai-card-footer">
      <span>Mahalla Analytics</span>
      <span>NBU AI · CERR</span>
    </footer>
  </section>
</template>
