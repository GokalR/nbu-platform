<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  selectedKey: { type: String, default: 'margilon_city' },
  districts: { type: Array, required: true },
})

const { t } = useI18n()

const selected = computed(
  () => props.districts.find((d) => d.key === props.selectedKey) || props.districts[0],
)
</script>

<template>
  <section
    class="bg-surface-container-low rounded-xl overflow-hidden relative min-h-[600px] flex items-center justify-center p-8"
  >
    <!-- Stylised abstract map -->
    <svg
      class="w-full h-full max-h-[480px] opacity-90"
      viewBox="0 0 600 400"
      fill="none"
      role="img"
      :aria-label="t('home.map.tooltipTitle')"
    >
      <defs>
        <linearGradient id="mapBg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#d6e3ff" />
          <stop offset="100%" stop-color="#eceef0" />
        </linearGradient>
      </defs>
      <path
        d="M40,180 Q80,80 200,90 Q340,70 460,140 Q560,200 540,290 Q480,380 320,360 Q160,360 80,290 Q20,240 40,180 Z"
        fill="url(#mapBg)"
        stroke="#185eb0"
        stroke-width="2"
      />
      <circle cx="180" cy="180" r="14" fill="#003d7c" />
      <circle cx="320" cy="160" r="18" fill="#003d7c" />
      <circle cx="430" cy="220" r="12" fill="#185eb0" />
      <circle cx="240" cy="280" r="10" fill="#515f74" />
      <circle cx="380" cy="300" r="10" fill="#515f74" />
    </svg>

    <!-- Floating tooltip -->
    <div
      class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white/90 backdrop-blur-md p-4 rounded-lg shadow-xl border-l-4 border-primary z-10 w-64"
    >
      <div class="flex justify-between items-start mb-2">
        <span class="text-primary font-bold text-lg">
          {{ t(`districtsList.${selected.key}`) }}
        </span>
        <AppIcon name="verified" class="text-primary" />
      </div>
      <dl class="space-y-1 text-xs">
        <div class="flex justify-between">
          <dt class="text-on-surface-variant">{{ t('common.population') }}:</dt>
          <dd class="font-bold">{{ selected.population }} ming</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-on-surface-variant">{{ t('common.area') }}:</dt>
          <dd class="font-bold">40.8 km²</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-on-surface-variant">{{ t('common.mahalla') }}:</dt>
          <dd class="font-bold">54</dd>
        </div>
      </dl>
    </div>

    <!-- Highlight banner -->
    <div
      class="absolute bottom-6 left-6 right-6 text-white p-6 rounded-xl flex justify-between items-center bg-gradient-to-r from-primary to-primary-container shadow-lg"
    >
      <div class="flex items-center gap-4">
        <div class="bg-white/20 p-3 rounded-lg backdrop-blur-sm">
          <AppIcon name="info" class="text-white text-3xl" />
        </div>
        <div>
          <h3 class="text-xl font-bold leading-none mb-1">
            {{ t('home.map.selectedTitle') }}
          </h3>
          <p class="text-blue-100 text-sm">{{ t('home.map.selectedDesc') }}</p>
        </div>
      </div>
      <button
        type="button"
        class="bg-white text-primary px-5 py-2 rounded-lg font-bold text-sm transition-transform active:scale-95 hover:scale-105"
      >
        {{ t('common.details') }}
      </button>
    </div>
  </section>
</template>
