<script setup>
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import { tools } from '@/data/districts'

const { t } = useI18n()

function componentFor(tool) {
  if (tool.comingSoon) return 'article'
  return tool.to ? RouterLink : 'article'
}
</script>

<template>
  <section class="p-6 lg:p-8 space-y-10">
    <PageHeader :title="t('tools.title')" :subtitle="t('tools.subtitle')" />

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
      <component
        :is="componentFor(tool)"
        v-for="tool in tools"
        :key="tool.key"
        :to="tool.comingSoon ? undefined : tool.to"
        class="group bg-surface-container-lowest rounded-xl p-6 shadow-sm transition-all flex flex-col gap-4 no-underline relative"
        :class="[
          tool.comingSoon
            ? 'opacity-80 cursor-default'
            : 'hover:shadow-lg hover:-translate-y-1',
          tool.featured && !tool.comingSoon ? 'ring-2 ring-primary/30' : '',
        ]"
      >
        <div class="flex items-start justify-between">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center text-white"
            :class="tool.accent"
          >
            <AppIcon :name="tool.icon" filled />
          </div>
          <span
            v-if="tool.comingSoon"
            class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full bg-amber-100 text-amber-800 inline-flex items-center gap-1"
          >
            <AppIcon name="hourglass_top" class="text-xs" />
            {{ t('tools.inDevelopment') }}
          </span>
          <span
            v-else-if="tool.featured"
            class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full bg-primary/10 text-primary"
          >{{ t('tools.new') }}</span>
        </div>
        <div class="space-y-2 flex-1">
          <h3 class="text-lg font-bold text-on-surface">{{ t(`tools.items.${tool.key}.title`) }}</h3>
          <p class="text-sm text-on-surface-variant leading-relaxed">
            {{ t(`tools.items.${tool.key}.desc`) }}
          </p>
        </div>
        <span
          v-if="!tool.comingSoon"
          class="self-start text-sm font-bold text-primary flex items-center gap-2 group-hover:gap-3 transition-all"
        >
          {{ t('tools.open') }}
          <AppIcon name="arrow_forward" />
        </span>
        <span
          v-else
          class="self-start text-sm font-semibold text-amber-700 flex items-center gap-2"
        >
          {{ t('tools.comingSoon') }}
        </span>
      </component>
    </div>
  </section>
</template>
