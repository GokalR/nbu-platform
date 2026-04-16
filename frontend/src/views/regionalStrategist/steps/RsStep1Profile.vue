<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import { useRsLang } from '@/composables/useRsLang'
import { REGIONS, VILOYAT_OPTIONS, AVAILABLE_HUDUDS } from '@/data/regionalStrategist/regions'
import RsSectionLabel from '@/components/regionalStrategist/RsSectionLabel.vue'
import RsTextField from '@/components/regionalStrategist/RsTextField.vue'
import RsSelectField from '@/components/regionalStrategist/RsSelectField.vue'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'
import { STEP1_T } from './rs-step1-i18n'

const emit = defineEmits(['back', 'next'])
const store = useRegionalStrategistStore()
const { profile, path } = storeToRefs(store)
const { lang } = useRsLang()
const t = computed(() => STEP1_T[lang.value])

const hududOptions = computed(() => {
  const all = profile.value.viloyat ? REGIONS[profile.value.viloyat] || [] : []
  return all.filter((h) => AVAILABLE_HUDUDS.has(h))
})

const updateViloyat = (v) => {
  store.updateProfile({ viloyat: v, hudud: '', mahalla: '' })
}

const entityCards = computed(() => [
  { id: 'Физическое лицо', icon: 'user', title: t.value.entityPhysTitle, desc: t.value.entityPhysDesc },
  { id: 'Юридическое лицо', icon: 'building-2', title: t.value.entityLegalTitle, desc: t.value.entityLegalDesc },
])

const loadErkinDemo = () => {
  store.seedDemo('erkinParvoz', lang.value)
}
</script>

