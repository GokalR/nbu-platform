<script setup>
import FcSidebar from '@/components/fincontrol/FcSidebar.vue'
import '@/assets/fincontrol.css'
</script>

<template>
  <div class="fc-app">
    <div class="fc-shell">
      <FcSidebar />
      <div class="fc-main">
        <slot />
      </div>
    </div>
  </div>
</template>
