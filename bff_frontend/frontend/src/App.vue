<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import FinControlLayout from '@/layouts/FinControlLayout.vue'
import RegionalStrategistLayout from '@/layouts/RegionalStrategistLayout.vue'
import EducationLayout from '@/layouts/EducationLayout.vue'

const route = useRoute()
const layout = computed(() => route.meta?.layout || 'default')
</script>

<template>
  <FinControlLayout v-if="layout === 'fincontrol'">
    <RouterView v-slot="{ Component, route: r }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="r.fullPath" />
      </transition>
    </RouterView>
  </FinControlLayout>

  <RegionalStrategistLayout v-else-if="layout === 'regionalStrategist'">
    <RouterView v-slot="{ Component, route: r }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="r.fullPath" />
      </transition>
    </RouterView>
  </RegionalStrategistLayout>

  <EducationLayout v-else-if="layout === 'education'">
    <RouterView v-slot="{ Component, route: r }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="r.fullPath" />
      </transition>
    </RouterView>
  </EducationLayout>

  <RouterView v-else-if="layout === 'blank'" v-slot="{ Component, route: r }">
    <transition name="fade" mode="out-in">
      <component :is="Component" :key="r.fullPath" />
    </transition>
  </RouterView>

  <DefaultLayout v-else>
    <RouterView v-slot="{ Component, route: r }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :key="r.fullPath" />
      </transition>
    </RouterView>
  </DefaultLayout>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
