<script setup>
import { ref } from 'vue'
import RsIcon from './RsIcon.vue'

const props = defineProps({
  factors: { type: Array, required: true },
  lang: { type: String, default: 'ru' },
})

const L = {
  ru: { weight: 'Вес', contribution: 'Вклад в балл', inputsLabel: 'Что мы учли', impact: 'Влияние', expand: 'Развернуть', collapse: 'Свернуть' },
  uz: { weight: 'Vazn', contribution: 'Ball hissasi', inputsLabel: 'Hisobga olindi', impact: 'Ta'sir', expand: 'Ochish', collapse: 'Yig'ish' },
}
const t = () => L[props.lang] ?? L.ru

const open = ref(new Set())
const toggle = (key) => {
  const s = new Set(open.value)
  s.has(key) ? s.delete(key) : s.add(key)
  open.value = s
}

const barColor = (v) => (v >= 75 ? 'bg-emerald-500' : v >= 60 ? 'bg-gold-500' : v >= 40 ? 'bg-amber-400' : 'bg-red-400')
const impactClass = (n) => (n > 0 ? 'text-emerald-600' : n < 0 ? 'text-red-500' : 'text-steel-500')
const impactSign = (n) => (n > 0 ? `+${n}` : n < 0 ? `${n}` : '±0')
</script>

<template>
  <div class="space-y-2">
    <div
      v-for="f in factors" :key="f.key"
      class="border border-rs-border rounded-[10px] overflow-hidden"
    >
      <button
        type="button"
        @click="toggle(f.key)"
        class="w-full flex items-center gap-4 py-3 px-4 hover:bg-navy-900/[0.02] transition-colors text-left"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-3">
            <span class="font-sans text-[13px] font-semibold text-carbon truncate">{{ f.label[lang] || f.label.ru }}</span>
            <span class="shrink-0 flex items-center gap-3">
              <span class="font-mono text-[11px] text-steel-500">{{ t().weight }} {{ Math.round(f.weight * 100) }}%</span>
              <span class="font-mono text-[14px] font-bold text-carbon tabular-nums">{{ f.value }}</span>
            </span>
          </div>
          <div class="mt-2 h-[5px] bg-gray-100 rounded-full overflow-hidden">
            <div :class="['h-full rounded-full transition-all duration-500', barColor(f.value)]" :style="{ width: `${f.value}%` }" />
          </div>
        </div>
        <RsIcon
          name="chevron-down" :size="16"
          :class="['shrink-0 text-steel-500 transition-transform', open.has(f.key) && 'rotate-180']"
        />
      </button>

      <div v-if="open.has(f.key)" class="px-4 pb-4 pt-1 border-t border-rs-border bg-navy-900/[0.015]">
        <p class="font-sans text-[12px] text-steel-500 italic mb-3 mt-2">{{ f.hint[lang] || f.hint.ru }}</p>

        <div class="rounded-[8px] bg-white border border-rs-border overflow-hidden">
          <div class="flex items-center px-3 py-2 bg-navy-900/[0.03] text-[10px] font-semibold uppercase tracking-[0.5px] text-steel-500">
            <div class="flex-1">{{ t().inputsLabel }}</div>
            <div class="w-20 text-right">{{ t().impact }}</div>
          </div>
          <div class="divide-y divide-rs-border">
            <div v-for="(i, idx) in f.inputs" :key="idx" class="flex items-center px-3 py-2 gap-3">
              <div class="flex-1 min-w-0">
                <div class="font-mono text-[11px] text-steel-500/90 truncate">{{ i.label }}</div>
                <div class="font-sans text-[13px] text-carbon break-words">{{ i.value }}</div>
              </div>
              <div :class="['w-20 text-right font-mono text-[13px] font-semibold tabular-nums', impactClass(i.impact)]">
                {{ impactSign(i.impact) }}
              </div>
            </div>
          </div>
        </div>

        <div class="mt-3 flex items-center justify-end gap-2 text-[11px] text-steel-500">
          <span>{{ t().contribution }}:</span>
          <span class="font-mono font-semibold text-carbon">{{ f.contribution }} / {{ Math.round(f.weight * 100) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
