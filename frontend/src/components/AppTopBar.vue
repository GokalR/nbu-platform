<script setup>
import AppIcon from './AppIcon.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'
</script>

<template>
  <header
    class="sticky top-0 z-50 flex justify-between items-center w-full px-8 py-4 bg-white/80 backdrop-blur-xl shadow-sm"
  >
    <div class="flex items-center gap-4">
      <h1 class="text-xl font-bold tracking-tight text-blue-900">
        {{ $t('app.title') }}
      </h1>
    </div>

    <div class="flex items-center gap-6">
      <LanguageSwitcher />

      <div class="flex items-center gap-3">
        <button
          type="button"
          class="p-2 text-slate-500 hover:text-blue-800 transition-colors active:scale-95 duration-200"
          aria-label="notifications"
        >
          <AppIcon name="notifications" />
        </button>
        <button
          type="button"
          class="p-2 text-slate-500 hover:text-blue-800 transition-colors active:scale-95 duration-200"
          aria-label="settings"
        >
          <AppIcon name="settings" />
        </button>
      </div>
    </div>
  </header>
</template>
