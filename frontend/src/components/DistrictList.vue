<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  districts: { type: Array, required: true },
  modelValue: { type: String, default: null },
})
const emit = defineEmits(['update:modelValue'])
const { t } = useI18n()

const expanded = ref(false)
const visible = computed(() => (expanded.value ? props.districts : props.districts.slice(0, 8)))

function select(key) {
  emit('update:modelValue', key)
}
</script>

<template>
  <section
    class="bg-surface-container-lowest rounded-xl p-6 h-[600px] flex flex-col shadow-sm"
  >
    <header class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold text-on-surface">{{ t('home.districts.title') }}</h2>
      <span class="text-xs text-on-surface-variant bg-surface-container px-2 py-1 rounded">
        {{ t('home.districts.subtitle') }}
      </span>
    </header>

    <ul class="flex-1 overflow-y-auto pr-2 no-scrollbar space-y-2">
      <li v-for="d in visible" :key="d.key">
        <button
          type="button"
          class="w-full flex items-center justify-between p-3 rounded-lg transition-colors border-l-2 text-left"
          :class="
            modelValue === d.key
              ? 'bg-surface-container-low border-primary'
              : 'border-transparent hover:bg-surface-container hover:border-primary'
          "
          @click="select(d.key)"
        >
          <span class="text-sm font-semibold text-on-surface">
            {{ t(`districtsList.${d.key}`) }}
          </span>
          <span
            class="text-xs font-bold text-primary bg-primary-fixed px-2 py-1 rounded whitespace-nowrap"
          >
            {{ d.population }} ming
          </span>
        </button>
      </li>
    </ul>

    <button
      type="button"
      class="mt-4 w-full py-3 border border-outline-variant/30 rounded-lg text-sm font-bold text-on-surface hover:bg-surface-container-high transition-colors"
      @click="expanded = !expanded"
    >
      {{ t('common.viewAll') }}
    </button>
  </section>
</template>
