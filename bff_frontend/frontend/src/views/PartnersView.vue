<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import { partners } from '@/data/partners'

const { t } = useI18n()

// Per-card expansion state. A Set keeps toggle logic O(1) and reactive.
const expanded = ref(new Set())

function toggle(key) {
  const next = new Set(expanded.value)
  if (next.has(key)) next.delete(key)
  else next.add(key)
  expanded.value = next
}

function isOpen(key) {
  return expanded.value.has(key)
}
</script>

<template>
  <section class="p-6 lg:p-8 space-y-8">
    <PageHeader :title="t('partners.title')" :subtitle="t('partners.subtitle')" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
      <article
        v-for="partner in partners"
        :key="partner.key"
        class="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all overflow-hidden"
      >
        <!-- Compact summary row -->
        <div class="p-5 flex items-center gap-4">
          <img
            :src="partner.logo"
            :alt="partner.name"
            class="w-14 h-14 rounded-xl object-cover bg-slate-100 shrink-0 border border-outline-variant/30"
            loading="lazy"
          />
          <div class="flex-1 min-w-0">
            <h2 class="text-base font-bold text-on-surface leading-snug truncate">
              {{ partner.name }}
            </h2>
            <p class="text-xs text-on-surface-variant mt-0.5 line-clamp-1">
              {{ t(partner.activityKey) }}
            </p>
          </div>
        </div>

        <!-- Actions -->
        <div class="px-5 pb-4 flex items-center gap-2 flex-wrap">
          <a
            :href="partner.websiteUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-white text-xs font-semibold hover:bg-primary/90 transition-colors no-underline"
          >
            <AppIcon name="language" class="!text-base" />
            {{ partner.website }}
            <AppIcon name="open_in_new" class="!text-sm opacity-80" />
          </a>
          <button
            type="button"
            @click="toggle(partner.key)"
            :aria-expanded="isOpen(partner.key)"
            class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-on-surface-variant text-xs font-semibold hover:bg-slate-100 transition-colors ml-auto"
          >
            {{ isOpen(partner.key) ? t('partners.hideDetails') : t('partners.showDetails') }}
            <AppIcon
              :name="isOpen(partner.key) ? 'expand_less' : 'expand_more'"
              class="!text-base"
            />
          </button>
        </div>

        <!-- Expanded details -->
        <transition name="reveal">
          <div
            v-if="isOpen(partner.key)"
            class="border-t border-outline-variant/30 px-5 py-5 bg-slate-50/40 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 text-sm"
          >
            <div class="sm:col-span-2 grid grid-cols-2 gap-x-6 gap-y-3 pb-3 border-b border-outline-variant/20">
              <div>
                <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                  {{ t('partners.fields.inn') }}
                </div>
                <div class="text-on-surface">{{ partner.inn }}</div>
              </div>
              <div>
                <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                  {{ t('partners.fields.foundedAt') }}
                </div>
                <div class="text-on-surface">{{ partner.foundedAt }}</div>
              </div>
            </div>

            <div class="sm:col-span-2">
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.address') }}
              </div>
              <div class="text-on-surface">{{ partner.address }}</div>
            </div>

            <div>
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.director') }}
              </div>
              <div class="text-on-surface">{{ partner.director }}</div>
            </div>

            <div>
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.employees') }}
              </div>
              <div class="text-on-surface">{{ partner.employees }}</div>
            </div>

            <div>
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.charterCapital') }}
              </div>
              <div class="text-on-surface">
                {{ partner.charterCapital || t('partners.values.notSpecified') }}
              </div>
            </div>

            <div>
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.audience') }}
              </div>
              <div class="text-on-surface">{{ t(partner.audienceKey) }}</div>
            </div>

            <div class="sm:col-span-2">
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.founders') }}
              </div>
              <ul class="space-y-0.5">
                <li
                  v-for="founder in partner.founders"
                  :key="founder.name"
                  class="flex items-center justify-between gap-3 text-on-surface"
                >
                  <span class="break-words">{{ founder.name }}</span>
                  <span class="font-semibold text-primary shrink-0">{{ founder.share }}</span>
                </li>
              </ul>
            </div>

            <div class="sm:col-span-2">
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.cooperationFormat') }}
              </div>
              <div class="text-on-surface">{{ t(partner.formatKey) }}</div>
            </div>

            <div class="sm:col-span-2">
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-0.5">
                {{ t('partners.fields.reward') }}
              </div>
              <div class="text-on-surface">{{ t(partner.rewardKey) }}</div>
            </div>

            <div v-if="partner.instagramUrl" class="sm:col-span-2">
              <div class="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold mb-1">
                {{ t('partners.fields.instagram') }}
              </div>
              <a
                :href="partner.instagramUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-primary font-semibold hover:underline"
              >
                <AppIcon name="photo_camera" class="!text-base" />
                {{ partner.instagram }}
              </a>
            </div>
          </div>
        </transition>
      </article>
    </div>
  </section>
</template>

<style scoped>
.reveal-enter-active,
.reveal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.reveal-enter-from,
.reveal-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
