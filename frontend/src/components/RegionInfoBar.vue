<script setup>
import { useI18n } from 'vue-i18n'
import AppIcon from './AppIcon.vue'

defineProps({
  regionKey: { type: String, required: true },
  data: { type: Object, required: true },
})
defineEmits(['analyze', 'reset'])

const { t } = useI18n()
</script>

<template>
  <section
    class="bg-surface-container-lowest rounded-xl shadow-lg border border-outline-variant/20 overflow-hidden"
  >
    <header class="px-6 py-3 bg-primary text-on-primary flex items-center justify-between">
      <div class="flex items-center gap-2">
        <AppIcon name="location_on" filled />
        <h3 class="text-base font-bold tracking-tight">{{ t(`regions.${regionKey}`) }}</h3>
      </div>
      <button
        type="button"
        class="text-xs font-semibold opacity-80 hover:opacity-100 inline-flex items-center gap-1"
        @click="$emit('reset')"
      >
        <AppIcon name="public" />
        {{ t('home.map.reset') }}
      </button>
    </header>

    <div class="grid grid-cols-2 md:grid-cols-4 divide-x divide-outline-variant/20">
      <div class="p-5">
        <div class="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold mb-1">
          {{ t('regionInfo.population') }}
        </div>
        <div class="text-2xl font-extrabold text-on-surface">{{ data.population }}</div>
      </div>
      <div class="p-5">
        <div class="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold mb-1">
          {{ t('regionInfo.districts') }}
        </div>
        <div class="text-2xl font-extrabold text-on-surface">{{ data.districts }}</div>
      </div>
      <div class="p-5">
        <div class="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold mb-1">
          {{ t('regionInfo.area') }}
        </div>
        <div class="text-2xl font-extrabold text-on-surface">{{ data.area }}</div>
      </div>
      <div class="p-5">
        <div class="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold mb-1">
          {{ t('regionInfo.status') }}
        </div>
        <div class="text-2xl font-extrabold text-tertiary flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-tertiary inline-block"></span>
          {{ t('regionInfo.active') }}
        </div>
      </div>
    </div>

    <footer class="px-6 py-3 bg-surface-container-low flex items-center justify-end gap-3">
      <button
        type="button"
        class="text-sm font-semibold text-on-surface-variant hover:text-primary inline-flex items-center gap-1"
      >
        <AppIcon name="upload_file" />
        {{ t('regionInfo.publishData') }}
      </button>
      <button
        type="button"
        class="bg-primary text-on-primary px-4 py-2 rounded-lg text-sm font-bold inline-flex items-center gap-2 hover:scale-105 active:scale-95 transition-transform"
        @click="$emit('analyze')"
      >
        <AppIcon name="analytics" />
        {{ t('regionInfo.viewAnalytics') }}
      </button>
    </footer>
  </section>
</template>
