<script setup>
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  pinflInn: { type: String, required: true },
  clientInfo: { type: Object, default: null },
  sphereCount: { type: Number, required: true },
  spheres: { type: Array, required: true },
  submitting: { type: Boolean, default: false },
  submitError: { type: String, default: '' },
})
const emit = defineEmits(['back', 'submit'])

const { t, locale } = useI18n()

function show(v) {
  return v && String(v).trim() !== ''
}
</script>

<template>
  <div class="space-y-6">
    <div class="text-center space-y-2">
      <div class="inline-flex items-center justify-center w-14 h-14 bg-primary/10 rounded-2xl">
        <AppIcon name="fact_check" class="text-primary text-2xl" />
      </div>
      <h2 class="text-2xl font-bold text-on-surface">{{ t('smeProfile.summary.title') }}</h2>
      <p class="text-sm text-on-surface-variant">{{ t('smeProfile.summary.subtitle') }}</p>
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
          <div v-if="show(clientInfo.company_name)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.companyFull') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.company_name }}</p>
          </div>
          <div v-if="show(clientInfo.director)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.director') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.director }}</p>
          </div>
          <div v-if="show(clientInfo.accountant)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.accountant') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.accountant }}</p>
          </div>
          <div v-if="show(clientInfo.reg_address)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.regAddress') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.reg_address }}</p>
          </div>
          <div v-if="show(clientInfo.phone)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.phone') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.phone }}</p>
          </div>
          <div v-if="show(clientInfo.activity_type)" class="py-2.5 grid grid-cols-2 gap-4">
            <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.activityType') }}</p>
            <p class="text-sm font-semibold text-on-surface break-words">{{ clientInfo.activity_type }}</p>
          </div>
        </template>
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.sphereCount') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ sphereCount }}</p>
        </div>
      </div>
    </div>

    <div v-if="clientInfo" class="bg-surface-container-lowest rounded-card p-5 shadow-sm">
      <p class="text-xs font-bold text-primary uppercase tracking-wide mb-3">
        {{ t('smeProfile.summary.financials') }}
      </p>
      <div class="divide-y divide-outline-variant">
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.debit') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ clientInfo.turnover_debit || '—' }}</p>
        </div>
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.credit') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ clientInfo.turnover_credit || '—' }}</p>
        </div>
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.salSum') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ clientInfo.sal_sum || '—' }}</p>
        </div>
        <div class="py-2.5 grid grid-cols-2 gap-4">
          <p class="text-xs text-on-surface-variant font-medium">{{ t('smeProfile.fields.shareholders') }}</p>
          <p class="text-sm font-semibold text-on-surface">{{ clientInfo.shareholders_count || '—' }}</p>
        </div>
      </div>
    </div>

    <div v-for="(sphere, si) in spheres" :key="si" class="bg-surface-container-lowest rounded-card p-5 shadow-sm">
      <div class="flex items-center gap-3 mb-3">
        <span class="text-xs font-bold text-white bg-primary px-3 py-1 rounded-full">
          {{ t('smeProfile.fields.sphere') }} {{ sphere.sphere_number }}
        </span>
        <span class="text-sm font-semibold text-primary">
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

    <div
      v-if="submitError"
      class="flex items-start gap-3 bg-red-50 border border-red-200 rounded-card p-4"
    >
      <AppIcon name="error" class="text-error mt-0.5 shrink-0" />
      <p class="text-sm text-error">{{ submitError }}</p>
    </div>

    <div class="flex gap-3">
      <button
        class="inline-flex items-center justify-center gap-2 flex-1 px-5 py-3 bg-surface-container text-on-surface border border-outline-variant rounded-btn text-sm font-semibold hover:bg-surface-container-high transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="submitting"
        @click="emit('back')"
      >
        <AppIcon name="arrow_back" />
        {{ t('smeProfile.back') }}
      </button>
      <button
        class="inline-flex items-center justify-center gap-2 flex-1 px-5 py-3 bg-primary text-white rounded-btn text-sm font-semibold hover:bg-primary/90 active:scale-[0.99] transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="submitting"
        @click="emit('submit')"
      >
        <AppIcon v-if="!submitting" name="check_circle" />
        <span
          v-else
          class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
        />
        {{ submitting ? t('smeProfile.submitting') : t('smeProfile.submit') }}
      </button>
    </div>
  </div>
</template>
