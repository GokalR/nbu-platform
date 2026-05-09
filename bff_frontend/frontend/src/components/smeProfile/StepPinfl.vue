<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { smeProfileApi } from '@/services/smeProfileApi'

const props = defineProps({
  initialValue: { type: String, default: '' },
  initialClientInfo: { type: Object, default: null },
  initialSphereCount: { type: Number, default: 1 },
})
const emit = defineEmits(['next'])

const { t } = useI18n()

const value = ref(props.initialValue)
const error = ref('')
const searching = ref(false)
const clientInfo = ref(props.initialClientInfo)
const notFound = ref(false)
const sphereInput = ref(String(props.initialSphereCount))
const sphereError = ref('')
const searched = ref(!!props.initialClientInfo)

async function handleSearch() {
  if (!value.value.trim()) {
    error.value = t('smeProfile.errors.empty')
    return
  }
  searching.value = true
  error.value = ''
  notFound.value = false
  clientInfo.value = null
  searched.value = false

  const res = await smeProfileApi.lookup(value.value.trim())
  searching.value = false

  if (!res.ok) {
    error.value = t('smeProfile.errors.backend')
    return
  }
  if (res.data.found) {
    clientInfo.value = {
      company_name:       res.data.company_name || '',
      director:           res.data.director || '',
      reg_address:        res.data.reg_address || '',
      phone:              res.data.phone || '',
      turnover_debit:     res.data.turnover_debit || '',
      turnover_credit:    res.data.turnover_credit || '',
      turnover_all:       res.data.turnover_all || '',
      shareholders_count: res.data.shareholders_count || '',
      accountant:         res.data.accountant || '',
      activity_type:      res.data.activity_type || '',
      sal_sum:            res.data.sal_sum || '',
    }
  } else {
    notFound.value = true
  }
  searched.value = true
}

function handleNext() {
  if (!value.value.trim()) {
    error.value = t('smeProfile.errors.empty')
    return
  }
  const count = parseInt(sphereInput.value, 10)
  if (!sphereInput.value || isNaN(count) || count < 1 || count > 100) {
    sphereError.value = t('smeProfile.errors.sphereRange')
    return
  }
  emit('next', {
    pinflInn: value.value.trim(),
    clientInfo: clientInfo.value,
    sphereCount: count,
  })
}

const infoRows = computed(() => {
  const ci = clientInfo.value
  if (!ci) return []
  return [
    { icon: 'business', label: t('smeProfile.fields.company'),    val: ci.company_name },
    { icon: 'person',   label: t('smeProfile.fields.director'),   val: ci.director },
    { icon: 'place',    label: t('smeProfile.fields.regAddress'), val: ci.reg_address },
    { icon: 'call',     label: t('smeProfile.fields.phone'),      val: ci.phone },
  ].filter((r) => r.val)
})

const inputCls =
  'flex-1 px-4 py-3 border border-outline-variant rounded-btn text-sm bg-white text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors'
const btnPrimary =
  'inline-flex items-center justify-center gap-2 px-5 py-3 bg-primary text-white rounded-btn text-sm font-semibold hover:bg-primary/90 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0'
</script>

