<script setup>
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import AppIcon from '@/components/AppIcon.vue'
import { smeProfileApi } from '@/services/smeProfileApi'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

function parseParts(val) {
  const parts = (val || '').split(' | ')
  return [parts[0] || '', parts[1] || '', parts[2] || '']
}
function combine(v, t, m) {
  if (!v) return ''
  if (!t) return v
  if (!m) return `${v} | ${t}`
  return `${v} | ${t} | ${m}`
}

const initial = parseParts(props.modelValue)
const selV = ref(initial[0])
const selT = ref(initial[1])
const selM = ref(initial[2])

const viloyats = ref([])
const tumans = ref([])
const mfyList = ref([])

const loadingV = ref(true)
const loadingT = ref(false)
const loadingM = ref(false)
const noSource = ref(false)

onMounted(async () => {
  const res = await smeProfileApi.fetchViloyats()
  loadingV.value = false
  if (!res.ok || !res.data?.source_found || !res.data?.viloyats?.length) {
    noSource.value = true
    return
  }
  viloyats.value = res.data.viloyats
})

watch(selV, async (v) => {
  selT.value = ''
  selM.value = ''
  tumans.value = []
  mfyList.value = []
  if (!v) return
  loadingT.value = true
  const res = await smeProfileApi.fetchTumans(v)
  loadingT.value = false
  if (res.ok) tumans.value = res.data.tumans || []
})

watch(selT, async (t) => {
  selM.value = ''
  mfyList.value = []
  if (!selV.value || !t) return
  loadingM.value = true
  const res = await smeProfileApi.fetchMfy(selV.value, t)
  loadingM.value = false
  if (res.ok) mfyList.value = res.data.mfy || []
})

watch([selV, selT, selM], () => {
  emit('update:modelValue', combine(selV.value, selT.value, selM.value))
})

const inputCls =
  'w-full px-4 py-3 border border-outline-variant rounded-btn text-sm bg-white text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors disabled:bg-surface-container-low disabled:text-on-surface-variant disabled:cursor-not-allowed'
</script>

<template>
  <input
    v-if="noSource"
    type="text"
    :value="modelValue"
    @input="emit('update:modelValue', $event.target.value)"
    :placeholder="t('smeProfile.address.placeholder')"
    :class="inputCls"
  />
  <div v-else class="space-y-3">
    <div class="flex items-center gap-2 text-xs text-on-surface-variant font-medium mb-1">
      <AppIcon name="location_on" class="text-primary text-base" />
      <span>
        {{ t('smeProfile.address.viloyat') }} → {{ t('smeProfile.address.tuman') }} → {{ t('smeProfile.address.mfy') }}
      </span>
    </div>

    <select v-model="selV" :disabled="loadingV" :class="[inputCls, 'cursor-pointer']">
      <option value="">
        {{ loadingV ? t('smeProfile.address.loading') : t('smeProfile.address.selectViloyat') }}
      </option>
      <option v-for="v in viloyats" :key="v" :value="v">{{ v }}</option>
    </select>

    <select v-model="selT" :disabled="!selV || loadingT" :class="[inputCls, 'cursor-pointer']">
      <option value="">
        {{ loadingT ? t('smeProfile.address.loading') : t('smeProfile.address.selectTuman') }}
      </option>
      <option v-for="t in tumans" :key="t" :value="t">{{ t }}</option>
    </select>

    <select v-model="selM" :disabled="!selT || loadingM" :class="[inputCls, 'cursor-pointer']">
      <option value="">
        {{ loadingM ? t('smeProfile.address.loading') : t('smeProfile.address.selectMfy') }}
      </option>
      <option v-for="m in mfyList" :key="m" :value="m">{{ m }}</option>
    </select>
  </div>
</template>
