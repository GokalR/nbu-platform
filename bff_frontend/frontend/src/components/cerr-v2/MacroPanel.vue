<script setup>
import { ref, computed } from 'vue'
import CerrIcon from './CerrIcon.vue'
import { fmt } from '@/data/cerrV2Format.js'

const props = defineProps({
  data: { type: Object, default: null },
  theme: { type: String, default: 'light' },        // 'light' | 'dark'
  defaultOpen: { type: Boolean, default: false },
})

const open = ref(props.defaultOpen)
function toggle() { open.value = !open.value }

const periodLabel = computed(() => {
  if (!props.data?.period) return ''
  return props.data.period
    .replace('январь – ', 'январю – ')
    .replace('декабрь', 'декабрю')
    .replace('март', 'марту')
})

function tone(v) { return v >= 100 ? 'pos' : 'neg' }
function pp(v) {
  const d = v - 100
  return (d > 0 ? '+' : '') + d.toFixed(1).replace('.', ',') + ' п.п.'
}
function pctText(v) { return v.toFixed(1).replace('.', ',') + '%' }
</script>

<template>
  <section
    v-if="data"
    :class="[
      'macro-panel collapsible',
      theme === 'dark' ? 'is-dark' : '',
      open ? 'is-open' : '',
    ]"
  >
    <button type="button" class="macro-panel-toggle" :aria-expanded="open" @click="toggle">
      <div class="macro-panel-toggle-l">
        <span class="macro-panel-toggle-ico"><CerrIcon name="chart" :size="16" /></span>
        <div>
          <div class="macro-panel-title">{{ data.title }}</div>
          <div class="macro-panel-period">{{ data.period }} · Источник: {{ data.source }}</div>
        </div>
      </div>
      <div class="macro-panel-toggle-r">
        <span class="macro-panel-toggle-hint">{{ open ? 'Скрыть' : 'Показать' }}</span>
        <span class="macro-panel-chevron" aria-hidden="true">▾</span>
      </div>
    </button>
    <div v-if="open" class="macro-panel-body">
      <div class="macro-panel-grid">
        <div v-for="i in (data.indicators || [])" :key="i.key" class="macro-tile">
          <div class="macro-tile-icon"><CerrIcon :name="i.ico || 'chart'" :size="14" /></div>
          <div class="macro-tile-label">{{ i.label }}</div>
          <template v-if="i.val != null">
            <div :class="`macro-tile-val ${tone(i.val)}`">
              {{ pctText(i.val) }}
              <span class="macro-tile-tri">▲</span>
            </div>
            <div class="macro-tile-delta">{{ pp(i.val) }}</div>
            <div class="macro-tile-foot">В % к {{ periodLabel }}</div>
          </template>
          <template v-else>
            <div class="macro-tile-val neu">—</div>
            <div class="macro-tile-foot">нет данных</div>
          </template>
        </div>
        <div v-if="data.population" class="macro-tile macro-tile-pop">
          <div class="macro-tile-icon"><CerrIcon name="users" :size="14" /></div>
          <div class="macro-tile-label">{{ data.population.label }}</div>
          <div class="macro-tile-val tabular">{{ fmt.num(data.population.value) }}</div>
          <div class="macro-tile-foot">По состоянию {{ data.population.asof }}</div>
        </div>
      </div>
    </div>
  </section>
</template>
