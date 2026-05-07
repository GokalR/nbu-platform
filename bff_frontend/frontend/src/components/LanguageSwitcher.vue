<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale, supportedLocales } from '@/i18n'

const { locale } = useI18n()

const labels = { uz: "O'z", ru: 'Ру' }
</script>

<template>
  <div
    class="inline-flex items-center bg-surface-container rounded-full p-0.5 text-xs font-bold"
    role="group"
    aria-label="Language switcher"
  >
    <button
      v-for="code in supportedLocales"
      :key="code"
      type="button"
      class="px-3 py-1.5 rounded-full transition-colors"
      :class="
        locale === code
          ? 'bg-primary text-on-primary shadow-sm'
          : 'text-on-surface-variant hover:text-primary'
      "
      :aria-pressed="locale === code"
      @click="setLocale(code)"
    >
      {{ labels[code] }}
    </button>
  </div>
</template>
