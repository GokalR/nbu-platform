<script setup>
import { computed } from 'vue'
import CerrIcon from './CerrIcon.vue'

const props = defineProps({
  histogram: { type: Array, default: () => [] },   // [{bucket, count}]
  totalLabel: { type: String, default: '' },
  side: { type: Object, default: null },           // optional side panel { big, lbl, desc, chips:[{tone, label, count}] }
})

const total = computed(() => props.histogram.reduce((s, b) => s + (b.count || 0), 0))
const max = computed(() => Math.max(1, ...props.histogram.map((b) => b.count || 0)))

function tier(i) { return ['t1', 't2', 't3', 't4', 't5'][i] || 't5' }
</script>

<template>
  <section class="card featured">
    <h3 class="card-title">
      <span class="ico-tile"><CerrIcon name="award" :size="14" /></span>
      {{ $t('cerrV2.histogram.title') }}
      <span class="card-title-end">{{ $t('cerrV2.histogram.summary', { n: total, g: histogram.length }) }}</span>
    </h3>
    <div class="rating-hero">
      <div v-if="side" class="rating-side">
        <div class="big tabular">{{ side.big }}</div>
        <div class="lbl">{{ side.lbl }}</div>
        <div v-if="side.desc" class="desc" v-html="side.desc"></div>
        <div v-if="side.chips" :style="{ display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }">
          <span v-for="(c, i) in side.chips" :key="i" :class="['rank-chip', c.tone]">
            <CerrIcon :name="c.tone === 'good' ? 'check' : c.tone === 'mid' ? 'info' : 'warn'" :size="10" />
            {{ c.count }} {{ c.label }}
          </span>
        </div>
      </div>
      <div>
        <div v-for="(b, i) in histogram" :key="i" class="rating-row">
          <span :class="`rating-tag ${tier(i)}`">{{ b.bucket }}</span>
          <div :class="`rating-bar ${tier(i)}`">
            <i :style="{ width: `${Math.max((b.count / max) * 100, 1.5)}%` }" />
          </div>
          <div class="rating-count">
            {{ b.count }}<div class="pct">{{ total ? Math.round((b.count / total) * 100) : 0 }}%</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
