<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  items: { type: Array, required: true },
})
</script>

<template>
  <nav class="crumb">
    <template v-for="(item, idx) in items" :key="idx">
      <span v-if="idx > 0" class="sep">›</span>
      <RouterLink
        v-if="item.to && idx < items.length - 1"
        :to="item.to"
      >
        {{ item.label }}
      </RouterLink>
      <span v-else :class="idx === items.length - 1 ? 'here' : ''">
        {{ item.label }}
      </span>
    </template>
  </nav>
</template>
