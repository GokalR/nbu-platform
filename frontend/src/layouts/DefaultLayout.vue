<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
import AppTopBar from '@/components/AppTopBar.vue'
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppSidebar />
    <main class="md:ml-64 min-h-screen flex flex-col">
      <AppTopBar />
      <div class="flex-1">
        <slot />
      </div>
      <footer class="p-8 border-t border-outline-variant/20 bg-surface-container-low text-center">
        <p class="text-xs text-on-surface-variant font-medium">{{ $t('footer.copyright') }}</p>
      </footer>
    </main>
  </div>
</template>
