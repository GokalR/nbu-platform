<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import CerrMap from '@/components/regionsV2/CerrMap.vue'
import MahallaTable from '@/components/regionsV2/MahallaTable.vue'
import { cerrApi } from '@/services/cerrApi'

const { t } = useI18n()
const route = useRoute()

const districtCode = computed(() => Number(route.params.districtCode))
const district = ref(null)
const overview = ref(null)
const mahallas = ref([])
const geo = ref(null)
const loading = ref(true)
const error = ref(null)
const hoveredStir = ref(null)

watchEffect(async () => {
  const code = districtCode.value
  if (!code) return
  loading.value = true
  error.value = null
  district.value = null
  overview.value = null
  mahallas.value = []
  geo.value = null

  const [d, ov, ml, g] = await Promise.all([
    cerrApi.getDistrict(code),
    cerrApi.getDistrictOverview(code),
    cerrApi.listDistrictMahallas(code),
    cerrApi.getDistrictGeo(code),
  ])
  loading.value = false
  if (!d.ok) {
    error.value = d.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  district.value = d.data
  overview.value = ov.ok ? ov.data : null
  mahallas.value = ml.ok ? ml.data : []
  geo.value = g.ok ? g.data : null
})

const kpis = computed(() => overview.value?.kpis || [])

const breadcrumb = computed(() => {
  if (!district.value) return [{ label: t('regionsV2.title'), to: '/regions-v2' }]
  return [
    { label: t('regionsV2.title'), to: '/regions-v2' },
    { label: district.value.region_name, to: `/regions-v2/regions/${district.value.region_code}` },
    { label: district.value.name },
  ]
})
</script>

<template>
  <div class="px-6 lg:px-10 py-8 max-w-7xl mx-auto">
    <BreadcrumbNav :items="breadcrumb" />

    <div v-if="loading" class="text-slate-500 py-20 text-center">{{ t('regionsV2.loading') }}</div>

    <div
      v-else-if="error"
      class="rounded-xl bg-amber-50 border border-amber-200 p-4 text-amber-900 text-sm"
    >
      {{ error }}
    </div>

    <template v-else-if="district">
      <header class="mb-6">
        <h1 class="text-3xl font-black text-slate-900 leading-tight">{{ district.name }}</h1>
        <p class="text-sm text-slate-500 mt-1">
          {{ district.region_name }}
          &middot;
          {{ (district.mahalla_count || 0).toLocaleString('ru-RU') }} {{ t('regionsV2.mahallasCount').toLowerCase() }}
        </p>
      </header>

      <section v-if="kpis.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
      </section>

      <div class="grid lg:grid-cols-5 gap-6">
        <div class="lg:col-span-3 h-[560px]">
          <CerrMap
            :geo="geo"
            :mahallas="mahallas"
            :highlighted-stir="hoveredStir"
            class="h-full"
            @hover="(s) => (hoveredStir = s)"
            @select="(s) => $router.push(`/regions-v2/mahallas/${s}`)"
          />
        </div>
        <div class="lg:col-span-2">
          <h2 class="text-lg font-bold text-slate-900 mb-3">{{ t('regionsV2.mahallasHeading') }}</h2>
          <div class="max-h-[520px] overflow-y-auto">
            <MahallaTable
              :mahallas="mahallas"
              :highlighted-stir="hoveredStir"
              @hover="(s) => (hoveredStir = s)"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
