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
const sphereCount = ref(props.initialSphereCount)
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
  searched.value = true

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
}

function handleNext() {
  if (!value.value.trim()) {
    error.value = t('smeProfile.errors.empty')
    return
  }
  emit('next', {
    pinflInn: value.value.trim(),
    clientInfo: clientInfo.value,
    sphereCount: sphereCount.value,
  })
}

const infoRows = computed(() => {
  const ci = clientInfo.value
  if (!ci) return []
  return [
    { icon: 'business', label: t('smeProfile.fields.company'), val: ci.company_name },
    { icon: 'person',   label: t('smeProfile.fields.director'), val: ci.director },
    { icon: 'place',    label: t('smeProfile.fields.address'),  val: ci.reg_address },
    { icon: 'call',     label: t('smeProfile.fields.phone'),    val: ci.phone },
  ].filter((r) => r.val)
})
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

    <div class="bg-surface-container-lowest rounded-xl p-6 shadow-sm">
      <label class="block text-sm font-semibold text-on-surface mb-3">
        {{ t('smeProfile.pinfl.label') }}
      </label>

      <div class="flex gap-2">
        <input
          v-model="value"
          type="text"
          :placeholder="t('smeProfile.pinfl.placeholder')"
          class="flex-1 sp-input"
          :class="{ 'sp-input--err': error }"
          @input="error = ''; clientInfo = null; notFound = false"
          @keydown.enter="handleSearch"
        />
        <button
          class="sp-btn sp-btn--primary"
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
        class="mt-4 flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3"
      >
        <AppIcon name="info" class="text-amber-600 text-base shrink-0" />
        <p class="text-xs text-amber-800">{{ t('smeProfile.pinfl.notFound') }}</p>
      </div>

      <div
        v-if="clientInfo && infoRows.length"
        class="mt-4 bg-primary/5 border border-primary/20 rounded-xl p-4 space-y-2.5"
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
          v-if="clientInfo.turnover_all || clientInfo.turnover_debit || clientInfo.accountant"
          class="mt-2 pt-2 border-t border-primary/20 space-y-1.5"
        >
          <div v-if="clientInfo.accountant" class="flex justify-between gap-2">
            <span class="text-xs text-on-surface-variant">{{ t('smeProfile.fields.accountant') }}:</span>
            <span class="text-xs font-semibold text-on-surface text-right">{{ clientInfo.accountant }}</span>
          </div>
          <div v-if="clientInfo.turnover_all" class="flex justify-between gap-2">
            <span class="text-xs text-on-surface-variant">{{ t('smeProfile.fields.turnoverAll') }}:</span>
            <span class="text-xs font-semibold text-on-surface">{{ clientInfo.turnover_all }}</span>
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
    <div class="bg-surface-container-lowest rounded-xl p-5 shadow-sm">
      <p class="text-sm font-semibold text-on-surface mb-3">
        {{ t('smeProfile.pinfl.sphereCount') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="n in [1, 2, 3, 4, 5]"
          :key="n"
          class="w-11 h-11 rounded-xl text-sm font-bold border-2 transition-all"
          :class="
            sphereCount === n
              ? 'bg-primary text-white border-primary shadow-md'
              : 'bg-white text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
          "
          @click="sphereCount = n"
        >
          {{ n }}
        </button>
      </div>
    </div>

    <button
      class="sp-btn sp-btn--primary w-full sp-btn--lg"
      :disabled="!value.trim()"
      @click="handleNext"
    >
      {{ t('smeProfile.next') }}
    </button>
  </div>
</template>

<style scoped>
.sp-input {
  padding: 0.875rem 1rem;
  border: 1px solid rgb(var(--md-sys-color-outline-variant) / 1);
  border-radius: 0.625rem;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: white;
}
.sp-input:focus {
  border-color: rgb(var(--md-sys-color-primary) / 1);
  box-shadow: 0 0 0 3px rgb(var(--md-sys-color-primary) / 0.18);
}
.sp-input--err {
  border-color: rgb(var(--md-sys-color-error) / 1);
  background: rgb(254 242 242 / 1);
}
.sp-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1.25rem;
  border-radius: 0.625rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.15s;
  border: none;
  cursor: pointer;
}
.sp-btn--primary {
  background: rgb(var(--md-sys-color-primary) / 1);
  color: white;
}
.sp-btn--primary:hover:not(:disabled) {
  filter: brightness(1.05);
}
.sp-btn--primary:active:not(:disabled) {
  transform: scale(0.97);
}
.sp-btn--lg {
  padding: 1rem 1.5rem;
  font-size: 1rem;
}
.sp-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