<template>
  <div class="bg-white border border-rs-border rounded-[12px] shadow-rs-card py-8 md:py-10 px-6 md:px-12 animate-rs-fade-in-up">
    <div class="flex items-start justify-between gap-4">
      <div>
        <span class="inline-flex items-center text-[12px] font-semibold text-gold-500 bg-gold-500/[0.08] rounded-[6px] py-1 px-3">
          {{ t.stepBadge }}
        </span>
        <h1 class="text-[24px] md:text-[28px] font-bold text-carbon mt-4">
          {{ path === 'new' ? t.titleNew : t.titleExisting }}
        </h1>
        <p class="text-[14px] md:text-[15px] text-[#898989] leading-[1.5] mt-2">
          {{ path === 'new' ? t.subNew : t.subExisting }}
        </p>
      </div>
      <button
        type="button"
        @click="loadErkinDemo"
        class="shrink-0 inline-flex items-center gap-2 text-[12px] font-semibold text-navy-900 border border-gold-500/40 bg-gold-500/[0.06] hover:bg-gold-500/[0.14] rounded-[8px] py-2 px-3 transition-colors duration-200"
        :title="lang === 'uz' ? 'ERKIN PARVOZ maʻlumotlarini yuklash (demo)' : 'Загрузить демо-ответы (ERKIN PARVOZ, Фергана)'"
      >
        <RsIcon name="sparkles" :size="14" class="text-gold-500" />
        {{ lang === 'uz' ? 'Demo: ERKIN PARVOZ' : 'Демо: ERKIN PARVOZ' }}
      </button>
    </div>

    <!-- Personal -->
    <div class="mt-10">
      <RsSectionLabel color="gold">{{ t.sectionPersonal }}</RsSectionLabel>
      <div class="mt-6 space-y-7">
        <RsTextField :label="t.name" :placeholder="t.namePlaceholder"
                     :model-value="profile.name" @update:model-value="v => store.updateProfile({ name: v })" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7">
          <RsSelectField :label="t.age" :options="t.ageOpts" :model-value="profile.ageRange"
                         @update:model-value="v => store.updateProfile({ ageRange: v })" :helper="t.ageHelper" />
          <RsSelectField :label="t.gender" :options="t.genderOpts" :model-value="profile.gender"
                         @update:model-value="v => store.updateProfile({ gender: v })" :helper="t.genderHelper" />
          <RsSelectField :label="t.education" :options="t.educationOpts" :model-value="profile.hasHigherEducation"
                         @update:model-value="v => store.updateProfile({ hasHigherEducation: v })" :helper="t.educationHelper" />
          <RsTextField :label="t.specialty" :placeholder="t.specialtyPlaceholder"
                       :model-value="profile.educationField" @update:model-value="v => store.updateProfile({ educationField: v })"
                       :helper="t.specialtyHelper" />
          <template v-if="path === 'new'">
            <RsSelectField :label="t.marital" :options="t.maritalOpts" :model-value="profile.maritalStatus"
                           @update:model-value="v => store.updateProfile({ maritalStatus: v })" />
            <RsSelectField :label="t.dependents" :options="t.dependentsOpts" :model-value="profile.dependents"
                           @update:model-value="v => store.updateProfile({ dependents: v })" :helper="t.dependentsHelper" />
          </template>
        </div>
      </div>
    </div>

    <!-- Business (existing only) -->
    <div v-if="path === 'existing'" class="mt-10">
      <RsSectionLabel color="navy">{{ t.sectionBusiness }}</RsSectionLabel>
      <p class="text-[14px] font-semibold text-carbon mt-6 mb-3">{{ t.entityQuestion }}</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          v-for="card in entityCards" :key="card.id" type="button"
          @click="store.updateProfile({ entityType: card.id })"
          :class="[
            'relative text-left rounded-[12px] border-[2px] p-5 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-500/40',
            profile.entityType === card.id
              ? 'border-navy-900 bg-navy-900/[0.03] shadow-[0_2px_12px_rgba(25,63,114,0.1)]'
              : 'border-rs-border bg-white hover:border-steel-500/50 hover:shadow-[0_1px_6px_rgba(0,0,0,0.04)]',
          ]"
        >
          <div :class="[
            'absolute top-4 right-4 w-5 h-5 rounded-full border-[2px] transition-all duration-200 flex items-center justify-center',
            profile.entityType === card.id ? 'border-navy-900 bg-navy-900' : 'border-rs-border bg-white',
          ]">
            <svg v-if="profile.entityType === card.id" width="8" height="6" viewBox="0 0 10 8" fill="none">
              <path d="M1 4L3.5 6.5L9 1" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <div :class="['w-10 h-10 rounded-[10px] flex items-center justify-center mb-3',
                        profile.entityType === card.id ? 'bg-navy-900/10' : 'bg-gray-100']">
            <RsIcon :name="card.icon" :size="20" :stroke-width="1.75"
                    :class="profile.entityType === card.id ? 'text-navy-900' : 'text-steel-500'" />
          </div>
          <div class="text-[16px] font-bold text-carbon">{{ card.title }}</div>
          <div class="text-[13px] text-[#898989] mt-1">{{ card.desc }}</div>
        </button>
      </div>
      <p class="text-[12px] italic text-steel-500 mt-2">{{ t.entityHelper }}</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-7">
        <RsSelectField :label="t.regForm" :options="t.regFormOpts" :model-value="profile.registrationForm"
                       @update:model-value="v => store.updateProfile({ registrationForm: v })" :helper="t.regFormHelper" />
        <RsSelectField :label="t.bizSize" :options="t.bizSizeOpts" :model-value="profile.businessSize"
                       @update:model-value="v => store.updateProfile({ businessSize: v })" :helper="t.bizSizeHelper" />
        <RsSelectField :label="t.bizAge" :options="t.bizAgeOpts" :model-value="profile.businessAge"
                       @update:model-value="v => store.updateProfile({ businessAge: v })" :helper="t.bizAgeHelper" />
        <RsSelectField :label="t.empCount" :options="t.empCountOpts" :model-value="profile.employeeCount"
                       @update:model-value="v => store.updateProfile({ employeeCount: v })" :helper="t.empCountHelper" />
      </div>
    </div>

    <!-- Location -->
    <div class="mt-10">
      <RsSectionLabel color="gold">{{ t.sectionLocation }}</RsSectionLabel>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
        <RsSelectField :label="t.viloyat" :options="VILOYAT_OPTIONS" :model-value="profile.viloyat"
                       @update:model-value="updateViloyat" :helper="t.viloyatHelper" />
        <RsSelectField :label="t.hudud" :options="hududOptions" :model-value="profile.hudud"
                       @update:model-value="v => store.updateProfile({ hudud: v })"
                       :placeholder="profile.viloyat ? t.hududPlaceholderReady : t.hududPlaceholderWait"
                       :disabled="!profile.viloyat" :helper="t.hududHelper" />
        <RsTextField :label="t.mahalla" :placeholder="t.mahallaPlaceholder"
                     :model-value="profile.mahalla" @update:model-value="v => store.updateProfile({ mahalla: v })" />
        <RsSelectField :label="t.urbanRural" :options="t.urbanOpts" :model-value="profile.urbanRural"
                       @update:model-value="v => store.updateProfile({ urbanRural: v })" :helper="t.urbanRuralHelper" />
      </div>
    </div>

    <!-- Experience (new only) -->
    <div v-if="path === 'new'" class="mt-10">
      <RsSectionLabel color="gold">{{ t.sectionExperience }}</RsSectionLabel>
      <div class="mt-6 space-y-7">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7">
          <RsSelectField :label="t.currentStatus" :options="t.statusOpts" :model-value="profile.currentStatus"
                         @update:model-value="v => store.updateProfile({ currentStatus: v })" :helper="t.currentStatusHelper" />
          <RsSelectField :label="t.expLevel" :options="t.expOpts" :model-value="profile.experienceLevel"
                         @update:model-value="v => store.updateProfile({ experienceLevel: v })" :helper="t.expLevelHelper" />
        </div>
        <RsSelectField :label="t.domainExp" :options="t.domainExpOpts" :model-value="profile.domainExperience"
                       @update:model-value="v => store.updateProfile({ domainExperience: v })" :helper="t.domainExpHelper" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7">
          <RsSelectField :label="t.training" :options="t.yesNo" :model-value="profile.hasTraining"
                         @update:model-value="v => store.updateProfile({ hasTraining: v })" />
          <RsSelectField :label="t.mentor" :options="t.yesNo" :model-value="profile.hasMentor"
                         @update:model-value="v => store.updateProfile({ hasMentor: v })" :helper="t.mentorHelper" />
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="mt-10 flex items-center justify-between">
      <button type="button" @click="emit('back')"
              class="inline-flex items-center text-[14px] font-medium text-steel-500 hover:text-navy-900 transition-colors duration-200">
        <RsIcon name="arrow-left" :size="16" class="mr-1" />
        {{ t.back }}
      </button>
      <button type="button" @click="emit('next')"
              class="inline-flex items-center text-[15px] font-semibold text-white bg-navy-900 hover:bg-navy-700 rounded-btn py-[14px] px-6 md:px-10 transition-colors duration-200">
        {{ t.next }}
        <RsIcon name="arrow-right" :size="18" :stroke-width="2.25" class="ml-2" />
      </button>
    </div>
  </div>
</template>
