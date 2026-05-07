<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRegionalStrategistStore } from '@/stores/regionalStrategist'
import { useRsLang } from '@/composables/useRsLang'
import { BUSINESS_DIRECTIONS } from '@/data/regionalStrategist/regions'
import RsSectionLabel from '@/components/regionalStrategist/RsSectionLabel.vue'
import RsTextField from '@/components/regionalStrategist/RsTextField.vue'
import RsSelectField from '@/components/regionalStrategist/RsSelectField.vue'
import RsIcon from '@/components/regionalStrategist/RsIcon.vue'
import RsExcelUpload from '@/components/regionalStrategist/RsExcelUpload.vue'
import { STEP2_T, STEP2_BANNER_ICONS } from './rs-step2-i18n'

const emit = defineEmits(['back', 'next'])
const store = useRegionalStrategistStore()
const { profile, finance, path } = storeToRefs(store)
const { lang } = useRsLang()
const t = computed(() => STEP2_T[lang.value])

const bannerData = computed(() => t.value.banners[profile.value.currentStatus] || null)
const bannerIcon = computed(() => STEP2_BANNER_ICONS[profile.value.currentStatus] || null)

const selectedCityId = computed(() => {
  const h = [profile.value.hudud, profile.value.viloyat, profile.value.mahalla].join(' ').toLowerCase()
  return /marg|марғ|марг/.test(h) ? 'margilan' : 'fergana'
})

const showCollateralType = computed(() => finance.value.hasCollateral === t.value.collateralOpts[0])
const showLoanAmount = computed(
  () => finance.value.needsLoan === t.value.loanOpts[0] || finance.value.needsLoan === t.value.loanOpts[1],
)

const canProceed = computed(() => {
  if (!finance.value.businessDirection) return false
  return path.value === 'new'
    ? !!finance.value.hasOwnFunds && !!finance.value.needsLoan
    : !!finance.value.monthlyIncome && !!finance.value.businessGoal
})

const updateField = (key, value) => store.updateFinance({ [key]: value })

const handleCollateralChange = (v) => {
  const keep = v === t.value.collateralOpts[0]
  store.updateFinance({ hasCollateral: v, collateralType: keep ? finance.value.collateralType : '' })
}
</script>

