<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from './AppIcon.vue'
import { regionColors } from '@/data/regionColors'

const props = defineProps({
  modelValue: { type: String, default: null },
  regions: { type: Array, required: true }, // [{key, population, ...}]
  availableRegions: { type: Set, default: null },
})
const emit = defineEmits(['update:modelValue', 'unavailable'])

const { t } = useI18n()
const open = ref(false)
const root = ref(null)

function toggle() {
  open.value = !open.value
}
function pick(key) {
  emit('update:modelValue', props.modelValue === key ? null : key)
  open.value = false
}
function onDocClick(e) {
  if (root.value && !root.value.contains(e.target)) open.value = false
}
function onKey(e) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  document.addEventListener('mousedown', onDocClick)
  document.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocClick)
  document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-colors border"
      :class="
        open || modelValue
          ? 'bg-primary text-on-primary border-primary'
          : 'bg-surface-container-lowest text-on-surface border-outline-variant/40 hover:border-primary'
      "
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <AppIcon name="map" />
      <span>
        {{ modelValue ? t(`regionsShort.${modelValue}`) : t('home.regions.button') }}
      </span>
      <AppIcon :name="open ? 'expand_less' : 'expand_more'" />
    </button>

    <transition name="dropdown">
      <div
        v-if="open"
        class="absolute right-0 mt-2 w-[min(960px,98vw)] bg-surface-container-lowest rounded-xl shadow-xl border border-outline-variant/30 overflow-hidden z-50"
        role="listbox"
      >
        <header class="px-4 py-3 bg-surface-container-low flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-widest text-on-surface-variant">
            {{ t('home.districts.title') }}
          </span>
          <span class="text-[10px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded">
            {{ t('home.districts.subtitle') }}
          </span>
        </header>

        <ul class="max-h-[60vh] overflow-y-auto py-1">
          <li v-for="r in regions" :key="r.key">
            <button
              type="button"
              class="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-surface-container transition-colors text-left"
              :class="[modelValue === r.key ? 'bg-primary-fixed' : '']"
              role="option"
              :aria-selected="modelValue === r.key"
              @click="pick(r.key)"
            >
              <span
                class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                :style="{ backgroundColor: regionColors[r.key]?.selected }"
              ></span>
              <span class="text-sm font-semibold flex-1 truncate">
                {{ t(`regions.${r.key}`) }}
              </span>
              <span class="text-xs font-bold text-primary bg-primary-fixed px-2 py-0.5 rounded">
                {{ r.population }}
              </span>
            </button>
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
