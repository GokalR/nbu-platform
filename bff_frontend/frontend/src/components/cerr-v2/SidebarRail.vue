<script setup>
import { ref, computed } from 'vue'
import CerrIcon from './CerrIcon.vue'

const props = defineProps({
  title: { type: String, required: true },
  count: { type: [Number, String], default: '' },
  items: { type: Array, default: () => [] },
  searchPlaceholder: { type: String, default: 'Поиск…' },
  activeKey: { type: [String, Number], default: null },
  /** (item) => { name, sub, badge, badgeTone } — render config per row. */
  rowFor: { type: Function, required: true },
  metaRight: { type: String, default: '' },
})
const emit = defineEmits(['select'])

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return props.items
  return props.items.filter((it) => {
    const cfg = props.rowFor(it)
    return (cfg?.name || '').toLowerCase().includes(q)
  })
})
</script>

<template>
  <aside class="rail">
    <slot name="header-top" />
    <div class="rail-head">
      <div class="rail-title"><CerrIcon name="layers" :size="14" /> {{ title }}</div>
      <div class="search-wrap">
        <span class="ico"><CerrIcon name="search" :size="14" /></span>
        <input
          class="search-input"
          v-model="search"
          :placeholder="searchPlaceholder"
        />
      </div>
      <div v-if="search.trim()" class="rail-meta">
        <span>Найдено: {{ filtered.length }}</span>
      </div>
    </div>
    <div class="rail-list">
      <button
        v-for="it in filtered"
        :key="rowFor(it).key"
        :class="[
          'rail-row',
          rowFor(it).key === activeKey ? 'active' : '',
          rowFor(it).disabled ? 'disabled' : '',
        ]"
        :disabled="rowFor(it).disabled"
        @click="!rowFor(it).disabled && emit('select', it)"
      >
        <span class="nm">{{ rowFor(it).name }}</span>
        <span v-if="rowFor(it).sub" :style="{ fontSize: '10.5px', color: 'var(--text-faint)', fontWeight: 600 }">
          {{ rowFor(it).sub }}
        </span>
        <span v-if="rowFor(it).badge != null" :class="['rt', rowFor(it).badgeTone || '']">
          {{ rowFor(it).badge }}
        </span>
      </button>
    </div>
  </aside>
</template>
