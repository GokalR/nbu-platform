<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import BreadcrumbNav from '@/components/regionsV2/BreadcrumbNav.vue'
import KpiCard from '@/components/regionsV2/KpiCard.vue'
import AiInsightsPanel from '@/components/regionsV2/AiInsightsPanel.vue'
import { cerrApi } from '@/services/cerrApi'

const { t } = useI18n()
const route = useRoute()

const stir = computed(() => String(route.params.stir))
const overview = ref(null)
const loading = ref(true)
const error = ref(null)

watchEffect(async () => {
  const s = stir.value
  if (!s) return
  loading.value = true
  error.value = null
  overview.value = null

  const res = await cerrApi.getMahalla(s)
  loading.value = false
  if (!res.ok) {
    error.value = res.reason === 'no-backend' ? t('regionsV2.noBackend') : t('regionsV2.errorLoad')
    return
  }
  overview.value = res.data
})

const header = computed(() => overview.value?.header || {})
const kpis = computed(() => overview.value?.kpis || [])
const aiInsights = computed(() => overview.value?.ai_insights || null)

// /api/cerr/mahallas/{stir} returns the same overview shape as district/region:
// header.breadcrumb gives the parent labels, but not their codes — so we
// reconstruct route links using the mahalla summary fields when present.
const districtCode = computed(() => overview.value?.district_oktmo || overview.value?.district_code)
const regionCode = computed(() => overview.value?.region_oktmo || overview.value?.region_code)

const breadcrumb = computed(() => {
  const items = [{ label: t('regionsV2.title'), to: '/regions-v2' }]
  const crumbs = header.value?.breadcrumb
  if (Array.isArray(crumbs) && crumbs.length >= 3) {
    // breadcrumb is [Country, Region, District, Mahalla]; we want the middle two
    const regionLabel = crumbs[1]
    const districtLabel = crumbs[2]
    if (regionLabel) items.push({ label: regionLabel, to: regionCode.value ? `/regions-v2/regions/${regionCode.value}` : null })
    if (districtLabel) items.push({ label: districtLabel, to: districtCode.value ? `/regions-v2/districts/${districtCode.value}` : null })
  }
  items.push({ label: header.value?.title || stir.value })
  return items
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

    <template v-else-if="overview">
      <header class="mb-6">
        <h1 class="text-3xl font-black text-slate-900 leading-tight">
          {{ header.title || $t('common.mahalla') }}
        </h1>
        <p v-if="header.subtitle" class="text-sm text-slate-500 mt-1">{{ header.subtitle }}</p>
        <div class="mt-2 inline-flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-100 rounded-full px-3 py-1">
          STIR · {{ stir }}
        </div>
      </header>

      <section v-if="kpis.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        <KpiCard v-for="(k, i) in kpis" :key="i" :kpi="k" />
      </section>

      <AiInsightsPanel :insights="aiInsights" />
    </template>
  </div>
</template>
