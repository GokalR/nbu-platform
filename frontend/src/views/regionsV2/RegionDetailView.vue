<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import { cerrApi } from '@/services/cerrApi'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const regionCode = computed(() => Number(route.params.regionCode))
const region = ref(null)
const overview = ref(null)
const districts = ref([])
const loading = ref(true)
const error = ref(null)

watchEffect(async () => {
  const code = regionCode.value
  if (!code) return
  loading.value = true
  error.value = null
  region.value = null
  overview.value = null
  districts.value = []

  const [r, ov, dl] = await Promise.all([
    cerrApi.getRegion(code),
    cerrApi.getRegionOverview(code),
    cerrApi.listRegionDistricts(code),
  ])
  loading.value = false

  if (!r.ok) {
    error.value = r.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  region.value = r.data
  overview.value = ov.ok ? ov.data : null
  districts.value = dl.ok ? dl.data : []
})

const kpis = computed(() => overview.value?.kpis || [])

const breadcrumb = computed(() => [
  { label: t('regionsV2.title'), to: '/regions-v2' },
  { label: region.value?.name || '…' },
])

function openDistrict(code) {
  router.push(`/regions-v2/districts/${code}`)
}
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

    <template v-else-if="region">
      <header class="mb-6">
        <h1 class="text-3xl font-black text-slate-900 leading-tight">{{ region.name }}</h1>
        <p class="text-sm text-slate-500 mt-1">
          {{ region.districts_count }} {{ t('regionsV2.districtsCount').toLowerCase() }}
          &middot;
          {{ (region.mahalla_count || 0).toLocaleString('ru-RU') }} {{ t('regionsV2.mahallasCount').toLowerCase() }}
        </p>
      </header>

      <section v-if="kpis.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
      </section>

      <section>
        <h2 class="text-lg font-bold text-slate-900 mb-3">{{ t('regionsV2.districtsHeading') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <button
            v-for="d in districts"
            :key="d.code"
            class="group text-left rounded-xl bg-white border border-slate-200/70 p-4 hover:shadow-md hover:border-blue-300 transition-all"
            @click="openDistrict(d.code)"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="text-base font-bold text-slate-900 leading-tight">{{ d.name }}</div>
                <div class="text-xs text-slate-500 mt-1">
                  {{ (d.mahalla_count || 0).toLocaleString('ru-RU') }} {{ t('regionsV2.mahallasCount').toLowerCase() }}
                </div>
              </div>
              <AppIcon
                name="arrow_forward"
                class="text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition-all"
              />
            </div>
          </button>
        </div>
      </section>
    </template>
  </div>
</template>
