<script setup>
import { computed } from 'vue'

// VITE_CERR_BUNDLE_URL points at the deployed Flask service that serves the
// CERR Mahalla Analytics bundle (reference_analytics_platform/platform/).
// Local dev: http://localhost:5000. Production: e.g.
//   https://cerr.nbu-platform.up.railway.app
const bundleUrl = computed(() => {
  const raw = import.meta.env.VITE_CERR_BUNDLE_URL
  if (raw && raw.trim()) return raw.replace(/\/$/, '')
  // Sensible default for local dev when the env var hasn't been set.
  return 'http://localhost:5000'
})
</script>

<template>
  <div class="cerr-frame-shell">
    <iframe
      :src="bundleUrl"
      title="CERR Mahalla Analytics"
      allow="fullscreen"
      class="cerr-frame"
    />
  </div>
</template>

<style scoped>
/* Fits inside DefaultLayout's main area, below AppTopBar.
   AppTopBar is sticky py-4 with a text-xl title — about 64px tall. */
.cerr-frame-shell {
  height: calc(100vh - 64px);
  width: 100%;
  background: #f4f7fc;
  overflow: hidden;
}
.cerr-frame {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
}
</style>