<template>
  <div class="bg-white border border-rs-border rounded-[12px] shadow-rs-card py-8 md:py-10 px-6 md:px-12 animate-rs-fade-in-up">
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

    <!-- Adaptive banner -->
    <div
      v-if="bannerData && bannerIcon"
      class="flex items-center gap-3 rounded-[10px] border py-4 px-5 mt-6"
      style="border-color: rgba(215,181,109,0.2); background: rgba(215,181,109,0.06);"
    >
      <div class="w-9 h-9 rounded-full bg-gold-500/10 inline-flex items-center justify-center shrink-0">
        <RsIcon :name="bannerIcon" :size="20" :stroke-width="2" class="text-gold-500" />
      </div>
      <div>
        <div class="text-[16px] font-semibold text-gold-500 leading-tight">{{ bannerData.label }}</div>
        <div class="text-[14px] text-[#898989] mt-[2px]">{{ bannerData.subtitle }}</div>
      </div>
    </div>

    <!-- Business Direction -->
    <div class="mt-10">
      <RsSectionLabel color="gold">{{ t.sectionDirection }}</RsSectionLabel>
      <p class="text-[13px] font-medium text-[#898989] mt-3 mb-4">{{ t.directionHint }}</p>
      <div class="flex flex-wrap gap-[10px]">
        <button
          v-for="direction in BUSINESS_DIRECTIONS" :key="direction.uz" type="button"
          @click="updateField('businessDirection', direction[lang])"
          :aria-pressed="finance.businessDirection === direction[lang] || finance.businessDirection === direction.uz || finance.businessDirection === direction.ru"
          :class="[
            'text-[14px] font-medium py-[10px] px-[18px] rounded-[10px] border-[1.5px] transition-colors duration-150',
            (finance.businessDirection === direction[lang] || finance.businessDirection === direction.uz || finance.businessDirection === direction.ru)
              ? 'bg-navy-900 text-white border-navy-900'
              : 'bg-gray-100 text-carbon border-rs-border hover:border-navy-700 hover:bg-navy-900/[0.03]',
          ]"
        >
          {{ direction[lang] }}
        </button>
      </div>
    </div>

    <!-- NEW path -->
    <template v-if="path === 'new'">
      <div class="mt-10">
        <RsSectionLabel color="navy">{{ t.sectionIdea }}</RsSectionLabel>
        <div class="mt-6 space-y-7">
          <RsTextField :label="t.ideaLabel" :placeholder="t.ideaPlaceholder"
                       :model-value="finance.ideaDescription"
                       @update:model-value="v => updateField('ideaDescription', v)" :helper="t.ideaHelper" />
          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7">
            <RsSelectField :label="t.whyBusiness" :options="t.whyOpts" :model-value="finance.whyThisBusiness"
                           @update:model-value="v => updateField('whyThisBusiness', v)" :helper="t.whyHelper" />
            <RsSelectField :label="t.targetCustomer" :options="t.targetOpts" :model-value="finance.targetCustomer"
                           @update:model-value="v => updateField('targetCustomer', v)" :helper="t.targetHelper" />
          </div>
        </div>
      </div>

      <div class="mt-10">
        <RsSectionLabel color="gold">{{ t.sectionResources }}</RsSectionLabel>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
          <RsSelectField :label="t.ownFunds" :options="t.fundsOpts" :model-value="finance.hasOwnFunds"
                         @update:model-value="v => updateField('hasOwnFunds', v)" :helper="t.ownFundsHelper" />
          <RsSelectField :label="t.hasSpace" :options="t.spaceOpts" :model-value="finance.hasSpace"
                         @update:model-value="v => updateField('hasSpace', v)" :helper="t.hasSpaceHelper" />
          <RsSelectField :label="t.hasEquipment" :options="t.equipOpts" :model-value="finance.hasEquipment"
                         @update:model-value="v => updateField('hasEquipment', v)" :helper="t.hasEquipmentHelper" />
          <RsSelectField :label="t.registered" :options="t.regOpts" :model-value="finance.hasRegisteredBusiness"
                         @update:model-value="v => updateField('hasRegisteredBusiness', v)" :helper="t.registeredHelper" />
        </div>
      </div>

      <div class="mt-10">
        <RsSectionLabel color="navy">{{ t.sectionPlanLoan }}</RsSectionLabel>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
          <RsSelectField :label="t.hasPlan" :options="t.planOpts" :model-value="finance.hasBusinessPlan"
                         @update:model-value="v => updateField('hasBusinessPlan', v)" :helper="t.hasPlanHelper" />
          <RsSelectField :label="t.needsLoan" :options="t.loanOpts" :model-value="finance.needsLoan"
                         @update:model-value="v => updateField('needsLoan', v)" :helper="t.needsLoanHelper" />
          <RsSelectField :label="t.timeline" :options="t.timeOpts" :model-value="finance.timeline"
                         @update:model-value="v => updateField('timeline', v)" :helper="t.timelineHelper" />
        </div>
      </div>
    </template>

    <!-- EXISTING path -->
    <template v-if="path === 'existing'">
      <div class="mt-10">
        <RsSectionLabel color="navy">{{ t.sectionCurrentState }}</RsSectionLabel>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
          <RsSelectField :label="t.monthlyIncome" :options="t.incomeOpts" :model-value="finance.monthlyIncome"
                         @update:model-value="v => updateField('monthlyIncome', v)" :helper="t.incomeHelper" />
          <RsSelectField :label="t.monthlyExpenses" :options="t.expenseOpts" :model-value="finance.monthlyExpenses"
                         @update:model-value="v => updateField('monthlyExpenses', v)" :helper="t.expensesHelper" />
          <RsSelectField :label="t.existingDebt" :options="t.debtOpts" :model-value="finance.existingDebt"
                         @update:model-value="v => updateField('existingDebt', v)" :helper="t.debtHelper" />
          <RsSelectField :label="t.ownFundsExisting" :options="t.fundsOpts" :model-value="finance.hasOwnFunds"
                         @update:model-value="v => updateField('hasOwnFunds', v)" :helper="t.ownFundsHelper" />
        </div>
      </div>

      <div class="mt-10">
        <RsSectionLabel color="gold">{{ t.sectionProblems }}</RsSectionLabel>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
          <RsSelectField :label="t.bizGoal" :options="t.goalOpts" :model-value="finance.businessGoal"
                         @update:model-value="v => updateField('businessGoal', v)" :helper="t.goalHelper" />
          <RsSelectField :label="t.mainProblem" :options="t.problemOpts" :model-value="finance.mainProblem"
                         @update:model-value="v => updateField('mainProblem', v)" :helper="t.problemHelper" />
        </div>
      </div>

      <div class="mt-10">
        <RsSectionLabel color="navy">{{ t.sectionFinancing }}</RsSectionLabel>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-7 mt-6">
          <RsSelectField :label="t.needsLoan" :options="t.loanOpts" :model-value="finance.needsLoan"
                         @update:model-value="v => updateField('needsLoan', v)" :helper="t.needsLoanHelper" />
          <RsSelectField v-if="showLoanAmount" :label="t.loanAmount" :options="t.amountOpts"
                         :model-value="finance.loanAmount"
                         @update:model-value="v => updateField('loanAmount', v)" :helper="t.loanAmountHelper" />
          <RsSelectField :label="t.hasCollateral" :options="t.collateralOpts" :model-value="finance.hasCollateral"
                         @update:model-value="handleCollateralChange" :helper="t.collateralHelper" />
          <RsSelectField v-if="showCollateralType" :label="t.collateralType" :options="t.collateralTypeOpts"
                         :model-value="finance.collateralType"
                         @update:model-value="v => updateField('collateralType', v)" :helper="t.collateralTypeHelper" />
          <RsSelectField :label="t.hasPlan" :options="t.planOpts" :model-value="finance.hasBusinessPlan"
                         @update:model-value="v => updateField('hasBusinessPlan', v)" :helper="t.hasPlanHelper" />
        </div>
      </div>
    </template>

    <!-- Excel upload (optional) — attach financial statements for richer analysis on Step 5 -->
    <div class="mt-10">
      <RsExcelUpload :lang="lang" :city-id="selectedCityId" :show-analyze="false" />
    </div>

    <!-- Navigation -->
    <div class="mt-12 flex items-center justify-between">
      <button type="button" @click="emit('back')"
              class="inline-flex items-center text-[14px] font-medium text-navy-700 hover:bg-navy-900/[0.04] rounded-[8px] py-2 px-3 transition-colors duration-150">
        <RsIcon name="arrow-left" :size="16" class="mr-1" />
        {{ t.backBtn }}
      </button>
      <button type="button" @click="emit('next')" :disabled="!canProceed"
              :class="[
                'inline-flex items-center text-[15px] font-semibold text-navy-900 bg-gold-500 rounded-btn py-[14px] px-6 md:px-10 transition-all duration-200',
                canProceed ? 'hover:bg-[#C9A85F] cursor-pointer' : 'opacity-50 cursor-not-allowed',
              ]">
        <RsIcon name="sparkles" :size="18" :stroke-width="2.25" class="mr-2" />
        {{ t.nextBtn }}
      </button>
    </div>
  </div>
</template>
