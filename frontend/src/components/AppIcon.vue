<script setup>
defineProps({
  name: { type: String, required: true },
  filled: { type: Boolean, default: false },
})
</script>

<template>
  <span
    class="material-symbols-outlined select-none"
    :style="filled ? { 'font-variation-settings': `'FILL' 1` } : null"
  >
    {{ name }}
  </span>
</template>
