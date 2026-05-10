<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CerrIcon from './CerrIcon.vue'
import { fmt } from '@/data/cerrV2Format.js'

const props = defineProps({
  data: { type: Object, default: null },
  theme: { type: String, default: 'light' },        // 'light' | 'dark'
  defaultOpen: { type: Boolean, default: false },
})

const { t: tFn, locale } = useI18n()
const open = ref(props.defaultOpen)
function toggle() { open.value = !open.value }

/** Title comes from raqamlarda.json. uz mode reads `title_uz` (added per
 *  region), ru mode reads `title`. Falls back to the other field if the
 *  preferred one is missing. */
const titleText = computed(() => {
  if (!props.data) return ''
  if (locale.value === 'uz' && props.data.title_uz) return props.data.title_uz
  return props.data.title || props.data.title_uz || ''
})

const periodLabel = computed(() => {
  if (!props.data?.period) return ''
  return props.data.period
    .replace('январь – ', 'январю – ')
    .replace('декабрь', 'декабрю')
    .replace('март', 'марту')
})

/** Resolve indicator label via i18n keyed by indicator key.
 *  Some keys have national vs regional variants (gdp, agri, inv, constr) —
 *  we detect by whether the panel title says "Узбекистан" / "Ўзбекистон". */
const isNational = computed(() => {
  const t = (props.data?.title || '') + ' ' + (props.data?.title_uz || '')
  return /Узбекистан|Ўзбекистон/i.test(t)
})

function indicatorLabel(ind) {
  if (!ind) return ''
  const k = ind.key
  const base = 'cerrV2.macroPanel.indicatorLabel.'
  if (k === 'gdp')   return tFn(base + (isNational.value ? 'gdp' : 'gdpRegional'))
  if (k === 'agri')  return tFn(base + (isNational.value ? 'agriFull' : 'agri'))
  if (k === 'inv')   return tFn(base + (isNational.value ? 'inv' : 'invShort'))
  if (k === 'constr')return tFn(base + (isNational.value ? 'constr' : 'constrShort'))
  const direct = base + k
  const resolved = tFn(direct)
  // vue-i18n returns the key string itself when missing; in that case fall
  // back to whatever the JSON carried.
  return resolved === direct ? (ind.label || '') : resolved
}

function populationLabel(pop) {
  if (!pop) return ''
  const t = tFn('cerrV2.macroPanel.populationLabel')
  return t === 'cerrV2.macroPanel.populationLabel' ? (pop.label || '') : t
}

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
          <div class="macro-panel-title">{{ titleText }}</div>
          <div class="macro-panel-period">{{ data.period }} · {{ $t('cerrV2.macroPanel.source') }}: {{ data.source }}</div>
        </div>
      </div>
      <div class="macro-panel-toggle-r">
        <span class="macro-panel-toggle-hint">{{ open ? $t('cerrV2.macroPanel.hide') : $t('cerrV2.macroPanel.show') }}</span>
        <span class="macro-panel-chevron" aria-hidden="true">▾</span>
      </div>
    </button>
    <div v-if="open" class="macro-panel-body">
      <div class="macro-panel-grid">
        <div v-for="i in (data.indicators || [])" :key="i.key" class="macro-tile">
          <div class="macro-tile-icon"><CerrIcon :name="i.ico || 'chart'" :size="14" /></div>
          <div class="macro-tile-label">{{ indicatorLabel(i) }}</div>
          <template v-if="i.val != null">
            <div :class="`macro-tile-val ${tone(i.val)}`">
              {{ pctText(i.val) }}
              <span class="macro-tile-tri">▲</span>
            </div>
            <div class="macro-tile-delta">{{ pp(i.val) }}</div>
            <div class="macro-tile-foot">{{ $t('cerrV2.macroPanel.pctTo', { period: periodLabel }) }}</div>
          </template>
          <template v-else>
            <div class="macro-tile-val neu">—</div>
            <div class="macro-tile-foot">{{ $t('cerrV2.macroPanel.noData') }}</div>
          </template>
        </div>
        <div v-if="data.population" class="macro-tile macro-tile-pop">
          <div class="macro-tile-icon"><CerrIcon name="users" :size="14" /></div>
          <div class="macro-tile-label">{{ populationLabel(data.population) }}</div>
          <div class="macro-tile-val tabular">{{ fmt.num(data.population.value) }}</div>
          <div class="macro-tile-foot">{{ $t('cerrV2.macroPanel.asOf', { date: data.population.asof }) }}</div>
        </div>
      </div>
    </div>
  </section>
</template>
