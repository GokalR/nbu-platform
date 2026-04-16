<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <header class="space-y-2">
    <div
      v-if="eyebrow"
      class="flex items-center gap-2 text-primary font-semibold tracking-wide text-xs uppercase"
    >
      <span class="material-symbols-outlined text-sm">location_on</span>
      {{ eyebrow }}
    </div>
    <h1 class="text-4xl md:text-5xl font-extrabold text-on-surface tracking-tight leading-none">
      {{ title }}
    </h1>
    <p v-if="subtitle" class="text-on-surface-variant max-w-2xl mt-2">{{ subtitle }}</p>
    <slot />
  </header>
</template>
