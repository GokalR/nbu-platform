<script setup>
import { RouterLink } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  items: { type: Array, required: true },
})
</script>

<template>
  <nav class="flex items-center gap-1.5 text-sm text-slate-500 mb-4 flex-wrap">
    <template v-for="(item, idx) in items" :key="idx">
      <span v-if="idx > 0" class="text-slate-300">
        <AppIcon name="chevron_right" class="!text-base" />
      </span>
      <RouterLink
        v-if="item.to && idx < items.length - 1"
        :to="item.to"
        class="hover:text-blue-700 transition-colors"
      >
        {{ item.label }}
      </RouterLink>
      <span
        v-else
        class="font-semibold"
        :class="idx === items.length - 1 ? 'text-slate-900' : 'text-slate-500'"
      >
        {{ item.label }}
      </span>
    </template>
  </nav>
</template>