<template>
  <div class="space-y-6">
    <div class="text-center space-y-3">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-2xl">
        <AppIcon name="badge" class="text-primary text-3xl" filled />
      </div>
      <div>
        <h2 class="text-2xl font-bold text-on-surface">{{ t('smeProfile.pinfl.title') }}</h2>
        <p class="text-sm text-on-surface-variant mt-1">{{ t('smeProfile.pinfl.hint') }}</p>
      </div>
    </div>

    <div class="bg-surface-container-lowest rounded-card p-6 shadow-sm">
      <label class="block text-sm font-semibold text-on-surface mb-3">
        {{ t('smeProfile.pinfl.label') }}
      </label>

      <div class="flex gap-2">
        <input
          v-model="value"
          type="text"
          maxlength="14"
          :placeholder="t('smeProfile.pinfl.placeholder')"
          :class="[inputCls, error ? 'border-error bg-red-50' : '']"
          @input="error = ''; clientInfo = null; notFound = false; searched = false"
          @keydown.enter="handleSearch"
        />
        <button
          :class="btnPrimary"
          :disabled="searching || !value.trim()"
          @click="handleSearch"
        >
          <span
            v-if="searching"
            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
          />
          <AppIcon v-else name="search" />
          {{ t('smeProfile.pinfl.searchBtn') }}
        </button>
      </div>

      <p v-if="error" class="text-xs text-error font-medium mt-2">{{ error }}</p>

      <div
        v-if="notFound && !clientInfo"
        class="mt-4 flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-btn px-4 py-3"
      >
        <AppIcon name="info" class="text-amber-600 text-base shrink-0" />
        <p class="text-xs text-amber-800">{{ t('smeProfile.pinfl.notFound') }}</p>
      </div>

      <div
        v-if="clientInfo && infoRows.length"
        class="mt-4 bg-primary/5 border border-primary/20 rounded-card p-4 space-y-2.5"
      >
        <p class="text-xs font-bold text-primary uppercase tracking-wide mb-3">
          ✓ {{ t('smeProfile.pinfl.found') }}
        </p>
        <div v-for="r in infoRows" :key="r.label" class="flex items-start gap-2.5">
          <AppIcon :name="r.icon" class="text-primary text-base mt-0.5 shrink-0" />
          <div>
            <span class="text-xs text-on-surface-variant">{{ r.label }}: </span>
            <span class="text-sm font-semibold text-on-surface">{{ r.val }}</span>
          </div>
        </div>
        <div
          v-if="clientInfo.turnover_debit || clientInfo.turnover_credit || clientInfo.accountant"
          class="mt-2 pt-2 border-t border-primary/20 space-y-1.5"
        >
          <div v-if="clientInfo.accountant" class="flex justify-between gap-2">
            <span class="text-xs text-on-surface-variant">{{ t('smeProfile.fields.accountant') }}:</span>
            <span class="text-xs font-semibold text-on-surface text-right">{{ clientInfo.accountant }}</span>
          </div>
          <div v-if="clientInfo.turnover_debit" class="flex justify-between gap-2">
            <span class="text-xs text-on-surface-variant">{{ t('smeProfile.fields.debit') }}:</span>
            <span class="text-xs font-semibold text-on-surface">{{ clientInfo.turnover_debit }}</span>
          </div>
          <div v-if="clientInfo.turnover_credit" class="flex justify-between gap-2">
            <span class="text-xs text-on-surface-variant">{{ t('smeProfile.fields.credit') }}:</span>
            <span class="text-xs font-semibold text-on-surface">{{ clientInfo.turnover_credit }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Sphere count -->
    <div class="bg-surface-container-lowest rounded-card p-5 shadow-sm">
      <p class="text-sm font-semibold text-on-surface mb-1">
        {{ t('smeProfile.pinfl.sphereCount') }}
      </p>
      <p class="text-xs text-on-surface-variant italic mb-3">
        {{ t('smeProfile.pinfl.sphereCountHint') }}
      </p>
      <input
        :value="sphereInput"
        type="text"
        inputmode="numeric"
        pattern="[0-9]*"
        :class="[
          'w-28 px-4 py-3 border rounded-btn text-sm font-bold text-center bg-white text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors',
          sphereError ? 'border-error bg-red-50' : 'border-outline-variant',
        ]"
        @input="sphereInput = $event.target.value.replace(/\D/g, ''); sphereError = ''"
      />
      <p v-if="sphereError" class="text-xs text-error font-medium mt-1">{{ sphereError }}</p>
    </div>

    <p v-if="!searched" class="text-xs text-center text-on-surface-variant">
      {{ t('smeProfile.pinfl.searchFirst') }}
    </p>

    <button
      class="inline-flex items-center justify-center gap-2 w-full px-6 py-4 bg-primary text-white rounded-btn text-base font-semibold hover:bg-primary/90 active:scale-[0.99] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
      :disabled="!value.trim() || !searched"
      @click="handleNext"
    >
      {{ t('smeProfile.next') }}
      <AppIcon name="arrow_forward" />
    </button>
  </div>
</template>
