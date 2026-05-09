<script setup>
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/PageHeader.vue'
import AppIcon from '@/components/AppIcon.vue'
import { partners } from '@/data/partners'

const { t } = useI18n()
</script>

<template>
  <section class="p-6 lg:p-8 space-y-10">
    <PageHeader :title="t('partners.title')" :subtitle="t('partners.subtitle')" />

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <article
        v-for="partner in partners"
        :key="partner.key"
        class="bg-surface-container-lowest rounded-2xl shadow-sm hover:shadow-lg transition-all overflow-hidden flex flex-col"
      >
        <!-- Header strip with logo + name -->
        <header class="p-6 flex items-start gap-4 border-b border-outline-variant/30">
          <div
            class="w-14 h-14 rounded-xl flex items-center justify-center text-white font-black text-lg shrink-0"
            :class="partner.accent"
          >
            {{ partner.logoText }}
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-bold text-on-surface leading-snug break-words">
              {{ partner.name }}
            </h2>
            <p class="text-xs text-on-surface-variant mt-1">
              {{ t('partners.fields.inn') }}: {{ partner.inn }}
              <span class="mx-1.5">·</span>
              {{ t('partners.fields.foundedAt') }} {{ partner.foundedAt }}
            </p>
          </div>
        </header>

        <!-- Body: key/value rows -->
        <div class="p-6 flex-1 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4 text-sm">
          <div class="sm:col-span-2">
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.address') }}
            </div>
            <div class="text-on-surface">{{ partner.address }}</div>
          </div>

          <div>
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.director') }}
            </div>
            <div class="text-on-surface">{{ partner.director }}</div>
          </div>

          <div>
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.employees') }}
            </div>
            <div class="text-on-surface">{{ partner.employees }}</div>
          </div>

          <div>
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.charterCapital') }}
            </div>
            <div class="text-on-surface">
              {{ partner.charterCapital || t('partners.values.notSpecified') }}
            </div>
          </div>

          <div>
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.audience') }}
            </div>
            <div class="text-on-surface">{{ t(partner.audienceKey) }}</div>
          </div>

          <div class="sm:col-span-2">
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.activity') }}
            </div>
            <div class="text-on-surface">{{ t(partner.activityKey) }}</div>
          </div>

          <div class="sm:col-span-2">
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.founders') }}
            </div>
            <ul class="space-y-1">
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
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.cooperationFormat') }}
            </div>
            <div class="text-on-surface">{{ t(partner.formatKey) }}</div>
          </div>

          <div class="sm:col-span-2">
            <div class="text-xs uppercase tracking-wide text-on-surface-variant font-semibold mb-1">
              {{ t('partners.fields.reward') }}
            </div>
            <div class="text-on-surface">{{ t(partner.rewardKey) }}</div>
          </div>
        </div>

        <!-- Footer: link buttons -->
        <footer class="px-6 pb-6 pt-4 border-t border-outline-variant/30 flex flex-wrap gap-3">
          <a
            :href="partner.websiteUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors no-underline"
          >
            <AppIcon name="language" />
            {{ partner.website }}
            <AppIcon name="open_in_new" class="text-base" />
          </a>
          <a
            v-if="partner.instagramUrl"
            :href="partner.instagramUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant text-on-surface text-sm font-semibold hover:bg-surface-container transition-colors no-underline"
          >
            <AppIcon name="photo_camera" />
            {{ partner.instagram }}
          </a>
        </footer>
      </article>
    </div>
  </section>
</template>
