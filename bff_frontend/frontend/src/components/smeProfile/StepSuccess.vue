<script setup>
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  pinflInn: { type: String, required: true },
  clientInfo: { type: Object, default: null },
  sphereCount: { type: Number, required: true },
  spheres: { type: Array, required: true },
})
const emit = defineEmits(['restart'])

const { t, locale } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <div class="bg-surface-container-lowest rounded-card p-8 shadow-sm">
      <div class="text-center space-y-4">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-green-50 rounded-full">
          <AppIcon name="check_circle" class="text-green-600 text-5xl" filled />
        </div>
        <div class="space-y-1">
          <h2 class="text-2xl font-bold text-on-surface">{{ t('smeProfile.success.title') }}</h2>
          <p class="text-sm text-on-surface-variant max-w-sm mx-auto leading-relaxed">
            {{ t('smeProfile.success.msg') }}
          </p>
        </div>
      </div>
    </div>

    <div class="bg-surface-container-lowest rounded-card p-5 shadow-sm">
      <p class="text-xs font-bold text-primary uppercase tracking-wide mb-3">
        {{ t('smeProfile.summary.general') }}
      </p>
      <div class="divide-y divide-outline-variant">
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.pinflInn') }}</p>
          <p class="text-sm font-semibold text-on-surface break-words">{{ pinflInn }}</p>
        </div>
        <template v-if="clientInfo">
          <div v-if="clientInfo.company_name" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.companyFull') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.company_name }}</p>
          </div>
          <div v-if="clientInfo.director" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.director') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.director }}</p>
          </div>
        </template>
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.sphereCount') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ sphereCount }}</p>
        </div>
      </div>
    </div>

    <div v-for="(sphere, si) in spheres" :key="si" class="bg-surface-container-lowest rounded-card p-5 shadow-sm">
      <div class="flex items-center gap-3 mb-3">
        <span class="text-xs font-bold text-white bg-primary px-3 py-1 rounded-full">
          {{ t('smeProfile.fields.sphere') }} {{ sphere.sphere_number }}
        </span>
        <span class="text-sm font-semibold text-on-surface">
          {{ locale === 'ru' ? sphere.category_name_ru : sphere.category_name_uz }}
        </span>
      </div>
      <div class="divide-y divide-outline-variant">
        <div v-for="ans in sphere.answers" :key="ans.question_id" class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">
            {{ locale === 'ru' ? ans.question_text_ru : ans.question_text_uz }}
          </p>
          <p class="text-sm font-semibold text-on-surface break-words">
            {{ ans.answer || '—' }}
          </p>
        </div>
      </div>
    </div>

    <button
      class="inline-flex items-center justify-center gap-2 w-full px-6 py-4 bg-primary text-white rounded-btn text-base font-semibold hover:bg-primary/90 active:scale-[0.99] transition-all shadow-sm"
      @click="emit('restart')"
    >
      <AppIcon name="refresh" />
      {{ t('smeProfile.success.startNew') }}
    </button>
  </div>
</template>
